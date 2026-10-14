#!/usr/bin/env python3
"""Feishu Bitable helpers for laowang-qiuzhi-jindu."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

API_BASE = "https://open.feishu.cn/open-apis"

STAGE_OPTIONS = [
    "意向",
    "已投",
    "测评中",
    "笔试中",
    "面试中",
    "OC/谈薪",
    "Offer",
    "拒信",
    "放弃",
]

REVIEW_STATUS_OPTIONS = ["待复盘", "已复盘"]


def default_workspace(season: str) -> Path:
    return Path(__file__).resolve().parent.parent / "workspace" / season


def resolve_obsidian_wx_path(workspace: Path, configured: str | None) -> Path | None:
    if not configured:
        return None
    candidate = Path(configured).expanduser()
    if not candidate.is_absolute():
        candidate = (workspace / candidate).resolve()
    return candidate if candidate.is_file() else None


def load_obsidian_wx_feishu(obsidian_path: Path) -> dict[str, str]:
    raw = json.loads(obsidian_path.read_text(encoding="utf-8"))
    app_id = str(raw.get("feishuAppId", "")).strip()
    app_secret = str(raw.get("feishuAppSecret", "")).strip()
    knowledge_bases = raw.get("feishuKnowledgeBases") or []
    return {
        "app_id": app_id,
        "app_secret": app_secret,
        "knowledge_bases": knowledge_bases,
        "config_sync_url": str(raw.get("configSyncUrl", "")).strip(),
    }


def load_config(workspace: Path) -> dict[str, Any]:
    path = workspace / "feishu-config.yaml"
    if not path.is_file():
        raise FileNotFoundError(
            f"缺少 {path}。先运行 import-obsidian-wx 或复制 assets/feishu-config.example.yaml。"
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    obsidian_path = resolve_obsidian_wx_path(workspace, data.get("obsidian_wx_data_path"))
    if obsidian_path:
        wx = load_obsidian_wx_feishu(obsidian_path)
        data.setdefault("app_id", wx["app_id"])
        data.setdefault("obsidian_wx_snapshot", {
            "path": str(obsidian_path),
            "knowledge_bases": wx["knowledge_bases"],
            "config_sync_url": wx["config_sync_url"],
        })
        wx_secret = wx["app_secret"]
        if wx_secret and wx_secret != "obsidian-wx:secret-storage:v1":
            data.setdefault("app_secret", wx_secret)

    secret_env = data.get("app_secret_env", "FEISHU_APP_SECRET")
    if not data.get("app_secret"):
        data["app_secret"] = os.environ.get(secret_env, "")
    if not data.get("app_id"):
        raise ValueError("feishu-config.yaml 缺少 app_id，且 obsidian-wx 未提供 feishuAppId")
    if not data.get("app_secret"):
        raise ValueError(
            f"缺少 app_secret：Obsidian 密钥在 SecretStorage 中，请 export {secret_env}=... "
            "或从火山 wx-proxy 同步后写入环境变量。"
        )
    return data


def save_config(workspace: Path, data: dict[str, Any]) -> None:
    path = workspace / "feishu-config.yaml"
    to_save = dict(data)
    to_save.pop("app_secret", None)
    path.write_text(yaml.dump(to_save, allow_unicode=True, sort_keys=False), encoding="utf-8")


class FeishuClient:
    def __init__(self, app_id: str, app_secret: str) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self._token = ""
        self._token_expire_at = 0.0

    def _ensure_token(self) -> str:
        if self._token and time.time() < self._token_expire_at - 60:
            return self._token
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}
        url = f"{API_BASE}/auth/v3/tenant_access_token/internal"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
        if raw.get("code") != 0:
            raise RuntimeError(f"Feishu auth failed: {raw.get('msg')} ({raw})")
        self._token = raw["tenant_access_token"]
        self._token_expire_at = time.time() + int(raw.get("expire", 7200))
        return self._token

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        auth: bool = True,
    ) -> dict[str, Any]:
        url = f"{API_BASE}{path}"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        if auth:
            headers["Authorization"] = f"Bearer {self._ensure_token()}"
        body = None
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} {path}: {detail}") from exc
        if raw.get("code") != 0:
            raise RuntimeError(f"Feishu API error {path}: {raw.get('msg')} ({raw})")
        return raw.get("data") or {}

    def create_app(self, name: str, folder_token: str = "") -> dict[str, Any]:
        payload: dict[str, Any] = {"name": name, "time_zone": "Asia/Shanghai"}
        if folder_token:
            payload["folder_token"] = folder_token
        return self._request("POST", "/bitable/v1/apps", payload)

    def create_table(self, app_token: str, table: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", f"/bitable/v1/apps/{app_token}/tables", {"table": table})

    def delete_table(self, app_token: str, table_id: str) -> None:
        self._request("DELETE", f"/bitable/v1/apps/{app_token}/tables/{table_id}")

    def create_record(self, app_token: str, table_id: str, fields: dict[str, Any]) -> str:
        data = self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records",
            {"fields": fields},
        )
        return data["record"]["record_id"]

    def update_record(
        self, app_token: str, table_id: str, record_id: str, fields: dict[str, Any]
    ) -> None:
        self._request(
            "PUT",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
            {"fields": fields},
        )

    def search_records(
        self, app_token: str, table_id: str, field_name: str, value: str
    ) -> list[dict[str, Any]]:
        payload = {
            "filter": {
                "conjunction": "and",
                "conditions": [
                    {"field_name": field_name, "operator": "is", "value": [value]}
                ],
            },
            "page_size": 20,
        }
        data = self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/search",
            payload,
        )
        return data.get("items") or []


def stage_field() -> dict[str, Any]:
    return {
        "field_name": "当前阶段",
        "type": 3,
        "property": {
            "options": [{"name": name, "color": idx % 12} for idx, name in enumerate(STAGE_OPTIONS)]
        },
    }


def review_status_field() -> dict[str, Any]:
    return {
        "field_name": "状态",
        "type": 3,
        "property": {
            "options": [
                {"name": "待复盘", "color": 1},
                {"name": "已复盘", "color": 10},
            ]
        },
    }


def ms_timestamp(value: str | None) -> int | None:
    if not value:
        return None
    text = value.strip()
    if len(text) == 10:
        text += "T00:00:00+08:00"
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return int(dt.timestamp() * 1000)


def build_tables(applications_table_id: str | None = None) -> list[dict[str, Any]]:
    applications = {
        "name": "投递主表",
        "default_view_name": "全部投递",
        "fields": [
            {"field_name": "card_id", "type": 1},
            {"field_name": "公司", "type": 1},
            {"field_name": "岗位", "type": 1},
            {"field_name": "城市", "type": 1},
            stage_field(),
            {"field_name": "面试轮次", "type": 1},
            {"field_name": "下一动作", "type": 1},
            {"field_name": "最近考点", "type": 1},
            {"field_name": "简历快照ID", "type": 1},
            {"field_name": "渠道", "type": 1},
            {
                "field_name": "最后更新",
                "type": 5,
                "property": {"date_formatter": "yyyy-MM-dd HH:mm"},
            },
        ],
    }
    timeline_fields = [
        {"field_name": "时间", "type": 5, "property": {"date_formatter": "yyyy-MM-dd HH:mm"}},
        {
            "field_name": "阶段",
            "type": 3,
            "property": {
                "options": [
                    {"name": name, "color": idx % 12} for idx, name in enumerate(STAGE_OPTIONS)
                ]
            },
        },
        {"field_name": "来源", "type": 1},
        {"field_name": "备注", "type": 1},
    ]
    if applications_table_id:
        timeline_fields.append(
            {
                "field_name": "关联投递",
                "type": 18,
                "property": {"table_id": applications_table_id, "multiple": False},
            },
        )
    timeline = {
        "name": "进度时间线",
        "default_view_name": "时间线",
        "fields": timeline_fields,
    }
    review = {
        "name": "待复盘队列",
        "default_view_name": "待复盘",
        "fields": [
            {"field_name": "公司", "type": 1},
            {"field_name": "岗位", "type": 1},
            {"field_name": "考点", "type": 1},
            {
                "field_name": "登记日",
                "type": 5,
                "property": {"date_formatter": "yyyy-MM-dd"},
            },
            review_status_field(),
        ],
    }
    return [applications, timeline, review]


def cmd_init(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    config = load_config(workspace)
    client = FeishuClient(config["app_id"], config["app_secret"])

    title = args.title or f"秋招求职进度-{date.today()}"
    app = client.create_app(title, config.get("folder_token", ""))
    app_token = app["app"]["app_token"]
    app_url = app["app"].get("url", "")
    default_table_id = app["app"].get("default_table_id")

    app_table = build_tables()[0]
    applications = client.create_table(app_token, app_table)
    applications_table_id = applications["table_id"]

    timeline = client.create_table(app_token, build_tables(applications_table_id)[1])
    review = client.create_table(app_token, build_tables(applications_table_id)[2])

    if default_table_id and default_table_id != applications_table_id:
        try:
            client.delete_table(app_token, default_table_id)
        except RuntimeError:
            pass

    config.update(
        {
            "app_token": app_token,
            "app_url": app_url,
            "tables": {
                "applications": applications_table_id,
                "timeline": timeline["table_id"],
                "review_queue": review["table_id"],
            },
            "record_map": config.get("record_map") or {},
            "initialized_at": str(datetime.now().isoformat(timespec="seconds")),
        }
    )
    save_config(workspace, config)
    print(json.dumps({"ok": True, "app_token": app_token, "app_url": app_url}, ensure_ascii=False, indent=2))
    return 0


def card_to_fields(card: dict[str, Any]) -> dict[str, Any]:
    interview = card.get("interview") or {}
    focus = interview.get("focus_topics") or []
    fields: dict[str, Any] = {
        "card_id": card.get("card_id", ""),
        "公司": card.get("company", ""),
        "岗位": card.get("role", ""),
        "城市": card.get("city", ""),
        "当前阶段": card.get("current_stage", ""),
        "面试轮次": interview.get("round", ""),
        "下一动作": card.get("next_action", ""),
        "最近考点": ", ".join(focus) if focus else "",
        "简历快照ID": card.get("resume_snapshot_id", ""),
        "渠道": card.get("channel", ""),
    }
    ts = ms_timestamp(card.get("updated_at"))
    if ts:
        fields["最后更新"] = ts
    return {k: v for k, v in fields.items() if v not in ("", None)}


def cmd_sync_card(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    config = load_config(workspace)
    client = FeishuClient(config["app_id"], config["app_secret"])
    app_token = config["app_token"]
    table_id = config["tables"]["applications"]

    card_path = Path(args.card).expanduser().resolve()
    card = yaml.safe_load(card_path.read_text(encoding="utf-8")) or {}
    card_id = card.get("card_id") or card_path.stem
    card["card_id"] = card_id
    fields = card_to_fields(card)

    record_map = config.setdefault("record_map", {})
    record_id = record_map.get(card_id)
    if not record_id:
        items = client.search_records(app_token, table_id, "card_id", card_id)
        if items:
            record_id = items[0]["record_id"]

    if record_id:
        client.update_record(app_token, table_id, record_id, fields)
    else:
        record_id = client.create_record(app_token, table_id, fields)
        record_map[card_id] = record_id

    save_config(workspace, config)
    print(json.dumps({"ok": True, "card_id": card_id, "record_id": record_id}, ensure_ascii=False))
    return 0


def cmd_apply_update(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    config = load_config(workspace)
    client = FeishuClient(config["app_id"], config["app_secret"])
    app_token = config["app_token"]
    tables = config["tables"]
    record_map = config.setdefault("record_map", {})

    card_id = payload["card_id"]
    cards_dir = workspace / "cards"
    card_path = cards_dir / f"{card_id}.yaml"
    card = {}
    if card_path.is_file():
        card = yaml.safe_load(card_path.read_text(encoding="utf-8")) or {}

    card.setdefault("card_id", card_id)
    if payload.get("stage"):
        card["current_stage"] = payload["stage"]
    if payload.get("interview_patch"):
        card.setdefault("interview", {}).update(payload["interview_patch"])
    if payload.get("next_action"):
        card["next_action"] = payload["next_action"]
    if payload.get("company"):
        card["company"] = payload["company"]
    if payload.get("role"):
        card["role"] = payload["role"]
    card["updated_at"] = str(date.today())

    fields = card_to_fields(card)
    record_id = record_map.get(card_id)
    if not record_id:
        items = client.search_records(app_token, tables["applications"], "card_id", card_id)
        if items:
            record_id = items[0]["record_id"]
    if record_id:
        client.update_record(app_token, tables["applications"], record_id, fields)
    else:
        record_id = client.create_record(app_token, tables["applications"], fields)
        record_map[card_id] = record_id

    timeline_entry = payload.get("timeline_entry")
    if timeline_entry:
        tl_fields: dict[str, Any] = {
            "关联投递": [record_id],
            "阶段": timeline_entry.get("stage", ""),
            "来源": timeline_entry.get("source", "用户口述"),
            "备注": timeline_entry.get("note", ""),
        }
        ts = ms_timestamp(timeline_entry.get("at"))
        if ts:
            tl_fields["时间"] = ts
        client.create_record(app_token, tables["timeline"], tl_fields)

    for item in payload.get("review_items") or []:
        review_fields = {
            "考点": item,
            "状态": "待复盘",
            "登记日": ms_timestamp(str(date.today())),
        }
        if card.get("company"):
            review_fields["公司"] = card["company"]
        if card.get("role"):
            review_fields["岗位"] = card["role"]
        client.create_record(app_token, tables["review_queue"], review_fields)

    save_config(workspace, config)
    print(json.dumps({"ok": True, "card_id": card_id, "record_id": record_id}, ensure_ascii=False))
    return 0


def cmd_import_obsidian_wx(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    obsidian_path = Path(args.obsidian_wx).expanduser().resolve()
    if not obsidian_path.is_file():
        raise FileNotFoundError(f"找不到 obsidian-wx 配置：{obsidian_path}")

    wx = load_obsidian_wx_feishu(obsidian_path)
    if not wx["app_id"]:
        raise ValueError("obsidian-wx data.json 里没有 feishuAppId")

    rel_path = os.path.relpath(obsidian_path, workspace)
    config_path = workspace / "feishu-config.yaml"
    existing = {}
    if config_path.is_file():
        existing = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    config = {
        "app_id": wx["app_id"],
        "app_secret_env": existing.get("app_secret_env", "FEISHU_APP_SECRET"),
        "obsidian_wx_data_path": rel_path,
        "folder_token": existing.get("folder_token", ""),
        "app_token": existing.get("app_token", ""),
        "app_url": existing.get("app_url", ""),
        "tables": existing.get(
            "tables",
            {"applications": "", "timeline": "", "review_queue": ""},
        ),
        "record_map": existing.get("record_map") or {},
        "initialized_at": existing.get("initialized_at", ""),
        "notes": [
            "app_id 来自 obsidian-wx；app_secret 默认读环境变量 FEISHU_APP_SECRET。",
            "obsidian-wx 若使用 SecretStorage，需手动 export 一次密钥，或从火山 wx-proxy 拉 client-config。",
            "obsidian-wx 当前用于飞书知识库发文，求职进度需额外开通 bitable:app / base:app:create 权限后 init。",
        ],
    }
    save_config(workspace, config)

    kb_names = [item.get("name", "") for item in wx["knowledge_bases"] if isinstance(item, dict)]
    print(
        json.dumps(
            {
                "ok": True,
                "app_id": wx["app_id"],
                "app_secret_source": "env" if wx["app_secret"] == "obsidian-wx:secret-storage:v1" else "obsidian-wx-data.json",
                "knowledge_bases": kb_names,
                "config_path": str(workspace / "feishu-config.yaml"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_ping(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    config = load_config(workspace)
    client = FeishuClient(config["app_id"], config["app_secret"])
    client._ensure_token()
    print(json.dumps({"ok": True, "app_token": config.get("app_token", "")}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Feishu Bitable sync for laowang-qiuzhi-jindu")
    parser.add_argument("--workspace", default=str(default_workspace("2027-fall")))
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create Feishu bitable and write feishu-config.yaml")
    p_init.add_argument("--title", default="")
    p_init.set_defaults(func=cmd_init)

    p_import = sub.add_parser("import-obsidian-wx", help="Import app_id from obsidian-wx data.json")
    p_import.add_argument(
        "--obsidian-wx",
        default=str(Path(__file__).resolve().parents[5] / ".obsidian/plugins/obsidian-wx/data.json"),
    )
    p_import.set_defaults(func=cmd_import_obsidian_wx)

    p_ping = sub.add_parser("ping", help="Test app credentials")
    p_ping.set_defaults(func=cmd_ping)

    p_sync = sub.add_parser("sync-card", help="Upsert one local card YAML to 投递主表")
    p_sync.add_argument("--card", required=True)
    p_sync.set_defaults(func=cmd_sync_card)

    p_apply = sub.add_parser("apply-update", help="Apply chat-update JSON payload to Feishu")
    p_apply.add_argument("--payload", required=True)
    p_apply.set_defaults(func=cmd_apply_update)

    args = parser.parse_args()
    try:
        return args.func(args)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

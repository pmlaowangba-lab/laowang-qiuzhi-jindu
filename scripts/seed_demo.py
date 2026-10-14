#!/usr/bin/env python3
"""Seed laowang-qiuzhi-jindu workspace with demo application data."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

DEMO_CARDS = [
    {
        "card_id": "xiaohongshu-shequ-zengzhang-pm-intern",
        "company": "小红书",
        "role": "社区增长产品经理实习",
        "city": "上海",
        "channel": "官网校招",
        "resume_snapshot_id": "resume-v3-xhs-community",
        "current_stage": "面试中",
        "interview": {
            "round": "一面",
            "status": "completed",
            "completed_at": "2026-09-26T15:20:00+08:00",
            "focus_topics": ["兴趣社区战略", "发帖量拆解", "活跃下降归因", "男性用户增长"],
        },
        "next_action": "等二面通知；周五 18:00 前无消息查官网",
        "timeline": [
            {"at": "2026-09-20", "stage": "已投", "source": "用户口述", "note": "官网校招提交"},
            {"at": "2026-09-24T10:00:00+08:00", "stage": "面试中", "source": "邮件", "note": "通知业务一面"},
            {
                "at": "2026-09-26T15:20:00+08:00",
                "stage": "面试中",
                "source": "用户口述",
                "note": "一面完成；小数指标、男性增长调性答得虚",
            },
        ],
    },
    {
        "card_id": "kuaishou-shequ-pm-intern",
        "company": "快手",
        "role": "社区产品实习",
        "city": "北京",
        "channel": "官网",
        "resume_snapshot_id": "resume-v2-growth",
        "current_stage": "面试中",
        "interview": {
            "round": "二面",
            "status": "completed",
            "completed_at": "2026-09-26T14:00:00+08:00",
            "focus_topics": ["指标归因", "漏斗分析", "社区调性"],
        },
        "next_action": "等结果；补强漏斗拆解进 mianshi-zhu",
        "timeline": [
            {"at": "2026-09-08", "stage": "已投", "source": "用户口述", "note": "网申提交"},
            {"at": "2026-09-15T14:00:00+08:00", "stage": "面试中", "source": "用户口述", "note": "一面完成"},
            {
                "at": "2026-09-26T14:00:00+08:00",
                "stage": "面试中",
                "source": "用户口述",
                "note": "二面完成；漏斗分析答得不满意",
            },
        ],
    },
    {
        "card_id": "meituan-ai-pm-intern",
        "company": "美团",
        "role": "AI 产品实习",
        "city": "北京",
        "channel": "官网",
        "resume_snapshot_id": "resume-v2-growth",
        "current_stage": "测评中",
        "interview": {"round": "", "status": "", "focus_topics": []},
        "next_action": "等测评结果，勿重复做测评",
        "timeline": [
            {"at": "2026-09-18", "stage": "已投", "source": "用户口述", "note": "网申提交"},
            {"at": "2026-09-22T09:00:00+08:00", "stage": "测评中", "source": "邮件", "note": "收到北森测评链接"},
            {
                "at": "2026-09-25T20:30:00+08:00",
                "stage": "测评中",
                "source": "用户口述",
                "note": "测评已交卷，待结果（非通过）",
            },
        ],
    },
    {
        "card_id": "byte-douyin-growth-pm-intern",
        "company": "字节跳动",
        "role": "抖音增长产品实习",
        "city": "北京",
        "channel": "BOSS",
        "resume_snapshot_id": "resume-v2-growth",
        "current_stage": "面试中",
        "interview": {
            "round": "一面",
            "status": "scheduled",
            "scheduled_at": "2026-09-29T10:00:00+08:00",
            "focus_topics": [],
        },
        "next_action": "下周一 10:00 业务一面（飞书视频）",
        "timeline": [
            {"at": "2026-09-12", "stage": "已投", "source": "用户口述", "note": "BOSS 投递"},
            {
                "at": "2026-09-26T11:00:00+08:00",
                "stage": "面试中",
                "source": "邮件",
                "note": "约下周一 10:00 业务一面，线上",
            },
        ],
    },
    {
        "card_id": "pdd-cuxiao-pm-intern",
        "company": "拼多多",
        "role": "促销活动产品实习",
        "city": "上海",
        "channel": "官网",
        "resume_snapshot_id": "resume-v1-pdd",
        "current_stage": "已投",
        "interview": {"round": "", "status": "", "focus_topics": []},
        "next_action": "等笔试/测评通知",
        "timeline": [
            {"at": "2026-09-23", "stage": "已投", "source": "用户口述", "note": "官网提交，简历强调 PDD 实习经历"},
        ],
    },
]

REVIEW_ITEMS = [
    {"company": "小红书", "role": "社区增长产品经理实习", "topic": "社区用户/亲书作者小数指标口径", "date": "2026-09-26"},
    {"company": "小红书", "role": "社区增长产品经理实习", "topic": "男性用户增长对社区调性的副作用", "date": "2026-09-26"},
    {"company": "快手", "role": "社区产品实习", "topic": "漏斗分析-指标归因题", "date": "2026-09-26"},
]

FOLLOW_UP = """# 跟进行动

## 待办（有截止日期）

- [ ] 【小红书】社区增长 PM — 周五 18:00 前无消息则官网查状态（2026-09-26）
- [ ] 【字节】抖音增长 — 下周一 10:00 业务一面，飞书视频（2026-09-29）
- [ ] 【快手】社区产品 — 二面后等结果，补强漏斗题进 mianshi-zhu（2026-09-26）
- [ ] 【美团】AI 产品 — 测评已交卷，等结果勿重做（2026-09-25）

## 可选（无硬性截止）

- [ ] 小红书一面录音转写 → laowang-mianshi-fu 复盘

## 已完成
"""

REVIEW_QUEUE = """# 待复盘队列

| 公司 | 岗位 | 考点 | 登记日 | 状态 |
|------|------|------|--------|------|
| 小红书 | 社区增长产品经理实习 | 社区用户/亲书作者小数指标口径 | 2026-09-26 | 待复盘 |
| 小红书 | 社区增长产品经理实习 | 男性用户增长对社区调性的副作用 | 2026-09-26 | 待复盘 |
| 快手 | 社区产品实习 | 漏斗分析-指标归因题 | 2026-09-26 | 待复盘 |
"""

MASTER_PIPELINE = """# 投递主表

| 公司 | 岗位 | 渠道 | 投递日 | 简历版本 | 阶段 | 轮次 | 下一步 | 更新日 |
|------|------|------|--------|----------|------|------|--------|--------|
| 小红书 | 社区增长产品经理实习 | 官网校招 | 2026-09-20 | resume-v3-xhs-community | 面试中 | 一面完成 | 等二面；周五查官网 | 2026-09-26 |
| 快手 | 社区产品实习 | 官网 | 2026-09-08 | resume-v2-growth | 面试中 | 二面完成 | 等结果；补漏斗题 | 2026-09-26 |
| 美团 | AI 产品实习 | 官网 | 2026-09-18 | resume-v2-growth | 测评中 | — | 等测评结果 | 2026-09-25 |
| 字节跳动 | 抖音增长产品实习 | BOSS | 2026-09-12 | resume-v2-growth | 面试中 | 一面已约 | 下周一 10:00 一面 | 2026-09-26 |
| 拼多多 | 促销活动产品实习 | 官网 | 2026-09-23 | resume-v1-pdd | 已投 | — | 等笔试通知 | 2026-09-23 |
"""

DASHBOARD = """# 求职进度总览

> 赛季：2027-fall | 更新：2026-09-26 | skill: laowang-qiuzhi-jindu（演示数据）

## 一眼看板

| 阶段 | 数量 | 公司 |
|------|------|------|
| 面试中 | 3 | 小红书、快手、字节 |
| 测评/笔试 | 1 | 美团（测评待结果） |
| 已投等待 | 1 | 拼多多 |
| Offer/OC | 0 | — |
| 拒信/放弃 | 0 | — |

## 本周优先（来自 follow-up.md）

1. **字节** 下周一 10:00 一面 — 用 mianshi-zhu 过抖音增长稿
2. **小红书** 周五前查官网 — 一面后等二面
3. **快手** 二面后等结果 — 漏斗题进待复盘
4. **美团** 测评已交卷 — 不要重复做

## 待复盘热点（来自 review-queue.md）

- 小红书：小数指标口径、男性增长调性权衡
- 快手：漏斗分析 / 指标归因

## 各厂明细

| 公司 | 岗位 | 阶段 | 轮次 | 下一步 | 更新日 |
|------|------|------|------|--------|--------|
| 小红书 | 社区增长产品经理实习 | 面试中 | 一面完成 | 等二面 | 2026-09-26 |
| 快手 | 社区产品实习 | 面试中 | 二面完成 | 等结果 | 2026-09-26 |
| 美团 | AI 产品实习 | 测评中 | — | 等结果 | 2026-09-25 |
| 字节跳动 | 抖音增长产品实习 | 面试中 | 一面已约 | 9/29 10:00 | 2026-09-26 |
| 拼多多 | 促销活动产品实习 | 已投 | — | 等通知 | 2026-09-23 |
"""


def write_local(workspace: Path) -> None:
    cards_dir = workspace / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)
    (workspace / "audit").mkdir(exist_ok=True)

    for card in DEMO_CARDS:
        payload = {**card, "updated_at": "2026-09-26"}
        path = cards_dir / f"{card['card_id']}.yaml"
        path.write_text(yaml.dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")

    (workspace / "master-pipeline.md").write_text(MASTER_PIPELINE, encoding="utf-8")
    (workspace / "progress-dashboard.md").write_text(DASHBOARD, encoding="utf-8")
    (workspace / "follow-up.md").write_text(FOLLOW_UP, encoding="utf-8")
    (workspace / "review-queue.md").write_text(REVIEW_QUEUE, encoding="utf-8")


def sync_feishu(workspace: Path) -> None:
    feishu_script = SCRIPT_DIR / "feishu_bitable.py"
    config_path = workspace / "feishu-config.yaml"
    if not config_path.is_file():
        print("SKIP feishu: no feishu-config.yaml", file=sys.stderr)
        return

    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not config.get("app_token"):
        print("SKIP feishu: app_token empty", file=sys.stderr)
        return

    for card in DEMO_CARDS:
        subprocess.run(
            [
                sys.executable,
                str(feishu_script),
                "--workspace",
                str(workspace),
                "sync-card",
                "--card",
                str(workspace / "cards" / f"{card['card_id']}.yaml"),
            ],
            check=True,
        )

    for item in REVIEW_ITEMS:
        payload = {
            "card_id": card_id_from_company(item["company"]),
            "review_items": [f"{item['topic']}-{item['company']}"],
        }
        tmp = workspace / "audit" / f"seed-review-{item['company']}.json"
        tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        subprocess.run(
            [
                sys.executable,
                str(feishu_script),
                "--workspace",
                str(workspace),
                "apply-update",
                "--payload",
                str(tmp),
            ],
            check=True,
        )


def card_id_from_company(company: str) -> str:
    mapping = {
        "小红书": "xiaohongshu-shequ-zengzhang-pm-intern",
        "快手": "kuaishou-shequ-pm-intern",
    }
    return mapping.get(company, "xiaohongshu-shequ-zengzhang-pm-intern")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=SKILL_DIR / "workspace" / "2027-fall")
    parser.add_argument("--no-feishu", action="store_true")
    args = parser.parse_args()

    workspace = args.workspace.expanduser().resolve()
    write_local(workspace)
    print(f"OK: seeded {len(DEMO_CARDS)} cards -> {workspace / 'cards'}")

    if not args.no_feishu:
        try:
            sync_feishu(workspace)
            print("OK: synced to Feishu bitable")
        except subprocess.CalledProcessError as exc:
            print(f"WARN: Feishu sync failed ({exc}); local data is ready", file=sys.stderr)
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

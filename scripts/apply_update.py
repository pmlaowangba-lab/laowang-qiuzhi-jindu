#!/usr/bin/env python3
"""Apply structured chat-update payload to card YAML."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path

import yaml


def load_card(cards_dir: Path, card_id: str) -> dict:
    path = cards_dir / f"{card_id}.yaml"
    if not path.is_file():
        data = {"card_id": card_id, "timeline": [], "updated_at": str(date.today())}
    else:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data, path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--payload", type=Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.payload.read_text(encoding="utf-8"))
    card_id = payload["card_id"]
    cards_dir = args.workspace / "cards"
    cards_dir.mkdir(exist_ok=True)

    data, path = load_card(cards_dir, card_id)
    if payload.get("stage"):
        data["current_stage"] = payload["stage"]
    if payload.get("timeline_entry"):
        data.setdefault("timeline", []).append(payload["timeline_entry"])
    if payload.get("interview_patch"):
        data.setdefault("interview", {}).update(payload["interview_patch"])
    data["updated_at"] = str(date.today())
    path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    audit = args.workspace / "audit"
    audit.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    (audit / f"chat-update-{stamp}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK: updated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

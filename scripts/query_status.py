#!/usr/bin/env python3
"""Query application card status."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--company", default="")
    parser.add_argument("--card-id", default="")
    args = parser.parse_args()

    cards_dir = args.workspace / "cards"
    if not cards_dir.is_dir():
        print("No cards yet")
        return 0

    for path in sorted(cards_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if args.card_id and data.get("card_id") != args.card_id:
            continue
        if args.company and args.company not in str(data.get("company", "")):
            continue
        print(f"=== {data.get('company')} — {data.get('role')} ===")
        print(f"阶段: {data.get('current_stage')}")
        iv = data.get("interview") or {}
        if iv:
            print(f"面试: {iv.get('round')} / {iv.get('status')}")
        tl = data.get("timeline") or []
        for row in tl[-3:]:
            print(f"  - {row.get('at')}: {row.get('note')}")
        print(f"下一步: {data.get('next_action', '—')}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

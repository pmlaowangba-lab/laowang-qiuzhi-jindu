#!/usr/bin/env python3
"""Init laowang-qiuzhi-jindu workspace."""

from __future__ import annotations

import argparse
import shutil
from datetime import date
from pathlib import Path

DIRS = ["cards", "timeline", "audit"]
ASSETS = [
    ("progress-dashboard-template.md", "progress-dashboard.md"),
    ("master-pipeline-template.md", "master-pipeline.md"),
    ("follow-up-template.md", "follow-up.md"),
    ("review-queue-template.md", "review-queue.md"),
]


def default_root(season: str) -> Path:
    return Path(__file__).resolve().parent.parent / "workspace" / season


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", default="2027-fall")
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args()

    root = (args.root or default_root(args.season)).expanduser().resolve()
    assets = Path(__file__).parent.parent / "assets"
    root.mkdir(parents=True, exist_ok=True)
    for d in DIRS:
        (root / d).mkdir(exist_ok=True)

    for src_name, dst_name in ASSETS:
        dst = root / dst_name
        if not dst.exists():
            shutil.copy(assets / src_name, dst)

    meta = root / "season-meta.txt"
    if not meta.exists():
        meta.write_text(f"season={args.season}\ncreated={date.today()}\n", encoding="utf-8")

    print(f"OK: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

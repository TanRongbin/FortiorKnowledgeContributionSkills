#!/usr/bin/env python3
"""Pretty-print mock submissions using explicit UTF-8 decoding."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent / "gateway" / "mock-submissions.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(description="View Fortior mock submissions with correct UTF-8 decoding")
    parser.add_argument("--file", default=str(DEFAULT_PATH), help="JSONL file to read")
    parser.add_argument("--last", type=int, default=0, help="Show only the last N records; 0 means all")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        raise SystemExit(f"Mock file not found: {path}")

    records = []
    with path.open("r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"Invalid JSON on line {lineno}: {exc}") from exc

    if args.last > 0:
        records = records[-args.last:]

    if not records:
        print("No mock submissions found.")
        return

    for index, record in enumerate(records, 1):
        print(f"\n=== Mock submission {index}/{len(records)} ===")
        print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

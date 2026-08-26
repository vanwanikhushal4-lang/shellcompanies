#!/usr/bin/env python3
"""Search page-level extraction with line context."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pattern")
    parser.add_argument("--company")
    parser.add_argument("--path")
    parser.add_argument("--context", type=int, default=2)
    parser.add_argument("--max", type=int, default=50)
    parser.add_argument("--input", type=Path, default=Path("tmp/pdfs/company_intelligence/page_text.jsonl"))
    args = parser.parse_args()

    pattern = re.compile(args.pattern, re.IGNORECASE)
    matches = 0
    with args.input.open(encoding="utf-8") as handle:
        for raw in handle:
            record = json.loads(raw)
            if args.company and args.company.lower() not in record["company_folder"].lower():
                continue
            if args.path and args.path.lower() not in record["relative_path"].lower():
                continue
            lines = record["text"].splitlines()
            indexes = [index for index, line in enumerate(lines) if pattern.search(line)]
            if not indexes:
                continue
            print(f"\n===== {record['relative_path']} | PAGE {record['page']} =====")
            printed = set()
            for index in indexes:
                start = max(0, index - args.context)
                end = min(len(lines), index + args.context + 1)
                for line_index in range(start, end):
                    if line_index not in printed:
                        print(f"{line_index + 1:04d}: {lines[line_index]}")
                        printed.add(line_index)
                matches += 1
                if matches >= args.max:
                    return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

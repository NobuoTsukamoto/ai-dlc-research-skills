#!/usr/bin/env python3
"""Check or update the Markdown reading log without external dependencies."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

HEADER_PREFIX = "| 登録日 | ステータス | タイトル |"


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = re.sub(r"https?://(dx\.)?doi\.org/", "", value)
    value = re.sub(r"\bdoi\s*:\s*", "", value)
    return re.sub(r"[^0-9a-z\u3040-\u30ff\u3400-\u9fff]+", "", value)


def normalize_doi(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value, flags=re.I)
    value = re.sub(r"^doi\s*:\s*", "", value, flags=re.I)
    return value.casefold().rstrip(" .")


def escape_cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").strip()


@dataclass
class Row:
    cells: list[str]

    @property
    def title(self) -> str:
        return self.cells[2] if len(self.cells) > 2 else ""

    @property
    def reference(self) -> str:
        return self.cells[9] if len(self.cells) > 9 else ""


def parse_table_rows(text: str) -> list[Row]:
    rows: list[Row] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith(HEADER_PREFIX):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table:
            if not line.startswith("|"):
                break
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
            if any(cells):
                rows.append(Row(cells))
    return rows


def find_duplicates(rows: Iterable[Row], title: str, doi: str) -> list[Row]:
    title_key = normalize_text(title)
    doi_key = normalize_doi(doi) if doi else ""
    matches: list[Row] = []
    for row in rows:
        row_title_key = normalize_text(row.title)
        row_ref = normalize_doi(row.reference)
        if doi_key and doi_key in row_ref:
            matches.append(row)
        elif title_key and row_title_key == title_key:
            matches.append(row)
    return matches


def insert_row(text: str, row_line: str) -> str:
    lines = text.splitlines()
    header_index = next(
        (i for i, line in enumerate(lines) if line.startswith(HEADER_PREFIX)), None
    )
    if header_index is None:
        raise ValueError("Reading log table header was not found.")
    separator_index = header_index + 1
    if separator_index >= len(lines) or not lines[separator_index].startswith("|---"):
        raise ValueError("Reading log table separator was not found.")

    insert_at = separator_index + 1
    while insert_at < len(lines) and lines[insert_at].startswith("|"):
        cells = [c.strip() for c in lines[insert_at].strip("|").split("|")]
        if not any(cells):
            lines[insert_at] = row_line
            return "\n".join(lines) + ("\n" if text.endswith("\n") else "")
        insert_at += 1

    lines.insert(insert_at, row_line)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def cmd_check(args: argparse.Namespace) -> int:
    path = Path(args.log)
    rows = parse_table_rows(path.read_text(encoding="utf-8"))
    matches = find_duplicates(rows, args.title, args.doi or "")
    if matches:
        print("DUPLICATE")
        for row in matches:
            print(" | ".join(row.cells))
        return 2
    print("NOT_FOUND")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    path = Path(args.log)
    text = path.read_text(encoding="utf-8")
    matches = find_duplicates(parse_table_rows(text), args.title, args.url or "")
    if matches and not args.force:
        print(
            "Duplicate candidate found. Use --force only after review.", file=sys.stderr
        )
        return 2

    values = [
        args.date,
        args.status,
        args.title,
        args.authors,
        str(args.year),
        args.type,
        args.venue,
        args.topics,
        str(args.score),
        args.url,
        args.notes,
    ]
    row_line = "| " + " | ".join(escape_cell(v) for v in values) + " |"
    path.write_text(insert_row(text, row_line), encoding="utf-8")
    print(f"Added: {args.title}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check")
    check.add_argument("--log", required=True)
    check.add_argument("--title", required=True)
    check.add_argument("--doi")
    check.set_defaults(func=cmd_check)

    add = sub.add_parser("add")
    add.add_argument("--log", required=True)
    add.add_argument("--date", required=True)
    add.add_argument(
        "--status",
        required=True,
        choices=["candidate", "selected", "reading", "read", "hold", "excluded"],
    )
    add.add_argument("--title", required=True)
    add.add_argument("--authors", required=True)
    add.add_argument("--year", required=True, type=int)
    add.add_argument("--type", required=True)
    add.add_argument("--venue", required=True)
    add.add_argument("--topics", required=True)
    add.add_argument("--score", required=True, type=int, choices=range(0, 11))
    add.add_argument("--url", required=True)
    add.add_argument("--notes", default="")
    add.add_argument("--force", action="store_true")
    add.set_defaults(func=cmd_add)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check or update the Markdown reading log without external dependencies."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit, urlunsplit

HEADER_PREFIX = "| 登録日 | 読了日 | ステータス | タイトル |"
DOI_PATTERN = re.compile(r"10\.\d{4,9}/[-._;()/:a-z0-9]+", re.I)
TITLE_INDEX = 3
REFERENCE_INDEX = 10


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = re.sub(r"https?://(dx\.)?doi\.org/", "", value)
    value = re.sub(r"\bdoi\s*:\s*", "", value)
    return re.sub(r"[^0-9a-z\u3040-\u30ff\u3400-\u9fff]+", "", value)


def normalize_doi(value: str) -> str:
    match = DOI_PATTERN.search(unicodedata.normalize("NFKC", value))
    if not match:
        return ""
    doi = match.group(0).casefold().rstrip(".,;")
    while doi.endswith(")") and doi.count(")") > doi.count("("):
        doi = doi[:-1]
    return doi


def normalize_reference(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip()
    doi = normalize_doi(value)
    if doi:
        return f"doi:{doi}"

    try:
        parts = urlsplit(value)
    except ValueError:
        return value

    if parts.scheme.casefold() not in {"http", "https"} or not parts.netloc:
        return value

    return urlunsplit(
        (
            parts.scheme.casefold(),
            parts.netloc.casefold(),
            parts.path.rstrip("/"),
            parts.query,
            "",
        )
    )


def escape_cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").strip()


def iso_date(value: str) -> str:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected YYYY-MM-DD") from exc
    return value


@dataclass
class Row:
    cells: list[str]

    @property
    def title(self) -> str:
        return self.cells[TITLE_INDEX] if len(self.cells) > TITLE_INDEX else ""

    @property
    def reference(self) -> str:
        return (
            self.cells[REFERENCE_INDEX] if len(self.cells) > REFERENCE_INDEX else ""
        )


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


def find_duplicates(rows: Iterable[Row], title: str, reference: str) -> list[Row]:
    title_key = normalize_text(title)
    doi_key = normalize_doi(reference)
    reference_key = normalize_reference(reference) if reference else ""
    matches: list[Row] = []
    for row in rows:
        row_title_key = normalize_text(row.title)
        row_doi_key = normalize_doi(row.reference)
        row_reference_key = normalize_reference(row.reference)
        if doi_key and row_doi_key and doi_key == row_doi_key:
            matches.append(row)
        elif (
            reference_key
            and row_reference_key
            and reference_key == row_reference_key
        ):
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
    if args.status == "read" and not args.read_date:
        print("--read-date is required when --status is read.", file=sys.stderr)
        return 2

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
        args.read_date,
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
    add.add_argument("--date", required=True, type=iso_date)
    add.add_argument("--read-date", default="", type=iso_date)
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

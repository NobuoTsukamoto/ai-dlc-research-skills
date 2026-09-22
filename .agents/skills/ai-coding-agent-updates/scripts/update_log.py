#!/usr/bin/env python3
"""Maintain the canonical JSONL log for AI coding-agent product updates."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TOOLS = (
    "github-copilot",
    "github-copilot-cli",
    "github-copilot-app",
    "openai-codex",
    "claude-code",
    "cursor",
    "antigravity-cli",
)
MAX_SUMMARY_LENGTH = 500
MAX_IMPACT_LENGTH = 500
MIN_SUMMARY_IMPACT_OVERLAP = 40
SOURCE_TYPES = (
    "official-changelog",
    "official-release",
    "official-docs",
    "official-blog",
    "official-repository",
)
RELEASE_STAGES = ("stable", "preview", "experimental", "prerelease", "unknown")
IMPORTANCE_LEVELS = ("high", "medium", "low")
TRACKING_QUERY_KEYS = {
    "authuser",
    "fbclid",
    "gclid",
    "hl",
    "ref",
    "source",
}
REQUIRED_FIELDS = {
    "schema_version",
    "id",
    "tool",
    "published_date",
    "discovered_date",
    "title",
    "url",
    "source_type",
    "release_stage",
    "importance",
    "summary",
    "impact",
}


class LogError(ValueError):
    """Raised when the update log or command input is invalid."""


def longest_common_substring(left: str, right: str) -> str:
    """Return the longest exact, consecutive substring shared by two values."""
    previous = [0] * (len(right) + 1)
    longest = ""
    for left_index, left_character in enumerate(left, start=1):
        current = [0]
        for right_index, right_character in enumerate(right, start=1):
            if left_character == right_character:
                length = previous[right_index - 1] + 1
                current.append(length)
                if length > len(longest):
                    longest = left[left_index - length : left_index]
            else:
                current.append(0)
        previous = current
    return longest


def validate_text_fields(summary: Any, impact: Any) -> None:
    if not isinstance(summary, str):
        raise LogError("summary must be a string")
    if not isinstance(impact, str):
        raise LogError("impact must be a string")

    summary = summary.strip()
    impact = impact.strip()
    if not summary:
        raise LogError("summary cannot be empty")
    if not impact:
        raise LogError("impact cannot be empty")
    if len(summary) > MAX_SUMMARY_LENGTH:
        raise LogError(
            f"summary cannot exceed {MAX_SUMMARY_LENGTH} characters"
        )
    if len(impact) > MAX_IMPACT_LENGTH:
        raise LogError(f"impact cannot exceed {MAX_IMPACT_LENGTH} characters")

    overlap = longest_common_substring(summary, impact)
    if len(overlap) >= MIN_SUMMARY_IMPACT_OVERLAP:
        raise LogError(
            "summary and impact share a consecutive phrase of at least "
            f"{MIN_SUMMARY_IMPACT_OVERLAP} characters; rewrite the summary "
            "and inference separately"
        )


def parse_iso_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise LogError(f"{field_name} must be a valid YYYY-MM-DD date: {value}") from exc


def normalize_title(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(character for character in normalized if character.isalnum())


def canonicalize_url(value: str) -> str:
    parts = urlsplit(value.strip())
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise LogError(f"url must be an absolute HTTP(S) URL: {value}")

    hostname = parts.hostname.lower()
    try:
        port = parts.port
    except ValueError as exc:
        raise LogError(f"url contains an invalid port: {value}") from exc
    if port and not (
        (parts.scheme.lower() == "http" and port == 80)
        or (parts.scheme.lower() == "https" and port == 443)
    ):
        hostname = f"{hostname}:{port}"

    query = [
        (key, query_value)
        for key, query_value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
        and key.lower() not in TRACKING_QUERY_KEYS
    ]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit(
        (
            parts.scheme.lower(),
            hostname,
            path,
            urlencode(sorted(query)),
            "",
        )
    )


def load_log(path: Path, *, validate_text: bool = False) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    items: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw_line.strip():
            continue
        try:
            item = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise LogError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(item, dict):
            raise LogError(f"{path}:{line_number}: each line must be a JSON object")
        missing = REQUIRED_FIELDS - set(item)
        if missing:
            raise LogError(
                f"{path}:{line_number}: missing fields: {', '.join(sorted(missing))}"
            )
        if item["tool"] not in TOOLS:
            raise LogError(f"{path}:{line_number}: unknown tool: {item['tool']}")
        if item["source_type"] not in SOURCE_TYPES:
            raise LogError(
                f"{path}:{line_number}: unknown source_type: {item['source_type']}"
            )
        if item["release_stage"] not in RELEASE_STAGES:
            raise LogError(
                f"{path}:{line_number}: unknown release_stage: {item['release_stage']}"
            )
        if item["importance"] not in IMPORTANCE_LEVELS:
            raise LogError(
                f"{path}:{line_number}: unknown importance: {item['importance']}"
            )
        parse_iso_date(str(item["published_date"]), "published_date")
        parse_iso_date(str(item["discovered_date"]), "discovered_date")
        canonicalize_url(str(item["url"]))
        if validate_text:
            validate_text_fields(item["summary"], item["impact"])
        items.append(item)
    return items


def find_duplicate(
    items: list[dict[str, Any]], tool: str, title: str, url: str
) -> dict[str, Any] | None:
    canonical_url = canonicalize_url(url)
    normalized_title = normalize_title(title)
    if not normalized_title:
        raise LogError("title must contain at least one letter or digit")
    for item in items:
        if (
            item["tool"] == tool
            and canonicalize_url(str(item["url"])) == canonical_url
        ):
            return item
        if (
            item["tool"] == tool
            and normalize_title(str(item["title"])) == normalized_title
        ):
            return item
    return None


def make_id(tool: str, title: str, url: str) -> str:
    identity = f"{tool}\0{canonicalize_url(url)}\0{normalize_title(title)}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]


def append_item(path: Path, item: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(item, ensure_ascii=False, sort_keys=True)
    needs_separator = path.exists() and path.stat().st_size > 0
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        if needs_separator:
            with path.open("rb") as existing:
                existing.seek(-1, 2)
                if existing.read(1) not in {b"\n", b"\r"}:
                    stream.write("\n")
        stream.write(serialized + "\n")


def command_check(args: argparse.Namespace) -> int:
    items = load_log(args.log)
    duplicate = find_duplicate(items, args.tool, args.title, args.url)
    if duplicate:
        print(f"DUPLICATE\t{duplicate['id']}")
    else:
        print("NOT_FOUND")
    return 0


def command_add(args: argparse.Namespace) -> int:
    published_date = parse_iso_date(args.published_date, "published_date")
    discovered_date = parse_iso_date(args.discovered_date, "discovered_date")
    if discovered_date < published_date:
        raise LogError("discovered_date cannot be earlier than published_date")
    validate_text_fields(args.summary, args.impact)

    items = load_log(args.log)
    duplicate = find_duplicate(items, args.tool, args.title, args.url)
    if duplicate:
        print(f"DUPLICATE\t{duplicate['id']}")
        return 0

    item = {
        "schema_version": 1,
        "id": make_id(args.tool, args.title, args.url),
        "tool": args.tool,
        "published_date": args.published_date,
        "discovered_date": args.discovered_date,
        "title": args.title.strip(),
        "url": canonicalize_url(args.url),
        "source_type": args.source_type,
        "release_stage": args.release_stage,
        "importance": args.importance,
        "summary": args.summary.strip(),
        "impact": args.impact.strip(),
    }
    append_item(args.log, item)
    print(f"ADDED\t{item['id']}")
    return 0


def escape_markdown(value: Any) -> str:
    return str(value).replace("|", r"\|").replace("\r", " ").replace("\n", " ")


def command_list(args: argparse.Namespace) -> int:
    from_date = parse_iso_date(args.from_date, "from_date")
    to_date = parse_iso_date(args.to_date, "to_date")
    if to_date < from_date:
        raise LogError("to_date cannot be earlier than from_date")

    items = [
        item
        for item in load_log(args.log)
        if from_date
        <= parse_iso_date(str(item["published_date"]), "published_date")
        <= to_date
        and (args.tool is None or item["tool"] == args.tool)
    ]
    items.sort(key=lambda item: (item["published_date"], item["tool"], item["title"]))

    if args.format == "jsonl":
        for item in items:
            print(json.dumps(item, ensure_ascii=False, sort_keys=True))
        return 0

    print("| 公開日 | ツール | 重要度 | タイトル |")
    print("|---|---|---|---|")
    for item in items:
        title = escape_markdown(item["title"])
        url = escape_markdown(item["url"])
        print(
            f"| {item['published_date']} | {item['tool']} | "
            f"{item['importance']} | [{title}]({url}) |"
        )
    return 0


def command_validate(args: argparse.Namespace) -> int:
    items = load_log(args.log, validate_text=True)
    print(f"VALID\t{len(items)}")
    return 0


def add_common_candidate_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--tool", choices=TOOLS, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--url", required=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Check for a duplicate")
    add_common_candidate_arguments(check_parser)
    check_parser.set_defaults(handler=command_check)

    add_parser = subparsers.add_parser("add", help="Append a canonical update")
    add_common_candidate_arguments(add_parser)
    add_parser.add_argument("--published-date", required=True)
    add_parser.add_argument("--discovered-date", required=True)
    add_parser.add_argument("--source-type", choices=SOURCE_TYPES, required=True)
    add_parser.add_argument("--release-stage", choices=RELEASE_STAGES, required=True)
    add_parser.add_argument("--importance", choices=IMPORTANCE_LEVELS, required=True)
    add_parser.add_argument("--summary", required=True)
    add_parser.add_argument("--impact", required=True)
    add_parser.set_defaults(handler=command_add)

    list_parser = subparsers.add_parser("list", help="List updates in a date range")
    list_parser.add_argument("--log", type=Path, required=True)
    list_parser.add_argument("--from-date", required=True)
    list_parser.add_argument("--to-date", required=True)
    list_parser.add_argument("--tool", choices=TOOLS)
    list_parser.add_argument("--format", choices=("jsonl", "markdown"), default="jsonl")
    list_parser.set_defaults(handler=command_list)

    validate_parser = subparsers.add_parser(
        "validate", help="Validate the complete update log"
    )
    validate_parser.add_argument("--log", type=Path, required=True)
    validate_parser.set_defaults(handler=command_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (LogError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

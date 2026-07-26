#!/usr/bin/env python3
"""Validate the local Agent Skill package."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
SKILL_DIR = ROOT / ".agents/skills/ai-dlc-research"
SKILL = SKILL_DIR / "SKILL.md"
REQUIRED = [
    ROOT / "AGENTS.md",
    ROOT / ".github/copilot-instructions.md",
    ROOT / "research/research-policy.md",
    ROOT / "research/reading-log.md",
    SKILL,
    SKILL_DIR / "references/output-templates.md",
    SKILL_DIR / "references/search-strategy.md",
    SKILL_DIR / "references/source-quality.md",
    SKILL_DIR / "scripts/reading_log.py",
]
ALLOWED_FRONTMATTER = {"name", "description", "license", "allowed-tools", "metadata"}
REQUIRED_REFERENCES = (
    "research/research-policy.md",
    "research/reading-log.md",
    "references/output-templates.md",
    "references/search-strategy.md",
)


def validate_skill_text(text: str) -> list[str]:
    errors: list[str] = []
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    if not match:
        return ["SKILL.md must contain closed YAML frontmatter at the start."]

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return [f"SKILL.md frontmatter is invalid YAML: {exc}"]

    if not isinstance(frontmatter, dict):
        return ["SKILL.md frontmatter must be a YAML mapping."]

    unexpected = set(frontmatter) - ALLOWED_FRONTMATTER
    if unexpected:
        errors.append(
            "SKILL.md frontmatter has unexpected fields: "
            + ", ".join(sorted(unexpected))
        )

    name = frontmatter.get("name")
    if name != SKILL_DIR.name:
        errors.append(
            f"SKILL.md name must match its directory: expected {SKILL_DIR.name!r}."
        )

    description = frontmatter.get("description")
    if not isinstance(description, str) or len(description.strip()) < 40:
        errors.append("SKILL.md description is missing or too vague.")
    elif len(description) > 1024:
        errors.append("SKILL.md description exceeds 1024 characters.")
    elif "<" in description or ">" in description:
        errors.append("SKILL.md description cannot contain angle brackets.")

    for required_ref in REQUIRED_REFERENCES:
        if required_ref not in text:
            errors.append(f"SKILL.md must reference {required_ref}.")

    return errors


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"Missing: {path.relative_to(ROOT)}")

    if SKILL.exists():
        text = SKILL.read_text(encoding="utf-8")
        errors.extend(validate_skill_text(text))

    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALID")
    for path in REQUIRED:
        print(f"- {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

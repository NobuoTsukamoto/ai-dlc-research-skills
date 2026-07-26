#!/usr/bin/env python3
"""Validate the local Agent Skill package."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SKILL = ROOT / ".agents/skills/ai-driven-development-research/SKILL.md"
REQUIRED = [
    ROOT / "AGENTS.md",
    ROOT / ".github/copilot-instructions.md",
    ROOT / "research/research-policy.md",
    ROOT / "research/reading-log.md",
    SKILL,
]


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"Missing: {path.relative_to(ROOT)}")

    if SKILL.exists():
        text = SKILL.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append("SKILL.md must start with YAML frontmatter.")
        if not re.search(r"^name:\s*ai-driven-development-research\s*$", text, re.M):
            errors.append("SKILL.md has an unexpected or missing name.")
        match = re.search(r"^description:\s*(.+)$", text, re.M)
        if not match or len(match.group(1).strip()) < 40:
            errors.append("SKILL.md description is missing or too vague.")
        for required_ref in ("research/research-policy.md", "research/reading-log.md"):
            if required_ref not in text:
                errors.append(f"SKILL.md must reference {required_ref}.")

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

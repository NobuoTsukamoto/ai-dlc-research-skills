#!/usr/bin/env python3
"""Validate the local Agent Skill package."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
SKILL_DIR = ROOT / ".agents/skills/ai-dlc-research"
ROOT_REQUIRED = [
    ROOT / "AGENTS.md",
    ROOT / "LICENSE",
    ROOT / ".github/copilot-instructions.md",
    ROOT / ".github/workflows/ci.yml",
    ROOT / "research/research-policy.md",
    ROOT / "research/reading-log.md",
    ROOT / "updates/update-log.jsonl",
]
SKILL_REQUIREMENTS = {
    "ai-dlc-research": (
        "SKILL.md",
        "references/output-templates.md",
        "references/search-strategy.md",
        "references/source-quality.md",
        "scripts/reading_log.py",
    ),
    "ai-coding-agent-updates": (
        "SKILL.md",
        "agents/openai.yaml",
        "references/official-sources.md",
        "references/output-templates.md",
        "references/buzz-and-discovery.md",
        "scripts/update_log.py",
    ),
}
ALLOWED_FRONTMATTER = {"name", "description", "license", "allowed-tools", "metadata"}
RESEARCH_REQUIRED_REFERENCES = (
    "research/research-policy.md",
    "research/reading-log.md",
    "references/output-templates.md",
    "references/search-strategy.md",
    "references/source-quality.md",
)
UPDATE_REQUIRED_REFERENCES = (
    "references/official-sources.md",
    "references/output-templates.md",
    "references/buzz-and-discovery.md",
    "updates/update-log.jsonl",
)


def validate_skill_text(
    text: str,
    *,
    skill_dir: Path = SKILL_DIR,
    required_references: tuple[str, ...] = RESEARCH_REQUIRED_REFERENCES,
) -> list[str]:
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
    if name != skill_dir.name:
        errors.append(
            f"SKILL.md name must match its directory: expected {skill_dir.name!r}."
        )

    description = frontmatter.get("description")
    if not isinstance(description, str) or len(description.strip()) < 40:
        errors.append("SKILL.md description is missing or too vague.")
    elif len(description) > 1024:
        errors.append("SKILL.md description exceeds 1024 characters.")
    elif "<" in description or ">" in description:
        errors.append("SKILL.md description cannot contain angle brackets.")

    for required_ref in required_references:
        if required_ref not in text:
            errors.append(f"SKILL.md must reference {required_ref}.")

    if "TODO" in text:
        errors.append("SKILL.md contains unresolved TODO markers.")

    return errors


def main() -> int:
    errors: list[str] = []
    required = list(ROOT_REQUIRED)
    for skill_name, relative_paths in SKILL_REQUIREMENTS.items():
        skill_dir = ROOT / ".agents/skills" / skill_name
        required.extend(skill_dir / relative_path for relative_path in relative_paths)

    for path in required:
        if not path.exists():
            errors.append(f"Missing: {path.relative_to(ROOT)}")

    reference_requirements = {
        "ai-dlc-research": RESEARCH_REQUIRED_REFERENCES,
        "ai-coding-agent-updates": UPDATE_REQUIRED_REFERENCES,
    }
    for skill_name in SKILL_REQUIREMENTS:
        skill_dir = ROOT / ".agents/skills" / skill_name
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            text = skill_file.read_text(encoding="utf-8")
            errors.extend(
                f"{skill_name}: {error}"
                for error in validate_skill_text(
                    text,
                    skill_dir=skill_dir,
                    required_references=reference_requirements[skill_name],
                )
            )

    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALID")
    for path in required:
        print(f"- {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

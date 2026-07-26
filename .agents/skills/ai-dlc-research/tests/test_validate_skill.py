from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_skill.py"
spec = importlib.util.spec_from_file_location("validate_skill", SCRIPT)
validate_skill = importlib.util.module_from_spec(spec)
sys.modules["validate_skill"] = validate_skill
assert spec.loader is not None
spec.loader.exec_module(validate_skill)

VALID_SKILL = """---
name: ai-dlc-research
description: Research and review AI-driven software development evidence for weekly and monthly workflows.
license: MIT
---

Read research/research-policy.md and research/reading-log.md.
Use references/output-templates.md, references/search-strategy.md, and references/source-quality.md.
"""


class ValidateSkillTests(unittest.TestCase):
    def test_valid_skill(self):
        self.assertEqual(validate_skill.validate_skill_text(VALID_SKILL), [])

    def test_rejects_unclosed_frontmatter(self):
        text = VALID_SKILL.replace("---\n\nRead", "\nRead", 1)
        self.assertIn(
            "closed YAML frontmatter",
            " ".join(validate_skill.validate_skill_text(text)),
        )

    def test_rejects_invalid_yaml(self):
        text = VALID_SKILL.replace(
            "name: ai-dlc-research", "name: [ai-dlc-research"
        )
        self.assertIn("invalid YAML", " ".join(validate_skill.validate_skill_text(text)))

    def test_rejects_unexpected_frontmatter_field(self):
        text = VALID_SKILL.replace("license: MIT", "license: MIT\nunexpected: true")
        self.assertIn(
            "unexpected fields",
            " ".join(validate_skill.validate_skill_text(text)),
        )

    def test_validates_second_skill_name_and_references(self):
        skill_dir = Path("ai-coding-agent-updates")
        text = """---
name: ai-coding-agent-updates
description: Track official AI coding-agent product updates in daily, weekly, and monthly reports.
---

Read references/official-sources.md, references/output-templates.md, and
references/buzz-and-discovery.md. Store canonical updates in
updates/update-log.jsonl.
"""
        self.assertEqual(
            validate_skill.validate_skill_text(
                text,
                skill_dir=skill_dir,
                required_references=validate_skill.UPDATE_REQUIRED_REFERENCES,
            ),
            [],
        )

    def test_rejects_unresolved_todo(self):
        text = VALID_SKILL + "\nTODO: finish this section\n"
        self.assertIn(
            "unresolved TODO",
            " ".join(validate_skill.validate_skill_text(text)),
        )


if __name__ == "__main__":
    unittest.main()

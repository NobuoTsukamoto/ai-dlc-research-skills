from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REPORT_WORKFLOWS = ("daily.yml", "weekly.yml", "monthly.yml")
REPORT_PROMPTS = (
    "daily-tool-updates.md",
    "weekly-tool-updates.md",
    "monthly-tool-updates.md",
)


class ReportConfigurationTests(unittest.TestCase):
    def test_report_workflows_default_to_gemini_and_keep_override(self) -> None:
        for workflow_name in REPORT_WORKFLOWS:
            with self.subTest(workflow=workflow_name):
                text = (
                    ROOT / ".github" / "workflows" / workflow_name
                ).read_text(encoding="utf-8")
                self.assertIn(
                    "COPILOT_MODEL: ${{ vars.COPILOT_MODEL || 'gemini-3.8-flash' }}",
                    text,
                )
                self.assertIn('--model="$COPILOT_MODEL"', text)

    def test_report_prompts_use_japanese_writing_skill(self) -> None:
        for prompt_name in REPORT_PROMPTS:
            with self.subTest(prompt=prompt_name):
                text = (ROOT / "prompts" / prompt_name).read_text(encoding="utf-8")
                self.assertIn("`japanese-tech-writing`", text)
                self.assertIn("`ai-coding-agent-updates`", text)
                self.assertIn("事実と推論の区別", text)


if __name__ == "__main__":
    unittest.main()

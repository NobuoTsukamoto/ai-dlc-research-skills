from __future__ import annotations

import unittest
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REPORT_WORKFLOWS = ("daily.yml", "weekly.yml", "monthly.yml")
REPORT_PROMPTS = (
    "daily-tool-updates.md",
    "weekly-tool-updates.md",
    "monthly-tool-updates.md",
)


class ReportConfigurationTests(unittest.TestCase):
    def test_monthly_schedule_waits_for_the_last_week(self) -> None:
        text = (ROOT / ".github/workflows/monthly.yml").read_text(encoding="utf-8")
        self.assertIn('cron: "0 3 8 * *"', text)
        # The weekly workflow runs on Monday; the eighth always follows the
        # first Monday after a month ends, including across year boundaries.
        for year in range(2024, 2053):
            for month in range(1, 13):
                next_month = date(year + (month == 12), month % 12 + 1, 1)
                last_day = next_month - timedelta(days=1)
                weekly_date = last_day + timedelta(days=7 - last_day.weekday())
                self.assertLess(weekly_date, next_month + timedelta(days=7))

    def test_monthly_missing_week_is_reported_and_output_is_checked(self) -> None:
        workflow = (ROOT / ".github/workflows/monthly.yml").read_text(encoding="utf-8")
        prompt = (ROOT / "prompts/monthly-tool-updates.md").read_text(encoding="utf-8")
        self.assertIn("::warning::Missing weekly report", workflow)
        self.assertIn('test -s "updates/monthly/${target_month}.md"', workflow)
        self.assertIn("欠落がある場合はcoverageをpartial", prompt)

    def test_report_workflows_default_to_luna_and_keep_override(self) -> None:
        for workflow_name in REPORT_WORKFLOWS:
            with self.subTest(workflow=workflow_name):
                text = (
                    ROOT / ".github" / "workflows" / workflow_name
                ).read_text(encoding="utf-8")
                self.assertIn(
                    "COPILOT_MODEL: ${{ vars.COPILOT_MODEL || 'gpt-6-luna' }}",
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

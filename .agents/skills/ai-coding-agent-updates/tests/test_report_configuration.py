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

    def test_event_reporting_is_separate_and_marks_incomplete_coverage(self) -> None:
        references = ROOT / ".agents/skills/ai-coding-agent-updates/references"
        templates = (references / "output-templates.md").read_text(encoding="utf-8")
        for period in ("daily", "weekly", "monthly"):
            with self.subTest(period=period):
                section = templates.split(f"## {period}\n", 1)[1].split("```", 2)[1]
                self.assertIn("## 公式イベント", section)
                self.assertIn("確認不能", section)
                self.assertIn("網羅的ではない", section)
                self.assertIn("発見日", section)
                self.assertNotIn("## バズ", section)
                self.assertNotIn("## 月間バズ", section)

        rules = (references / "buzz-and-discovery.md").read_text(encoding="utf-8")
        for requirement in ("告知日", "開催日", "変更日", "主催者", "確認不能"):
            self.assertIn(requirement, rules)
        self.assertIn("イベント単独の告知は製品更新ログへ追加しない", rules)
        self.assertIn("旧形式でイベント欄がない", rules)

    def test_late_events_are_backfilled_and_reconciled_before_state_acceptance(self) -> None:
        references = ROOT / ".agents/skills/ai-coding-agent-updates/references"
        rules = (references / "buzz-and-discovery.md").read_text(encoding="utf-8")
        for requirement in (
            "実際に確認した日",
            "告知日・変更日で判定する",
            "欠落している場合は作成せず",
            "週次と暦月の月次が既にあれば",
            "期間後の保存済み日次",
            "重複追加しない",
        ):
            self.assertIn(requirement, rules)
        daily = (ROOT / "prompts/daily-tool-updates.md").read_text(encoding="utf-8")
        self.assertIn("collection/event-reconciliation.ok", daily)
        for period in ("weekly", "monthly"):
            prompt = (ROOT / "prompts" / f"{period}-tool-updates.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("後の保存済み日次", prompt)
            self.assertIn("遅延発見を取り込む", prompt)
        for workflow_name in ("daily.yml", "daily-dry-run.yml"):
            workflow = (ROOT / ".github/workflows" / workflow_name).read_text(
                encoding="utf-8"
            )
            self.assertIn("rm -f collection/event-reconciliation.ok", workflow)
            self.assertIn("test -f collection/event-reconciliation.ok", workflow)
            self.assertLess(
                workflow.index("rm -f collection/event-reconciliation.ok"),
                workflow.index("test -f collection/event-reconciliation.ok"),
            )

    def test_buzz_sources_are_not_added_to_automated_research(self) -> None:
        for workflow_name in REPORT_WORKFLOWS:
            with self.subTest(workflow=workflow_name):
                text = (ROOT / ".github/workflows" / workflow_name).read_text(
                    encoding="utf-8"
                )
                allowed = next(
                    line for line in text.splitlines() if "COPILOT_ALLOWED_URLS:" in line
                )
                self.assertNotIn("reddit.com", allowed.lower())
                self.assertNotIn("ycombinator.com", allowed.lower())
        weekly = (ROOT / "prompts/weekly-tool-updates.md").read_text(encoding="utf-8")
        monthly = (ROOT / "prompts/monthly-tool-updates.md").read_text(encoding="utf-8")
        self.assertIn("バズやコミュニティ反応を調査しない", weekly)
        self.assertIn("既存の公式情報源に現れた候補", monthly)
        self.assertIn("バズやコミュニティ反応は調査しない", monthly)


if __name__ == "__main__":
    unittest.main()

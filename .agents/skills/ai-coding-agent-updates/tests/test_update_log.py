from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "update_log.py"
spec = importlib.util.spec_from_file_location("update_log", SCRIPT)
update_log = importlib.util.module_from_spec(spec)
sys.modules["update_log"] = update_log
assert spec.loader is not None
spec.loader.exec_module(update_log)


class UpdateLogTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.log = Path(self.temporary_directory.name) / "update-log.jsonl"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def add(self, **overrides):
        values = {
            "tool": "openai-codex",
            "published_date": "2026-07-25",
            "discovered_date": "2026-07-26",
            "title": "Codex adds a useful feature",
            "url": "https://example.com/update?utm_source=test",
            "source_type": "official-changelog",
            "release_stage": "stable",
            "importance": "medium",
            "summary": "公式情報の要約",
            "impact": "実務への影響",
        }
        values.update(overrides)
        argv = ["add", "--log", str(self.log)]
        for key, value in values.items():
            argv.extend((f"--{key.replace('_', '-')}", value))
        with redirect_stdout(io.StringIO()):
            return update_log.main(argv)

    def check(self, *, tool, title, url):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = update_log.main(
                [
                    "check",
                    "--log",
                    str(self.log),
                    "--tool",
                    tool,
                    "--title",
                    title,
                    "--url",
                    url,
                ]
            )
        return exit_code, stdout.getvalue()

    def test_add_preserves_japanese_and_canonicalizes_url(self):
        self.assertEqual(self.add(), 0)
        items = update_log.load_log(self.log)
        self.assertEqual(items[0]["summary"], "公式情報の要約")
        self.assertEqual(items[0]["url"], "https://example.com/update")

    def test_duplicate_by_url_ignores_tracking_parameters(self):
        self.add()
        exit_code, output = self.check(
            tool="openai-codex",
            title="Different cross-post title",
            url="https://example.com/update?utm_campaign=weekly#details",
        )
        self.assertEqual(exit_code, 0)
        self.assertTrue(output.startswith("DUPLICATE"))

    def test_duplicate_by_normalized_title_within_same_tool(self):
        self.add()
        exit_code, output = self.check(
            tool="openai-codex",
            title="CODEX: adds a useful feature!",
            url="https://example.com/another-page",
        )
        self.assertEqual(exit_code, 0)
        self.assertTrue(output.startswith("DUPLICATE"))

    def test_same_title_for_different_tool_is_not_duplicate(self):
        self.add()
        exit_code, output = self.check(
            tool="claude-code",
            title="Codex adds a useful feature",
            url="https://example.com/claude-update",
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(output.strip(), "NOT_FOUND")

    def test_same_url_for_different_tool_is_not_duplicate(self):
        self.add()
        exit_code, output = self.check(
            tool="github-copilot-app",
            title="Shared announcement with app-specific changes",
            url="https://example.com/update",
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(output.strip(), "NOT_FOUND")

    def test_distinct_titles_with_common_prefix_are_not_duplicates(self):
        self.add(title="Release 1.2.3 fixes Windows", url="https://example.com/1.2.3")
        exit_code, output = self.check(
            tool="openai-codex",
            title="Release 1.2.4 fixes Windows",
            url="https://example.com/1.2.4",
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(output.strip(), "NOT_FOUND")

    def test_list_filters_date_range(self):
        self.add()
        self.add(
            title="Later update",
            url="https://example.com/later",
            published_date="2026-08-01",
            discovered_date="2026-08-01",
        )
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = update_log.main(
                [
                    "list",
                    "--log",
                    str(self.log),
                    "--from-date",
                    "2026-07-01",
                    "--to-date",
                    "2026-07-31",
                    "--format",
                    "markdown",
                ]
            )
        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("Codex adds a useful feature", output)
        self.assertNotIn("Later update", output)

    def test_rejects_invalid_date(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = self.add(published_date="2026-02-30")
        self.assertEqual(exit_code, 2)
        self.assertIn("valid YYYY-MM-DD", stderr.getvalue())

    def test_rejects_discovery_before_publication(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = self.add(
                published_date="2026-07-26", discovered_date="2026-07-25"
            )
        self.assertEqual(exit_code, 2)
        self.assertIn("cannot be earlier", stderr.getvalue())

    def test_rejects_empty_summary(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = self.add(summary=" ")
        self.assertEqual(exit_code, 2)
        self.assertIn("summary cannot be empty", stderr.getvalue())

    def test_rejects_summary_over_maximum_length(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = self.add(summary="あ" * (update_log.MAX_SUMMARY_LENGTH + 1))
        self.assertEqual(exit_code, 2)
        self.assertIn("summary cannot exceed", stderr.getvalue())

    def test_rejects_impact_over_maximum_length(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = self.add(impact="あ" * (update_log.MAX_IMPACT_LENGTH + 1))
        self.assertEqual(exit_code, 2)
        self.assertIn("impact cannot exceed", stderr.getvalue())

    def test_rejects_long_consecutive_match_between_summary_and_impact(self):
        copied_phrase = (
            "同じ公式文をそのまま繰り返した長い表現が含まれています。"
            "この文章は独立した推論ではありません。"
        )
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = self.add(
                summary=f"変更内容: {copied_phrase}",
                impact=f"影響: {copied_phrase}",
            )
        self.assertEqual(exit_code, 2)
        self.assertIn("consecutive phrase", stderr.getvalue())

    def test_validate_checks_existing_items(self):
        self.log.write_text(
            '{"schema_version": 1, "id": "bad", "tool": "openai-codex", '
            '"published_date": "2026-07-25", "discovered_date": "2026-07-26", '
            '"title": "Update", "url": "https://example.com/update", '
            '"source_type": "official-changelog", "release_stage": "stable", '
            '"importance": "medium", "summary": "' + "あ" * 501 + '", '
            '"impact": "実務への影響"}\n',
            encoding="utf-8",
        )
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = update_log.main(
                ["validate", "--log", str(self.log)]
            )
        self.assertEqual(exit_code, 2)
        self.assertIn("summary cannot exceed", stderr.getvalue())

    def test_validate_reports_valid_log(self):
        self.add()
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = update_log.main(["validate", "--log", str(self.log)])
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue().strip(), "VALID\t1")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from argparse import Namespace
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "reading_log.py"
spec = importlib.util.spec_from_file_location("reading_log", SCRIPT)
reading_log = importlib.util.module_from_spec(spec)
sys.modules["reading_log"] = reading_log
assert spec.loader is not None
spec.loader.exec_module(reading_log)

SAMPLE = """# Log

| 登録日 | 読了日 | ステータス | タイトル | 著者 | 年 | 種別 | 掲載先 | テーマ | 評価 | DOI・参照先 | メモ |
|---|---|---|---|---|---:|---|---|---|---:|---|---|
| 2026-01-01 | 2026-01-15 | read | A Study of Coding Agents | A | 2026 | 査読論文 | ICSE | agents | 9 | https://doi.org/10.1000/XYZ | note |
"""


class ReadingLogTests(unittest.TestCase):
    def test_normalize_doi(self):
        self.assertEqual(
            reading_log.normalize_doi("https://doi.org/10.1000/XYZ"), "10.1000/xyz"
        )

    def test_duplicate_by_doi(self):
        rows = reading_log.parse_table_rows(SAMPLE)
        self.assertEqual(
            len(reading_log.find_duplicates(rows, "Different title", "10.1000/xyz")), 1
        )

    def test_duplicate_by_title(self):
        rows = reading_log.parse_table_rows(SAMPLE)
        self.assertEqual(
            len(reading_log.find_duplicates(rows, "A Study of Coding Agents", "")), 1
        )

    def test_distinct_doi_with_common_prefix_is_not_duplicate(self):
        rows = reading_log.parse_table_rows(
            SAMPLE.replace("10.1000/XYZ", "10.1000/XYZ-extra")
        )
        self.assertEqual(
            len(reading_log.find_duplicates(rows, "Different title", "10.1000/xyz")),
            0,
        )

    def test_distinct_url_with_common_prefix_is_not_duplicate(self):
        rows = reading_log.parse_table_rows(
            SAMPLE.replace(
                "https://doi.org/10.1000/XYZ",
                "https://example.com/papers/agent-study-extra",
            )
        )
        self.assertEqual(
            len(
                reading_log.find_duplicates(
                    rows, "Different title", "https://example.com/papers/agent-study"
                )
            ),
            0,
        )

    def test_insert_row_replaces_blank(self):
        text = SAMPLE.replace(
            "| 2026-01-01 | 2026-01-15 | read | A Study of Coding Agents | A | 2026 | 査読論文 | ICSE | agents | 9 | https://doi.org/10.1000/XYZ | note |",
            "|  |  |  |  |  |  |  |  |  |  |  |  |",
        )
        updated = reading_log.insert_row(
            text,
            "| 2026-02-01 |  | selected | New | B | 2026 | 査読論文 | FSE | quality | 8 | url | note |",
        )
        self.assertIn("| 2026-02-01 |  | selected | New |", updated)

    def test_read_status_requires_read_date(self):
        args = Namespace(status="read", read_date="")
        with redirect_stderr(io.StringIO()):
            self.assertEqual(reading_log.cmd_add(args), 2)

    def test_check_duplicate_is_a_successful_result(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "reading-log.md"
            log.write_text(SAMPLE, encoding="utf-8")
            args = Namespace(
                log=str(log),
                title="Different title",
                doi="10.1000/xyz",
            )

            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(reading_log.cmd_check(args), 0)
            self.assertTrue(output.getvalue().startswith("DUPLICATE"))

    def test_check_not_found_is_a_successful_result(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "reading-log.md"
            log.write_text(SAMPLE, encoding="utf-8")
            args = Namespace(
                log=str(log),
                title="A New Study",
                doi="10.1000/new",
            )

            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(reading_log.cmd_check(args), 0)
            self.assertEqual(output.getvalue().strip(), "NOT_FOUND")

    def test_add_read_row_includes_read_date(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "reading-log.md"
            log.write_text(SAMPLE, encoding="utf-8")
            args = Namespace(
                log=str(log),
                date="2026-02-01",
                read_date="2026-02-14",
                status="read",
                title="A New Study",
                authors="B",
                year=2026,
                type="査読論文",
                venue="FSE",
                topics="quality",
                score=8,
                url="https://doi.org/10.1000/new",
                notes="reviewed",
                force=False,
            )

            with redirect_stdout(io.StringIO()):
                self.assertEqual(reading_log.cmd_add(args), 0)
            self.assertIn(
                "| 2026-02-01 | 2026-02-14 | read | A New Study |",
                log.read_text(encoding="utf-8"),
            )

    def test_rejects_invalid_iso_date(self):
        parser = reading_log.build_parser()
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "add",
                    "--log",
                    "log.md",
                    "--date",
                    "2026/02/01",
                    "--status",
                    "candidate",
                    "--title",
                    "Title",
                    "--authors",
                    "A",
                    "--year",
                    "2026",
                    "--type",
                    "paper",
                    "--venue",
                    "FSE",
                    "--topics",
                    "agents",
                    "--score",
                    "8",
                    "--url",
                    "https://example.com",
                ]
            )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "reading_log.py"
spec = importlib.util.spec_from_file_location("reading_log", SCRIPT)
reading_log = importlib.util.module_from_spec(spec)
sys.modules["reading_log"] = reading_log
assert spec.loader is not None
spec.loader.exec_module(reading_log)

SAMPLE = """# Log

| 登録日 | ステータス | タイトル | 著者 | 年 | 種別 | 掲載先 | テーマ | 評価 | DOI・参照先 | メモ |
|---|---|---|---|---:|---|---|---|---:|---|---|
| 2026-01-01 | read | A Study of Coding Agents | A | 2026 | 査読論文 | ICSE | agents | 9 | https://doi.org/10.1000/XYZ | note |
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

    def test_insert_row_replaces_blank(self):
        text = SAMPLE.replace(
            "| 2026-01-01 | read | A Study of Coding Agents | A | 2026 | 査読論文 | ICSE | agents | 9 | https://doi.org/10.1000/XYZ | note |",
            "|  |  |  |  |  |  |  |  |  |  |  |",
        )
        updated = reading_log.insert_row(
            text,
            "| 2026-02-01 | selected | New | B | 2026 | 査読論文 | FSE | quality | 8 | url | note |",
        )
        self.assertIn("| 2026-02-01 | selected | New |", updated)


if __name__ == "__main__":
    unittest.main()

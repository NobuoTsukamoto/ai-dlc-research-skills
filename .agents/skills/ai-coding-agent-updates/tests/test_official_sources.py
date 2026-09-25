from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OFFICIAL_SOURCES = (
    ROOT
    / ".agents"
    / "skills"
    / "ai-coding-agent-updates"
    / "references"
    / "official-sources.md"
)
DAILY_PROMPT = ROOT / "prompts" / "daily-tool-updates.md"
CURSOR_RSS_URL = "https://cursor.com/changelog/rss.xml"


class OfficialSourcesTests(unittest.TestCase):
    def test_cursor_rss_is_registered_with_date_guidance(self) -> None:
        text = OFFICIAL_SOURCES.read_text(encoding="utf-8")

        self.assertIn(CURSOR_RSS_URL, text)
        self.assertIn("`pubDate`をAsia/Tokyoへ変換", text)
        self.assertIn("`link`をcanonical URL", text)
        self.assertIn("対象日の`pubDate`がなければ「更新なし」", text)

    def test_daily_prompt_requires_cursor_rss_date_check(self) -> None:
        text = DAILY_PROMPT.read_text(encoding="utf-8")

        self.assertIn("Cursorは公式RSS", text)
        self.assertIn("`pubDate`をAsia/Tokyoへ変換", text)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[4]
WORKFLOW = ROOT / ".github" / "workflows" / "daily-dry-run.yml"
PRIMARY_DOMAINS = {
    "github.com",
    "api.github.com",
    "raw.githubusercontent.com",
    "github.blog",
    "learn.chatgpt.com",
    "cursor.com",
    "antigravity.google",
}


class DryRunWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    @classmethod
    def env_value(cls, name: str) -> str:
        match = re.search(rf"^  {re.escape(name)}: (.+)$", cls.text, re.MULTILINE)
        if match is None:
            raise AssertionError(f"Missing workflow env value: {name}")
        return match.group(1).strip('"')

    def test_is_manual_and_read_only_by_default(self) -> None:
        self.assertIn("on:\n  workflow_dispatch:", self.text)
        self.assertNotIn("\n  schedule:", self.text)
        self.assertNotIn("\n  push:", self.text)
        self.assertNotIn("\n  pull_request:", self.text)
        self.assertRegex(
            self.text,
            r"live_fetch:\n(?: {8}.+\n)* {8}default: false",
        )
        self.assertIn("permissions:\n  contents: read", self.text)

    def test_live_fetch_is_explicit_and_never_publishes(self) -> None:
        self.assertIn("if: inputs.live_fetch", self.text)
        self.assertNotIn("data_branch.py sync", self.text)
        self.assertNotIn("git push", self.text)
        self.assertNotIn("--allow-all", self.text)

    def test_model_and_url_permissions_are_pinned(self) -> None:
        self.assertEqual(self.env_value("COPILOT_CLI_VERSION"), "1.0.87")
        self.assertEqual(self.env_value("COPILOT_MODEL"), "gpt-5.6-luna")
        self.assertNotIn("gpt-5.4-nano", self.text)
        self.assertEqual(
            set(self.env_value("COPILOT_ALLOWED_URLS").split(",")),
            PRIMARY_DOMAINS,
        )
        self.assertIn('--model="$COPILOT_MODEL"', self.text)
        self.assertIn('--allow-tool=\'web_fetch\'', self.text)
        self.assertIn('--allow-url="$COPILOT_ALLOWED_URLS"', self.text)
        self.assertIn("--no-ask-user", self.text)

    def test_live_result_is_validated_and_uploaded(self) -> None:
        self.assertIn("update_log.py validate", self.text)
        self.assertIn("permission denied", self.text)
        self.assertIn("actions/upload-artifact@v4", self.text)


if __name__ == "__main__":
    unittest.main()

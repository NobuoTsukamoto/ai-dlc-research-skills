from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[4] / ".github" / "scripts" / "data_branch.py"
spec = importlib.util.spec_from_file_location("data_branch", SCRIPT)
data_branch = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(data_branch)


class DataBranchTests(unittest.TestCase):
    def test_copy_updates_replaces_stale_generated_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            destination = root / "destination"
            source.mkdir()
            destination.mkdir()
            (source / "daily").mkdir()
            (source / "daily" / "2026-09-22.md").write_text("report", encoding="utf-8")
            (destination / "stale.md").write_text("stale", encoding="utf-8")

            data_branch.copy_updates(source, destination)

            self.assertEqual(
                (destination / "daily" / "2026-09-22.md").read_text(encoding="utf-8"),
                "report",
            )
            self.assertFalse((destination / "stale.md").exists())


if __name__ == "__main__":
    unittest.main()

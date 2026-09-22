from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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

    def test_sync_uses_ephemeral_auth_header_when_github_token_present(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            updates = root / "updates"
            data = root / "data"
            (updates / "daily").mkdir(parents=True)
            (data / "updates").mkdir(parents=True)
            (updates / "daily" / "2026-09-22.md").write_text("report", encoding="utf-8")

            run_calls: list[tuple[str, ...]] = []

            def fake_run(*args: str, cwd: Path = data_branch.ROOT, check: bool = True):
                run_calls.append(args)
                return None

            diff_result = mock.Mock(returncode=1)

            with (
                mock.patch.object(data_branch, "ROOT", root),
                mock.patch.object(data_branch, "DATA", data),
                mock.patch.object(data_branch, "UPDATES", updates),
                mock.patch.object(data_branch, "run", side_effect=fake_run),
                mock.patch.object(data_branch.subprocess, "run", return_value=diff_result),
                mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}, clear=False),
            ):
                data_branch.sync()

            self.assertIn(("git", "commit", "-m", "chore: update generated reports"), run_calls)
            self.assertEqual(run_calls[-1][0:4], ("git", "-c", mock.ANY, "push"))
            self.assertEqual(run_calls[-1][-2:], ("origin", "HEAD:data"))
            self.assertIn("AUTHORIZATION: basic", run_calls[-1][2])


if __name__ == "__main__":
    unittest.main()

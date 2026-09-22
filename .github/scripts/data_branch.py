#!/usr/bin/env python3
"""Prepare and persist generated updates on the dedicated data branch."""

from __future__ import annotations

import shutil
import subprocess
import sys
import os
from base64 import b64encode
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
UPDATES = ROOT / "updates"


def run(
    *args: str, cwd: Path = ROOT, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=check, text=True)


def copy_updates(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def prepare() -> None:
    run("git", "fetch", "origin", "data", check=False)
    remote_branch = subprocess.run(
        ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/data"),
        cwd=ROOT,
        check=False,
    )
    if remote_branch.returncode == 0:
        run("git", "worktree", "add", "--detach", str(DATA), "origin/data")
    else:
        run("git", "worktree", "add", "--detach", str(DATA))
        run("git", "switch", "--orphan", "data", cwd=DATA)
        run("git", "rm", "-rf", ".", cwd=DATA, check=False)
    data_updates = DATA / "updates"
    data_updates.mkdir(parents=True, exist_ok=True)
    if data_updates.exists():
        copy_updates(data_updates, UPDATES)


def sync() -> None:
    copy_updates(UPDATES, DATA / "updates")
    run("git", "add", "--", "updates", cwd=DATA)
    if (
        subprocess.run(
            ("git", "diff", "--cached", "--quiet"), cwd=DATA, check=False
        ).returncode
        == 0
    ):
        print("No generated update changes.")
        return
    run("git", "config", "user.name", "github-actions[bot]", cwd=DATA)
    run(
        "git",
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
        cwd=DATA,
    )
    run("git", "commit", "-m", "chore: update generated reports", cwd=DATA)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        basic_auth = b64encode(f"x-access-token:{token}".encode()).decode()
        run(
            "git",
            "-c",
            f"http.extraheader=AUTHORIZATION: basic {basic_auth}",
            "push",
            "origin",
            "HEAD:data",
            cwd=DATA,
        )
        return
    run("git", "push", "origin", "HEAD:data", cwd=DATA)


def main(argv: list[str]) -> int:
    if argv == ["prepare"]:
        prepare()
    elif argv == ["sync"]:
        sync()
    else:
        print("usage: data_branch.py prepare|sync", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

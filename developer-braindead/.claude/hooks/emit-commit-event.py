#!/usr/bin/env python3
"""Append a `commit` event to the visualizer's state.ndjson on every
git commit. Invoked by .git/hooks/post-commit.

Reads HEAD's short-sha + subject and writes one NDJSON line. Silent on
failure — never blocks the commit.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent  # brain/
STATE_PATH = REPO_ROOT / "developer-braindead" / "experiments" / "visualizer" / "state.ndjson"


def main() -> None:
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--pretty=format:%h%x09%s"],
            cwd=str(REPO_ROOT),
            text=True,
            encoding="utf-8",
        ).strip()
        if not out or "\t" not in out:
            return
        sha, subject = out.split("\t", 1)
        event = {
            "wallTime": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "source": "git",
            "type": "commit",
            "msg": f"{sha} · {subject}",
            "cls": "commit",
        }
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with STATE_PATH.open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"emit-commit-event: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

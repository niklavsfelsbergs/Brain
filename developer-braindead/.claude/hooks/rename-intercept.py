#!/usr/bin/env python
# rename-intercept.py — /rename for any Claude Code session (S073).
#
# The cockpit board lets you relabel a session. Inside the cockpit's own
# embedded terminal that happens via a keystroke mirror in web/term.js
# (writes browser localStorage). But a session running in VSCode never
# touches that terminal, so it had no way to set its board label.
#
# This UserPromptSubmit hook closes that gap UNIFORMLY: when the prompt is a
# `/rename <name>` (recognized via .claude/commands/rename.md, which expands to
# a <cockpit-rename>…</cockpit-rename> sentinel), we write the name to
# switchboard/state-names.json keyed by sid8 and BLOCK the prompt (exit 2) so
# no model turn is spent. The cockpit backend reads that file and the board
# prefers it over the bare actor name.
#
# Defensive by construction: any parse/IO failure exits 0 (let the prompt
# through). Only a successful rename exits 2.

import json
import os
import re
import sys
from pathlib import Path

# HERE = .../brain/developer-braindead/.claude/hooks/rename-intercept.py
HERE = Path(__file__).resolve()
DEV_BRAIN = HERE.parent.parent.parent              # .../developer-braindead
VIZ_DIR = DEV_BRAIN.parent / "switchboard"         # brain-root/switchboard (D-026)
NAMES_PATH = VIZ_DIR / "state-names.json"          # {sid8: label} — read by backend.py

NAME_MAX = 40

# Two shapes, so we match whether the hook sees the raw input or the expanded
# command body: the command file expands `/rename foo` to the sentinel, but if
# a build ever surfaces the raw text we still catch it.
_SENTINEL = re.compile(r"<cockpit-rename>\s*(.*?)\s*</cockpit-rename>", re.DOTALL)
_RAW = re.compile(r"^/rename\s+(.+)$", re.IGNORECASE)


def _extract(prompt: str):
    """Return the requested name if this prompt is a /rename, else None."""
    m = _SENTINEL.search(prompt)
    if m:
        return m.group(1)
    m = _RAW.match(prompt.strip())
    if m:
        return m.group(1)
    return None


def _sanitize(name: str) -> str:
    # Single line, no control chars, collapsed whitespace, capped.
    name = re.sub(r"\s+", " ", name.replace("\r", " ").replace("\n", " ")).strip()
    name = "".join(c for c in name if c.isprintable())
    return name[:NAME_MAX].strip()


def _write_name(sid8: str, name: str) -> None:
    try:
        names = json.loads(NAMES_PATH.read_text(encoding="utf-8"))
        if not isinstance(names, dict):
            names = {}
    except (OSError, ValueError):
        names = {}
    if name:
        names[sid8] = name
    else:
        names.pop(sid8, None)
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    NAMES_PATH.write_text(json.dumps(names, indent=2), encoding="utf-8")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0  # can't parse — never block a real prompt

    if payload.get("hook_event_name") not in (None, "UserPromptSubmit"):
        return 0

    prompt = payload.get("prompt") or ""
    requested = _extract(prompt)
    if requested is None:
        return 0  # ordinary prompt — fast, silent pass-through

    sid = payload.get("session_id") or os.environ.get("CLAUDE_CODE_SESSION_ID") or ""
    sid8 = sid[:8].lower()
    if not sid8:
        # No session id to key on — let it through rather than swallow silently.
        return 0

    name = _sanitize(requested)
    if not name:
        sys.stderr.write("usage: /rename <name>")
        return 2

    try:
        _write_name(sid8, name)
    except OSError as e:
        sys.stderr.write(f"/rename failed to write name store: {e}")
        return 2  # still block — the model body is just a sentinel, useless to send

    # exit 2 on UserPromptSubmit: prompt is erased, stderr is shown to the user
    # only (never enters model context), no turn is spent.
    sys.stderr.write(f'renamed this session to "{name}" on the cockpit board')
    return 2


if __name__ == "__main__":
    sys.exit(main())

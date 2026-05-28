#!/usr/bin/env python
# session-end-safety-net.py — best-effort durability net for an UN-closed session
# (S115 close-enforcement, layer 3).
#
# On SessionEnd, if this session posted an OPEN but never a CLOSING, append an
# auto-CLOSING STUB to the relevant comms channel so siblings + the next respawn
# see the session ended without a proper close and know to reconcile.
#
# HONEST LIMITS (confirmed via the Claude Code hooks docs, S115):
#   - SessionEnd runs ASYNC / no-wait — on a hard terminal-close the process may
#     be killed before this finishes (a short file append *may* land; do not rely
#     on it). It is a best-effort net for a GRACEFUL end (/exit, logout), NOT a
#     guarantee. The reliable floor stays the in-session per-turn quest-log +
#     OPEN, recovered by the next respawn's reconciliation.
#   - It deliberately does NOT commit. An unattended commit in this shared-index,
#     parallel-session repo is the exact hazard that once swept a sibling's
#     staged file (dev S118). Uncommitted work stays in the tree for the next
#     session to reconcile; this stub is only the coordination signal.
#   - reason=='clear'/'resume' are NOT true ends (clear reborns the session,
#     resume pauses it) — skip them.
#   - Fail open: any error exits 0. A missed stub costs a reconciliation prompt
#     next session; a crash here must never be the thing that breaks shutdown.

import json
import sys
import time
from pathlib import Path

BRAIN_ROOT = Path(__file__).resolve().parent.parent.parent
COMMS_FILES = [
    BRAIN_ROOT / "developer-braindead" / "comms" / "active.md",
    BRAIN_ROOT / "gielinor" / "comms" / "active.md",
]
NON_TERMINAL_REASONS = {"clear", "resume"}


def _open_token_without_closing(text: str, sid8: str):
    """If comms has an OPEN line for this sid8 but no CLOSING line, return the
    '<actor>-<sid8>' token from the OPEN line; else None."""
    open_tok = None
    has_closing = False
    for line in text.splitlines():
        s = line.strip()
        if f"-{sid8} OPEN" in s and open_tok is None:
            # line shape: "[ts] <actor>-<sid8> OPEN ..." -> take the 2nd field
            parts = s.split()
            for p in parts:
                if p.endswith(f"-{sid8}"):
                    open_tok = p
                    break
        if f"-{sid8} CLOSING" in s:
            has_closing = True
    return open_tok if (open_tok and not has_closing) else None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0

    if payload.get("hook_event_name") not in (None, "SessionEnd"):
        return 0

    reason = (payload.get("reason") or "").lower()
    if reason in NON_TERMINAL_REASONS:
        return 0  # not a real end

    sid = payload.get("session_id") or ""
    sid8 = sid[:8].lower()
    if not sid8:
        return 0

    ts = time.strftime("%Y-%m-%d %H:%M")
    for comms in COMMS_FILES:
        try:
            if not comms.exists():
                continue
            tok = _open_token_without_closing(
                comms.read_text(encoding="utf-8", errors="replace"), sid8)
            if not tok:
                continue
            stub = (
                f"\n[{ts}] {tok} CLOSING (auto / SessionEnd reason={reason or 'other'})\n"
                f"  Session ended WITHOUT a manual close ritual. Work may be uncommitted; "
                f"this is a safety-net stub, not a real close. NEXT SESSION: reconcile via "
                f"the in-progress quest-log + git status (close_check.py was not run). "
                f"No auto-commit (shared-index hazard).\n"
            )
            with comms.open("a", encoding="utf-8") as fh:
                fh.write(stub)
        except OSError:
            continue  # best-effort per channel; never disrupt shutdown

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""verification/close_check.py -- completeness gate for the dev-brain close ritual.

Re-derives the dev `session-close.md` steps from GROUND TRUTH (comms, quest-log,
respawn, active-mode, git status) for a given session, so "I think I closed" is
replaced by "the checklist passed -- or it told me exactly what's missing." This
is the mechanized antidote to the S115 close where three steps were skipped and
only a manual checklist-vs-filesystem walk caught them.

Run it as the penultimate close step (after the commit, before the wrapped_up
marker):

  python developer-braindead/verification/close_check.py --sid8 <sid8>

Exit 0 = every checkable step landed (it then names the one remaining manual
action: write the wrapped_up marker). Exit 1 = at least one gap; prints the
locked CLOSE-RITUAL banner + the specific gaps, so the ritual halts and is fixed
rather than declared done. Scoped to the DEV-brain close ritual (the one S115
botched); the gielinor close-session is a parallel future extension.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]            # brain root
DEVBRAIN = ROOT / "developer-braindead"
COMMS = DEVBRAIN / "comms" / "active.md"
RESPAWN = DEVBRAIN / "respawn.md"
QUESTLOG = DEVBRAIN / "quest-log"
ACTIVE_MODE = ROOT / ".claude" / "active-mode.txt"

# Locked failure receipt (Khaan item 2 pattern; ASCII per the Windows-console
# lesson). Dev-brain-local -- the close ritual is a dev ritual, not one of the
# gielinor rituals in spellbook/failure-banners.md.
BANNER = (
    "## CLOSE RITUAL INCOMPLETE -- not done; do NOT declare the session wrapped\n"
    "One or more session-close steps did not land on disk. Fix the gaps below, "
    "re-commit if needed, and re-run this check before writing the wrapped_up marker."
)


def _git_clean(path: Path) -> bool:
    """True if `path` has no uncommitted change (tracked + unmodified)."""
    r = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", str(path)],
                       capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() == ""


def _find_questlog(sid8: str) -> Path | None:
    for base in (QUESTLOG / "in-progress", QUESTLOG):
        if not base.exists():
            continue
        for f in base.glob(f"*{sid8}*.md"):
            return f
    return None


def _first_respawn_block(text: str) -> str:
    """The most recent **Last updated** block (top of file to the first 'Prior')."""
    start = text.find("**Last updated")
    if start < 0:
        return ""
    nxt = text.find("**Prior", start)
    return text[start:nxt if nxt > 0 else len(text)]


# --- checks: each returns (name, ok, detail) ---

def check_closing(sid8):
    name = "CLOSING posted"
    try:
        txt = COMMS.read_text(encoding="utf-8", errors="replace")
        if f"braindead-{sid8} CLOSING" in txt:
            return (name, True, "comms/active.md has a CLOSING for this sid8")
        return (name, False, f"no 'braindead-{sid8} CLOSING' line in comms/active.md (step 6)")
    except Exception as e:
        return (name, False, f"exception: {e}")


def check_questlog(sid8):
    name = "quest-log + cascade lines"
    try:
        f = _find_questlog(sid8)
        if f is None:
            return (name, False, f"no quest-log file matching *{sid8}*.md (step 2)")
        body = f.read_text(encoding="utf-8", errors="replace")
        missing = []
        if "**Cascade." not in body:
            missing.append("**Cascade.** line")
        if "Main-brain changes" not in body:
            missing.append("**Main-brain changes.** line")
        if missing:
            return (name, False, f"{f.name} missing {', '.join(missing)} (step 2, load-bearing)")
        return (name, True, f"{f.name} present with Cascade + Main-brain lines")
    except Exception as e:
        return (name, False, f"exception: {e}")


def check_respawn(sid8):
    name = "respawn updated"
    try:
        block = _first_respawn_block(RESPAWN.read_text(encoding="utf-8", errors="replace"))
        if sid8 in block:
            return (name, True, "respawn.md's top Last-updated block references this sid8")
        return (name, False, f"respawn.md's most-recent block does not mention {sid8} (step 3)")
    except Exception as e:
        return (name, False, f"exception: {e}")


def check_active_mode():
    name = "active-mode unscoped"
    try:
        val = ACTIVE_MODE.read_text(encoding="utf-8", errors="replace").strip()
        if val == "unscoped" or val == "":
            return (name, True, f"active-mode.txt = {val!r}")
        return (name, False, f"active-mode.txt = {val!r}, expected 'unscoped' (step 7)")
    except Exception as e:
        return (name, False, f"exception: {e}")


def check_committed(sid8):
    name = "core artifacts committed"
    try:
        f = _find_questlog(sid8)
        dirty = [p for p in (RESPAWN, f) if p is not None and not _git_clean(p)]
        if dirty:
            return (name, False,
                    f"uncommitted: {', '.join(p.name for p in dirty)} (step 8 -- commit them)")
        return (name, True, "quest-log + respawn show no uncommitted changes")
    except Exception as e:
        return (name, False, f"exception: {e}")


def run(sid8: str) -> int:
    results = [
        check_closing(sid8),
        check_questlog(sid8),
        check_respawn(sid8),
        check_active_mode(),
        check_committed(sid8),
    ]
    width = max(len(r[0]) for r in results)
    for cname, ok, detail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {cname:<{width}}  {detail}")
    if all(ok for _, ok, _ in results):
        print("\nClose verified. FINAL action remaining: write the wrapped_up marker "
              f"(.claude/intent/{sid8}.mode = 'wrapped_up').")
        return 0
    sys.stderr.write("\n" + BANNER + "\n")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sid8", required=True, help="first 8 chars of CLAUDE_CODE_SESSION_ID")
    return run(ap.parse_args().sid8.strip())


if __name__ == "__main__":
    sys.exit(main())

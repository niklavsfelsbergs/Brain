#!/usr/bin/env python3
"""verification/close_check.py -- completeness gate for the close rituals.

Re-derives the load-bearing close-ritual steps from GROUND TRUTH (comms,
quest-log, respawn/inventory, active-mode, git status) for a given session, so
"I think I closed" is replaced by "the checklist passed -- or it told me exactly
what's missing." This is the mechanized antidote to the S115 dev close where
three steps were skipped and only a manual checklist-vs-filesystem walk caught
them.

Two rituals, selected by --ritual (default `dev` so the wired dev step keeps
working unchanged):

  # dev-brain close (developer-braindead/spellbook/session-close.md, step 9):
  python developer-braindead/verification/close_check.py --sid8 <sid8>

  # gielinor PLAYER close (gielinor/spellbook/rituals/close-session.md, step 9):
  python developer-braindead/verification/close_check.py --ritual player --sid8 <sid8>

Run it as the penultimate close step (after the commit, before the wrapped_up
marker). Exit 0 = every checkable step landed (it then names the one remaining
manual action: write the wrapped_up marker). Exit 1 = at least one gap; prints
the locked CLOSE-RITUAL banner + the specific gaps, so the ritual halts and is
fixed rather than declared done.

The two rituals have genuinely different artifacts, so they run two separate
check-lists rather than one forked set: the dev close is single-track (one
respawn.md, one comms, one active-mode marker); the gielinor player close is
per-player and multi-player (keyed by sid8 across players/*/), has no rolling
respawn.md (resume state lives in each player's inventory/), and does not use
the dev-brain active-mode marker. Only the harness -- BANNER, _git_clean, the
print/exit loop -- is shared. (D-034 + its gielinor follow-on, S117.)
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

GIELINOR = ROOT / "gielinor"
GIELINOR_COMMS = GIELINOR / "comms" / "active.md"
GIELINOR_PLAYERS = GIELINOR / "players"

# Locked failure receipt (Khaan item 2 pattern; ASCII per the Windows-console
# lesson). Ritual-neutral wording -- both close rituals share the same
# do-NOT-declare-wrapped semantics on a gap.
BANNER = (
    "## CLOSE RITUAL INCOMPLETE -- not done; do NOT declare the session wrapped\n"
    "One or more session-close steps did not land on disk. Fix the gaps below, "
    "re-commit if needed, and re-run this check before writing the wrapped_up marker."
)

# The one manual action that remains after a clean check (same for both rituals).
def _wrapped_up_hint(sid8: str) -> str:
    return ("Close verified. FINAL action remaining: write the wrapped_up marker "
            f"(.claude/intent/{sid8}.mode = 'wrapped_up').")


def _git_clean(path: Path) -> bool:
    """True if `path` has no uncommitted change (tracked + unmodified).

    A modified-tracked OR an untracked file both produce porcelain output, so
    this also catches orphan-untracked quest-log files (gielinor step 9.2)."""
    r = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", str(path)],
                       capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() == ""


def _emit(results, ok_hint: str) -> int:
    """Shared print/exit harness for both rituals."""
    width = max(len(r[0]) for r in results)
    for cname, ok, detail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {cname:<{width}}  {detail}")
    if all(ok for _, ok, _ in results):
        print("\n" + ok_hint)
        return 0
    sys.stderr.write("\n" + BANNER + "\n")
    return 1


# ===================== dev-brain close ritual =====================

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


def run_dev(sid8: str) -> int:
    results = [
        check_closing(sid8),
        check_questlog(sid8),
        check_respawn(sid8),
        check_active_mode(),
        check_committed(sid8),
    ]
    return _emit(results, _wrapped_up_hint(sid8))


# ===================== gielinor player close ritual =====================
# Keyed by sid8 across players/*/. A single session may touch >1 player; the
# sid8 is the join key (it is embedded in quest filenames SNNN_<sid8>_<slug>.md
# and inventory resume filenames <slug>-resume__<sid8>.md).

def _player_quest_files(sid8: str, stages=("in-progress", "completed")):
    """[(player, path)] for every players/*/quest-log/<stage>/*<sid8>*.md."""
    out = []
    if not GIELINOR_PLAYERS.exists():
        return out
    for player_dir in GIELINOR_PLAYERS.iterdir():
        ql = player_dir / "quest-log"
        if not ql.is_dir():
            continue
        for stage in stages:
            base = ql / stage
            if base.is_dir():
                for f in base.glob(f"*{sid8}*.md"):
                    out.append((player_dir.name, f))
    return out


def _inbox_files(sid8: str):
    inbox = GIELINOR_PLAYERS / "inbox"
    if not inbox.is_dir():
        return []
    return list(inbox.glob(f"*{sid8}*.md"))


def _player_resume_files(player: str, sid8: str):
    """Inventory resume files for this player carrying the sid8 suffix."""
    inv = GIELINOR_PLAYERS / player / "inventory"
    if not inv.is_dir():
        return []
    # suffixed shape <slug>-resume__<sid8>.md is the only one keyable to a sid8;
    # legacy unsuffixed resume files cannot be attributed to a session.
    return [f for f in inv.glob(f"*resume*{sid8}*.md")]


def check_closing_player(sid8):
    name = "CLOSING posted"
    try:
        txt = GIELINOR_COMMS.read_text(encoding="utf-8", errors="replace")
        open_present = f"-{sid8} OPEN" in txt
        closing_present = f"-{sid8} CLOSING" in txt
        if not open_present:
            return (name, True, f"no '-{sid8} OPEN' in gielinor comms; CLOSING not required (step 8)")
        if closing_present:
            return (name, True, "gielinor/comms/active.md has a CLOSING for this sid8")
        return (name, False, f"OPEN posted but no '-{sid8} CLOSING' in gielinor comms (step 8)")
    except Exception as e:
        return (name, False, f"exception: {e}")


def check_questlog_player(sid8):
    name = "quest-log present"
    try:
        qf = _player_quest_files(sid8)
        inbox = _inbox_files(sid8)
        if qf:
            players = sorted({p for p, _ in qf})
            return (name, True, f"{len(qf)} quest file(s) for this sid8 ({', '.join(players)})")
        if inbox:
            return (name, True, f"{len(inbox)} inbox entry/entries for this sid8 (unscoped, step 11)")
        return (name, False,
                f"no players/*/quest-log or players/inbox entry matching *{sid8}*.md (step 2/11)")
    except Exception as e:
        return (name, False, f"exception: {e}")


def check_resume_player(sid8):
    name = "inventory resume present"
    try:
        inprog = _player_quest_files(sid8, stages=("in-progress",))
        if not inprog:
            return (name, True, "no in-progress quest for this sid8; resume file not required")
        missing = []
        for player in sorted({p for p, _ in inprog}):
            if not _player_resume_files(player, sid8):
                missing.append(player)
        if missing:
            return (name, False,
                    f"in-progress quest(s) but no inventory/*-resume__{sid8}.md for: "
                    f"{', '.join(missing)} (step 3 / step 9.1 enforcement clause)")
        return (name, True, "every player with an in-progress quest has a resume file for this sid8")
    except Exception as e:
        return (name, False, f"exception: {e}")


def check_committed_player(sid8):
    name = "core artifacts committed"
    try:
        files = [f for _, f in _player_quest_files(sid8)] + list(_inbox_files(sid8))
        for player in sorted({p for p, _ in _player_quest_files(sid8, stages=("in-progress",))}):
            files += _player_resume_files(player, sid8)
        dirty = [f for f in files if not _git_clean(f)]
        if dirty:
            return (name, False,
                    f"uncommitted/untracked: {', '.join(p.name for p in dirty)} (step 9)")
        if not files:
            return (name, True, "no artifacts for this sid8 to commit")
        return (name, True, f"{len(files)} quest/resume artifact(s) show no uncommitted changes")
    except Exception as e:
        return (name, False, f"exception: {e}")


def run_player(sid8: str) -> int:
    results = [
        check_closing_player(sid8),
        check_questlog_player(sid8),
        check_resume_player(sid8),
        check_committed_player(sid8),
    ]
    return _emit(results, _wrapped_up_hint(sid8))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sid8", required=True, help="first 8 chars of CLAUDE_CODE_SESSION_ID")
    ap.add_argument("--ritual", choices=("dev", "player"), default="dev",
                    help="which close ritual to verify (default: dev)")
    args = ap.parse_args()
    sid8 = args.sid8.strip()
    return run_player(sid8) if args.ritual == "player" else run_dev(sid8)


if __name__ == "__main__":
    sys.exit(main())

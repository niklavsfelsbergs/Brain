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

The player check-list also asserts the resume freshness header (quest/sid8/ts)
on this session's own resume files -- the gielinor end of Khaan item 6 (S118).
It is bounded to the current sid8, so legacy resumes that predate the header
convention are never inspected and never false-trip.
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

# Session-load hygiene caps (S125 audit). The brain's discipline-NUDGE chores
# (comms rotation, the respawn A4 trim) drift because nothing forces them -- the
# A4 trim was a verbatim no-op for 10+ consecutive closes. This converts those
# WATCHes into a close-GATE: a real FAIL until the surface is rotated/trimmed,
# so a must-hold cap actually holds (hook-blocking holds, WATCH drifts). The
# comms threshold mirrors comms/_about.md's ~300-line rotation trigger; the
# respawn cap is the header's own "current block + 1-2 pointers" rule.
THRESH_COMMS_LINES = 300
THRESH_RESPAWN_PRIOR = 2  # stacked '**Prior ([[Sxxx' per-session blocks (NOT the curated rollups)

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


def check_session_load_dev():
    name = "session-load hygiene"
    try:
        issues = []
        n = len(COMMS.read_text(encoding="utf-8", errors="replace").splitlines())
        if n > THRESH_COMMS_LINES:
            issues.append(f"dev comms/active.md {n} lines > {THRESH_COMMS_LINES} -- rotate to comms/archive/ "
                          "(keep newest ~30-45; move the rest; per comms/_about.md)")
        priors = RESPAWN.read_text(encoding="utf-8", errors="replace").count("**Prior ([[")
        if priors > THRESH_RESPAWN_PRIOR:
            issues.append(f"respawn.md has {priors} stacked Prior blocks > {THRESH_RESPAWN_PRIOR} -- run the A4 trim "
                          "(fold older blocks into the rollups; full detail stays in quest-log/)")
        if issues:
            return (name, False, "; ".join(issues))
        return (name, True, f"dev comms {n} lines, respawn {priors} stacked Prior block(s) -- within caps")
    except Exception as e:
        return (name, False, f"exception: {e}")


def run_dev(sid8: str) -> int:
    results = [
        check_closing(sid8),
        check_questlog(sid8),
        check_respawn(sid8),
        check_active_mode(),
        check_committed(sid8),
        check_session_load_dev(),
    ]
    return _emit(results, _wrapped_up_hint(sid8))


# ===================== gielinor player close ritual =====================
# Keyed by sid8 across players/*/. A single session may touch >1 player; the
# sid8 is the join key (it is embedded in quest filenames SNNN_<sid8>_<slug>.md
# and inventory resume filenames <slug>-resume__<sid8>.md). A CONTINUATION
# session has no filename match (the parent quest carries the parent's sid8), so
# the checks join on _session_quest_files = own (filename) + continued (lineage:
# body-stamp or a sid8-keyed resume's `quest:` header) -- see the lineage block
# above. This keeps the false-FAIL fix and the no-going-blind guarantee in ONE
# place that every downstream check shares.

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


# --- continuation lineage (the X.2-precondition fix) ----------------------
# A CONTINUATION session gets a fresh sid8 but appends to a parent quest born
# under a DIFFERENT sid8 -- so the parent's filename carries the parent's sid8,
# not this session's. Joining the player checks on the literal sid8 alone then
# false-FAILs a legitimate continuation (the work IS on disk, under the parent's
# name) and -- worse for the Stop-gate -- lets the downstream resume/freshness/
# committed checks go vacuously blind (they're gated on the same lookup). The
# two signals below recognize the lineage WITHOUT going blind to a genuinely
# missing quest-log: a session that left no own quest, no stamped append, and no
# resume naming an existing parent still FAILs.

_CONT_CACHE: dict = {}  # keyed incl. GIELINOR_PLAYERS so monkeypatched test trees never collide


def _resume_parent_quest(resume_path: Path):
    """The `quest:` freshness-header value of a resume file (e.g. 'S147_scm-perf-audit'),
    or None. Parse-lenient -- a substring scan of the first lines, same spirit as
    _missing_header_keys, so format drift never breaks it."""
    try:
        for line in resume_path.read_text(encoding="utf-8", errors="replace").splitlines()[:15]:
            s = line.strip()
            if s.lower().startswith("quest:"):
                return s.split(":", 1)[1].strip() or None
    except Exception:
        return None
    return None


def _quest_field_matches(quest_field: str, stem: str) -> bool:
    """True if a resume `quest:` value (SNNN_slug) names the quest file `stem`
    (SNNN_<parent_sid8>_slug). Matches on the SNNN prefix + trailing slug, so the
    parent's sid8 in the middle is irrelevant; an SNNN-only value matches on the
    prefix. The after-SNNN '_' guard stops 'S14' from prefixing 'S147_...'."""
    qf = (quest_field or "").strip()
    if not qf:
        return False
    snnn, _, slug = qf.partition("_")
    if not stem.startswith(snnn):
        return False
    after = stem[len(snnn):]
    if after and not after.startswith("_"):
        return False
    return stem.endswith(slug) if slug else True


def _continuation_quest_files(sid8: str, stages=("in-progress", "completed")):
    """[(player, path)] for quest files this session CONTINUED but did not create.

    Two lineage signals (the picked design -- resume-header + body-stamp):
      (a) the quest file's BODY carries this sid8 (an explicitly stamped append); or
      (b) a sid8-keyed resume file's `quest:` header names this quest (the robust
          signal -- present even when the continuation append is unstamped, as in
          the real S147/3bb042ff case).
    Files attributable by FILENAME (*{sid8}*.md) are excluded -- those are this
    session's OWN quests, already handled by _player_quest_files."""
    key = (str(GIELINOR_PLAYERS), sid8, tuple(stages))
    if key in _CONT_CACHE:
        return _CONT_CACHE[key]
    out = []
    if GIELINOR_PLAYERS.exists():
        for player_dir in GIELINOR_PLAYERS.iterdir():
            ql = player_dir / "quest-log"
            if not ql.is_dir():
                continue
            resume_targets = [q for q in (_resume_parent_quest(rf)
                              for rf in _player_resume_files(player_dir.name, sid8)) if q]
            for stage in stages:
                base = ql / stage
                if not base.is_dir():
                    continue
                for f in base.glob("*.md"):
                    if sid8 in f.name:
                        continue  # own quest (filename match) -- not a continuation
                    body = f.read_text(encoding="utf-8", errors="replace")
                    if sid8 in body or any(_quest_field_matches(q, f.stem) for q in resume_targets):
                        out.append((player_dir.name, f))
    _CONT_CACHE[key] = out
    return out


def _session_quest_files(sid8: str, stages=("in-progress", "completed")):
    """Own (filename-keyed) + continued (lineage) quest files for this session,
    deduped by path. The single join the player checks should use so a continuation
    is recognized everywhere the literal-sid8 lookup used to go blind."""
    seen, out = set(), []
    for player, f in _player_quest_files(sid8, stages) + _continuation_quest_files(sid8, stages):
        if f not in seen:
            seen.add(f)
            out.append((player, f))
    return out


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
        own = _player_quest_files(sid8)
        cont = _continuation_quest_files(sid8)
        inbox = _inbox_files(sid8)
        if own or cont:
            players = sorted({p for p, _ in own + cont})
            note = f"{len(own)} own"
            if cont:
                note += f" + {len(cont)} continued (lineage)"
            return (name, True, f"{note} quest file(s) for this sid8 ({', '.join(players)})")
        if inbox:
            return (name, True, f"{len(inbox)} inbox entry/entries for this sid8 (unscoped, step 11)")
        return (name, False,
                f"no quest-log/inbox entry for *{sid8}*.md, no stamped append, and no "
                f"resume naming an existing parent quest (step 2/11)")
    except Exception as e:
        return (name, False, f"exception: {e}")


def check_resume_player(sid8):
    name = "inventory resume present"
    try:
        inprog = _session_quest_files(sid8, stages=("in-progress",))
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


def _missing_header_keys(path: Path):
    """Header keys absent from a resume file's top region (empty = header present).

    Parse-lenient on purpose: a substring scan of the first lines, NOT a strict
    YAML parse, so benign format drift (spacing, field order, an extra comment)
    never false-trips -- only a wholesale-missing header does. Bounded to the
    CURRENT sid8's resume files by the caller, so legacy/other-session resumes
    that predate the convention are never inspected. (Khaan item 6, S118.)"""
    head = "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[:15]).lower()
    return [k for k in ("quest:", "sid8:", "ts:") if k not in head]


def check_freshness_header_player(sid8):
    name = "resume freshness header"
    try:
        inprog = _session_quest_files(sid8, stages=("in-progress",))
        if not inprog:
            return (name, True, "no in-progress quest for this sid8; no resume header required")
        bad, any_file = [], False
        for player in sorted({p for p, _ in inprog}):
            for f in _player_resume_files(player, sid8):
                any_file = True
                missing = _missing_header_keys(f)
                if missing:
                    bad.append(f"{f.name} (missing {', '.join(missing)})")
        if not any_file:
            # 'inventory resume present' already FAILs this; don't double-report.
            return (name, True, "no resume file for this sid8 (covered by 'inventory resume present')")
        if bad:
            return (name, False,
                    f"resume file(s) missing the freshness header: {'; '.join(bad)} "
                    "(quest/sid8/ts -- close-session step 3 / inventory _about convention)")
        return (name, True, "every resume file for this sid8 carries the quest/sid8/ts header")
    except Exception as e:
        return (name, False, f"exception: {e}")


def check_committed_player(sid8):
    name = "core artifacts committed"
    try:
        files = [f for _, f in _session_quest_files(sid8)] + list(_inbox_files(sid8))
        for player in sorted({p for p, _ in _session_quest_files(sid8, stages=("in-progress",))}):
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


def check_session_load_player():
    name = "session-load hygiene"
    try:
        n = len(GIELINOR_COMMS.read_text(encoding="utf-8", errors="replace").splitlines())
        if n > THRESH_COMMS_LINES:
            return (name, False,
                    f"gielinor comms/active.md {n} lines > {THRESH_COMMS_LINES} -- rotate to comms/archive/ "
                    "(keep newest ~30; move the rest; per comms/_about.md)")
        return (name, True, f"gielinor comms {n} lines -- within the {THRESH_COMMS_LINES}-line cap")
    except Exception as e:
        return (name, False, f"exception: {e}")


def run_player(sid8: str) -> int:
    results = [
        check_closing_player(sid8),
        check_questlog_player(sid8),
        check_resume_player(sid8),
        check_freshness_header_player(sid8),
        check_committed_player(sid8),
        check_session_load_player(),
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

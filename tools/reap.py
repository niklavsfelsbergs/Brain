#!/usr/bin/env python3
"""reap.py -- runtime-debris reaper for the brain (audit finding #8, structural half).

The brain accumulates runtime litter no ritual reaps: per-session intent
sidecars (.claude/intent/*.txt|*.mode) pile up as sessions die; .mode markers
were tracked-in-git noise (clobber-fuel for the #1 shared-index hazard);
sub-agent quest traces orphan in players/*/quest-log/in-progress/; inventory
resume files silt. Every reap was a deferred-manual step, and (the audit's law)
deferred-manual drifts.

This is the STRUCTURAL half: a runnable pass that QUANTIFIES every debris class
and ARCHIVES (never deletes -- block-deletes discipline) the SAFE infra classes
only (stale per-session intent sidecars at the intent root). The
PLAYER-namespace classes (orphaned sub-agent traces, silted inventory resumes)
are REPORT-ONLY here -- graduating those is alching / close-session's job
(Guthix lorebook draft 2026-05-30, alching-sweeps-orphan-subagent-traces). Run
read-only by default.

USAGE
  py tools/reap.py                 # dry-run: report every debris class + counts
  py tools/reap.py --apply         # archive stale infra intent sidecars ONLY
  py tools/reap.py --stale-days N  # age threshold for "stale" (default 2)

Safety: never touches a sidecar newer than the threshold (a live session), never
the CURRENT session's own sidecars, never a player file, never deletes.
"""
import argparse
import os
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INTENT = REPO / ".claude" / "intent"
INTENT_ARCHIVE = INTENT / "archive"


def _sid8() -> str:
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    return sid[:8] if sid else ""


def _age_days(p: Path) -> float:
    try:
        return (time.time() - p.stat().st_mtime) / 86400.0
    except OSError:
        return 0.0


def scan_stale_intent(stale_days: float, my_sid8: str):
    """Per-session intent sidecars at the intent ROOT, older than stale_days and
    not the current session's -- the only class this tool will archive."""
    out = []
    if not INTENT.is_dir():
        return out
    for p in INTENT.iterdir():
        if not p.is_file() or p.suffix not in (".txt", ".mode"):
            continue
        if my_sid8 and my_sid8 in p.name:   # never my own session
            continue
        if _age_days(p) < stale_days:        # never fresh -> never a live sibling
            continue
        out.append(p)
    return sorted(out)


def scan_player_debris():
    """REPORT-ONLY: orphaned sub-agent quest traces + inventory resume silt."""
    traces, resumes = [], []
    players = REPO / "gielinor" / "players"
    if players.is_dir():
        for pl in sorted(players.iterdir()):
            ip = pl / "quest-log" / "in-progress"
            if ip.is_dir():
                for f in ip.glob("*.md"):
                    n = f.name.lower()
                    if "_dwarf" in n or "_penguin" in n or n.startswith(("dwarf_", "penguin_")):
                        traces.append(f)
            inv = pl / "inventory"
            if inv.is_dir():
                resumes += list(inv.glob("*-resume*.md"))
    return sorted(traces), sorted(resumes)


def main() -> int:
    ap = argparse.ArgumentParser(description="Brain runtime-debris reaper (audit #8)")
    ap.add_argument("--apply", action="store_true",
                    help="archive stale infra intent sidecars (default: dry-run)")
    ap.add_argument("--stale-days", type=float, default=2.0)
    args = ap.parse_args()
    my = _sid8()

    stale = scan_stale_intent(args.stale_days, my)
    traces, resumes = scan_player_debris()
    arch_n = len(list(INTENT_ARCHIVE.glob("*"))) if INTENT_ARCHIVE.is_dir() else 0

    print(f"== reap.py (stale-days={args.stale_days}, my-sid8={my or '?'}) ==")
    print(f"[infra] stale intent sidecars at .claude/intent/ (>{args.stale_days}d, not mine): {len(stale)}")
    for p in stale:
        print(f"    {p.relative_to(REPO).as_posix()}  ({_age_days(p):.1f}d)")
    print(f"[infra] already in .claude/intent/archive/: {arch_n}  "
          f"(now gitignored; one-time `git rm --cached .claude/intent/archive/*.mode` to untrack)")
    print(f"[player REPORT-ONLY] orphaned sub-agent quest traces: {len(traces)}  -> alching graduates these")
    for t in traces:
        print(f"    {t.relative_to(REPO).as_posix()}")
    print(f"[player REPORT-ONLY] inventory resume files (silt candidates): {len(resumes)}  -> sweep on graduation (alching)")

    if not args.apply:
        print(f"\nDRY-RUN. {len(stale)} infra sidecars would be archived (nothing deleted). Re-run with --apply.")
        print("Player-namespace debris is report-only -- alching / close-session owns it.")
        return 0

    INTENT_ARCHIVE.mkdir(parents=True, exist_ok=True)
    moved = 0
    for p in stale:
        dest = INTENT_ARCHIVE / p.name
        if dest.exists():
            dest = INTENT_ARCHIVE / f"{p.stem}.{int(p.stat().st_mtime)}{p.suffix}"
        shutil.move(str(p), str(dest))
        moved += 1
    print(f"\nAPPLIED: archived {moved} stale infra intent sidecars -> .claude/intent/archive/ (nothing deleted).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

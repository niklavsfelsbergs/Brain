#!/usr/bin/env python3
"""quest-graduation-check.py -- the quest-graduation hygiene detector.

Read-only audit of per-player `quest-log/in-progress/`. The sibling of
`lesson-store-check.py`: same philosophy ("hand-enforced caps drift; detectors
hold"), applied to episodic memory instead of the lesson store.

The problem it watches (Guthix bankstanding B-020, 2026-06-18): quest promotion
(`in-progress/` -> `completed/`) is ritual discipline, not enforced, and the
ritual that does it (close-session step 6 / D-029) is skipped by fast / late-OPEN
sessions. So `in-progress/` accumulates: shipped-and-closed quests that were never
moved, plus sub-agent run-log traces that were never quests and have no
graduation path at all. Jebrim held 73 files at B-020.

The signal already exists: close-session writes `open_dep:` into each quest's
`inventory/<slug>-resume__<sid8>.md` header, and that field's own doc
(`inventory/_about.md`) names it the D-029 graduation discriminator. This detector
surfaces that signal OUTSIDE the ritual, so a respawn / bankstanding can see the
backlog instead of it growing silently.

Three classifications per in-progress file:

  GRADUATABLE -- a real quest whose resume declares `open_dep: none*`. The player
                 has stated no open dependency -> it should be in `completed/`.
                 (D-029: open_dep: none on a shipped quest graduates silently.)
  HELD        -- a real quest whose resume names an open dependency. Legitimately
                 still in-progress; left alone.
  NO_RESUME   -- a real quest with no resume file (close-session step-3 gap, or a
                 legacy quest). Soft flag: open_dep can't be read, classify by
                 hand. Not auto-graduatable.
  TRACE       -- a sub-agent run-log (shipping-agent / dwarf / gnome / penguin /
                 recon), not a quest. Counted separately; it inflates the
                 in-progress count but has no graduation path -- the structural
                 fix is to route these to quest-log/traces/ (B-020 Part 2).

This detector NEVER writes. Graduation (`git mv` to `completed/`) and trace
archival stay gated to close-session / a gnome / the principal -- a cross-
namespace mover would fight the S144 parallel-safety guard (sessions don't sweep
siblings). The detector only makes the backlog legible.

Run:
  python developer-braindead/verification/quest-graduation-check.py
  python developer-braindead/verification/quest-graduation-check.py --player jebrim
  python developer-braindead/verification/quest-graduation-check.py --graduatable   # list the batch
  python developer-braindead/verification/quest-graduation-check.py --brain-root <dir>  # test/override
  python developer-braindead/verification/quest-graduation-check.py --strict        # exit 1 on any flag
"""
import argparse
import re
import sys
from pathlib import Path

BRAIN_ROOT = Path(__file__).resolve().parents[2]

# Per-player non-trace in-progress count past which the backlog is flagged.
# (Not a hard limit -- a legibility threshold, like lesson-store's working cap.)
INPROGRESS_SOFT_CAP = 15

_SID8 = re.compile(r"^[0-9a-f]{8}$")
_SNNN = re.compile(r"^S(\d{3})")
_FM_FIELD = re.compile(r"^([A-Za-z_]+):\s*(.*)$")

# A sub-agent run-log trace, not a quest. Matches the filenames B-020 found:
#   S_shipagent_*, S_dwarf_*, penguin_*, recon_*  (no real SNNN, or a bare S_)
#   S256_shipping-agent_*, S251_<sid8>_shipagent_*, S241_shipagent_*  (embedded marker)
#   S253_<sid8>_g1_alching  (a _g1_/_d2_/_p3_ delegation marker)
_TRACE_PREFIX = re.compile(r"^(S_|penguin[_-]|recon[_-])", re.IGNORECASE)
_TRACE_MARKER = re.compile(
    r"(?:^|_)(?:shipagent|shipping-agent|dwarf|penguin|gnome)(?:_|$)",
    re.IGNORECASE,
)
# delegation suffix like _g1_ / _d2_ / _p10_ (NOT an 8-hex sid8)
_TRACE_DELEG = re.compile(r"_[dgp]\d{1,2}_", re.IGNORECASE)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def is_trace(stem: str) -> bool:
    """True if this in-progress filename is a sub-agent run-log, not a quest."""
    if _TRACE_PREFIX.search(stem):
        return True
    if _TRACE_DELEG.search(stem):
        return True
    if _TRACE_MARKER.search(stem):
        return True
    return False


def quest_keys(stem: str):
    """(snnn, sid8) parsed from a quest filename `SNNN_<sid8>_<slug>` (sid8
    optional; legacy `SNNN_YYYY-MM-DD_<slug>` yields sid8=None)."""
    snnn = None
    m = _SNNN.match(stem)
    if m:
        snnn = m.group(1)
    sid8 = None
    parts = stem.split("_")
    for p in parts[1:3]:  # the token right after SNNN is usually the sid8
        if _SID8.match(p):
            sid8 = p
            break
    return snnn, sid8


def parse_resume(path: Path) -> dict:
    """Pull the frontmatter fields (quest/sid8/ts/open_dep) from a resume file."""
    txt = _read(path)
    fields = {}
    if txt.startswith("---"):
        body = txt[3:]
        end = body.find("\n---")
        block = body[:end] if end != -1 else body
        for line in block.splitlines():
            m = _FM_FIELD.match(line.strip())
            if m:
                fields[m.group(1).lower()] = m.group(2).strip()
    # resume filename sid8 (…__<sid8>.md)
    fstem = path.name[:-3] if path.name.endswith(".md") else path.name
    fsid8 = None
    if "__" in fstem:
        tail = fstem.rsplit("__", 1)[1]
        if _SID8.match(tail):
            fsid8 = tail
    snnn = None
    qf = fields.get("quest", "")
    m = _SNNN.match(qf)
    if m:
        snnn = m.group(1)
    return {
        "path": path,
        "sid8": fields.get("sid8") or fsid8,
        "snnn": snnn,
        "open_dep": fields.get("open_dep"),
        "has_open_dep_field": "open_dep" in fields,
    }


def _open_dep_is_none(val) -> bool:
    """open_dep declares no open dependency if it starts with 'none'
    (handles 'none', 'none (shipped+committed; only parked X remain)')."""
    if val is None:
        return False
    return val.strip().lower().startswith("none")


def match_resume(qsnnn, qsid8, resumes: list):
    """Best resume for a quest: prefer sid8+snnn, then sid8, then snnn."""
    if qsid8 and qsnnn:
        for r in resumes:
            if r["sid8"] == qsid8 and r["snnn"] == qsnnn:
                return r
    if qsid8:
        for r in resumes:
            if r["sid8"] == qsid8:
                return r
    if qsnnn:
        for r in resumes:
            if r["snnn"] == qsnnn:
                return r
    return None


def audit_player(player_dir: Path) -> dict:
    name = player_dir.name
    res = {
        "player": name, "in_progress": 0, "quests": 0, "traces": 0,
        "graduatable": [], "held": [], "no_resume": [], "trace_files": [],
        "over_cap": False,
    }
    ip = player_dir / "quest-log" / "in-progress"
    if not ip.is_dir():
        return res
    inv = player_dir / "inventory"
    resumes = []
    if inv.is_dir():
        resumes = [parse_resume(p) for p in inv.glob("*resume*.md")]

    for qf in sorted(ip.glob("*.md")):
        res["in_progress"] += 1
        stem = qf.name[:-3]
        if is_trace(stem):
            res["traces"] += 1
            res["trace_files"].append(qf.name)
            continue
        res["quests"] += 1
        snnn, sid8 = quest_keys(stem)
        r = match_resume(snnn, sid8, resumes)
        if r is None:
            res["no_resume"].append(qf.name)
        elif not r["has_open_dep_field"]:
            res["no_resume"].append(qf.name)  # legacy resume, no open_dep -> by hand
        elif _open_dep_is_none(r["open_dep"]):
            res["graduatable"].append((qf.name, r["open_dep"] or ""))
        else:
            res["held"].append((qf.name, r["open_dep"] or ""))

    res["over_cap"] = res["quests"] > INPROGRESS_SOFT_CAP
    return res


def audit(brain_root: Path, only_player=None) -> list:
    players_dir = brain_root / "gielinor" / "players"
    out = []
    if not players_dir.is_dir():
        return out
    for d in sorted(players_dir.iterdir()):
        if not d.is_dir() or d.name == "inbox":
            continue
        if only_player and d.name != only_player:
            continue
        if not (d / "quest-log" / "in-progress").is_dir():
            continue
        out.append(audit_player(d))
    return out


def print_report(results: list, show_graduatable: bool) -> int:
    flags = 0
    print("=" * 72)
    print("QUEST-GRADUATION HYGIENE -- per-player in-progress backlog audit")
    print("=" * 72)
    if not results:
        print("\n** no players with quest-log/in-progress/ found **")
        return 1

    for r in results:
        print(f"\n[{r['player']}] {r['in_progress']} in-progress "
              f"= {r['quests']} quest(s) + {r['traces']} trace(s)")
        if r["over_cap"]:
            flags += 1
            print(f"  ** {r['quests']} real quests in-progress (soft cap "
                  f"{INPROGRESS_SOFT_CAP}) -- backlog; run a close-session graduation pass **")
        if r["graduatable"]:
            flags += 1
            print(f"  GRADUATABLE: {len(r['graduatable'])} quest(s) declare open_dep: none "
                  f"-> should be in completed/")
            if show_graduatable:
                for fn, dep in r["graduatable"]:
                    print(f"      - {fn}")
        if r["traces"]:
            flags += 1
            print(f"  TRACES: {r['traces']} sub-agent run-log(s) in in-progress/ "
                  f"(no graduation path -> route to quest-log/traces/, B-020 Part 2)")
        if r["no_resume"]:
            print(f"  NO-RESUME: {len(r['no_resume'])} quest(s) with no readable open_dep "
                  f"(close-session step-3 gap / legacy -> classify by hand)")
        if not (r["over_cap"] or r["graduatable"] or r["traces"] or r["no_resume"]):
            print("  ok (no backlog, no stray traces)")

    print("\n" + "-" * 72)
    total_grad = sum(len(r["graduatable"]) for r in results)
    total_trace = sum(r["traces"] for r in results)
    print(f"summary: {flags} flag-class(es). "
          f"{total_grad} graduatable quest(s), {total_trace} trace(s) across "
          f"{len(results)} player(s).")
    print("note: detector is read-only. The git mv stays gated to "
          "close-session / a gnome / the principal (S144 parallel-safety).")
    return flags


def main() -> int:
    ap = argparse.ArgumentParser(
        description="quest-graduation hygiene detector (read-only)")
    ap.add_argument("--brain-root", default="", help="override brain root (testing)")
    ap.add_argument("--player", default="", help="audit a single player")
    ap.add_argument("--graduatable", action="store_true",
                    help="list the graduatable quest filenames (the cleanup batch)")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any flag-class is raised")
    args = ap.parse_args()

    brain_root = Path(args.brain_root) if args.brain_root else BRAIN_ROOT
    results = audit(brain_root, only_player=(args.player or None))
    flags = print_report(results, show_graduatable=args.graduatable)

    if args.strict:
        return 1 if flags else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

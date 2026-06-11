#!/usr/bin/env python3
"""lesson-store-check.py -- the two-funnel lesson-store hygiene detector.

Read-only audit of the relationship between the brain's two lesson funnels:

  Funnel A -- the brain's examine/ (gated, archived, portable; the canonical
              self-model). Already tended by alching/bankstanding.
  Funnel B -- the harness auto-memory (MEMORY.md index + memory/*.md topic
              files; always-loaded every session/mode). Tended by NOTHING
              brain-side until this detector + the bankstanding reconcile step.

The 2026-06-01 B-015 steer is keep-BOTH: the two stores serve different
strengths, the problem was never duplication-of-stores but the missing BRIDGE
between them (see developer-braindead/bank/research/2026-06-11-lesson-store-grounding.md).
This detector is the enforcement half of that bridge -- "hand-enforced caps
drift, detectors hold".

Four checks (all read-only; the fixes are the bankstanding/alching reconcile
step's, principal-gated):

  1. CAP      -- MEMORY.md size vs a WORKING cap (headroom under the hard
                 harness cap, so retirement fires before truncation) and vs the
                 hard cap itself (over hard => the harness truncates at load).
  2. LINES    -- index lines over the ~200-char one-line guidance (move detail
                 into the topic file).
  3. INTEGRITY-- topic files not in the index (orphans) + index links to a
                 missing topic file (dangling).
  4. DRIFT    -- a Funnel-B topic file that DUPLICATES a Funnel-A examine anchor
                 (same lesson, two stores) WITHOUT a cross-link between them.
                 This is the reconcile worklist: each pair wants one canonical
                 examine anchor + a cross-link, not divergent hand-mirrored prose.

Run:
  python developer-braindead/verification/lesson-store-check.py
  python developer-braindead/verification/lesson-store-check.py --memory-dir <dir>   # test/override
  python developer-braindead/verification/lesson-store-check.py --exit-over-cap       # exit 1 if over HARD cap
  python developer-braindead/verification/lesson-store-check.py --strict              # exit 1 on any flag
"""
import argparse
import re
import sys
from pathlib import Path

BRAIN_ROOT = Path(__file__).resolve().parents[2]

# Harness memory cap is ~24.4 KB (the load-truncation point). Work under it so
# retirement triggers WITH headroom rather than at the cliff.
HARD_CAP_BYTES = 24400
WORKING_CAP_BYTES = 20000
LINE_CHAR_CAP = 200

# DRIFT matching thresholds (CHECK 4).
JACCARD_MIN = 0.6   # token-overlap floor for a "likely" duplicate
SHARED_MIN = 3      # and at least this many shared tokens (kills trivial matches)

_DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")
_KIND_PREFIX = re.compile(r"^(feedback|reference|project)[_-]")
# generic tokens that shouldn't drive a duplicate match on their own
_STOP = {"the", "a", "an", "to", "of", "is", "isnt", "not", "vs", "and", "for",
         "before", "after", "on", "in", "be", "it", "its"}


def _default_memory_dir() -> Path:
    """The harness auto-memory dir for THIS repo. Claude Code encodes the repo
    path into the project dir name by replacing : \\ / . with '-'."""
    enc = re.sub(r"[:\\/.]", "-", str(BRAIN_ROOT))
    cand = Path.home() / ".claude" / "projects" / enc / "memory"
    if cand.is_dir():
        return cand
    base = Path.home() / ".claude" / "projects"
    if base.is_dir():
        for h in sorted(base.glob("*brain*/memory")):
            if (h / "MEMORY.md").is_file():
                return h
    return cand  # may not exist; main() reports cleanly


def _norm_tokens(filename: str) -> list:
    s = filename.lower()
    if s.endswith(".md"):
        s = s[:-3]
    s = _DATE_PREFIX.sub("", s)
    s = _KIND_PREFIX.sub("", s)
    return [t for t in re.split(r"[-_]+", s) if t]


def _norm_key(filename: str) -> str:
    return " ".join(_norm_tokens(filename))


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _examine_anchors() -> list:
    """All examine/confirmed/<dated>.md anchors (global + per-player), excluding
    the curated current.md roll-up."""
    out = []
    g = BRAIN_ROOT / "gielinor" / "examine" / "confirmed"
    if g.is_dir():
        out += [p for p in g.glob("*.md") if p.name != "current.md"]
    players = BRAIN_ROOT / "gielinor" / "players"
    if players.is_dir():
        for d in sorted(players.iterdir()):
            ex = d / "examine" / "confirmed"
            if ex.is_dir():
                out += [p for p in ex.glob("*.md") if p.name != "current.md"]
    return out


def _linked(mem_path: Path, ex_path: Path) -> bool:
    """A cross-link exists if either body names the other's filename stem."""
    mem_stem = mem_path.name[:-3] if mem_path.name.endswith(".md") else mem_path.name
    ex_stem = ex_path.name[:-3] if ex_path.name.endswith(".md") else ex_path.name
    ex_dateless = _DATE_PREFIX.sub("", ex_stem)
    mem_body = _read(mem_path)
    ex_body = _read(ex_path)
    if ex_stem in mem_body or ex_dateless in mem_body:
        return True
    if mem_stem in ex_body:
        return True
    return False


def audit(memory_dir: Path) -> dict:
    res = {
        "memory_dir": memory_dir,
        "found": memory_dir.is_dir() and (memory_dir / "MEMORY.md").is_file(),
        "bytes": 0, "over_hard": False, "over_working": False,
        "long_lines": [], "orphans": [], "dangling": [],
        "topic_count": 0, "index_count": 0,
        "dupes": [],  # (mem_name, ex_relpath, confidence, linked)
    }
    if not res["found"]:
        return res

    index = memory_dir / "MEMORY.md"
    index_text = _read(index)
    res["bytes"] = len(index_text.encode("utf-8"))
    res["over_hard"] = res["bytes"] > HARD_CAP_BYTES
    res["over_working"] = res["bytes"] > WORKING_CAP_BYTES

    # CHECK 2 -- long index lines (char count, not bytes).
    for n, line in enumerate(index_text.splitlines(), 1):
        if line.startswith("- [") and len(line) > LINE_CHAR_CAP:
            res["long_lines"].append((n, len(line)))

    # CHECK 3 -- integrity (orphans + dangling).
    topic_files = [p for p in memory_dir.glob("*.md") if p.name != "MEMORY.md"]
    res["topic_count"] = len(topic_files)
    linked_names = set(re.findall(r"\(([a-z0-9_]+\.md)\)", index_text))
    res["index_count"] = len(linked_names)
    for p in topic_files:
        if p.name not in linked_names:
            res["orphans"].append(p.name)
    for name in sorted(linked_names):
        if not (memory_dir / name).is_file():
            res["dangling"].append(name)

    # CHECK 4 -- DRIFT: Funnel-B topic file duplicating a Funnel-A examine anchor
    # without a cross-link. Exact normalized-key match = high confidence;
    # token-overlap >= JACCARD_MIN (and >= SHARED_MIN shared tokens) = likely.
    anchors = _examine_anchors()
    anchor_keys = []
    for ap in anchors:
        toks = set(_norm_tokens(ap.name)) - _STOP
        anchor_keys.append((ap, _norm_key(ap.name), toks))
    for mp in topic_files:
        # only feedback-shaped memories are examine-eligible (project/reference are warm-only)
        if not mp.name.startswith("feedback"):
            continue
        m_key = _norm_key(mp.name)
        m_toks = set(_norm_tokens(mp.name)) - _STOP
        best = None  # (ap, confidence)
        for ap, a_key, a_toks in anchor_keys:
            if m_key == a_key:
                best = (ap, "DUPLICATE")
                break
            shared = m_toks & a_toks
            union = m_toks | a_toks
            if union and len(shared) >= SHARED_MIN and len(shared) / len(union) >= JACCARD_MIN:
                if best is None:
                    best = (ap, "likely")
        if best:
            ap, conf = best
            res["dupes"].append((
                mp.name,
                ap.relative_to(BRAIN_ROOT).as_posix(),
                conf,
                _linked(mp, ap),
            ))
    return res


def print_report(r: dict) -> int:
    flags = 0
    print("=" * 72)
    print("LESSON-STORE HYGIENE -- two-funnel (examine <-> harness MEMORY) audit")
    print("=" * 72)
    if not r["found"]:
        print(f"\n** MEMORY.md not found under {r['memory_dir']} **")
        print("   (pass --memory-dir, or run from the repo whose auto-memory this is)")
        return 1

    kb = r["bytes"] / 1024
    print(f"\nMEMORY.md: {r['bytes']} bytes ({kb:.1f} KB)  "
          f"[working cap {WORKING_CAP_BYTES}, hard cap {HARD_CAP_BYTES}]")
    if r["over_hard"]:
        flags += 1
        print("  ** OVER HARD CAP -- the harness TRUNCATES MEMORY.md at load. Retire/dedupe now. **")
    elif r["over_working"]:
        flags += 1
        print("  ! over working cap -- headroom gone; reconcile/retire to stay clear of the cliff.")
    else:
        print("  CAP: ok")

    if r["long_lines"]:
        flags += 1
        print(f"  LINES: {len(r['long_lines'])} index line(s) over {LINE_CHAR_CAP} chars "
              f"(trim to the rule; detail lives in the topic file):")
        for n, ln in sorted(r["long_lines"], key=lambda x: -x[1])[:5]:
            print(f"    - line {n}: {ln} chars")
        if len(r["long_lines"]) > 5:
            print(f"    ... and {len(r['long_lines']) - 5} more")
    else:
        print(f"  LINES: ok (all index lines <= {LINE_CHAR_CAP} chars)")

    print(f"  INTEGRITY: {r['topic_count']} topic file(s), {r['index_count']} index link(s)")
    if r["orphans"]:
        flags += 1
        print(f"    ** {len(r['orphans'])} ORPHAN topic file(s) (no index line -> add a pointer):")
        for o in r["orphans"]:
            print(f"      - {o}")
    if r["dangling"]:
        flags += 1
        print(f"    ** {len(r['dangling'])} DANGLING index link(s) (no topic file -> fix/remove):")
        for d in r["dangling"]:
            print(f"      - {d}")
    if not r["orphans"] and not r["dangling"]:
        print("    integrity: ok (index <-> topic files is a clean bijection)")

    dupes = r["dupes"]
    unlinked = [d for d in dupes if not d[3]]
    if dupes:
        print(f"\n  DRIFT: {len(dupes)} examine<->MEMORY duplicate(s) "
              f"({sum(1 for d in dupes if d[2]=='DUPLICATE')} exact, "
              f"{sum(1 for d in dupes if d[2]=='likely')} likely); "
              f"{len(unlinked)} WITHOUT a cross-link.")
        print("  (reconcile worklist: one canonical examine anchor + a cross-link per pair)")
        for mem, ex, conf, linked in sorted(dupes, key=lambda d: (d[3], d[2])):
            mark = "linked" if linked else "** UNLINKED **"
            print(f"    [{conf:9}] {mem}")
            print(f"                <-> {ex}   {mark}")
        if unlinked:
            flags += 1
    else:
        print("\n  DRIFT: none detected (no examine<->MEMORY duplicate by name; "
              "note: reworded twins evade name-matching -- the reconcile pass catches those by hand)")

    print("\n" + "-" * 72)
    print(f"summary: {flags} flag-class(es) raised. DRIFT recall is a conservative "
          f"floor (name-match only).")
    return flags


def main() -> int:
    ap = argparse.ArgumentParser(description="two-funnel lesson-store hygiene detector (read-only)")
    ap.add_argument("--memory-dir", default="", help="override the harness auto-memory dir (testing)")
    ap.add_argument("--exit-over-cap", action="store_true", help="exit 1 only if MEMORY.md is over the HARD cap")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any flag-class is raised")
    args = ap.parse_args()

    memory_dir = Path(args.memory_dir) if args.memory_dir else _default_memory_dir()
    r = audit(memory_dir)
    flags = print_report(r)

    if args.exit_over_cap:
        return 1 if r["found"] and r["over_hard"] else 0
    if args.strict:
        return 1 if (not r["found"] or flags) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

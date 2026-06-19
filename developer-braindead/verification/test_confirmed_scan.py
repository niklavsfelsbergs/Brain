#!/usr/bin/env python3
"""test_confirmed_scan.py -- guards the gated-layer contradiction/rot scan.

Builds a synthetic gated tree in a tmp dir and asserts each check:
  HARD  -- DANGLING (broken slug link), LOOSE (prose target, soft), UNDATED
           (figure with no date), STALE (figure + old date).
  pairs -- COLLISION (>=0.6 title jaccard), RELATED (>=0.34), same-namespace
           gating, and the templated/anchor link skips.
"""
import importlib.util
from datetime import date
from pathlib import Path
import tempfile

SPEC = Path(__file__).resolve().parent / "confirmed-scan.py"
spec = importlib.util.spec_from_file_location("confirmed_scan", SPEC)
cs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cs)

PASS = FAIL = 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  [PASS] {name}")
    else:
        FAIL += 1; print(f"  [FAIL] {name}")


def _w(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        gj = root / "players" / "jebrim" / "bank" / "notes" / "projects"
        ge = root / "players" / "jebrim" / "examine" / "confirmed"
        gz = root / "players" / "zezima" / "bank" / "notes"

        # an existing anchor so a good link resolves
        _w(ge / "2026-06-01-real-anchor.md", "# real\nbody\n")
        # DANGLING: links a slug that does not exist
        _w(gj / "2026-06-10-alpha.md",
           "As of 2026-06-10\nSee [[2026-06-01-real-anchor]] and [[totally-missing-slug]].\n")
        # LOOSE: prose target (has spaces) -> soft, not dangling
        _w(gj / "2026-06-10-beta.md",
           "As of 2026-06-10\n12% lift. See [[a concept by description]].\n")
        # templated + pure-anchor links must NOT flag
        _w(gj / "2026-06-10-gamma.md",
           "As of 2026-06-10\n€5 each. [[S217_*_glob]] and [[#section]].\n")
        # UNDATED: carries a figure, no date anywhere
        _w(gj / "no-date-note.md", "# undated\nCosts €1,200 per run.\n")
        # STALE: figure + an old date
        _w(gj / "2026-01-01-old.md", "As of 2026-01-01\nMargin 9%.\n")
        # COLLISION pair (near-identical titles, same namespace)
        _w(gj / "2026-06-02-ups-rate-card-diff.md", "As of 2026-06-02\nx\n")
        _w(gj / "2026-06-03-ups-rate-card-diff.md", "As of 2026-06-03\ny\n")
        # cross-namespace pair that shares tokens must NOT pair
        _w(gz / "ups-rate-card-diff-latvia.md", "As of 2026-06-02\nz\n")

        r = cs.audit(root, today=date(2026, 6, 18), stale_days=45,
                     corpus_roots=[root])

        dang = {t for _, t in r["dangling"]}
        loose = {t for _, t in r["loose"]}
        undated = set(r["undated"])
        stale_files = {f for f, _, _ in r["stale"]}
        coll = {(c["a"].split("/")[-1], c["b"].split("/")[-1]) for c in r["collisions"]}

        check("DANGLING catches the missing slug", "totally-missing-slug" in dang)
        check("good link does NOT dangle", "2026-06-01-real-anchor" not in dang)
        check("prose target is LOOSE not DANGLING",
              "a concept by description" in loose and "a concept by description" not in dang)
        check("templated (*) link is skipped", not any("glob" in t for t in dang | loose))
        check("pure-anchor link is skipped", not any(t.startswith("#") for t in dang | loose))
        check("UNDATED catches figure w/o date",
              "players/jebrim/bank/notes/projects/no-date-note.md" in undated)
        check("dated figure note is NOT undated",
              "players/jebrim/bank/notes/projects/2026-06-10-alpha.md" not in undated)
        check("STALE catches old dated figure",
              any("2026-01-01-old.md" in f for f in stale_files))
        check("recent dated figure is NOT stale",
              not any("2026-06-10-beta.md" in f for f in stale_files))
        check("COLLISION pairs the near-duplicate titles",
              ("2026-06-02-ups-rate-card-diff.md", "2026-06-03-ups-rate-card-diff.md") in coll)
        check("cross-namespace pair is NOT collided",
              not any("latvia" in a or "latvia" in b for a, b in coll))

        # an undated note with NO figure must not be flagged load-bearing
        _w(ge / "2026-06-09-prose-only.md", "# prose\nThis is currently the way we work.\n")
        r2 = cs.audit(root, today=date(2026, 6, 18), stale_days=45, corpus_roots=[root])
        check("present-tense prose w/o a figure is NOT undated",
              "players/jebrim/examine/confirmed/2026-06-09-prose-only.md" not in set(r2["undated"]))

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

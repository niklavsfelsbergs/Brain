#!/usr/bin/env python3
"""test_domain_coverage.py -- guards the §Z.D domain-coverage detector.

Builds a synthetic players/ tree in a tmp dir, repoints the detector at it, and
asserts the three signals: STALE (corpus note newer than synthesized), UNCOVERED
(a note in no digest corpus), and NO-LAYER (notes but no digests). Plus MISSING
(corpus cites a vanished note) and the no-false-stale case (synth >= mtime).

Run: python developer-braindead/verification/domain-coverage.py via import.
"""
import importlib.util
import os
import sys
import tempfile
import time
from pathlib import Path

SPEC = Path(__file__).resolve().parent / "domain-coverage.py"
spec = importlib.util.spec_from_file_location("domain_coverage", SPEC)
dc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dc)

PASS = FAIL = 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  [PASS] {name}")
    else:
        FAIL += 1; print(f"  [FAIL] {name}")


def _note(player_root, rel, days_ago=10):
    p = player_root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# note\nbody\n", encoding="utf-8")
    t = time.time() - days_ago * 86400
    os.utime(p, (t, t))
    return p


def _digest(player_root, slug, corpus, synthesized):
    d = player_root / "bank" / "domains"
    d.mkdir(parents=True, exist_ok=True)
    lines = ["---", f"domain: {slug}", f"title: {slug} digest", "patterns:",
             f"  - {slug}", "corpus:"]
    lines += [f"  - {c}" for c in corpus]
    lines += [f"synthesized: {synthesized}", "freshness: " + synthesized, "---", "", "# body"]
    (d / f"{slug}.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        dc.PLAYERS_DIR = root / "gielinor" / "players"

        # jebrim: a fresh digest, a STALE digest, an uncovered note, a missing-corpus ref.
        jeb = dc.PLAYERS_DIR / "jebrim"
        _note(jeb, "bank/notes/projects/fresh_note.md", days_ago=30)
        _note(jeb, "bank/notes/projects/changed_note.md", days_ago=1)   # edited yesterday
        _note(jeb, "bank/notes/projects/orphan_note.md", days_ago=5)    # in no corpus
        _digest(jeb, "fresh", ["bank/notes/projects/fresh_note.md"], "2026-06-08")
        _digest(jeb, "stale", ["bank/notes/projects/changed_note.md",
                               "bank/notes/projects/gone.md"], "2026-01-01")

        # zezima: notes, no digests -> NO-LAYER.
        zez = dc.PLAYERS_DIR / "zezima"
        _note(zez, "bank/notes/projects/latvia.md", days_ago=3)

        # _infra dir + inbox are skipped.
        (dc.PLAYERS_DIR / "_about").mkdir(parents=True, exist_ok=True)
        (dc.PLAYERS_DIR / "inbox").mkdir(parents=True, exist_ok=True)

        jr = dc.audit_player(jeb)
        zr = dc.audit_player(zez)

        check("jebrim has layer", jr["has_layer"] is True)
        check("stale detected (changed_note > 2026-01-01)",
              any("changed_note" in s[1] for s in jr["stale"]))
        check("fresh NOT stale (synth 2026-06-08 >= 30d-old note)",
              not any("fresh_note" in s[1] for s in jr["stale"]))
        check("missing corpus detected (gone.md)",
              any("gone.md" in m[1] for m in jr["missing"]))
        check("uncovered detected (orphan_note)",
              any("orphan_note" in n for v in jr["uncovered"].values() for n in v))
        check("covered notes NOT uncovered (changed_note absent from uncovered)",
              not any("changed_note" in n for v in jr["uncovered"].values() for n in v))
        check("zezima flagged NO-LAYER (notes, no digests)",
              zr["has_layer"] is False and zr["note_count"] == 1)

        names = {p.name for p in dc._player_dirs()}
        check("_infra + inbox skipped from player scan", "_about" not in names and "inbox" not in names)

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())

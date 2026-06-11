#!/usr/bin/env python3
"""test_lesson_store_check.py -- guards the two-funnel lesson-store detector.

Builds a synthetic harness-memory dir + a synthetic examine/ tree in a tmp dir,
repoints the detector at both, and asserts the four checks: CAP (over working /
hard), LINES (>200 chars), INTEGRITY (orphan + dangling), and DRIFT (exact +
likely examine<->MEMORY duplicates, the linked-vs-unlinked split, and that
project/reference memories + unique lessons are NOT flagged).
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

SPEC = Path(__file__).resolve().parent / "lesson-store-check.py"
spec = importlib.util.spec_from_file_location("lesson_store_check", SPEC)
ls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls)

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


def _anchor(root: Path, rel: str, body: str = "# anchor\nbody\n"):
    _w(root / rel, body)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        ls.BRAIN_ROOT = root
        # tiny caps so CAP fires deterministically on the small fixture (~629 B)
        ls.HARD_CAP_BYTES = 500
        ls.WORKING_CAP_BYTES = 300

        mem = root / "memory"
        mem.mkdir(parents=True, exist_ok=True)

        # --- topic files (Funnel B) ---
        _w(mem / "feedback_reconcile_definition_before_numbers.md", "# dup, unlinked\nbody\n")
        _w(mem / "feedback_verify_diffs_both_ways.md", "# likely dup, unlinked\nbody\n")
        _w(mem / "feedback_some_linked_lesson.md",
           "# dup but linked\nsee [[2026-01-01-some-linked-lesson]]\n")
        _w(mem / "feedback_unique_lesson.md", "# no twin\nbody\n")
        _w(mem / "project_brain_overview.md", "# project, drift-exempt\nbody\n")
        _w(mem / "feedback_orphaned.md", "# present on disk, absent from index\nbody\n")

        long_line = "- [Long](feedback_unique_lesson.md) — " + ("x" * 220)
        index = "\n".join([
            "- [Reconcile](feedback_reconcile_definition_before_numbers.md) — pin the definition first",
            "- [Diffs](feedback_verify_diffs_both_ways.md) — self-diff plus synthetic positive",
            "- [Linked](feedback_some_linked_lesson.md) — already cross-linked",
            "- [Project](project_brain_overview.md) — two siblings",
            long_line,
            "- [Ghost](feedback_vanished.md) — dangling: no topic file on disk",
        ]) + "\n"
        _w(mem / "MEMORY.md", index)

        # --- examine anchors (Funnel A): global + two players ---
        _anchor(root, "gielinor/examine/confirmed/2026-06-01-verify-diffs-both-ways-explicit.md")
        _anchor(root, "gielinor/examine/confirmed/current.md", "roll-up; must be ignored\n")
        _anchor(root, "gielinor/players/jebrim/examine/confirmed/2026-05-29-reconcile-definition-before-numbers.md")
        _anchor(root, "gielinor/players/zezima/examine/confirmed/2026-01-01-some-linked-lesson.md")

        r = ls.audit(mem)

        # CAP
        check("found MEMORY.md", r["found"] is True)
        check("over working cap", r["over_working"] is True)
        check("over hard cap", r["over_hard"] is True)

        # LINES
        check("long index line flagged (>200 chars)", len(r["long_lines"]) == 1)

        # INTEGRITY
        check("orphan flagged (feedback_orphaned.md)", "feedback_orphaned.md" in r["orphans"])
        check("dangling flagged (feedback_vanished.md)", "feedback_vanished.md" in r["dangling"])
        check("current.md NOT counted as an anchor",
              all("current.md" not in d[1] for d in r["dupes"]))

        # DRIFT
        dmap = {d[0]: d for d in r["dupes"]}
        check("exact duplicate detected (reconcile)",
              dmap.get("feedback_reconcile_definition_before_numbers.md", (None, None, None))[2] == "DUPLICATE")
        check("exact duplicate is UNLINKED",
              dmap.get("feedback_reconcile_definition_before_numbers.md", (None, None, None, True))[3] is False)
        check("likely duplicate detected (verify_diffs)",
              dmap.get("feedback_verify_diffs_both_ways.md", (None, None, None))[2] == "likely")
        check("linked duplicate marked linked (some_linked)",
              dmap.get("feedback_some_linked_lesson.md", (None, None, None, False))[3] is True)
        check("unique lesson NOT flagged", "feedback_unique_lesson.md" not in dmap)
        check("project_ memory drift-exempt", "project_brain_overview.md" not in dmap)

        # report runs without error and counts flags
        flags = ls.print_report(r)
        check("print_report raised flags", flags > 0)

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())

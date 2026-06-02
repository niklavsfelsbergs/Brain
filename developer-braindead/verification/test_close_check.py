#!/usr/bin/env python3
"""test_close_check.py -- boundary harness for close_check.py's PLAYER ritual,
focused on the continuation-lineage fix (the X.2 Stop-gate precondition).

The bug it guards against: the player checks joined on the LITERAL sid8 (glob
*{sid8}*.md), so a CONTINUATION session -- fresh sid8, appending to a parent
quest born under a DIFFERENT sid8 -- false-FAILed `quest-log present` and, worse,
sent the downstream resume/freshness/committed checks vacuously BLIND. The fix
recognizes lineage via two signals (a sid8-keyed resume's `quest:` header, or a
body-stamped append) WITHOUT going blind to a genuinely-missing quest-log.

Each test builds a synthetic gielinor/players tree in a unique tempdir and
monkeypatches close_check's module globals at it. _git_clean is stubbed where a
test exercises the committed check. Two anchor requirements (the brief):
  * a continuation case that should PASS  (test_continuation_* )
  * a genuinely-incomplete case that must still FAIL (test_gap_* )

Run:  python developer-braindead/verification/test_close_check.py
Exit 0 = all pass; 1 = a failure (prints each).
"""

import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("close_check", HERE / "close_check.py")
cc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cc)

_FAILS: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}  {detail}")
        _FAILS.append(name)


# --- synthetic tree builder ------------------------------------------------

def _point_globals_at(tmp: Path):
    """Repoint close_check's module globals at a temp tree + reset the memo."""
    cc.ROOT = tmp
    cc.GIELINOR = tmp / "gielinor"
    cc.GIELINOR_COMMS = tmp / "gielinor" / "comms" / "active.md"
    cc.GIELINOR_PLAYERS = tmp / "gielinor" / "players"
    cc._CONT_CACHE.clear()


def _w(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build(tmp: Path, *, quests=(), resumes=(), comms="", player="jebrim"):
    """quests: [(stage, filename, body)]; resumes: [(filename, body)]."""
    base = tmp / "gielinor" / "players" / player / "quest-log"
    for stage, fname, body in quests:
        _w(base / stage / fname, body)
    inv = tmp / "gielinor" / "players" / player / "inventory"
    for fname, body in resumes:
        _w(inv / fname, body)
    _w(tmp / "gielinor" / "comms" / "active.md", comms or "# comms\n")
    _point_globals_at(tmp)


def _resume_body(quest, sid8, ts="2026-06-02 (sess-2)", extra=""):
    return f"---\nquest: {quest}\nsid8: {sid8}\nts: {ts}\n---\n\n# resume\n{extra}\n"


# --- continuation PASS cases (the false-FAIL fix) --------------------------

def test_continuation_via_resume_header_unstamped_append():
    """Case 1 shape (real S147/3bb042ff): parent born under PARENT88, continuation
    CONT88 appends WITHOUT stamping its sid8 in the body -> only the resume's
    `quest:` header carries the lineage. quest-log + resume + freshness all PASS."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        build(tmp,
              quests=[("in-progress", "S147_PARENT88_scm-perf-audit.md",
                       "# S147\nwork by the parent session, no continuation sid here\n")],
              resumes=[("scm-perf-audit-resume__CONT8888.md",
                        _resume_body("S147_scm-perf-audit", "CONT8888"))])
        n, ok, det = cc.check_questlog_player("CONT8888")
        check("continuation/resume-header => quest-log present PASS", ok, det)
        check("continuation/resume-header => credited as continued", "continued" in det, det)
        _, ok2, det2 = cc.check_resume_player("CONT8888")
        check("continuation/resume-header => resume present PASS", ok2, det2)
        _, ok3, det3 = cc.check_freshness_header_player("CONT8888")
        check("continuation/resume-header => freshness header PASS", ok3, det3)


def test_continuation_via_body_stamp():
    """Case 2 shape (real S124/7b460f67): the append IS sid8-stamped in the body,
    AND a resume exists -> quest-log present + resume + freshness PASS."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        build(tmp,
              quests=[("in-progress", "S124_PARENT88_shipping-report.md",
                       "# S124\n## continuation (sess-2, sid BODYST88)\nappended turn\n")],
              resumes=[("shipping-report-resume__BODYST88.md",
                        _resume_body("S124_shipping-report", "BODYST88"))])
        n, ok, det = cc.check_questlog_player("BODYST88")
        check("continuation/body-stamp => quest-log present PASS", ok, det)
        _, ok2, det2 = cc.check_resume_player("BODYST88")
        check("continuation/body-stamp => resume present PASS", ok2, det2)


def test_continuation_in_completed_stage():
    """Parent quest MOVED to completed/ this session -> still recognized (stages)."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        build(tmp,
              quests=[("completed", "S100_PARENT88_done-thing.md", "# S100\nfinished\n")],
              resumes=[("done-thing-resume__CONT8888.md",
                        _resume_body("S100_done-thing", "CONT8888"))])
        n, ok, det = cc.check_questlog_player("CONT8888")
        check("continuation/completed-stage => quest-log present PASS", ok, det)
        # no in-progress quest -> resume not required (vacuous PASS is correct here)
        _, ok2, det2 = cc.check_resume_player("CONT8888")
        check("continuation/completed-stage => resume not required", ok2, det2)


def test_own_quest_filename_match_unregressed():
    """The normal path (quest born THIS session) still PASSes after the refactor."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        build(tmp,
              quests=[("in-progress", "S200_OWN88888_fresh.md", "# S200\nnew work\n")],
              resumes=[("fresh-resume__OWN88888.md", _resume_body("S200_fresh", "OWN88888"))])
        n, ok, det = cc.check_questlog_player("OWN88888")
        check("own filename-match => quest-log present PASS", ok, det)
        check("own filename-match => credited as own", "1 own" in det, det)


# --- genuine-gap FAIL cases (no going blind) -------------------------------

def test_gap_nothing_on_disk():
    """No quest, no resume, no inbox -> quest-log present must FAIL."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        build(tmp, quests=[("in-progress", "S001_OTHER888_unrelated.md", "# S001\nnothing here\n")])
        n, ok, det = cc.check_questlog_player("MISSING8")
        check("gap/nothing => quest-log present FAIL", not ok, det)


def test_gap_continuation_without_resume_fails_resume_check():
    """A body-stamped continuation in-progress quest but NO resume file -> the
    relaxation must NOT swallow the missing resume; resume present FAILs."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        build(tmp,
              quests=[("in-progress", "S301_PARENT88_thing.md",
                       "# S301\ncontinuation append, sid NORES888, no resume written\n")])
        n, ok, det = cc.check_questlog_player("NORES888")
        check("gap/no-resume => quest-log present still PASS (work exists)", ok, det)
        _, ok2, det2 = cc.check_resume_player("NORES888")
        check("gap/no-resume => resume present FAIL (not blind)", not ok2, det2)


def test_gap_resume_names_nonexistent_parent():
    """A resume whose `quest:` names a parent quest that does NOT exist must not
    fabricate a pass -> no own, no continuation -> quest-log present FAILs."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        build(tmp,
              quests=[("in-progress", "S400_OTHER888_unrelated.md", "# S400\nunrelated\n")],
              resumes=[("ghost-resume__DANGLE88.md",
                        _resume_body("S999_ghost-quest-that-was-never-written", "DANGLE88"))])
        n, ok, det = cc.check_questlog_player("DANGLE88")
        check("gap/dangling-resume => quest-log present FAIL", not ok, det)


def test_gap_continuation_freshness_header_missing():
    """Continuation resume WITHOUT the quest/sid8/ts header -> freshness FAILs
    (the freshness arm must not go blind on continuations either)."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        build(tmp,
              quests=[("in-progress", "S500_PARENT88_thing.md", "# S500\nparent work\n")],
              resumes=[("thing-resume__NOHDR888.md", "# resume\nno header at all\n")])
        # lineage still recognized via body? no -- via... nothing. Add a stamped append
        # so the quest IS attributed, isolating the freshness failure.
        _w(tmp / "gielinor" / "players" / "jebrim" / "quest-log" / "in-progress"
           / "S500_PARENT88_thing.md", "# S500\nappend sid NOHDR888\n")
        cc._CONT_CACHE.clear()
        n, ok, det = cc.check_questlog_player("NOHDR888")
        check("gap/no-header => quest-log present PASS (work exists)", ok, det)
        _, ok2, det2 = cc.check_freshness_header_player("NOHDR888")
        check("gap/no-header => freshness header FAIL (not blind)", not ok2, det2)


# --- committed check: no going blind on the continuation parent ------------

def test_committed_continuation_uncommitted_parent_fails():
    """The continued PARENT quest (modified this session) being uncommitted must be
    caught -- the old cascade went blind here (vacuous PASS)."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        parent = tmp / "gielinor" / "players" / "jebrim" / "quest-log" / "in-progress" / "S147_PARENT88_x.md"
        build(tmp,
              quests=[("in-progress", "S147_PARENT88_x.md", "# S147\nparent\n")],
              resumes=[("x-resume__CONT8888.md", _resume_body("S147_x", "CONT8888"))])
        cc._git_clean = lambda p: Path(p).name != "S147_PARENT88_x.md"  # parent dirty
        n, ok, det = cc.check_committed_player("CONT8888")
        check("committed/uncommitted-parent => FAIL (not blind)", not ok, det)
        check("committed/uncommitted-parent => names the parent", "S147_PARENT88_x.md" in det, det)


def test_committed_continuation_all_clean_passes():
    """Continuation with parent + resume all committed -> committed check PASSes."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        build(tmp,
              quests=[("in-progress", "S147_PARENT88_x.md", "# S147\nparent\n")],
              resumes=[("x-resume__CONT8888.md", _resume_body("S147_x", "CONT8888"))])
        cc._git_clean = lambda p: True
        n, ok, det = cc.check_committed_player("CONT8888")
        check("committed/all-clean => PASS", ok, det)


# --- _quest_field_matches unit edges ---------------------------------------

def test_quest_field_matcher_edges():
    f = cc._quest_field_matches
    check("matcher: SNNN_slug names SNNN_<sid8>_slug",
          f("S147_scm-perf-audit", "S147_dcb495a7_scm-perf-audit"))
    check("matcher: S14 does NOT prefix S147_...",
          not f("S14_scm", "S147_dcb495a7_scm"))
    check("matcher: SNNN-only matches on prefix",
          f("S147", "S147_dcb495a7_scm-perf-audit"))
    check("matcher: wrong slug rejected",
          not f("S147_other-slug", "S147_dcb495a7_scm-perf-audit"))
    check("matcher: empty field rejected", not f("", "S147_x_y"))


# --- run all ---------------------------------------------------------------

def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    print(f"close_check player-ritual continuation harness -- {len(tests)} test groups\n")
    for t in tests:
        t.__call__()
    print()
    if _FAILS:
        print(f"FAILED ({len(_FAILS)}): {', '.join(_FAILS)}")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

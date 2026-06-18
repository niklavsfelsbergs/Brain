#!/usr/bin/env python3
"""Tests for quest-graduation-check.py -- the quest-graduation hygiene detector.

Builds a synthetic brain root in a temp dir (no dependence on the live brain) and
exercises classification (GRADUATABLE / HELD / NO_RESUME / TRACE), resume matching
by sid8+SNNN, the open_dep: none discriminator, and the soft-cap flag.

Run: python developer-braindead/verification/test_quest_graduation.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "qg", _HERE / "quest-graduation-check.py")
qg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qg)

_passed = 0
_failed = 0


def check(name, cond):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  PASS  {name}")
    else:
        _failed += 1
        print(f"  FAIL  {name}")


def _mk(root: Path, player: str, in_progress: dict, resumes: dict):
    """in_progress: {filename_stem: None}; resumes: {filename_stem: frontmatter_str}."""
    ip = root / "gielinor" / "players" / player / "quest-log" / "in-progress"
    inv = root / "gielinor" / "players" / player / "inventory"
    ip.mkdir(parents=True, exist_ok=True)
    inv.mkdir(parents=True, exist_ok=True)
    for stem in in_progress:
        (ip / f"{stem}.md").write_text(f"# {stem}\n", encoding="utf-8")
    for stem, fm in resumes.items():
        (inv / f"{stem}.md").write_text(fm, encoding="utf-8")


def _resume(quest, sid8, open_dep=None):
    lines = ["---", f"quest: {quest}", f"sid8: {sid8}", "ts: 2026-06-18 10:00"]
    if open_dep is not None:
        lines.append(f"open_dep: {open_dep}")
    lines += ["---", "", "# resume", "**Where we are:** x", ""]
    return "\n".join(lines)


# ---- is_trace classification ----
def test_is_trace():
    print("test_is_trace")
    check("S_ prefix is trace", qg.is_trace("S_shipagent_foo"))
    check("penguin_ is trace", qg.is_trace("penguin_usps-fuel"))
    check("recon_ is trace", qg.is_trace("recon_dashboard-state"))
    check("embedded _shipagent_ is trace", qg.is_trace("S241_shipagent_na_cost"))
    check("embedded _shipping-agent_ is trace", qg.is_trace("S256_shipping-agent_quota"))
    check("dwarf delegation _d1_ is trace", qg.is_trace("S194_907d4e63_d1_numbers"))
    check("gnome delegation _g1_ is trace", qg.is_trace("S235_fcf8efd5_g1_alching"))
    check("real quest is NOT trace", not qg.is_trace("S265_5cbb1d00_scm-resizable-columns"))
    check("real quest 2 is NOT trace",
          not qg.is_trace("S251_d8d2c1be_ups-may-accounting-mart-vs-silver"))
    # a slug that merely contains 'penguin' mid-word must not false-trigger:
    check("mid-word safe", not qg.is_trace("S300_aabbccdd_report-on-something"))


# ---- open_dep discriminator ----
def test_open_dep():
    print("test_open_dep_is_none")
    check("plain none", qg._open_dep_is_none("none"))
    check("none with parenthetical",
          qg._open_dep_is_none("none (shipped+committed; only parked Q15 remain)"))
    check("None capitalized", qg._open_dep_is_none("None"))
    check("named dep is not none", not qg._open_dep_is_none("awaiting principal commit go"))
    check("SHIPPED-with-residual is not none",
          not qg._open_dep_is_none("SHIPPED — committed a22ca52; only Breakdown remains"))
    check("missing is not none", not qg._open_dep_is_none(None))


# ---- quest_keys parsing ----
def test_quest_keys():
    print("test_quest_keys")
    snnn, sid8 = qg.quest_keys("S265_5cbb1d00_scm-resizable-columns")
    check("snnn parsed", snnn == "265")
    check("sid8 parsed", sid8 == "5cbb1d00")
    snnn2, sid8b = qg.quest_keys("S014_2026-05-21_ttyd-howto")  # legacy date form
    check("legacy snnn parsed", snnn2 == "014")
    check("legacy sid8 None", sid8b is None)


# ---- end-to-end classification on a synthetic player ----
def test_classification():
    print("test_classification")
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        in_progress = {
            "S900_aaaaaaaa_grad-foo": None,           # graduatable (open_dep none)
            "S901_bbbbbbbb_held-bar": None,           # held (named dep)
            "S902_cccccccc_noresume-baz": None,       # no resume at all
            "S903_dddddddd_legacy-qux": None,         # resume but no open_dep field
            "S906_11111111_grad-parked": None,        # graduatable (none + parked)
            "S_shipagent_trace-one": None,            # trace (prefix)
            "penguin_trace-two": None,                # trace (prefix)
            "S904_eeeeeeee_shipagent_trace-three": None,  # trace (marker)
            "S905_ffffffff_d1_trace-four": None,      # trace (delegation)
        }
        resumes = {
            "grad-foo-resume__aaaaaaaa": _resume("S900_grad-foo", "aaaaaaaa", "none"),
            "held-bar-resume__bbbbbbbb": _resume("S901_held-bar", "bbbbbbbb",
                                                 "awaiting principal commit go"),
            "legacy-qux-resume__dddddddd": _resume("S903_legacy-qux", "dddddddd", None),
            "grad-parked-resume__11111111": _resume(
                "S906_grad-parked", "11111111", "none (shipped+committed; parked X)"),
        }
        _mk(root, "tester", in_progress, resumes)
        results = qg.audit(root, only_player="tester")
        check("one player audited", len(results) == 1)
        r = results[0]
        check("in_progress count 9", r["in_progress"] == 9)
        check("quests count 5", r["quests"] == 5)
        check("traces count 4", r["traces"] == 4)
        grad = {fn for fn, _ in r["graduatable"]}
        check("grad-foo graduatable", "S900_aaaaaaaa_grad-foo.md" in grad)
        check("grad-parked graduatable", "S906_11111111_grad-parked.md" in grad)
        check("graduatable count 2", len(r["graduatable"]) == 2)
        held = {fn for fn, _ in r["held"]}
        check("held-bar held", "S901_bbbbbbbb_held-bar.md" in held)
        check("held count 1", len(r["held"]) == 1)
        check("noresume includes missing", "S902_cccccccc_noresume-baz.md" in r["no_resume"])
        check("noresume includes legacy-no-open_dep",
              "S903_dddddddd_legacy-qux.md" in r["no_resume"])
        check("noresume count 2", len(r["no_resume"]) == 2)
        check("not over cap at 5 quests", not r["over_cap"])


# ---- soft cap fires past the threshold ----
def test_soft_cap():
    print("test_soft_cap")
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        # 16 graduatable real quests > INPROGRESS_SOFT_CAP (15)
        in_progress, resumes = {}, {}
        for i in range(16):
            sid = f"{i:08d}"
            stem = f"S{500+i}_{sid}_q{i}"
            in_progress[stem] = None
            resumes[f"q{i}-resume__{sid}"] = _resume(f"S{500+i}_q{i}", sid, "none")
        _mk(root, "capper", in_progress, resumes)
        r = qg.audit(root, only_player="capper")[0]
        check("16 quests over soft cap", r["over_cap"])
        check("all 16 graduatable", len(r["graduatable"]) == 16)


# ---- resume matched by sid8 even when SNNN collides (D-024 parallel) ----
def test_sid8_disambiguation():
    print("test_sid8_disambiguation")
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        in_progress = {
            "S250_44773956_recon-a": None,   # -> none
            "S250_bd2469b9_routing-b": None,  # -> named dep
        }
        resumes = {
            "recon-a-resume__44773956": _resume("S250_recon-a", "44773956", "none"),
            "routing-b-resume__bd2469b9": _resume("S250_routing-b", "bd2469b9",
                                                  "awaiting decision"),
        }
        _mk(root, "twin", in_progress, resumes)
        r = qg.audit(root, only_player="twin")[0]
        grad = {fn for fn, _ in r["graduatable"]}
        held = {fn for fn, _ in r["held"]}
        check("same-SNNN: only 44773956 graduatable",
              grad == {"S250_44773956_recon-a.md"})
        check("same-SNNN: bd2469b9 held", "S250_bd2469b9_routing-b.md" in held)


def main():
    test_is_trace()
    test_open_dep()
    test_quest_keys()
    test_classification()
    test_soft_cap()
    test_sid8_disambiguation()
    print(f"\n{_passed} passed, {_failed} failed")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())

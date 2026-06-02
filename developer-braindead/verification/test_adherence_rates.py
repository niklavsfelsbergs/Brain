#!/usr/bin/env python3
"""test_adherence_rates.py — boundary harness for adherence-rates.py (plan §X.7).

Drives compute() / write_snapshot() / trend() on SYNTHETIC event streams and
asserts the rate math. This analyzer is read-only (not a hook), so there is no
write-boundary to fence — the "boundary" here is the rate computation's edges:
first-event compliance, division-by-zero guards, window filtering, malformed-line
tolerance, the honest non-gate-grounded tier, and the snapshot round-trip.

Run:  python developer-braindead/verification/test_adherence_rates.py
Exit 0 = all pass; 1 = a failure (prints the first).
"""

import importlib.util
import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("adherence_rates",
                                               HERE / "adherence-rates.py")
ar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ar)

_FAILS: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}  {detail}")
        _FAILS.append(name)


def ev(hook, decision, sid8="s1", actor="", ts=None):
    return {"ts": ts if ts is not None else time.time(), "hook": hook,
            "decision": decision, "actor": actor, "sid8": sid8, "path_class": ""}


# ── Tier 1: OPEN-on-entry compliance ────────────────────────────────────────
def test_open_first_allow_is_compliant():
    # session posted OPEN before writing -> first require-open is allow
    m = ar.compute([ev("require-open", "allow", "aaa", "braindead"),
                    ev("require-open", "allow", "aaa", "braindead")])
    check("first-allow => compliant", m["open_compliance_rate"] == 1.0,
          str(m["open_compliance_rate"]))
    check("first-allow => 0 catches", m["open_catches"] == 0)


def test_open_first_block_is_caught():
    # wrote before OPEN (block), then posted + recovered (allow)
    m = ar.compute([ev("require-open", "block", "bbb", "jebrim"),
                    ev("require-open", "allow", "bbb", "jebrim")])
    check("first-block => non-compliant", m["open_compliance_rate"] == 0.0,
          str(m["open_compliance_rate"]))
    check("first-block counts a catch", m["open_catches"] == 1)
    check("recovered (block then allow) => not never_recovered",
          m["open_never_recovered"] == 0)


def test_open_never_recovered():
    m = ar.compute([ev("require-open", "block", "ccc", "jebrim"),
                    ev("require-open", "block", "ccc", "jebrim")])
    check("block-only session => never_recovered", m["open_never_recovered"] == 1)
    check("two blocks => 2 catches", m["open_catches"] == 2)


def test_open_mixed_rate():
    # 3 compliant sessions, 1 caught -> 75%
    evs = []
    for sid in ("p1", "p2", "p3"):
        evs.append(ev("require-open", "allow", sid, "braindead"))
    evs.append(ev("require-open", "block", "p4", "braindead"))
    m = ar.compute(evs)
    check("3 allow + 1 block => 75%", abs(m["open_compliance_rate"] - 0.75) < 1e-9,
          str(m["open_compliance_rate"]))
    check("open_total_sessions == 4", m["open_total_sessions"] == 4)


def test_open_skip_noactor_excluded():
    # an unresolved-actor session is NOT scored as pass or fail
    m = ar.compute([ev("require-open", "skip-noactor", "ddd", ""),
                    ev("require-open", "allow", "eee", "braindead")])
    check("skip-noactor not in pass/fail denom", m["open_total_sessions"] == 1)
    check("skip-noactor counted separately", m["open_noactor_sessions"] == 1)
    check("rate from the one real session", m["open_compliance_rate"] == 1.0)


def test_open_zero_guard():
    m = ar.compute([ev("grounding-cue", "nudge", "x", "")])
    check("no require-open => rate None (no div0)",
          m["open_compliance_rate"] is None)
    check("no require-open => open_total 0", m["open_total_sessions"] == 0)


# ── Tier 1: catch-counts ────────────────────────────────────────────────────
def test_floor_and_boundary_counts():
    evs = [
        ev("block-deletes", "block", "s", "jebrim"),
        ev("block-deletes", "bypass-braindead", "s", ""),   # authorized, not counted
        ev("block-confirmed", "block", "s", "zezima"),
        ev("git-index-guard", "block", "s", ""),
        ev("gnome-boundary", "block", "s", ""),
        ev("penguin-boundary", "block", "s", ""),
    ]
    m = ar.compute(evs)
    check("floor catches = 3 (2 block-* + git-index, bypass excluded)",
          m["floor_catches_total"] == 3, str(m["floor_catches"]))
    check("bypass-braindead not a floor catch",
          "bypass-braindead" not in str(m["floor_catches"]))
    check("boundary catches = 2", m["boundary_catches_total"] == 2,
          str(m["boundary_catches"]))


def test_draft_gate_redirect_vs_bypass():
    evs = [ev("draft-gate", "redirect", "s", ""),
           ev("draft-gate", "redirect", "s", ""),
           ev("draft-gate", "bypass-ritual", "s", ""),
           ev("draft-gate", "bypass-braindead", "s", "")]
    m = ar.compute(evs)
    check("draft redirects = 2", m["draft_redirects"] == 2)
    check("draft bypasses = 2", m["draft_bypasses"] == 2)


# ── Tier 2: forced-read coverage ────────────────────────────────────────────
def test_forced_read_player_coverage():
    # two player sessions; one got the inject, one did not
    evs = [
        ev("require-open", "allow", "j1", "jebrim"),
        ev("forced-read", "player-inject", "j1", ""),
        ev("require-open", "allow", "j2", "jebrim"),   # no inject this session
        ev("forced-read", "session-start", "j1", ""),
        # a braindead session is NOT a player session -> excluded from denom
        ev("require-open", "allow", "b1", "braindead"),
        ev("forced-read", "session-start", "b1", ""),
    ]
    m = ar.compute(evs)
    check("player sessions seen = 2 (braindead excluded)",
          m["player_sessions_seen"] == 2, str(m["player_sessions_seen"]))
    check("player-inject coverage = 50%",
          m["player_inject_coverage_rate"] == 0.5,
          str(m["player_inject_coverage_rate"]))
    check("session-start injects counted across sessions",
          m["forced_read_session_start"] == 2)


def test_forced_read_zero_guard():
    m = ar.compute([ev("require-open", "allow", "b", "braindead")])
    check("no player sessions => coverage None",
          m["player_inject_coverage_rate"] is None)


# ── Tier 3: advisory cue fires + proxy (honest, NOT obedience) ──────────────
def test_cue_fires_and_proxy():
    evs = [
        ev("domain-cue:shipping", "nudge", "c1", ""),
        ev("domain-cue:deploy-schema", "nudge", "c1", ""),
        ev("grounding-cue", "nudge", "c2", ""),
        ev("forced-read", "player-inject", "c1", ""),   # c1 also got an inject
    ]
    m = ar.compute(evs)
    check("cue fires total = 3", m["cue_fires_total"] == 3, str(m["cue_fires"]))
    check("cue sessions = 2", m["cue_sessions"] == 2)
    check("proxy = 50% (c1 had an inject, c2 did not)",
          m["cue_load_proxy_rate"] == 0.5, str(m["cue_load_proxy_rate"]))


def test_cue_prefix_match_future_domains():
    # a brand-new domain-cue:<x> row needs no code change to be tallied
    m = ar.compute([ev("domain-cue:brand-new-domain", "nudge", "z", "")])
    check("unknown domain-cue:* still counted", m["cue_fires_total"] == 1)


# ── windowing + malformed tolerance + snapshot round-trip ───────────────────
def test_window_filter():
    now = time.time()
    evs = [ev("require-open", "allow", "old", "braindead", ts=now - 10 * 86400),
           ev("require-open", "block", "new", "braindead", ts=now - 1 * 3600)]
    tmp = Path(tempfile.mkdtemp()) / "events.ndjson"
    tmp.write_text("\n".join(json.dumps(e) for e in evs) + "\n", encoding="utf-8")
    loaded = ar._load(tmp, days=2)
    check("window drops the 10-day-old event", len(loaded) == 1,
          f"loaded {len(loaded)}")
    m = ar.compute(loaded)
    check("windowed compute sees only the recent block",
          m["open_compliance_rate"] == 0.0)


def test_malformed_lines_skipped():
    tmp = Path(tempfile.mkdtemp()) / "events.ndjson"
    good = json.dumps(ev("require-open", "allow", "s", "braindead"))
    tmp.write_text(good + "\n{ this is not json\n\n" + good + "\n", encoding="utf-8")
    loaded = ar._load(tmp, days=None)
    check("malformed line skipped, 2 good kept", len(loaded) == 2,
          f"loaded {len(loaded)}")


def test_snapshot_round_trip():
    m = ar.compute([ev("require-open", "allow", "s1", "braindead"),
                    ev("require-open", "block", "s2", "braindead")])
    tmp = Path(tempfile.mkdtemp()) / "snaps.ndjson"
    ar.write_snapshot(m, 7, tmp)
    ar.write_snapshot(m, None, tmp)
    rows = [json.loads(l) for l in tmp.read_text(encoding="utf-8").splitlines() if l.strip()]
    check("two snapshots appended", len(rows) == 2)
    check("snapshot carries the flagship rate",
          rows[0]["open_compliance_rate"] == 0.5, str(rows[0]))
    check("snapshot carries window_days", rows[0]["window_days"] == 7)
    lines = ar.trend(tmp)
    check("trend renders both rows", sum(1 for l in lines if "50%" in l) == 2,
          "\n".join(lines))


def test_empty_stream():
    m = ar.compute([])
    check("empty stream => 0 sessions, no crash", m["sessions_total"] == 0)
    check("empty stream => all rates None",
          m["open_compliance_rate"] is None
          and m["player_inject_coverage_rate"] is None
          and m["cue_load_proxy_rate"] is None)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"=== test_adherence_rates.py — {len(tests)} test groups ===")
    for t in tests:
        t()
    print()
    if _FAILS:
        print(f"FAILED: {len(_FAILS)} check(s): {', '.join(_FAILS)}")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

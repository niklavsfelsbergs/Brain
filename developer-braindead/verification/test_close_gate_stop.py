#!/usr/bin/env python3
"""test_close_gate_stop.py -- boundary harness for close-gate-stop.py (plan §X.2,
the Stop-event close-ritual gate).

What it pins down (the design seam Niklavs flagged + the chosen severity):
  * THE SEAM -- the gate engages ONLY on a `wrapped_up` close-claim. Every
    ordinary turn-end (no marker / mid-wrap 'closing' / a flavor tag) passes
    straight through, so in-flight work can NEVER be false-blocked. This is the
    load-bearing assertion: most Stops must be invisible to the gate.
  * SEVERITY -- a wrapped_up-claim with a close_check FAIL BLOCKs (exit 2, gaps
    on stderr); the SAME state with stop_hook_active set DEGRADEs to warn (exit
    0) so it can't trap a session in an infinite continue-loop.
  * RITUAL SELECTION -- the layered dev-vs-player discriminator (braindead intent
    anchor / dev comms / active-mode, else player).
  * MARKER SCATTER -- `<sid8>.mode` is found in EITHER intent dir; freshest wins.
  * FAIL-OPEN -- unparseable payload / wrong event / empty sid / missing
    close_check all allow (exit 0), and never run close_check.

The gate's decision logic is tested in isolation by monkeypatching the three
helpers (marker read / ritual detect / close_check run) so the harness exercises
THIS hook, not close_check (already covered 24/24 by test_close_check.py). Three
tests use the REAL helpers against synthetic dirs / the live repo to prove the
plumbing -- including an end-to-end _run_close_check subprocess against the real
closed dev session (PASS) and a known-FAIL player session.

Run:  python developer-braindead/verification/test_close_gate_stop.py
Exit 0 = all pass; 1 = a failure (prints each).
"""

import importlib.util
import io
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRAIN_ROOT = HERE.parents[1]

# S187: route synthetic test events to a temp file, never the LIVE analytics
# stream (switchboard/ritual_log.py honors RITUAL_EVENTS_PATH per call;
# subprocesses inherit it). Pre-S187 these suites polluted the real log.
import os as _os
import tempfile as _tempfile
_os.environ["RITUAL_EVENTS_PATH"] = str(
    Path(_tempfile.gettempdir()) / "ritual-events-test.ndjson")
HOOK = BRAIN_ROOT / "gielinor" / ".claude" / "hooks" / "close-gate-stop.py"
_spec = importlib.util.spec_from_file_location("close_gate_stop", HOOK)
g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g)

# Originals captured at load so run_main can restore them — else a monkeypatched
# helper leaks into the REAL-helper tests that run after it.
_ORIG = (g._read_mode_marker, g._detect_ritual, g._run_close_check)

_FAILS: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}  {detail}")
        _FAILS.append(name)


def run_main(payload, *, marker=None, ritual="dev", cc_result=(0, ""),
             stdin_raw=None):
    """Drive main() with crafted payload + monkeypatched helpers.
    Returns (exit_code, stderr_text). marker=None -> '' (no marker)."""
    calls = {"close_check": 0}

    g._read_mode_marker = lambda sid8: (marker or "")
    g._detect_ritual = lambda sid8: ritual

    def _fake_cc(sid8, rit):
        calls["close_check"] += 1
        return cc_result
    g._run_close_check = _fake_cc

    raw = stdin_raw if stdin_raw is not None else json.dumps(payload)
    old_in, old_err = sys.stdin, sys.stderr
    # Isolate from the ambient session env so the empty-sid path is actually empty
    # (main() falls back to CLAUDE_CODE_SESSION_ID, which is set when run inside a
    # live session).
    old_env = os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
    sys.stdin = io.StringIO(raw)
    sys.stderr = io.StringIO()
    try:
        code = g.main()
        err = sys.stderr.getvalue()
    finally:
        sys.stdin, sys.stderr = old_in, old_err
        if old_env is not None:
            os.environ["CLAUDE_CODE_SESSION_ID"] = old_env
        # Restore the real helpers so the REAL-helper tests aren't poisoned.
        g._read_mode_marker, g._detect_ritual, g._run_close_check = _ORIG
    return code, err, calls["close_check"]


STOP = {"hook_event_name": "Stop", "session_id": "abcd1234ef", "stop_hook_active": False}


def _stop(**over):
    p = dict(STOP)
    p.update(over)
    return p


# ===================== THE SEAM: only wrapped_up engages =====================

def test_no_marker_allows_silently():
    code, err, n = run_main(_stop(), marker=None, cc_result=(1, "GAP"))
    check("no marker -> allow, close_check NOT run (mid-work pause)",
          code == 0 and n == 0 and err == "", f"code={code} n={n} err={err!r}")


def test_closing_marker_allows():
    # mid-wrap (may be a legit pause-for-nod) must pass through, even if a
    # close_check would fail right now.
    code, err, n = run_main(_stop(), marker="closing", cc_result=(1, "GAP"))
    check("marker 'closing' -> allow, close_check NOT run",
          code == 0 and n == 0, f"code={code} n={n}")


def test_flavor_marker_allows():
    for fl in ("alching", "bankstanding", "consultation", "drafts"):
        code, err, n = run_main(_stop(), marker=fl, cc_result=(1, "GAP"))
        check(f"flavor marker '{fl}' -> allow, close_check NOT run",
              code == 0 and n == 0, f"code={code} n={n}")


# ===================== severity: block / pass / degrade =====================

def test_wrapped_up_pass_allows():
    code, err, n = run_main(_stop(), marker="wrapped_up", ritual="dev", cc_result=(0, "all good"))
    check("wrapped_up + close_check PASS -> allow (exit 0), close_check WAS run",
          code == 0 and n == 1, f"code={code} n={n}")


def test_wrapped_up_fail_blocks():
    code, err, n = run_main(_stop(stop_hook_active=False), marker="wrapped_up",
                            ritual="player", cc_result=(1, "[FAIL] core artifacts committed"))
    check("wrapped_up + FAIL + not-active -> BLOCK (exit 2)",
          code == 2 and n == 1, f"code={code} n={n}")
    check("block stderr carries BLOCKED + the gaps + ritual",
          "BLOCKED" in err and "core artifacts committed" in err and "player" in err,
          f"err={err!r}")


def test_wrapped_up_fail_active_degrades():
    code, err, n = run_main(_stop(stop_hook_active=True), marker="wrapped_up",
                            ritual="dev", cc_result=(1, "[FAIL] respawn updated"))
    check("wrapped_up + FAIL + stop_hook_active -> DEGRADE (exit 0, loop-guard)",
          code == 0 and n == 1, f"code={code} n={n}")
    check("degrade stderr warns + carries the gaps (not silent)",
          "warn" in err.lower() and "respawn updated" in err, f"err={err!r}")


def test_wrapped_up_pass_active_still_allows():
    # the loop-guard only matters on FAIL; a PASS allows regardless.
    code, err, n = run_main(_stop(stop_hook_active=True), marker="wrapped_up", cc_result=(0, ""))
    check("wrapped_up + PASS + stop_hook_active -> allow", code == 0, f"code={code}")


# ===================== fail-open posture =====================

def test_unparseable_payload_allows():
    code, err, n = run_main(None, stdin_raw="{not json", marker="wrapped_up", cc_result=(1, "X"))
    check("unparseable stdin -> allow (exit 0), nothing run",
          code == 0 and n == 0, f"code={code} n={n}")


def test_wrong_event_allows():
    code, err, n = run_main(_stop(hook_event_name="PreToolUse"), marker="wrapped_up", cc_result=(1, "X"))
    check("non-Stop event -> allow, close_check NOT run", code == 0 and n == 0, f"code={code} n={n}")


def test_missing_event_name_treated_as_stop():
    p = {"session_id": "abcd1234ef", "stop_hook_active": False}  # no hook_event_name
    code, err, n = run_main(p, marker="wrapped_up", ritual="dev", cc_result=(0, ""))
    check("absent hook_event_name treated as Stop (close_check run)", n == 1, f"n={n}")


def test_empty_sid_allows():
    code, err, n = run_main(_stop(session_id=""), marker="wrapped_up", cc_result=(1, "X"))
    check("empty session_id -> allow, nothing run", code == 0 and n == 0, f"code={code} n={n}")


# ===================== REAL helpers (plumbing proof) =====================

def test_real_mode_marker_scatter():
    """_read_mode_marker finds the marker in EITHER dir; freshest wins."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        root_intent = tmp / "root" / ".claude" / "intent"
        giel_intent = tmp / "gielinor" / ".claude" / "intent"
        root_intent.mkdir(parents=True)
        giel_intent.mkdir(parents=True)
        old = g.INTENT_DIRS
        try:
            g.INTENT_DIRS = (root_intent, giel_intent)
            # only in gielinor dir
            (giel_intent / "11112222.mode").write_text("wrapped_up", encoding="utf-8")
            check("marker found in gielinor intent dir",
                  g._read_mode_marker("11112222") == "wrapped_up")
            # only in root dir
            (root_intent / "33334444.mode").write_text("closing", encoding="utf-8")
            check("marker found in root intent dir",
                  g._read_mode_marker("33334444") == "closing")
            # no marker
            check("no marker -> ''", g._read_mode_marker("deadbeef") == "")
            # both dirs: freshest (gielinor, written second) wins
            (root_intent / "55556666.mode").write_text("closing", encoding="utf-8")
            time.sleep(0.02)
            (giel_intent / "55556666.mode").write_text("wrapped_up", encoding="utf-8")
            check("both dirs -> freshest wins",
                  g._read_mode_marker("55556666") == "wrapped_up",
                  f"got {g._read_mode_marker('55556666')!r}")
        finally:
            g.INTENT_DIRS = old


def test_real_detect_ritual():
    """The per-session discriminator: dev signals win, else player. Crucially,
    the GLOBAL active-mode.txt must NOT bleed into classification (parallel-
    session safety)."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        intent = tmp / ".claude" / "intent"
        intent.mkdir(parents=True)
        comms = tmp / "developer-braindead" / "comms" / "active.md"
        comms.parent.mkdir(parents=True)
        comms.write_text("[ts] braindead-aaaa1111 OPEN\n", encoding="utf-8")
        old = (g.INTENT_DIRS, g.DEV_COMMS)
        try:
            g.INTENT_DIRS = (intent, tmp / "gielinor" / ".claude" / "intent")
            g.DEV_COMMS = comms
            # 1. live braindead intent anchor
            (intent / "braindead-bbbb2222.txt").write_text("x", encoding="utf-8")
            check("dev via braindead intent anchor", g._detect_ritual("bbbb2222") == "dev")
            # 2. dev comms mention
            check("dev via dev-comms braindead-<sid8>", g._detect_ritual("aaaa1111") == "dev")
            # else -> player (no per-session dev signal)
            check("unknown sid -> player", g._detect_ritual("cccc3333") == "player")
            # PARALLEL-SESSION SAFETY: a real live dev-brain active-mode must NOT
            # reclassify an unknown/player sid -> still player.
            real_am = (BRAIN_ROOT / ".claude" / "active-mode.txt").read_text(
                encoding="utf-8", errors="replace").strip() if (
                BRAIN_ROOT / ".claude" / "active-mode.txt").exists() else ""
            check("global active-mode does NOT bleed into classification "
                  f"(live active-mode={real_am!r}) -> player",
                  g._detect_ritual("cccc3333") == "player")
        finally:
            g.INTENT_DIRS, g.DEV_COMMS = old


def test_real_close_check_subprocess():
    """End-to-end through the REAL close_check subprocess against the live repo:
    proves _run_close_check actually shells out, runs the right ritual, and
    propagates the exit code + output.

    Both directions assert only that the subprocess RAN the right ritual (its
    check names appear in the output) and propagated an int exit code -- NOT a
    specific exit value. The PASS->exit-0 and FAIL->exit-2 severity wiring is
    proven deterministically by test_wrapped_up_pass_allows /
    test_wrapped_up_fail_blocks above (monkeypatched). Pinning a live session's
    pass/fail here made the suite FLAKY: the old assertion required player
    b82b0b90 to exit 1 because a shared-lineage quest file was uncommitted in
    this parallel tree -- true only until that file was committed, after which
    b82b0b90 PASSes and the hard-coded exit==1 false-failed (2026-06-18 audit).
    This test's job is the shell-out plumbing, not the exit value."""
    code_dev, out_dev = g._run_close_check("0526dd9d", "dev")
    check("real close_check dev subprocess RAN the dev ritual (check names present)",
          "CLOSING posted" in out_dev and "active-mode" in out_dev and isinstance(code_dev, int),
          f"code={code_dev} out={out_dev[:120]!r}")
    code_player, out_player = g._run_close_check("b82b0b90", "player")
    check("real close_check player subprocess RAN + propagated an int exit code",
          isinstance(code_player, int) and "CLOSING posted" in out_player,
          f"code={code_player} out={out_player[:120]!r}")


def main() -> int:
    print("close-gate-stop.py boundary harness\n")
    for fn in sorted(
        (v for k, v in globals().items() if k.startswith("test_") and callable(v)),
        key=lambda f: f.__code__.co_firstlineno,
    ):
        fn()
    total = sum(1 for k in globals() if k.startswith("test_"))
    print(f"\n{'ALL PASS' if not _FAILS else 'FAILURES: ' + ', '.join(_FAILS)} "
          f"({total} test fns)")
    return 1 if _FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

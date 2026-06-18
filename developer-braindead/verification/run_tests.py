#!/usr/bin/env python3
"""run_tests.py -- one runner for every test_*.py boundary harness in this dir.

WHY THIS EXISTS (2026-06-18 audit). The verification suites are standalone
scripts (each `sys.exit(0/1)` at module level -- pytest can't collect them), and
nothing ran them as a batch. So a suite could ROT silently: test_git_index_guard.py
pointed its HOOK constant at a non-existent path for weeks, and because Python
exits 2 on a missing file -- the same code the harness reads as BLOCK -- its
BLOCK cases passed by accident while every ALLOW case failed, unnoticed because
no runner ever executed it. This runner closes that gap: it discovers every
test_*.py, runs each as its own subprocess, and reports a pass/fail tally. A dead
or broken suite now surfaces the moment this runs.

Each harness is the source of truth for its own assertions; this only aggregates
exit codes (0 = pass, non-zero = fail) and surfaces the failing tail.

Run:  python developer-braindead/verification/run_tests.py
      python developer-braindead/verification/run_tests.py -v   # show each suite's tail
Exit 0 if every suite passes; 1 if any fail (the names print).

NOTE: some suites (test_close_check, test_close_gate_stop) shell out to the REAL
close_check against the live tree -- they assert plumbing, not mutable tree
state, so they are stable to run here. If a suite starts depending on live
working-tree state, decouple it (see the 2026-06-18 close-gate fix) rather than
excluding it here -- a silent exclusion is the same blind spot this runner exists
to kill.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    suites = sorted(HERE.glob("test_*.py"))
    if not suites:
        print("run_tests: no test_*.py suites found", file=sys.stderr)
        return 1

    passed: list[str] = []
    failed: list[tuple[str, int, str]] = []

    print(f"run_tests: {len(suites)} suite(s) under {HERE.name}/\n")
    for suite in suites:
        p = subprocess.run(
            [sys.executable, str(suite)],
            capture_output=True, text=True, cwd=str(HERE),
        )
        out = (p.stdout or "") + (p.stderr or "")
        tail = next((ln for ln in reversed(out.splitlines()) if ln.strip()), "")
        if p.returncode == 0:
            passed.append(suite.name)
            print(f"  PASS  {suite.name:<38} {tail[:60]}")
        else:
            failed.append((suite.name, p.returncode, tail))
            print(f"  FAIL  {suite.name:<38} exit={p.returncode}  {tail[:60]}")
        if verbose:
            for ln in out.splitlines()[-12:]:
                print(f"        | {ln}")

    print(f"\n{'-' * 60}")
    print(f"SUITES: {len(passed)} passed, {len(failed)} failed "
          f"(of {len(suites)})")
    if failed:
        print("FAILED: " + ", ".join(name for name, _, _ in failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

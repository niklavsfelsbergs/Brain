#!/usr/bin/env python
"""test_block_confirmed_unlock.py — the D-036 Guthix floor-unlock path in
block-confirmed-writes.py (2026-06-19, sid d371d189).

The unlock's job: let GUTHIX write confirmed/ paths, but ONLY when all three
independent gates hold — actor==guthix AND mode in {bankstanding, alching} AND
a non-empty `<sid8>.floor-unlock` marker (the principal's explicit, session-
scoped grant). Drop any one gate and the floor holds exactly as before. The
braindead bypass is unchanged; deletes are NOT covered by this hook at all.

Drives the real hook via stdin (the PreToolUse entry point); exit 2 = BLOCK,
exit 0 = ALLOW. Sets up real sidecar markers in gielinor/.claude/intent for a
throwaway sid8 (the dir the hook actually reads), torn down in a finally.
"""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / "gielinor" / ".claude" / "hooks" / "block-confirmed-writes.py"
BRAIN = Path(__file__).resolve().parents[2]
INTENT = BRAIN / "gielinor" / ".claude" / "intent"
CONFIRMED_PATH = str(BRAIN / "gielinor" / "players" / "jebrim" / "examine" / "confirmed" / "_unlock_probe.md")
DRAFT_PATH = str(BRAIN / "gielinor" / "players" / "jebrim" / "examine" / "drafts" / "_unlock_probe.md")

SID = "ts777701"  # no real session uses this


def setup(actor=None, mode=None, unlock=False):
    teardown()
    if actor:
        (INTENT / f"{actor}-{SID}.txt").write_text("probe intent\n", encoding="utf-8")
    if mode:
        (INTENT / f"{SID}.mode").write_text(mode + "\n", encoding="utf-8")
    if unlock:
        (INTENT / f"{SID}.floor-unlock").write_text("granted (test)\n", encoding="utf-8")


def teardown():
    for name in (f"guthix-{SID}.txt", f"jebrim-{SID}.txt", f"braindead-{SID}.txt",
                 f"{SID}.mode", f"{SID}.floor-unlock"):
        try:
            (INTENT / name).unlink()
        except OSError:
            pass


def run(file_path=CONFIRMED_PATH):
    payload = {"tool_name": "Write", "tool_input": {"file_path": file_path}, "session_id": SID}
    p = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                       capture_output=True, text=True)
    return p.returncode


# (name, expected_exit, setup_kwargs, run_kwargs)
CASES = [
    ("braindead actor                       -> ALLOW", 0, dict(actor="braindead"), {}),
    ("guthix + bankstanding + marker        -> ALLOW", 0, dict(actor="guthix", mode="bankstanding", unlock=True), {}),
    ("guthix + alching + marker             -> ALLOW", 0, dict(actor="guthix", mode="alching", unlock=True), {}),
    ("guthix + bankstanding + NO marker     -> BLOCK", 2, dict(actor="guthix", mode="bankstanding", unlock=False), {}),
    ("guthix + consultation + marker        -> BLOCK", 2, dict(actor="guthix", mode="consultation", unlock=True), {}),
    ("guthix + NO mode + marker             -> BLOCK", 2, dict(actor="guthix", mode=None, unlock=True), {}),
    ("player + bankstanding + marker        -> BLOCK", 2, dict(actor="jebrim", mode="bankstanding", unlock=True), {}),
    ("unresolved actor + marker            -> BLOCK", 2, dict(actor=None, mode="bankstanding", unlock=True), {}),
    ("guthix+bankstanding+marker, DRAFT path-> ALLOW", 0, dict(actor="guthix", mode="bankstanding", unlock=True), dict(file_path=DRAFT_PATH)),
]


def main():
    fails = 0
    try:
        for name, expected, skw, rkw in CASES:
            setup(**skw)
            got = run(**rkw)
            ok = got == expected
            print(f"  [{'PASS' if ok else 'FAIL'}] {name}  (exit {got}, want {expected})")
            if not ok:
                fails += 1
    finally:
        teardown()
    total = len(CASES)
    print(f"\n{total - fails}/{total} passed")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

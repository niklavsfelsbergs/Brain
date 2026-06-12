#!/usr/bin/env python
"""test_block_deletes_scope.py — the scope guard added to block-deletes.py
(2026-06-12, sid a7ea5300).

The guard's job: keep BLOCKING deletes that target brain paths, while ALLOWING
deletes whose effective directory is a real repo outside the brain (the bug —
a `git rm` in bi-analytics tripped the brain guard because the patterns match
the command string regardless of where the delete lands).

Drives the real hook via stdin (the actual PreToolUse entry point); exit 2 =
BLOCK, exit 0 = ALLOW. Uses a session_id with no intent/status anchor so the
actor resolves '' (non-braindead) — i.e. the guard, not the braindead bypass,
is what's under test.
"""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / "gielinor" / ".claude" / "hooks" / "block-deletes.py"
BRAIN = Path(__file__).resolve().parents[2]
WORK = "/c/Users/niklavs.felsbergs/Documents/GitHub/bi-analytics-main"
WORK_WIN = r"C:\Users\niklavs.felsbergs\Documents\GitHub\bi-etl"
BRAIN_ABS = str(BRAIN).replace("\\", "/")

# no intent/status file exists for this sid8 -> actor resolves '' (not braindead)
NOACTOR = "zz999999"


def run(command, tool="Bash", cwd=None, sid=NOACTOR):
    payload = {"tool_name": tool, "tool_input": {"command": command}, "session_id": sid}
    if cwd is not None:
        payload["cwd"] = cwd
    p = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                       capture_output=True, text=True)
    return p.returncode


CASES = [
    # (name, expected_exit, kwargs)
    ("work-repo git rm (cd bash)        -> ALLOW", 0,
     dict(command=f"cd {WORK} && git rm 2_analysis/_probe.py")),
    ("work-repo rm -rf (cd bash)        -> ALLOW", 0,
     dict(command=f"cd {WORK} && rm -rf 2_analysis/scratch/")),
    ("work-repo Set-Location (pwsh)     -> ALLOW", 0,
     dict(tool="PowerShell", command=f"Set-Location {WORK_WIN}; git rm foo.py")),
    ("work-repo delete, cwd outside     -> ALLOW", 0,
     dict(command="git rm foo.py", cwd=WORK_WIN)),
    ("brain relative rm, no cd          -> BLOCK", 2,
     dict(command="rm gielinor/examine/confirmed/x.md", cwd=BRAIN_ABS)),
    ("brain absolute rm from /tmp       -> BLOCK", 2,
     dict(command=f"cd /tmp && rm {BRAIN_ABS}/gielinor/examine/x.md")),
    ("brain absolute rm (git-bash /c/)  -> BLOCK", 2,
     dict(command="cd /tmp && rm /c/Users/niklavs.felsbergs/Documents/GitHub/brain/keepsake/x.md")),
    ("brain Remove-Item, cwd brain      -> BLOCK", 2,
     dict(tool="PowerShell", command="Remove-Item gielinor/meta/foo.md", cwd=str(BRAIN))),
    ("no delete verb at all             -> ALLOW", 0,
     dict(command=f"cd {WORK} && git status")),
]


def main():
    fails = 0
    for name, expected, kw in CASES:
        got = run(**kw)
        ok = got == expected
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}  (exit {got}, want {expected})")
        if not ok:
            fails += 1
    total = len(CASES)
    print(f"\n{total - fails}/{total} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

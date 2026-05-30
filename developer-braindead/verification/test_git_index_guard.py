#!/usr/bin/env python3
"""Synthetic harness for git-index-guard.py — pipes JSON payloads to the hook's
process and checks exit codes + stderr. Mirrors how the other boundary hooks are
tested at the PreToolUse boundary. Throwaway; not wired into anything."""
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "git-index-guard.py")
BLOCK, ALLOW = 2, 0


def run(command, tool="Bash", env_extra=None):
    payload = {"tool_name": tool, "tool_input": {"command": command}}
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    p = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps(payload),
        capture_output=True, text=True, env=env,
    )
    return p.returncode, p.stderr


CASES = [
    # (label, command, tool, env, expected_exit)
    ("1  git add -A",                      "git add -A",                       "Bash",       None,                  BLOCK),
    ("2  git add .",                       "git add .",                        "Bash",       None,                  BLOCK),
    ("3  git commit -am msg",              'git commit -am "msg"',             "Bash",       None,                  BLOCK),
    ("4  git commit -a",                   "git commit -a",                    "Bash",       None,                  BLOCK),
    ("5  git add explicit path",           "git add gielinor/players/jebrim/foo.md", "Bash", None,                  ALLOW),
    ("6  git commit -m no -a",             'git commit -m "fix"',              "Bash",       None,                  ALLOW),
    ("7  git commit -- pathspec",          "git commit -- gielinor/foo.md",    "Bash",       None,                  ALLOW),
    ("8a git status",                      "git status",                       "Bash",       None,                  ALLOW),
    ("8b ls (non-git)",                    "ls",                               "Bash",       None,                  ALLOW),
    ("9  commit -m mentions 'git add -A'", 'git commit -m "mentions git add -A in text"', "Bash", None,             ALLOW),
    ("10 git add -A + GIT_BARE_OK=1",      "git add -A",                       "Bash",       {"GIT_BARE_OK": "1"},  ALLOW),
    # --- extra robustness cases (not in the required 10 but worth proving) ---
    ("E1 chained cd && git add -A",        "cd gielinor && git add -A",        "Bash",       None,                  BLOCK),
    ("E2 git add --all",                   "git add --all",                    "Bash",       None,                  BLOCK),
    ("E3 git add -- .",                    "git add -- .",                     "Bash",       None,                  BLOCK),
    ("E4 git add -A . (combined)",         "git add -A .",                     "Bash",       None,                  BLOCK),
    ("E5 git commit -a -m msg (split)",    'git commit -a -m "msg"',           "Bash",       None,                  BLOCK),
    ("E6 PowerShell git add -A",           "git add -A",                       "PowerShell", None,                  BLOCK),
    ("E7 git add ./gielinor/x.md (path)",  "git add ./gielinor/x.md",          "Bash",       None,                  ALLOW),
    ("E8 echo then commit -m",             'echo hi && git commit -m "git add -A"', "Bash",  None,                  ALLOW),
    ("E9 malformed payload (no cmd)",      "",                                 "Bash",       None,                  ALLOW),
]


def main():
    fails = 0
    for label, cmd, tool, env_extra, expected in CASES:
        code, stderr = run(cmd, tool, env_extra)
        ok = code == expected
        verdict = "PASS" if ok else "FAIL"
        if not ok:
            fails += 1
        exp_s = {BLOCK: "BLOCK", ALLOW: "ALLOW"}[expected]
        got_s = {2: "BLOCK", 0: "ALLOW"}.get(code, f"exit {code}")
        line = f"[{verdict}] {label:38s} expect={exp_s:5s} got={got_s}"
        if expected == BLOCK and ok:
            line += "  (+stderr banner)" if stderr.strip() else "  (!! NO STDERR)"
        print(line)
    print()
    print("ALL PASS" if fails == 0 else f"{fails} FAILURE(S)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

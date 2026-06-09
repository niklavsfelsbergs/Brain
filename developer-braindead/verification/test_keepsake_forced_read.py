#!/usr/bin/env python3
"""Boundary harness for gielinor/.claude/hooks/keepsake-forced-read.py (plan §X.4).

Verifies the two arms at the hook boundary on synthetic payloads — no live session
needed (the same discipline as the domain-cue / require-open harnesses). Asserts the
exit-0-always contract and that the RIGHT content is forced into context.

Run: python developer-braindead/verification/test_keepsake_forced_read.py
"""
import importlib.util
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

BRAIN = Path(__file__).resolve().parents[2]
HOOK = BRAIN / "gielinor" / ".claude" / "hooks" / "keepsake-forced-read.py"

spec = importlib.util.spec_from_file_location("kfr", HOOK)
kfr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kfr)

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")


def run(payload, actor=None, sentinel_exists=False, tmp=None):
    """Drive main() with a payload via stdin; control actor + a temp STATUS_DIR.
    Returns (exit_code, stdout_str)."""
    kfr.STATUS_DIR = tmp
    if actor is not None:
        kfr.resolve_actor = lambda sid8, brain_root=None, _a=actor: _a
    sid8 = (payload.get("session_id") or "")[:8].lower()
    if sentinel_exists and sid8:
        (tmp / f"{sid8}.fread").write_text("1", encoding="utf-8")
    buf = io.StringIO()
    real_stdin = sys.stdin
    sys.stdin = io.StringIO(json.dumps(payload))
    try:
        with redirect_stdout(buf):
            code = kfr.main()
    finally:
        sys.stdin = real_stdin
    return code, buf.getvalue()


def parse_ctx(out):
    if not out.strip():
        return None
    try:
        return json.loads(out)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        return "<<unparseable>>"


def main():
    print("keepsake-forced-read.py — boundary harness\n")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        # 1. SessionStart -> directive + global keepsake block, exit 0
        c, out = run({"hook_event_name": "SessionStart", "session_id": "aaaa1111-x",
                      "source": "startup"}, tmp=tmp)
        ctx = parse_ctx(out)
        check("1 SessionStart exit 0", c == 0)
        check("1 SessionStart injects the FORCED-READ directive", ctx and "FORCED-READ" in ctx)
        check("1 SessionStart names the Global keepsake", ctx and "Global keepsake/current.md" in ctx)
        check("1 SessionStart names the resume read", ctx and "inventory/*-resume" in ctx)

        # 2. SessionStart for a sub-agent (agent_type set) -> silent
        c, out = run({"hook_event_name": "SessionStart", "session_id": "bbbb2222-x",
                      "source": "startup", "agent_type": "dwarf"}, tmp=tmp)
        check("2 SessionStart sub-agent silent", c == 0 and out.strip() == "")

        # 3. First UserPromptSubmit, actor=jebrim -> inline jebrim keepsake + sentinel
        sid = "cccc3333-x"
        c, out = run({"hook_event_name": "UserPromptSubmit", "session_id": sid,
                      "prompt": "pull the mart numbers"}, actor="jebrim", tmp=tmp)
        ctx = parse_ctx(out)
        check("3 jebrim first-prompt exit 0", c == 0)
        check("3 jebrim keepsake content inlined (real file read)",
              ctx and "Shipping Data Mart" in ctx)
        check("3 jebrim keepsake labelled in-force", ctx and "Jebrim keepsake/current.md" in ctx)
        check("3 sentinel written", (tmp / "cccc3333.fread").exists())
        # §Z.B: the always-read domain map rides in the SAME emission (real _index.md).
        check("3 jebrim domain-index inlined (real file read)",
              ctx and "Jebrim bank/domains/_index.md" in ctx)
        check("3 jebrim domain-index carries the map (Digested domains)",
              ctx and "Digested domains" in ctx)
        check("3 keepsake AND domain-index in one emission",
              ctx and "Jebrim keepsake/current.md" in ctx and "Jebrim bank/domains/_index.md" in ctx)

        # 4. Second prompt same session (sentinel present) -> silent
        c, out = run({"hook_event_name": "UserPromptSubmit", "session_id": sid,
                      "prompt": "and again"}, actor="jebrim", sentinel_exists=True, tmp=tmp)
        check("4 second prompt silent (sentinel)", c == 0 and out.strip() == "")

        # 5. UserPromptSubmit, actor=braindead -> silent, NO sentinel
        c, out = run({"hook_event_name": "UserPromptSubmit", "session_id": "dddd4444-x",
                      "prompt": "lets develop gielinor"}, actor="braindead", tmp=tmp)
        check("5 braindead silent", c == 0 and out.strip() == "")
        check("5 braindead no sentinel (skip != done)", not (tmp / "dddd4444.fread").exists())

        # 6. UserPromptSubmit, actor unresolved ('') -> silent, NO sentinel (retry next turn)
        c, out = run({"hook_event_name": "UserPromptSubmit", "session_id": "eeee5555-x",
                      "prompt": "hi"}, actor="", tmp=tmp)
        check("6 unresolved-actor silent", c == 0 and out.strip() == "")
        check("6 unresolved no sentinel (retry)", not (tmp / "eeee5555.fread").exists())

        # 7. UserPromptSubmit, actor=unscoped -> silent (global covered it), NO sentinel
        c, out = run({"hook_event_name": "UserPromptSubmit", "session_id": "ffff6666-x",
                      "prompt": "thoughts?"}, actor="unscoped", tmp=tmp)
        check("7 unscoped silent", c == 0 and out.strip() == "")
        check("7 unscoped no sentinel (later switch can inject)",
              not (tmp / "ffff6666.fread").exists())

        # 8. UserPromptSubmit, actor=zezima -> inline zezima keepsake (different player path)
        c, out = run({"hook_event_name": "UserPromptSubmit", "session_id": "7777aaaa-x",
                      "prompt": "the flat"}, actor="zezima", tmp=tmp)
        ctx = parse_ctx(out)
        check("8 zezima keepsake content inlined", ctx and "Zezima keepsake/current.md" in ctx)
        # §Z.B: zezima has no bank/domains/_index.md yet -> no domain block, no crash.
        check("8 zezima no domain-index block (none on disk)",
              ctx and "bank/domains/_index.md" not in ctx)

        # 11. §Z.B over-budget: a bloated index is NAMED, not inlined (digest-territory).
        orig_cap = kfr.INDEX_BYTE_CAP
        kfr.INDEX_BYTE_CAP = 10  # force the real jebrim index over cap
        try:
            c, out = run({"hook_event_name": "UserPromptSubmit", "session_id": "9999cccc-x",
                          "prompt": "scm work"}, actor="jebrim", tmp=tmp)
            ctx = parse_ctx(out)
        finally:
            kfr.INDEX_BYTE_CAP = orig_cap
        check("11 over-budget index named not inlined",
              ctx and "over budget" in ctx and "Digested domains" not in ctx)
        check("11 over-budget still inlines the keepsake",
              ctx and "Jebrim keepsake/current.md" in ctx)

        # 9. Malformed stdin -> exit 0, no output
        buf = io.StringIO()
        real = sys.stdin
        sys.stdin = io.StringIO("{not json")
        try:
            with redirect_stdout(buf):
                c = kfr.main()
        finally:
            sys.stdin = real
        check("9 malformed stdin exit 0 silent", c == 0 and buf.getvalue().strip() == "")

        # 10. Unrelated event (Stop) -> exit 0, no output
        c, out = run({"hook_event_name": "Stop", "session_id": "8888bbbb-x"}, actor="jebrim", tmp=tmp)
        check("10 unrelated event silent", c == 0 and out.strip() == "")

    n = len(results)
    passed = sum(1 for _, ok in results if ok)
    print(f"\n{passed}/{n} PASS")
    return 0 if passed == n else 1


if __name__ == "__main__":
    sys.exit(main())

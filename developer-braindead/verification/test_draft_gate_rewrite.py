#!/usr/bin/env python3
"""Boundary harness for gielinor/.claude/hooks/draft-gate-rewrite.py (plan §X.3).

Verifies the input-rewrite at the hook boundary on synthetic payloads — no live
session needed (same discipline as the keepsake-forced-read / domain-cue harnesses).
Asserts: the redirect fires for a main-agent bank/notes/ + spellbook/skills/ write;
it STANDS DOWN for the promotion contexts (sub-agent, braindead, ritual .mode); it is
idempotent + gielinor-scoped; and the FULL tool_input survives the rewrite (the
updatedInput full-replace gotcha). Exit 0 always.

Run: python developer-braindead/verification/test_draft_gate_rewrite.py
"""
import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

BRAIN = Path(__file__).resolve().parents[2]

# S187: route synthetic test events to a temp file, never the LIVE analytics
# stream (switchboard/ritual_log.py honors RITUAL_EVENTS_PATH per call;
# subprocesses inherit it). Pre-S187 these suites polluted the real log.
import os as _os
import tempfile as _tempfile
_os.environ["RITUAL_EVENTS_PATH"] = str(
    Path(_tempfile.gettempdir()) / "ritual-events-test.ndjson")
HOOK = BRAIN / "gielinor" / ".claude" / "hooks" / "draft-gate-rewrite.py"
GIE = BRAIN / "gielinor"

spec = importlib.util.spec_from_file_location("dgr", HOOK)
dgr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dgr)

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")


def run(payload, actor="jebrim", mode=""):
    """Drive main() with a payload via stdin; control resolved actor + .mode marker.
    Returns (exit_code, parsed_output_or_None)."""
    dgr.resolve_actor = lambda sid8, brain_root=None, _a=actor: _a
    dgr.mode_marker = lambda sid8, _m=mode: _m
    buf = io.StringIO()
    real = sys.stdin
    sys.stdin = io.StringIO(json.dumps(payload))
    try:
        with redirect_stdout(buf):
            code = dgr.main()
    finally:
        sys.stdin = real
    raw = buf.getvalue()
    parsed = json.loads(raw) if raw.strip() else None
    return code, parsed


def hso(parsed):
    return (parsed or {}).get("hookSpecificOutput", {})


def new_path(parsed):
    ui = hso(parsed).get("updatedInput", {})
    return ui.get("file_path") or ui.get("notebook_path")


def gie_path(*parts):
    return str(GIE.joinpath(*parts))


def main():
    print("draft-gate-rewrite.py — boundary harness\n")

    # 1. main-agent bank/notes write -> redirect to bank/drafts/notes, allow, exit 0
    p = gie_path("players", "jebrim", "bank", "notes", "projects", "eu-tender.md")
    c, out = run({"tool_name": "Write", "session_id": "aaaa1111-x",
                  "tool_input": {"file_path": p, "content": "BODY"}})
    check("1 bank/notes exit 0", c == 0)
    check("1 bank/notes permissionDecision allow", hso(out).get("permissionDecision") == "allow")
    check("1 bank/notes -> bank/drafts/notes",
          new_path(out) and new_path(out).replace("\\", "/").endswith(
              "players/jebrim/bank/drafts/notes/projects/eu-tender.md"))
    check("1 full input preserved (content survives)",
          hso(out).get("updatedInput", {}).get("content") == "BODY")

    # 2. main-agent spellbook/skills write -> redirect to spellbook/drafts/skills
    p = gie_path("players", "jebrim", "spellbook", "skills", "run-report.md")
    c, out = run({"tool_name": "Write", "session_id": "aaaa1112-x",
                  "tool_input": {"file_path": p, "content": "X"}})
    check("2 spellbook/skills -> spellbook/drafts/skills",
          new_path(out) and new_path(out).replace("\\", "/").endswith(
              "players/jebrim/spellbook/drafts/skills/run-report.md"))

    # 3. already-drafts path -> idempotent, no redirect (silent allow)
    p = gie_path("players", "jebrim", "bank", "drafts", "notes", "x.md")
    c, out = run({"tool_name": "Write", "session_id": "aaaa1113-x",
                  "tool_input": {"file_path": p, "content": "X"}})
    check("3 already-drafts: no redirect (idempotent)", c == 0 and out is None)

    # 4. sub-agent (gnome alching promotes) -> stand down
    p = gie_path("players", "jebrim", "bank", "notes", "x.md")
    c, out = run({"tool_name": "Write", "session_id": "aaaa1114-x", "agent_type": "gnome",
                  "tool_input": {"file_path": p, "content": "X"}})
    check("4 sub-agent silent (promotion not broken)", c == 0 and out is None)

    # 5. braindead actor (D-032) -> stand down
    c, out = run({"tool_name": "Write", "session_id": "aaaa1115-x",
                  "tool_input": {"file_path": p, "content": "X"}}, actor="braindead")
    check("5 braindead silent (D-032 full access)", c == 0 and out is None)

    # 6. active ritual marker (alching) -> stand down (promotion is legitimate)
    c, out = run({"tool_name": "Write", "session_id": "aaaa1116-x",
                  "tool_input": {"file_path": p, "content": "X"}}, mode="alching")
    check("6 ritual .mode alching: no redirect (promotion)", c == 0 and out is None)
    # 6b. a non-promotion ritual marker also stands down (defensive width)
    c, out = run({"tool_name": "Write", "session_id": "aaaa1117-x",
                  "tool_input": {"file_path": p, "content": "X"}}, mode="bankstanding")
    check("6b ritual .mode bankstanding: no redirect", c == 0 and out is None)

    # 7. non-gielinor (dev-brain) bank/notes -> no redirect (no drafts gate there)
    dev = str(BRAIN / "developer-braindead" / "bank" / "notes" / "x.md")
    c, out = run({"tool_name": "Write", "session_id": "aaaa1118-x",
                  "tool_input": {"file_path": dev, "content": "X"}})
    check("7 dev-brain path: no redirect (gielinor-scoped)", c == 0 and out is None)

    # 8. non-write tool (Read) -> silent
    c, out = run({"tool_name": "Read", "session_id": "aaaa1119-x",
                  "tool_input": {"file_path": gie_path("players", "jebrim", "bank", "notes", "x.md")}})
    check("8 non-write tool silent", c == 0 and out is None)

    # 9. unrelated gielinor path (quest-log) -> no redirect
    p = gie_path("players", "jebrim", "quest-log", "in-progress", "S999_x.md")
    c, out = run({"tool_name": "Write", "session_id": "aaaa1120-x",
                  "tool_input": {"file_path": p, "content": "X"}})
    check("9 unrelated path (quest-log): no redirect", c == 0 and out is None)

    # 10. MultiEdit (file_path + edits) -> redirect preserves edits
    p = gie_path("players", "jebrim", "bank", "notes", "m.md")
    c, out = run({"tool_name": "MultiEdit", "session_id": "aaaa1121-x",
                  "tool_input": {"file_path": p, "edits": [{"old_string": "a", "new_string": "b"}]}})
    check("10 MultiEdit redirects + preserves edits",
          new_path(out) and "drafts" in new_path(out)
          and hso(out).get("updatedInput", {}).get("edits") == [{"old_string": "a", "new_string": "b"}])

    # 11. Windows backslash path -> redirect works (separator-agnostic)
    p = str(GIE).replace("/", "\\") + r"\players\zezima\bank\notes\flat.md"
    c, out = run({"tool_name": "Write", "session_id": "aaaa1122-x",
                  "tool_input": {"file_path": p, "content": "X"}}, actor="zezima")
    check("11 backslash path redirects",
          new_path(out) and "drafts" in new_path(out).replace("\\", "/")
          and new_path(out).replace("\\", "/").endswith("zezima/bank/drafts/notes/flat.md"))

    # 12. NotebookEdit (notebook_path key) -> redirect on notebook_path
    p = gie_path("players", "jebrim", "bank", "notes", "nb.ipynb")
    c, out = run({"tool_name": "NotebookEdit", "session_id": "aaaa1123-x",
                  "tool_input": {"notebook_path": p, "new_source": "code"}})
    check("12 NotebookEdit redirects notebook_path",
          new_path(out) and "drafts" in new_path(out)
          and hso(out).get("updatedInput", {}).get("new_source") == "code")

    # 13. deity (guthix) bank/notes -> redirect (rule generalizes beyond players)
    p = gie_path("deities", "guthix", "bank", "notes", "drift.md")
    c, out = run({"tool_name": "Write", "session_id": "aaaa1124-x",
                  "tool_input": {"file_path": p, "content": "X"}}, actor="guthix")
    check("13 guthix deity bank/notes redirects",
          new_path(out) and new_path(out).replace("\\", "/").endswith(
              "deities/guthix/bank/drafts/notes/drift.md"))

    # 14. malformed stdin -> exit 0 silent
    buf = io.StringIO()
    real = sys.stdin
    sys.stdin = io.StringIO("{not json")
    try:
        with redirect_stdout(buf):
            c = dgr.main()
    finally:
        sys.stdin = real
    check("14 malformed stdin exit 0 silent", c == 0 and buf.getvalue().strip() == "")

    # 15. empty file_path -> silent
    c, out = run({"tool_name": "Write", "session_id": "aaaa1125-x", "tool_input": {}})
    check("15 empty file_path silent", c == 0 and out is None)

    n = len(results)
    passed = sum(1 for _, ok in results if ok)
    print(f"\n{passed}/{n} PASS")
    return 0 if passed == n else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Boundary harness for the [LOR] lorebook-decision cue arm (dev-brain, S192).

Covers `_parse_lorebook_index` + `_lorebook_blocks` in `domain-cue-reminder.py`
over the live `gielinor/lorebook/_index.md`: a cue-active decision (one carrying
both `patterns:` and `rule:`) gets its distilled RULE force-inlined on a prompt
match, once per session per decision, then goes silent for that session (no
name-nudge tail — lorebook cues like "commit" recur too often for one).
Sub-agents and braindead are skipped. Closes knowledge-miss regression case 10.

Synthetic payloads at the hook boundary — same discipline as
test_domain_cue_inline.py. STATUS_DIR redirected to a tmp dir; RITUAL_EVENTS_PATH
redirected so no synthetic event touches the live analytics stream (S187).

Run: python developer-braindead/verification/test_lorebook_cue.py
"""
import importlib.util
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

BRAIN = Path(__file__).resolve().parents[2]

# S187: route synthetic test events to a temp file, never the LIVE stream.
os.environ["RITUAL_EVENTS_PATH"] = str(
    Path(tempfile.gettempdir()) / "ritual-events-test.ndjson")

HOOK_DIR = BRAIN / "gielinor" / ".claude" / "hooks"
HOOK = HOOK_DIR / "domain-cue-reminder.py"

if str(HOOK_DIR) not in sys.path:
    sys.path.insert(0, str(HOOK_DIR))

spec = importlib.util.spec_from_file_location("dcr_lorebook", HOOK)
dcr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dcr)

dcr.STATUS_DIR = Path(tempfile.mkdtemp(prefix="lorebook_cue_test_"))

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")


def run(prompt, actor="jebrim", sid="sessAAAA0000", agent_type=None):
    dcr.resolve_actor = lambda sid8, brain_root=None, _a=actor: _a
    payload = {"hook_event_name": "UserPromptSubmit", "prompt": prompt,
               "session_id": sid}
    if agent_type:
        payload["agent_type"] = agent_type
    buf = io.StringIO()
    stdin_bak = sys.stdin
    sys.stdin = io.StringIO(json.dumps(payload))
    try:
        with redirect_stdout(buf):
            code = dcr.main()
    finally:
        sys.stdin = stdin_bak
    return code, buf.getvalue()


def emitted_context(stdout_str):
    if not stdout_str.strip():
        return ""
    try:
        return json.loads(stdout_str)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        return ""


# --- 1. live index parses; the four cue-active rows are present -----------------
entries = dcr._parse_lorebook_index()
ids = {e["id"] for e in entries}
check("parse: live index yields cue-active entries", len(entries) >= 4)
check("parse: D-017/D-023/D-024/D-034 cue-active",
      {"D-017", "D-023", "D-024", "D-034"} <= ids)
check("parse: inert entries (carried-by only) excluded", "D-025" not in ids)
check("parse: every entry has patterns+rule",
      all(e["patterns"] and e["rule"] for e in entries))

# --- 2. commit-shaped prompt -> D-024 rule INLINED ------------------------------
# Stable token from the D-024 rule line (asserts the RULE text lands, not a name).
TOK_D024 = "explicit pathspecs"
code, out = run("ok lets commit this and close up", sid="sessLOR00001")
ctx = emitted_context(out)
check("inline: exit 0", code == 0)
check("inline: emitted on commit prompt", bool(ctx))
check("inline: D-024 named", "D-024" in ctx)
check("inline: rule TEXT inlined", TOK_D024 in ctx)
check("inline: points at the full entry", "lorebook/confirmed/D-024" in ctx)

# --- 3. same session, second commit prompt -> SILENT (no wallpaper tail) --------
code, out = run("commit the rest too", sid="sessLOR00001")
ctx = emitted_context(out)
check("once-per-session: exit 0", code == 0)
check("once-per-session: silent on repeat (no name-nudge tail)", "D-024" not in ctx)

# --- 4. different session -> inlines again (sentinel per-session) ---------------
code, out = run("commit it", sid="sessLOR20002")
check("per-session: fresh session re-inlines", TOK_D024 in emitted_context(out))

# --- 5. powershell prompt -> D-023 rule inlined ---------------------------------
code, out = run("write me a powershell one-liner to patch these files",
                sid="sessLOR30003")
ctx = emitted_context(out)
check("D-023: fires on powershell", "D-023" in ctx and "ReadAllText" in ctx)

# --- 6. two decisions in one prompt -> ONE combined emission, both present ------
code, out = run("powershell bulk edit, then commit it", sid="sessLOR40004")
ctx = emitted_context(out)
check("multi: both decisions in one emission",
      "D-023" in ctx and "D-024" in ctx)
check("multi: combined-block header used",
      "Multiple knowledge-home topics detected" in ctx)

# --- 7. benign prompt -> silent --------------------------------------------------
code, out = run("how are the carrier volumes trending this week?",
                sid="sessLOR50005")
ctx = emitted_context(out)
check("benign: no lorebook block", "lorebook" not in ctx.lower() or "D-0" not in ctx)

# --- 8. braindead -> skipped; sub-agent -> skipped -------------------------------
code, out = run("commit this", actor="braindead", sid="sessLOR60006")
check("braindead: nothing emitted", emitted_context(out) == "")
code, out = run("commit this", sid="sessLOR70007", agent_type="dwarf")
check("subagent: no lorebook block", "D-024" not in emitted_context(out))

# --- 9. domain arm unregressed: shipping still fires alongside ------------------
code, out = run("pull the DHL surcharge from the shipping mart",
                actor="zezima", sid="sessLOR80008")
ctx = emitted_context(out)
check("unregressed: shipping nudge still fires", "Read before answering:" in ctx)

# --- 10. logging + missing index + malformed input -------------------------------
logged = []
dcr.log_event = lambda event, status, **k: logged.append((event, status))
run("commit the file", sid="sessLOR90009")
check("log: lorebook inline logged",
      ("lorebook-cue:D-024", "inline") in logged)

idx_bak = dcr.LOREBOOK_INDEX
dcr.LOREBOOK_INDEX = Path(tempfile.gettempdir()) / "no_such_index_lor.md"
try:
    code, out = run("commit the file", sid="sessLORa000a")
    check("missing index: exit 0, no lorebook block",
          code == 0 and "D-024" not in emitted_context(out))
finally:
    dcr.LOREBOOK_INDEX = idx_bak

sys.stdin = io.StringIO("not json{")
try:
    code = dcr.main()
finally:
    sys.stdin = sys.__stdin__
check("malformed: exit 0", code == 0)

# --- summary ---------------------------------------------------------------------
passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f"\n{passed}/{total} passed")
sys.exit(0 if passed == total else 1)

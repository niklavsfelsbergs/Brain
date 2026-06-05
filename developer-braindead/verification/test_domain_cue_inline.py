#!/usr/bin/env python3
"""Boundary harness for the domain-cue FORCE-INLINE upgrade (dev-brain, 2026-06-05).

Covers the `inline_homes` field on `cue_registry.py` + the `_maybe_inline` arm of
`domain-cue-reminder.py`: a matched domain with small, in-tree knowledge homes gets
its CONTENTS force-injected (not just named), ONCE per session per domain, byte-capped,
sub-agents excluded, with graceful fallback to the name-only nudge. This is the §X.4
keepsake move applied to domain knowledge ("a directive only NAMES; inlining FORCES").

Synthetic payloads at the hook boundary — no live session needed (same discipline as
test_domain_cue_registry.py / test_keepsake_forced_read.py). STATUS_DIR is redirected
to a tmp dir so sentinel writes never touch the real ~/.claude/status.

Asserts:
  - deploy-schema (has inline_homes) inlines its notes' CONTENTS on first match,
  - the same domain in the SAME session emits the lighter name-only nudge afterward,
  - a DIFFERENT session inlines again (sentinel is per-session),
  - shipping (no inline_homes) is name-only as before,
  - sub-agents (agent_type set) get the name-nudge, never the inline,
  - over-cap homes fall back to naming AND do NOT burn the sentinel (nudge keeps firing),
  - braindead is still fully skipped,
  - the inline/nudge distinction is logged,
  - exit-0-always holds; malformed input is safe.

Run: python developer-braindead/verification/test_domain_cue_inline.py
"""
import importlib.util
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

BRAIN = Path(__file__).resolve().parents[2]
HOOK_DIR = BRAIN / "gielinor" / ".claude" / "hooks"
HOOK = HOOK_DIR / "domain-cue-reminder.py"

if str(HOOK_DIR) not in sys.path:
    sys.path.insert(0, str(HOOK_DIR))

import cue_registry  # noqa: E402

spec = importlib.util.spec_from_file_location("dcr_inline", HOOK)
dcr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dcr)

# Isolate sentinel writes — never litter the real status dir.
dcr.STATUS_DIR = Path(tempfile.mkdtemp(prefix="dcue_inline_test_"))

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")


def run(prompt, actor="jebrim", sid="sessAAAA0000", agent_type=None):
    """Drive main() with a prompt via stdin, forcing the resolved actor.
    `sid` keys the per-session sentinel; vary it to test session scoping."""
    dcr.resolve_actor = lambda sid8, brain_root=None, _a=actor: _a
    payload = {"hook_event_name": "UserPromptSubmit", "prompt": prompt, "session_id": sid}
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


# Stable tokens that appear in the deploy-schema notes' bodies (asserts CONTENTS land,
# not just the path names).
TOK_TOPOLOGY = "deploy topology"
TOK_FIF = "FIF report data quirks"
INLINE_MARKER = "force-loaded once this session"

# --- 1. first deploy match in a session -> CONTENTS inlined --------------------
code, out = run("how should I order the schema migration deploy", sid="sessONE00001")
ctx = emitted_context(out)
check("inline: exit 0", code == 0)
check("inline: nudge emitted", bool(ctx))
check("inline: force-load marker present", INLINE_MARKER in ctx)
check("inline: topology note CONTENTS present", TOK_TOPOLOGY in ctx)
check("inline: FIF note CONTENTS present", TOK_FIF in ctx)
check("inline: still carries the name/read-before nudge", "Read before answering:" in ctx)

# --- 2. same session, second deploy match -> name-only (contents already loaded) --
code, out = run("another deploy question, same session", sid="sessONE00001")
ctx = emitted_context(out)
check("once-per-session: exit 0", code == 0)
check("once-per-session: nudge still emitted", bool(ctx))
check("once-per-session: NO re-inlined contents", INLINE_MARKER not in ctx)
check("once-per-session: name nudge retained", "Canonical knowledge home:" in ctx)

# --- 3. different session -> inlines again (sentinel is per-session) ------------
code, out = run("schema deploy ordering?", sid="sessTWO00002")
ctx = emitted_context(out)
check("per-session: fresh session re-inlines", INLINE_MARKER in ctx and TOK_TOPOLOGY in ctx)

# --- 4. shipping (no inline_homes) -> name-only, never inlined ------------------
code, out = run("pull the DHL surcharge from the shipping mart", sid="sessSHIP0003")
ctx = emitted_context(out)
check("shipping: exit 0", code == 0)
check("shipping: name nudge emitted", "Read before answering:" in ctx)
check("shipping: NO force-load marker (no inline_homes)", INLINE_MARKER not in ctx)

# --- 5. sub-agent -> name-nudge only, never the heavier inline ------------------
code, out = run("schema migration deploy ordering", sid="sessSUB00004", agent_type="dwarf")
ctx = emitted_context(out)
check("subagent: exit 0", code == 0)
check("subagent: name nudge emitted", bool(ctx))
check("subagent: NO force-load inline", INLINE_MARKER not in ctx)

# --- 6. over-cap -> fall back to naming, sentinel NOT burned --------------------
cap_bak = dcr.INLINE_BYTE_CAP
dcr.INLINE_BYTE_CAP = 10  # smaller than any real note
try:
    code, out = run("deploy schema migration", sid="sessCAP00005")
    ctx = emitted_context(out)
    check("over-cap: exit 0", code == 0)
    check("over-cap: falls back to name-only", INLINE_MARKER not in ctx and bool(ctx))
    # sentinel must NOT exist -> a later (cap-restored) prompt can still inline
    # (sid8 is sid[:8].lower() -> "sesscap0")
    sentinel = dcr.STATUS_DIR / "sesscap0.dcue-deploy-schema"
    check("over-cap: sentinel NOT burned", not sentinel.exists())
finally:
    dcr.INLINE_BYTE_CAP = cap_bak
# now with the cap restored, the same session inlines (proves the no-burn above)
code, out = run("deploy schema migration", sid="sessCAP00005")
check("over-cap: inlines once cap restored", INLINE_MARKER in emitted_context(out))

# --- 7. braindead -> fully skipped (no inline, no nudge) -----------------------
code, out = run("deploy the schema migration", actor="braindead", sid="sessBD000006")
check("braindead: exit 0", code == 0)
check("braindead: nothing emitted", emitted_context(out) == "")

# --- 8. logging: first match logs 'inline', repeat logs 'nudge' ----------------
logged = []
dcr.log_event = lambda event, status, **k: logged.append((event, status))
run("schema deploy ordering", sid="sessLOG00007")
run("schema deploy ordering", sid="sessLOG00007")
check("log: first match logged as inline",
      ("domain-cue:deploy-schema", "inline") in logged)
check("log: repeat match logged as nudge",
      ("domain-cue:deploy-schema", "nudge") in logged)

# --- 9. malformed input: never disrupts ----------------------------------------
sys.stdin = io.StringIO("not json{")
try:
    code = dcr.main()
finally:
    sys.stdin = sys.__stdin__
check("malformed: exit 0", code == 0)

# --- summary -------------------------------------------------------------------
passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f"\n{passed}/{total} passed")
sys.exit(0 if passed == total else 1)

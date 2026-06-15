#!/usr/bin/env python3
"""Boundary harness for §Z.C — per-player domain-digest auto-discovery in
domain-cue-reminder.py.

Covers the discovery arm: the hook discovers the ACTIVE player's bank/domains/*.md
digests, reads their frontmatter `patterns`, and force-inlines the matching DIGEST
on a cue match — discovered (not hand-listed in cue_registry) and digest-not-whole-
notes. Reuses the §X.3 `_maybe_inline` machinery (once-per-session sentinel, byte cap,
sub-agent exclusion). The global registry stays for external/specialist domains.

Reads the REAL jebrim scm.md digest (the Z.A pilot) — so this also verifies the live
digest inlines on an "SCM" prompt. Synthetic payloads at the hook boundary; STATUS_DIR
redirected to tmp so sentinels never touch ~/.claude/status.

Run: python developer-braindead/verification/test_domain_digest_discovery.py
"""
import importlib.util
import io
import json
import sys
import tempfile
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
HOOK_DIR = BRAIN / "gielinor" / ".claude" / "hooks"
HOOK = HOOK_DIR / "domain-cue-reminder.py"
SCM_DIGEST = BRAIN / "gielinor" / "players" / "jebrim" / "bank" / "domains" / "scm.md"

if str(HOOK_DIR) not in sys.path:
    sys.path.insert(0, str(HOOK_DIR))

spec = importlib.util.spec_from_file_location("dcr_discovery", HOOK)
dcr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dcr)

dcr.STATUS_DIR = Path(tempfile.mkdtemp(prefix="dcue_discovery_test_"))

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")


def run(prompt, actor="jebrim", sid="sessAAAA0000", agent_type=None):
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


def ctx_of(out):
    if not out.strip():
        return ""
    try:
        return json.loads(out)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        return ""


INLINE_MARKER = "force-loaded once this session"
# Stable token in the scm.md digest BODY (not its frontmatter) — proves CONTENTS land.
TOK_BODY = "cost_for_routing"

# --- 0. frontmatter parse + discovery shape (no registry edit needed) ----------
fm = dcr._parse_frontmatter(SCM_DIGEST)
check("0 frontmatter: scm patterns parsed as a list", isinstance(fm.get("patterns"), list))
check("0 frontmatter: 'scm' among patterns", "scm" in (fm.get("patterns") or []))
check("0 frontmatter: domain slug == scm", fm.get("domain") == "scm")
disc = dcr._discover_digests("jebrim")
names = {d["name"] for d in disc}
check("0 discovery: jebrim digests include domain-scm", "domain-scm" in names)
check("0 discovery: scm entry inlines its own digest file",
      any(any("bank/domains/scm.md" in h for h in (d.get("inline_homes") or [])) for d in disc))

# --- 1. an "SCM" prompt -> the real digest inlines -----------------------------
code, out = run("Hey Jebrim, let's work on the SCM", sid="scmONE0001")
ctx = ctx_of(out)
check("1 exit 0", code == 0)
check("1 scm digest nudge emitted", bool(ctx))
check("1 force-load marker present", INLINE_MARKER in ctx)
check("1 digest BODY inlined (cost_for_routing)", TOK_BODY in ctx)
check("1 names the digest as authoritative", "authoritative" in ctx)

# --- 2. once-per-session: a second SCM prompt -> name-only ----------------------
code, out = run("more SCM work this session", sid="scmONE0001")
ctx = ctx_of(out)
check("2 still emits", bool(ctx))
check("2 NO re-inlined body second time", INLINE_MARKER not in ctx)

# --- 3. a fresh session re-inlines (sentinel is per-session; distinct sid8) ------
code, out = run("SCM alert engine question", sid="scmTWO0002")
check("3 fresh session re-inlines", INLINE_MARKER in ctx_of(out))

# --- 4. a non-matching prompt -> no scm block ----------------------------------
code, out = run("what's the weather like", sid="sessNONE0003")
check("4 unrelated prompt: silent", ctx_of(out) == "")

# --- 5. zezima (no bank/domains digests) -> discovery empty, no crash ----------
check("5 zezima discovery empty", dcr._discover_digests("zezima") == [])
code, out = run("Hey Zezima, the SCM", actor="zezima", sid="sessZEZ00004")
check("5 zezima: no scm digest inlined", INLINE_MARKER not in ctx_of(out))

# --- 6. braindead -> fully skipped ---------------------------------------------
code, out = run("SCM", actor="braindead", sid="sessBD000005")
check("6 braindead discovery empty", dcr._discover_digests("braindead") == [])
check("6 braindead: nothing emitted", ctx_of(out) == "")

# --- 7. sub-agent -> name-nudge, never the heavier inline ----------------------
code, out = run("let's work on the SCM", sid="sessSUB00006", agent_type="dwarf")
ctx = ctx_of(out)
check("7 subagent: emits a nudge", bool(ctx))
check("7 subagent: NO force-load inline", INLINE_MARKER not in ctx)

# --- 8. discovered digest coexists with the static registry --------------------
# "shipping costs monitoring" hits BOTH the scm digest AND static shipping (\bshipping\b).
code, out = run("shipping costs monitoring dashboard", sid="sessBOTH0007")
ctx = ctx_of(out)
check("8 both: scm digest body present", TOK_BODY in ctx)
check("8 both: static shipping nudge also present",
      "SOURCE #1" in ctx and "shipping_mart" in ctx)

# --- 9. malformed input -> safe ------------------------------------------------
sys.stdin = io.StringIO("not json{")
try:
    code = dcr.main()
finally:
    sys.stdin = sys.__stdin__
check("9 malformed: exit 0", code == 0)

passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f"\n{passed}/{total} passed")
sys.exit(0 if passed == total else 1)

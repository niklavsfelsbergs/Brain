#!/usr/bin/env python3
"""Boundary harness for the enriched domain-cue registry (dev-brain plan §Y.5).

Covers the Y.5 enrichment of `cue_registry.py` (structured fields canonical_files /
specialist / freshness / read_before) and the `domain-cue-reminder.py` renderer that
composes the nudge FROM those fields. Synthetic payloads at the hook boundary — no
live session needed (same discipline as the keepsake-forced-read / draft-gate harnesses).

Asserts:
  - every live DOMAINS entry carries the structured fields,
  - in-brain canonical_files actually resolve on disk (a router must not point at
    dead paths — the whole reason Y.5 verified paths before writing them),
  - _render composes the structured tail (files / specialist / freshness / read_before),
  - backward-compat: an entry with only `message` renders just that line,
  - the combine path joins multiple matched domains under [name] headers,
  - the exit-0-always contract holds (advisory hook, never disrupts a prompt),
  - actor skip + malformed input are safe.

Run: python developer-braindead/verification/test_domain_cue_registry.py
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
HOOK_DIR = BRAIN / "gielinor" / ".claude" / "hooks"
HOOK = HOOK_DIR / "domain-cue-reminder.py"

# The hook does `from cue_registry import DOMAINS` at import time; that resolves via
# the script's own dir when run directly, so put HOOK_DIR on the path before loading
# it via importlib (otherwise DOMAINS would silently fall back to []).
if str(HOOK_DIR) not in sys.path:
    sys.path.insert(0, str(HOOK_DIR))

import cue_registry  # noqa: E402

spec = importlib.util.spec_from_file_location("dcr", HOOK)
dcr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dcr)

# Isolate any sentinel writes (the inline arm burns a per-session sentinel) to a tmp
# dir so this harness never touches the real ~/.claude/status.
import tempfile  # noqa: E402
dcr.STATUS_DIR = Path(tempfile.mkdtemp(prefix="dcue_registry_test_"))

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")


def run(prompt, actor="jebrim"):
    """Drive main() with a prompt via stdin, forcing the resolved actor.
    Returns (exit_code, stdout_str)."""
    dcr.resolve_actor = lambda sid8, brain_root=None, _a=actor: _a
    payload = {"hook_event_name": "UserPromptSubmit",
               "prompt": prompt, "session_id": "test1234abcd"}
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
    """Parse the additionalContext out of the hook's stdout, or '' if none."""
    if not stdout_str.strip():
        return ""
    try:
        return json.loads(stdout_str)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        return ""


# --- 1. data: every live entry carries the structured fields -------------------
REQUIRED = ("name", "patterns", "message", "canonical_files", "freshness", "read_before")
for d in cue_registry.DOMAINS:
    nm = d.get("name", "?")
    for f in REQUIRED:
        check(f"entry '{nm}' has field '{f}'", d.get(f))
    check(f"entry '{nm}' canonical_files is a non-empty list",
          isinstance(d.get("canonical_files"), list) and len(d["canonical_files"]) > 0)

# --- 2. in-brain canonical_files resolve on disk -------------------------------
# External-repo paths (labelled "<repo> repo: ...") are intentionally skipped — they
# don't live in this tree; only brain-relative paths are checked.
for d in cue_registry.DOMAINS:
    for entry in d.get("canonical_files", []):
        if "repo:" in entry:
            continue  # external knowledge home — not in this tree
        # strip a trailing " §N" section marker and any parenthetical
        path = entry.split(" §")[0].split(" (")[0].strip()
        # skip directory-ish references that aren't a concrete file
        if path.endswith("/"):
            continue
        check(f"[{d['name']}] canonical file exists: {path}",
              (BRAIN / "gielinor" / path).exists())

# --- 3. _render composes the structured tail -----------------------------------
ship = next(d for d in cue_registry.DOMAINS if d["name"] == "shipping")
rendered = dcr._render(ship, "DHL")
check("render: substitutes {matched}", "DHL" in rendered)
check("render: includes Canonical knowledge home", "Canonical knowledge home:" in rendered)
check("render: includes the specialist (shipping has one)", "Or spawn:" in rendered)
check("render: includes Freshness", "Freshness:" in rendered)
check("render: includes Read before answering", "Read before answering:" in rendered)
check("render: surfaces the external repo home",
      "picanova/shipping-agent" in rendered)

deploy = next(d for d in cue_registry.DOMAINS if d["name"] == "deploy-schema")
rendered_dep = dcr._render(deploy, "deploy")
check("render: deploy-schema has NO specialist line", "Or spawn:" not in rendered_dep)
check("render: deploy-schema lists an in-brain note path",
      "bi_analytics_deploy_topology.md" in rendered_dep)

# --- 4. backward-compat: message-only entry renders just the lead --------------
bare = {"name": "bare", "message": "Bare topic ({matched})."}
rendered_bare = dcr._render(bare, "x")
check("render: message-only entry renders the lead", rendered_bare == "Bare topic (x).")
check("render: message-only entry has no structured tail",
      "Canonical knowledge home:" not in rendered_bare)

# --- 5. end-to-end: a shipping prompt emits the structured nudge ---------------
code, out = run("can you pull the DHL surcharge from the shipping mart")
ctx = emitted_context(out)
check("e2e shipping: exit 0", code == 0)
check("e2e shipping: nudge emitted", bool(ctx))
check("e2e shipping: nudge carries the read-before directive",
      "Read before answering:" in ctx)

# --- 6. combine path: two domains in one prompt --------------------------------
code, out = run("deploy the shipping mart schema migration for the carrier view")
ctx = emitted_context(out)
check("combine: exit 0", code == 0)
check("combine: multi-domain header present",
      "Multiple knowledge-home topics detected" in ctx)
check("combine: shipping block present", "[shipping]" in ctx)
check("combine: deploy-schema block present", "[deploy-schema]" in ctx)

# --- 7. ordinary prompt: silent pass-through -----------------------------------
code, out = run("what's the weather like today")
check("benign: exit 0", code == 0)
check("benign: no nudge", emitted_context(out) == "")

# --- 8. actor skip: braindead gets nothing -------------------------------------
code, out = run("pull the DHL shipping mart figure", actor="braindead")
check("braindead skip: exit 0", code == 0)
check("braindead skip: no nudge", emitted_context(out) == "")

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

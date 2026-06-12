#!/usr/bin/env python3
"""Boundary harness for grounding-cue-reminder.py (dev-brain, S192).

The hook never had a suite; it gets one alongside the S192 artifact-path fix
(knowledge-miss regression case 5). Covers BOTH halves:

  - the continuation-CUE path (load-bearing since D-028; unchanged), and
  - the ARTIFACT path, rebuilt S192: the old ARTIFACT_KEYS payload-field guess
    was dead code (the real UserPromptSubmit payload carries NO attachment
    fields — verified against the shipped binary's payload constructor), so
    detection now matches the upload PLACEHOLDERS the TUI inserts into the
    prompt text ([Image #N], [Pasted text #N +M lines], [...Truncated...],
    dragged absolute doc paths), once per session for artifact-only fires.

Synthetic payloads at the hook boundary; STATUS_DIR redirected to a tmp dir;
RITUAL_EVENTS_PATH redirected (S187 — no synthetic events in the live stream).

Run: python developer-braindead/verification/test_grounding_cue.py
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

os.environ["RITUAL_EVENTS_PATH"] = str(
    Path(tempfile.gettempdir()) / "ritual-events-test.ndjson")

HOOK = BRAIN / "gielinor" / ".claude" / "hooks" / "grounding-cue-reminder.py"
spec = importlib.util.spec_from_file_location("gcr", HOOK)
gcr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gcr)

gcr.STATUS_DIR = Path(tempfile.mkdtemp(prefix="gcue_test_"))

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")


def run(prompt, sid="sessGCUE0000"):
    payload = {"hook_event_name": "UserPromptSubmit", "prompt": prompt,
               "session_id": sid}
    buf = io.StringIO()
    stdin_bak = sys.stdin
    sys.stdin = io.StringIO(json.dumps(payload))
    try:
        with redirect_stdout(buf):
            code = gcr.main()
    finally:
        sys.stdin = stdin_bak
    return code, buf.getvalue()


def ctx(out):
    if not out.strip():
        return ""
    try:
        return json.loads(out)["hookSpecificOutput"]["additionalContext"]
    except Exception:
        return ""


# --- 1. continuation-cue path (the D-028 core, unchanged) -----------------------
code, out = run("once again about the tender numbers")
check("cue: fires on 'once again'", code == 0 and "Grounding cue" in ctx(out))
code, out = run("where is the report I prepared earlier?")
check("cue: fires on 'prepared earlier'", "Grounding cue" in ctx(out))
code, out = run("what are the carrier volumes this week?")
check("cue: silent on benign prompt", ctx(out) == "")

# --- 2. artifact placeholders (the real shapes, from the binary's own grammar) --
code, out = run("[Image #1] what do you make of this?", sid="sessART10001")
c = ctx(out)
check("artifact: fires on [Image #N]", "uploaded artifact" in c and "[Image #1]" in c)
code, out = run("here: [Pasted text #2 +45 lines] thoughts?", sid="sessART20002")
check("artifact: fires on [Pasted text #N +M lines]",
      "uploaded artifact" in ctx(out))
code, out = run("[Pasted text #1] short paste", sid="sessART30003")
check("artifact: fires on [Pasted text #N] (no lines suffix)",
      "uploaded artifact" in ctx(out))
code, out = run("[...Truncated text #1 +900 lines...] rest cut", sid="sessART40004")
check("artifact: fires on truncated-text marker", "uploaded artifact" in ctx(out))

# --- 3. dragged absolute doc path fires; in-tree relative path does NOT ---------
code, out = run(r'look at "C:\Users\nik\Downloads\gertrudes-folio.pdf" please',
                sid="sessART50005")
check("artifact: fires on dragged absolute .pdf path", "uploaded artifact" in ctx(out))
code, out = run("open gielinor/lorebook/_index.md and check it", sid="sessART60006")
check("artifact: silent on in-tree relative .md path", ctx(out) == "")
code, out = run(r"run C:\tools\scripts\build.py now", sid="sessART70007")
check("artifact: silent on absolute CODE path (.py not a doc ext)", ctx(out) == "")

# --- 4. artifact-only is once-per-session; cue path unaffected by the sentinel --
code, out = run("[Image #2] and another screenshot", sid="sessART10001")
check("artifact: SECOND artifact-only fire same session is silent", ctx(out) == "")
code, out = run("[Image #3] once again the same view", sid="sessART10001")
check("artifact: cue match still fires after artifact sentinel burned",
      "Grounding cue" in ctx(out))
code, out = run("[Image #1] fresh session upload", sid="sessART80008")
check("artifact: fresh session fires again", "uploaded artifact" in ctx(out))

# --- 5. braindead skipped (status sidecar) ---------------------------------------
(gcr.STATUS_DIR / "sessbd00.json").write_text(
    json.dumps({"actor": "braindead"}), encoding="utf-8")
code, out = run("[Image #1] once again", sid="sessbd000bd0")
check("braindead: fully skipped", ctx(out) == "")

# --- 6. logging + malformed ------------------------------------------------------
logged = []
gcr.log_event = lambda event, status, **k: logged.append((event, status, k.get("detail")))
run("[Image #1] hello", sid="sessLOG10009")
check("log: artifact fire logged with marker detail",
      any(e == "grounding-cue" and "Image #1" in (d or "") for e, s, d in logged))

sys.stdin = io.StringIO("not json{")
try:
    code = gcr.main()
finally:
    sys.stdin = sys.__stdin__
check("malformed: exit 0", code == 0)

# --- summary ----------------------------------------------------------------------
passed = sum(1 for _, ok in results if ok)
print(f"\n{passed}/{len(results)} passed")
sys.exit(0 if passed == len(results) else 1)

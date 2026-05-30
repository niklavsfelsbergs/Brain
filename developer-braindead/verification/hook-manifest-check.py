#!/usr/bin/env python3
"""verification/hook-manifest-check.py -- hook-manifest self-test (audit S2 #4).

The meta-pattern under half the audit: hooks load only at SESSION START (no
hot-reload of the *registration set* -- a hook newly REGISTERED in settings.json
mid-session is inert until a fresh session), yet "verified" gets claimed on
synthetic tests of a hook the running session never loaded. The cure is a
checkable signal, not a "remember to re-verify" note: diff what's REGISTERED in
the settings files against what's actually present + loadable on disk, and
surface the inert/broken/orphaned ones.

What it checks:
  1. Parse BOTH settings files -- brain-root `.claude/settings.json` and
     `gielinor/.claude/settings.json`. Extract every registered hook command,
     pull the .py path out of each `python "<path>.py"` string, and record the
     settings file + event (PreToolUse/UserPromptSubmit/Stop/...) + matcher.
  2. Classify each registered path:
       MISSING  -- file absent (registered but nothing to load -> silently inert). FAIL.
       BROKEN   -- exists but does not py_compile (won't parse/load -> inert).    FAIL.
       OK       -- exists + compiles.
  3. Reverse check: every *.py in the hooks dirs that NO settings registration
     references -> ORPHAN (WARN, not fail -- helpers / intentionally-dormant
     scripts are orphans by design, e.g. a shared _actor.py).
  4. Best-effort WARN: a registered hook whose mtime is NEWER than this session's
     anchor (the per-session intent file `.claude/intent/<actor>-<sid8>.txt`,
     sid8 = first 8 of $CLAUDE_CODE_SESSION_ID) was modified after session start,
     so it likely isn't loaded in THIS session. Skipped silently if the anchor
     can't be resolved -- it's a nicety, never a failure source.

Ship-dormant (like check.py): runnable standalone
(`python developer-braindead/verification/hook-manifest-check.py`) but NOT
auto-wired into any hook or pre-commit gate. Wiring is a user-only ritual call.

Exit 1 (with the locked banner) if any MISSING or BROKEN; else exit 0. Orphans
and inert-this-session warnings are reported but do NOT by themselves fail.

stdlib only. `--json` for machine output.
"""
from __future__ import annotations

import argparse
import json
import os
import py_compile
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]            # brain root

# Settings files to parse. (label, path) -- label is what shows in the table.
SETTINGS_FILES = [
    ("root", ROOT / ".claude" / "settings.json"),
    ("gielinor", ROOT / "gielinor" / ".claude" / "settings.json"),
]

# Hook directories to scan for the reverse (orphan) check. Only dirs that
# actually exist are scanned; a missing dir is silently skipped.
HOOK_DIRS = [
    ROOT / ".claude" / "hooks",
    ROOT / "gielinor" / ".claude" / "hooks",
    ROOT / "developer-braindead" / ".claude" / "hooks",
]

# Locked failure receipt for this check (same dogfood pattern as check.py's
# BANNER -- construction tooling, not a ritual, so it lives here, not in the
# gielinor failure-banner registry).
BANNER = (
    "## HOOK-MANIFEST CHECK FAILED -- a registered hook is inert\n"
    "One or more hooks registered in settings.json are MISSING or BROKEN: the "
    "harness has nothing to load, so the guarantee they encode is not enforced. "
    "Fix the path / syntax, then re-run from a FRESH session (hook registration "
    "is read at session start)."
)

# A command string looks like:  python "C:/.../foo.py"   or   python "${CLAUDE_PROJECT_DIR}/.claude/hooks/foo.py"
# Pull out the first token ending in .py inside quotes (single or double).
_PY_IN_QUOTES = re.compile(r"""["']([^"']*?\.py)["']""")


def _expand(raw: str, project_dir: Path) -> Path:
    """Resolve a raw hook path string to an absolute Path.

    ${CLAUDE_PROJECT_DIR} resolves against `project_dir` -- the launch dir for
    which the *owning* settings file is the project config. For brain-root
    `.claude/settings.json` that is the brain root; for `gielinor/.claude/
    settings.json` that is the gielinor dir (a gielinor-launched session sets
    CLAUDE_PROJECT_DIR=<...>/gielinor and loads that file). Resolving each file's
    token against its own project dir is what keeps the check honest -- a naive
    "substitute brain root everywhere" flags every gielinor-scoped hook MISSING
    because <root>/.claude/hooks/ does not exist (the S085 expansion trap).
    """
    s = raw.replace("${CLAUDE_PROJECT_DIR}", str(project_dir)).replace(
        "$CLAUDE_PROJECT_DIR", str(project_dir))
    p = Path(s)
    if not p.is_absolute():
        p = project_dir / p
    return Path(os.path.normpath(str(p)))


def _extract_py_path(command: str):
    """Pull the .py path out of a hook command string. None if not a .py hook."""
    m = _PY_IN_QUOTES.search(command)
    if m:
        return m.group(1)
    # Fallback: unquoted -- grab the last whitespace-token ending in .py
    for tok in command.split():
        if tok.endswith(".py"):
            return tok.strip("\"'")
    return None


def _iter_registrations(settings: dict):
    """Yield (event, matcher, command) for every command hook in a settings dict."""
    hooks = settings.get("hooks", {})
    if not isinstance(hooks, dict):
        return
    for event, groups in hooks.items():
        if not isinstance(groups, list):
            continue
        for group in groups:
            if not isinstance(group, dict):
                continue
            matcher = group.get("matcher", "*")
            for h in group.get("hooks", []):
                if not isinstance(h, dict):
                    continue
                if h.get("type") != "command":
                    continue
                cmd = h.get("command", "")
                yield event, matcher, cmd


def collect_registrations():
    """Returns (rows, parse_errors).

    rows: list of dicts {settings, event, matcher, raw, path (abs Path or None)}.
    parse_errors: list of (label, path, error-string) for unparseable settings.
    """
    rows = []
    parse_errors = []
    for label, sfile in SETTINGS_FILES:
        if not sfile.exists():
            parse_errors.append((label, str(sfile), "settings file not found"))
            continue
        try:
            data = json.loads(sfile.read_text(encoding="utf-8"))
        except Exception as e:
            parse_errors.append((label, str(sfile), f"JSON parse error: {e}"))
            continue
        # The project dir for a settings file is its .claude/ parent's parent:
        # <project>/.claude/settings.json -> <project>. That is what
        # ${CLAUDE_PROJECT_DIR} expands to when a session launches there.
        project_dir = sfile.resolve().parent.parent
        for event, matcher, cmd in _iter_registrations(data):
            raw = _extract_py_path(cmd)
            path = _expand(raw, project_dir) if raw else None
            rows.append({
                "settings": label,
                "event": event,
                "matcher": matcher,
                "raw": raw,
                "command": cmd,
                "path": path,
            })
    return rows, parse_errors


def classify(path: Path) -> tuple[str, str]:
    """Return (status, detail) for a registered hook path."""
    if path is None:
        return ("UNKNOWN", "could not extract a .py path from the command string")
    if not path.exists():
        return ("MISSING", "registered but file does not exist")
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as e:
        return ("BROKEN", f"does not compile: {str(e).splitlines()[0]}")
    except Exception as e:
        return ("BROKEN", f"compile error: {e}")
    return ("OK", "exists + compiles")


def find_orphans(referenced: set[Path]):
    """Every *.py in the hook dirs not in the referenced set -> orphan."""
    orphans = []
    for d in HOOK_DIRS:
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.py")):
            fp = Path(os.path.normpath(str(f.resolve())))
            if fp not in referenced:
                orphans.append(fp)
    return orphans


def _session_anchor_mtime():
    """mtime of this session's intent anchor, or None if unresolvable."""
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    if len(sid) < 8:
        return None
    sid8 = sid[:8]
    intent_dir = ROOT / ".claude" / "intent"
    if not intent_dir.is_dir():
        return None
    matches = list(intent_dir.glob(f"*-{sid8}.txt"))
    if not matches:
        return None
    # Earliest anchor mtime is the best proxy for session start.
    return min(m.stat().st_mtime for m in matches)


def find_inert_this_session(rows):
    """Best-effort: registered hooks modified after this session's anchor mtime.

    Returns (list_of_paths, anchor_mtime) or ([], None) when unresolvable.
    """
    anchor = _session_anchor_mtime()
    if anchor is None:
        return ([], None)
    inert = []
    seen = set()
    for r in rows:
        p = r["path"]
        if p is None or not p.exists():
            continue
        if p in seen:
            continue
        seen.add(p)
        if p.stat().st_mtime > anchor:
            inert.append(p)
    return (inert, anchor)


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(p)


def run():
    rows, parse_errors = collect_registrations()

    # Classify each registration.
    referenced = set()
    for r in rows:
        if r["path"] is not None:
            referenced.add(Path(os.path.normpath(str(r["path"].resolve()
                          if r["path"].exists() else r["path"]))))
        status, detail = classify(r["path"])
        r["status"] = status
        r["detail"] = detail

    orphans = find_orphans(referenced)
    inert, anchor = find_inert_this_session(rows)
    inert_set = {Path(os.path.normpath(str(p))) for p in inert}

    fails = [r for r in rows
             if r["status"] in ("MISSING", "BROKEN", "UNKNOWN")] + \
            [{"settings": lbl, "event": "-", "matcher": "-", "raw": pth,
              "path": None, "status": "BROKEN", "detail": err}
             for (lbl, pth, err) in parse_errors]

    failed = bool(fails)
    return {
        "rows": rows,
        "parse_errors": parse_errors,
        "orphans": orphans,
        "inert": inert,
        "inert_set": inert_set,
        "anchor": anchor,
        "failed": failed,
    }


def print_report(result):
    rows = result["rows"]
    parse_errors = result["parse_errors"]
    orphans = result["orphans"]
    inert_set = result["inert_set"]

    if parse_errors:
        print("Settings parse errors:")
        for lbl, pth, err in parse_errors:
            print(f"  [FAIL] {lbl}: {err}  ({pth})")
        print()

    # Table.
    print(f"{'STATUS':<8} {'SETTINGS':<9} {'EVENT':<16} {'HOOK':<42} MATCHER")
    print("-" * 100)
    for r in sorted(rows, key=lambda x: (x["settings"], x["event"], x["raw"] or "")):
        hook = _rel(r["path"]) if r["path"] is not None else (r["raw"] or "<unparsed>")
        flag = ""
        if r["path"] is not None and Path(os.path.normpath(str(r["path"]))) in inert_set:
            flag = "  <- INERT-THIS-SESSION (modified after session start)"
        print(f"{r['status']:<8} {r['settings']:<9} {r['event']:<16} "
              f"{hook:<42} {r['matcher']}{flag}")

    # Orphans.
    if orphans:
        print("\nOrphans (present on disk, not registered in any settings file -- "
              "WARN, not a failure; may be helpers/dormant by design):")
        for o in orphans:
            print(f"  [WARN] ORPHAN  {_rel(o)}")

    # Inert-this-session.
    if result["anchor"] is None:
        # Silent skip per spec -- one quiet line so the reader knows it ran.
        print("\n(inert-this-session check skipped: session anchor unresolved)")
    elif result["inert"]:
        print("\nPossibly inert THIS session (mtime newer than session anchor -- "
              "re-verify from a fresh session):")
        for p in result["inert"]:
            print(f"  [WARN] INERT   {_rel(p)}")

    # Summary.
    n = len(rows)
    n_ok = sum(1 for r in rows if r["status"] == "OK")
    n_missing = sum(1 for r in rows if r["status"] == "MISSING")
    n_broken = sum(1 for r in rows if r["status"] == "BROKEN")
    n_unknown = sum(1 for r in rows if r["status"] == "UNKNOWN")
    print(f"\n{n_ok}/{n} registered hooks OK"
          f" | MISSING={n_missing} BROKEN={n_broken} UNKNOWN={n_unknown}"
          f" | orphans={len(orphans)} inert-this-session={len(result['inert'])}"
          f" | parse-errors={len(parse_errors)}")

    if result["failed"]:
        sys.stderr.write("\n" + BANNER + "\n")
        return 1
    print("\nAll registered hooks present + loadable. (Orphan/inert warnings, if "
          "any, do not fail the check.)")
    return 0


def print_json(result):
    out = {
        "failed": result["failed"],
        "hooks": [
            {"settings": r["settings"], "event": r["event"], "matcher": r["matcher"],
             "path": _rel(r["path"]) if r["path"] is not None else None,
             "raw": r["raw"], "status": r["status"], "detail": r["detail"]}
            for r in result["rows"]
        ],
        "parse_errors": [
            {"settings": lbl, "path": pth, "error": err}
            for (lbl, pth, err) in result["parse_errors"]
        ],
        "orphans": [_rel(o) for o in result["orphans"]],
        "inert_this_session": [_rel(p) for p in result["inert"]],
        "session_anchor_resolved": result["anchor"] is not None,
    }
    print(json.dumps(out, indent=2))
    return 1 if result["failed"] else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--settings", action="append", default=None,
                    help="override settings file(s) to parse (repeatable). "
                         "Used by the fault-injection self-test.")
    args = ap.parse_args(argv)

    if args.settings:
        global SETTINGS_FILES
        SETTINGS_FILES = [(Path(s).stem, Path(s)) for s in args.settings]

    result = run()
    if args.json:
        return print_json(result)
    return print_report(result)


if __name__ == "__main__":
    sys.exit(main())

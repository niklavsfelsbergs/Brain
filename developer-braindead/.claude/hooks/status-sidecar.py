#!/usr/bin/env python3
# Terminal switchboard status sidecar (D-020).
#
# Writes ~/.claude/status/<sid8>.json on every UserPromptSubmit, PreToolUse,
# PostToolUse, Stop, and SessionEnd. The file records the session's current
# state (working / waiting_for_user / ended) so an aggregator view can show
# which terminals are idle, working, or parked on a Stop waiting for the
# principal.
#
# Idle is *not* stamped by this writer — readers derive it from
# `state == "waiting_for_user" AND now - last_event_ts > 5 min`. The hook
# doesn't fire while idle, so writer-side stamping would require either
# polling or a timer.
#
# Never fails the tool call — any error is swallowed to stderr.
#
# Sibling of emit-event.py. Kept separate so visualizer logic and switchboard
# logic have isolated failure modes; both register independently in
# brain/.claude/settings.json.

import json
import os
import sys
import time
from pathlib import Path

# User-global so a single switchboard view sees every Claude Code session on
# the machine, regardless of which repo opened them. See D-020 §"The contract"
# for why per-project was rejected.
STATUS_DIR = Path.home() / ".claude" / "status"
STATUS_ARCHIVE_DIR = STATUS_DIR / "archive"

# Phase 2 (D-020): the browser-served visualizer can't reach STATUS_DIR
# directly (file:// + served-tree sandboxing), so the sidecar mirrors a
# manifest snapshot into the viz dir on every fire. The browser fetches one
# file at a known relative path; no custom server or symlink needed.
#
# HERE = .../brain/developer-braindead/.claude/hooks/status-sidecar.py
# HERE.parent.parent.parent = .../brain/developer-braindead/
# We derive the viz dir from the script's own location rather than the
# session's CLAUDE_PROJECT_DIR — the hook is registered under brain, so the
# brain-local viz path is always the right mirror target regardless of which
# repo the session was opened in.
HERE = Path(__file__).resolve()
DEV_BRAIN = HERE.parent.parent.parent
VIZ_DIR = DEV_BRAIN / "experiments" / "visualizer"
MANIFEST_PATH = VIZ_DIR / "state-switchboard.json"
INSTANCES_PATH = VIZ_DIR / "state-instances.json"

# Same intent length cap as the visualizer hook so a sidebar can render
# sidecar intent inline without re-truncating.
INTENT_MAX_LEN = 100

# Reader-derives-idle threshold — 5 min matches the visualizer despawn timer.
# Carried here only for documentation; the writer never reads it.
# IDLE_SEC = 300

# Sweeper threshold — entries older than this move to archive/ on the next
# hook fire from any session. 24h gives plenty of room for slow-cadence
# sessions while keeping the active list scannable.
STALE_SEC = 24 * 60 * 60

# Hook events we care about, mapped to the state they imply. Anything not in
# this map is ignored — the script exits silently.
EVENT_STATE = {
    "UserPromptSubmit": "working",
    "PreToolUse": "working",
    "PostToolUse": "working",
    "Stop": "waiting_for_user",
    "SessionEnd": "ended",
}


def _project_dir() -> Path | None:
    """Returns the project root from CLAUDE_PROJECT_DIR (set by Claude Code
    for every hook invocation). None if unset — without it we can't find the
    intent files."""
    p = os.environ.get("CLAUDE_PROJECT_DIR")
    if not p:
        return None
    try:
        return Path(p).resolve()
    except Exception:
        return None


def _detect_actor(project_dir: Path | None, sid8: str) -> tuple[str, str]:
    """Look for <project_dir>/.claude/intent/<actor>-<sid8>.txt. Returns
    (actor, intent_first_line). Falls back to ("unknown", "") when no
    per-session intent file exists yet — early in a session the sidecar may
    fire before the agent has written intent. The next event updates the
    status file with the resolved actor.

    Scans the intent dir for any `*-<sid8>.txt` rather than enumerating known
    actor names. Avoids the hand-sync drift hazard with emit-event.py's roster
    when new players land. If exactly one file matches, the prefix is the
    actor name. Multiple matches is anomalous (a session can only be one
    actor at a time) — return unknown and let the next event re-detect."""
    if not project_dir:
        return ("unknown", "")
    intent_dir = project_dir / ".claude" / "intent"
    if not intent_dir.exists():
        return ("unknown", "")
    matches: list[tuple[str, Path]] = []
    try:
        for p in intent_dir.glob(f"*-{sid8}.txt"):
            if not p.is_file():
                continue
            name = p.stem
            if not name.endswith(f"-{sid8}"):
                continue
            actor = name[:-(len(sid8) + 1)]
            if actor:
                matches.append((actor, p))
    except Exception:
        return ("unknown", "")
    if len(matches) != 1:
        return ("unknown", "")
    actor, p = matches[0]
    try:
        raw = p.read_text(encoding="utf-8").strip()
    except Exception:
        raw = ""
    first = raw.splitlines()[0].strip()[:INTENT_MAX_LEN] if raw else ""
    return (actor, first)


def _detect_instance(actor: str, session_id: str) -> int:
    """S033 finding #2: read the visualizer's state-instances.json to surface
    the real instance number in the switchboard manifest. The previous
    behavior — `prev.get("instance") or 1` — meant two parallel Braindead
    sessions both rendered as 'Braindead' in the sidebar (instance 1) with
    no way to distinguish them.

    Returns 1 when actor isn't instanced (wisp, guthix, dwarves) or the
    instance map doesn't have this session yet. emit-event.py is the writer;
    this is a read-only consumer."""
    if not actor or actor in ("unknown", "wisp", "guthix"):
        return 1
    try:
        state = json.loads(INSTANCES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return 1
    entry = state.get(actor)
    if not isinstance(entry, dict):
        return 1
    by_id = entry.get("byId") or {}
    v = by_id.get(session_id)
    try:
        return int(v) if v else 1
    except (TypeError, ValueError):
        return 1


def _detect_host() -> str:
    """Best-effort terminal substrate detection from env. Phase 3 will use
    this to pick the focus mechanism. Unknown means "we'll figure it out
    later" — never blocks the status write."""
    if os.environ.get("TERM_PROGRAM") == "vscode" or os.environ.get("VSCODE_PID"):
        return "vscode"
    if os.environ.get("WT_SESSION"):
        return "windows-terminal"
    if os.environ.get("TERM_PROGRAM"):
        return os.environ["TERM_PROGRAM"].lower()
    return "unknown"


def _ppid_chain(start_pid: int) -> list[dict]:
    """Walk the process tree up from start_pid via Windows toolhelp32 snapshot.
    Returns [{"pid": N, "name": "exe.exe"}, ...] in child→ancestor order.
    Called once per session (cached afterwards) so the cost is bounded.

    Why walk here instead of in focus-window.ps1: Claude Code spawns hooks via
    a short-lived wrapper (cmd.exe / similar) whose PID is what os.getppid()
    returns. That wrapper exits seconds after the hook completes, so by the
    time the user clicks the switchboard row, the immediate parent PID points
    nowhere. Capturing the chain now, while every ancestor is still alive,
    lets the focus script skip past dead nodes."""
    chain: list[dict] = []
    try:
        import ctypes
        import ctypes.wintypes as wt

        class PE32(ctypes.Structure):
            _fields_ = [
                ("dwSize", wt.DWORD),
                ("cntUsage", wt.DWORD),
                ("th32ProcessID", wt.DWORD),
                ("th32DefaultHeapID", ctypes.c_void_p),
                ("th32ModuleID", wt.DWORD),
                ("cntThreads", wt.DWORD),
                ("th32ParentProcessID", wt.DWORD),
                ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", wt.DWORD),
                ("szExeFile", ctypes.c_char * 260),
            ]

        TH32CS_SNAPPROCESS = 0x00000002
        kernel32 = ctypes.windll.kernel32
        kernel32.CreateToolhelp32Snapshot.restype = wt.HANDLE
        kernel32.Process32First.argtypes = [wt.HANDLE, ctypes.POINTER(PE32)]
        kernel32.Process32First.restype = wt.BOOL
        kernel32.Process32Next.argtypes = [wt.HANDLE, ctypes.POINTER(PE32)]
        kernel32.Process32Next.restype = wt.BOOL
        kernel32.CloseHandle.argtypes = [wt.HANDLE]

        snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if not snap or snap == wt.HANDLE(-1).value:
            return [{"pid": start_pid, "name": ""}]
        try:
            pe = PE32()
            pe.dwSize = ctypes.sizeof(PE32)
            parent_of: dict[int, int] = {}
            name_of: dict[int, str] = {}
            if kernel32.Process32First(snap, ctypes.byref(pe)):
                while True:
                    parent_of[pe.th32ProcessID] = pe.th32ParentProcessID
                    try:
                        name_of[pe.th32ProcessID] = pe.szExeFile.decode("utf-8", "replace")
                    except Exception:
                        name_of[pe.th32ProcessID] = ""
                    if not kernel32.Process32Next(snap, ctypes.byref(pe)):
                        break
            cur = start_pid
            for _ in range(20):
                chain.append({"pid": cur, "name": name_of.get(cur, "")})
                ppid = parent_of.get(cur)
                if not ppid or ppid == cur:
                    break
                cur = ppid
        finally:
            kernel32.CloseHandle(snap)
    except Exception as e:
        print(f"status-sidecar: ppid chain walk failed: {e}", file=sys.stderr)
        if not chain:
            chain = [{"pid": start_pid, "name": ""}]
    return chain


def _atomic_write_json(path: Path, obj: dict) -> None:
    """Same pattern as emit-event.py's save_json — write to .tmp.<pid>, then
    os.replace onto destination. Crashes leave the previous file intact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _load_existing(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_manifest() -> None:
    """Snapshot live status files into a single manifest at VIZ_DIR. Browser
    polls this one file (fetch is cheap for one file, expensive for a glob).

    Excludes 'ended' entries — the sidebar shows live sessions only. Ended
    sessions are preserved on disk (one per session at STATUS_DIR/<sid8>.json,
    moved to archive/ after STALE_SEC) and can be surfaced via a future
    history view; they don't belong in the live switchboard. S033 finding #9
    aligned this code with the docstring promise.

    Manifest shape:
        {
          "generated_at": <unix-ts>,
          "sessions": [
            { ...same shape as <sid8>.json... },
            ...
          ]
        }

    Errors swallowed; the per-session file write is the load-bearing one,
    not the manifest."""
    try:
        sessions = []
        if STATUS_DIR.exists():
            for p in STATUS_DIR.iterdir():
                if not p.is_file() or p.suffix != ".json":
                    continue
                try:
                    j = json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    continue
                if not isinstance(j, dict):
                    continue
                if j.get("state") == "ended":
                    continue
                sessions.append(j)
        sessions.sort(key=lambda x: x.get("last_event_ts") or 0, reverse=True)
        out = {
            "generated_at": time.time(),
            "sessions": sessions,
        }
        VIZ_DIR.mkdir(parents=True, exist_ok=True)
        tmp = MANIFEST_PATH.with_suffix(MANIFEST_PATH.suffix + f".tmp.{os.getpid()}")
        tmp.write_text(json.dumps(out, indent=2), encoding="utf-8")
        os.replace(tmp, MANIFEST_PATH)
    except Exception as e:
        print(f"status-sidecar: manifest write failed: {e}", file=sys.stderr)


def _sweep_stale_tmp() -> None:
    """Sweep stale `.tmp.<pid>` files in VIZ_DIR and STATUS_DIR. Both this
    sidecar and `emit-event.py` use `path.with_suffix(".tmp.<pid>")` + atomic
    replace; on Windows, `os.replace` occasionally fails (file lock, AV scan,
    concurrent writer) and leaks the tmp file. No cleanup elsewhere — they
    accumulate. Sweep tmps older than 5 minutes; legitimate tmps are at most
    seconds old. Errors are swallowed."""
    cutoff = time.time() - 5 * 60
    for dir_ in (VIZ_DIR, STATUS_DIR):
        try:
            if not dir_.exists():
                continue
            for p in dir_.iterdir():
                if not p.is_file():
                    continue
                # `.tmp.<pid>` lives as path.suffix; e.g. `state.json.tmp.123`
                # → name ends with `.tmp.<digits>` after the canonical suffix.
                if ".tmp." not in p.name:
                    continue
                # Tighten: only sweep files whose name looks like atomic-write
                # leftovers — `<base>.<ext>.tmp.<digits>`.
                stem_parts = p.name.split(".tmp.")
                if len(stem_parts) != 2 or not stem_parts[1].isdigit():
                    continue
                try:
                    if p.stat().st_mtime > cutoff:
                        continue
                    p.unlink()
                except Exception as e:
                    print(f"status-sidecar: tmp sweep failed for {p.name}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"status-sidecar: tmp sweep dir {dir_} failed: {e}", file=sys.stderr)


def _sweep_stale() -> None:
    """Move status files older than STALE_SEC to STATUS_ARCHIVE_DIR. Bounded
    to whatever fits in STATUS_DIR — typically ≤20 files even on a heavy
    multi-session machine. Errors are swallowed; one stale file that can't
    be moved doesn't block this session's write."""
    try:
        if not STATUS_DIR.exists():
            return
        now = time.time()
        for p in STATUS_DIR.iterdir():
            if not p.is_file() or p.suffix != ".json":
                continue
            try:
                age = now - p.stat().st_mtime
            except Exception:
                continue
            if age <= STALE_SEC:
                continue
            STATUS_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            dst = STATUS_ARCHIVE_DIR / p.name
            # Append suffix on collision instead of overwriting — keeps the
            # archive append-only in spirit.
            if dst.exists():
                dst = STATUS_ARCHIVE_DIR / f"{p.stem}.{int(now)}{p.suffix}"
            try:
                p.replace(dst)
            except Exception as e:
                print(f"status-sidecar: sweep move failed for {p.name}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"status-sidecar: sweep failed: {e}", file=sys.stderr)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    hook_event = payload.get("hook_event_name") or ""
    state = EVENT_STATE.get(hook_event)
    if state is None:
        sys.exit(0)

    sid = payload.get("session_id") or os.environ.get("CLAUDE_CODE_SESSION_ID") or ""
    if not isinstance(sid, str) or not sid:
        sys.exit(0)
    sid8 = sid[:8]

    project_dir = _project_dir()
    actor, intent = _detect_actor(project_dir, sid8)

    now_ts = time.time()
    out_path = STATUS_DIR / f"{sid8}.json"
    prev = _load_existing(out_path)

    # Phase 3 (D-020): record the ancestor process chain from the hook's
    # parent up. focus-window.ps1 iterates this chain to find the first live
    # Code.exe with a MainWindowHandle. Cached after the first fire — the
    # chain is stable for the session's lifetime, and the toolhelp32 snapshot
    # is the most expensive thing this script does.
    claude_pid_chain = prev.get("claude_pid_chain")
    if not claude_pid_chain:
        claude_pid_chain = _ppid_chain(os.getppid())
    claude_pid = (claude_pid_chain[0].get("pid") if claude_pid_chain else os.getppid())

    # Intent carry-forward: only inherit prev.intent when prev.actor matches.
    # An unknown actor (early-fire before intent file exists) used to inherit
    # the previous actor's intent, pinning a stale line in the sidebar.
    carry_intent = ""
    if not intent and actor == (prev.get("actor") or ""):
        carry_intent = prev.get("intent") or ""

    # S033 finding #2: pull instance from the visualizer's instance map so the
    # sidebar can disambiguate parallel sessions of the same actor. Once the
    # session has been instance-stamped (any event with `actor` from
    # emit-event.py), the number sticks; previous fires that resolved to 1 get
    # promoted as soon as the map has a real entry.
    instance = _detect_instance(actor, sid) or (prev.get("instance") or 1)

    record = {
        "sid8": sid8,
        "session_id": sid,
        "actor": actor,
        "instance": instance,
        "state": state,
        "last_event_kind": hook_event,
        "last_event_ts": now_ts,
        "started_at": prev.get("started_at") or now_ts,
        "intent": intent or carry_intent,
        "project_dir": str(project_dir) if project_dir else (prev.get("project_dir") or ""),
        "cwd": os.getcwd(),
        "host": prev.get("host") or _detect_host(),
        "claude_pid": claude_pid,
        "claude_pid_chain": claude_pid_chain,
    }

    try:
        _atomic_write_json(out_path, record)
    except Exception as e:
        print(f"status-sidecar: write failed: {e}", file=sys.stderr)

    # Sweep runs after the write so a failure in the sweep can't prevent this
    # session's own status from landing.
    _sweep_stale()
    _sweep_stale_tmp()

    # Manifest mirror runs last — purely a snapshot for the browser; a failure
    # here can't affect the canonical per-session store.
    _write_manifest()

    sys.exit(0)


if __name__ == "__main__":
    main()

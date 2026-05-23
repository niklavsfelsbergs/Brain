#!/usr/bin/env python3
# Visualizer live-mode emitter (D-009).
#
# Fires as PostToolUse on Edit | Write | MultiEdit | NotebookEdit | Read |
# Glob | Grep — classifies the touched path, appends move + log events to
# state.ndjson, coalesces moves via state-actors.json so repeated work in
# the same building doesn't spam moves.
#
# Fires as PreToolUse + PostToolUse on Task — emits spawn-dwarf / despawn-
# dwarf events, parent inferred from the most-recently-active non-wisp
# actor in state.ndjson (falls back to wisp).
#
# Never fails the tool call — any error is swallowed to stderr.

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve()
DEV_BRAIN = HERE.parent.parent.parent          # developer-braindead/
REPO_ROOT = DEV_BRAIN.parent                   # brain/
# S052: visualizer promoted from developer-braindead/experiments/visualizer/
# to switchboard/ at repo root — observability surface for both brains.
# VIZ_DIR name kept for minimum-disruption diff.
VIZ_DIR = REPO_ROOT / "switchboard"
MAP_PATH = VIZ_DIR / "path-map.json"
STATE_PATH = VIZ_DIR / "state.ndjson"
ACTORS_PATH = VIZ_DIR / "state-actors.json"
DWARVES_PATH = VIZ_DIR / "state-dwarves.json"
GNOMES_PATH = VIZ_DIR / "state-gnomes.json"
PENGUINS_PATH = VIZ_DIR / "state-penguins.json"
INSTANCES_PATH = VIZ_DIR / "state-instances.json"

# S052: chat.ndjson is the human-language event stream for the chat panel.
# Append-only NDJSON; one event per line; truncated on growth threshold.
# Lives in the same viz dir as state.ndjson — the http.server serves both;
# migration to brain/switchboard/ happens after a sibling strip pass.
CHAT_PATH = VIZ_DIR / "chat.ndjson"
CHAT_TEXT_MAX = 200
CHAT_SIZE_MAX = 1_000_000     # bytes — truncate when exceeded
CHAT_LINES_MAX = 5000         # lines — truncate when exceeded
CHAT_TAIL_KEEP = 2000         # lines retained on truncate

# D-017: actors that can run as parallel sessions, each getting its own
# visualizer sprite. Sub-agents (dwarves, gnomes) have unique IDs already.
# Wisp is system-voice and conceptually singular. Guthix is bankstanding-deity,
# always solo.
PLAYER_ACTORS = {"jebrim", "zezima"}

# D-019: actors eligible for parallel-instance routing. Player-class plus
# Braindead — multiple dev-brain sessions are now a supported pattern (was
# explicitly deferred in D-017). resolve_instance() and the append()
# instance-stamp gate on this set; visualizer-side spawnPlayerInstance covers
# the same set. wisp and guthix stay excluded — neither forks meaningfully.
INSTANCED_ACTORS = PLAYER_ACTORS | {"braindead"}

# S028: any non-player actor that may carry a per-session intent-file suffix
# (`<actor>-<sid8>.txt`). Players already get suffix stripping; these get it
# too so the hook resolves the bare actor name regardless of which filename
# variant the agent used. Pre-S028 fix: braindead-ed610cbe.txt was being
# treated as a unique actor by the visualizer, so dev-brain bubbles never
# rendered for sessions using the per-session filename pattern.
NON_PLAYER_SUFFIX_ACTORS = {"braindead", "guthix", "wisp"}

# Sub-agent kinds. spawn-time selection from tool_input.subagent_type; tool-call
# attribution from payload.agent_type. Both reach into the same per-kind state
# (id prefix, color palette, event names, chat speaker).
#
# Adding a new kind:
#   - Add an entry below with all six keys; pick a unique id_prefix letter and
#     a fresh state file under VIZ_DIR.
#   - Add matching CSS vars (--<color_prefix>-1..N) in index.html and a sprite
#     spawner (parallel to spawnDwarf / spawnGnome).
#   - Update spawn_kind_from_tool_input to route subagent_type strings to the
#     new kind. Already an "in ROLE_CONFIG" lookup since penguins landed.
#   - Update attribute_to_subagent's agent_type dispatch. Already an
#     "in ROLE_CONFIG" lookup since penguins landed.
#   - Add a COMMS tab + filter + dot CSS for the new speaker (parallel to
#     dwarves/gnomes/penguins blocks in index.html).
ROLE_CONFIG = {
    "dwarf": {
        "id_prefix": "D",
        "state_path": DWARVES_PATH,
        "spawn_event": "spawn-dwarf",
        "despawn_event": "despawn-dwarf",
        "speaker": "dwarves",
        "color_prefix": "dwarf",
        "color_count": 3,
    },
    "gnome": {
        "id_prefix": "G",
        "state_path": GNOMES_PATH,
        "spawn_event": "spawn-gnome",
        "despawn_event": "despawn-gnome",
        "speaker": "gnomes",
        "color_prefix": "gnome",
        "color_count": 3,
    },
    "penguin": {
        "id_prefix": "P",
        "state_path": PENGUINS_PATH,
        "spawn_event": "spawn-penguin",
        "despawn_event": "despawn-penguin",
        "speaker": "penguins",
        "color_prefix": "penguin",
        "color_count": 3,
    },
}

WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Glob", "Grep"}
# D-014: tools that emit chat-side `action` events. Read is intentionally
# omitted — too noisy, sprite movement already shows building shifts.
ACTION_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit", "Bash", "Glob", "Grep"}

INTENT_FRAGMENT = "/.claude/intent/"
INTENT_MAX_LEN = 100             # D-014: was 60, bumped for two-line bubble.

NARRATION_FRAGMENT = "/.claude/narration.txt"
NARRATION_PATH = REPO_ROOT / ".claude" / "narration.txt"
NARRATION_MAX_LEN = 200

ACTION_TARGET_MAX = 80
SUBTASK_MAX_LEN = 80

ACTIVE_MODE_FRAGMENT = "/.claude/active-mode.txt"
ACTIVE_MODE_PATH = REPO_ROOT / ".claude" / "active-mode.txt"
DEV_BRAIN_MODE = "dev-brain"

# S028: Guthix is the bankstanding deity. Appears when the agent writes intent
# to guthix.txt; departs when intent flips back to a player/braindead/wisp or
# the session ends. Session ownership tracked via _guthix_session_id in
# state-actors.json (parallel to braindead's _mode_session_id).
GUTHIX_ACTOR = "guthix"
GUTHIX_DEFAULT_BUILDING = "lorebook-library"

# Claude Code passes a stable UUID per top-level session in every hook payload.
# We stamp it onto each emitted event so the recency walk can distinguish
# parallel sessions sharing this state.ndjson — without this, Bash attribution
# leaks across sessions (whichever session wrote intent most recently wins,
# regardless of which session's tool call is actually firing the hook).
# Set in main(); read by append() and current_main_actor().
_SESSION_ID: str | None = None

# Sidecar writes from Bash (`echo X > .claude/<sidecar>`) need the same special
# handling as Edit/Write tool calls — otherwise the active-mode marker doesn't
# trigger spawn-braindead, intent files don't emit intent events, and the
# narration channel stays silent. Bash isn't a WRITE_TOOL, so handle_write_or_read
# never runs for these; we detect the embedded redirects in the command string
# and dispatch from handle_bash. Patterns are permissive — a false positive
# (e.g., echoing a path string without actually redirecting) at worst fires a
# handler that re-reads the file and finds nothing new. The regex looks for one
# or more '>' followed by optional whitespace + an optional quote + a relative
# or absolute path ending in the sidecar suffix.
BASH_ACTIVE_MODE_RE = re.compile(
    r'>+\s*[\'"]?(?:[\w./\\-]*[\\/])?\.claude[\\/]active-mode\.txt[\'"]?',
    re.IGNORECASE,
)
BASH_NARRATION_RE = re.compile(
    r'>+\s*[\'"]?(?:[\w./\\-]*[\\/])?\.claude[\\/]narration\.txt[\'"]?',
    re.IGNORECASE,
)
BASH_INTENT_RE = re.compile(
    r'>+\s*[\'"]?(?P<path>(?:[\w./\\-]*[\\/])?\.claude[\\/]intent[\\/][\w-]+\.txt)[\'"]?',
    re.IGNORECASE,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except Exception:
        return default


def save_json(path: Path, obj) -> None:
    """B8: atomic write — temp file in the same dir + os.replace. A crash
    mid-write leaves either the old file intact or the new file complete,
    never a truncated middle state. os.replace is atomic on both POSIX and
    Windows (NTFS), unlike rename which fails on Windows if dst exists.

    Note: state.ndjson (append-only via `append`) cannot be made atomic this
    way without rewriting the whole file each tick. Documented as B9 in the
    S021 audit — concurrent appends from parallel tool calls can interleave;
    self-heals on the next non-racing event."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
        tmp.write_text(json.dumps(obj), encoding="utf-8")
        os.replace(tmp, path)
    except Exception as e:
        print(f"emit-event: cannot write {path.name}: {e}", file=sys.stderr)


# D-018: state-actors.json read/write helpers. Player-class actors get a nested
# shape `{ "byId": { "<sessionId>": "<building>" } }` so two parallel Jebrim
# sessions don't trample each other's move-coalescing state. Non-player actors
# (wisp, braindead) and bookkeeping keys (_mode, _mode_session_id) stay flat —
# they're conceptually singular, so per-session keying would just be ceremony.
# Legacy flat entries for player actors are read as session-agnostic fallback;
# the first write under the new shape promotes them. Lossy on rollout (the old
# flat building is dropped on first nested write), but the old shape was racy
# anyway, so any state it held was unreliable.
def get_actor_building(actors: dict, actor: str, session_id: str | None) -> str | None:
    entry = actors.get(actor)
    if entry is None:
        return None
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict) and session_id:
        by_id = entry.get("byId") or {}
        v = by_id.get(session_id)
        if isinstance(v, str):
            return v
    return None


def set_actor_building(actors: dict, actor: str, session_id: str | None, building: str) -> None:
    if actor in INSTANCED_ACTORS and session_id:
        entry = actors.get(actor)
        if not isinstance(entry, dict):
            entry = {"byId": {}}
        by_id = entry.get("byId") or {}
        by_id[session_id] = building
        entry["byId"] = by_id
        actors[actor] = entry
    else:
        actors[actor] = building


def resolve_instance(actor: str, session_id: str | None) -> int:
    """D-017/D-019: maps (actor, session_id) → instance number for instanced
    actors (player-class + braindead per D-019). First-seen session for a
    given actor gets instance 1; subsequent parallel sessions get 2, 3, …
    Non-instanced actors (wisp, guthix, dwarves, gnomes) always return 1 —
    they don't fork into parallel sprites.

    Slot-reclaiming allocation. When a session ends and its byId entry is
    deleted, the slot becomes free. New sessions take the lowest free slot
    in `[1, max(byId.values()) + 1]` rather than monotonically incrementing
    `next` forever. Without this, the visible instance ticker drifts up
    indefinitely (braindead-17 with only four live sessions, observed in
    the wild) and never returns to ·1 ·2 ·3 ·4 as the principal expects.

    `next` is kept as a high-water mark for diagnostics; not load-bearing.

    Persists assignments in state-instances.json so a hook re-invocation in
    the same session lands on the same instance number. Schema:
        { "<actor>": { "next": <int>, "byId": { "<session_id>": <int> } } }
    """
    if not actor or actor not in INSTANCED_ACTORS:
        return 1
    if not session_id:
        return 1
    state = load_json(INSTANCES_PATH, {})
    entry = state.get(actor) or {"next": 1, "byId": {}}
    by_id = entry.get("byId") or {}
    if session_id in by_id:
        return int(by_id[session_id])
    in_use = set()
    for v in by_id.values():
        try:
            in_use.add(int(v))
        except (TypeError, ValueError):
            continue
    n = 1
    while n in in_use:
        n += 1
    by_id[session_id] = n
    entry["byId"] = by_id
    # high-water mark; never decreases, useful for diagnostics
    entry["next"] = max(int(entry.get("next") or 1), n + 1)
    state[actor] = entry
    save_json(INSTANCES_PATH, state)
    return n


def append(event: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if _SESSION_ID and "sessionId" not in event:
        event["sessionId"] = _SESSION_ID
    # D-017/D-019: stamp instance number for instanced actors. Events without
    # an `actor` field, or events for non-instanced actors, skip the stamp —
    # `instance` absent reads as 1 in the visualizer.
    if "instance" not in event:
        actor = event.get("actor") or ""
        if actor in INSTANCED_ACTORS:
            event["instance"] = resolve_instance(actor, event.get("sessionId") or _SESSION_ID)
    with STATE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, separators=(",", ":")) + "\n")


def classify(needle: str, m: dict) -> tuple[str | None, str]:
    s = needle.replace("\\", "/")
    key = "/" + s if not s.startswith("/") else s
    # Append a trailing slash so directory-shaped needles (e.g., "gielinor/meta",
    # or globs like "**/meta") match rules that end with "/". File-shaped
    # needles still match because the building name is mid-path, not terminal.
    if not key.endswith("/"):
        key = key + "/"
    building = None
    for rule in m.get("buildingRules", []):
        if rule["contains"] in key:
            building = rule["building"]
            break
    actor = m.get("defaultActor", "wisp")
    for rule in m.get("actorRules", []):
        if rule["contains"] in key:
            actor = rule["actor"]
            break
    return building, actor


def to_rel(file_path: str) -> str | None:
    try:
        p = Path(file_path).resolve()
        return str(p.relative_to(REPO_ROOT)).replace("\\", "/")
    except Exception:
        return None


def needle_from_payload(tool_name: str, tool_input: dict) -> str | None:
    if tool_name in WRITE_TOOLS:
        fp = tool_input.get("file_path") or tool_input.get("notebook_path")
        return to_rel(fp) if fp else None
    if tool_name == "Read":
        fp = tool_input.get("file_path")
        return to_rel(fp) if fp else None
    if tool_name in ("Glob", "Grep"):
        path = tool_input.get("path")
        if path:
            rel = to_rel(path)
            if rel:
                return rel
        return tool_input.get("pattern") or None
    return None


def _walk_recent_actor(session_id: str | None = None) -> tuple[str | None, str | None]:
    """Pure recency walk over state.ndjson. Returns (actor, building) for the
    most recent non-wisp intent or move within RECENCY_SEC, or (None, None)
    if nothing fresh. No dev-brain override — callers layer that on top per
    their own needs (spawn-parent inference vs. Bash attribution have
    different priorities; see infer_dwarf_parent and current_main_actor).

    When session_id is given, only events stamped with the same sessionId are
    considered — needed for Bash attribution when parallel sessions share this
    state stream. Events written before session_id stamping was added (i.e.
    legacy events without a sessionId field) are ignored under the filter, so
    a session whose events all predate stamping will return (None, None) and
    fall through to the caller's fallback."""
    RECENCY_SEC = 600   # 10 minutes
    try:
        if not STATE_PATH.exists():
            return (None, None)
        lines = STATE_PATH.read_text(encoding="utf-8").splitlines()
    except Exception:
        return (None, None)

    now = datetime.now(timezone.utc)
    intent_actor = None
    move_actor = None
    actors = load_json(ACTORS_PATH, {})

    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if session_id and ev.get("sessionId") != session_id:
            continue
        wt = _parse_iso(ev.get("wallTime", ""))
        if wt is None:
            # Malformed event — skip it; older events may still be in-window.
            continue
        if (now - wt).total_seconds() > RECENCY_SEC:
            # Past the recency window — stop walking; older events are stale.
            break
        t = ev.get("type")
        if t == "intent":
            a = ev.get("actor")
            if a and a != "wisp" and intent_actor is None:
                intent_actor = a
                break   # intent is the strongest signal — take it and stop
        elif t == "move":
            a = ev.get("actor")
            if a and a != "wisp" and move_actor is None:
                ev_sid = ev.get("sessionId") or session_id
                move_actor = (a, ev.get("to") or get_actor_building(actors, a, ev_sid) or "quest-hall")

    if intent_actor:
        return (intent_actor, get_actor_building(actors, intent_actor, session_id) or "quest-hall")
    if move_actor:
        return move_actor
    return (None, None)


def infer_dwarf_parent() -> tuple[str, str]:
    """Parent inference for Task spawn events. Dev-brain short-circuit fires
    FIRST because a dev-brain session spawning a dwarf should always attribute
    parent=Braindead, even if a stale player intent sits inside the recency
    window from a prior gielinor session.

    Session-scoped recency walk avoids cross-session bleed: a Task spawned
    here inherits this hook invocation's sessionId, so the parent must also
    be this session's recent actor."""
    if is_dev_brain_session():
        return ("braindead", "braindead-workshop")
    if is_guthix_session():
        return (GUTHIX_ACTOR, GUTHIX_DEFAULT_BUILDING)
    actor, at = _walk_recent_actor(session_id=_SESSION_ID)
    if actor:
        return (actor, at or "quest-hall")
    disk_actor = _session_actor_from_disk()
    if disk_actor:
        return (disk_actor, "quest-hall")
    actors = load_json(ACTORS_PATH, {})
    return ("wisp", get_actor_building(actors, "wisp", _SESSION_ID) or "quest-hall")


def _parse_iso(s: str):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _is_stale_braindead_marker() -> bool:
    """B4: detect when state-actors.json._mode='dev-brain' is leftover from a
    prior session that never wrote 'unscoped' to active-mode.txt on close.
    Walks state.ndjson backward; returns True if the latest spawn-braindead
    is older than FRESH_SEC (i.e., no fresh activity to balance against).
    Used to suppress misleading 'Braindead packs up and leaves' chat lines
    when the despawn is actually closing out a stale prior-session spawn."""
    FRESH_SEC = 300  # 5 minutes — sessions don't pause that long mid-flow.
    try:
        if not STATE_PATH.exists():
            return True
        now = datetime.now(timezone.utc)
        # Bound the walk: stop scanning past STALE_SEC ago (1h) to keep cost
        # bounded on long-lived stream files.
        STALE_SEC = 3600
        for line in reversed(STATE_PATH.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            wt = _parse_iso(ev.get("wallTime", ""))
            if wt is None:
                continue
            age = (now - wt).total_seconds()
            if age > STALE_SEC:
                break
            t = ev.get("type")
            if t == "spawn-braindead":
                return age > FRESH_SEC
            if t == "despawn-braindead":
                # Latest braindead event is a despawn — anything before it is
                # already balanced. The current _mode=dev-brain must be stale.
                return True
        return True
    except Exception:
        return True


def gc_stale_subagents(kind: str) -> None:
    """B7: walk role-state file; emit despawn events for spawns whose
    PreToolUse landed but PostToolUse never did (Claude Code crash, network
    error, parent kill). Threshold STALE_SEC ago. Called from handle_task_pre
    / handle_task_post so live sub-agent activity is the trigger; bounds
    overhead without needing a session-boundary signal.

    D-018: walks every session's substate under `bySession`. A long-lived
    parallel session whose dwarves never returned cleanly still gets its
    leaked entries swept here even when this hook fires under a different
    session."""
    STALE_SEC = 3600     # foreground: 1 hour (PostToolUse never landed)
    IDLE_BG_SEC = 300    # background: 5 min since last sub-agent activity
    cfg = ROLE_CONFIG[kind]
    st = load_json(cfg["state_path"], _subagent_default())
    by_session = st.get("bySession") or {}
    if not by_session:
        return
    now = datetime.now(timezone.utc)
    dirty = False
    wall = now_iso()
    for sid, sub in list(by_session.items()):
        if not isinstance(sub, dict):
            continue
        by_tui = sub.get("byToolUseId") or {}
        if not by_tui:
            continue
        stale = []
        for tui, entry in list(by_tui.items()):
            spawned = _parse_iso(entry.get("spawnedAt", ""))
            active = _parse_iso(entry.get("lastActiveAt", ""))
            # Entries without spawnedAt predate the B7 fix; treat them as fresh
            # on this pass (they'll be cleaned up next time once a fresh spawn
            # updates the file format, or by hand). Avoids a one-time GC storm.
            if not spawned:
                continue
            # S028 follow-up: background tasks use a shorter idle threshold
            # against last sub-agent activity. Foreground keeps the 1h
            # never-landed-Post fallback. Use the freshest of (spawnedAt,
            # lastActiveAt) so an active sub-agent stays alive regardless of
            # how long ago it was spawned.
            ref = active if (active and active > spawned) else spawned
            background = bool(entry.get("background"))
            threshold = IDLE_BG_SEC if background else STALE_SEC
            if (now - ref).total_seconds() > threshold:
                stale.append((tui, entry, background))
        if not stale:
            continue
        by_agent = sub.setdefault("byAgentId", {})
        pending = sub.setdefault("pendingAgentBind", [])
        for tui, entry, background in stale:
            by_tui.pop(tui, None)
            for aid, t in list(by_agent.items()):
                if t == tui:
                    by_agent.pop(aid, None)
            if tui in pending:
                pending.remove(tui)
            append({
                "wallTime": wall, "source": "hook",
                "type": cfg["despawn_event"],
                "id": entry["id"],
            })
            reason = (
                f"idle {IDLE_BG_SEC // 60}m (background)"
                if background
                else f"no PostToolUse, GC after {STALE_SEC // 60}m"
            )
            append({
                "wallTime": wall, "source": "hook",
                "type": "log",
                "msg": f"* {entry['id']} timed out ({reason})",
                "cls": "system",
                "speaker": cfg["speaker"],
            })
            print(
                f"emit-event: GC stale {kind} {entry['id']} "
                f"(tool_use_id={tui}, session={sid}, background={background})",
                file=sys.stderr,
            )
        dirty = True
    if dirty:
        save_json(cfg["state_path"], st)


def read_active_mode() -> str:
    """Returns the first line of active-mode.txt, lowercased+stripped, or ''."""
    try:
        if not ACTIVE_MODE_PATH.exists():
            return ""
        return ACTIVE_MODE_PATH.read_text(encoding="utf-8").strip().splitlines()[0].lower() if ACTIVE_MODE_PATH.stat().st_size else ""
    except Exception:
        return ""


def is_dev_brain_session() -> bool:
    """True only when active-mode.txt says dev-brain AND the session that set
    the marker is this hook invocation's session. Without the session_id gate,
    a parallel non-dev-brain session would see the shared marker and fire the
    dev-brain override on its own events — re-attributing them to braindead.
    See [[S023 visualizer attribution]] for the failure mode."""
    if read_active_mode() != DEV_BRAIN_MODE:
        return False
    if not _SESSION_ID:
        return False
    actors = load_json(ACTORS_PATH, {})
    return actors.get("_mode_session_id") == _SESSION_ID


def is_guthix_session() -> bool:
    """S028: True when this hook invocation's session is currently bankstanding
    (intent file is guthix.txt). Session-gated like is_dev_brain_session — a
    parallel non-bankstanding session sharing this state.ndjson must not
    re-attribute its own work to Guthix."""
    if not _SESSION_ID:
        return False
    actors = load_json(ACTORS_PATH, {})
    return actors.get("_guthix_session_id") == _SESSION_ID


def _session_actor_from_disk() -> str | None:
    """S028 follow-up: recover the session's actor by inspecting
    `.claude/intent/<actor>-<sid8>.txt` on disk. The intent file outlives
    state.ndjson, so this survives a live-mode truncation/reset cycle.

    Returns the actor name if exactly one per-session intent file matches
    this session's sid8 prefix; None otherwise. A session can only be in one
    mode at a time, so multiple matches is anomalous — fall through to other
    fallbacks rather than guess.

    Sessions writing to bare `<actor>.txt` (no session suffix) are not
    detectable here — bare files have no ownership and could be shared across
    parallel sessions. The protocol mandates per-session naming for that
    reason; see `gielinor/meta/communication-protocol.md`."""
    if not _SESSION_ID:
        return None
    short = _SESSION_ID[:8]
    intent_dir = REPO_ROOT / ".claude" / "intent"
    if not intent_dir.exists():
        return None
    candidates = PLAYER_ACTORS | NON_PLAYER_SUFFIX_ACTORS | {GUTHIX_ACTOR}
    matches = []
    for actor in candidates:
        if (intent_dir / f"{actor}-{short}.txt").exists():
            matches.append(actor)
    if len(matches) == 1:
        return matches[0]
    return None


def handle_active_mode_write(needle: str) -> bool:
    """If needle is .claude/active-mode.txt, detect mode transition and emit
    spawn-braindead / despawn-braindead as needed. Returns True if handled."""
    s = needle.replace("\\", "/")
    key = "/" + s if not s.startswith("/") else s
    if ACTIVE_MODE_FRAGMENT not in key:
        return False
    new_mode = read_active_mode()
    actors = load_json(ACTORS_PATH, {})
    prev_mode = (actors.get("_mode") or "").lower()
    if new_mode == prev_mode:
        # No mode transition, but stamp _mode_session_id if missing or stale
        # so the dev-brain override knows whose marker this is. Without this,
        # a session whose mode was set under the pre-session-id code would
        # never get its own override to fire.
        if new_mode == DEV_BRAIN_MODE and _SESSION_ID \
                and actors.get("_mode_session_id") != _SESSION_ID:
            actors["_mode_session_id"] = _SESSION_ID
            save_json(ACTORS_PATH, actors)
        return True
    wall = now_iso()
    # B14: append spawn/despawn events BEFORE persisting _mode. If append
    # fails, _mode hasn't been recorded, so the next active-mode write will
    # retry rather than silently leaving Braindead un-spawned for the rest
    # of the session (the `_mode == new_mode` short-circuit above).
    if new_mode == DEV_BRAIN_MODE and prev_mode != DEV_BRAIN_MODE:
        append({
            "wallTime": wall, "source": "hook",
            "type": "spawn-braindead",
            "at": "braindead-workshop",
        })
        append({
            "wallTime": wall, "source": "hook",
            "type": "log",
            "msg": "Braindead arrives at the workshop",
            "cls": "session-start",
            "speaker": "braindead",
        })
    elif prev_mode == DEV_BRAIN_MODE and new_mode != DEV_BRAIN_MODE:
        stale = _is_stale_braindead_marker()
        append({
            "wallTime": wall, "source": "hook",
            "type": "despawn-braindead",
        })
        if stale:
            # B4: this despawn is closing out a stale _mode marker from a
            # prior session, not a current Braindead presence. Emit a
            # system-voice narrate instead of the Braindead chat line so the
            # new session's COMMS isn't polluted with a misleading farewell.
            append({
                "wallTime": wall, "source": "hook",
                "type": "narrate",
                "text": "Cleared stale dev-brain marker from prior session",
            })
        else:
            append({
                "wallTime": wall, "source": "hook",
                "type": "log",
                "msg": "Braindead packs up and leaves",
                "cls": "session-start",
                "speaker": "braindead",
            })
    actors["_mode"] = new_mode
    if new_mode == DEV_BRAIN_MODE and _SESSION_ID:
        actors["_mode_session_id"] = _SESSION_ID
    elif new_mode != DEV_BRAIN_MODE:
        actors.pop("_mode_session_id", None)
    save_json(ACTORS_PATH, actors)
    return True


def handle_narration_write(needle: str) -> bool:
    """If needle is .claude/narration.txt, read the file and emit a single
    `narrate` event (system-voice broader-scope commentary, D-014). Returns
    True if handled (consumes the write so the normal path-classify flow
    skips it). Empty file → no event, still consume."""
    s = needle.replace("\\", "/")
    key = "/" + s if not s.startswith("/") else s
    if NARRATION_FRAGMENT not in key:
        return False
    text = ""
    try:
        if NARRATION_PATH.exists() and NARRATION_PATH.stat().st_size:
            text = NARRATION_PATH.read_text(encoding="utf-8").strip().splitlines()[0]
    except Exception:
        text = ""
    text = text[:NARRATION_MAX_LEN]
    if text:
        append({
            "wallTime": now_iso(), "source": "hook",
            "type": "narrate",
            "text": text,
        })
    return True


def _pretty_target_path(fp: str) -> str:
    if not fp:
        return ""
    rel = to_rel(fp)
    if rel:
        return rel[:ACTION_TARGET_MAX]
    return Path(fp).name[:ACTION_TARGET_MAX]


# Subtask channel (S028). The visualizer has two pre-existing channels feeding
# the COMMS panel — intent (agent voice, slow, scope) and action (hook voice,
# fast, raw tool call). The middle band is missing: when the agent doesn't
# update intent for a stretch, the bubble freezes even while tool calls fire
# underneath. `subtask` fills that gap — hook-authored, natural-language,
# medium-cadence. Each tool call gets one subtask phrase synthesized from the
# tool name + args; the visualizer renders it as a muted secondary line under
# the intent.
#
# Debouncing lives in the visualizer (long-lived JS, real in-memory state) not
# the hook (fresh process per tool call). Hook emits every call at full
# fidelity; the visualizer drops bursts.

BASH_SUBTASK_TABLE: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^\s*git\s+(status|diff|log|show|blame)\b"), "checking git {verb}"),
    (re.compile(r"^\s*git\s+add\b"),    "staging changes"),
    (re.compile(r"^\s*git\s+commit\b"), "committing changes"),
    (re.compile(r"^\s*git\s+push\b"),   "pushing changes"),
    (re.compile(r"^\s*git\s+(pull|fetch)\b"), "{verb}ing from remote"),
    (re.compile(r"^\s*git\b"),          "running git"),
    (re.compile(r"^\s*(ls|cd|pwd|mkdir|cp|mv|rm)\b"), "navigating files"),
    (re.compile(r"^\s*(cat|head|tail|less|more)\b"), "reading output"),
    (re.compile(r"^\s*(python|python3|node|npm|yarn|pnpm|rg|jq|curl|wget|gh)\b"),
        "running {tool}"),
    # `echo ... > .claude/<sidecar>` is the only echo-pattern we want to
    # surface as "writing sidecar." Plain `echo "hello"` should fall through to
    # the generic phrase — labelling every echo as a sidecar write was
    # misleading.
    (re.compile(r"^\s*echo\b[^|]*?>+\s*[\'\"]?(?:[\w./\\-]*[\\/])?\.claude[\\/]"), "writing sidecar"),
]


def bash_subtask(cmd: str) -> str:
    """Pattern-match the first verb of a Bash command to a natural-language
    micro-step phrase. Falls back to a generic phrase rather than dumping the
    raw command — that's the audit's deferred I12 ("action target
    prettification") landing as foundation work for subtask."""
    if not cmd:
        return ""
    for regex, template in BASH_SUBTASK_TABLE:
        m = regex.search(cmd)
        if not m:
            continue
        if "{verb}" in template:
            return template.format(verb=m.group(1))
        if "{tool}" in template:
            return template.format(tool=m.group(1))
        return template
    return "running shell command"


def _basename(p: str) -> str:
    if not p:
        return ""
    return Path(p).name or p


def _hostname(url: str) -> str:
    if not url:
        return ""
    try:
        from urllib.parse import urlparse
        h = urlparse(url).hostname or ""
        return h
    except Exception:
        return ""


def subtask_for(tool_name: str, tool_input: dict) -> str:
    """Synthesize a natural-language micro-step phrase from a tool call.
    Returns '' when no useful phrase can be made."""
    if tool_name == "Read":
        return f"reading {_basename(tool_input.get('file_path') or '')}".strip()
    if tool_name == "Edit":
        return f"editing {_basename(tool_input.get('file_path') or '')}".strip()
    if tool_name == "Write":
        return f"writing {_basename(tool_input.get('file_path') or '')}".strip()
    if tool_name == "MultiEdit":
        return f"editing {_basename(tool_input.get('file_path') or '')}".strip()
    if tool_name == "NotebookEdit":
        return f"editing {_basename(tool_input.get('notebook_path') or '')}".strip()
    if tool_name == "Glob":
        pat = (tool_input.get("pattern") or "").strip()
        return f"globbing `{pat}`" if pat else "globbing"
    if tool_name == "Grep":
        pat = (tool_input.get("pattern") or "").strip()
        return f"searching for `{pat}`" if pat else "searching"
    if tool_name == "Bash":
        return bash_subtask((tool_input.get("command") or "").strip())
    if tool_name in ("Task", "Agent"):
        desc = (tool_input.get("description") or "").strip()
        return f"spawning dwarf — {desc}" if desc else "spawning dwarf"
    if tool_name == "WebFetch":
        host = _hostname(tool_input.get("url") or "")
        return f"fetching {host}" if host else "fetching a page"
    if tool_name == "WebSearch":
        q = (tool_input.get("query") or "").strip()
        return f"searching: {q}" if q else "searching the web"
    return ""


# S052: chat.ndjson human-language emitter.
#
# The hook is a fresh process per tool call, so we can't keep an in-memory
# debounce dict across invocations the way the visualizer JS can. The simpler
# implementation specified in the task brief — "let the same call land twice
# across rapid invocations, log inflation is mild" — is what we do. Truncate
# pass at write time keeps the file bounded regardless.
def _humanize_tool_call(tool_name: str, tool_input: dict) -> str:
    """Synthesize a ≤200-char human-language line for a tool call. Returns ''
    when nothing useful can be said (caller skips the emit)."""
    if not tool_name:
        return ""
    if tool_name in ("Edit", "MultiEdit"):
        fp = tool_input.get("file_path") or ""
        return f"Editing {_basename(fp)}".strip() if fp else "Editing a file"
    if tool_name == "Write":
        fp = tool_input.get("file_path") or ""
        return f"Writing {_basename(fp)}".strip() if fp else "Writing a file"
    if tool_name == "NotebookEdit":
        fp = tool_input.get("notebook_path") or ""
        return f"Editing {_basename(fp)}".strip() if fp else "Editing a notebook"
    if tool_name == "Read":
        fp = tool_input.get("file_path") or ""
        return f"Reading {_basename(fp)}".strip() if fp else "Reading a file"
    if tool_name == "Bash":
        cmd = (tool_input.get("command") or "").strip()
        if not cmd:
            return "Running a shell command"
        # Recognized prefixes get nicer phrasing.
        head = cmd[:80].lower()
        if head.startswith("git status"):
            return "Checking git status"
        if head.startswith("git log"):
            return "Reviewing git history"
        if head.startswith("git diff"):
            return "Reviewing diff"
        if head.startswith("git commit"):
            return "Committing changes"
        if head.startswith("git mv"):
            return "Moving files (git mv)"
        if "python -m http.server" in cmd:
            return "Starting local web server"
        return f"Running: {cmd[:60]}"
    if tool_name == "Grep":
        pat = (tool_input.get("pattern") or "").strip()
        if not pat:
            return "Searching"
        return f"Searching for '{pat[:40]}'"
    if tool_name == "Glob":
        pat = (tool_input.get("pattern") or "").strip()
        if not pat:
            return "Looking for files"
        return f"Looking for files matching {pat}"
    if tool_name in ("Task", "Agent"):
        sub_type = (tool_input.get("subagent_type") or "dwarf").strip() or "dwarf"
        desc = (tool_input.get("description") or "").strip()
        if desc:
            return f"Spawning {sub_type}: {desc[:80]}"
        return f"Spawning {sub_type}"
    return f"Using {tool_name}"


def _emit_chat_line(actor: str, sid8: str, kind: str, text: str,
                    instance: int | None = None) -> None:
    """Append one NDJSON line to chat.ndjson. Atomic at the OS level via
    append-mode write; same approach state.ndjson uses (B9 — interleavable
    appends from parallel sessions, self-heals)."""
    if not text:
        return
    text = text[:CHAT_TEXT_MAX]
    event = {
        "ts": time.time(),
        "actor": actor or "wisp",
        "instance": instance,
        "sid8": sid8 or "",
        "kind": kind,
        "text": text,
    }
    try:
        CHAT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CHAT_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, separators=(",", ":")) + "\n")
    except Exception as e:
        print(f"emit-event: chat write failed: {e}", file=sys.stderr)


def emit_chat_action(actor: str, tool_name: str, tool_input: dict) -> None:
    """Append a human-language action line to chat.ndjson for one tool call.
    Skips silently when no useful phrase can be made."""
    text = _humanize_tool_call(tool_name, tool_input)
    if not text:
        return
    sid8 = (_SESSION_ID or "")[:8]
    instance = None
    if actor in INSTANCED_ACTORS and _SESSION_ID:
        try:
            instance = resolve_instance(actor, _SESSION_ID)
        except Exception:
            instance = None
    _emit_chat_line(actor, sid8, "action", text, instance)


def sweep_chat_ndjson() -> None:
    """Truncate chat.ndjson when it exceeds size or line caps. Keeps the tail
    CHAT_TAIL_KEEP lines via atomic rewrite. Cheap no-op on the common path."""
    try:
        if not CHAT_PATH.exists():
            return
        size = CHAT_PATH.stat().st_size
        over_size = size > CHAT_SIZE_MAX
        lines: list[str] | None = None
        if over_size:
            # If we're past size, definitely truncate without counting lines.
            try:
                lines = CHAT_PATH.read_text(encoding="utf-8").splitlines()
            except Exception:
                return
        else:
            # Cheap line count via reading; only matters when size is in range.
            # Skip the read entirely if file is tiny.
            if size < 200_000:
                return
            try:
                lines = CHAT_PATH.read_text(encoding="utf-8").splitlines()
            except Exception:
                return
            if len(lines) <= CHAT_LINES_MAX:
                return
        if lines is None:
            return
        tail = lines[-CHAT_TAIL_KEEP:]
        tmp = CHAT_PATH.with_suffix(CHAT_PATH.suffix + f".tmp.{os.getpid()}")
        tmp.write_text("\n".join(tail) + "\n", encoding="utf-8")
        os.replace(tmp, CHAT_PATH)
    except Exception as e:
        print(f"emit-event: chat sweep failed: {e}", file=sys.stderr)


def emit_subtask(wall: str, actor: str, tool_name: str, tool_input: dict) -> None:
    """Append a `subtask` event to the stream. No-op when no actor or no
    phrase can be synthesized."""
    if not actor:
        return
    text = subtask_for(tool_name, tool_input)
    if not text:
        return
    append({
        "wallTime": wall, "source": "hook",
        "type": "subtask",
        "actor": actor,
        "text": text[:SUBTASK_MAX_LEN],
    })


def action_verb_and_target(tool_name: str, tool_input: dict) -> tuple[str, str]:
    """D-014: map a tool call to a (verb, target) pair for the `action` event.
    Returns ("", "") for tools that should not emit (e.g., Read)."""
    if tool_name == "Edit":
        return ("editing", _pretty_target_path(tool_input.get("file_path") or ""))
    if tool_name == "Write":
        return ("writing", _pretty_target_path(tool_input.get("file_path") or ""))
    if tool_name == "MultiEdit":
        return ("editing", _pretty_target_path(tool_input.get("file_path") or ""))
    if tool_name == "NotebookEdit":
        return ("editing", _pretty_target_path(tool_input.get("notebook_path") or ""))
    if tool_name == "Bash":
        cmd = (tool_input.get("command") or "").strip()
        return ("running", cmd[:ACTION_TARGET_MAX])
    if tool_name == "Glob":
        return ("globbing", (tool_input.get("pattern") or "")[:ACTION_TARGET_MAX])
    if tool_name == "Grep":
        return ("searching", (tool_input.get("pattern") or "")[:ACTION_TARGET_MAX])
    return ("", "")


def current_main_actor() -> str:
    """Best-effort main-thread actor for events without a path (e.g., Bash).

    Walks events stamped with this hook invocation's sessionId — the only
    session-local signal we have, since state.ndjson and active-mode.txt are
    both shared across parallel Claude sessions. When the session has at
    least one prior intent/move stamped, that's the answer.

    Falls back to active-mode.txt only when the recency walk finds nothing
    session-tagged — covers the genuinely-first-event-of-session case where
    a dev-brain session's opening Bash fires before any intent has landed.
    Even then, accept that this can be wrong if a parallel non-dev-brain
    session set the marker last; the fallback is best-effort.

    Requires intent narration to be written regularly (per
    `meta/communication-protocol.md`) so the session-filtered walk has
    something to lock onto early in a session."""
    actor, _ = _walk_recent_actor(session_id=_SESSION_ID)
    if actor:
        return actor
    disk_actor = _session_actor_from_disk()
    if disk_actor:
        return disk_actor
    if is_dev_brain_session():
        return "braindead"
    if is_guthix_session():
        return GUTHIX_ACTOR
    return "wisp"


def handle_bash(payload: dict) -> None:
    """D-014: emit an `action` event for Bash (no path → no move).
    Attributes to sub-agent (dwarf or gnome) via agent_id when present, else
    to the current main-thread actor.

    S022 follow-up: also detect sidecar writes embedded in the command
    (`echo X > .claude/active-mode.txt`, intent files, narration) and route
    them through the same handlers Edit/Write would have hit. Without this,
    a respawn ritual that uses Bash echo to set the active-mode marker
    leaves _mode stale in state-actors.json — no spawn-braindead event is
    emitted, narration goes silent, and intent bubbles never appear."""
    tool_input = payload.get("tool_input") or {}
    cmd = tool_input.get("command") or ""

    # Sidecar dispatch runs BEFORE the action event so the resulting
    # spawn-braindead / intent / narrate events appear in the stream in the
    # right order — the Bash action is the "what just happened," and the
    # sidecar events are the consequences the user sees on the map.
    if cmd:
        if BASH_ACTIVE_MODE_RE.search(cmd):
            try:
                handle_active_mode_write(".claude/active-mode.txt")
            except Exception as e:
                print(f"emit-event: bash active-mode dispatch failed: {e}", file=sys.stderr)
        if BASH_NARRATION_RE.search(cmd):
            try:
                handle_narration_write(".claude/narration.txt")
            except Exception as e:
                print(f"emit-event: bash narration dispatch failed: {e}", file=sys.stderr)
        # Dedupe by path — a single command can name the same intent file
        # multiple times (test strings, multi-line scripts); we want one
        # dispatch per path, not one per textual mention.
        intent_paths = {
            m.group("path").replace("\\", "/")
            for m in BASH_INTENT_RE.finditer(cmd)
        }
        for path in intent_paths:
            try:
                # handle_intent_write parses the actor name from the trailing
                # filename, not the leading path.
                handle_intent_write(path)
            except Exception as e:
                print(f"emit-event: bash intent dispatch failed: {e}", file=sys.stderr)

    verb, target = action_verb_and_target("Bash", tool_input)
    if not target:
        return
    sub, _st, _kind = attribute_to_subagent(payload)
    actor = sub["id"] if sub else current_main_actor()
    wall = now_iso()
    append({
        "wallTime": wall, "source": "hook",
        "type": "action",
        "actor": actor,
        "verb": verb,
        "target": target,
    })
    emit_subtask(wall, actor, "Bash", tool_input)
    # S052: chat-side human-language line for the Bash call.
    emit_chat_action(actor, "Bash", tool_input)


def handle_session_end(payload: dict) -> None:
    """D-017: emit despawn-instance events for every player instance bound to
    the ending session. The visualizer uses these for fast cleanup on clean
    exits — the 5-minute idle timer is the safety net for forced kills."""
    sid = payload.get("session_id") or _SESSION_ID
    if not sid:
        return
    # S028: if this session owned Guthix, fade him out cleanly. Without this,
    # a bankstanding session that closes (rather than flipping intent back to
    # a player) leaves the marker stale and the sprite persistent until idle
    # despawn fires.
    actors = load_json(ACTORS_PATH, {})
    if actors.get("_guthix_session_id") == sid:
        wall0 = now_iso()
        append({
            "wallTime": wall0, "source": "hook",
            "type": "despawn-guthix",
        })
        append({
            "wallTime": wall0, "source": "hook",
            "type": "log",
            "msg": "Guthix recedes — the brain is tended",
            "cls": "session-start",
            "speaker": "guthix",
        })
        actors.pop("_guthix_session_id", None)
        save_json(ACTORS_PATH, actors)
    state = load_json(INSTANCES_PATH, {})
    wall = now_iso()
    matcher = payload.get("matcher") or payload.get("reason") or "other"
    for actor, entry in (state or {}).items():
        if actor not in INSTANCED_ACTORS:
            continue
        by_id = (entry or {}).get("byId") or {}
        if sid not in by_id:
            continue
        instance = int(by_id[sid])
        append({
            "wallTime": wall, "source": "hook",
            "type": "despawn-instance",
            "actor": actor,
            "instance": instance,
            "reason": str(matcher),
        })
        # Reclaim the slot — the next session for this actor can reuse this
        # instance number rather than monotonically incrementing forever.
        del by_id[sid]
        entry["byId"] = by_id
        # next stays where it was; reclaim is opportunistic, not required.
        # (Reusing low-numbered slots is a separate optimization.)
        state[actor] = entry
    save_json(INSTANCES_PATH, state)

    # S033 finding #5: clear this session's byId entries from state-actors.json.
    # Without this, byId accumulates dead session IDs forever (8 dead Braindead
    # sessions + 6 dead Jebrim sessions observed in the wild). Reload because
    # the guthix block above may have written; safe re-read.
    actors = load_json(ACTORS_PATH, {})
    dirty = False
    for actor_name, entry in list(actors.items()):
        if not isinstance(entry, dict):
            continue
        by_id = entry.get("byId")
        if not isinstance(by_id, dict):
            continue
        if sid in by_id:
            del by_id[sid]
            entry["byId"] = by_id
            actors[actor_name] = entry
            dirty = True
    # S033 finding #7: clear _mode_session_id when this session owns it. Without
    # this, a crashed dev-brain session leaves _mode="dev-brain" with a stale
    # _mode_session_id pointing at the dead session; the next active-mode write
    # short-circuits in handle_active_mode_write without emitting a spawn event.
    if actors.get("_mode_session_id") == sid:
        actors.pop("_mode_session_id", None)
        # _mode itself isn't cleared — if the session crashed mid-dev-brain, the
        # next dev-brain session writing the same value will short-circuit but
        # at least take ownership of the marker via the existing stamp path.
        dirty = True
    if dirty:
        save_json(ACTORS_PATH, actors)


def _intent_file_candidates(actor: str, session_id: str | None) -> list[Path]:
    """D-017: per-instance intent files. Each parallel session of a player
    writes to `.claude/intent/<actor>-<sid8>.txt`; legacy shared files at
    `<actor>.txt` are still honored for the first-instance fallback. Returns
    the read-order list — per-session file first, then shared."""
    base = REPO_ROOT / ".claude" / "intent"
    short = (session_id or "")[:8]
    out: list[Path] = []
    if short:
        out.append(base / f"{actor}-{short}.txt")
    out.append(base / f"{actor}.txt")
    return out


_STALE_INTENT_SEC = 300   # 5 minutes — intent files older than this are stale


def _reemit_intent_after_move(actor: str, wall: str) -> None:
    """After a player actor moves, re-emit their current intent file content
    so the visualizer bubble reappears at the new building. The visualizer
    clears player intents on building change (clearIntent in move handler);
    without this, the bubble stays gone until the actor's next intent write,
    which can be a long silence while the actor is actively running tools.

    S028 follow-up: skip the re-emit when the intent file is stale (older
    than _STALE_INTENT_SEC). Otherwise a bare-file intent set hours ago by a
    long-gone session keeps getting resurrected on every move event from
    *other* sessions sharing the file (e.g., wisp.txt is shared across all
    unscoped sessions). The bubble locks on the old text indefinitely. With
    the staleness check, an abandoned intent ages out naturally."""
    import time
    name = (actor or "").strip().lower()
    if not name:
        return
    text = ""
    fresh = False
    for p in _intent_file_candidates(name, _SESSION_ID):
        if not p.exists():
            continue
        try:
            age = time.time() - p.stat().st_mtime
            raw = p.read_text(encoding="utf-8").strip()
        except Exception:
            continue
        if raw:
            text = raw.splitlines()[0].strip()
            fresh = age <= _STALE_INTENT_SEC
            break
    if not text or not fresh:
        return
    append({
        "wallTime": wall, "source": "hook",
        "type": "intent",
        "actor": name,
        "text": text[:INTENT_MAX_LEN],
    })


def _handle_guthix_lifecycle(actor: str) -> None:
    """S028: emit spawn-guthix / despawn-guthix events around intent writes.
    Called from handle_intent_write before the intent event is appended.

    - intent for guthix in a session that wasn't bankstanding → spawn-guthix,
      stamp _guthix_session_id.
    - intent for any other actor in a session that was bankstanding → despawn-
      guthix, clear _guthix_session_id.

    Session-gated: only this session's transition fires events. A parallel
    session whose intent file is bare guthix.txt would not also flip the
    marker out from under THIS session."""
    if not _SESSION_ID:
        return
    actors = load_json(ACTORS_PATH, {})
    owner = actors.get("_guthix_session_id")
    wall = now_iso()
    if actor == GUTHIX_ACTOR and owner != _SESSION_ID:
        # Newly arriving — spawn.
        append({
            "wallTime": wall, "source": "hook",
            "type": "spawn-guthix",
            "at": GUTHIX_DEFAULT_BUILDING,
        })
        append({
            "wallTime": wall, "source": "hook",
            "type": "log",
            "msg": "Guthix descends to tend the brain",
            "cls": "session-start",
            "speaker": "guthix",
        })
        actors["_guthix_session_id"] = _SESSION_ID
        save_json(ACTORS_PATH, actors)
    elif actor != GUTHIX_ACTOR and owner == _SESSION_ID:
        # Bankstanding ended in this session — despawn.
        append({
            "wallTime": wall, "source": "hook",
            "type": "despawn-guthix",
        })
        append({
            "wallTime": wall, "source": "hook",
            "type": "log",
            "msg": "Guthix recedes — the brain is tended",
            "cls": "session-start",
            "speaker": "guthix",
        })
        actors.pop("_guthix_session_id", None)
        save_json(ACTORS_PATH, actors)


def handle_intent_write(needle: str) -> bool:
    """If needle is .claude/intent/<actor>.txt or
    .claude/intent/<actor>-<sid>.txt, emit an intent event and return True.
    Otherwise return False so the normal path-classify flow runs. Intent
    writes skip building-move + log noise on purpose.

    D-017: filenames may carry a per-session suffix (`jebrim-abc12345.txt`).
    Actor name is extracted from the prefix when the suffix is present and the
    prefix matches a known player. Instance routing happens automatically via
    append() — the writing session's instance number is stamped, regardless of
    which filename variant was used. The suffix is a label for human clarity,
    not a routing input."""
    s = needle.replace("\\", "/")
    key = "/" + s if not s.startswith("/") else s
    if INTENT_FRAGMENT not in key:
        return False
    name = Path(s).name
    if not name.endswith(".txt"):
        return True   # consume — unknown intent file shape, but don't fall through
    base = name[:-4].strip().lower()
    if not base:
        return True
    # Split off the per-session suffix when it follows a known actor name.
    # Covers PLAYER_ACTORS (jebrim, zezima) and NON_PLAYER_SUFFIX_ACTORS
    # (braindead, guthix, wisp) — anything else stays as-is.
    actor = base
    if "-" in base:
        prefix, _ = base.rsplit("-", 1)
        if prefix in PLAYER_ACTORS or prefix in NON_PLAYER_SUFFIX_ACTORS:
            actor = prefix
    # S028: Guthix lifecycle runs BEFORE the intent event lands so the
    # spawn-guthix event precedes the first intent — the visualizer needs the
    # sprite to exist before the bubble attaches.
    try:
        _handle_guthix_lifecycle(actor)
    except Exception as e:
        print(f"emit-event: guthix lifecycle failed: {e}", file=sys.stderr)
    text = ""
    try:
        intent_path = REPO_ROOT / s
        text = intent_path.read_text(encoding="utf-8").strip().splitlines()[0] if intent_path.exists() else ""
    except Exception:
        text = ""
    text = text[:INTENT_MAX_LEN]
    append({
        "wallTime": now_iso(), "source": "hook",
        "type": "intent",
        "actor": actor,
        "text": text,
    })
    return True


def handle_write_or_read(tool_name: str, tool_input: dict, m: dict, payload: dict) -> None:
    needle = needle_from_payload(tool_name, tool_input)
    if not needle:
        return
    # Sidecar writes get special handling — no building move, no log noise.
    if tool_name in WRITE_TOOLS and handle_active_mode_write(needle):
        return
    if tool_name in WRITE_TOOLS and handle_intent_write(needle):
        return
    if tool_name in WRITE_TOOLS and handle_narration_write(needle):
        return
    building, actor = classify(needle, m)
    if not building:
        # S052: even when the path doesn't classify into a building (Grep on a
        # repo-wide pattern, Glob with no path, Read outside any mapped layer),
        # the chat panel still wants a human-language line. Pick actor via the
        # same recency / disk fallback Bash uses.
        sub_actor = None
        try:
            sub, _st, _kind = attribute_to_subagent(payload)
            if sub:
                sub_actor = sub["id"]
        except Exception:
            sub_actor = None
        chat_actor = sub_actor or current_main_actor()
        emit_chat_action(chat_actor, tool_name, tool_input)
        return

    wall = now_iso()
    # D-014: Read still emits a move (sprite walks into the building) but no
    # chat-side action — too noisy. Other tools emit a chat-visible action.
    emit_action = tool_name in ACTION_TOOLS
    verb, target = action_verb_and_target(tool_name, tool_input) if emit_action else ("", "")

    # Sub-agent path — if the payload carries `agent_id`, this tool call came
    # from inside a Task/Agent sub-agent. Dispatch to dwarf or gnome state by
    # the payload's `agent_type`. Move + action both attribute to the sub-agent
    # so its sprite roams and chat lines speak in its voice.
    sub, st, kind = attribute_to_subagent(payload)
    if sub:
        cfg = ROLE_CONFIG[kind]
        if sub.get("at") != building:
            append({
                "wallTime": wall, "source": "hook",
                "type": "move", "actor": sub["id"], "to": building,
            })
            sub["at"] = building
            save_json(cfg["state_path"], st)
        if emit_action and target:
            append({
                "wallTime": wall, "source": "hook",
                "type": "action",
                "actor": sub["id"],
                "verb": verb,
                "target": target,
            })
        emit_subtask(wall, sub["id"], tool_name, tool_input)
        # S052: chat line for the sub-agent's call. Includes Read (the
        # state.ndjson action stream skips Read by design, but the chat panel
        # wants human-language "Reading X" lines for visibility).
        emit_chat_action(sub["id"], tool_name, tool_input)
        return

    # Main-thread path — attribute to the active player as before.
    # Mode-marker override: if no path actor rule matched (actor == defaultActor),
    # and THIS session is the dev-brain session that set the marker, default to
    # Braindead instead of wisp. Session-gated so a parallel non-dev-brain
    # session doesn't see the shared marker and mis-flip its own events.
    if actor == m.get("defaultActor", "wisp"):
        if is_dev_brain_session():
            actor = "braindead"
        elif is_guthix_session():
            actor = GUTHIX_ACTOR
        else:
            # Path didn't identify a player (wildcard glob like
            # `players/*/quest-log/*`, or a path outside any player root).
            # Fall back to whatever actor THIS session has been operating
            # as — same recency trick current_main_actor uses for Bash.
            recent, _ = _walk_recent_actor(session_id=_SESSION_ID)
            if recent:
                actor = recent
            else:
                disk_actor = _session_actor_from_disk()
                if disk_actor:
                    actor = disk_actor
    actors = load_json(ACTORS_PATH, {})
    if get_actor_building(actors, actor, _SESSION_ID) != building:
        append({
            "wallTime": wall, "source": "hook",
            "type": "move", "actor": actor, "to": building,
        })
        set_actor_building(actors, actor, _SESSION_ID, building)
        save_json(ACTORS_PATH, actors)
        # Re-emit the actor's current intent so the bubble follows to the new
        # building. Visualizer clears player intents on move; without this, the
        # bubble stays gone until the actor's next intent file write.
        _reemit_intent_after_move(actor, wall)
    if emit_action and target:
        append({
            "wallTime": wall, "source": "hook",
            "type": "action",
            "actor": actor,
            "verb": verb,
            "target": target,
        })
    emit_subtask(wall, actor, tool_name, tool_input)
    # S052: chat line. Includes Read (see sub-agent branch comment).
    emit_chat_action(actor, tool_name, tool_input)


def _subagent_default() -> dict:
    # D-018: top-level shape for a per-role state file (dwarves, gnomes).
    #   nextId    — globally-monotonic sub-agent counter; stays top-level so
    #               parallel sessions can't both spawn "D1" (visual collision).
    #   bySession — { session_id: substate } partitioning the binding registries
    #               so session A's pending bind can't be stolen by session B's
    #               first sub-call. Each substate carries byToolUseId,
    #               pendingQueue, byAgentId, pendingAgentBind with the same
    #               semantics as the legacy flat shape.
    #
    # Legacy flat-shape entries (top-level byToolUseId / pendingQueue /
    # byAgentId / pendingAgentBind from before this re-key) are no longer
    # consulted. In-flight Task spawns at migration time leak silently and
    # get cleaned up by gc_stale_subagents after STALE_SEC.
    return {
        "nextId": 1,
        "bySession": {},
    }


def _session_substate(state: dict, session_id: str | None) -> dict:
    """D-018: get-or-create the per-session sub-state. Sessions firing before
    Claude Code's session_id is wired up (extremely rare) all share '_none'."""
    key = session_id or "_none"
    by_session = state.setdefault("bySession", {})
    sub = by_session.get(key)
    if not isinstance(sub, dict):
        sub = {
            "byToolUseId": {},
            "pendingQueue": [],
            "byAgentId": {},
            "pendingAgentBind": [],
        }
        by_session[key] = sub
    else:
        # Heal partial substates (e.g., a write that landed mid-rollout).
        sub.setdefault("byToolUseId", {})
        sub.setdefault("pendingQueue", [])
        sub.setdefault("byAgentId", {})
        sub.setdefault("pendingAgentBind", [])
    return sub


def spawn_kind_from_tool_input(tool_input: dict) -> str:
    """Map a Task tool_input to a ROLE_CONFIG kind. Subagent_type strings that
    match a configured kind ('gnome', 'penguin') route there; anything else
    is treated as a dwarf (general-purpose tasks, claude-code-guide, Explore,
    etc. all carry dwarf semantics in the visualizer)."""
    sub_type = (tool_input.get("subagent_type") or "").strip().lower()
    if sub_type in ROLE_CONFIG:
        return sub_type
    return "dwarf"


def handle_task_pre(payload: dict) -> None:
    tool_use_id = payload.get("tool_use_id") or ""
    tool_input = payload.get("tool_input") or {}
    kind = spawn_kind_from_tool_input(tool_input)
    cfg = ROLE_CONFIG[kind]
    # B7: GC stale entries before adding new ones. Bounded; only fires when
    # an entry is older than STALE_SEC (1h).
    gc_stale_subagents(kind)
    parent, at = infer_dwarf_parent()

    st = load_json(cfg["state_path"], _subagent_default())
    n = st.get("nextId", 1)
    sub_id = f"{cfg['id_prefix']}{n}"
    color = f"{cfg['color_prefix']}-{((n - 1) % cfg['color_count']) + 1}"
    st["nextId"] = n + 1
    # D-018: per-session binding registries — pendingAgentBind for THIS session
    # is the only queue eligible to claim THIS session's first sub-call.
    sub = _session_substate(st, _SESSION_ID)
    # S028 follow-up: detect run_in_background. Background Task calls return
    # the handle to the parent immediately, so PostToolUse fires ~300ms after
    # PreToolUse — long before the sub-agent's actual work completes. If we
    # despawn on Post for these, the sprite vanishes before the visualizer's
    # 1800ms fade-in animation finishes; the dwarf is invisible. Flag the
    # spawn so handle_task_post skips the despawn and the 1h GC handles
    # cleanup instead.
    background = bool(
        tool_input.get("run_in_background")
        or tool_input.get("runInBackground")
    )
    # B7: spawnedAt is the GC anchor; used by gc_stale_subagents to find
    # entries whose PostToolUse never landed.
    entry = {"id": sub_id, "color": color, "at": at, "spawnedAt": now_iso()}
    if background:
        entry["background"] = True
    if tool_use_id:
        sub["byToolUseId"][tool_use_id] = entry
        # Queue this spawn so the first sub-call carrying `agent_id` can claim
        # it. The Agent tool's Pre fires before the sub-agent exists, so we
        # don't know its agent_id yet; bind on first sighting.
        sub["pendingAgentBind"].append(tool_use_id)
    else:
        sub["pendingQueue"].append(entry)
    save_json(cfg["state_path"], st)

    description = tool_input.get("description") or tool_input.get("subagent_type") or "task"
    wall = now_iso()
    # parentSid8 lets the visualizer route sub-agent clicks back to the spawning
    # session for click-to-focus (the sub-agent has no terminal of its own).
    # Same key cascades parent-despawn → sub-agent despawn when the parent's
    # sid disappears from the switchboard manifest.
    parent_sid8 = (_SESSION_ID or "")[:8]
    append({
        "wallTime": wall, "source": "hook",
        "type": cfg["spawn_event"],
        "id": sub_id, "color": color, "parent": parent, "at": at,
        "intent": description[:INTENT_MAX_LEN],
        "parentSid8": parent_sid8,
    })
    append({
        "wallTime": wall, "source": "hook",
        "type": "log",
        "msg": f"* {sub_id} spawned by {parent} — {description}",
        "cls": "system",
        "speaker": cfg["speaker"],
    })
    emit_subtask(wall, parent, "Task", tool_input)
    # S052: chat line authored by the spawning actor.
    emit_chat_action(parent, "Task", tool_input)


def handle_task_post(payload: dict) -> None:
    tool_use_id = payload.get("tool_use_id") or ""
    tool_input = payload.get("tool_input") or {}
    kind = spawn_kind_from_tool_input(tool_input)
    cfg = ROLE_CONFIG[kind]
    # B7: GC pass alongside Post so long-lived sessions self-clean even if no
    # new spawns are firing.
    gc_stale_subagents(kind)
    st = load_json(cfg["state_path"], _subagent_default())
    sub = _session_substate(st, _SESSION_ID)

    # S028 follow-up: for background tasks the Post fires when the parent gets
    # its handle back, not when the sub-agent's actual work completes. Peek at
    # the entry first; if it's flagged background, leave it in place and skip
    # the despawn — the 1h gc_stale_subagents sweep will clean it eventually.
    if tool_use_id and tool_use_id in sub["byToolUseId"]:
        peek = sub["byToolUseId"].get(tool_use_id)
        if peek and peek.get("background"):
            return

    entry = None
    if tool_use_id and tool_use_id in sub["byToolUseId"]:
        entry = sub["byToolUseId"].pop(tool_use_id)
        # Clean up the agent_id binding so it can't be reused for a future spawn.
        by_agent = sub["byAgentId"]
        for aid, tui in list(by_agent.items()):
            if tui == tool_use_id:
                by_agent.pop(aid, None)
        # Also drop from the pendingAgentBind queue in case this spawn never
        # had any sub-calls (instant return) so we don't leak a stale entry.
        pq = sub["pendingAgentBind"]
        if tool_use_id in pq:
            pq.remove(tool_use_id)
    elif sub["pendingQueue"]:
        # FIFO fallback when tool_use_id wasn't available at Pre time.
        entry = sub["pendingQueue"].pop(0)
    save_json(cfg["state_path"], st)

    if not entry:
        return
    wall = now_iso()
    # Re-infer parent for the despawn message so it reads symmetric to spawn.
    parent, _ = infer_dwarf_parent()
    append({
        "wallTime": wall, "source": "hook",
        "type": cfg["despawn_event"],
        "id": entry["id"],
    })
    append({
        "wallTime": wall, "source": "hook",
        "type": "log",
        "msg": f"* {entry['id']} returns to {parent}",
        "cls": "system",
        "speaker": cfg["speaker"],
    })


def attribute_to_subagent(payload: dict):
    """If the hook payload carries `agent_id` (sub-agent tool call), return
    the sub-agent entry { id, color, at, spawnedAt } that owns it, plus the
    state dict and the kind (any key of ROLE_CONFIG — 'dwarf', 'gnome',
    'penguin'). Dispatches on `payload.agent_type`; falls back to dwarf state
    when agent_type is absent or unknown (older Claude Code versions or
    general-purpose tasks where the field may not be populated). Binds
    agent_id → spawn tool_use_id on first sighting via LIFO match (S022 /
    B1 — most-recent spawn wins when ambiguous). Returns (entry, state, kind)
    on success, (None, None, None) otherwise — caller is responsible for
    saving `state` if it mutates `entry["at"]`."""
    agent_id = payload.get("agent_id")
    if not agent_id:
        return None, None, None
    agent_type = (payload.get("agent_type") or "").strip().lower()
    kind = agent_type if agent_type in ROLE_CONFIG else "dwarf"
    cfg = ROLE_CONFIG[kind]
    st = load_json(cfg["state_path"], _subagent_default())
    # D-018: look up only in THIS session's substate. Sub-agent agent_ids are
    # owned by the session that spawned them, so cross-session search would
    # only introduce attribution races.
    sub = _session_substate(st, _SESSION_ID)
    by_agent = sub["byAgentId"]
    by_tui = sub["byToolUseId"]
    tool_use_id = by_agent.get(agent_id)
    if tool_use_id is None:
        pending = sub["pendingAgentBind"]
        if not pending:
            # B6: silent fallthrough — agent_id present but no pending spawn
            # to bind it to. Caller will attribute to main actor; live-mode
            # operators need a breadcrumb to debug.
            print(
                f"emit-event: cannot attribute agent_id={agent_id} ({kind}) — "
                f"no pending spawn binding",
                file=sys.stderr,
            )
            return None, None, None
        # B1: LIFO instead of FIFO. The original FIFO misattributes when two
        # spawns fire close in time and the older one returns instantly
        # without sub-calls — the newer spawn's first sub-call popped the
        # older's tool_use_id. LIFO biases toward the most recent spawn,
        # which matches the typical pattern ("I just spawned a dwarf, it
        # immediately did stuff"). Concurrent same-kind spawns that both do
        # work remain inherently ambiguous from the hook's vantage point
        # (Claude Code doesn't pass parent_tool_use_id on sub-calls); the
        # warning below makes the ambiguity visible.
        if len(pending) > 1:
            print(
                f"emit-event: ambiguous binding for agent_id={agent_id} "
                f"({kind}) — {len(pending)} pending spawns; binding to most "
                f"recent (LIFO)",
                file=sys.stderr,
            )
        tool_use_id = pending.pop()
        by_agent[agent_id] = tool_use_id
        save_json(cfg["state_path"], st)
    entry = by_tui.get(tool_use_id)
    if not entry:
        # tool_use_id was bound but the spawn entry has vanished (e.g., despawn
        # race, manual state cleanup). Same fallthrough story as above.
        print(
            f"emit-event: agent_id={agent_id} ({kind}) bound to "
            f"tool_use_id={tool_use_id} but no spawn entry found",
            file=sys.stderr,
        )
        return None, None, None
    # S028 follow-up: stamp last-activity so the idle-despawn GC can find
    # background sub-agents that have gone quiet. Persisted so the next hook
    # invocation reads it. Cheap — single write per sub-agent tool call.
    entry["lastActiveAt"] = now_iso()
    save_json(cfg["state_path"], st)
    # Also fire the idle sweep so a long-running session whose Tasks all
    # already despawned doesn't hold zombie background entries forever.
    # Cheap because gc_stale_subagents walks one role's state only.
    try:
        gc_stale_subagents(kind)
    except Exception as e:
        print(f"emit-event: gc from attribute failed: {e}", file=sys.stderr)
    return entry, st, kind


def main() -> None:
    global _SESSION_ID
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    sid = payload.get("session_id")
    if isinstance(sid, str) and sid:
        _SESSION_ID = sid

    tool_name = payload.get("tool_name", "")
    hook_event = payload.get("hook_event_name", "")

    # S028 follow-up: idle-despawn sweep runs on every hook invocation, not
    # just sub-agent activity. Without this, a session whose dwarves all
    # finish and then does plain Edit/Bash/Read work would never trigger a
    # GC pass — idle background dwarves (and their bubbles) would linger
    # indefinitely. Cheap: two state-file reads per hook fire.
    for _kind in ROLE_CONFIG:
        try:
            gc_stale_subagents(_kind)
        except Exception as e:
            print(f"emit-event: top-level gc {_kind} failed: {e}", file=sys.stderr)

    # D-017: SessionEnd is a best-effort signal that fires on graceful exits
    # (prompt_input_exit, clear, resume, logout, other matchers). NOT
    # guaranteed on crashes or forced kills — the visualizer's 5-minute idle
    # timer is the load-bearing despawn signal. This hook just lets clean
    # exits despawn faster than the timer.
    if hook_event == "SessionEnd":
        try:
            handle_session_end(payload)
        except Exception as e:
            print(f"emit-event: session-end failed: {e}", file=sys.stderr)
        # S052: chat ndjson sweep — keep file bounded across long-lived
        # workspaces. SessionEnd is one of two sanctioned sweep points
        # (the other is status-sidecar on UserPromptSubmit).
        try:
            sweep_chat_ndjson()
        except Exception as e:
            print(f"emit-event: chat sweep failed: {e}", file=sys.stderr)
        sys.exit(0)

    if tool_name in ("Task", "Agent"):
        if hook_event == "PreToolUse":
            try:
                handle_task_pre(payload)
            except Exception as e:
                print(f"emit-event: task-pre failed: {e}", file=sys.stderr)
        elif hook_event == "PostToolUse":
            try:
                handle_task_post(payload)
            except Exception as e:
                print(f"emit-event: task-post failed: {e}", file=sys.stderr)
        sys.exit(0)

    # Non-Task: only PostToolUse, only for tools we care about.
    if hook_event and hook_event != "PostToolUse":
        sys.exit(0)

    # Bash has no path → no building classification, no move. Just an action.
    if tool_name == "Bash":
        try:
            handle_bash(payload)
        except Exception as e:
            print(f"emit-event: bash handle failed: {e}", file=sys.stderr)
        sys.exit(0)

    if tool_name not in WRITE_TOOLS and tool_name not in READ_TOOLS:
        sys.exit(0)

    m = load_json(MAP_PATH, None)
    if m is None:
        sys.exit(0)

    try:
        handle_write_or_read(tool_name, payload.get("tool_input") or {}, m, payload)
    except Exception as e:
        print(f"emit-event: handle failed: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()

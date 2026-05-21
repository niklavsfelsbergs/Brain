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
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve()
DEV_BRAIN = HERE.parent.parent.parent          # developer-braindead/
REPO_ROOT = DEV_BRAIN.parent                   # brain/
VIZ_DIR = DEV_BRAIN / "experiments" / "visualizer"
MAP_PATH = VIZ_DIR / "path-map.json"
STATE_PATH = VIZ_DIR / "state.ndjson"
ACTORS_PATH = VIZ_DIR / "state-actors.json"
DWARVES_PATH = VIZ_DIR / "state-dwarves.json"
GNOMES_PATH = VIZ_DIR / "state-gnomes.json"

# Sub-agent kinds. spawn-time selection from tool_input.subagent_type; tool-call
# attribution from payload.agent_type. Both reach into the same per-kind state
# (id prefix, color palette, event names, chat speaker).
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

ACTIVE_MODE_FRAGMENT = "/.claude/active-mode.txt"
ACTIVE_MODE_PATH = REPO_ROOT / ".claude" / "active-mode.txt"
DEV_BRAIN_MODE = "dev-brain"


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
    try:
        path.write_text(json.dumps(obj), encoding="utf-8")
    except Exception as e:
        print(f"emit-event: cannot write {path.name}: {e}", file=sys.stderr)


def append(event: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
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


def infer_dwarf_parent() -> tuple[str, str]:
    # The stream is global across all Claude sessions; the hook can't tell
    # which conversation fired the Task. Prefer the most recent `intent`
    # event over `move` because every turn writes intent for its active
    # actor — that's the cleanest per-session anchor. Fall back to `move`
    # only if no recent intent exists, and ignore stale events past the
    # window so a long-dormant actor doesn't keep claiming new spawns.
    RECENCY_SEC = 600   # 10 minutes
    try:
        if not STATE_PATH.exists():
            return ("wisp", "quest-hall")
        lines = STATE_PATH.read_text(encoding="utf-8").splitlines()
    except Exception:
        return ("wisp", "quest-hall")

    now = datetime.now(timezone.utc)

    def parse_wall(s):
        try: return datetime.fromisoformat(s)
        except Exception: return None

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
        wt = parse_wall(ev.get("wallTime", ""))
        if wt is None or (now - wt).total_seconds() > RECENCY_SEC:
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
                move_actor = (a, ev.get("to") or actors.get(a) or "quest-hall")

    if intent_actor:
        at = actors.get(intent_actor) or "quest-hall"
        return (intent_actor, at)
    if move_actor:
        return move_actor
    return ("wisp", actors.get("wisp") or "quest-hall")


def read_active_mode() -> str:
    """Returns the first line of active-mode.txt, lowercased+stripped, or ''."""
    try:
        if not ACTIVE_MODE_PATH.exists():
            return ""
        return ACTIVE_MODE_PATH.read_text(encoding="utf-8").strip().splitlines()[0].lower() if ACTIVE_MODE_PATH.stat().st_size else ""
    except Exception:
        return ""


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
        return True
    actors["_mode"] = new_mode
    save_json(ACTORS_PATH, actors)
    wall = now_iso()
    # Transitioned INTO dev-brain — Braindead arrives at the workshop.
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
    # Transitioned OUT of dev-brain — Braindead leaves.
    elif prev_mode == DEV_BRAIN_MODE and new_mode != DEV_BRAIN_MODE:
        append({
            "wallTime": wall, "source": "hook",
            "type": "despawn-braindead",
        })
        append({
            "wallTime": wall, "source": "hook",
            "type": "log",
            "msg": "Braindead packs up and leaves",
            "cls": "session-start",
            "speaker": "braindead",
        })
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
    Dev-brain mode always attributes to Braindead — the recency walk would
    otherwise lock onto stale player intents from the prior gielinor session.
    Outside dev-brain, use the same recency heuristic as dwarf parent
    inference, falling back to Wisp."""
    if read_active_mode() == DEV_BRAIN_MODE:
        return "braindead"
    actor, _ = infer_dwarf_parent()
    return actor if actor != "wisp" else "wisp"


def handle_bash(payload: dict) -> None:
    """D-014: emit an `action` event for Bash (no path → no move).
    Attributes to sub-agent (dwarf or gnome) via agent_id when present, else
    to the current main-thread actor."""
    tool_input = payload.get("tool_input") or {}
    verb, target = action_verb_and_target("Bash", tool_input)
    if not target:
        return
    sub, _st, _kind = attribute_to_subagent(payload)
    actor = sub["id"] if sub else current_main_actor()
    append({
        "wallTime": now_iso(), "source": "hook",
        "type": "action",
        "actor": actor,
        "verb": verb,
        "target": target,
    })


def handle_intent_write(needle: str) -> bool:
    """If needle is .claude/intent/<actor>.txt, emit an intent event and
    return True. Otherwise return False so the normal path-classify flow
    runs. Intent writes skip building-move + log noise on purpose."""
    s = needle.replace("\\", "/")
    key = "/" + s if not s.startswith("/") else s
    if INTENT_FRAGMENT not in key:
        return False
    name = Path(s).name
    if not name.endswith(".txt"):
        return True   # consume — unknown intent file shape, but don't fall through
    actor = name[:-4].strip().lower()
    if not actor:
        return True
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
        return

    # Main-thread path — attribute to the active player as before.
    # Mode-marker override: if no path actor rule matched (actor == defaultActor),
    # and the session is dev-brain, the default actor is Braindead, not wisp.
    if actor == m.get("defaultActor", "wisp") and read_active_mode() == DEV_BRAIN_MODE:
        actor = "braindead"
    actors = load_json(ACTORS_PATH, {})
    if actors.get(actor) != building:
        append({
            "wallTime": wall, "source": "hook",
            "type": "move", "actor": actor, "to": building,
        })
        actors[actor] = building
        save_json(ACTORS_PATH, actors)
    if emit_action and target:
        append({
            "wallTime": wall, "source": "hook",
            "type": "action",
            "actor": actor,
            "verb": verb,
            "target": target,
        })


def _subagent_default() -> dict:
    # Stable shape for a per-role state file (dwarves, gnomes). Keys:
    #   nextId          — next sub-agent number to assign (D1, D2, … or G1, G2, …)
    #   byToolUseId     — { tool_use_id: { id, color, at } } until despawn
    #   pendingQueue    — FIFO of sub-agents whose spawn Pre lacked tool_use_id
    #   byAgentId       — { agent_id: tool_use_id } bound on first sub-call
    #   pendingAgentBind — FIFO of tool_use_ids awaiting agent_id binding
    return {
        "nextId": 1,
        "byToolUseId": {},
        "pendingQueue": [],
        "byAgentId": {},
        "pendingAgentBind": [],
    }


def spawn_kind_from_tool_input(tool_input: dict) -> str:
    """Map a Task tool_input to a ROLE_CONFIG kind. Anything not explicitly
    'gnome' is treated as a dwarf (general-purpose tasks, claude-code-guide,
    Explore, etc. all carry dwarf semantics in the visualizer)."""
    sub_type = (tool_input.get("subagent_type") or "").strip().lower()
    return "gnome" if sub_type == "gnome" else "dwarf"


def handle_task_pre(payload: dict) -> None:
    tool_use_id = payload.get("tool_use_id") or ""
    tool_input = payload.get("tool_input") or {}
    kind = spawn_kind_from_tool_input(tool_input)
    cfg = ROLE_CONFIG[kind]
    parent, at = infer_dwarf_parent()

    st = load_json(cfg["state_path"], _subagent_default())
    n = st.get("nextId", 1)
    sub_id = f"{cfg['id_prefix']}{n}"
    color = f"{cfg['color_prefix']}-{((n - 1) % cfg['color_count']) + 1}"
    st["nextId"] = n + 1
    entry = {"id": sub_id, "color": color, "at": at}
    if tool_use_id:
        st.setdefault("byToolUseId", {})[tool_use_id] = entry
        # Queue this spawn so the first sub-call carrying `agent_id` can claim
        # it. The Agent tool's Pre fires before the sub-agent exists, so we
        # don't know its agent_id yet; bind on first sighting.
        st.setdefault("pendingAgentBind", []).append(tool_use_id)
    else:
        st.setdefault("pendingQueue", []).append(entry)
    save_json(cfg["state_path"], st)

    description = tool_input.get("description") or tool_input.get("subagent_type") or "task"
    wall = now_iso()
    append({
        "wallTime": wall, "source": "hook",
        "type": cfg["spawn_event"],
        "id": sub_id, "color": color, "parent": parent, "at": at,
        "intent": description[:INTENT_MAX_LEN],
    })
    append({
        "wallTime": wall, "source": "hook",
        "type": "log",
        "msg": f"* {sub_id} spawned by {parent} — {description}",
        "cls": "system",
        "speaker": cfg["speaker"],
    })


def handle_task_post(payload: dict) -> None:
    tool_use_id = payload.get("tool_use_id") or ""
    tool_input = payload.get("tool_input") or {}
    kind = spawn_kind_from_tool_input(tool_input)
    cfg = ROLE_CONFIG[kind]
    st = load_json(cfg["state_path"], _subagent_default())

    entry = None
    if tool_use_id and tool_use_id in st.get("byToolUseId", {}):
        entry = st["byToolUseId"].pop(tool_use_id)
        # Clean up the agent_id binding so it can't be reused for a future spawn.
        by_agent = st.setdefault("byAgentId", {})
        for aid, tui in list(by_agent.items()):
            if tui == tool_use_id:
                by_agent.pop(aid, None)
        # Also drop from the pendingAgentBind queue in case this spawn never
        # had any sub-calls (instant return) so we don't leak a stale entry.
        pq = st.setdefault("pendingAgentBind", [])
        if tool_use_id in pq:
            pq.remove(tool_use_id)
    elif st.get("pendingQueue"):
        # FIFO fallback when tool_use_id wasn't available at Pre time.
        entry = st["pendingQueue"].pop(0)
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
    the sub-agent entry { id, color, at } that owns it, plus the state dict
    and the kind ('dwarf' or 'gnome'). Dispatches on `payload.agent_type`;
    falls back to dwarf state when agent_type is absent (older Claude Code
    versions or general-purpose tasks where the field may not be populated).
    Binds agent_id → spawn tool_use_id on first sighting via FIFO match.
    Returns (entry, state, kind) on success, (None, None, None) otherwise —
    caller is responsible for saving `state` if it mutates `entry["at"]`."""
    agent_id = payload.get("agent_id")
    if not agent_id:
        return None, None, None
    agent_type = (payload.get("agent_type") or "").strip().lower()
    kind = "gnome" if agent_type == "gnome" else "dwarf"
    cfg = ROLE_CONFIG[kind]
    st = load_json(cfg["state_path"], _subagent_default())
    by_agent = st.setdefault("byAgentId", {})
    by_tui = st.setdefault("byToolUseId", {})
    tool_use_id = by_agent.get(agent_id)
    if tool_use_id is None:
        pending = st.setdefault("pendingAgentBind", [])
        if not pending:
            return None, None, None
        tool_use_id = pending.pop(0)
        by_agent[agent_id] = tool_use_id
        save_json(cfg["state_path"], st)
    entry = by_tui.get(tool_use_id)
    if not entry:
        return None, None, None
    return entry, st, kind


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    hook_event = payload.get("hook_event_name", "")

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

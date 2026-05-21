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

WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Glob", "Grep"}

INTENT_FRAGMENT = "/.claude/intent/"
INTENT_MAX_LEN = 60

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
    # Walk state.ndjson from the tail; first non-wisp actor with a `move`
    # wins. Fall back to wisp at quest-hall.
    try:
        if not STATE_PATH.exists():
            return ("wisp", "quest-hall")
        lines = STATE_PATH.read_text(encoding="utf-8").splitlines()
    except Exception:
        return ("wisp", "quest-hall")
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if ev.get("type") == "move":
            actor = ev.get("actor")
            if actor and actor != "wisp":
                return (actor, ev.get("to") or "quest-hall")
    # Nothing but wisp / no moves at all
    actors = load_json(ACTORS_PATH, {})
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


def handle_write_or_read(tool_name: str, tool_input: dict, m: dict) -> None:
    needle = needle_from_payload(tool_name, tool_input)
    if not needle:
        return
    # Sidecar writes get special handling — no building move, no log noise.
    if tool_name in WRITE_TOOLS and handle_active_mode_write(needle):
        return
    if tool_name in WRITE_TOOLS and handle_intent_write(needle):
        return
    building, actor = classify(needle, m)
    if not building:
        return
    # Mode-marker override: if no path actor rule matched (actor == defaultActor),
    # and the session is dev-brain, the default actor is Braindead, not wisp.
    if actor == m.get("defaultActor", "wisp") and read_active_mode() == DEV_BRAIN_MODE:
        actor = "braindead"
    is_write = tool_name in WRITE_TOOLS
    cls = "write" if is_write else "read"
    wall = now_iso()
    actors = load_json(ACTORS_PATH, {})
    if actors.get(actor) != building:
        append({
            "wallTime": wall, "source": "hook",
            "type": "move", "actor": actor, "to": building,
        })
        actors[actor] = building
        save_json(ACTORS_PATH, actors)
    append({
        "wallTime": wall, "source": "hook",
        "type": "log",
        "msg": f"{tool_name.lower()} {needle}",
        "cls": cls,
        "speaker": actor,
    })


def handle_task_pre(payload: dict) -> None:
    tool_use_id = payload.get("tool_use_id") or ""
    tool_input = payload.get("tool_input") or {}
    parent, at = infer_dwarf_parent()

    dw = load_json(DWARVES_PATH, {"nextId": 1, "byToolUseId": {}, "pendingQueue": []})
    n = dw.get("nextId", 1)
    dwarf_id = f"D{n}"
    color = f"dwarf-{((n - 1) % 3) + 1}"
    dw["nextId"] = n + 1
    if tool_use_id:
        dw.setdefault("byToolUseId", {})[tool_use_id] = {"id": dwarf_id, "color": color}
    else:
        dw.setdefault("pendingQueue", []).append({"id": dwarf_id, "color": color})
    save_json(DWARVES_PATH, dw)

    description = tool_input.get("description") or tool_input.get("subagent_type") or "task"
    wall = now_iso()
    append({
        "wallTime": wall, "source": "hook",
        "type": "spawn-dwarf",
        "id": dwarf_id, "color": color, "parent": parent, "at": at,
        "intent": description[:INTENT_MAX_LEN],
    })
    append({
        "wallTime": wall, "source": "hook",
        "type": "log",
        "msg": f"spawning {dwarf_id} — {description}",
        "cls": "spawn",
        "speaker": "dwarves",
    })


def handle_task_post(payload: dict) -> None:
    tool_use_id = payload.get("tool_use_id") or ""
    dw = load_json(DWARVES_PATH, {"nextId": 1, "byToolUseId": {}, "pendingQueue": []})

    entry = None
    if tool_use_id and tool_use_id in dw.get("byToolUseId", {}):
        entry = dw["byToolUseId"].pop(tool_use_id)
    elif dw.get("pendingQueue"):
        # FIFO fallback when tool_use_id wasn't available at Pre time.
        entry = dw["pendingQueue"].pop(0)
    save_json(DWARVES_PATH, dw)

    if not entry:
        return
    wall = now_iso()
    append({
        "wallTime": wall, "source": "hook",
        "type": "despawn-dwarf",
        "id": entry["id"],
    })
    append({
        "wallTime": wall, "source": "hook",
        "type": "log",
        "msg": f"{entry['id']} returns",
        "cls": "spawn",
        "speaker": "dwarves",
    })


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    hook_event = payload.get("hook_event_name", "")

    if tool_name == "Task":
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
    if tool_name not in WRITE_TOOLS and tool_name not in READ_TOOLS:
        sys.exit(0)

    m = load_json(MAP_PATH, None)
    if m is None:
        sys.exit(0)

    try:
        handle_write_or_read(tool_name, payload.get("tool_input") or {}, m)
    except Exception as e:
        print(f"emit-event: handle failed: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()

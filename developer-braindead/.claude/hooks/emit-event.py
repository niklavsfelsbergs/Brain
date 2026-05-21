#!/usr/bin/env python3
# Visualizer live-mode emitter (D-009). PostToolUse on Edit | Write today;
# Read | Glob | Grep added in step 3, Task spawn/despawn in step 4.
#
# Reads the tool-call payload from stdin, classifies the touched path against
# path-map.json, and appends a `move` + `log` event to state.ndjson. Never
# fails the tool call — any error is swallowed to stderr.

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


def load_map() -> dict | None:
    try:
        return json.loads(MAP_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"emit-event: cannot read path-map.json: {e}", file=sys.stderr)
        return None


def classify(rel_path: str, m: dict) -> tuple[str | None, str]:
    posix = rel_path.replace("\\", "/")
    # Substring contains anywhere; rules ordered most-specific first.
    key = "/" + posix if not posix.startswith("/") else posix
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


def append(event: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, separators=(",", ":")) + "\n")


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        sys.exit(0)

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not file_path:
        sys.exit(0)

    rel = to_rel(file_path)
    if not rel:
        sys.exit(0)

    m = load_map()
    if m is None:
        sys.exit(0)

    building, actor = classify(rel, m)
    if not building:
        sys.exit(0)

    wall = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    try:
        append({
            "wallTime": wall, "source": "hook",
            "type": "move", "actor": actor, "to": building,
        })
        append({
            "wallTime": wall, "source": "hook",
            "type": "log", "msg": f"{tool_name.lower()} {rel}",
            "cls": "write", "speaker": actor,
        })
    except Exception as e:
        print(f"emit-event: append failed: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()

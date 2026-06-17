#!/usr/bin/env python3
"""test_async_crew_lifecycle.py -- guards the async-Agent "awaiting crew" fix.

The bug: the modern `Agent` tool launches sub-agents ASYNC -- its PostToolUse
fires ~250ms later at LAUNCH (the parent gets a handle), not at completion. The
real result arrives minutes later via a `<task-notification>` re-invoke carrying
the original `<tool-use-id>`. emit-event.py treated the Agent spawn as the old
blocking `Task` and despawned it on Post, ~230ms after spawn -- before the
cockpit's ~2s poll ever saw a pending sub-agent. So "awaiting crew" never showed
(observed live: G12 gnome + D264 dwarf both despawned ~230ms after spawn).

The fix (two hooks):
  - emit-event.py: flag a foreground `Agent` spawn `async_agent`; handle_task_post
    SKIPS the launch-despawn for it (and for run_in_background `background`).
  - status-sidecar.py: _reconcile_async_crew despawns an `async_agent` entry once
    its `<task-notification>` lands in the transcript (the completion signal the
    launch-time Post can't give). emit-event's 1h GC is the backstop.

These cases drive the REAL hook functions (the entry points the harness calls),
with the role-state / event paths repointed at a temp dir.

Run: python developer-braindead/verification/test_async_crew_lifecycle.py
"""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

# file is developer-braindead/verification/test_*.py → parents[1] == developer-braindead/
HOOKS = Path(__file__).resolve().parents[1] / ".claude" / "hooks"

PASS = 0
FAIL = 0


def check(name, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}: got {got!r}, want {want!r}")


def _load(modname, filename):
    spec = importlib.util.spec_from_file_location(modname, HOOKS / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


def _repoint_emit(ee, root):
    """Redirect every write path emit-event touches to the temp dir."""
    ee.VIZ_DIR = root
    ee.STATE_PATH = root / "state.ndjson"
    ee.CHAT_PATH = root / "chat.ndjson"
    ee.DWARVES_PATH = root / "state-dwarves.json"
    ee.GNOMES_PATH = root / "state-gnomes.json"
    ee.PENGUINS_PATH = root / "state-penguins.json"
    if hasattr(ee, "SHIPPING_AGENTS_PATH"):
        ee.SHIPPING_AGENTS_PATH = root / "state-shipping-agents.json"
    # ROLE_CONFIG captured the path objects at import — repoint per kind.
    namemap = {
        "dwarf": ee.DWARVES_PATH, "gnome": ee.GNOMES_PATH,
        "penguin": ee.PENGUINS_PATH,
    }
    for kind, cfg in ee.ROLE_CONFIG.items():
        if kind in namemap:
            cfg["state_path"] = namemap[kind]
        else:
            cfg["state_path"] = root / f"state-{kind}s.json"


def _repoint_sidecar(ss, root):
    ss.SUBAGENT_STATE_PATHS = (
        root / "state-dwarves.json", root / "state-gnomes.json",
        root / "state-penguins.json", root / "state-shipping-agents.json",
    )
    ss.STATE_NDJSON_PATH = root / "state.ndjson"


def _role(root, name):
    p = root / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _entry(role, sid, tui):
    return ((role.get("bySession") or {}).get(sid) or {}).get("byToolUseId", {}).get(tui)


def main():
    ee = _load("emit_event_mod", "emit-event.py")
    ss = _load("status_sidecar_mod", "status-sidecar.py")
    SID = "5974b4ee-aaaa-bbbb-cccc-000000000001"

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _repoint_emit(ee, root)
        _repoint_sidecar(ss, root)
        ee._SESSION_ID = SID

        # --- Case 1: async Agent gnome — recorded with async_agent, SURVIVES Post.
        tui_g = "toolu_async_gnome_0001"
        ee.handle_task_pre({
            "tool_name": "Agent", "tool_use_id": tui_g, "session_id": SID,
            "tool_input": {"subagent_type": "gnome", "description": "alching"},
        })
        g = _entry(_role(root, "state-gnomes.json"), SID, tui_g)
        check("gnome spawn recorded", bool(g), True)
        check("gnome flagged async_agent", bool(g and g.get("async_agent")), True)

        ee.handle_task_post({
            "tool_name": "Agent", "tool_use_id": tui_g, "session_id": SID,
            "tool_input": {"subagent_type": "gnome"},
        })
        check("async gnome SURVIVES launch Post (not despawned)",
              bool(_entry(_role(root, "state-gnomes.json"), SID, tui_g)), True)

        # It reads as crew (pending), so the board can show "awaiting crew".
        pending = ss._pending_subagents_by_session().get(SID, [])
        check("async gnome appears in pending crew list", g["id"] in pending, True)

        # --- Case 2: task-notification lands -> reconcile despawns it.
        transcript = root / "transcript.jsonl"
        transcript.write_text(
            json.dumps({"type": "user", "message": {"role": "user", "content":
                f"<task-notification>\n<task-id>abc123</task-id>\n<tool-use-id>{tui_g}</tool-use-id>\n<status>completed</status>\n</task-notification>"}}) + "\n",
            encoding="utf-8")
        ss._reconcile_async_crew(SID, transcript)
        check("async gnome despawned after its task-notification",
              _entry(_role(root, "state-gnomes.json"), SID, tui_g), None)
        # despawn event emitted for the sprite
        ev_lines = (root / "state.ndjson").read_text(encoding="utf-8").splitlines() if (root / "state.ndjson").exists() else []
        check("despawn-gnome event emitted",
              any('"despawn-gnome"' in ln and g["id"] in ln for ln in ev_lines), True)
        check("crew list empty after completion",
              ss._pending_subagents_by_session().get(SID, []), [])

        # --- Case 3: the OLD blocking Task tool still despawns on Post.
        tui_t = "toolu_sync_task_0002"
        ee.handle_task_pre({
            "tool_name": "Task", "tool_use_id": tui_t, "session_id": SID,
            "tool_input": {"description": "scan"},  # no subagent_type -> dwarf
        })
        d = _entry(_role(root, "state-dwarves.json"), SID, tui_t)
        check("sync Task recorded as dwarf", bool(d), True)
        check("sync Task NOT flagged async_agent", bool(d and d.get("async_agent")), False)
        ee.handle_task_post({
            "tool_name": "Task", "tool_use_id": tui_t, "session_id": SID,
            "tool_input": {"description": "scan"},
        })
        check("sync Task despawns on Post (old behavior preserved)",
              _entry(_role(root, "state-dwarves.json"), SID, tui_t), None)

        # --- Case 4: run_in_background Agent -> background, EXCLUDED from crew.
        tui_b = "toolu_bg_agent_0003"
        ee.handle_task_pre({
            "tool_name": "Agent", "tool_use_id": tui_b, "session_id": SID,
            "tool_input": {"subagent_type": "dwarf", "run_in_background": True},
        })
        b = _entry(_role(root, "state-dwarves.json"), SID, tui_b)
        check("bg Agent flagged background", bool(b and b.get("background")), True)
        check("bg Agent NOT flagged async_agent", bool(b and b.get("async_agent")), False)
        check("bg Agent excluded from crew pending list",
              b["id"] in ss._pending_subagents_by_session().get(SID, []), False)

        # --- Case 5: reconcile with a DIFFERENT tui leaves the async entry alone.
        tui_g2 = "toolu_async_gnome_0004"
        ee.handle_task_pre({
            "tool_name": "Agent", "tool_use_id": tui_g2, "session_id": SID,
            "tool_input": {"subagent_type": "gnome", "description": "alching2"},
        })
        other = root / "transcript2.jsonl"
        other.write_text(
            json.dumps({"type": "user", "message": {"role": "user", "content":
                "<task-notification>\n<tool-use-id>toolu_unrelated_9999</tool-use-id>\n</task-notification>"}}) + "\n",
            encoding="utf-8")
        ss._reconcile_async_crew(SID, other)
        check("async gnome NOT despawned by an unrelated notification",
              bool(_entry(_role(root, "state-gnomes.json"), SID, tui_g2)), True)

    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()

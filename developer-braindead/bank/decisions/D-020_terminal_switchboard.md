# D-020 — 2026-05-22 — Terminal switchboard (per-session status sidecar)

**Context.** With parallel sessions now a routine pattern ([[D-017_parallel_player_instances]] Jebrims, [[D-019_parallel_braindead_and_comms_channel]] Braindeads, plus Guthix and Wisp), Niklavs runs five-to-ten Claude Code terminals at a time, each at a different point in its turn cycle. The visualizer answers *"who's where in the brain"* — it does not answer *"which of these terminals is waiting on me right now."*

That second question matters more for routine operation. The cost today is alt-tabbing through every window to check who's idle, who's mid-tool-call, and who's parked on a Stop with a question for the principal. A status sidecar plus an aggregator view collapses the lookup from N tabs to one glance.

**Decision.** Build a **three-phase** terminal switchboard. Phase 1 (this session) lands the contract. Phases 2 and 3 defer to subsequent sessions.

## The state machine

Every Claude Code session is in one of three states, derived from hook events:

| State | Derived from |
|---|---|
| `working` | latest hook event was `UserPromptSubmit`, `PreToolUse`, or `PostToolUse` |
| `waiting_for_user` | latest hook event was `Stop` |
| `idle` | `waiting_for_user` AND `now - last_event_ts > 5 min` — **computed by the reader, not stamped by the writer** |

`SessionEnd` writes `state: "ended"`. The reader hides ended files (or shows them gray-and-collapsed); a sweeper removes them after 24h of staleness via move into `~/.claude/status/archive/` (no deletes, dev-brain follows the same archive-or-nothing convention as gielinor).

The reader-derives-idle rule is load-bearing: a writer-side idle stamp would require either polling (no hook fires while idle) or a SessionStart-time timer (substrate-fragile). Reader-side is a function of two fields the writer already has, so it costs nothing and stays accurate to the second.

## The contract

**File path.** `~/.claude/status/<sid8>.json` — **user-global**, not per-project. Chosen so one switchboard sees every Claude Code session on the machine across all repos. The per-project alternative (`.claude/status/`) would require running one switchboard per directory; that doesn't match the actual workflow.

**File shape.**

```json
{
  "sid8": "a989e89a",
  "session_id": "a989e89a-37ff-45b0-bebd-c60b484a26df",
  "actor": "braindead",
  "instance": 1,
  "state": "working",
  "last_event_kind": "PostToolUse",
  "last_event_ts": 1716400000.123,
  "started_at": 1716399000.000,
  "intent": "Designing terminal switchboard",
  "project_dir": "C:/Users/niklavs.felsbergs/Documents/GitHub/brain",
  "cwd": "C:/Users/niklavs.felsbergs/Documents/GitHub/brain",
  "host": "vscode"
}
```

- `sid8`, `session_id` — first 8 chars + full UUID from `CLAUDE_CODE_SESSION_ID` (and `payload.session_id` on hooks).
- `actor` — derived by scanning `<project_dir>/.claude/intent/<actor>-<sid8>.txt` for an existing match. Falls back to `unknown` if no per-session intent file is present yet (early in a session, before the first intent write).
- `instance` — for Phase 1, always `1`. Reading `state-instances.json` to recover the true instance number is doable but couples this hook to the visualizer's data. Defer to Phase 2 if the sidebar wants to disambiguate `Braindead·2`.
- `intent` — first line of the per-session intent file, ≤100 chars (same cap as `INTENT_MAX_LEN` in the visualizer hook). Lets the sidebar render *what the agent thinks it's doing* alongside the status dot.
- `project_dir` — from `CLAUDE_PROJECT_DIR` env var (set by Claude Code). The repo this session was opened in.
- `cwd` — actual process cwd at hook fire time. Usually equals `project_dir` but the agent can `cd` during a session.
- `host` — best-effort substrate detection from env: `vscode` if `TERM_PROGRAM=vscode` or `VSCODE_PID` set; `windows-terminal` if `WT_SESSION` set; `unknown` otherwise. Phase 3 uses this to pick the right focus mechanism.

**Atomic write.** Same pattern as `emit-event.py`'s `save_json` — write to `<path>.tmp.<pid>`, then `os.replace` onto the destination. Crashes leave the old file intact, never a half-written status.

**Sweeper.** On every hook fire, the script also scans `~/.claude/status/*.json` for entries older than 24h and moves them to `~/.claude/status/archive/`. Bounded (≤O(active sessions on the machine)); no separate cron needed.

## Hook wiring

A **new script**, `developer-braindead/.claude/hooks/status-sidecar.py`, registered in `brain/.claude/settings.json` for `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `SessionEnd`. Kept separate from `emit-event.py` for two reasons:

1. **Collision isolation.** `emit-event.py` is 1500+ lines of visualizer logic. A new sidecar that lives in its own file doesn't touch any of that surface area — small blast radius, easy to remove later if the design changes.
2. **Failure isolation.** If the sidecar throws, the visualizer hook stays intact. The hooks run in sequence per event; both being registered means a bad sidecar can't take down the emitter.

Both hooks read the same stdin payload, both `sys.exit(0)` on any error — the standard "never break the tool call" discipline.

## Phase build order

| Phase | Scope | Status |
|---|---|---|
| **1** | Status sidecar hook + user-global file contract + sweeper | **this session** |
| **2** | Sidebar pane in the visualizer reading `~/.claude/status/*.json`. Status dot per sprite + a session list with one-line entries. | next session — defer until f39b5b3f's visualizer work is settled |
| **3** | VS Code window-focus mechanism. The status file already records `host` and the OS window title can be derived from VS Code's workspace title. Click handler in the sidebar runs a PowerShell helper using `user32.dll`'s `FindWindow` + `SetForegroundWindow`. | deferred — only build once Phase 2 proves the sidebar list isn't enough on its own |

This order is deliberate. Phase 1 alone gives a *machine-readable* signal even before any UI; tools like `gh-dash`-style TUIs or a bare `watch cat ~/.claude/status/*.json` script could already use it. Phase 2 is the human-readable layer. Phase 3 is the click-to-focus mechanism — the least essential piece, because the moment you can *see* the list of sessions, alt-tab is fast enough for routine work.

## What "shipped" looks like (Phase 1)

- `developer-braindead/bank/decisions/D-020_terminal_switchboard.md` (this file).
- `developer-braindead/.claude/hooks/status-sidecar.py` — the script.
- `brain/.claude/settings.json` — wires the new hook to the five event kinds (no edits to `emit-event.py` or its hook registration).
- `~/.claude/status/<sid8>.json` — appears for this session and survives across hook fires.
- A smoke-test trace (in this session's quest-log) confirming the four transitions land.

## Out of scope for the first cut

- **Sidebar UI.** Phase 2.
- **Click-to-focus.** Phase 3.
- **Cross-machine aggregation.** If Niklavs runs sessions on a VPS later, the user-global path doesn't help. Wait for an actual need before designing the network shape.
- **Instance number stamping in the status file.** Phase 2 can read `state-instances.json` and merge; this hook stays decoupled.
- **Status entries for sub-agents (dwarves, gnomes).** They share the parent session's `sid8` — already covered by the parent's status. Phase 2 sidebar can render sub-agents as nested entries if useful.
- **Idle threshold tuning.** 5 min matches the visualizer despawn timer. Could become per-actor later (a Braindead at 5 min idle is probably done; a Jebrim mid-research might want 15 min). Defer until observed.

## Open questions

- **Actor detection latency.** The first hook fire of a fresh session may run before the agent has written `<actor>-<sid8>.txt` (intent narration usually follows the Plan line, but the Plan line itself might be the first user turn that fires `UserPromptSubmit`). The sidecar will write `actor: "unknown"` for that one fire; the next event will update it. Acceptable — the sidebar can render `unknown` as a gray dot until the actor resolves.
- **Sweeper-races-writer.** A session writing its status concurrently with another session's sweeper moving the same file is theoretically possible only if the writer was already stale (>24h) — which means the writer process is long dead. Treat as a non-issue.
- **VS Code multi-window.** VS Code with multiple workspace windows open creates ambiguity: which window owns this terminal? Phase 3 can resolve via `VSCODE_PID` → walk to parent process. Defer.
- **No-write turns.** Pure-thinking turns where the agent runs no tools still fire `UserPromptSubmit` and `Stop` — the four events bracket every turn, so the state machine doesn't have a "silent turn" hole.

## Related

- [[D-014_visualizer_chat_panel]] — visualizer intent-vs-action channels. The status sidecar is a third channel: state-machine signal, not voice and not action.
- [[D-017_parallel_player_instances]], [[D-019_parallel_braindead_and_comms_channel]] — parallel sessions; the existence of multiple concurrent terminals is the problem this decision solves.
- [[D-018_parallel_session_substrate_isolation]] — per-session intent files; actor-from-disk detection here reuses that filename convention.
- `gielinor/meta/communication-protocol.md` — the intent narration rule; this sidecar reads what intent narration has already written.

## S052 amendment — 2026-05-23

The manifest mirror moved. `state-switchboard.json` now lives at `switchboard/state-switchboard.json` (was `developer-braindead/experiments/visualizer/state-switchboard.json`) — the surface was promoted to brain root in [[D-026_switchboard_promotion]] when the map collapsed and the switchboard became load-bearing on its own. `status-sidecar.py`'s `VIZ_DIR` constant points at the new location; everything in this doc about the contract, state machine, and write path is unchanged on the *shape* side.

Sibling stream added in the same session: `switchboard/chat.ndjson` — hook-side humanized event log (write/edit/grep/bash/spawn/idle lines) written by `emit-event.py`, consumed by the switchboard's chat panel. Independent of the status sidecar; same atomic-append pattern.

# D-028 — 2026-05-23 — Switchboard rebuild: standalone fleet cockpit

**Context.** The switchboard accreted across ~18 of the last ~25 dev sessions (S037, S039, S042–S043, S047–S053, S056–S062). It started as an isometric map ([[D-009_visualizer_live_mode_v0]]), shed the map for switchboard+chat panels ([[D-026_switchboard_promotion]]), then grew an embedded agent chat ([[S060]]), a COMMS reskin, and a lifecycle feed — each session bolting a feature onto whichever of three identities felt urgent that day. The result is three uncoordinated products in one trenchcoat:

1. **Monitor** — which session needs me, what's each doing (the rows + `status-sidecar.py`).
2. **Feed** — the cross-session narrative (COMMS / `chat.ndjson` / comms mirrors), which shapeshifted three times (coordination channel → action firehose → lifecycle ticker).
3. **Driver** — prompt agents in-app via headless `claude` (`server.py` `/chat` + `terminal.js`), the most bug-dense and least-eyeballed chunk.

The recurring bugs (server dying, stale-cache "hard-refresh or it's broken," ~1,100 lines of uncommitted parallel-session edits, three-way file-ownership wars) cluster in #2 and #3. The thing the principal actually relies on is #1. This matches [[D-027_inward_outward_build_imbalance]]'s finding that the brain over-invested in inward observability scaffolding (~52% of recent commits) at the expense of outward capability — the principal: *"I'm spending time building it when I should be building my agents. But I need this app, it makes everything so much better if it works."*

Root cause is not bad code — it's **no fixed definition**. The fix is to define what it is, then rebuild against that definition.

## Decision

Rebuild the switchboard from scratch as a **standalone fleet cockpit** — *the* place the principal runs a fleet of parallel Claude sessions from, not a dashboard glanced at beside VS Code. VS Code drops to the engine room; the cockpit is the operator's console. The name was right all along: a switchboard operator watches a board of live calls and patches/releases them. We built the wallboard (the lights); we never built the console.

The verbs it must nail (principal's words):

- **See the whole fleet at once** — up to ~10 sessions plus nested subagents, each showing real state: `WORKING / WAITING ON YOU / AWAITING CREW / ALCHING / WRAPPED UP / ENDED`. Kills the core pain: clicking through VS Code terminals hunting for the one blocked on you.
- **Watch the work flow** — the live stream of what each session is doing. This is the engagement surface ("the chat solves boredom; I want to look at what's happening"), not a debug log.
- **Drive any of them in-app** — prompt + reply right there. This is *why* it's standalone — no more bouncing monitor↔VS Code.
- **Command the fleet** — when a session is `WRAPPED UP`, release it and place a new one. Place / re-task / release, from the board.

## Foundation (stack)

- **One Python process via `pywebview`.** Hosts the window + backend + claude-driver, so it launches and dies as one — the server-dying disease (a separate-process server going stale/squatting the port) cannot recur. Native chromeless window, own taskbar icon, compiles to an `.exe`. Stays all-Python (hooks are Python; the proven stream-json driving is Python) — no Node, no Rust, no bundler. Uses Win11's bundled WebView2 as the renderer. Not a one-way door: the web frontend lifts into Tauri later if a polished installable is ever wanted.
- **Frontend: Preact + `htm` via an ESM import map.** No build step, no `node_modules`. Reactive components map 1:1 to "one model, three views," killing the hand-rolled-DOM/stale-render bug class that plagued the old client.
- **Assets served `Cache-Control: no-store`** → the "hard-refresh or it's stale" tax is gone permanently.
- **Greenfield in a new `cockpit/` directory.** Zero edits to `switchboard/`, so the current board stays live through the multi-phase build. The old client is archived (never deleted, per archive discipline) only at the final swap. Swap-vs-keep-the-name decided at swap time.

## One session model, three views (the anti-accretion discipline)

The old client's bugs came from three uncoordinated data paths (`state-switchboard.json`, `chat.ndjson`, comms mirrors, `/history`) that drifted out of sync. The rebuild assembles **one** session model in the backend; the three surfaces are projections of it:

- A **session** = `{ identity (actor, sid8, instance, host), state, activity[], transcript, subagents[] }`.
- **Fleet board** renders state + activity + subagent nesting + click-to-focus.
- **Session console** renders + writes transcript (drivable for cockpit-launched sessions; read-only peek for VS Code-launched).
- **Activity feed** renders state-transitions + comms across the fleet.

Backend exposes one shaped API (`/api/sessions`, `/api/sessions/<id>` for transcript, `/chat` WS for driving). The frontend never juggles raw state files again.

## Preserved contracts (hooks untouched)

The hooks are where ~18 sessions of subtle parallel-session / PID-liveness / Windows-encoding logic live. They are **preserved as contracts** — the new backend reads their existing output; `status-sidecar.py` and `emit-event.py` are not rewritten. Captured so nothing is lost:

- **`state-switchboard.json`** — per-session manifest: `sid8`, `session_id`, `actor`, `instance`, `state`, `last_event_kind/ts`, `started_at`, `first_prompt`, `intent`, `project_dir`, `cwd`, `host`, `claude_pid`, `claude_pid_chain`, `claude_hwnd`, `building`, `latest_action`/`_ts`, `subtitle`. The board's primary source.
- **State vocabulary** — `working / waiting_for_user / waiting_for_subagents / alching / wrapped_up / closing / idle / ended`, derived hook-side (incl. PID-liveness drop, `.mode` marker overrides for alching/wrapped_up). Exactly the states the principal listed.
- **Subagent state** — `state-dwarves.json` / `-gnomes.json` / `-penguins.json` (`bySession[sid].byToolUseId`/`pendingQueue`/`byAgentId`), and `state-instances.json` for instance numbering.
- **`chat.ndjson`** — append-only humanized event + lifecycle-checkpoint stream (`{ts, kind, actor, text}`; kinds incl. the S062 PICKED UP/PLAN/PROGRESS/NEEDS YOU/DONE).
- **`state-comms-{gielinor,braindead}.md`** — comms mirrors.
- **Driving** — headless `claude -p --input-format stream-json --output-format stream-json --include-partial-messages --verbose --permission-mode bypassPermissions --session-id <uuid>` at brain root; `/history?session=<uuid>` parses on-disk `.jsonl` into visual turns; `{type:"interrupt"}` → `control_request`; resume via `--resume`. Re-implemented cleanly in the new backend, same protocol.
- **Persistence** — detached launch (`start-switchboard.vbs` pattern) survives terminal closes; folded into the pywebview launcher.

## Build phases (a spine that stands, then ribs)

Each phase is independently useful and committable; no phase depends on a later one rendering.

1. **Shell + board (read-only).** pywebview window launches from an icon, hosts the backend, renders the live fleet board off the existing state files. *This phase alone kills the core pain.* Proves the foundation.
2. **Session console.** Click a row → its conversation; drive cockpit-launched sessions (prompt/reply/interrupt), read-only peek VS Code ones. Re-implements the stream-json driver + `.jsonl` history.
3. **Fleet command.** Place (spawn w/ actor+brain+prompt, cockpit writes the address) / re-task / release (terminate).
4. **Activity feed.** Lifecycle checkpoints + comms; raw actions off-by-default toggle; merged, filterable, click-to-jump.
5. **Package + polish.** Compile to `.exe` + icon; sort/pulse + optional sound on WAITING; remembers size/position, single-instance, optional always-on-top; clean-modern theme.

## Locked product decisions (S064 elicitation)

- **Aesthetic:** clean modern (not the OSRS parchment of the old client).
- **Permissions:** `bypassPermissions` for cockpit-driven sessions; an in-cockpit approval surface is a possible later phase.
- **Place a session:** pick actor (Jebrim/Zezima/Guthix/Braindead/unscoped) + brain + prompt; the cockpit writes the `Hey <actor>,` address.
- **Operator verbs:** place = new session; re-task = re-prompt an idle/wrapped session; release = terminate the process.
- **VS Code sessions:** shown as read-only peek rows (first thing to cut if it fights us).
- **Subagents:** nested under parent, own state chip + short intent, collapsible.
- **Row lifetime:** WRAPPED stays until released; ENDED fades after a few minutes.
- **Both brains, one board** (gielinor players + dev Braindead + Guthix + Wisp).
- **Feed:** lifecycle checkpoints + comms; raw actions off by default; merged, filterable, click-to-jump.
- **Attention:** visual pulse always + optional sound on WAITING.
- **Window:** remembers size/position, single-instance, optional always-on-top.
- **Console rendering:** streamed text, tool cards, thinking blocks, markdown, cost/time dividers; full transcript on open.

## Consequences

- The old `switchboard/` keeps running untouched during the build; sibling session `braindead-3d2dc4b1` (S063) was on the incremental-patch path (cache-bust, rename COMMS) — those follow-ups are moot under the rebuild and were flagged off in comms.
- Greenfield means no migration churn and no parallel-edit collisions ([[D-024_parallel_player_coordination]]) with the live client.
- At swap, the old client archives; `path-map.json`/vestigial bits get resolved then.

## Related

- [[D-009_visualizer_live_mode_v0]] — visualizer live-mode origin.
- [[D-014_visualizer_chat_panel]] — chat panel (absorbed into the feed + console).
- [[D-020_terminal_switchboard]] — terminal switchboard (the monitor that earned the name).
- [[D-024_parallel_player_coordination]] — parallel coordination; why greenfield avoids collision.
- [[D-026_switchboard_promotion]] — switchboard promotion to brain root; the cockpit stays a both-brains surface.
- [[D-027_inward_outward_build_imbalance]] — inward/outward build imbalance; this rebuild is meant to *end* the switchboard's time-sink, not extend it.
- [[S060]] — embedded agent chat; the driver mechanism preserved here.
- S064 — quest-log entry capturing the rebuild construction.

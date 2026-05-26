# D-009 — 2026-05-21 — Visualizer live-mode v0 ships as hooks + NDJSON + polling

**Context.** [[Q-007]] proposed live mode as the substrate-change follow-up to the replay-from-git-log v0 shipped in [[S008]] / [[D-008_iso_replay_v0_over_three_js]]. After [[S009]]'s aesthetic pass, the v0 was deemed "good enough to show people," which is the trigger Q-007 named for committing to real-time. Decision needed on transport, write sources, and engine-touch surface.

**Decision.** Ship live-mode v0 as: **Claude Code hooks appending events to an NDJSON file, renderer polling that file via a `?live=1` URL flag, engine untouched**. No server, no watchdog (deferred), no actor inference beyond path-based mapping.

The five knobs (settled in chat with Niklavs):

- **Transport:** polling `state.ndjson` every 500ms. No SSE / WebSocket. Works on `file://` with zero infrastructure.
- **Replay mode:** kept as the default URL. Live is opt-in via `?live=1`.
- **Read events:** coalesced. Move events only fire when the actor's building changes; reads still emit `log` events but are visually demoted.
- **Active player inference:** wisp by default. Hooks have no visibility into the address-routing cue at message start, so unscoped-as-wisp is the honest fallback. Smarter inference deferred.
- **Page launch:** manual. Niklavs opens the tab when he wants to watch. No session-start auto-open.

**Alternatives considered.**

- **Server + SSE.** Lower latency, smoother updates. Rejected for v0: requires running a Python process alongside Claude Code, breaks the single-HTML-file constraint inherited from [[D-008_iso_replay_v0_over_three_js]], and 500ms polling is already faster than the cadence of human-readable narrative.
- **`watchdog` filesystem watcher as primary source.** Catches manual edits + git commits but misses Read / Glob / Grep — the interesting motion. Hooks cover the Claude side natively. Watchdog deferred to a "phase 2" if non-Claude writes turn out to matter visually.
- **Mutate-in-place `state.json` (as Q-007 originally sketched).** Rejected for append-only NDJSON: safer with concurrent writers, tail-only-parse on the renderer side, trivially `tail -f`-able while debugging.
- **Auto-spawn the page on session start.** Rejected: annoying when Niklavs doesn't want to watch. Manual launch is one keystroke.

**Consequences.**

- The engine surface (timeline + `applyEvent` dispatch + RAF tick + CSS transitions) is **preserved**. Only the event-loading code branches on `?live=1`. This honours the asset-agnostic-engine principle established in [[D-008_iso_replay_v0_over_three_js]] and reinforced in [[S009]]'s respawn.
- Event vocabulary stays identical to the baked `EVENTS` array — `move`, `log`, `spawn-dwarf`, `despawn-dwarf`, `spawn-wisp`, `despawn-wisp`, `session-start`, `commit`. Schema adds `wallTime` (ISO timestamp) and `source` (`hook` | `watchdog` | `manual`). The `t` field becomes "ms since stream start," computed by the renderer.
- The path → building / path → actor lookup that's currently *implicit* in the baked EVENTS gets **extracted** to a shared module/JSON, reused by both the hook script and the renderer (for sanity-checks and future watchdog).
- New Claude Code hooks under `developer-braindead/.claude/hooks/` (separate from the architectural hooks in `gielinor/.claude/hooks/`). `PreToolUse` + `PostToolUse` on `Read | Edit | Write | Glob | Grep | Task`, scoped to paths under `brain/`. Hook writes append-only to `experiments/visualizer/state.ndjson`.
- Dwarves: `Task` tool invocation triggers `spawn-dwarf` (Pre) and `despawn-dwarf` (Post). Dwarf ID = increment from tail of NDJSON. Parent = current active player or wisp.
- Replay mode (the existing baked `EVENTS` array + git log) keeps shipping as the demo case. Live is for self-observation; replay is for showing people.
- If live-mode reveals that read-event noise is too much even with coalescing, the next iteration tightens the heuristic — but the engine still doesn't change. That's the design promise.

**Steps (~half-day, each independently shippable).**

1. Extract path → building / path → actor mapping out of baked EVENTS into a shared lookup.
2. One hook, `Edit | Write` only. First live move on the page.
3. Add `Read | Glob | Grep` with coalescing.
4. `Task` → spawn / despawn dwarves.
5. Bootstrap-from-tail: opening the page mid-session replays the existing NDJSON with `instant=true` to bring the scene to current state.

Optional follow-ups deferred: idle indicator, `watchdog` for non-Claude writes, smarter active-player inference, SSE upgrade.

**Session ref.** [[S010]] (in progress).

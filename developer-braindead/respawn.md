# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S015]], pre-commit).

## Where we are

[[S015]] was a quick follow-up after S014 closed — two live-mode bugs surfaced when Jebrim spawned dwarves in parallel and got tested in the wild. Both fixes are landed but **not yet verified against a real Jebrim Task spawn** — that's first thing next session.

**Fix 1 — parent inference** (`infer_dwarf_parent`). Was walking the global stream for the last `move` event, which picked braindead's session-close move from a long-closed dev-brain session. Now prefers the most recent `intent` event (cleanest per-session anchor — every turn writes one) inside a 10-minute recency window. Falls back to `move` only if no recent intent exists.

**Fix 2 — sub-agent attribution via `agent_id`** (new `attribute_to_dwarf`). Docs at `code.claude.com/docs/en/hooks.md` confirm hook payloads carry `agent_id` on sub-agent tool calls (constant across one sub-agent's lifetime). Bound agent_id → spawning Agent's `tool_use_id` on first sighting via FIFO match against a new `pendingAgentBind` queue. Once bound, sub-call writes emit `move` events under the dwarf's id; the dwarf sprite walks the map instead of sitting at spawn. Renderer side: fixed `ensureActorExists` regex (was `dwarf-`, actual IDs are `D1`/`D2`/...); dwarf bubbles persist through moves (task description, not per-turn intent); bubble slides along the move via `renderIntent` after each move event.

[[S014]] background: two visualizer rounds (polish + aesthetics) plus the Task→Agent hook-matcher fix. Pond gone, paths curved, trees scattered, walls textured. Three commits in S014: `4585a12`, `15c8de8`, `750a559`.

## Next concrete step — START HERE

**Verify S015 dwarf attribution in the wild.** Both fixes are landed but only smoke-tested with a mocked payload. Real verification needs Jebrim (or any player session) to spawn an Agent and do work inside it. Watch `state.ndjson` and the live visualizer:

1. Tail the stream: `tail -f developer-braindead/experiments/visualizer/state.ndjson | grep -E "spawn-dwarf|move|despawn-dwarf"`.
2. Have a player spawn an Agent. Expect:
   - `spawn-dwarf` event with correct `parent` (the spawning player) and initial `at`.
   - First sub-agent tool call → `move actor:Dn to:<building>` (binding happened) plus a log line prefixed with `Dn`.
   - Subsequent sub-calls in different buildings → more `move` events for the same `Dn`.
   - `despawn-dwarf` when the Agent returns.
3. In the browser at `?live=1`: dwarf sprite walks across the map, bubble (task description) slides with it.

Failure modes to watch for: (a) `agent_id` field absent or named differently in actual payloads (docs vs. reality drift); (b) FIFO bind-on-first-sighting picks wrong dwarf when multiple Agents spawn in rapid succession before any sub-call lands; (c) renderer's `move` handler chokes on `actor:Dn` because `actor-Dn` element exists but `moveActor` fails some assumption.

**Then resume visualizer iteration** from S014's open candidates:

- **Curve magnitude.** 14–22% of segment length might over- or under-bow some pairs. Single-line knob in `pathControl()`.
- **Tree distribution.** 130 candidates, perimeter-weighted. If middle still reads bare or edges still read thick, tune `TREE_CANDIDATES` and the `accept = (1 - edge) * 0.85 + 0.06` mix.
- **Wall texture density.** `wallTexture()` derives course count from `h / 14` for stone, and uses 6 planks for wood. Tower and small workshop may want different counts.
- **Roof shingle rows.** `roofTexture()` derives from `r / 14`. The tall Spellbook Tower has r=84 → 6 rows, might be too busy; the workshop has r=14 → 1 row, might be too sparse.
- **Per-building polish backlog from [[S009]].** The Inn, Bank, Hall of Mirrors, Keepsake Vault, Inbox Square could still use idiosyncratic character beyond the generic stone-vs-wood split.

Other live threads:

- **Thread A from S013 — verify visualizer feature set end-to-end.** Still outstanding from S011/S012/S013. Especially worth re-running now that ensureActorExists self-heals the braindead/wisp sprite case.
- **Thread B — observe the harvest pump.** No code; watch what the next 3–5 sessions' harvests produce, drift to aspirational drafts, bank drafts-gate friction.

Iteration menu (deferred from earlier, no priority assigned):

- **Idle indicator / watchdog for non-Claude writes / smarter active-player inference / SSE upgrade.** D-009 deferred.
- **Aesthetic backlog from [[S009]].** Per-building character (see above).
- **Read-event noise tuning.**

## Open at the start of next session

- **S015 verification — first priority.** Confirm `agent_id` attribution works against a real Jebrim Task spawn.
- Visualizer Round 3 iteration (whatever bothers you when you look at the new map).
- Browser-side verification (Thread A — outstanding since S011).
- Harvest pump observation (Thread B).
- **§C Pilot definition** — data source, "concerning" definition, output channel. Unchanged.
- **§H.3 brain-zone taxonomy** — content for `player/working-agreements.md`. Not blocking.
- **§H.4 identity ↔ main-brain interaction** — how `examine/I-NNN` entries here interact with main-brain `examine/`. [[I-002]] is a candidate for export.

## Carried-over observations

From [[S015]] (new, one incident): **shipping behind "the docs say X" is risky in this codebase because the docs are right but the integration is novel.** `agent_id` is documented; whether it lands the way I read it depends on payload shape, FIFO assumptions, and renderer-side glue. Smoke test ≠ live test. Next-session verification is the actual signal.

From [[S015]] (separate observation): **delete discipline isn't enforced for dev-brain infrastructure.** Used `rm -f` on a probe script without thinking; only realised after that the block-deletes hook is gielinor-scoped. Even for ephemeral infrastructure code, the discipline is "no deletes" — move to a `.claude/hooks/archive/` slot or just don't write the file in the first place if it's truly temporary.

From [[S014]] (new, two-incident pattern strengthening): **the renderer needs to be self-healing because the hook stream is a lossy substrate.** Two distinct bugs this session boiled down to "the event the renderer needed was never emitted" — Braindead's `spawn-braindead` skipped because `state-actors.json _mode` was stale, and Jebrim's `spawn-dwarf` skipped because the brain-root matcher was on the old tool name. The first I fixed in the renderer (auto-spawn on first move/intent); the second I fixed at the hook layer. Pattern: **don't assume the upstream emitted what you'd render against — defend in the renderer too.** Companion to [[I-002]] (render in your head before shipping it) — this is the runtime version: render assuming partial data, because the upstream is allowed to be imperfect.

From [[S014]] (one incident): **tool renames upstream are silent regressions.** `Task → Agent` broke the brain-root hook with no error message — just zero events on a path that used to fire. Worth checking the other side: are there places where the renderer or other hooks key off a tool name that may have already moved?

From [[S013]] (still candidate, two incidents now): **the procedure was right; the procedure assumed a state that didn't exist.** First Jebrim alching (S012/S013) found near-empty layers because Pump 2 wasn't installed yet — the same shape as S010's live-vs-replay miss ([[I-002]]). Today's two renderer/hook bugs are the same shape: the *renderer* assumed `spawn-*` would arrive; the *hook* assumed the tool was still named `Task`. Pattern now at 4 incidents — strong enough to draft an `I-NNN` if/when bankstanding next runs.

From [[S013]] (separate observation): **uncommitted work occupies the ID space.** Confirmed pattern; nothing new here.

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss.**

From [[S009]]: **mental UI preview must include z-order and all collision targets.**

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]]: **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.**

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S015_dwarf_attribution_via_agent_id.md` — most recent session (untested in prod)
3. `quest-log/S014_visualizer_polish_and_aesthetics_pass.md` — S014
4. `quest-log/S013_close_session_harvest_pump.md` — harvest pump
5. `bank/decisions/D-012_close_session_harvest_pump.md`
6. `bank/decisions/D-013_braindead_character_and_workshop.md`
7. `bank/decisions/D-010_visualizer_intent_narration.md`
8. `bank/decisions/D-009_visualizer_live_mode_v0.md`
9. `bank/decisions/D-008_iso_replay_v0_over_three_js.md` — iso-vs-3D (still load-bearing)
10. `experiments/visualizer/index.html` — the artifact being iterated
11. `experiments/visualizer/_README.md` — how to run both modes
12. `experiments/visualizer/path-map.json` — shared lookup (hook + renderer)
13. `.claude/hooks/emit-event.py` (under `developer-braindead/`) — live-mode + intent + mode-marker hook; now Agent|Task aware + dwarf attribution
14. `.claude/hooks/emit-commit-event.py` (under `developer-braindead/`) — post-commit emitter for the COMMITS lane
15. `bank/open-questions/Q-007_gielinor_visualizer.md` — points at D-009; deferred follow-ups
16. `bank/plan.md` — current mission state

`bank/decisions/`, `bank/assumptions/`, `bank/open-questions/`, `bank/risks/` are reference material — open as cited.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during aesthetic iteration**. State additions across S009–S015 are layered on top of the dispatch surface, not changes to it. Keep extending, don't rewrite.

S014 added: `applyEvent` reads `ev.wallTime` for live-mode timestamps; `ensureActorExists()` runs at the head of `move` + `intent`. S015 added: move handler skips `clearIntent` for dwarf actors (matches `/^D\d+$/`) and re-runs `renderIntent` after every move so bubbles slide with sprites. All additive.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.

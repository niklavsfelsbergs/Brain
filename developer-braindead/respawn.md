# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S016]], pre-commit).

## Where we are

[[S016]] was a pure-design session. Niklavs asked for the visualizer to surface "what players are doing" more clearly and frequently. The output is [[D-014]] — a chat panel below the map, fed by three streams: the existing per-actor intent file (cap raised 60 → 100 chars, bubble wraps to two lines centered, same string feeds bubble *and* chat), a new global authored **narration channel** (`.claude/narration.txt`, system voice for broader-scope context like *"Bankstanding phase 0 begins"*), and a new **`action` event** emitted by the hook on Edit/Write/Bash/Grep/Glob (Read skipped). Plus a discipline rule: intent = *why/scope*, action = *which file/command*, so the two don't mirror each other in chat.

No code shipped. Implementation touches three surfaces (hook, renderer, protocol) and is non-trivial — recommend breaking into smaller PRs (chat panel + intent cap first, narration second, actions third).

**S015 is still untested in the wild.** The `agent_id` dwarf attribution and the parent-inference fix landed in code last session but were only smoke-tested with a mocked payload. **Verifying that against a real Jebrim Task spawn remains the first step** — it should land before D-014 implementation, because the chat-panel work assumes dwarf attribution works.

## Next concrete step — START HERE

**Step 1 — verify S015 dwarf attribution in the wild.** Unchanged from S015's close. Tail `developer-braindead/experiments/visualizer/state.ndjson` and watch a real player session spawn an Agent. Expect `spawn-dwarf` with correct parent, `move actor:Dn` events as the dwarf's sub-calls land in different buildings, sliding bubble, despawn on return. Failure modes: `agent_id` field absent/named differently in actual payloads; FIFO bind-on-first-sighting misattributing under rapid-fire spawns; renderer `move` handler choking on `actor:Dn`.

**Step 2 — implement [[D-014]].** Recommend splitting:

1. **Chat panel + intent cap.** Build the `#chat-panel` div, wire `applyEvent` cases for `intent` and the existing system events (`move`, `spawn-dwarf`, `despawn-dwarf`). Bump intent truncation 60 → 100 chars in `emit-event.py`. Update bubble SVG to wrap to two lines centered. Smallest useful slice; ships history-of-bubbles immediately.
2. **Narration channel.** Add `.claude/narration.txt` branch in the hook; new `narrate` event in renderer rendered muted/italic with `*` prefix. Gitignore the file.
3. **`action` event.** Extend the hook's PreToolUse path to emit `action` events for Edit/Write/Bash/Grep/Glob (skip Read). Add `applyEvent` case for `action`. Test path prettification only once chat is in use and bad cases surface.
4. **Protocol additions.** Update `gielinor/meta/communication-protocol.md` with the new cap, the narration channel, and the intent-vs-action discipline rule. Also fix the drift: `wisp.txt` → `braindead.txt` for dev-brain mode.

**Step 3 — resume visualizer iteration** from S014's open candidates if appetite remains: curve magnitude, tree distribution, wall texture density, roof shingle rows, per-building polish from [[S009]].

Other live threads:

- **Thread A from S013 — verify visualizer feature set end-to-end.** Still outstanding. Worth re-running once D-014 lands.
- **Thread B — observe the harvest pump.** No code; watch what the next sessions' harvests produce, drift to aspirational drafts, bank drafts-gate friction.

Iteration menu (deferred, no priority assigned):

- **Idle indicator / watchdog for non-Claude writes / smarter active-player inference / SSE upgrade.** D-009 deferred.
- **Aesthetic backlog from [[S009]].** Per-building character.
- **Read-event noise tuning.** May become moot once chat shows what's happening — revisit after D-014 ships.

## Open at the start of next session

- **S015 verification — first priority** (unchanged).
- **D-014 implementation** — broken into the four sub-steps above.
- Visualizer Round 3 iteration (S014 candidates).
- Browser-side verification (Thread A — outstanding since S011).
- Harvest pump observation (Thread B).
- **§C Pilot definition** — data source, "concerning" definition, output channel. Unchanged.
- **§H.3 brain-zone taxonomy** — content for `player/working-agreements.md`. Not blocking.
- **§H.4 identity ↔ main-brain interaction** — how `examine/I-NNN` entries here interact with main-brain `examine/`. [[I-002]] is a candidate for export.

## Carried-over observations

From [[S016]] (new): **"players communicate" in dev-brain mode probably means the visualizer, not the chat preamble.** First read landed on the comm-protocol meta-doc; principal corrected to the on-screen surface. Cheap correction this time; worth holding the bias next time someone says "communication" while the visualizer is the active artifact.

From [[S015]]: **shipping behind "the docs say X" is risky in this codebase because the docs are right but the integration is novel.** `agent_id` is documented; whether it lands as read depends on payload shape, FIFO assumptions, and renderer-side glue. Smoke test ≠ live test.

From [[S015]] (separate): **delete discipline isn't enforced for dev-brain infrastructure.** Used `rm -f` on a probe script without thinking; block-deletes hook is gielinor-scoped. Even for ephemeral infrastructure code, discipline is "no deletes" — move to a `.claude/hooks/archive/` slot or just don't write the file if it's truly temporary.

From [[S014]] (two-incident pattern strengthening): **the renderer needs to be self-healing because the hook stream is a lossy substrate.** Two bugs both boiled down to "the event the renderer needed was never emitted." Pattern: **don't assume the upstream emitted what you'd render against — defend in the renderer too.** Companion to [[I-002]] (render in your head before shipping) — runtime version: render assuming partial data.

From [[S014]] (one incident): **tool renames upstream are silent regressions.** `Task → Agent` broke the brain-root hook with no error message. Worth checking other places that key off tool names.

From [[S013]] (still candidate, four incidents now): **the procedure was right; the procedure assumed a state that didn't exist.** Four-incident pattern — strong enough to draft an `I-NNN` if/when bankstanding next runs.

From [[S013]]: **uncommitted work occupies the ID space.** Confirmed pattern.

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss.**

From [[S009]]: **mental UI preview must include z-order and all collision targets.**

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]]: **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.**

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S016_visualizer_chat_panel_design.md` — most recent session (design only, no code)
3. `bank/decisions/D-014_visualizer_chat_panel.md` — the design to implement
4. `quest-log/S015_dwarf_attribution_via_agent_id.md` — previous session (untested in prod)
5. `quest-log/S014_visualizer_polish_and_aesthetics_pass.md`
6. `bank/decisions/D-013_braindead_character_and_workshop.md`
7. `bank/decisions/D-010_visualizer_intent_narration.md` — the contract D-014 extends
8. `bank/decisions/D-009_visualizer_live_mode_v0.md`
9. `bank/decisions/D-008_iso_replay_v0_over_three_js.md` — iso-vs-3D (still load-bearing)
10. `experiments/visualizer/index.html` — the artifact being iterated
11. `experiments/visualizer/_README.md` — how to run both modes
12. `experiments/visualizer/path-map.json` — shared lookup (hook + renderer)
13. `.claude/hooks/emit-event.py` (under `developer-braindead/`) — live-mode + intent + mode-marker hook
14. `.claude/hooks/emit-commit-event.py` (under `developer-braindead/`) — post-commit emitter for the COMMITS lane
15. `bank/open-questions/Q-007_gielinor_visualizer.md` — points at D-009; deferred follow-ups
16. `bank/plan.md` — current mission state

`bank/decisions/`, `bank/assumptions/`, `bank/open-questions/`, `bank/risks/` are reference material — open as cited.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during aesthetic iteration**. State additions across S009–S015 are layered on top of the dispatch surface, not changes to it. Keep extending, don't rewrite.

D-014 adds: `narrate` and `action` events alongside existing `intent`/`move`/`spawn-dwarf`/`despawn-dwarf`. New `#chat-panel` DOM node consumes the stream in parallel with the map. All additive — same engine.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.

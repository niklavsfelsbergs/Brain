# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-22 (end of [[S028]] continuation — deities scaffold + bubble layout + background-dwarf lifecycle).

## Where we are

[[S028]] shipped two things end-to-end and one mid-session pivot:

**1. Subtask channel** — design from [[subtask-channel-design]] picked up as S027's Step 2. A third visualizer channel between intent (agent voice, slow, scope) and action (hook voice, fast, raw) — a hook-authored natural-language micro-step that updates the bubble at medium cadence. Slices 1–3 shipped:

- Slice 1 (hook): `subtask_for(tool_name, tool_input)` + `bash_subtask(cmd)` + `BASH_SUBTASK_TABLE` + `emit_subtask(...)` in `emit-event.py`. Wired into `handle_bash`, both branches of `handle_write_or_read`, and `handle_task_pre`. Bash verb table covers git family / file-nav / file-read / interpreters / echo / fallback. Smoke test in `experiments/subtask_smoketest.py`.
- Slice 2+3 (visualizer): `setSubtask`, `case 'subtask'` in `applyEvent`, `intents[actorKey].subtask` field, `renderIntent` extended to lay subtask as muted-italic line 2 under the intent. Intent wins ties (verbose intent suppresses subtask); no orphan bubbles without intent.

**Slice 4 (debounce) deferred** — pending live observation. Starting numbers from the design: 500ms min update, 1.5s aggregation, 2s reset gap. May not be needed at all; typical 5–10 calls / 30s is already 3–6s between updates.

**Deviation from design.** Doc recommended COMMS append for subtask events; held off — action lines already cover that surface, near-duplicate. Revisit if bubble-only feels insufficient.

**2. Guthix — the bankstanding deity** — surfaced during live test of subtask. Principal saw Jebrim's session running bankstanding and asked *"why is my Jebrim walking around as a wisp?"* Subtask events made the wisp's bankstanding work feel intensely Jebrim-shaped, exposing an architecture/intuition mismatch the old "bankstanding = system voice = wisp" framing papered over. Wisp was carrying two unrelated meanings — unscoped session + system curation; the second didn't fit.

Shipped end-to-end:

- **Visualizer.** New CSS palette (`--guthix-robe` etc.), float keyframes (`guthix-float`, 3800ms, ±6px), glow filter (`guthixGlow`), full pixel-art sprite (hooded green robe, white beard, wooden staff with green gem, soft aura). `ACTOR_Y_OFFSET['guthix'] = -48` so he floats above buildings on every move + instant scrub. `NON_WALKING_ACTORS = {'guthix'}` suppresses `.walking` class + dust trail; chat says "drifts to" instead of "walks to." spawnGuthix / despawnGuthix parallel to wisp/braindead; default building `lorebook-library`. `ensureActorExists` self-heal branch. Legend, COMMS tab, speaker dot, filter, `.user` color, `deriveSpeaker` precedence — all wired.
- **Hook.** `GUTHIX_ACTOR`, `GUTHIX_DEFAULT_BUILDING`, `is_guthix_session()`, `_handle_guthix_lifecycle()` runs from `handle_intent_write` — emits `spawn-guthix` + log on first guthix intent write per session, `despawn-guthix` + log when intent flips back to a non-guthix actor or session ends. Session ownership tracked via `_guthix_session_id` in `state-actors.json` (parallel to braindead). Wisp-fallback paths in `handle_write_or_read`, `current_main_actor`, and `infer_dwarf_parent` now check `is_guthix_session()` between dev-brain and the recency walk.
- **Meta docs.** New `gielinor/meta/guthix.md` (persona, voice, write reach, Invocation contract menu, Returning section). `modes.md` bankstanding section rewritten — voice = Guthix, intent file = `guthix.txt`, two entry routes (`Hey Guthix` and `let's bankstand`). `communication-protocol.md` active-actor table adds the bankstanding route. `write-rules.md` adds "Voice per ritual" paragraph. `gielinor/CLAUDE.md` adds `Hey Guthix, ...` to "Player invocation by address" with matching rules + mid-session switching extended.

**3. Live-test debugging that shipped same session.**

- **Map wipe.** Truncated state.ndjson + reset state-actors / state-dwarves / state-gnomes / state-instances. Visualizer self-heals on truncation (B5).
- **Braindead bubble routing bug fixed.** `handle_intent_write` only stripped `-<sid8>` suffix for `PLAYER_ACTORS` — `braindead-<sid8>.txt` emitted `actor="braindead-<sid8>"`, visualizer couldn't route. Added `NON_PLAYER_SUFFIX_ACTORS = {"braindead", "guthix", "wisp"}` and extended the check. Bug silently present since D-018 chunk 3.
- **Disk-fallback session→actor recovery.** Wipe surfaced that a session whose state.ndjson events got cleared falls back to wisp because the recency walk returns nothing. Added `_session_actor_from_disk()` — checks `.claude/intent/<actor>-<sid8>.txt` on disk (intent file outlives state.ndjson). Plugged into three fallback paths.
- **Protocol tightened.** Per-session intent filenames now mandatory for every actor (not just players). Bare-file fallback removed.

## Next concrete step — START HERE

**Step 1 — Scale up the whole map.** Principal's close ask: *"We need to give the map room to breathe. Lets make the scale of everything bigger so the agents have more room to spread out."* With 7+ background dwarves clustering at one building plus the parent + bubbles, even after the gather-slot + bubble-layout work the map feels cramped. The world geometry (`TILE_W`, `TILE_H`, building footprints, STAND positions, viewport crop in `buildGround`, the iso transformation in `isoToScreen`) all assume a tighter scale. Worth a focused pass:

- Increase `TILE_W` / `TILE_H` proportionally (current values define base tile size).
- Scale building dimensions to match — they're drawn at fixed sizes in their respective spawn-building functions / SVG definitions.
- Re-test STAND positions and `GATHER_SLOTS` offsets — the current ±58px far-side slots may need to grow with the world.
- Consider whether sprites themselves scale too, or just the world (probably keep sprites at current size; the cluster gets more room).
- Adjust viewport crop in `buildGround` and the SVG viewBox so the bigger world still fills the visible frame.
- Watch out for the path-map polylines (`path-map.json`) — they may need scaling too if they exist in pixel coordinates rather than building-relative.
- Cross-cutting test: scrub the demo timeline + run live and verify everything still places correctly.

The whole change probably touches `experiments/visualizer/index.html` only (no hook changes needed; building keys and event shapes unchanged).

**Step 2 — Live test Guthix end-to-end.** Open the visualizer in live mode and cue bankstanding via either entry route:

- `Hey Guthix` (alone or with `, what can you do`) → expect the menu surface.
- `Hey Guthix, [specific request]` → expect direct execution.
- `let's bankstand` from any session → expect the same result.

Watch for:

- Sprite renders correctly (green hooded robe, white beard, staff with green gem, soft aura).
- Float behavior — slow ±6px bob, ~48px above the building, no walking step animation, no dust trail.
- "Guthix drifts to X" chat lines (not "walks to").
- COMMS tab `GUTHIX` collects his lines; filter works.
- Despawn fires cleanly when intent flips back to a player or session ends.
- Bubble fan-up + gather-slot clustering work cleanly with multiple actors at the same building.
- Background dwarves stay visible while working; despawn after ~5min idle.

Tune if needed: float amplitude, Y-offset, robe colors, staff position, gather-slot offsets, bubble-layout `PAD`, idle-despawn threshold `IDLE_BG_SEC`.

**Step 3 — Subtask debounce decision.** After a few minutes of real work observed, decide whether to ship slice 4. Default to no debounce if the bubble feels alive without strobing.

**Step 4 — Replay-mode demo arcs.** Deferred subtask + Guthix demos in the EVENTS array. Restructure a session arc to include intent + subtask + action together (subtask demo) and a bankstanding arc with `spawn-guthix` / `despawn-guthix` (Guthix demo).

**Step 5 — Recover Jebrim session 58f8e88a.** That session is using bare `jebrim.txt` (pre-D-018-chunk-3 pattern). Disk fallback doesn't recover bare files. Either (a) nudge that window so it writes its intent again and the hook lands an event, or (b) wait for its next respawn — it'll re-read the tightened protocol and start using `jebrim-58f8e88a.txt`. Disk-fallback will cover it from then on.

**Step 6 — Drafts triage** (carried S018 → S019 → S020 → S021 → S022 → S026 → S027):

- `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md` — promote to `lorebook/decisions/D-NNN_*.md`.
- `gielinor/players/jebrim/keepsake/proposals/2026-05-21_eu-tender-2026.md`.
- `gielinor/players/jebrim/spellbook/drafts/skills/moving-target-decomposition.md` (Jebrim alching).
- `gielinor/players/jebrim/niksis8_character/drafts/` (S017-era + 2026-05-21-prefers-evidence-over-premature-infrastructure).

**Step 7 — Audit follow-up notes** (carried from S027):

- `bank/decisions/`: *recon dwarves should cross-check audit findings against intervening commits before bundling.* Three closed-but-reported items across S021 and S027.
- B1 day/night cadence — 87s/day may be too fast.
- B9 hook D-018 read race — separate session at the hook level.

**Step 8 — First live gnome spawn** (carried S020+). Validates the boundary cascade + session-scoped substates under sub-agent activity. Candidate: Jebrim alching gnome.

**Step 9 — Q-008 visualizer aliveness pick** (carried). Step 3 (subtask debounce) now subsumes the urgency of this somewhat.

## Open at the start of next session

- **Scale up the map** — Step 1. First action.
- **Live test Guthix** — Step 2.
- **Subtask debounce decision** — Step 3.
- **Replay demos** — Step 4.
- **Jebrim 58f8e88a recovery** — Step 5 (probably resolves itself by next respawn of that session).
- **Drafts triage backlog** — Step 6.
- **Audit follow-up notes** — Step 7.
- **First live gnome spawn** — Step 8.
- **Q-008 pick** — Step 9.
- §C Pilot definition, §H.3 brain-zone taxonomy, §H.4 identity ↔ main-brain interaction — unchanged.

## Carried-over observations

From [[S028]] (new): **subtask exposes architecture/intuition mismatches that quieter channels papered over.** Before subtask, the wisp's bankstanding activity was a single "Bankstanding complete" intent flicker — easy to miss. With subtask, every Read/Bash showed up under the wisp sprite, and the mismatch with the principal's mental model became obvious within minutes. Worth a `bank/decisions/` note: *new instrumentation channels are also surfacing tools for architecture review.*

From [[S028]] (new): **silent suffix-strip bugs hide until the surface gets busy.** The `handle_intent_write` PLAYER_ACTORS-only check shipped weeks ago and never produced a Braindead bubble for sessions using per-session intent files — but the principal didn't notice because bubbles came from elsewhere (recency walks, fallback paths). Subtask + state wipe stripped away the noise and the missing bubble became visible immediately. Pattern: *infrastructure bugs are easier to spot once redundant signal is removed.*

From [[S028]] (new): **the "bare intent file" fallback was never load-bearing — only confusing.** The protocol allowed bare files as a fallback when the session env var was unavailable. Result: sessions silently fell back, lost session ownership, broke recovery paths. Removing the fallback (S028 protocol tightening) is a strict simplification. Worth a `lorebook/drafts/` entry on *"defaults that exist only for absent inputs accumulate hidden coupling — prefer a hard surface."*

From [[S027]] (still relevant): **recon dwarves should cross-check audit findings against intervening commits before bundling.** Pattern worth canonicalizing as a `bank/decisions/` note.

From [[S027]] (still relevant): **a multi-fix audit pass converts the audit doc from a primer into a verification checklist.** Worth canonicalizing as a two-step workflow when an audit spans sessions.

From [[S023]] (still relevant): **shared global state at brain root is hostile to parallel Claude sessions.** S028's `_guthix_session_id` follows the same gating pattern as `_mode_session_id`. Cumulative incident pattern now spans S014, S022, S023, S027, S028.

From [[S023]] (still relevant): **watching-it-run finds bugs the audit-and-validate phase missed.** S028 confirms — three bugs (stale sprites, missing braindead bubble, jebrim-as-wisp attribution) were all found by the principal looking at the screen, not by code review.

From [[S022]] (still relevant): **audit-then-validate finds different bugs than either alone.**

From [[S022]] (still relevant): **shared global state is hostile to parallel Claude sessions.**

From [[S021]] (still relevant): **the audit-then-validate pattern works for accreted infrastructure.**

From [[S021]] (still relevant): **cross-file invariants need an explicit list when ≥3 surfaces enumerate the same set.** S028 adds a fifth surface — the suffix-strip prefix set now needs to cover players + braindead + guthix + wisp; the disk-fallback candidate set is the same.

From [[S020]] (still relevant): **architectural guarantees need a live failure test, not just code review.** S023, S027, S028 — six-incident pattern now.

From [[S020]] (still relevant): **the claude-code-guide agent earned its spawn.**

From [[S019]] (still relevant): **a new role's blocklist is easier to get right than its allow-list.**

From [[S019]] (still relevant): **single source of truth for tunable numbers is worth one hop.**

From [[S018]] (still relevant): **the quest log is the gravitational center; other layers starve without explicit routing.** Candidate for an `I-NNN` next bankstanding.

From [[S018]] (still relevant): **bundle big structural decisions; resist piecemeal landing.** S028 followed this — Guthix landed end-to-end in a single session despite being a mid-session pivot.

From [[S017]] (still relevant): **spec docs that prescribe DOM/structure without inventorying what already exists will ship suboptimal designs.**

From [[S017]] (still relevant): **heuristics that walk back through `state.ndjson` need to remember the stream is cross-session.** S028's disk-fallback acknowledges that state.ndjson itself is volatile under truncation.

From [[S017]] (still relevant): **emulating a specific UI's look means font and palette must change together.**

From [[S016]]: **"players communicate" in dev-brain mode probably means the visualizer, not the chat preamble.**

From [[S015]]: **shipping behind "the docs say X" is risky in this codebase because the docs are right but the integration is novel.**

From [[S015]] (separate): **delete discipline isn't enforced for dev-brain infrastructure.**

From [[S014]] (now ten-incident pattern with S018, S020, S022, S023, S027, S028): **the procedure was right; the procedure assumed a state that didn't exist.**

From [[S014]]: **the renderer needs to be self-healing because the hook stream is a lossy substrate.** S028's disk-fallback is a new instance of this discipline.

From [[S014]]: **tool renames upstream are silent regressions.**

From [[S013]]: **uncommitted work occupies the ID space.**

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss.**

From [[S009]]: **mental UI preview must include z-order and all collision targets.**

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]]: **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.**

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S028_subtask_channel_and_guthix.md` — what just shipped (subtask channel + Guthix end-to-end + post-ship live-fix wave).
3. `bank/research/subtask-channel-design.md` — original design; subtask slices 1–3 implement most of it. Slice 4 still open.
4. `gielinor/meta/guthix.md` — the new bankstanding deity. Persona, voice, Invocation contract menu.
5. `gielinor/meta/modes.md` (rewritten bankstanding section), `gielinor/meta/communication-protocol.md` (per-session intent rules tightened), `gielinor/meta/write-rules.md` (Voice per ritual paragraph), `gielinor/CLAUDE.md` (Hey Guthix routing).
6. `experiments/visualizer/index.html` — Guthix sprite + float behavior; subtask state + render.
7. `developer-braindead/.claude/hooks/emit-event.py` — subtask synthesis, Guthix lifecycle, disk-fallback. Still hosts B9 (hook D-018 read race) as deferred work.
8. `bank/research/visualizer-audit-S026-prep.md` — S027 worked this. Mostly historical; open-questions section still pending live verification.
9. `bank/open-questions/Q-008_visualizer_aliveness.md` — parked.
10. `gielinor/.claude/hooks/gnome-write-boundary.py` + `dwarf-write-boundary.py` + `block-sub-spawn.py` — still untested under live sub-agent activity.
11. `gielinor/spellbook/skills/spawning-gnomes.md` — gnome operating spec.
12. `gielinor/.claude/agents/gnome.md` — agent config.
13. `gielinor/spellbook/rituals/respawn.md` + `close-session.md` + `alching.md` + `bankstanding.md` — Phase 0 spawn-decisions.
14. `bank/decisions/D-014_visualizer_chat_panel.md`, `D-016_gnomes_subagent.md`, `D-017_parallel_player_instances.md`, `D-018_parallel_session_substrate_isolation.md` — prior decisions.
15. `bank/plan.md` — current mission state.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during fix iteration**. S028 followed this discipline — subtask and Guthix both layered on the dispatch surface; the engine itself wasn't reshaped. Keep extending; don't rewrite.

New event types in S028: `subtask` (hook-authored, medium-cadence micro-step), `spawn-guthix` / `despawn-guthix` (bankstanding actor lifecycle). All five existing event chains (intent, action, narrate, move, spawn-*/despawn-*) untouched.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.

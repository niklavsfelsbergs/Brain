# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-22 (end of dev-brain session that shipped [[D-018]] chunks 1–3 and prepped the S026 visualizer audit).

## Where we are

This dev-brain session **shipped [[D-018]] chunks 1–3 end-to-end** and **prepped the S026 visualizer audit**.

D-018 ships:
- **Chunk 1** (commit `0873ae0`) — `state-actors.json` re-keyed for player-class actors: jebrim/zezima get nested `{ byId: { sessionId: building } }` via new `get_actor_building` / `set_actor_building` helpers. Wisp, braindead, and `_mode*` keys stay flat. Legacy strings still read transparently.
- **Chunk 2** (same commit) — `state-dwarves.json` / `state-gnomes.json` re-keyed: top-level shape now `{ nextId, bySession }`. `nextId` stays globally monotonic (parallel sessions can't both spawn "D1"); `byToolUseId` / `pendingQueue` / `byAgentId` / `pendingAgentBind` partitioned per session. `attribute_to_subagent` and `gc_stale_subagents` updated accordingly.
- **Chunk 3** (commit `5172257`) — `gielinor/meta/communication-protocol.md` mandates `<actor>-<sid8>.txt` intent filenames using `CLAUDE_CODE_SESSION_ID`. Hook's dual-read fallback in `_intent_file_candidates` stays for sessions without the env var.

**Bug confirmation under live observation.** A screenshot mid-session showed two parallel Jebrims with **identical bubble text** ("CSV rework home - synthesis, awaiting smoke") after a move. Root-caused live to exactly the on-disk file race D-018 predicted: both Jebrims write to bare `jebrim.txt`, then `_reemit_intent_after_move` falls through to bare and re-emits whichever session wrote most recently. Chunk 3 fix lands but won't take effect for those running Jebrim sessions until their next turn re-reads `meta/`.

S026 audit prep:
- Three Explore dwarves walked `experiments/visualizer/index.html` (3249 lines) in parallel — D1 architecture & rendering, D2 event dispatch & state shapes, D3 CSS / UX / visual polish.
- Synthesized into `bank/research/visualizer-audit-S026-prep.md`: 9 bugs ranked by severity, 10 improvements ranked by payoff, 6 open questions for the running-app verification phase.
- Recommended start order documented; B1 (day/night ignores replay timeline) + B3 (Braindead COMMS gap, S021 C2 still open) + I1 (centralize actor color taxonomy, S021 C1 still open) + I2 (scroll-lock on COMMS) lead.

Prior context that still matters:
- [[S025]] shipped [[D-017]] end-to-end: visualizer renders parallel sessions of the same player as distinct tinted sprites with per-instance bubbles and COMMS prefixes. Open follow-ups from D-017 (none blocking): cross-instance dwarf delegation, accessibility check of tint palette, active-player as `Set`, sprite stacking at 3+ instances per building.
- The S014 → S025 parallel-session race pattern (six incidents by now) is what D-018 closes. Success criterion: "bug surface from parallel-session shared-state races stays flat for 3+ sessions of mixed work."

Open follow-ups from D-017 (none blocking): cross-instance dwarf delegation, accessibility check of tint palette, active-player as `Set` instead of single value, sprite stacking at 3+ instances per building.

[[S024]]'s aliveness pass (idle breath SMIL, ambient particles, day/night overlay, reduced-motion gating, intent re-emit on move) is in place. Aliveness options **4 (NPC wanderers) and 5 (trail echoes) deferred** without committed trigger.

The first **live gnome spawn** is still deferred — now folded into Step 2.

## Next concrete step — START HERE

**Step 1 — Visualizer audit (NEW).** Read `bank/research/visualizer-audit-S026-prep.md` first. It's the primer this session produced via three parallel Explore dwarves (D1 architecture, D2 event dispatch + state, D3 CSS/UX). The doc covers how the renderer works (engine, 14 event types, in-memory state shapes, layer model, CSS systems, modes), 9 bugs ranked by severity with `file:line` refs, 10 improvements with payoff estimates, and 6 open questions that need running-app verification. Recommended start order is at the bottom of the prep doc — B1 day/night-in-replay, B3 Braindead COMMS, I1 color taxonomy, I2 scroll-lock first.

D-018 chunks 1–3 are **shipped this session** (commits `0873ae0` and `5172257`). Hook-side state files now session-isolate per D-018 Category A; `meta/communication-protocol.md` mandates per-session intent filenames. Parallel Jebrim sessions still running at session-close will keep clobbering each other's bubble until their next turn re-reads `meta/`.

**Step 2 — first live gnome spawn (carried from S020 / S021 / S022 / S023 / S024 / S025).** Still the natural validation event for the boundary hook (S020's env→payload-field fix), the visualizer's gnome render path, and audit fixes that only fire under sub-agent activity. The session-gating from [[S023]], the intent-re-emit from [[S024]], the instance-routing from [[S025]], and the session-scoped substates from D-018 are all dependencies to test under sub-agent activity. Audit open question #6 in the S026 prep doc — no `state-gnomes.json` exists on disk yet because gnomes haven't been spawned. Combined-test candidate: a Jebrim alching gnome.

**Step 3 — drafts triage** (carried from S018 → S019 → S020 → S021 → S022). Several drafts still await ruling:

- `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md` — promote to `lorebook/decisions/D-NNN_*.md` to canonicalize the S018 audit's structural decisions.
- `gielinor/players/jebrim/keepsake/proposals/2026-05-21_eu-tender-2026.md` (still untouched).
- `gielinor/players/jebrim/spellbook/drafts/skills/moving-target-decomposition.md` — awaits Jebrim skills-promotion at first Jebrim alching (covered by Step 2 if the gnome runs).
- `gielinor/players/jebrim/niksis8_character/drafts/` (S017-era + `2026-05-21-prefers-evidence-over-premature-infrastructure.md`) — also covered by Step 2 if the gnome runs.

**Step 4 — D-014 + S015 browser verification** (carried from S017). Subsumed by Step 2's combined test if the visualizer is open in live mode while the gnome runs.

**Step 5 — narration channel shakedown** (carried from S021/S022). Used heavily across opens; a deliberate stress test still warrants its own session.

**Step 6 — pick from [[Q-008]]** when ready to make the world feel alive. Recommendation in the entry: NPC wanderers + trail echoes (the two not yet shipped by S024).

Other live threads (carried, lower priority):

- **Substantial un-committed Jebrim work.** Throughout S022/S023 a parallel Jebrim session has been working in `gielinor/players/jebrim/` — S023 (shipping-mart-coverage-audit) closed mid-S022 session, S024 (shipping-agent-rules) opened mid-S023 dev-brain. Inventory files, niksis8_character drafts/confirmeds/rejecteds, spellbook drafts/confirmeds, quest-log entries, modifications to keepsake/current.md. Reconciliation belongs to the next Jebrim respawn, not this dev-brain close.
- **Soft-block tuning** (S018 close-session pre-commit) — three options offered; re-evaluate "abandon" after first fire.
- **Self-observation sweep tuning** (S018 alching step 3a) — cap 0–3; watch first alching pass output (Step 1).
- **Cross-player parity for future players.** Jebrim + Zezima aligned. No template system yet.
- **Possible `I-NNN` from S018** — quest-log-as-vacuum pattern.
- **Possible `lorebook/drafts/` from S020** — *architectural guarantees need a live failure test, not just code review.* S023 makes this a four-incident pattern. Pattern worth canonicalizing.
- **Possible `bank/decisions/` from S021/S023** — *cross-file invariants need an explicit list when ≥3 surfaces enumerate the same set.* And: *parallel-safe attribution requires every shared-state check to be session-gated* (S023). Worth a note at next bankstanding.
- **Possible `bank/decisions/` from S022/S023** — *audit-then-validate finds different bugs than either alone, and watching-it-run finds bugs the audit-and-validate phase missed.* S023's bugs all surfaced under live observation, not in the audit or its fix-validation. Three-incident pattern.

Iteration menu (deferred, no priority assigned):

- **[[Q-008]] visualizer aliveness picks.** Idle breath, ambient particles, day/night, wanderers, trail echoes.
- **Action target prettification** (audit I12). Bash commands show raw command text; could pattern-match common verbs and prettify.
- **Chat scroll-lock UX** (audit I13).
- **Bubble two-line edge cases** (audit I14).
- **Idle indicator / watchdog for non-Claude writes / smarter active-player inference / SSE upgrade.** D-009 deferred (audit I9–I11).
- **Tighten gnome hook allowlist** from `/spellbook/drafts/` to `/spellbook/drafts/skills/` for symmetry with [[D-016]] (audit I17). Phantom risk today.
- **Gnome workshop building** (audit I16). Defer until the gnome has been used a few times.
- **Path-based dev-brain override narrowing.** S022 narrowed only the Bash side; S023 narrowed the path-based side too. Both now session-gated. Should be done — re-open only if a new leak surfaces.

## Open at the start of next session

- **S026 visualizer audit** — Step 1. Read `bank/research/visualizer-audit-S026-prep.md` and execute the recommended start order.
- **First live gnome spawn** — Step 2. Validates the S020 cascade + D-018 session-scoped substates under sub-agent activity.
- **Drafts triage** — Step 3.
- **D-014 + S015 browser verification** — Step 4. Subsumed by Step 2 if the visualizer is open during the gnome run.
- **Narration shakedown** — Step 5.
- **[[Q-008]] pick** — Step 6.
- §C Pilot definition, §H.3 brain-zone taxonomy, §H.4 identity ↔ main-brain interaction — unchanged.

## Carried-over observations

From [[S023]] (new): **shared global state at brain root is hostile to parallel Claude sessions — third incident.** Mitigation pattern has stabilized: gate every shared-state read on `_SESSION_ID`, stamp the writer's session_id into shared state when it sets a mode/marker, only honor overrides when current session matches. S014, S022, S023 all fit the pattern.

From [[S023]] (new): **watching-it-run finds bugs the audit-and-validate phase missed.** The ticker freeze, the inverse-direction Bash misattribution, and the wildcard-glob override hijack all surfaced while the principal had the visualizer open and was observing — not during the audit, not during its fix-validation. Third-tier observation phase to canonicalize.

From [[S022]] (still relevant): **audit-then-validate finds different bugs than either alone.** Static read first, live test second. S023 added a third tier — sustained observation after validation.

From [[S022]] (still relevant): **shared global state is hostile to parallel Claude sessions.** S023 reinforces — same pattern, different surfaces.

From [[S021]] (still relevant): **the audit-then-validate pattern works for accreted infrastructure.**

From [[S021]] (still relevant): **cross-file invariants need an explicit list when ≥3 surfaces enumerate the same set.** Six surfaces enumerate the same 10 buildings in the visualizer; building list could be next. Pattern worth a `bank/decisions/` note.

From [[S020]] (still relevant): **architectural guarantees need a live failure test, not just code review.** S023 makes this a four-incident pattern.

From [[S020]] (still relevant): **the claude-code-guide agent earned its spawn.** Confirms [[D-014]]'s dwarf-spawn heuristic.

From [[S019]] (still relevant): **a new role's blocklist is easier to get right than its allow-list.**

From [[S019]] (still relevant): **single source of truth for tunable numbers is worth one hop.**

From [[S018]] (still relevant): **the quest log is the gravitational center; other layers starve without explicit routing.** Candidate for an `I-NNN` next bankstanding.

From [[S018]] (still relevant): **bundle big structural decisions; resist piecemeal landing.**

From [[S017]] (still relevant): **spec docs that prescribe DOM/structure without inventorying what already exists will ship suboptimal designs.**

From [[S017]] (still relevant): **heuristics that walk back through `state.ndjson` need to remember the stream is cross-session.** Reinforced by S023 — the recency walk needed session-filter to disambiguate; the dev-brain override needed session_id stamping to know whose marker it was.

From [[S017]] (still relevant): **emulating a specific UI's look means font and palette must change together.**

From [[S016]]: **"players communicate" in dev-brain mode probably means the visualizer, not the chat preamble.**

From [[S015]]: **shipping behind "the docs say X" is risky in this codebase because the docs are right but the integration is novel.**

From [[S015]] (separate): **delete discipline isn't enforced for dev-brain infrastructure.**

From [[S014]] (now eight-incident pattern with S018, S020, S022, S023): **the procedure was right; the procedure assumed a state that didn't exist.**

From [[S014]]: **the renderer needs to be self-healing because the hook stream is a lossy substrate.**

From [[S014]]: **tool renames upstream are silent regressions.**

From [[S013]]: **uncommitted work occupies the ID space.**

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss.**

From [[S009]]: **mental UI preview must include z-order and all collision targets.**

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]]: **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.**

## Files to read first

1. `respawn.md` (this file)
2. `bank/research/visualizer-audit-S026-prep.md` — **the primer for Step 1**. How the visualizer works, 9 bugs with line refs, 10 improvements, 6 open questions.
3. `bank/decisions/D-018_parallel_session_substrate_isolation.md` — shipped this session; reference for the per-session substrate model.
4. `experiments/visualizer/index.html` — the audit target (3249 lines).
5. `developer-braindead/.claude/hooks/emit-event.py` — the event producer feeding the visualizer; updated this session with D-018 changes.
6. `bank/research/visualizer-audit-S021.md` — prior audit; C1 (color taxonomy) and C2 (Braindead COMMS) are still open and appear as I1 and B3 in the S026 prep.
7. `bank/open-questions/Q-008_visualizer_aliveness.md` — parked.
8. `gielinor/.claude/hooks/gnome-write-boundary.py` + `dwarf-write-boundary.py` + `block-sub-spawn.py` — boundary hooks, still untested in the wild.
9. `gielinor/spellbook/skills/spawning-gnomes.md` — gnome operating spec.
10. `gielinor/.claude/agents/gnome.md` — agent config.
11. `gielinor/meta/modes.md` — principal/dwarf/gnome axis.
12. `gielinor/meta/communication-protocol.md` — updated this session to mandate per-session intent filenames.
13. `gielinor/spellbook/rituals/close-session.md` + `alching.md` — step 0 spawn-decisions.
14. `bank/decisions/D-014_visualizer_chat_panel.md`, `D-016_gnomes_subagent.md`, `D-017_parallel_player_instances.md` — prior decisions.
15. `bank/plan.md` — current mission state.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during fix iteration**. S023 followed this discipline — every fix layered on top of the dispatch surface, never reshaped it. Keep extending; don't rewrite.

D-014 added `narrate` and `action` events alongside `intent` / `move` / `spawn-dwarf` / `despawn-dwarf`. S020 added `spawn-gnome` / `despawn-gnome`. S022 added nothing new. S023 added `sessionId` as a stamped field on every event — additive metadata, no new event type.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.

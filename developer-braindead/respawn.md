# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-22 (end of [[S025]] — parallel player instances via D-017).

## Where we are

[[S025]] designed and shipped [[D-017]] end-to-end in one session: visualizer renders parallel sessions of the same player as distinct tinted sprites with per-instance bubbles and COMMS prefixes. Hook stamps `instance` on every event from a player-class actor; state-instances.json registry maps `(actor, session_id) → instance`. Validated live on first run — two parallel Jebrim sessions appeared correctly. First tint pass too subtle (+25°), bumped to +140°/+220°/+80° for clear differentiation.

Open follow-ups from D-017 (none blocking): cross-instance dwarf delegation, accessibility check of tint palette, active-player as `Set` instead of single value, sprite stacking at 3+ instances per building.

[[S024]] shipped the first wave of [[Q-008]] visualizer aliveness work plus one bug surfaced and fixed under live observation:

- **Idle sprite breath.** Vertical scale (1 → 0.95 → 1) via inline SMIL `<animateTransform>` on each player's `.bob` group. Switched from CSS to SMIL after the `.actor .bob` descendant selector silently refused to animate while the wisp's direct-class `.wisp-bob` worked fine — root cause not pinned. Final form reads as breath, not float: head compresses ~1.5px, feet drift ~0.35px (imperceptible).
- **Ambient particles.** Forge smoke at braindead-workshop, candle-flicker on lit lorebook-library windows, parchment-flutter on three inbox-square bulletin notes. Keepsake-vault's gem-shine already covered.
- **Day/night hue overlay.** Fullscreen `<rect>` below the vignette, `mix-blend-mode: multiply`, JS interpolates four hour-keyed anchor tints, refreshed every 60s.
- **Reduced-motion gate.** New animations zeroed and overlay hidden under `@media (prefers-reduced-motion: reduce)`.
- **Bug fix — intent re-emit on move.** Visualizer clears player intents on building change, and the hook only emits intent events on intent-file writes — so a working session that calls tools without updating its intent file silently loses its bubble after the first move. Fixed in `emit-event.py` with `_reemit_intent_after_move()` called right after every main-actor move event. Sub-agents skip (no intent file).

Aliveness options **4 (NPC wanderers) and 5 (trail echoes) deferred** without committed trigger — neither on critical path.

[[S023]]'s "watching-it-run finds bugs the audit-and-validate phase missed" pattern reinforced — the intent silence only surfaced under sustained live observation, not the build phase. **Four-incident pattern** now (S014, S022, S023, S024).

The first **live gnome spawn** is still deferred.

## Next concrete step — START HERE

**Step 1 — first live gnome spawn (carried from S020 / S021 / S022 / S023).** Still the natural validation event for the boundary hook (S020's env→payload-field fix), the visualizer's gnome render path, and audit fixes that only fire under sub-agent activity. The session-gating in [[S023]] and the intent-re-emit-on-move from [[S024]] are dependencies to test under sub-agent activity — gnome spawn carries the parent session's `session_id`, so the gnome's tool calls should still attribute correctly via `agent_id` first, then session_id as fallback. Combined-test candidate: a Jebrim alching gnome.

**Step 2 — drafts triage** (carried from S018 → S019 → S020 → S021 → S022). Several drafts still await ruling:

- `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md` — promote to `lorebook/decisions/D-NNN_*.md` to canonicalize the S018 audit's structural decisions.
- `gielinor/players/jebrim/keepsake/proposals/2026-05-21_eu-tender-2026.md` (still untouched).
- `gielinor/players/jebrim/spellbook/drafts/skills/moving-target-decomposition.md` — awaits Jebrim skills-promotion at first Jebrim alching (covered by Step 1 if the gnome runs).
- `gielinor/players/jebrim/niksis8_character/drafts/` (S017-era + `2026-05-21-prefers-evidence-over-premature-infrastructure.md`) — also covered by Step 1 if the gnome runs.

**Step 3 — D-014 + S015 browser verification** (carried from S017). Subsumed by Step 1's combined test if the visualizer is open in live mode while the gnome runs.

**Step 4 — narration channel shakedown** (carried from S021/S022). Used heavily across opens; a deliberate stress test still warrants its own session.

**Step 5 — pick from [[Q-008]]** when ready to make the world feel alive. Recommendation in the entry: idle sprite breath + per-building ambient particles first, gated behind `prefers-reduced-motion`.

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

- **First live gnome spawn** — Step 1. Validates the whole S020 cascade plus the S022/S023 attribution-gating under sub-agent activity.
- **Drafts triage** — Step 2.
- **D-014 + S015 browser verification** — Step 3.
- **Narration shakedown** — Step 4.
- **[[Q-008]] pick** — Step 5.
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
2. `quest-log/S023_visualizer_ticker_and_cross_session_attribution.md` — the session that just closed.
3. `quest-log/S022_visualizer_audit_fixes.md` — the previous session; S023 builds on its cross-session attribution work.
4. `bank/research/visualizer-audit-S021.md` — the audit that drove S022. Historical record.
5. `bank/open-questions/Q-008_visualizer_aliveness.md` — parked.
6. `developer-braindead/.claude/hooks/emit-event.py` + `experiments/visualizer/index.html` — the patched targets.
7. `gielinor/.claude/hooks/gnome-write-boundary.py` + `dwarf-write-boundary.py` + `block-sub-spawn.py` — boundary hooks, still untested in the wild.
8. `gielinor/spellbook/skills/spawning-gnomes.md` — gnome operating spec.
9. `gielinor/.claude/agents/gnome.md` — agent config.
10. `gielinor/meta/modes.md` — principal/dwarf/gnome axis.
11. `gielinor/spellbook/rituals/close-session.md` + `alching.md` — step 0 spawn-decisions.
12. `bank/decisions/D-014_visualizer_chat_panel.md`, `D-015_jebrim_layer_audit_outcomes.md`, `D-016_gnomes_subagent.md` — prior decisions.
13. `bank/plan.md` — current mission state.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during fix iteration**. S023 followed this discipline — every fix layered on top of the dispatch surface, never reshaped it. Keep extending; don't rewrite.

D-014 added `narrate` and `action` events alongside `intent` / `move` / `spawn-dwarf` / `despawn-dwarf`. S020 added `spawn-gnome` / `despawn-gnome`. S022 added nothing new. S023 added `sessionId` as a stamped field on every event — additive metadata, no new event type.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.

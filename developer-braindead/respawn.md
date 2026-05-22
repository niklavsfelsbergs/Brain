# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-22 (end of [[S027]] — visualizer audit executed).

## Where we are

[[S027]] worked the S026 audit primer end-to-end and shipped 11 audit items in a single sitting against `developer-braindead/experiments/visualizer/index.html`. The visualizer's bug surface is materially reduced; the remaining work is **running-app verification**, not more code changes.

Shipped this session (all single-file deltas in `index.html`, modulo a one-line gitignore add):

- **B1** day/night follows the replay timeline (`currentHour()` branches on `LIVE`; `tick()`/`seekTo()` drive `updateDayNight()`; 87s TOTAL_MS maps to one virtual day — visibly cycles when scrubbing).
- **B3** `deriveSpeaker` reordered to prefer `braindeadActive`/`wispActive` over a stale `activePlayer` — the actual coherence gap. The HTML/CSS/dot chrome the audit thought was missing was already shipped by S022.
- **B4** `setIntent('')` for a sub-agent no-ops; task labels survive empty-text noise.
- **B5** `pollLive()` detects `state.ndjson` truncation, resets world, bootstraps from byte 0.
- **B6** Live poll fetch/parse errors surface as `console.warn` (first 5) + brand-subtitle `LIVE · poll error (N)` badge that self-clears.
- **B7** `instanceKey()` warns once per actor on `instance:0`, coerces to 1.
- **B8** Bubble width capped at 300px in `renderIntent()`.
- **I1** Last hardcoded per-actor hex (`.log-entry.commit`) swapped to `var(--commits-text)` + `color-mix(...)`.
- **I2** COMMS scroll-lock + jump-to-latest pip; threshold 12px; unread counter; resets in `resetWorld()`.
- **I3** `.speech-bubble` drop-shadow filter.
- **I4** Per-tab unread badges, cleared on tab click and `clearTabUnread('all')`.

**Verified-not-a-bug.** B2 `actorMoveTimers` was already keyed by `actorKey` (the instanceKey) at the only call site (line 2994). D-017's instance-routing work fixed it incidentally. Pattern worth a `bank/decisions/` note at next bankstanding: *recon dwarves should cross-check audit findings against intervening commits before bundling.*

**Skipped per audit "low payoff" framing.** I5 (idle-despawn configurable), I6 (color cycle wrap), I7 (label offsets dynamic), I8 (vignette follow), I9 (live freeze toggle), I10 (wisp glow precomputed). Iteration menu, not bugs.

**Out of scope.** B9 hook-side D-018 read race (flagged for follow-up).

**Live observation.** Mid-session, parallel Jebrim sessions on screen still showed the same stale bubble "CSV rework home — synthesis, awaiting smoke" from 12:52. Bare `jebrim.txt` clobber. Expected in-flight residual per [[S026]] — the pre-D-018-chunk-3 Jebrim sessions still write only to the bare file; `_reemit_intent_after_move` falls through to it on move. Resolves on those sessions' next turn (which re-reads `meta/communication-protocol.md` and adopts per-session intent files). No remediation from this side.

## Next concrete step — START HERE

**Step 1 — Running-app verification of S027 fixes.** Open `experiments/visualizer/index.html` in replay mode first. Confirm:

- B1 day/night cycles through the scrub. **Tune.** 87s/day is dramatic; if it reads too fast, knock it back to 2× or 4× of TOTAL_MS (constant in `currentHour()`).
- I2 scroll-lock — scroll up mid-replay, watch the "↓ N new" pip appear and accumulate; click jumps to bottom, lock clears.
- I4 tab badges — switch to JEBRIM filter, watch other tabs' badge counts tick up; click tabs to clear.
- I3 bubble drop-shadow visible against grass/path/buildings.
- B8 bubble clamp — find a long-intent test event or temporarily wrap to 80 chars and confirm cap.

Then live mode (`python -m http.server 8765`, `?live=1`). Confirm:

- B6 error badge by stopping the http server briefly, then restarting — `LIVE · poll error (N)` should appear, then clear.
- B5 ndjson reset by truncating `state.ndjson` while polling — visualizer should `resetWorld()` and rebuild from current state.
- B3 — in a dev-brain session like this one, Braindead-emitted log lines should land tagged `braindead`, not whatever player was last active.

**Step 2 — First live gnome spawn** (carried from S020+, still deferred). Validates the S020 boundary cascade, the visualizer's gnome render path, and S023/S024/D-018's session-scoped substates *under sub-agent activity*. No `state-gnomes.json` exists on disk yet (audit open question #6). Combined-test candidate: a Jebrim alching gnome.

**Step 3 — Drafts triage** (carried S018 → S019 → S020 → S021 → S022 → S026). Several still await ruling:

- `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md` — promote to `lorebook/decisions/D-NNN_*.md`.
- `gielinor/players/jebrim/keepsake/proposals/2026-05-21_eu-tender-2026.md`.
- `gielinor/players/jebrim/spellbook/drafts/skills/moving-target-decomposition.md` (Jebrim alching).
- `gielinor/players/jebrim/niksis8_character/drafts/` (S017-era + 2026-05-21-prefers-evidence-over-premature-infrastructure).

**Step 4 — Visualizer audit follow-up notes.**

- Add a `bank/decisions/` (or `lorebook/drafts/`) entry: *recon dwarves should cross-check audit findings against intervening commits before bundling.* S027 closed B2 and most of B3 by re-reading the file, both of which the audit primer reported as open. Three closed-but-reported items across S021 and S027 → pattern.
- B1's 87s/day cadence — decide whether to tune. Choices: keep (most dramatic), 2× TOTAL_MS, 4× TOTAL_MS, or anchor to a noon-centered slice.
- B9 hook-side D-018 read race needs a separate session at the hook level (`emit-event.py`). Atomic write or read-then-merge.

**Step 5 — Narration channel shakedown** (carried from S021/S022). Used heavily across opens; deliberate stress test still warrants its own session.

**Step 6 — pick from [[Q-008]]** when ready to make the world feel alive. Recommendation in the entry: NPC wanderers + trail echoes (the two not yet shipped by S024).

Other live threads (carried, lower priority):

- **Substantial un-committed Jebrim work** across `gielinor/players/jebrim/` — S023, S024 et al. Reconciliation belongs to next Jebrim respawn, not this dev-brain close.
- **Soft-block tuning** (S018 close-session pre-commit) — three options offered; re-evaluate "abandon" after first fire.
- **Self-observation sweep tuning** (S018 alching step 3a) — cap 0–3; watch first alching pass output.
- **Cross-player parity for future players.** Jebrim + Zezima aligned. No template system yet.
- **Possible `I-NNN` from S018** — quest-log-as-vacuum pattern.
- **Possible `lorebook/drafts/` from S020** — *architectural guarantees need a live failure test, not just code review.* S023, S027 → five-incident pattern. Pattern worth canonicalizing.
- **Possible `bank/decisions/` from S027** — *recon dwarves should cross-check findings against intervening commits.* (See Step 4.)
- **Possible `bank/decisions/` from S022/S023** — *audit-then-validate finds different bugs than either alone, and watching-it-run finds bugs the audit-and-validate phase missed.* S023's bugs all surfaced under live observation. Three-incident pattern, S027 reinforces (live screenshot caught the residual Jebrim clobber visibly).

Iteration menu (deferred, no priority assigned):

- **[[Q-008]] visualizer aliveness picks.** Idle breath, ambient particles, day/night, wanderers, trail echoes.
- **S027-skipped polish.** I5 (idle-despawn configurable), I6 (color cycle), I7 (label offsets), I8 (vignette), I9 (live freeze), I10 (wisp glow precomputed).
- **B9 hook D-018 read race** (separate session).
- **B1 day/night cadence tuning.**
- **Action target prettification** (audit I12).
- **Chat scroll-lock UX** — shipped as I2 in S027; gather usage feedback before further iteration.
- **Bubble two-line edge cases** (audit I14).
- **Idle indicator / watchdog for non-Claude writes / smarter active-player inference / SSE upgrade.** D-009 deferred.
- **Tighten gnome hook allowlist** from `/spellbook/drafts/` to `/spellbook/drafts/skills/` for symmetry with [[D-016]]. Phantom risk today.
- **Gnome workshop building** (audit I16). Defer until the gnome has been used a few times.

## Open at the start of next session

- **Running-app verification of S027 fixes** — Step 1. First action, before any new feature work.
- **First live gnome spawn** — Step 2. Validates S020 cascade + D-017/D-018 session-scoped substates under sub-agent activity.
- **Drafts triage** — Step 3.
- **Audit follow-up notes** — Step 4 (`bank/decisions/` on recon dwarf hygiene; B1 cadence tuning; B9 hook session).
- **Narration shakedown** — Step 5.
- **[[Q-008]] pick** — Step 6.
- §C Pilot definition, §H.3 brain-zone taxonomy, §H.4 identity ↔ main-brain interaction — unchanged.

## Carried-over observations

From [[S027]] (new): **recon dwarves should cross-check audit findings against intervening commits before bundling.** B2 was already fixed by D-017's instance-routing work; the audit primer reported it as open because the dwarf cited a static line without tracing the call site. B3's chrome was shipped by S022. Three closed-but-reported items across S021 and S027 — pattern worth a `bank/decisions/` note.

From [[S027]] (new): **a multi-fix audit pass converts the audit doc from a primer into a verification checklist.** The S026 prep doc was the briefing; the S027 quest-log + respawn is the receipt. Worth canonicalizing as a two-step workflow when an audit is large enough to span sessions.

From [[S023]] (still relevant): **shared global state at brain root is hostile to parallel Claude sessions — third incident.** Mitigation pattern has stabilized: gate every shared-state read on `_SESSION_ID`, stamp the writer's session_id into shared state when it sets a mode/marker, only honor overrides when current session matches. S014, S022, S023 all fit. S027's live screenshot confirms the residual stays visible until the affected sessions re-read the new protocol.

From [[S023]] (still relevant): **watching-it-run finds bugs the audit-and-validate phase missed.** Ticker freeze, inverse-direction Bash misattribution, wildcard-glob override hijack all surfaced under sustained observation. S027 reinforces — the screenshot itself was the verification surface that confirmed the in-flight Jebrim residual.

From [[S022]] (still relevant): **audit-then-validate finds different bugs than either alone.** Static read first, live test second. S023 added a third tier — sustained observation after validation. S027 demonstrates the full chain: prep doc (static), audit pass (changes), screenshot review (live confirmation).

From [[S022]] (still relevant): **shared global state is hostile to parallel Claude sessions.**

From [[S021]] (still relevant): **the audit-then-validate pattern works for accreted infrastructure.**

From [[S021]] (still relevant): **cross-file invariants need an explicit list when ≥3 surfaces enumerate the same set.**

From [[S020]] (still relevant): **architectural guarantees need a live failure test, not just code review.** S023, S027 → five-incident pattern.

From [[S020]] (still relevant): **the claude-code-guide agent earned its spawn.** Confirms [[D-014]]'s dwarf-spawn heuristic.

From [[S019]] (still relevant): **a new role's blocklist is easier to get right than its allow-list.**

From [[S019]] (still relevant): **single source of truth for tunable numbers is worth one hop.**

From [[S018]] (still relevant): **the quest log is the gravitational center; other layers starve without explicit routing.** Candidate for an `I-NNN` next bankstanding.

From [[S018]] (still relevant): **bundle big structural decisions; resist piecemeal landing.**

From [[S017]] (still relevant): **spec docs that prescribe DOM/structure without inventorying what already exists will ship suboptimal designs.**

From [[S017]] (still relevant): **heuristics that walk back through `state.ndjson` need to remember the stream is cross-session.**

From [[S017]] (still relevant): **emulating a specific UI's look means font and palette must change together.**

From [[S016]]: **"players communicate" in dev-brain mode probably means the visualizer, not the chat preamble.**

From [[S015]]: **shipping behind "the docs say X" is risky in this codebase because the docs are right but the integration is novel.**

From [[S015]] (separate): **delete discipline isn't enforced for dev-brain infrastructure.**

From [[S014]] (now nine-incident pattern with S018, S020, S022, S023, S027): **the procedure was right; the procedure assumed a state that didn't exist.**

From [[S014]]: **the renderer needs to be self-healing because the hook stream is a lossy substrate.**

From [[S014]]: **tool renames upstream are silent regressions.**

From [[S013]]: **uncommitted work occupies the ID space.**

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss.**

From [[S009]]: **mental UI preview must include z-order and all collision targets.**

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]]: **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.**

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S027_visualizer_audit.md` — what just shipped + verification checklist.
3. `bank/research/visualizer-audit-S026-prep.md` — the primer S027 worked. Now mostly historical, but the open-questions section (§Open questions 1–6) is still pending live verification.
4. `experiments/visualizer/index.html` — audit target.
5. `developer-braindead/.claude/hooks/emit-event.py` — event producer. Still hosts B9 (hook D-018 read race) as deferred work.
6. `bank/research/visualizer-audit-S021.md` — prior audit; closed by S022/S027.
7. `bank/open-questions/Q-008_visualizer_aliveness.md` — parked.
8. `gielinor/.claude/hooks/gnome-write-boundary.py` + `dwarf-write-boundary.py` + `block-sub-spawn.py` — boundary hooks, still untested under live sub-agent activity.
9. `gielinor/spellbook/skills/spawning-gnomes.md` — gnome operating spec.
10. `gielinor/.claude/agents/gnome.md` — agent config.
11. `gielinor/meta/modes.md` — principal/dwarf/gnome axis.
12. `gielinor/meta/communication-protocol.md` — mandates per-session intent filenames (D-018 chunk 3).
13. `gielinor/spellbook/rituals/close-session.md` + `alching.md` — step 0 spawn-decisions.
14. `bank/decisions/D-014_visualizer_chat_panel.md`, `D-016_gnomes_subagent.md`, `D-017_parallel_player_instances.md`, `D-018_parallel_session_substrate_isolation.md` — prior decisions.
15. `bank/plan.md` — current mission state.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during fix iteration**. S027 followed this discipline — every fix layered on top of the dispatch surface, never reshaped it. Keep extending; don't rewrite.

D-014 added `narrate` and `action` events alongside `intent` / `move` / `spawn-dwarf` / `despawn-dwarf`. S020 added `spawn-gnome` / `despawn-gnome`. S022 added nothing new. S023 added `sessionId` as a stamped field on every event. S027 added no new event types — purely renderer-side fixes.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.

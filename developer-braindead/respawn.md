# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S019]], post-commit; follow-up landed for naming/placement fixes).

## Where we are

[[S019]] shipped the gnomes sub-agent implementation end-to-end. Founding decision [[D-016]] + 4 phases (design, hook + agent, rulebook, rituals + skill spec). The principal/dwarf axis is now principal/dwarf/gnome, with the third role aimed at structural housekeeping (session-close, alching, drafts-triage). All 7 respawn-listed deliverables for gnomes are done; visualizer integration is the explicit one-deferred deliverable.

Concrete structural changes:

- New role **gnome** — system-namespace structural housekeeper, distinct from dwarves (functional/task-local). One agent config at `gielinor/.claude/agents/gnome.md`; spawn brief carries player scope as parameter.
- New hook `gielinor/.claude/hooks/gnome-write-boundary.py` — allow-list (drafts/proposals/inventory/quest-log across players + globals' drafts + `players/inbox/`) and explicit blocklist (`confirmed/`, `lorebook/decisions/`, `keepsake/current.md`, `meta/`, `spellbook/rituals/`, body files, `.claude/`-infrastructure). Blocklist wins on collisions. Gated on `CLAUDE_BRAIN_GNOME=1`.
- Renamed + generalized: `block-sub-dwarf-spawn.py` → `block-sub-spawn.py`. Fires on either `CLAUDE_BRAIN_DWARF=1` or `CLAUDE_BRAIN_GNOME=1`. Message names the role.
- New skill `gielinor/spellbook/skills/spawning-gnomes.md` — operating spec, **single source of truth for the heuristic numbers**. Both rituals (close-session, alching) reference this file at their step 0 spawn-decision rather than carrying their own copies.
- Rulebook: `meta/modes.md` axis retitled "principal vs sub-agent" with three subsections; `meta/write-rules.md` table got Session-close + Drafts-triage rows + hooks-enforced list updated; `gielinor/CLAUDE.md` 4 → 5 architectural guarantees.
- Both rituals patched with step 0 spawn-decision (`close-session.md`, `alching.md`).
- Alching write-reach in `write-rules.md` quietly corrected to include `spellbook/drafts/skills/` (was missed in D-015's table edit).

S015 dwarf attribution still untested in the wild. D-014 chat panel verification (S017 outstanding) still pending. Gnomes themselves are also untested in the wild — first live spawn will validate the hook + agent config.

**Post-close follow-up (same date).** Two naming/placement fixes landed as a follow-up commit: (a) `gielinor/spellbook/skills/gnomes.md` → `spawning-gnomes.md` to match `spawning-dwarves.md` convention, (b) `.claude/agents/gnome.md` (brain root) → `gielinor/.claude/agents/gnome.md` so the agent config sits with the rest of the gnome architecture (hook, skill, mode table). All internal references updated. **Discoverability caveat for next session:** verify a gielinor-scope session can still discover the agent at its new path — a brain-root session may or may not (which is semantically the right answer — dev-brain sessions shouldn't spawn gnomes).

## Next concrete step — START HERE

**Step 1 — approve gnomes work + implement them in the visualizer** (queued by principal at S019 close). Two sub-deliverables:

1. **Principal review and ratification of the S019 cascade.** Re-read [[D-016]], `gielinor/spellbook/skills/spawning-gnomes.md`, the two ritual step-0 additions, and the modes.md gnome-role section. Surface anything that needs adjustment before the gnomes go live in production. Specifically worth re-checking: the explicit blocklist in `gnome-write-boundary.py` (does it cover every principal-only surface?) and the spawn heuristic numbers (are they tuned right or do they need first-pass calibration?).

2. **Visualizer integration.** Spec + implement. Concrete deliverables for the visualizer pass:
   - **Sprite.** Gnome sprite distinct from dwarves. Smaller? Different hat? Per [[D-016]] *Things deferred* — defer the building question initially; reuse dwarf-spawn semantics (gnome spawns next to the active player like a dwarf) until a workshop building is warranted.
   - **Spawn/despawn events.** When the principal spawns a gnome via Task with `subagent_type: gnome` (or whatever the agent config registers as), the hook should emit a `spawn-gnome` event mirroring `spawn-dwarf`. Despawn on agent completion.
   - **Chat panel attribution.** Gnome's `description` field on the Task call becomes the gnome's bubble at spawn time (parallel to D-014's dwarf attribution). Action events emitted by the gnome get `actor:Gn` attribution.
   - **Optional: workshop building.** A dedicated gnome building (a workshop/garden/laboratory?) on the map. Defer until the gnome has been used a few times and the visual gap is felt.

   See `developer-braindead/experiments/visualizer/` for the renderer. `developer-braindead/.claude/hooks/emit-event.py` is where the spawn-gnome event would emit.

**Step 2 — first live gnome spawn.** Once visualizer hooks land, run the first gnome — likely as a session-close gnome for a heavy gielinor session, or as a Jebrim alching gnome (Jebrim's been overdue since S018; this would also exercise the D-015 alching procedure step 3a self-observation sweep end-to-end). The first spawn is the validation.

**Step 3 — drafts triage (carried from S018).** Several drafts still await ruling:

- `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md` — promote to `lorebook/decisions/D-NNN_*.md` to canonicalize the S018 audit's structural decisions.
- `gielinor/players/jebrim/keepsake/proposals/2026-05-21_eu-tender-2026.md` (still untouched). Note: `2026-05-21_shipping-data-mart-ttyd.md` was pinned during a prior session and the proposal file moved to `keepsake/archive/proposals/`.
- `gielinor/players/jebrim/spellbook/drafts/skills/moving-target-decomposition.md` — awaits Jebrim skills-promotion at first Jebrim alching.
- Pre-existing `gielinor/players/jebrim/niksis8_character/drafts/` (S017-era + 1 new today, `2026-05-21-prefers-evidence-over-premature-infrastructure.md`) — also await Jebrim alching.

**Step 4 — D-014 browser verification (outstanding from S017).** Spawn a real Jebrim Task while live mode is open. Watch for the full chat-event taxonomy. Subsumes S015 attribution verification. Worth combining with the first gnome spawn in Step 2 above — exercise both attributions at once.

**Step 5 — narration channel shakedown.** Still pending — try writing `.claude/narration.txt` at session boundaries / phase transitions and see if the chat line reads well. Was used this session at S019 open ("Dev-brain session opens — gnomes implementation begins"). Worth checking the read in the visualizer.

Other live threads (carried from S018):

- **Untracked Jebrim files at S019 close.** Several Jebrim files appeared in the working tree during this dev-brain session that I did not author this session — `inventory/S015-ttyd-resume.md`, `niksis8_character/drafts/2026-05-21-prefers-evidence-over-premature-infrastructure.md`, `spellbook/drafts/skills/investigate-before-specialize.md`, `quest-log/in-progress/S015_*.md`, modifications to `keepsake/current.md` and `quest-log/completed/S014_*.md`, and `keepsake/archive/proposals/`. These appear to be from a prior Jebrim session that didn't close cleanly. **Not committed in S019.** Next Jebrim session should pick them up via the reconciliation prompt at respawn.
- **Migration of S014's resume sections.** Per S018 D-015's deferred items. May already be done (see `inventory/S015-ttyd-resume.md` in the working tree). Confirm at next Jebrim respawn.
- **Soft-block tuning** (S018 close-session pre-commit soft-block) — three options offered; re-evaluate "abandon" after first fire.
- **Self-observation sweep tuning** (S018 alching step 3a) — cap 0–3; watch first alching pass output.
- **Cross-player parity for future players.** Jebrim + Zezima aligned. No template system yet.
- **Possible `I-NNN` from S018** — quest-log-as-vacuum pattern. Candidate for next bankstanding.
- **Thread A from S013 — verify visualizer feature set end-to-end.** Still outstanding.
- **Thread B — observe the harvest pump.** No code; watch what the next sessions' harvests produce.

Iteration menu (deferred, no priority assigned):

- **D-014 follow-ups from the decision doc.** Action target prettification. Chat scroll-lock UX. Actor color taxonomy tightening. Bubble two-line edge cases.
- **Idle indicator / watchdog for non-Claude writes / smarter active-player inference / SSE upgrade.** D-009 deferred.
- **Aesthetic backlog from [[S009]].** Per-building character.

## Open at the start of next session

- **Gnomes ratification + visualizer integration** — first priority. Step 1 above.
- **First live gnome spawn** — second priority. Validates the whole S019 cascade.
- **Drafts triage** — third priority. Multiple decisions pending.
- **D-014 browser verification + S015 attribution** — fourth priority. Combine with first gnome spawn.
- §C Pilot definition, §H.3 brain-zone taxonomy, §H.4 identity ↔ main-brain interaction — unchanged.

## Carried-over observations

From [[S019]] (new): **a new role's blocklist is easier to get right than its allow-list.** The gnome write-boundary hook uses both — allow-list for the housekeeping surface (broad), and explicit blocklist for principal-only paths that might otherwise match (`confirmed/` inside drafts-archive paths, `keepsake/current.md` inside the keepsake/ surface). Blocklist precedence is load-bearing; surface this if the hook ever fires unexpectedly.

From [[S019]] (new): **single source of truth for tunable numbers is worth one hop.** Spawn heuristic thresholds live in `gielinor/spellbook/skills/spawning-gnomes.md`; the rituals reference but don't copy. If the numbers prove wrong on first use, one file edits the threshold for all sites.

From [[S018]] (still relevant): **the quest log is the gravitational center; other layers starve without explicit routing.** Layer-routing.md + drafts-gates + inventory promotion fixed this for now. Candidate for an `I-NNN` next bankstanding.

From [[S018]] (still relevant): **bundle big structural decisions; resist piecemeal landing.** S019's gnomes work follows the same phased pattern (A→D with ratification gates between phases). Same coherence benefit.

From [[S017]] (still relevant): **spec docs that prescribe DOM/structure without inventorying what already exists will ship suboptimal designs.** Companion to S018's pattern.

From [[S017]] (still relevant): **heuristics that walk back through `state.ndjson` need to remember the stream is cross-session.**

From [[S017]] (still relevant): **emulating a specific UI's look means font and palette must change together.**

From [[S016]]: **"players communicate" in dev-brain mode probably means the visualizer, not the chat preamble.**

From [[S015]]: **shipping behind "the docs say X" is risky in this codebase because the docs are right but the integration is novel.**

From [[S015]] (separate): **delete discipline isn't enforced for dev-brain infrastructure.**

From [[S014]] (now five-incident pattern with S018): **the procedure was right; the procedure assumed a state that didn't exist.**

From [[S014]]: **the renderer needs to be self-healing because the hook stream is a lossy substrate.**

From [[S014]]: **tool renames upstream are silent regressions.**

From [[S013]]: **uncommitted work occupies the ID space.**

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss.**

From [[S009]]: **mental UI preview must include z-order and all collision targets.**

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]]: **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.**

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S019_gnomes_subagent_implementation.md` — most recent session, the gnomes build.
3. `bank/decisions/D-016_gnomes_subagent.md` — the founding decision; ratify before visualizer integration.
4. `gielinor/spellbook/skills/spawning-gnomes.md` — operating spec; single source of truth for heuristics.
5. `gielinor/.claude/hooks/gnome-write-boundary.py` — the enforcement.
6. `gielinor/.claude/agents/gnome.md` — agent config.
7. `gielinor/meta/modes.md` — updated principal/dwarf/gnome axis.
8. `gielinor/spellbook/rituals/close-session.md` + `alching.md` — step 0 spawn-decisions.
9. **For visualizer integration (Step 1.2):** `developer-braindead/.claude/hooks/emit-event.py` and `experiments/visualizer/index.html` — where spawn-gnome events would emit and render.
10. `bank/decisions/D-014_visualizer_chat_panel.md`, `D-015_jebrim_layer_audit_outcomes.md` — prior decisions the gnome work builds on.
11. `bank/plan.md` — current mission state.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during aesthetic iteration**. State additions across S009–S017 are layered on top of the dispatch surface, not changes to it. Keep extending, don't rewrite.

D-014 added `narrate` and `action` events alongside existing `intent`/`move`/`spawn-dwarf`/`despawn-dwarf`. The gnome integration adds `spawn-gnome`/`despawn-gnome` to that same dispatch surface — additive, no engine rewrite.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.

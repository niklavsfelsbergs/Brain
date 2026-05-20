# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-20 (end of [[S005]]).

## Where we are

Three sessions ago [[S003]] built the main brain Phase 1 scaffold at `Documents/GitHub/brain/gielinor/`. [[S004]] landed four corrections after Niklavs reviewed the audit. [[S005]] landed three more changes on top: a new per-player ritual (**alching**), a new universal **Understanding/Plan preamble protocol**, and the two missing **CLAUDE.md routers** at brain root and inside the dev brain.

What changed in [[S005]] vs [[S004]]:

1. **Alching ritual (new).** Per-player tending counterpart to bankstanding. `gielinor/spellbook/rituals/alching.md` documents scope (single active player only), six-step procedure, five recommendation thresholds at respawn, two invocation modes (explicit / threshold-recommended). Each player got a `last-alched.md` placeholder.
2. **Bankstanding sharpened (rewrite).** Now strictly **global-only writes**. Reads everything for cross-player synthesis, but per-player tending is alching's job. Procedure trimmed 8 → 7 steps; new step 6 reads each player's `last-alched.md` to flag overdue players.
3. **Four-mode framework (modes.md rewrite).** Session modes expanded three → four: player, unscoped, alching, bankstanding. The orthogonality with the principal-vs-dwarf axis is preserved.
4. **Write-rules ritual-reach table (new subsection).** `meta/write-rules.md` now documents bankstanding-vs-alching-vs-respawn reach alongside the per-layer write discipline.
5. **Understanding/Plan preamble protocol (new behavioral rule).** Every response opens with two short bold-labelled lines before the substantive reply. Compresses for trivial asks. Applies in every mode and role; voice adapts, structure does not. Full rule in `meta/communication-protocol.md` (new); prominent summary added near the top of master `CLAUDE.md` (before "What you are"); `@import` added to the meta block. Per-player `persona.md` files each got a brief `**Preamble.**` note acknowledging the protocol applies and how voice adapts. Not restated per persona.
6. **Brain-root routers (new files outside `gielinor/`).** `brain/CLAUDE.md` is the top-level router: two brain systems, route by working directory, no cross-read by default. `developer-braindead/CLAUDE.md` is the dev-brain entry: read `respawn.md` first, build-assistant scope, one-way cross-read allowance to `gielinor/` on explicit cue.
7. **Audit refreshed.** `build_audit.py` annotations updated for every S005-touched file; new annotations added for the new files. New `CONTENT_GROUPS` section "Brain-root routers (outside gielinor/)" renders the two external CLAUDE.md files in the linear contents view (they're intentionally not in the sidebar tree, which stays a clean mirror of `gielinor/`). Landing diagram redrawn. `gielinor-audit.html` regenerated: 105 files / 80 dirs / 46 drift flags.

Net main-brain state: +4 files inside `gielinor/` over end-of-[[S004]], plus 2 new files at the brain root and dev-brain root. The brain has still not been run on a real task.

## Next concrete step — START HERE

**Run the main brain.** Same as end of [[S004]] — open a Claude Code session in `Documents/GitHub/brain/gielinor/` and exercise the brain on a real task. Most natural first task is still a Jebrim work session against `Documents/bi-analytics-main/NFE/` or `Documents/bi-etl/`, or a Zezima reading-reflection session.

What to watch for during the first real use (updated from [[S004]] with S005 additions):

1. **Understanding/Plan preamble in practice.** Does the agent open every turn with the two-line preamble? Does it compress correctly on trivial asks? Does the voice adapt to player (Jebrim terse, Zezima reflective) without becoming a robotic recital? Does the preamble actually catch a misunderstanding at any point, or is it dead weight in practice?
2. **Address-based invocation in action.** First message likely opens with `Hey Jebrim, ...` or `Hey Zezima, ...`. Routes correctly on the first turn (no preemptive "which player?" prompt)? Sticky across un-addressed follow-ups? Mid-session switch (`Hey Zezima, ...` mid-Jebrim) works? Cross-player dwarf invocation (`Hey Jebrim, ask Zezima for ...`) works?
3. **Respawn ritual feel.** Does the load order still feel complete? Per-player sub-steps (a–g) in the right order? Where does it drag, what's missing?
4. **Hook enforcement.** Try to write to a `confirmed/` path (including `lorebook/confirmed/`). Try to delete a file under `gielinor/`. Both should block.
5. **First alching candidate.** After a few sessions on a player, the thresholds may breach and a recommendation should surface at respawn. When it does, run alching deliberately to validate the six-step procedure end-to-end. First real alching round may itself surface adjustments to the ritual.
6. **Bankstanding vs alching boundary.** When something surfaces during alching that feels system-level rather than per-player, does the agent correctly defer it to next bankstanding rather than promoting to globals from inside alching?
7. **Persona drift.** Does Jebrim's persona hold up? Same for Zezima if exercised. Observations to `gielinor/players/<name>/examine/drafts/`.
8. **Write-rule frictions.** "Wanted to write X but couldn't" each becomes an observation about the rules — candidate `lorebook/drafts/` entry.
9. **Per-turn quest-log discipline.** Does it actually happen? If not, the discipline rule needs a hook backing it.
10. **First lorebook entry candidate.** First real use may surface a self-improvement worth recording — first `lorebook/drafts/` entry, and the principal's review of it is the first real test of the new lorebook flow.

After the first real use, run a dev-brain session to capture observations and update `[[plan]]` §C–§G with what surfaced.

## Open at the start of next session

- **§C Pilot definition** — data source, "concerning" definition, output channel. Drives §B-class architecture refinements through real use.
- **§E Gates layer** — blocked on [[Q-002]] (async gates). Pick up when a real workflow surfaces the need.
- **§H.3 brain-zone taxonomy** — content for `player/working-agreements.md`. Not blocking but worth landing.
- **§H.4 identity ↔ main-brain interaction** — how `examine/I-NNN` entries here interact with main-brain `examine/` and per-player `examine/`. Decide when an identity observation from dev work needs to land in the main brain too.

## Carried-over observations

From [[S003]] / reaffirmed [[S004]]: **structure-first, content earns its way in.** Reaffirmed again in [[S005]] — three rounds of corrections against the same scaffold, each landing before content accumulated against the previous shape. Worth surfacing as a candidate `examine/` identity entry at next bankstanding.

From [[S004]] / reaffirmed [[S005]]: **build the verification surface alongside the artifact, not after.** The audit HTML kept earning its weight through both correction rounds — Niklavs sized each batch of changes to the audit's call-out surface. Also a candidate `examine/` entry.

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S005_alching_preamble_protocol_brain_routers.md` — most recent session
3. `quest-log/S004_main_brain_corrections_post_s003.md` — prior session (the four corrections)
4. `quest-log/S003_main_brain_phase_1_scaffold.md` — original build session
5. `bank/plan.md` — current mission state (§B done; §C and beyond open)
6. **Brain-root router:** `../CLAUDE.md` (new in [[S005]])
7. **Main brain entry:** `../gielinor/CLAUDE.md` (note the new "Communication protocol — read first" section near the top and the new `meta/communication-protocol.md` in the imports)
8. **New main-brain files in [[S005]]:**
   - `../gielinor/meta/communication-protocol.md` (the Understanding/Plan rule)
   - `../gielinor/spellbook/rituals/alching.md` (the new per-player ritual)
9. **Main-brain files significantly rewritten in [[S005]]:**
   - `../gielinor/spellbook/rituals/bankstanding.md` (global-only scope; 7-step procedure)
   - `../gielinor/meta/modes.md` (four-mode framework)
   - `../gielinor/meta/write-rules.md` (ritual write-reach table)
   - `../gielinor/players/_about.md` (alching pairing)
   - `../gielinor/players/jebrim/persona.md` and `../gielinor/players/zezima/persona.md` (preamble notes)
10. **Audit:** `../gielinor-audit.html` (double-click to open; reflects S005 state).

`bank/decisions/`, `bank/assumptions/`, `bank/open-questions/`, `bank/risks/` are reference material — open as cited.

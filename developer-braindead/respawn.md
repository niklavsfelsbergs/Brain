# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S006]]).

## Where we are

Main brain has been exercised on real work — Jebrim ran two player-side sessions today: S001 (repo orientation + close-session ritual adoption) and S002 (Shipping Data Mart V1 gap-analysis scoping). Both produced quest-log entries and bank notes; S002 is mid-execution with three dwarves planned but not yet spawned.

[[S006]] (this dev-brain session) was triggered by a failure mode surfaced *during* the brain-root → dev-brain transition: I attempted to bulk-read Jebrim's in-progress S002 quest file to "write a hand-off note" when no player had been active in the current session at all. Two pushes from Niklavs got the conceptual error named: the brain-root and master `CLAUDE.md` both said "previously active player's `quest-log/in-progress/` (if any) gets a hand-off note" — which I read as "any in-progress file on disk" rather than "outgoing player in *this session*."

What [[S006]] landed:

1. **Hand-off note precondition (3 files).** `gielinor/spellbook/rituals/respawn.md` mini-respawn step 1 now leads with an explicit **Precondition** — skipped when no outgoing player exists this session — and the step itself defines the note's shape (one-line marker, "do not re-read or summarize the quest's existing content"). `gielinor/CLAUDE.md` and `brain/CLAUDE.md` both got matching clarifications.
2. **Spawning-dwarves skill (new).** `gielinor/spellbook/skills/spawning-dwarves.md` codifies the dwarf workflow end-to-end: trigger heuristic (≥2 independent paths + amplifier), pre-flight check, briefing template, **background-by-default** channel, status-on-ping, completion-weave, dwarf quest-log streaming discipline, anti-patterns. Heuristic seeded from Jebrim's own S002 self-observation.
3. **Dwarf-spawn annotation.** `gielinor/meta/communication-protocol.md` got a subsection mandating that the Plan line lists dwarves inline (manifest) when the heuristic fires — piggybacks on the already-in-force Understanding/Plan preamble.

Net main-brain delta: +1 file, 4 files edited in place. No new dev-brain entries beyond this session's `respawn.md` overwrite and `S006_*.md` quest-log entry.

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

**Resume Jebrim S002 and exercise the new spawning-dwarves skill.** Jebrim's S002 quest is mid-execution with three dwarves planned (D1 ClickUp subtree, D2 bi-etl scan, D3 Redshift coverage). That spawn wave will be the **first real test** of the [[S006]] skill — specifically the background-by-default channel, the Plan-line manifest annotation, and the status-on-ping behavior. Watch for friction during real use; that's the design feedback we're after.

Secondary follow-ups, in priority order:

1. **Draft the deferred dev-brain records.** A `D-NNN` decision capturing the hand-off wording fix (context → decision → alternatives → consequences). An `I-NNN` examine draft on the failure mode itself — *conflating disk-state with session-state, and the bulk-read-to-write-a-marker reflex.* Both were proposed at the end of [[S006]] but user cued close before they landed.
2. **Watch for the third occurrence pattern.** [[S004]] / [[S005]] / [[S006]] all surfaced via pushback after the agent committed to a wrong-shaped action. If a fourth occurrence lands, that's the threshold for promoting "principal pushback is the primary ambiguity signal" to a confirmed `examine/` entry in the main brain.

What to watch for during the dwarf spawn (specific to [[S006]] additions):

1. **Dwarf-spawn heuristic firing correctly.** When the principal hits the three-dwarf wave for S002, does the Plan-line manifest annotation actually appear? Does the principal go background-by-default, or fall back to foreground blocking spawn?
2. **Status-on-ping behavior.** When the user asks "status?" mid-wave, does the principal tail siblings since last check (cheap) or re-read the whole file (expensive)? Friction here gets flagged for the hook-vs-discipline call.
3. **Completion-weave timing.** Does each dwarf's completion get surfaced in the next response, or batched silently until all return? The skill says next response; verify.
4. **Synthesis gate.** Principal must wait for *all* dwarves before synthesizing unless user cues otherwise. Watch for premature synthesis on partial returns.
5. **Hand-off note shape — verified by absence.** Next mid-session player switch (or player→unscoped switch) should produce a one-line marker, not a bulk-read prelude. If the agent still bulk-reads, the fix didn't land at the behavior level — only at the rule level.
6. **Carry-over from prior watch-list:** Understanding/Plan preamble in practice (compress correctly? voice adapts?); address-based invocation (sticky? mid-session switch?); hook enforcement (`confirmed/` writes, file deletes — both should block); per-turn quest-log discipline.

After the dwarf wave completes, run a dev-brain session to capture observations and write the deferred `D-NNN` + `I-NNN` drafts.

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
2. `quest-log/S006_handoff_precondition_and_dwarf_spawning.md` — most recent session
3. `quest-log/S005_alching_preamble_protocol_brain_routers.md` — prior session (alching, preamble, routers)
4. `quest-log/S004_main_brain_corrections_post_s003.md` — the four corrections
5. `quest-log/S003_main_brain_phase_1_scaffold.md` — original build session
6. `bank/plan.md` — current mission state (§B done; §C and beyond open)
7. **Brain-root router:** `../CLAUDE.md` (note the [[S006]] hand-off no-op clause)
8. **Main brain entry:** `../gielinor/CLAUDE.md` (note the [[S006]] outgoing-player clarification on the mid-session switching paragraph)
9. **New main-brain file in [[S006]]:**
   - `../gielinor/spellbook/skills/spawning-dwarves.md` (the new skill)
10. **Main-brain files edited in [[S006]]:**
    - `../gielinor/spellbook/rituals/respawn.md` (mini-respawn Precondition + hand-off note shape spec)
    - `../gielinor/meta/communication-protocol.md` (dwarf-spawn annotation subsection)
11. **Audit:** `../gielinor-audit.html` (still reflects S005 state — regenerate next dev-brain session if file count or structure shifts justify a refresh; [[S006]]'s +1 file delta may not warrant it).

`bank/decisions/`, `bank/assumptions/`, `bank/open-questions/`, `bank/risks/` are reference material — open as cited.

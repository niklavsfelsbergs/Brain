# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-20 (end of [[S004]]).

## Where we are

Two sessions ago [[S003]] built the main brain Phase 1 scaffold at `Documents/GitHub/brain/gielinor/`. The session that just ended ([[S004]]) built the audit tool Niklavs asked for and landed four corrections he surfaced after reviewing it. The main brain is now ready for first real use.

What changed in [[S004]] vs [[S003]]:

1. **Lorebook redefined** — was `{drafts, decisions/, assumptions.md, patch-notes.md}`, now is the identity-pattern `{drafts, confirmed, archive, rejected}`. It is the agent's **self-improvement log** — what changed in how *it* operates, decided by *it* about *itself*. Construction history (main-brain [[D-001]], [[D-002]], the original patch-notes and assumptions placeholder) moved to `developer-braindead/bank/main-brain-construction/`.
2. **Three session modes** — `meta/modes.md` now leads with player / unscoped / bankstanding as a session-mode axis, orthogonal to the principal/dwarf role axis. Bankstanding is explicitly its own mode with cross-cutting reach.
3. **Bankstanding rewritten** — adds explicit mode-framing at the top, a new step 3 (cross-player synthesis: promote recurring per-player patterns to the global layer), drops the assumptions/patch-notes steps, replaces them with "log behavioral changes to `lorebook/drafts/`."
4. **Player invocation gap closed** — `players/_about.md` rewritten to match the address-based model (it was the last file still describing a preemptive prompt). Cross-player dwarf trigger phrases enumerated in both master `CLAUDE.md` and `players/_about.md`.
5. **Tightenings** — "Rejected drafts are data" section added to the six identity-layer `_about.md` files. Reconciliation prompt in `respawn.md` refined to three explicit options including "reconcile the pending action externally first," with an explicit "do not auto-resume" rule.
6. **Audit tool** — `gielinor-audit.html` at brain root. Single self-contained HTML, structural audit + linear verbatim contents section. `build_audit.py` is the re-runnable generator; all annotations updated for S004 changes.

Net main-brain state: 51 substantive files (down 5 from end-of-[[S003]] since 4 moved out; placeholder `.gitkeep`s aren't substantive). The brain has not yet been run on a real task.

## Next concrete step — START HERE

**Run the main brain.** Open a Claude Code session in `Documents/GitHub/brain/gielinor/` and exercise it on a real task. The most natural first task is a Jebrim work session — likely against `Documents/bi-analytics-main/NFE/` or `Documents/bi-etl/`, since that's where bank-grounded content can start accumulating. A Zezima reading-reflection session is the other natural option.

What to watch for during the first real use:

1. **Address-based invocation in action.** The first message likely opens with `Hey Jebrim, ...` or `Hey Zezima, ...`. Does the agent route correctly on the first turn (no preemptive "which player?" prompt)? Does sticky behavior hold across subsequent un-addressed turns? Try a mid-session switch (`Hey Zezima, ...` mid-Jebrim) and a cross-player dwarf invocation (`Hey Jebrim, ask Zezima for ...` or `Hey Zezima, have Jebrim look up ...`).
2. **Does the respawn ritual feel right?** Now that step 6 (read assumptions) is gone, does the load order still feel complete? Are the per-player sub-steps (a-g) in the right order? Where does it drag, what's missing?
3. **Do the hooks fire as expected?** Test them deliberately — try to write to a `confirmed/` path (including the new `lorebook/confirmed/`), try to delete a file under `gielinor/`. They should block.
4. **Does Jebrim's persona hold up, or does it drift?** Observation goes in `gielinor/players/jebrim/examine/drafts/`. Same for Zezima if she's exercised.
5. **When does the agent want to write something it can't?** Each "wanted to write X but couldn't" is an observation about the write rules — a candidate `lorebook/drafts/` entry.
6. **Per-turn quest-log discipline** — does it actually happen? If not, the discipline rule needs a hook backing it.
7. **First lorebook entry candidate.** The first real use may itself surface a self-improvement worth recording — that becomes the first `lorebook/drafts/` entry, and the principal's review of it is the first real test of the new lorebook flow.

After the first real use, run a dev-brain session to capture observations and update `[[plan]]` §C-§G with what surfaced.

## Open at the start of next session

- **§C Pilot definition** — data source, "concerning" definition, output channel. Drives §B-class architecture refinements through real use.
- **§E Gates layer** — blocked on [[Q-002]] (async gates). Pick up when a real workflow surfaces the need.
- **§H.3 brain-zone taxonomy** — content for `player/working-agreements.md`. Not blocking but worth landing.
- **§H.4 identity ↔ main-brain interaction** — how `examine/I-NNN` entries here interact with main-brain `examine/` and per-player `examine/`. Decide when an identity observation from dev work needs to land in the main brain too.

## Carried-over observation

From [[S003]]: **structure-first, content earns its way in.** Reaffirmed in [[S004]] when Niklavs surfaced corrections within hours rather than letting content accumulate against a drifted base. Worth surfacing in `examine/` as a candidate identity entry at next bankstanding. Currently structural memory only.

From [[S004]]: **build the verification surface alongside the artifact, not after.** The audit HTML earned its weight immediately — drift flags led the eye to the spots that needed adjustment. Also a candidate `examine/` entry.

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S004_main_brain_corrections_post_s003.md` — most recent session, has the corrections list
3. `quest-log/S003_main_brain_phase_1_scaffold.md` — previous session (the build)
4. `bank/plan.md` — current mission state (§B done; §C and beyond open)
5. **Main brain entry:** `../gielinor/CLAUDE.md` (note the new layer-index lorebook description and the expanded cross-player dwarf triggers)
6. **Main brain redefined layers:**
   - `../gielinor/lorebook/_about.md` (the new self-improvement-log framing)
   - `../gielinor/meta/modes.md` (the new three-session-modes section)
   - `../gielinor/spellbook/rituals/bankstanding.md` (the mode-aware rewrite)
   - `../gielinor/spellbook/rituals/respawn.md` (step 6 removed; reconciliation refined)
   - `../gielinor/players/_about.md` (invocation section rewritten)
7. **Construction history (relocated):** `bank/main-brain-construction/_about.md` plus the four files there.
8. **Audit:** `../gielinor-audit.html` (double-click to open; reflects S004 state).

`bank/decisions/`, `bank/assumptions/`, `bank/open-questions/`, `bank/risks/` are reference material — open as cited.

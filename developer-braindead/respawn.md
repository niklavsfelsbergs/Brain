# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-20 (end of [[S003]]).

## Where we are

Phase 1 complete on the main-brain side. [[S001]] bootstrapped the dev brain. [[S002]] restructured it around RuneScape layers ([[D-006]]). [[S003]] built the main brain Phase 1 scaffold at `Documents/GitHub/brain/gielinor/` ([[D-007]] referencing main-brain [[D-001]]), then added the address-based player invocation rule (main-brain [[D-002]], same session).

The main brain exists. Its founding decision is recorded; its rulebook is in `gielinor/meta/`; its rituals are defined; its four hooks are wired; Zezima and Jebrim are scaffolded as players with minimal `_about.md`, `persona.md`, and `CLAUDE.md`. Player invocation is by address at message start (`Hey Zezima, ...` etc., sticky, strict matching) — no preemptive prompt. Most folders are empty by design — content lands through real use.

The dev brain's job has shifted from **designing** the main brain to **observing and refining** it.

## Next concrete step — START HERE

**Build an audit HTML for `gielinor/`.** Niklavs built a large system in ~3 hours and explicitly asked, end-of-[[S003]]: *"I need to understand what I've built so I can correct it before it's too late."* He needs to verify what was actually written against what he intended, before running the main brain on real work and accumulating content on top of a possibly-drifted base.

Specified shape (all three points confirmed by Niklavs at end of [[S003]]):

- **Scope:** just `gielinor/`. Not the dev-brain updates.
- **Format:** one self-contained `.html` file. Double-click to open. No JS dependencies, no external assets.
- **Contents:** full file contents inlined (not summaries).

Required structure:

- **Left nav.** Collapsible tree mirroring `gielinor/`. Click a file → it loads in the right pane.
- **Landing view (right pane, default).** Architecture diagram showing the layer model (body / hooks / rulebook / global layers / rituals / players). Summary counts (directories, files). A "start auditing here" list — hooks first, since they bind hardest; then the rulebook in `meta/`; then the rituals; then the founding decisions [[D-001]] and [[D-002]]; then per-player content.
- **File view (right pane, per file).**
  - One-sentence **purpose** (what role this file plays).
  - **Drift flags** callout — a visible badge on any file where the builder (me, in [[S003]]) made a non-obvious judgment call Niklavs should double-check. Examples to flag: every `_about.md` (judgment in framing the metaphor and rules), `D-001` and `D-002` (full content authored, not just structured), all `persona.md` and player `_about.md` files (character framing is interpretive), the four hook scripts (security boundary; verify the regexes and the env-var assumption are right), `CLAUDE.md` (master + per-player; tone choices), the rituals (load order is canonical, must be exactly right).
  - **Full file contents**, syntax-highlighted by extension (markdown rendered or raw-toggleable; Python highlighted; JSON highlighted).
  - **Cross-links** to related decisions and other files (clicking a `[[D-001]]` style link or a `gielinor/meta/...` path opens that file in the same pane).

**Styling:** functional and dense. Monospace headings, tight spacing, dark mode. Audit tool, not a pitch deck. He's scanning for "did the builder write what I asked," not reading for pleasure.

**Self-imposed constraints for the build:**

- Embed file contents as JSON inline in the HTML — don't reference external files. The audit must work standalone.
- No external CSS/JS — inline everything. Single file, double-click open.
- Don't paraphrase file contents in the "purpose" line — that defeats the audit. Purpose describes the role of the file in the architecture; the contents view shows what's actually in it.
- Be honest in drift flags. Where the builder extended Niklavs's sketches, say so. Where the builder authored content from scratch (e.g., the design rationale paragraphs in `_about.md` files), say so. Niklavs's whole reason for asking is to catch this.

When the audit HTML lands, save it as `gielinor-audit.html` at the brain root (`Documents/GitHub/brain/gielinor-audit.html`) so it sits next to both brains without being inside either.

## After the audit

Once Niklavs has reviewed the audit and made any corrections to `gielinor/`, the next concrete step is **run the main brain.** Open a Claude Code session in `Documents/GitHub/brain/gielinor/` and exercise it on a real task — likely a Jebrim work session against `Documents/bi-analytics-main/NFE/` or `Documents/bi-etl/`, since that's where bank-grounded content can start accumulating.

What to watch for during the first real use:

1. **Address-based invocation in action.** First message likely opens with `Hey Jebrim, ...`. Does the agent route correctly on the first turn (no preemptive "which player?" prompt)? Does sticky behavior hold across subsequent un-addressed turns? Try a mid-session switch (`Hey Zezima, ...`) and a cross-player dwarf (`Hey Jebrim, ask Zezima for ...`).
2. Does the rest of the respawn ritual feel right? Where does it drag, what's missing?
3. Do the hooks fire as expected? Test them deliberately — try to write to a `confirmed/` path, try to delete a file under `gielinor/`. They should block.
4. Does Jebrim's persona hold up, or does it drift? Observation goes in `gielinor/players/jebrim/examine/drafts/`.
5. When does the agent want to write something it can't? Each "wanted to write X but couldn't" is an observation about the write rules.
6. Per-turn quest-log discipline — does it actually happen? If not, the discipline rule needs a hook backing it.

After first real use, run a dev-brain session to capture observations and update [[plan]] §C-§G with what surfaced.

## Open at the start of next session

- **§C Pilot definition** — data source, "concerning" definition, output channel. Now decoupled from §B (which is done). Drives §B-class architecture refinements through real use.
- **§E Gates layer** — blocked on [[Q-002]] (async gates). Pick up when a real workflow surfaces the need.
- **§H.3 brain-zone taxonomy** — content for `player/working-agreements.md`. Not blocking but worth landing.
- **§H.4 identity ↔ main-brain interaction** — how `examine/I-NNN` entries here interact with main-brain `examine/` and per-player `examine/`. Decide when an identity observation from dev work needs to land in the main brain too.

## Carried-over observation from [[S003]]

Niklavs has been consistent across [[S001]]→[[S002]]→[[S003]] about **structure-first, content earns its way in.** Worth surfacing in `examine/` as a candidate identity entry at next bankstanding. Currently structural memory only — risks fading if not captured.

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S003_main_brain_phase_1_scaffold.md` — most recent session
3. `bank/plan.md` — current mission state
4. `bank/decisions/D-007_main_brain_phase_1_scaffold_landed.md` — meta-decisions that shaped the build
5. **Main brain entry:** `../gielinor/CLAUDE.md` and `../gielinor/lorebook/patch-notes.md` (Day 0 + the player-invocation entry)
6. **Main brain decisions:** `../gielinor/lorebook/decisions/D-001_phase-1-scaffold.md` and `../gielinor/lorebook/decisions/D-002_player_invocation_by_address.md`

`bank/decisions/`, `bank/assumptions/`, `bank/open-questions/`, `bank/risks/` are reference material — open as cited.

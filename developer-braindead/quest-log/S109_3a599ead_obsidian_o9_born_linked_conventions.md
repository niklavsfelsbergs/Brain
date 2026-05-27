# S109 — 2026-05-27 — Obsidian §O.9: born-linked authoring conventions

Dev-brain via "lets develop gielinor", entered mid-conversation. Principal's question: *now that we're Obsidian-enabled, what must change so all **new** entries accommodate it?* — i.e. the going-forward conventions, not another corpus migration.

## What happened

- **Diagnosis (read-only, empirical).** The §O.2–§O.6 passes migrated the *existing* corpus to full-stem `[[links]]` + wrapped prose anchors (~2,550 wraps, S105). But **nothing had touched the docs that teach how a new entry is written** — so every new note would re-rot the graph: plain-text anchors → isolated nodes (the very 76%-isolated finding §O.6 fixed); bare `[[ID]]` → phantom links. §O would be a recurring backfill.
- **Root finding (grep-confirmed, not assumed):**
  - **gielinor had no stated link rule anywhere** — `grep` for "full-stem"/"Obsidian" across `gielinor/**/*.md` = 0 hits. Gielinor can't read the dev-brain [[D-004_stable_ids]] (brain-root router), so a player session authoring a bank note had zero instruction to link.
  - The dev-brain front-door docs still taught the *old* form: `_about.md:26` + `CLAUDE.md:52` said *"Wiki-links `[[ID]]`"*, contradicting the D-004 amendment they predate.
  - The anchor templates (`## Anchor`, `**Source:**`, `**Observation (SNNN)**`) are emergent (not specified in meta), and several brand-new entries (Zezima's 2026-05-26 `niksis8_character/confirmed`) carried plain-text anchors with no source link.

## The fix — 8 doc-prose edits (no renames, no hooks; authoring discipline)

- `gielinor/meta/write-rules.md` — **new "Link & anchor conventions" section** (the centerpiece; gielinor's first stated rule): full-stem `[[stem|ID]]`, all prefixes, **source anchor must be a link**. @imported → loads every gielinor session.
- `gielinor/meta/drafts-mechanics.md` — linked-anchor note appended to the observation rule.
- `developer-braindead/_about.md` + `CLAUDE.md` — `[[ID]]` → full-stem per [[D-004_stable_ids]] (the contradiction fix).
- `developer-braindead/spellbook/entry-formats.md` — full-stem rule generalized to all prefixes; stale *"A/Q/R/I/S still bare pending pass"* note corrected; clarified the template `[[SNNN]]` are placeholders for the full-stem link.
- [[D-004_stable_ids]] — amendment extended with a **"Going-forward authoring"** subsection (covers all prefixes + anchor-as-link + the gielinor mirror).
- `bank/research/obsidian-fit-and-migration-spec.md` — *Forward convention* section extended.
- `bank/plan.md` — new **§O.9** item + §O status-line update.

Cross-brain refs left as plain text per §O.5 (per-brain vaults); example links in the gielinor meta written as code-spans so they don't dangle / aren't re-migrated.

## Coordination ([[D-024_parallel_player_coordination]])

- Entered while S105 (7c91117c, §O.6) looked live-but-stale (~23min idle, no CLOSING, ~2,550 uncommitted wraps in tree). Stayed read-only; surfaced it + offered the principal a sequencing choice. Principal: *"that session is finished, check in with others."* Re-checked: **S105 had committed** (`5174201`+`143c3a0`), tree clean.
- One live sibling at implement time: **f4aadfed** (S107, comms-rotation/read-discipline) — "discussion only, no file targets," steering clear of in-place edits. Its surface (comms `_about.md` + rotation) didn't touch mine. It had flagged 3a599ead as an ABANDONED candidate (I'd gone quiet awaiting the principal) — refreshed intent + pinged it.
- **Two collisions hit live & resolved:** (1) plan.md raced (f4aadfed committed comms-rotation + a plan touch mid-edit) → re-read, re-applied. (2) **§O.8 was already taken** by 7c91117c for a *different* thing (deferred topical cross-linking) → renumbered mine to **§O.9** + fixed the §O.8 text refs in D-004 + spec. (3) S107/S108 taken (f4aadfed/98592157) → claimed **S109**.

## Open / next

- **Not yet committed** — awaiting principal go (boundary: always ask before committing). Commit by pathspec: the 8 surfaces + this quest-log only; exclude f4aadfed's comms-rotation WIP, cockpit/switchboard runtime, the zezima S095 quest WIP, build-lessons.
- §O.9 is inward (keeps §O durable / serves §N). *(See the addendum below: later in this same session the principal recalibrated §C's urgency — a known much-later phase, not the load-bearing next step.)*

**Cascade.** gielinor/meta/{write-rules,drafts-mechanics}.md; developer-braindead/{_about,CLAUDE}.md; developer-braindead/spellbook/entry-formats.md; bank/decisions/D-004_stable_ids.md; bank/research/obsidian-fit-and-migration-spec.md; bank/plan.md; this quest-log.
**Main-brain changes.** gielinor/meta/write-rules.md + drafts-mechanics.md (the going-forward authoring rule gielinor sessions read every respawn).

## Addendum — §C urgency recalibrated (same session)

Principal steer mid-conversation: *"lets stop taking point C so seriously, we will get to it. For now I'm working in collaboration with you. Scheduled tasks will come much later."* Saved as a feedback memory; then reframed the dev docs so the steer sticks across respawns (otherwise the next respawn re-loads "§C is the load-bearing next step"):
- `respawn.md` "Where we are" — "load-bearing gap / strategic next step" → "the inward/outward *observation* stands; the *urgency* is recalibrated — known future phase, hands-on collaboration now." (The "Next concrete step" demotion was already landed by the parallel [[S110_144c0ca2_brain_full_audit|S110]] audit's steering note — we converged on the same steer.)
- `bank/plan.md §C` — status softened from "the load-bearing gap / the next build" to "a known future phase, deprioritized 2026-05-27."
- [[D-027_inward_outward_build_imbalance]] — dated *Amendment (urgency recalibrated)*; analysis preserved, and the "watch on inward over-build" consequence kept (this is about *timing of the outward build*, not licence for more inward work).

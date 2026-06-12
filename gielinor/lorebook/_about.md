# lorebook/ — the agent's self-improvement log

**Cognitive role.** The log of changes the agent decides to make to **how it operates** — the rules it follows, the rituals it runs, the discipline it holds itself to. Decided by the agent, about itself, during bankstanding or reflection.

**Metaphor.** A wizard's spellbook of *rule-changes* — not the rules themselves (those live in `meta/`), but the record of when and why each rule changed.

## Scope — what this layer is for

The lorebook is the agent's record of **its own evolution.** When the agent notices that the way it currently operates is wrong, outdated, or could be tightened — and the principal approves the change — that decision lands here.

Each entry is a single self-improvement: what was changed, why it was changed, when, and what triggered the change (a specific observation, a failure, a piece of user feedback, a pattern noticed in rejected drafts).

**Append-only.** Past entries are not rewritten. When a later entry supersedes an earlier one, the new entry references the old; the old entry remains in `confirmed/` as historical record. When an entry no longer reflects current operation at all, it moves to `archive/`.

## Scope — what this layer is NOT for

- **Construction history** — decisions made while *building* the brain (founding shape, scaffolding choices, initial roster, hook design). That lives in the dev brain (`developer-braindead/bank/`), not here. The dev brain is the place that records *how the agent came to exist*; the lorebook is the place that records *how the agent changes itself once it exists*.
- **Working assumptions** — those belong in master `CLAUDE.md` (load-bearing always-in-context assumptions) or in `examine/` (self-observed patterns).
- **Per-session narrative** — that's `quest-log/`. A session might *produce* a lorebook draft, but the session log itself is not a lorebook entry.
- **Factual change records** ("what files moved during bankstanding") — subsumed by entries read chronologically. Bankstanding produces a lorebook draft only when it changed *how the agent operates*, not for routine triage.

## Structure

```
lorebook/
  _about.md            # this file
  _index.md            # synthesized cue index — per-decision distilled rule + prompt patterns
  drafts/              # proposed self-improvements awaiting principal review
  confirmed/           # approved self-improvements; each entry is its own file
  archive/             # confirmed entries that no longer reflect current operation
  rejected/            # drafts the principal turned down (kept; patterns matter)
```

**The cue index (`_index.md`, [[S192_384c1c27_db-schenker-reroute-package-dims|S192]]).** Confirmed decisions never loaded at respawn — a player mid-task could miss an applicable one (knowledge-miss regression case 10). `_index.md` is the synthesized map the `[LOR]` arm of `domain-cue-reminder.py` parses every prompt: a decision with `patterns:` + `rule:` gets its distilled rule force-inlined when a prompt matches (once per session per decision); the rest carry a `carried-by:` label naming where their behavior already lives (always-on meta file, ritual read, hook). **Every promotion to `confirmed/` adds an index entry in the same pass** (drafts-triage / bankstanding carry the step); `developer-braindead/verification/hygiene-check.py` flags unindexed decisions and ghost entries.

Same drafts/confirmed/archive/rejected pattern as the other identity-shaped layers (`examine/`, `niksis8/`, per-player `examine/`, per-player `niksis8_character/`).

## Entry shape

Each entry is a markdown file in `confirmed/`. Filename: `YYYY-MM-DD-<slug>.md`. Date is when the change was approved, not when the trigger happened.

Each entry should answer:

- **What changed** — which rule, ritual, or discipline now operates differently.
- **Why** — the reasoning. Why this change instead of leaving things alone.
- **What triggered it** — the specific observation, failure, feedback, or pattern that surfaced the need.
- **What was affected** — which `meta/` files, rituals, or layer `_about.md` files changed in lockstep.
- **Supersedes / superseded by** — links to other lorebook entries if any.

## Write rules

Identity-pattern. Drafts auto-write; promotions to `confirmed/` and edits there are user-only and hook-enforced. See `meta/write-rules.md` and `meta/drafts-mechanics.md`.

## Rejected drafts are data

`rejected/` is kept on purpose. A pattern in what gets rejected — the same kind of self-improvement proposed and turned down repeatedly — is itself a signal that the agent's model of "what's worth changing" is miscalibrated. Bankstanding reviews these patterns and may surface them as working-agreement updates.

## Related

- `meta/` — the *current* rulebook. Lorebook entries describe how `meta/` came to be the way it is.
- `spellbook/rituals/bankstanding.md` — the ritual that surfaces opportunities for lorebook drafts.
- `examine/` — the agent's self-model. Observations in `examine/` may eventually produce a lorebook entry (if the observation implies a behavioral change).
- `developer-braindead/bank/main-brain-construction/` — where the original founding decisions (D-001, D-002, the day-0 patch notes) now live.

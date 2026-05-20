# `bank/` — about

Semantic memory for the dev brain. What is known about how to build the agent: settled decisions, assumptions, open questions, risks, the plan, external research, and Niklavs's unfinished design sketches.

Metaphor: items sorted, kept, withdrawn on demand.

## Contents

| Slot | Holds |
|---|---|
| `plan.md` | Single living plan. One mission, iterated. |
| `why.md` | Project reason-for-being and the pilot framing. |
| `decisions/` | One file per [[D-NNN]] — durable design decisions with rationale. |
| `assumptions/` | One file per [[A-NNN]] — things proceeded on without proof. Each has a `Replace when:` trigger. |
| `open-questions/` | One file per [[Q-NNN]] — unresolved design questions. |
| `risks/` | One file per [[R-NNN]] — known fragilities and concerns. |
| `research/` | External sources read while building. One file per source. |
| `drafts/` | Niklavs's half-formed sketches before promotion. |
| `archive/` | Superseded entries. Mirrors active structure when populated. Empty until needed. |

## Conventions

- **Stable IDs never reused.** See [[D-004]]. Filename pattern: `D-001_descriptive_name.md`. Wiki-link uses just the ID: `[[D-001]]`.
- **Nothing destroyed.** Superseded entries move to `archive/`, with the active entry's tail line updated to `**Status.** superseded by [[X-NNN]].`
- **Entry formats** documented in `spellbook/entry-formats.md`.

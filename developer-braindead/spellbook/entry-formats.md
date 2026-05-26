# entry-formats — how to write each kind of entry

**Invoked.** Reference. Open when writing or reviewing an entry.

## Stable IDs

| Prefix | Lives in | Examples |
|---|---|---|
| `D-NNN` | `bank/decisions/` | [[D-001_two_brain_split]], [[D-006_dev_brain_restructure]] |
| `A-NNN` | `bank/assumptions/` | [[A-001]] |
| `Q-NNN` | `bank/open-questions/` | [[Q-001]] |
| `R-NNN` | `bank/risks/` | [[R-001]] |
| `I-NNN` | `examine/` (identity) | [[I-001]] |
| `SNNN` | `quest-log/` | [[S001_dev_brain_architecture]], [[S002_dev_brain_runescape_restructure]] |

Numbers never reused. References use the **full filename stem** (`[[D-001_two_brain_split]]`) with the ID prefix as the stable anchor — per the [[D-004_stable_ids]] amendment (2026-05-26). *Decisions migrated 2026-05-26; A/Q/R/I/S links still use the bare ID pending their own pass.*

## Decision — `bank/decisions/D-NNN_descriptive_name.md`

```markdown
# D-NNN — YYYY-MM-DD — Short title

**Context.** Why this needed deciding.
**Decision.** What was decided.
**Alternatives considered.** Options and why each was rejected.
**Consequences.** What this implies downstream.
**Session ref.** [[SNNN]].
```

Optional tail: `**Supersedes.** [[D-NNN]] (reason).` Mark the older decision's tail with `**Status.** superseded by [[D-NNN]].`

## Assumption — `bank/assumptions/A-NNN_descriptive_name.md`

```markdown
# A-NNN — Short title

**Status.** `working` | `locked`. Opened in [[SNNN]].

Body — what we're proceeding on without proof.

**Replace when.** Explicit trigger that would convert this assumption into a decision or invalidate it.
```

## Open question — `bank/open-questions/Q-NNN_descriptive_name.md`

```markdown
# Q-NNN — Short title

**Status.** `open` | `working` | `blocked` | `answered`. Opened in [[SNNN]].

Body — the question, what's at stake, what's been floated.
```

When answered, edit status to `answered by [[D-NNN]]` (or `[[A-NNN]]`).

## Risk — `bank/risks/R-NNN_descriptive_name.md`

```markdown
# R-NNN — Short title

**Severity.** `low` | `medium` | `high`. Opened in [[SNNN]].

Body — the fragility.

**Mitigation.** What we're doing (or deferring) about it.
```

## Identity entry — `examine/I-NNN_descriptive_name.md`

```markdown
# I-NNN — Short title (the posture rule, lead with it)

**Date.** YYYY-MM-DD. **Session ref.** [[SNNN]].

**Ruling.** One line. The rule itself.

**Context.** What happened that surfaced this. Quote or paraphrase the moment.

**Why.** The reason this is now a rule. What it prevents or unlocks.
```

## Quest-log entry — `quest-log/SNNN_descriptive_name.md`

```markdown
# SNNN — YYYY-MM-DD — Quest name

- 3–5 bullets describing what happened. Wiki-link every artifact ([[D-NNN]], [[I-NNN]], etc.).

**Cascade.** What dev-brain files landed this session.
**Main-brain changes.** What crossed into `vault/`. Use `none` if nothing crossed.
```

## General conventions

- **Newest at top** within any single-file collection (the plan, identity if you keep it in one file). Per-entry collections (decisions/, assumptions/, etc.) don't need ordering — the filename sorts.
- **Wiki-links are load-bearing**, not decorative. Use them whenever you reference another entry.
- **Be terse.** A short clear entry that exists is worth ten thorough drafts that don't.

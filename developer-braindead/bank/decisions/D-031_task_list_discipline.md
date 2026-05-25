# D-031 — 2026-05-25 — Task-list discipline for gielinor

> **Status: decided and built (doc-only).** Principal observed gielinor charges long tasks head-first and wanted it to decompose into tracked task lists more often. Chose the **threshold-gated, two-home** shape. This session landed the rule (`gielinor/meta/task-lists.md` + wiring); no hooks, no code.

## Context — the gap

gielinor had no machinery for **sequential decomposition** of a long task within a session. What existed only half-covered it:

| Existing | Covers | Doesn't cover |
|---|---|---|
| Understanding/Plan preamble | catches misunderstanding of *what* the task is | one sentence of intent — not a step breakdown, no progress state |
| `inventory/` resume-state | "where we are / next step" across sessions | written at session *boundaries* (close writes, respawn reads), not a live in-flight checklist |
| Dwarf-spawn heuristic | *parallel* fan-out decomposition | sequential, single-actor ordered work |
| Harness `TaskCreate`/`TaskUpdate` | live in-session tracking | never referenced by any gielinor ritual |

So for a long ordered task in one session, the agent stated a one-line plan and dove. The principal's read was accurate.

## Decision — threshold-gated, two homes

Adopt a task-list discipline, gated by a complexity threshold and using two complementary storage homes. Picked over the two alternatives:

- **Lightweight (harness todos only)** — rejected as the *whole* answer: no durability, loses the crash-recovery and cockpit-surfacing wins. Kept as the live layer.
- **Heavy (durable inventory checklist for every long task)** — rejected as default: highest risk of fighting the brain's terseness/anti-recitation culture; ceremony on tasks that don't need it.

**The threshold** (the load-bearing part — it's what stops list-*theater*): make a list when **multi-step AND** (multi-file OR spans turns OR irreversible/outward action OR order-dependent). Skip for single-action, trivial, or pure-discussion asks. Tiebreaker: *would a dropped or out-of-order step be expensive?* This deliberately mirrors the dwarf-spawn and alching thresholds — same calibration instinct, so it sits in muscle memory the agent already has.

**Two homes:**

- **Harness list** — every list-worthy task. Live, visible, ephemeral.
- **`inventory/` durable mirror** — added only when work outlives the turn or carries risk. Lives in the existing resume file; it *is* the recovery signal `death-and-spawn.md` already asks for at action grain, now at task grain. No new structure — `inventory/_about.md` and `layer-routing.md` already route "open task list" there; the rule just says *when* it's obligatory.

**Surfacing:** the list appears in/after the Plan line so the principal can correct the *decomposition* before commitment — the Plan-preamble rationale at finer grain. The agent doesn't recite the full list every turn; the harness list + intent line carry it.

## Why this is inward build, and why it's still justified

Per [[D-027]], the brain has over-built *inward* (observability, cockpit) and under-built outward *hands*; the §C pilot remains the strategic next step. This is more inward work. It's justified anyway: it removes a recurring quality tax on *every* long task in *every* mode (dropped steps, un-correctable plans, crash-fragility), it's doc-only (no maintenance surface), and it directly sharpens the agent's execution discipline — which the outward §C pilot will itself lean on when it runs multi-step briefs. Small, broad, cheap.

## What landed

- `gielinor/meta/task-lists.md` — the canonical rule (threshold, two homes, lifecycle, anti-patterns, scope).
- `gielinor/CLAUDE.md` — `@meta/task-lists.md` added to the imported rulebook + a layer-index/rulebook mention.
- `gielinor/meta/communication-protocol.md` — a *Task-list surfacing* subsection (sibling to the dwarf-spawn annotation): how the list appears relative to the Plan line.
- `gielinor/meta/layer-routing.md` — a row pointing decomposed-task checklists at the `inventory/` resume file.

## Out of scope / open

- **No hook enforcement.** This is discipline like the rest of `meta/`. If the agent reliably skips list-making on tasks that warranted one (the inverse of the OPEN-skip leak), revisit — a `Stop`-hook nudge could surface "this looked multi-step; no list was made," but not built now.
- **Cockpit surfacing of the inventory checklist** — the durable mirror could render as a progress strip on the board. Not built; noted as a natural future tie-in.
- **Live calibration.** The threshold is a first cut; watch real sessions for both failure directions (theater vs. head-first) and tune.

## Related

- [[D-024]] — parallel coordination; the `__<sid8>` resume-file shape the durable mirror writes into.
- [[D-025]] — multiple-choice-with-recommendation; the mechanism used to pick this shape with the principal.
- [[D-027]] — inward/outward imbalance; the context that frames this as justified inward work.
- `gielinor/meta/task-lists.md` — the rule itself.
- `gielinor/spellbook/skills/spawning-dwarves.md` — the parallel-decomposition sibling whose threshold this mirrors.

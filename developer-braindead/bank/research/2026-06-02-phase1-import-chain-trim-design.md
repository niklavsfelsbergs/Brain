# Phase 1 design — trim the always-on @import chain (the keystone)

**Session.** [[S145_543c6caf_knowledge_loading_and_rule_adherence_audit|S145]] (dev-brain, 2026-06-02). The structural fix in the anti-deterioration plan (`plan.md` §X.5). **Design-only** — `meta/*.md` and `CLAUDE.md` are user-only, so this lands as a **Guthix godly proposal at bankstanding**, not a Braindead edit. This doc is the proposal's blueprint.

## Problem (measured, not asserted)

`brain-weight.py` @ HEAD: the @import chain is **23,295 tok / 10 files**, expanded inline **every session, unconditionally**, and it **tripled (8k→23k) in 13 days, monotonically** (archive-discipline never removes). Per the [[S145_543c6caf_knowledge_loading_and_rule_adherence_audit|S145]] research, a heavier always-on load degrades adherence to *every* rule (constraint-count collapse ~81%→37%, lost-in-the-middle, context rot). So the chain's growth curve *is* the "acting dumber" curve. Cutting it is the highest-leverage structural move.

## The central principle (the guard against making it worse)

**A rule may move out of the always-on core ONLY if something deterministic re-triggers it** — a ritual step that reads it, or a hook that injects it at the moment it applies. If we just turn the rulebook into a pointer-index and trust the agent to `Read` it "when relevant," we recreate the exact knowledge-doesn't-load failure this whole effort exists to kill — one level up, on the rules themselves.

So the trim and the retrieval are **coupled**: *you can only safely trim what you can reliably re-trigger.* This is the line that separates this design from naive "just make CLAUDE.md shorter."

Three sanctioned re-trigger mechanisms (in order of reliability):
- **R1 — ritual-embedded read.** The rituals are markdown the agent already follows step-by-step; a rule read inside the relevant ritual is loaded deterministically when that ritual runs. (Strongest — the ritual is the forcing function.)
- **R2 — hook injection.** A PreToolUse/UserPromptSubmit hook injects the rule (or a tight pointer) at the moment of the governed action (spawning a sub-agent, writing a gated layer). The domain-cue registry is the proven pattern.
- **R3 — index pointer.** The thin core carries a one-screen index ("spawning? → modes.md"). Agent loads on demand. **Weakest — reintroduces the decide-to-load failure**, so use ONLY for genuinely rare reference detail, never for a load-bearing rule.

## The cut — per-file classification

Token counts from `brain-weight.py`. "Re-trigger" = what loads it after it leaves the core.

| File | Now (tok) | Disposition | Re-trigger |
|---|---|---|---|
| `CLAUDE.md` (root) | 1,033 | **CORE** (thinned ~700) | — always-on router |
| `gielinor/CLAUDE.md` | 2,650 | **CORE** (thinned ~1,400) | — address-routing every first msg |
| `meta/communication-protocol.md` | 5,590 | **SPLIT** | preamble/voice/5-lens/multiple-choice/wrong-instance/Guthix-routing → CORE (~1,800); intent-narration mechanics + `.mode` markers + narration channel → **JIT** (~3,800) via R1 (rituals/visualizer setup read it) |
| `meta/modes.md` | 4,867 | **JIT** | R1+R2 — spawn skills read the write-boundary tables; the boundaries are *hook-enforced* already, so the prose is reference. CORE keeps a 3-line "four sub-agent roles exist; hooks enforce their surfaces." |
| `meta/write-rules.md` | 2,876 | **JIT** | R1+R2 — alching/drafts-triage read it; `confirmed/`-writes already hook-blocked. CORE keeps the draft→approve one-liner. |
| `meta/layer-routing.md` | 2,299 | **CORE** (~2,000) | — this *is* the map; it's how the agent knows where to read/write. The index R3 points *from*. |
| `meta/task-lists.md` | 1,415 | **SPLIT** | threshold ("when to make a list") → CORE (~300); full mechanics → JIT via R2 (a multi-step-ask nudge) / R3 |
| `meta/drafts-mechanics.md` | 1,152 | **JIT** | R1 — drafts-triage + alching read it |
| `meta/death-and-spawn.md` | 748 | **JIT** | R1 — respawn ritual reads it (it's literally about respawn/reset) |
| `meta/archive-discipline.md` | 665 | **JIT** | hook-enforced (`block-deletes`); CORE keeps "never delete, only archive →" pointer |

**Projected CORE ≈ 6,600 tok** (root 700 + gielinor 1,400 + comms-core 1,800 + layer-routing 2,000 + rule-index 400 + summaries 300) **vs 23,295 now — a ~72% cut.** The remaining ~15k loads only when its ritual/hook fires. (Re-run `brain-weight.py` post-migration against the real number; this is the design target, not a promise.)

## The thin CORE — what stays always-on

The irreducible every-turn set:
1. **Two-brain router** (root CLAUDE.md) — which brain, the dev-brain entry cue.
2. **Player invocation by address** (gielinor CLAUDE.md) — load-bearing on every first message; strict matching rules.
3. **The six architectural guarantees** as a *pointer* — they're hook-enforced, so the core states they exist + "don't try to bypass," not the full prose.
4. **Communication core** — Understanding/Plan preamble + compression rule + five-lens (brief) + copyable-deliverables + multiple-choice-with-recommendation + wrong-instance check + Guthix-routing. These fire every response.
5. **The layer map** (`layer-routing.md`) — the read/write router.
6. **The rule index** — the R3 pointer list to the JIT'd detail.

## Risks & mitigations

- **R-1: a load-bearing rule moves to JIT but its trigger doesn't fire → rule silently lost.** This is the failure mode we're fighting, applied to rules. *Mitigation:* the central principle (only move what R1/R2 re-triggers; R3 only for rare reference). Plus **stage it** (below) and re-score the regression set + watch `ritual-stats` adherence between stages — a regression means a trigger didn't fire.
- **R-2: high blast radius on identity prose.** *Mitigation:* it's a prose *restructure*, not a logic change; fully git-reversible; lands via godly proposal (principal reviews every meta edit).
- **R-3: the JIT'd ritual reads add their own load when the ritual runs.** Accepted — that load is *conditional* (only during that ritual), which is the whole point; it doesn't tax every session.

## Staged rollout (safest first, measure between)

1. **Stage A — the already-backed files.** Move `death-and-spawn` (respawn reads it), `archive-discipline` (hook-enforced), `drafts-mechanics` (drafts/alching read it) out of @import; add the rituals' explicit reads + core pointers. ~2.6k cut, lowest risk (triggers already exist). Measure.
2. **Stage B — modes + write-rules.** Move to JIT behind the spawn skills / alching; they're hook-enforced so prose-loss is low-stakes. ~7.7k cut. Re-score regression set. Measure.
3. **Stage C — the comms-protocol split.** The biggest single win (~3.8k) but the most delicate (it's behavioral). Split CORE vs operational-detail carefully; the operational half rides with the visualizer/ritual reads. Measure adherence hard here.
4. **Stage D — task-lists split + the rule index + final core thinning.** Cleanup.

Each stage: re-run `brain-weight.py` (weight ↓), re-score `knowledge-miss-regression-set.md` (no regression), check `ritual-stats` adherence didn't drop. A stage that regresses adherence gets reverted — the weight cut isn't worth a dumber brain.

## The godly-proposal framing

Braindead can't touch `meta/`/`CLAUDE.md`. The path: at the next **bankstanding**, Guthix drafts the proposal in `deities/guthix/proposals/` (per [[D-032_godly_proposal_flow_and_code_bearing_seam|D-032]]), staged A→D, each stage a reviewable diff. The ritual reads that *enable* the JIT (e.g. respawn explicitly reading `death-and-spawn.md`) are themselves user-only ritual edits — same proposal. This design doc is the blueprint Guthix works from.

## Verification target

- Weight: CORE ≤ ~7k tok (`brain-weight.py`), down from 23.3k.
- Coverage: regression set holds or improves (no `caught`→`miss`).
- Adherence: `ritual-stats` block/nudge pattern stable or better across the migration.

The success criterion is not "smaller" — it's **smaller *without* getting dumber**, proved by the regression set and adherence numbers, not asserted.

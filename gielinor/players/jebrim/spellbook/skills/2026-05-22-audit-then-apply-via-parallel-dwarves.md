# Audit-then-apply via parallel dwarves

**Date:** 2026-05-22
**Player:** Jebrim
**Anchor:** [[S033_2026-05-22_shipping-agent-audit|S033]] shipping-agent audit — `S033_2026-05-22_shipping-agent-audit.md` + the four dwarf logs `S033_d1_shims-and-import.md`, `S033_d2_harness-and-scatter.md`, `S033_d3_restamp.md`, `S033_d4_doc-sweep.md`.

## The pattern

A reusable shape for audit-then-fix work on a single package or repo where the audit yields N independent finding clusters.

1. **Pass 1 — principal walks the package read-only.** No edits. Output is a flat finding list captured in the quest-log as the read progresses. Read-only mandate is load-bearing: pass-1 fixes bias the reading.
2. **Pass 2 — principal clusters and leverage-ranks the findings.** Group by area (e.g., entry-shims, harness/scatter, restamp, doc-sweep). Each cluster gets a one-line proposal with location + fix shape. Surface in chat for triage (recommend / maybe / probably not).
3. **Principal locks decisions.** The user picks which findings to apply, which to defer, which to drop. Lock these explicitly in the quest log before spawning anything — drift after spawn is expensive.
4. **Dwarves spawn in parallel — one cluster per dwarf, with a file-ownership map.** Each dwarf gets explicit `owns:` paths so writes don't overlap. The map is what makes parallel safe.
5. **Principal synthesizes the dwarf returns, runs final verification, and commits.**

## The load-bearing detail — file-ownership map

The parallel-safety guarantee is "exactly one writer per file." Spawn briefing names it explicitly. Anchor (verbatim from [[S033_2026-05-22_shipping-agent-audit|S033]] spawn turn):

> *"D1 owns shims, D2 owns harness scripts + scatter files, D3 owns coverage-audit + sources.md maturity table, D4 owns the rest"*

When two clusters both want to touch the same file (e.g., D2 and D4 both wanting `how_to.md` edits), collapse the touch-points into one dwarf even if the work is logically two clusters. Cheaper to expand one dwarf's brief than to coordinate a merge.

## When to use this

- **Yes:** audit produced ≥ 3 independent clusters, each non-trivial enough to warrant a dwarf, file-ownership is partitionable.
- **No:** single-file fix (just do it). Or audit clusters that all touch the same hot file (serialize).
- **No:** the audit itself is still mid-pass-1. The pattern starts after pass 2 finishes.

## Why this beats serial principal-edits

- Parallelism: 4 dwarves return in roughly the time of one. [[S033_2026-05-22_shipping-agent-audit|S033]]'s 4-dwarf wave finished in one turn-pair.
- Verification isolation: each dwarf's report is scoped to its lane, easier to spot a missed fix than re-reading a long serial diff.
- Failure containment: if D2 returns with a surprise, D1/D3/D4 still landed clean.

## Anti-patterns

- Spawning before decisions are locked. Dwarves can't choose between competing fix options.
- Overlapping ownership. If two dwarves write to the same file, expect merge conflicts and lost edits.
- Skipping pass 1. Without the read-only sweep, the cluster boundaries are guesses.

## Why this is the second-time pattern

[[S032_2026-05-22_bi-etl-shipping-mart-harvest|S032]] used the recon-spawn variant (parallel reads → principal synthesis, no apply). [[S033_2026-05-22_shipping-agent-audit|S033]] is the apply-fix variant. Different terminal step (commits land vs report), same parallelization mechanic. Worth promoting from skill-draft to skill once a third invocation lands.

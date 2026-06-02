# A static code-audit's ranking is a hypothesis until measured

**Observation ([[S147_dcb495a7_scm-perf-audit|S147]], 2026-06-02).** The 5-dwarf static perf audit of the SCM dashboard ranked the DuckDB connection serialization (D1) as the headline and the `shifts` 4× inline scan (D2-F1) as high-leverage. Live measurement reordered all of it:

- **D1** — real, but the dashboard is 1–2 users, so the serialization rarely bites for latency (it survives only as the `bd_cache` race fix + a growth bet).
- **D2-F1** — the 4× inline genuinely re-scans, but only **1.6×** (41ms vs 25ms), not the "biggest multiplier" the static read guessed.
- **The actual dominant cost** — scan **breadth**: full 29-month glob = 268ms vs 10ms for one month (26.8×), with row-group statistics absent so no within-file pruning. Nothing subtle; the static audit under-weighted it.
- **A "quick win" that wasn't** — routing the deviations trend onto an existing pre-agg tier (P2) *failed* an old-vs-new live compare: the pre-agg's population doesn't match the per-shipment query's `both-costs-present` filter, so the swap would have silently changed displayed numbers.

**Why it matters.** This is the "missing half" pattern again ([[S146_f20d7744_scm-serving-memory-review|S146]]: the chat-side `bd_cache` diagnosis was wrong; kubectl corrected it). Reading code tells you *where the hot paths are*; it does **not** reliably tell you *which one costs the most* or *whether a substitute is equivalent*. Two concrete rules for perf/optimization work:

1. **Rank by measured cost, not inferred mechanism.** A clever-looking inefficiency (4× re-scan) can be a 1.6× footnote while a boring one (scan breadth) is the 27× headline. Measure before committing build effort.
2. **A pre-agg tier only retires a per-shipment scan if its population matches the query's filter.** Verify old-vs-new outputs row-by-row before re-routing — a population mismatch is a correctness regression, not a perf win. (Reinforces [[reconcile-definition-before-numbers]] and the verify-diffs-both-ways discipline.)

The live-validation cost was small (in-pod DuckDB probes, capped memory) and changed the entire build plan — front-load it on any optimization audit where the fix is expensive to unwind.

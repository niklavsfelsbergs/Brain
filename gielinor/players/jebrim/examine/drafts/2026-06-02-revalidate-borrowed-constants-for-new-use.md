# Re-validate a borrowed constant for its NEW purpose

**Observation ([[S147_dcb495a7_scm-perf-audit|S147]] sess-3, 2026-06-02).** Building the transit roll-up tier, I lifted `TRANSIT_BIN_TAIL=14` straight from the existing `transit/histogram` route, where 14 is a *display* cap (`LEAST(FLOOR(x),14)` — the UI shows a "14+" bin). I reused it as the bin cap for *percentile reconstruction* and even wrote in the code "matches the histogram EXACTLY so the route is a clean swap." It built, synthetic-verified within ±0.3 day, and read as done.

The live old-vs-new validation refuted it: on real data, exact p99 reaches 42 days and p95 reaches 30 — so a 14-cap floored p95 on 12/59 corridors and p99 on 29/59 (errors up to 16d/28d). The constant was *correct for its original purpose* (a histogram display tail) and *wrong for the new one* (a fidelity parameter for percentiles up to p99). A cap sweep on the real months → 45, size flat (sparse-zero tail bins) → all percentiles ±0.6 day.

**The pattern.** A constant borrowed from context A silently becomes an *assumption* when reused in context B. Its fitness for A says nothing about its fitness for B. The fix is cheap and the lesson is the same shape as the standing one: a specced/inherited value is a hypothesis until measured *against the new use's requirement* — here, "the cap must exceed the highest percentile the UI shows," which the histogram's display cap was never chosen to satisfy.

**How to apply.** When reusing a magic number / threshold / default across a purpose boundary, name what the new purpose actually requires of it and validate against *that*, not against "it works where it came from." Cross-links the static-audit-ranking-is-a-hypothesis-until-measured draft (sess-1) and the global [[verify-the-thing-dont-trust-the-wiring]] confirmed entry — this is the borrowed-constant instance of that family.

*Anchor: [[S147_dcb495a7_scm-perf-audit|S147]] sess-3 (sid 6595ae02) — TAIL=14→45 after the live cap sweep. Caught only because the validation step explicitly stress-tested the tail on real fat-tailed distributions.*

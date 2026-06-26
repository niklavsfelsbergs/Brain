# A borrowed coherence constant produced a confidently-wrong preliminary verdict — verify-the-thing caught it

**Moment ([[S368_364d42cd_orwo-per-lane-band-grain-sizing|S368]], sid8 364d42cd, 2026-06-25).** Sizing whether finer ORWO routing grain pays, I ported the EU-tender smoothing — including its `floor = max(25, 5% of lane)` constant — into the diagnostic. The smoothed result came back −€999 (≈ nothing), and I drafted the verdict "finer grain banks nothing for ORWO." It was **wrong**: the €34.6k DE prize (DHL <10kg → Maersk ≥10kg) was real, and the borrowed 5%-of-lane floor had silently eaten it — on DE (548k parcels) 5% = 27,401, a bar no DE weight band clears, so a genuine monotone hand-off got absorbed as "noise." A second artifact (a 31kg DHL=Maersk tie breaking to incumbent → fake A→B→A → full-lane collapse) compounded it.

**What recovered the truth.** Niklavs pressed ("are we sure?"), and I re-derived the DE number **directly** — a two-segment calc bypassing the borrowed smoothing machinery entirely — which surfaced the prize the machinery hid. Then the union-of-breakpoints scan proved completeness.

**Why this matters / how to apply.**
- This is the **re-validate-borrowed-constants** + **thinning-threshold-regresses-on-the-sparse/extreme-case** family, instantiated sharply: a constant tuned for one distribution (EU tender's smaller, multi-carrier lanes) **silently regresses on a different one** (a lane that's 90% of the book makes a %-floor an impossible absolute bar). A borrowed threshold is a hypothesis, not a setting — validate it against the NEW distribution before trusting its output.
- The self-check that *passed* (rung-1 reproduced €2,311,013 exactly) gave false confidence in the *whole* pipeline; the defect was downstream of the checked step. A green self-check on one stage is not a green pipeline.
- The recovery lever was **re-derive directly, bypassing the suspect machinery** — not debug the machinery in place. When a borrowed apparatus returns "nothing here," confirm with a hand calc before believing it.

Generalizable form already in cross-conversation memory ([[feedback_revalidate_borrowed_constants]], [[feedback_thinning_threshold_regresses_sparse_case]]) — not duplicating; this is the ORWO instance for the examine record.

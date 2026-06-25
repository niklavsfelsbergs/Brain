# S368 — ORWO finer-grain (destination × weight-band) routing sizing

**Session:** sid8 `364d42cd`, 2026-06-25. Player: Jebrim. Continues the ORWO tender arc ([[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]] umbrella / [[S285_2bf7cf70_orwo-tender-logic-walkthrough-and-us-disregard|S285]] logic walkthrough / S286 annualization / [[S367_ae7565da_orwo-methodology-walkthrough|S367]] methodology doc).
**Mode:** discussion + READ-ONLY sizing. One NFE scratch script written (uncommitted by principal decision).

## What was asked
Niklavs: "we are routing per lane. what's a lane? A whole country?" → escalated to: single-carrier-per-country routing hides weight crossovers (Maersk wins GB ≤3kg, GLS 3kg+) — should ORWO route at the EU-tender grain (destination × package × weight band)? Discuss, then size whether finer grain pays.

## Turn log

**What a lane is.** ORWO ships from one origin (Wolfen), so a lane collapses to the destination, and the current routing grain is **country** (`per_lane_optimum.py` groups by `country_iso2`, deliberately rejecting per-parcel as "unbookable").

**The concern, grounded.** `per_lane_optimum.py` picks one carrier per country = `min(incumbent, GLS, Maersk)` on whole-lane full cost. The author framed it as binary (whole-lane bookable vs per-parcel unbookable) and skipped the bookable middle: **country × weight band**. EU-tender precedent corrected: the EU routing report is `dest × packagetype` (one carrier per cell), with weight-crossover upside captured only as the decision-report *ceiling*; the ~€102.5k routing↔decision gap = the operational haircut. ORWO is dim-poor (no packagetype) → the natural finer axis is weight band.

**How the EU tender combats flip-flops** (read `ops_coherence/triage_routing_rules.py` + `cost_check_smoothing.py`): raw per-1kg-cell argmin → coherence definition (monotone step function, one upward switch normal, A→B→A return = defect) → smoothing (a switch needs `floor = max(25, 5% of lane)`, span ≥2kg; sub-floor bands absorbed into the larger neighbour) → priced the coherence at ~€39k/yr (4–5%).

**Built the sizing diagnostic** `per_lane_band_optimum.py` (3-rung ladder: whole-country / raw per-band ceiling / smoothed bookable). Self-check PASSED — rung-1 reproduced the known H1 optimum €2,311,013 exactly. But the smoothed rung-3 came back −€999 (≈ nothing).

**Pressed on it (verify-the-thing) — the −€999 was WRONG.** DE's band table shows a real, clean monotone hand-off: DHL wins 0–9kg, **Maersk wins every band 10kg+** (10kg: €22,433 vs €12,708). The smoothing had absorbed it because (1) the borrowed `5% × 548k = 27,401` floor is a bar no DE band clears, and (2) a 31kg DHL=Maersk tie broke to incumbent, faking a return that triggered full-lane collapse. Direct two-segment calc, bypassing the smoothing: **DE ≥10kg → Maersk = €34,619 H1** (11,360 parcels), best threshold confirmed at 10kg.

**Niklavs pressed again — "are we sure we catch it all? did you check the contracts?"** Answered honestly: NO contracts checked — the 10kg threshold was empirical from cost; the integer `floor(kg)` grid is lossy (collapses Maersk's sub-kg breaks). Proposed + ran the **exhaustive method: band on the UNION of carrier rate-card breakpoints** (crossovers can only occur at a breakpoint, so the grid catches all). Union-grid scan (incl Maersk 0.25kg resolution) = **€36,206 H1 ≈ coarse 1kg €36,197**; raw ceiling €36,568 barely above bookable → **nothing hidden, we caught it all.** DE = €34,619 (96%, clean single threshold), FR €1,503 footnote, GB no crossover, 21/25 lanes single-carrier-optimal.

## Decisions
- **Finer grain is worth it for ORWO — but it's essentially ONE move:** DE ≥10kg → Maersk (~€34.6k H1 / ~€84k/yr indicative). Not a 25-country re-fragmentation.
- **The exhaustive method = union-of-rate-card-breakpoints grid.** Contracts set grid edges (completeness), not thresholds; values stay computed.
- **`per_lane_band_optimum.py` left UNCOMMITTED** (principal): it carries 2 artifacts (the %-floor + the tie-break collapse). The validated logic is the inline union-grid scan, to be built fresh in the redo.
- The whole-country baseline (−€343k/yr) is unchanged and still the headline; the DE band move is additive.

## Pending external actions
None pending. (NFE `per_lane_band_optimum.py` + `band_sizing/` written to disk, deliberately not git-committed.)

## Plan / next move
The 5-step redo plan + the validated method + the three open method choices live in `inventory/orwo-band-grain-resume__364d42cd.md`. Next session is blocked on the principal locking: absolute floor value, tie-break rule, DE-only vs +FR.

## Cascade.
None — no canonical ORWO doc/digest updated this session (discussion + scratch sizing only). The `orwo-tender` domain digest is still un-created (tracked on `bank/domains/_index.md` bootstrap worklist); this session's finding is queued via the bank draft for that digest's eventual creation.

## Main-brain changes.
None to globals/meta/rituals. Brain footprint = this quest-log + the inventory resume + comms OPEN/CLOSING + 2 harvest drafts (1 bank, 1 examine), all in Jebrim's namespace.

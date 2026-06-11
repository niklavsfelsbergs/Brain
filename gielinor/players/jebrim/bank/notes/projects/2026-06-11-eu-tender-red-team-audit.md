# EU Tender 2026 red-team audit - findings and must-fix state

As of: 2026-06-09

- Audited state: bi-analytics `39c4595`. The arithmetic ties end-to-end; all directional calls SURVIVE: run the tender, migrate off UPS, keep Maersk on France, decline DPD's new offer, DB Schenker for freight.
- What does NOT survive: (1) the "conservative floor" framing - the era headline (EUR 377,471 / 12.77%, since superseded; live numbers in the bank/domains/ eu-tender digest) is a Q1 off-season best case; (2) confidence in the "add Hermes" call - the weakest call, defensible as coverage, not as saving at booked magnitude.
- Structural exposures: the saving leans on Hermes + Maersk-EU, the two engines with zero own-actuals to validate against, scored at face value; the trust-gate measures the winning (argmin) slice, a winner's-curse construction, not accuracy; the scenario selector's `mandatory_saving` has no per-parcel min(bid, real_invoice) floor, so it structurally rewards under-pricing engines - exactly why the unvalidatable ones dominate the pick.
- Hermes engine omitted a carrier-defined Manual Handling tier (~EUR 249k on 98,884 cross-section-breaching parcels) - biases the lean-on carrier cheaper. Guell rides a HELD (unconfirmed) rate card.
- Must-fix/confirm list (a)-(g): (a) confirm MAERSKUK baseline scope; (b) re-frame headline as Q1 best case, annual = separate re-weight; (c) state the Hermes/Maersk-EU face-value no-actuals caveat on the exec brief; (d) bias haircut or band on the Hermes + Maersk-EU migration; (e) fix the selector floor in decision_scorer.py (min(bid, real)) or report the [mandatory, migration] band; (f) regenerate bias_table.md + 10 stale docs, correct the false "FedEx unwired" governance statement; (g) note Guell/AP small own-actuals + UPS GRI 5% vs 5.9% + cross-track LPS inconsistency.
- Follow-through state as of 2026-06-10: 1 closed / 3 partial / 3 open ([[S194_907d4e63_eu-tender-holdup-pass-and-project-rating|S194]] D2 verified). (a) is the closed one - MAERSKUK confirmed a separate deal, out of tender scope; FR-only baseline deliberate.
- Cleared on verification (do not re-flag): GLS Stettin line-haul EUR 0 is carrier-confirmed correct; Maersk EU oversize took the conservative reading deliberately.
- Standing risk after the must-fixes: the Q1-to-annual re-weight magnitude (fuel/peak on the new-offer slice) was the largest unhedged item - addressed by the annualization spec, see [[2026-06-10-eu-tender-annualization-method-and-assumptions]].

Source research: [[2026-06-09-eu-tender-2026-red-team-audit]] - full sources and detail there.

# UPS OML/LPS — negotiated dimensional thresholds + the CUSTOM_OVERSIZED cohort hypothesis

**As-of:** 2026-06-11. **Session:** S199 (ee882f39). **Player:** Jebrim. **Status:** draft (principal-stated facts + an untested hypothesis).

## Negotiated thresholds (ours — override the published book)

- **LPS (Large Package Surcharge): triggers at length+girth > 325 cm** — our special negotiated condition (principal-stated 2026-06-11).
- **OML (Over Maximum): triggers at length+girth > 419 cm.**
- These OVERRIDE the UPS DE 2026 published book values (book: LPS >300 and ≤400 cm; Over-Max >400 cm — see [[2026-06-11-ups-de-2026-published-surcharges]]). Any band analysis on our UPS traffic must use 325/419, not the book numbers.
- The 2026-06-02 verify run ([[S-shipping-agent_pcs-pl-ups-oml-lps-verify]]) banded at exactly 325/419 — those bands were **correct**, though the run didn't record they were contractual. This note closes that gap.
- **Unconfirmed against our contract:** the book's secondary Over-Max triggers — longest single side > 274 cm, actual weight > 70 kg. Treat as hypotheses until the contract text confirms whether they're customized too.

## CUSTOM_OVERSIZED cohort hypothesis — TESTED, CLEARED (S199, 2026-06-11)

The S199 predictor investigation ([[S199_ee882f39_sa_ups-oml-lps-predictor]]) tested the deep-cohort cross (packagetype × dim band × weight band). **CUSTOM_OVERSIZED is NOT the predictor** — label ≠ physical: avg L+G 296, only 70 of 31,580 above 325; it behaves like any other just-under-threshold cohort (€95k net @ 1.9% incidence). The DHL-Paket caveat (categorical label, not physical fact) confirmed again.

**The actual predictor is UPS's own dimensioner measurement**, printed on the invoice (`packagedimensions`) next to what we keyed (`detailkeyeddim` = our declared, passthrough-verified). Verdict on €1.44M standing net: ~€425k over-trigger by our own dims (94% = ONE box: `zugeschnittene Verpackung` 130.3×91.6×7–10, L+G 327.5–333.5, **catalog dims** 2.5–8.5 cm over, charged ~50% in 2023–24 / 26.7% in 2026 — coin-flip incidence = physically threshold-straddling); ~€390k tolerance-zone 300–325 (UPS thin-axis inflation, STANZVERPACKUNG 120×90 epicenter); ~€641k dispute incl. the entire over-max family (zero parcels >419 by our dims ever; UPS measured lengths 1.5–2.7× keyed — physically implausible). Reversal coverage collapsed Q4-2025 → receivable accruing ~€160k+/qtr. The >325 box nearly vanished in 2025 (12 shipments) and returned in 2026 — ask PCS PL what changed.

## Related

- [[2026-06-11-ups-invoice-charge-profile]] — charge structure, oversize NET discipline (refund-in-place reversals).
- [[2026-06-09-carrier-invoice-dimension-coverage]] — UPS billed-dims handle: silver `ups_invoices.chargedescriptioncode IN ('LPS','OVR','OML')` for spend; bronze `csv_ups_zip_invoicedata` `packagedimensions`/`detailkeyeddim` for UPS-measured dims (~0.8% of lines, concentrated on oversize/freight lines).

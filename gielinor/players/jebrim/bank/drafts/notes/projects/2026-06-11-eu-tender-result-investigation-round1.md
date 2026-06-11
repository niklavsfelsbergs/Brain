# EU tender — result_investigation round 1 (Q01–Q06)

As of: 2026-06-11 (S196/5733cb1d). Source: bi-analytics
`2_analysis/result_investigation/` (README = index; per-question scripts + findings with
principal conclusions inline). Committed through Q04d at 98cdd49; Q05/Q06 pending commit.

**What the folder is.** Niklavs reviews the final report by question rounds; each question gets
a reproducible script + findings note + his recorded conclusion. Round 1 closed Q01–Q06.

**Durable claims (cite the findings files for detail):**
- Headline moved **€997,720 → €974,720/yr** after the FR incumbent rebase (q04f session):
  FR "today" was stale — DPD-FR stopped in January (cohort → Maersk, verified), UPS-FR light
  bands mid-migration. Carrier staleness was FR-only (18-dest sweep clean elsewhere).
- **Flows are per-origin slices of whole-cell decisions** (cell = dest×packagetype×1-kg band,
  standard types; variable types per-parcel). A flow row is descriptive, not a declinable
  decision; minority origin-slices can be dragged at a loss (keep candidate = dominant
  incumbent only).
- **UPS→DPD (192k) is a discretionary dial**: ~half the flow is GRI-avoidance; band-level
  threshold parks 25% for ~€1.1k/yr. Re-decide when DPD's final offer lands (+18.8% draft kills it).
- **UPS→Maersk (165k, €217k/yr) is the value flow** — real −17% gap, threshold doesn't bite;
  risk is offer-trust, managed contractually.
- **DHL CH** = genuine (Warenpost −48% + 0% fuel; customs like-for-like verified both sides —
  Picanova's own CH VAT account + Round-2 recipient-cleared). CH lane has NO DHL invoice history
  (98.6% UPS today) — offer-trust despite incumbent label. **AU** small (~€30k/yr) + optional.
- **Variable-track (CUSTOM_OVERSIZED etc.) routing is per-parcel cherry-pick** — UPS slice
  selected on ex-post billed fees, not executable ex ante. Recorded dims template-like
  (fee/no-fee parcels identical ~132×84×6); real dims at dispatch is the prerequisite for ANY
  executable rule. **The quantified dims prize: UPS oversize-fee pool €140.9k Q1 (~€675k/yr);
  plan rescues ~half; ~€190k/yr recurring LPS in standard cells is unreachable without dims**
  (q06 findings §Q06c).
- Packagetype LABEL CHURN mid-Q1 (W80x60AE→ORWO_80x60 18k/mo, ST120x90→120x80) — cells keyed on
  dead labels; q04e parallel session owns the deep-dive.
- Oversize book drifting DBS→UPS during Q1 (DE share 54%→41%) — added as 4th module-gate check.

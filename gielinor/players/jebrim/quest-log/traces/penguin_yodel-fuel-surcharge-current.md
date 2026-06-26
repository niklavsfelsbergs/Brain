# Penguin research — Yodel UK fuel surcharge current rate

**Spawned:** 2026-06-19 | **For:** Jebrim (UK shipping cost validation)
**Brief:** Verify whether published Yodel UK monthly fuel surcharge is still 18% (June 2026); report current rate, basis, recent trend.
**Deliverable:** research/2026-06-19-yodel-uk-fuel-surcharge-current.md

## Turn log

- Fetched primary source yodel.co.uk/fuel-surcharges + parallel search sweep. Primary confirms **18% effective June 2026**, basis May 2026 RFP £1,841.10/1,000 L, 14-Apr-2014 band.
- Pulled historic page — JS-driven, returned only single band values (11.0% on 1-Aug-2012 band, a different contract vintage). No chronological trend readable there.
- Two independent searches converge on **May 2026 = 19%** (basis April 2026 RFP £1,898.10/1,000 L). Trend = down one point M/M; diesel fell ~£57/1,000 L.
- Wrote research file. 18% holds — no material change vs assumption. Flagged contract-vintage mapping (14-Apr-2014 vs 1-Aug-2012) as the open verification.

**Status:** complete. Confidence high on current rate, medium on multi-month trend (historic page JS-blocked).

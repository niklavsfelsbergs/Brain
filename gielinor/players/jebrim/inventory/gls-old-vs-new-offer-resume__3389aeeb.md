---
quest: S201_gls-old-vs-new-offer
sid8: 3389aeeb
ts: 2026-06-11 15:55
open_dep: bi-analytics 1_offers/picanova/GLS/comparison/* uncommitted there (commit go pending)
---

# Resume — GLS old vs new offer comparison

## Status
analysis done — deliverable shipped + question answered in-session; only the bi-analytics commit is open

## Where we are
- Question ("why is GLS uncompetitive when the old contract was good?") answered and accepted by
  Niklavs ("ok got it"). Full findings in bi-analytics
  `2_EU_tender_2026/1_offers/picanova/GLS/comparison/findings.md`.
- Headline: tender +14.9% vs 2025 terms on the same Q1 parcels; +8.7% ABOVE GLS's own 2026
  continuation conditions. ~80–85% of the deterioration is the BASE CARD (flat 2–25 kg pricing
  abolished + ≤1 kg entry band +20–30%); stack adds a uniform +3.7% (new 4.1% dieselfloater,
  klima 2.5%, EFTA 25). Old-book lanes (NL/AT/BE/DK): +16.5% / +24.8% / +30.5% / +25.8%.
- Old-stack model validated vs invoiced actuals (shipping-agent): non-DE 28.8% actual vs 29.2%
  modelled; DE toll €0.380 exact. GLS volume ended 2025-07.

## Next concrete step
Ask Niklavs: commit the bi-analytics GLS comparison files (comparison/ scripts + findings.md +
parquets)? Optional follow-ups he may cue: (a) negotiation angle — ask GLS why the tender bid sits
above their own continuation pricing; (b) mart charge-bucket-mapping gap (GLS energy/klima/toll all
land in "Unclassified") if GLS analysis recurs.

## Files / paths to read first
- bi-analytics `2_EU_tender_2026/1_offers/picanova/GLS/comparison/findings.md` (the deliverable)
- `comparison/compare_old_vs_new.py` (re-runnable; stack constants + bridge)
- quest-log `S201_3389aeeb_gls-old-vs-new-offer.md` (turn narrative)
- bank draft `bank/drafts/notes/projects/2026-06-11-gls-old-vs-new-offer-why-worse.md`

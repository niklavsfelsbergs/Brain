---
quest: S202_eu-tender-negotiation-levers
sid8: 276897ca
ts: 2026-06-11 16:50
open_dep: 80x60 AE / 90x60 Wickel physical box-width verification (principal-owned: spec sheet or tape measure; optional 1-day DHL trial)
---

# Resume — EU tender negotiation levers (S202)

## Status
in-progress (analysis delivered in chat; one principal-owned verification open)

## Where we are
- Negotiation deliverable shipped: per-carrier levers + cost-position table on the no-Hermes plan book
  (DPD fuel ≈€156k/yr + non-sortable ≈€73k/yr; Maersk overpack €0.40/pcl ≈€75k/yr + fuel pin;
  DHL peak €148k/yr + toll/CO2 ≈€166k/yr; volume-cover: DPD +119% / Maersk +102% / DHL only +8%).
  Persisted: bank/drafts/notes/projects/2026-06-11-eu-tender-negotiation-cost-positions.md.
- DHL Sperrgut: NOT a negotiation lever — template knife-edge artifact (90x60 at d_mid 60.5 vs 60.0
  gate; DHL bills 1.3% in reality). Plan headline NOT affected on keeps (March-anchored invoices);
  real exposure = €29k/yr on 314 engine-priced switches + conditional €110–140k/yr unlock if the
  80x60 AE box (template 63cm, 17.2k Q1 parcels on DPD/UPS) physically measures ≤60.
  Persisted: bank/drafts/notes/projects/2026-06-11-dhl-sperrgut-template-knife-edge.md.

## Next concrete step
Ask Niklavs for the box-width verdicts (80x60 AE spec sheet / tape measure first — free).
If ≤60cm: fix the population template dims (or Sperrgut hit-rate), re-run cascade
(routing_2026q1 → annual_2026 → final_report), expect ~+€110–140k/yr headline move.
If >60cm: optionally run the 1-day DHL trial for the DE 80x60 AE cell (~190 parcels,
worst case ~€3.5k); readout = DHL invoice oversize lines in the mart for the trial cohort.

## Files / paths to read first
- bank/drafts/notes/projects/2026-06-11-dhl-sperrgut-template-knife-edge.md (the finding + trial design)
- bank/drafts/notes/projects/2026-06-11-eu-tender-negotiation-cost-positions.md (the lever table)
- bi-analytics `2_analysis/carriers/dhl_paket/surcharges/bulky_de.py` (the 120/60/60 trigger)
- quest-log S202_276897ca_eu-tender-negotiation-levers.md (T1–T10 narrative incl. the retraction chain)

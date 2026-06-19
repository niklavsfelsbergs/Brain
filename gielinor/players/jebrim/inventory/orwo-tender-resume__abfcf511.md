---
quest: S275_abfcf511_orwo-tender-contracts-coverage-weight-grain
sid8: abfcf511
ts: 2026-06-19
open_dep: harvest done (paused by Niklavs). Resume = build the tracking-grain ORWO repricing base. NFE 7_ORWO_tender_2026/ uncommitted (his call); bi-etl 5ab0322c2 local-unpushed.
---

# ORWO Tender 2026 - resume

## Where we are
Tender kickoff done. Standalone home `NFE/projects/7_ORWO_tender_2026/`. Contracts reviewed (UPS/DHL/AT-Post/Guell/old), mart coverage + invoices profiled, weight/dims fully traced. Key reframe: **base rates are weight x zone (no dims needed); ORWO is repriceable on weight.** Paused for harvest.

## Load-bearing facts (verified live 2026-06-19)
- **Weight:** mart `weight_kg` is per-ORDER packaging weight (~0.1-0.5kg), MIS-GRAINED. ORWO consolidated ~4.79 shipment_ids/tracking. True parcel weight = `parcelfinish.weight` (per tracking, ~100% all carriers) ~= invoice `billedweight` (UPS 0.5kg banding + 13% dim weight). Reprice at TRACKING grain.
- **Dims:** DHL2 Paket = real capture gap (~73% no packaging row; unfixable in warehouse). Other streams have dims via usedpackaging (wireable). DHL2 OK on weight alone (weight-tier priced + 94% invoiced).
- **POST gap CLOSED:** DHL Warenpost Intl = Deutsche Post (rate card in hand).
- **Contracts:** current 2026 cards UPS/DHL/AT-Post/Guell; GLS lapsed; AT-Post Factsheet + 2026 Guell card missing.

## Next concrete step
Build **tracking-grain ORWO repricing base** as an NFE topic/folder under `7_ORWO_tender_2026/`:
1. One row per physical parcel (tracking), ORWO, with: carrier, dest country, weight = COALESCE(invoice billedweight, parcelfinish raw rounded to carrier band), service.
2. Apply weight-tier rate cards (UPS + DHL first - solid cards + weights). DHL2 on weight alone.
3. Roll up to the tender comparison (current vs alternative carriers).

## Chase list
- AT-Post Factsheet (volumetric divisor, rural surcharge) - Jens Mertens.
- 2026 Guell rate card (contract has 2025 only).
- GLS fresh 2026 quote (old lapsed, dims-friendly).
- UPS monthly fuel index (35%-off-floating; not reconstructable from contract).

## Parked (separate scoped pieces)
- **bi-etl weight fix** = a per-parcel-grain weight-semantic redesign (NOT the superseded COALESCE in `bi_etl_fixes/01`). Implement ourselves, with SCM-impact check. After dims.
- **sendmoments** scope (ships under ORWO DHL acct; may be invoice+offer only, not PTS).
- **`orwo-tender` domain** - create the digest at next Jebrim alching. Routes: project state -> orwo-tender; mart weight-grain/consolidation/dims-capture -> shipping-mart (+bi-etl lineage); ORWO rate cards -> carrier-contracts.

## Anchors
NFE `projects/7_ORWO_tender_2026/` (all deliverables). Bank drafts (this session): `2026-06-19-orwo-tender-scope-and-cost-basis`, `2026-06-19-orwo-mart-weight-grain-and-consolidation`, `2026-06-19-orwo-carrier-contracts-2026`. Quest [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain]]. Prior ORWO: [[S266_e455d12d_orwo-box-grain-quota-estimator]].

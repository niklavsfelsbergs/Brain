---
quest: S275_abfcf511_orwo-tender-contracts-coverage-weight-grain
sid8: abfcf511
ts: 2026-06-19 (updated by session 6fbdcee1: roadmap + Phase-1 UPS slice)
open_dep: Phase 1 (UPS) pipeline built; base-rate gap RESOLVED (card validated vs silver Dom. Standard lines; the €5.41 "gap" was a mart base-bucket artifact). Next = rebuild actual-base from silver lines + reprice. NFE 7_ORWO_tender_2026/ uncommitted (his call); bi-etl 5ab0322c2 local-unpushed.
---

# ORWO Tender 2026 - resume

## Where we are
Tender kickoff done (S275). **Session 6fbdcee1:** wrote `roadmap.md` (5-phase plan) + built **Phase 1 UPS tracking-grain repricing base** end-to-end, verified live. Standalone home `NFE/projects/7_ORWO_tender_2026/`; new `repricing_base/` (sql/01 + findings.md). Key reframe holds: **base = weight x zone (no dims); reprice at TRACKING grain.**

## Phase 1 verified facts (live 2026-06-19)
- **Grain:** 128,805 UPS shipment rows -> 34,001 trackings (3.79:1). 5 dest countries: DE 91.8%, AT 5%, UK 2.7%, FR 0.5%, NO trace.
- **Cost source = MART** `SUM(real_shipping_cost_eur WHERE cost_source='invoice')`/tracking == silver netamount (€7.16 vs 7.27) -> equal-split, **SUM correct** (MAX undercounts). 74.8% cov, full order period. **Silver ups_orwo_invoices spans invoice dates Jan-Jun 2026** (275k ISO rows, ~9-15k trk/mo); lower bound ~Jan -> Oct-Dec 2025 ORDERS absent + recent lag (that's the 44% order-month match, NOT an Apr cutoff — earlier "Jan-Apr" was wrong). Silver = valid actual + billedweight + zone on its window; mart preferred for full-period coverage.
- **Weight:** COALESCE(billedweight_kg, parcelfinish.weight_grams/1000). pf superset 83.4%; billed (kg) subset 44%. Gateable (cost+weight) = 21,511 trk (63%).
- **Service code != contract product:** UPSWWE ships DE/UK/AT (not US/CA) -> zone off DESTINATION COUNTRY. UPSWWE/DE (3,798, no weight) = own stream, flagged.
- **MCP limit:** read-only conn blocks temp-table materialization (WITH CTEs + cross-schema CTE joins fail "transaction is read-only") -> use FROM-subquery joins. trackingnumber PII-guarded out of SELECT output.

## THE PHASE-1 FINDING (RESOLVED — card validated)
First gate looked alarming (mart base bucket €5.41 vs modeled €2.92-3.61, +50-85%). Traced to **silver charge lines** = closed it: actual forward freight (`Dom. Standard` line) matches the card to the cent by band — 3-5kg €3.26 vs card €3.26; 10+kg €5.77 vs €5.79; 5-10kg €4.14 (blend). **The card is CORRECT.** The "gap" was the mart `base_rate_eur` bucket: it sums across ~3.8 consolidated rows/tracking + bundles `Rückholservice`/service lines + RTS redistribution (S251) -> NOT the contract forward base, wrong gate target. NOT weight (billed≈actual, no dim uplift); gross-tariff hypothesis disproven by per-band match.
**Decision: INVOICES ONLY** (Niklavs — most reliable). Cost basis = silver `ups_orwo_invoices` charge lines; mart real cost DROPPED (bundled/consolidated/RTS-redistributed). No-invoice parcels = model-only (card x weight).
**No cheap-mail stream (self-corrected).** Earlier "big sub-gram ~€0.97 stream" was a query ARTIFACT — line-level `actualweight<=1` filter dropped the freight line, kept fuel+VAT companions. At tracking grain, genuinely-cheap (≤€1.50) = 49 trk = 0.4%, ~0% cost. DE UPS ORWO = 99.6% normal parcels avg ~6.5kg (68.6% are 3kg+). One population, one validated card. LESSON: band on per-tracking MAX weight, never a line-level weight filter.

## Next concrete step
**Rebuild the actual-base column from silver per-line forward freight** (`Dom. Standard`/`TB Standard`/`WW` + zone equivalents), not the mart base bucket = the correct reconcile + reprice target; model the light sub-3kg `Rückholservice` stream (~€0.97) separately. Then: extend zones/rates to AT/UK/FR (full matrices from xlsm), resolve UPSWWE/DE stream, then template the validated pipeline onto DHL (Phase 2).

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

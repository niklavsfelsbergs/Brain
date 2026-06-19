---
quest: S275_abfcf511_orwo-tender-contracts-coverage-weight-grain
sid8: abfcf511
ts: 2026-06-19 (updated by session e5be6eb5: SPINE CORRECTION + silver-anchored base build)
open_dep: SPINE CORRECTED — ORWO = production_site='Wolfen' (NOT source_system='ORWO'). Real UPS book = ~126k trks, cross-border-first (AT 41k > DE 33k > UK 21k > FR 12k > CH 5k > US 3k). Silver-anchored per-tracking base BUILT + validated (repricing_base/sql/02). RATE CARDS EXTRACTED + TRUST-GATED (repricing_base/rate_cards.md): cards reproduce invoiced freight to the cent. REPRICE ENGINE BUILT (repricing_base/engine/, EU-tender-style: build_rate_tables.py → parquet → calculate.py polars as-of join → run_gate.py). FULL-GRAIN TRUST GATE PASSES: modeled base €335k vs invoiced freight €345k = 0.971 portfolio; every material lane 0.98-1.00 (AT/FR/NL/CH/IT/ES/BE/LU ~0.998, DE 0.979). Misses are tiny tails (GB Economy DDP 0.911 = zone-35 tail routes to z34; DK 15trk wrong column; NO 3trk remote surcharge) — all documented in engine/README.md. cost_total 0.942 (the ~6% = unmodeled surcharge_other bucket). NEW UPS OFFER REPRICED (offers/UPS/, Niklavs uploaded 'Netto-Tarife ORWO Photolab - Tender 2026.xlsm'): SAVING €16,973 H1 / ~€34k/yr (4.4%), ALMOST ALL Switzerland (CH −€11.2k/−29%, light-parcel cut 11.44→8.04) + mid-weight DE (−€5.7k/−11%). AT (biggest lane 20k) + FR/NL/IT/ES + GB/US ALL UNCHANGED. Built offers/UPS/{build_offer_tables.py → rates_offer_standard.parquet, compare_offer.py → offer_vs_baseline.parquet, offer_summary.md}.
**BASIS CORRECTION (Niklavs, S280 post-close):** the €34k is the CONSERVATIVE frozen-today floor — wrong counterfactual. Do-nothing = today + the next UPS GRI (net rates are discounts off published tariff, which GRIs annually). So FLAT lanes (AT/FR/NL/IT/ES) ARE a saving = the GRI avoided; offer's true go-forward value vs do-nothing(+GRI) ≈ €50k/yr at ~5% GRI (€34k + ~€18k GRI-avoided on ~€352k flat-lane spend). This is the EU-tender go-forward-not-raw basis; I anchored on raw-today, too conservative. Also corrected the AT overstatement (5% off AT ≈ €12k/yr, NOT > CH's €22k/yr; ~9% to match CH; AT lane ≈ €246k/yr).
Next = **DHL PHASE 2 — the decided next engine (Niklavs, S280 close)**, ~65% of ORWO volume, biggest unpriced slice. Build mirrors UPS: (1) profile DHL spine (production_site='Wolfen', shipping_provider_group='DHL') + silver dhl_orwo_invoices (prod-code→product Paket/Warenpost/POST map, weight source+coverage per product, cost) on the corrected Wolfen spine — head start in coverage_and_invoice_profile.md §C but that was the OLD source_system='ORWO' spine, re-verify on Wolfen; (2) extract the DHL 2026 rate cards (Paket International + Warenpost International — PDFs, not xlsm, harder); (3) build silver-anchored base (invoices only) + product-routed engine + trust-gate, same engine/ pattern. Watch: DHL Paket-domestic has NO invoice weight → PTS backfill; Warenpost=POST=Deutsche Post (rate-card modeled, ~0.6% invoiced). MCP disconnected late S280 — pull via redshift_connector (NFE/.env creds), as the engine does.
Deferred (not chosen this round): re-baseline to do-nothing(+GRI) [needs ORWO GRI%]; cut-below-today AT ask; competitor offers (AT-Post/Güll/GLS/Maersk); annualization via seasonal ratios. NFE 7_ORWO_tender_2026/ uncommitted (his call); bi-etl 5ab0322c2 local-unpushed.
---

# ORWO Tender 2026 - resume

## ⚠ SPINE CORRECTION (session e5be6eb5, 2026-06-19) — supersedes the "DE 91.8%" facts below
**ORWO = `production_site='Wolfen'`, NOT `source_system='ORWO'`.** The old filter caught only a DE-heavy 34k sub-slice (the entire reason Phase-1 read "92% DE"). ORWO production lives at the Wolfen plant; the mart splits it across two source_systems — `ORWO` (34k) + `Picturator` (93k), both `production_site='Wolfen'` = ~126k UPS trks. PCS-PL (432k) stays the separate Picanova tender. The real book is **cross-border-first**: AT 41.4k > DE 33.1k > UK 21.4k > FR 12.2k > CH 5.2k > US 3.1k.

**Cost basis = silver invoices (INVOICES ONLY, S279), and silver is the COMPLETE spine for the invoiced population** — it carries trackingnumber + receivercountry + `zone` (UPS zone #) + billedweight + per-line cost. 93.5% (58,085) of the 62,107 silver freight trks match mart-Wolfen, but the mart adds nothing silver lacks. Mart-Wolfen reserved for the non-invoiced hole (model-only).

**ORWO is a white-label op:** ships for ~20 photo brands under 2 UPS accounts, both with ORWO 2026 rate cards — `0R6D66` ORWO Photolab proper (~12k, intl) + `0R6D51` shared reseller (~50k: Hofer/Rossmann/Aldi/Monoeuvre/Sendmoments/Bestecanvas/MeinFoto/Lidl/MyPoster/…). Tender scope (principal-confirmed) = the whole Wolfen book / both accounts. **Same `production_site='Wolfen'` key applies to DHL (Phase 2).**

**Validated cost shape (silver, freight>0, ex tax/duty) → `repricing_base/sql/02_ups_tracking_base_silver.sql`:** AT €6.08 (1.2kg, TB Standard) · GB €8.98 (Economy DDP) · DE €5.86 (8.6kg, Dom. Standard) · FR €5.81 · CH €13.80 (WW Standard) · US €14.03. Fuel ≈18% of freight throughout.

---


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

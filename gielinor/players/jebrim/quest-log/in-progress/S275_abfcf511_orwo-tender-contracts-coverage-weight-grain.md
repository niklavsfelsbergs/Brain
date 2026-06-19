# S275 - ORWO tender kickoff: contracts, mart coverage, weight/dims grain

**sid8:** abfcf511 - 2026-06-19 - continues the ORWO arc ([[S266_e455d12d_orwo-box-grain-quota-estimator|S266]] box-grain, [[S273_824518c9_orwo-may-quota-rate-vs-estimate|S273]]). NEW workstream: extend the carrier tender to ORWO (focus ORWO; sendmoments parked).

## Ask (Niklavs)
Start the ORWO carrier tender (sibling of the Picanova EU tender, project 2). Read ORWO contracts (old+new) and write up; stand up a standalone folder; check what we have (mart coverage + invoices); resolve the dims/weight question; figure out the bi-etl changes needed. Pause + harvest at the end.

## Done this session
- **Committed [[S266_e455d12d_orwo-box-grain-quota-estimator|S266]] bi-etl box-grain SQL** locally (5ab0322c2, feat/fif-ups-orwo-monthly) - NOT pushed. NFE topic 50 already committed+synced.
- **Standalone home:** `NFE/projects/7_ORWO_tender_2026/` (`_scope.md` + `contracts_review/` + `coverage_and_invoice_profile.md` + `bi_etl_fixes/`).
- **Contracts (5 dwarves, parallel):** UPS / DHL / Austrian Post / Guell / old-sweep -> `contracts_review/{ups,dhl,austrian_post,guell,_old_sweep,_index}.md`. **Base rates are weight x zone for ALL carriers - dims NOT needed for base** (5/5); **POST gap RESOLVED - DHL Warenpost International = Deutsche Post** (settlement code 66, billing 5311934365 66xx); GLS lapsed; AT-Post Factsheet missing; Guell card 2025-only.
- **Live mart coverage (Redshift MCP):** ORWO weight_kg ~58% NULL aggregate (NOT 77%), heterogeneous: POST 97% / DHL 29% / UPS 25%. Inverse to invoice coverage. `invoiced OR has-weight` ~93%.
- **Invoices carry weight:** UPS billedweight 100%/trk; DHL wgt+vol_wgt 100% for Warenpost/Intl prods (0% Paket domestic). UPS billedweight + DHL vol_wgt embed the oversize/dim effect.
- **Weight/dims trace (read bi-etl `shipping_mart/fact_shipments/sql/insert_to_silver.sql` Step 8e):**
  - Mart wires ORWO weight+dims via `orderdeliveryview.sendingorderingid -> usedpackaging -> packaging`. `parcelfinish` joined ONLY for PII; its complete `weight` unused.
  - **Dims gap = DHL2 Paket specifically** (usedpackaging match: DHLKP 99%, DHL2 27%, even allowing any sending-id). ~73% of DHL2 parcels have NO packaging-dims row -> true capture gap, not a fixable join. POST/Warenpost/Kleinpaket/UPS DO have dims (wireable).
  - **Weight is MIS-GRAINED, not just sparse:** mart `weight_kg` = `usedpackaging.weightg` = per-ORDER packaging weight (~0.1-0.5kg). ORWO CONSOLIDATED (~4.79 shipment_ids/tracking UPS; DAG: 20.7% shared, avg 9). True parcel weight = `parcelfinish.weight` (per tracking, ~100%) ~= invoice `billedweight` (same rounded to UPS 0.5kg bands + dim weight on 13%, +0.15kg avg). The naive COALESCE fix was DISPROVEN (parcel weight on order rows -> SUM over-counts ~5x).

## Corrections logged (verify-the-thing paid repeatedly)
- "dims all in Redshift, just unwired" -> FALSE for DHL2 Paket (real capture gap).
- fz/FOTOWELT/parcelfinish-key theory -> RED HERRING (mart uses orderdeliveryview numeric key, 100%).
- "invoice 9-11kg vs parcelfinish 3.4kg unresolved" -> consolidation-grain averaging artifact; per-tracking they reconcile (~2 vs 2.3kg).

## Decisions (Niklavs)
- Focus ORWO only; sendmoments parked (ships under ORWO DHL acct; may be invoice+offer only, not PTS).
- DHL2 on weight alone (no dims) - fine, weight-tier priced + 94% invoiced.
- Weight bi-etl fix SAVED/parked (now superseded to a grain-semantic decision) - implement ourselves, after dims. Don't trust the ETL team.

## Open / next
- Build the **tracking-grain ORWO repricing base** (one row per physical parcel): carrier + dest country + weight (invoice billedweight where present, parcelfinish raw else) -> weight-tier card. Start UPS + DHL.
- Chase: AT-Post Factsheet, 2026 Guell card, GLS fresh quote, UPS monthly fuel index.
- Mart weight-semantic fix = separate scoped piece (per-parcel grain + SCM impact). Dims for DHL2 = dead end (capture gap; PTSLive Oracle would be needed).
- **Create `orwo-tender` domain at next alching** (see resume + domains `_index` worklist).

## Pending external actions
None pending. (bi-etl 5ab0322c2 push is Niklavs' action, not a dangling pending; NFE tender folder committed at close.)

## Cascade
NFE repo `7_ORWO_tender_2026/` created + committed at close. bi-etl 5ab0322c2 committed local, unpushed (his push). No mart writes (all read-only). Brain: this quest + resume + 3 bank drafts + 1 examine draft + domains-index worklist line + 5 dwarf traces + comms OPEN/CLOSING.

---

## Increment — session 66b558bb (2026-06-19): DHL Phase 2 engine + offer transfer

"hey jebrim lets continue orwo tender" → built the DHL reprice engine (the decided next engine), then transferred the ORWO offers in from the EU-tender and refreshed the docs.

- **Profiled `enterprise_silver.dhl_orwo_invoices`** (1.73M rows / 571k trks, Sep25–Jun26, 98% DE / €2.86M = the domestic spine, inverse of UPS's cross-border book).
- **Decoded all prod codes authoritatively** via `enterprise_silver.shipping_charge_bucket_mapping` (the mart's own charge-bucket dim — Niklavs pointed me to it). Freight = `100510050` PAKET bis5kg / `100510100` bis10 / `100510315` bis31,5 / `275000002` Kleinpaket / `112000001` PAKET Intl Premium; surcharges = Maut/CO2 + energy + peak; `1610` = Sperrgut/bulky.
- **Overturned the resume's "DHL domestic has no invoice weight → PTS backfill" worry** (verify-the-thing paid again): the freight line is `wgt>0` 100% and the prod code IS the weight band; the "0% weight" codes were the FEE lines. Net `charge_amount` = `total`/1.19 (German VAT) reproduces the card to the cent (bis5 €3.35 / bis10 €4.95 / bis31,5 €10.55 / Kleinpaket €2.79).
- **Built the engine** `repricing_base/engine/{constants_dhl, build_dhl_rate_tables, calculate_dhl, run_dhl_gate}.py` + `README_DHL.md`, mirroring UPS. **Trust gate 0.9992** (modeled freight €1.907M vs invoiced €1.909M). Intl Premium deeply negotiated (AT €5.22 not the €13 published) → country rates invoice-derived (0.986).
- **Modeled the surcharge layer** (option a, Niklavs): `SURCHARGE_EXP` calibrated per freight product, split ongoing (Maut/CO2+energy, year-round) vs seasonal (peak+peak-in-peak, Nov–Dec). Gated 0.9995. **modeled cost_total €2.050M vs invoiced €2.052M = 0.9992.** Sperrgut/bulky €307k **UNPREDICTED by decision** (unexpected, residual, like UPS surcharge_other).
- **Transferred the ORWO offer set** from `2_EU_tender_2026/1_offers/orwo_sendmoments/` (PARKED there for "the future ORWO review pass" = now) → `7_ORWO_tender_2026/offers/{DHL,GLS,Maersk}/` (copy; binaries gitignored, EU-tender parked copy left intact). The new DHL ORWO Paket card (202604) holds domestic FLAT at baseline = GRI-avoided; intl/Warenpost/returns reprice is next. Stub `offers/DHL/offer_summary.md`.
- **Docs refreshed:** roadmap (Phase 2 DHL ✅, §4/§7 weight-risk RESOLVED, §8 deliverables), _scope (session-3 block), coverage_and_invoice_profile (DHL weight correction).

**Open / next:** reprice the DHL offer (parse 3 .xlsb → rates_dhl_offer_*.parquet → vs reprice_dhl_own.parquet, per offers/DHL/offer_summary.md TODO), then GLS + Maersk same machinery. Deferred UPS items (AT ask, do-nothing+GRI). NFE 7_ORWO_tender_2026/ uncommitted (his call). Late comms OPEN posted (require-open gate caught the skip).

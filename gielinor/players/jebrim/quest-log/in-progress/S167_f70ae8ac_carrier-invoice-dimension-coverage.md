# S167 — Carrier invoice DIMENSION-data coverage audit (shipping-agent sub-agent)

**Asked:** Which carriers provide DIMENSION data on their own invoices, and how complete is that coverage? (Raw layer, NOT gold dim columns — gold dims can be order/product-sourced and would mislead.)

**Scope / tier:** UPSTREAM, off the gold contract. Authorized via the maintainer overlay (tcg_nfe / CLAUDE.local). Evidence = `enterprise_silver.*_invoices` + charge-line tables (the cleaned per-carrier invoice sources). Raw vocab, no bucket collapse, no DQ cleaning.

## Turn log
- Enumerated full `enterprise_silver` + `enterprise_bronze` catalog; per-carrier invoice/charge-line sources are the silver `*_invoices` set + `db_schenker_lines` + `dpd_poland_struct1_charge_lines`.
- Pulled `information_schema.columns` across all per-carrier invoice tables; filtered + then full-column-scanned the no-hit carriers to confirm true absence vs filter miss.
- Real L/W/H fields found on 5 carriers: asendia_usa, maersk, ontrac, usps, yodel. Volume scalar: direct_link, hermes (+ dhl_orwo vol_wgt).
- Profiled non-null & non-zero coverage. Window: last 12 months where dated; fell back to all-time where the table is stale/recent-only.

## Headline result
- **6 of ~21 carriers** expose any dimension-shaped field on the invoice; only **5 give usable real data**, and only **4 with L/W/H**:
  - REAL L/W/H: maersk (100%), ontrac (100%), asendia_usa (~90%), usps (~81% manifest L/W/H).
  - REAL volume-only (no L/W/H): direct_link (~89%). hermes volume 67.6% but **stale 2020–2022 only**.
  - FIELD-PRESENT-BUT-ZERO: yodel (L/W/H 0% all-time), dhl_orwo (vol_wgt 0%), maersk cubic_value (0%, but its L/W/H is the real signal).
  - NO dimension field at all: ambro, apg, colis_prive, db_schenker, dhl(DE), dhl_america, dpd(DE), dpd_poland (all variants + charge-lines), dpd_uk, fedex, gls, ups, ups_orwo.

## Checks
- Verified asendia & maersk dim values are realistic varied measurements (not a placeholder constant).
- Caught a window artifact: yodel showed 7.8% on a 949-row 12m sliver but 0% across the full 1.25M-row table — reported the all-time 0%.
- Confirmed colis_prive `abnormal_dimension` is a surcharge amount, not a measurement.
- Confirmed table freshness per carrier (hermes historical-only; yodel Mar–May 2026; maersk/usps recent).

## Caveats
- Off the gold contract — raw per-carrier vocabulary, no curated guarantees.
- Carrier→table identity inferred from table naming; not cross-checked against the gold provider SQL on disk (DB was authoritative).

**Deliverable:** chat-only (table + summary returned to Jebrim).

---

## CORRECTION — UPS deep re-check (same session, Niklavs skeptical of the "ups: none" verdict)

The broad pass above concluded **ups / ups_orwo = NO dimension field** (line 18). **That is wrong.** It was drawn off the narrow silver `ups_invoices` (19 cols, weight-only) and a column-name scan; it never opened the full-fidelity bronze source.

### What the deep dive found
- Catalog enumerated all `ups`-named tables: silver `ups_invoices`(19c)/`ups_orwo_invoices`(22c); bronze `csv_ups_zip_invoicedata`(254c), `ups_orwo`(253c) + temp/zip variants. (`ga4_gana_campaign_groups` is a false "ups"-substring hit.)
- The **254-col bronze file carries REAL measured L×W×H**: `packagedimensions` e.g. `70.0x 41.0x 5.0` with unit `C`=cm, plus `detailkeyeddim` (keyed dims), `rawdimensionlength`, `scaleweightquantity`, `enteredweight` vs `billedweight`+`billedweighttype`. So UPS = class **(a) raw dims** — but raw dims are SPARSE (~0.8% of charge lines all-time; they sit on the freight line + the oversize surcharge lines only).
- **Dimension-DERIVED surcharge signal is abundant and reachable from SILVER** (charge-line values, not column names): codes AHC (Additional Handling, ~176k lines), SAH (Demand-Surcharge AH, ~85k), LPS (Large Package Surcharge, ~19,952 lines / €794k), OVR (Over Max Size, 2,173 / €147k), OML (Over Max Length, 692 / €57k). AHC/SAH net ~€0 (waived); LPS+OVR+OML ≈ **€998k** real dim-derived spend, silver history 2023-01→2026-05. This is the cost surface the PCS-PL oversize recovery work targets.

### Root cause of the miss
Prior pass scanned column NAMES; silver has no `oversize`/`dim` column, so it false-concluded "none". The oversize signal lives in **charge-description VALUES** (`chargedescriptioncode` AHC/LPS/OVR/OML), and the raw L/W/H lives in the **bronze 254-col file**, neither of which a name-scan on silver reaches. Same lesson as the yodel window artifact: profile values, not names.

### Caveats
- Off the gold contract — raw vocab. Bronze tables are recent snapshots (csv_ups_zip ~Mar–Jun 2026; ups_orwo Feb–Jun 2026); silver holds full history. Windows: bronze population profiled all-time + last-30d (dw_timestamp); silver surcharge €/lines all-time (transactiondate 2023-01→2026-05).

**Deliverable:** chat-only — full UPS verdict + column inventory + profile returned to Jebrim.

---

## EXTENSION — Ambro / APG / DB Schenker deep re-check (shipping-agent sub-agent, same S167 thread)

Same method as the UPS correction: open the WIDE bronze source per carrier, profile column population AND charge-code/description VALUES — do not name-scan the narrow silver invoice table. All three were in the "NO dimension field" list of the broad pass (line 18); two of them flip.

### Catalog (bronze = the wide source the broad pass skipped)
- Ambro: silver `ambro_invoices` 7c (weight-only) vs **bronze `ambro` 25c**.
- APG: silver `apg_invoices` 19c vs bronze `apg` 18c (silver actually has the surcharge cols too).
- DB Schenker: silver `db_schenker_invoices` 6c + `db_schenker_lines` 15c vs **bronze `db_schenker` 31c** (+ 3 bak/temp dup tables, ignored).

### Verdicts
- **Ambro = (a) RAW L×W×H.** `dimensions` 100% non-blank (format `L/W//H` cm, e.g. `182.00/10.00//122.00`), `shipment_volume` m³ 99.8% non-zero, `size` band labels (Mebel/Gabaryt), `weight` 96.8%. BUT window = **May–Oct 2023 only, 2,239 rows** — historical/dead feed, not live. Coverage rich, recency nil.
- **APG = (b) dim-DERIVED billing signal.** No raw dims. Dedicated `oversized_surcharge` (73 lines / £1,712) + `overweight_surcharge` (8 / £316) columns + `billed_weight` 100%. Window Oct-2023→Dec-2025, 46,158 rows. Surcharge incidence ~0.18% (lightweight stream, avg 2.15kg). Currency GBP.
- **DB Schenker = (a) volumetric/chargeable, the correct freight signal.** `cbm` (m³) 99.9% non-zero (avg 0.329), `grsw` (gross kg) 99.9% (avg 10.87), silver-lines `billed_weight` 100% (avg ~10.4 kg). `ldm` (loading-meter/lademeter) column PRESENT but **all-zero** (0/219,183). `taxw` (chargeable wt) only 5 rows. Window May-2023→Apr-2026, 219k rows. Charge codes are transport/fuel/MAUT/mobility — **no oversize/large-package code** (codes 550/301/620 etc. carry NO decode label, didn't speculate). Freight prices on cbm+chargeable-weight directly, so the volumetric measure IS the dim signal.

### Checks
- Ambro dims are varied real measurements per weight (not a placeholder constant) — confirmed via group-by.
- APG surcharge cols cross-checked bronze vs silver — both carry them; counts tie.
- DB Schenker `ldm` all-zero confirmed (0 non-zero across full table) — reported field-present-but-empty, not "has loading meter."
- Schenker charge codes: pulled decode labels; only generic codes (Transport/Fuel/MAUT/Mobility/System HOME) have labels — no oversize text in any value, so verdict rests on cbm/chargeable-weight, not a surcharge code.

### Net correction to the broad pass
Broad pass line 18 listed ambro, apg, db_schenker as "NO dimension field at all." Wrong for all three: Ambro has raw L×W×H (historical), APG has named oversize/overweight surcharge columns, DB Schenker has full volumetric+chargeable-weight. Same root cause as UPS — name-scanned narrow silver, never opened the wide bronze nor profiled charge VALUES.

### Caveats
- Off the gold contract — raw per-carrier vocab, no curated guarantees.
- APG surcharge euros are GBP-denominated in bronze (silver has total_price_eur but the surcharge cols stay GBP).
- Carrier→table identity by table naming; DB authoritative.

**Deliverable:** chat-only — full per-carrier verdict + inventory + profile returned to Jebrim.

---

## EXTENSION — FedEx/DHL + GLS/Yodel/Colis-Privé re-check + DPD (4-agent fan-out, same S167 thread)

Niklavs approved re-running ALL "no dims" carriers with the deep method. 4 shipping-agents fanned out. DPD has its own sub-trace file (`S167_f70ae8ac_dpd-dimension-coverage-reaudit.md`). Net: the first pass's negatives were mostly a silver-name-scan artifact; most flip.

### FedEx / DHL agent
- **FedEx = (a)+(b), richest carrier.** Bronze `fedex_invoicedata_historical` (158c): raw L/W/H populated **91% all-time** (1.56M/1.71M) + `package_size` band + rated-vs-actual weight. Derived: `AHS - Dimensions` €1.05M, `Oversize Charge` €338k, Add'l/Demand Handling, Peak-Oversize → **~€1.86M** dim-derived. (FedEx `dw_timestamp` is a uniform load-stamp — can't slice recent; 91% is all-time.)
- **DHL DE = (c).** `volwgt` non-zero 0.004% of 26.8M; `extrachargeamount` rolled up, no description split. Genuine none (oversize billed but invisible).
- **DHL America = (c).** `description` is a service name, no surcharge/dim text.
- **DHL ORWO = (c).** `vol_wgt` column 100% empty (0/1.68M).

### GLS / Yodel / Colis-Privé agent
- **Yodel = (a), prior "0%" WRONG.** Bronze `yodel` (47c) `actual_length/width/height` (mm) + `actual_volume` (m³): **~45% recent (Oct 2025+), 7.4% all-time** — live & growing. Silver was 0%, bronze is populated (the exact failure mode).
- **GLS = (b).** Weight-only columns; signal in `bezeichnung` VALUES: Übermaß €20.5k / Großpaket / Überlänge / Volumen (~€22k tight oversize) + `Nicht sortierfähig` €527k (39.9% of parcels, shape-driven handling — broader than oversize, list separately). Bronze encoding mojibake needs a normalization map.
- **Colis Privé = (b), trivial.** `abnormal_dimension` = flat €5.95 fee (65 lines, €387), NOT a measurement. No raw dims.

### DPD agent (see sub-trace for detail)
- **DPD DE = (a)** raw L/W/H ~9% but feed ends ~2024-09 (stale). **DPD UK = (b)** £46k oversize, live. **DPD Poland = (b)** ~€33k "exceeding technical limitations", live.

### Net corrected picture (full map → bank draft)
~10 carriers real measured dims (Tier1 live: Maersk/OnTrac/FedEx/Asendia/USPS/DB-Schenker/Direct-Link; Tier2 partial: Yodel/UPS; Tier3 stale: DPD-DE/Ambro/Hermes), 5 derived-only (DPD-UK/GLS/DPD-PL/APG/Colis-Privé), 3 nothing (DHL DE/America/ORWO). Full table + caveats: `bank/drafts/notes/projects/2026-06-09-carrier-invoice-dimension-coverage.md`.

### Method lesson (the load-bearing takeaway)
Per carrier: profile the WIDEST bronze source (not narrow silver) AND charge-DESCRIPTION values (not column names). A silver column-name scan reaches neither the raw L/W/H (bronze) nor the oversize signal (charge values) — it false-concludes "none." Verified per-instance across 21 carriers; did not generalize one carrier's shape to the rest.

## Reconcile
No pending external actions — read-only mart audit, all deliverables are brain-side (bank draft + this trace + chat). Deliverable form: chat + bank draft note; report-doc render offered, not requested.

## Open (carry-forward, non-blocking)
1. DPD DE — post-2024-09 feed currency? 2. Ambro — retired or renamed feed? 3. Optional: reconcile carrier→table vs gold provider SQL. 4. Promote bank draft at next alching.

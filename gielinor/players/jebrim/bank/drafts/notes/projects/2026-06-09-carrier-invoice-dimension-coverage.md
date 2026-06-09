# Carrier invoice DIMENSION-data coverage map (raw upstream layer)

**As-of:** 2026-06-09. **Session:** S167 (f70ae8ac). **Player:** Jebrim.
**Question answered:** Which carriers provide DIMENSION data on their own invoices, and how complete is that coverage?
**Tier:** UPSTREAM — off the gold contract. Evidence = `enterprise_bronze.*` (wide source files) + `enterprise_silver.*_invoices` / charge-line tables. Authorized via the maintainer overlay (`tcg_nfe` / `CLAUDE.local.md`). Raw vocab, no bucket collapse, no DQ cleaning. Read-only.

> **Method caveat — this overturned a first pass.** A first audit name-scanned the *narrow silver* `*_invoices` tables (weight-only) and false-concluded "no dims" for ~14 carriers. Proven wrong (UPS, then FedEx/DPD-DE/Yodel/Ambro/DB-Schenker). **The discipline, per carrier:** (1) profile the *widest bronze source*, not the narrow silver table; (2) profile charge-DESCRIPTION **values**, not just column names — oversize/handling signal lives in `chargedescription` values, raw L/W/H lives in the wide bronze file. A column-name scan reaches neither.

## The bottom line
Of ~21 carriers with raw invoice sources: **~10 carry real measured dimensions** (L×W×H or volumetric), **5 carry a dimension-DERIVED oversize/handling billing signal only** (no measurement), and **3 (the DHL feeds) give nothing usable.** "Provides dims" splits hard on **currency** (EUR vs GBP) and **recency** (several rich sources are stale/dead feeds).

## Two classes of signal
- **(a) raw measured dimensions** — L/W/H or volume actually on the invoice line.
- **(b) dimension-DERIVED billing signal** — oversize / large-package / additional-handling / over-maximum surcharge codes, or a billable-vs-actual weight gap. The carrier *assessed* size but didn't expose the measurement.

## Tier 1 — real measured dimensions, well-populated, current
| Carrier | Field | Coverage | Source table | Notes |
|---|---|---|---|---|
| Maersk | L/W/H (cm) | 100% | `maersk_invoices` | `cubic_value` 0%; L/W/H is the real signal. `is_rated_dimensional_weight` flag present |
| OnTrac | L/W/H (in) | 100% | `ontrac_invoices` | carries declared + billed dim triplets |
| FedEx | L/W/H (+ rated vs actual wt, `package_size` band) | 91% all-time | bronze `fedex_invoicedata_historical` (158c) | richest carrier; see Tier-4 derived too |
| Asendia USA | L/W/H | ~90% | `asendia_usa_invoices` | realistic varied measurements |
| USPS | manifest L/W/H | ~81% | `usps_invoices` | carrier-*assessed* dims only 6.7%; dim-weight 4.1% |
| DB Schenker | `cbm` volumetric m³ | 99.9% | bronze `db_schenker` (31c) | freight — volume *is* the dim signal. `ldm` (loading-meter) column present but all-zero |
| Direct Link | volume scalar | ~89% | `direct_link_invoices` | volume only, no L/W/H |

## Tier 2 — real dimensions, partial / split signal
| Carrier | Field | Coverage | Source | Notes |
|---|---|---|---|---|
| Yodel | actual L/W/H (mm) + volume (m³) | ~45% recent (Oct 2025+), 7.4% all-time | bronze `yodel` (47c) | first pass said "0%" (silver) — WRONG; bronze populated & growing. Live. `declared_*` dims empty; the populated set is `actual_*` |
| UPS | L/W/H (cm) | ~0.8% of lines | bronze `csv_ups_zip_invoicedata` (254c) | raw dims only on freight + oversize lines. Plus the big derived signal below — UPS is (a)+(b) |

## Tier 3 — real dimensions but STALE / dead feed (do NOT count as live coverage)
| Carrier | Field | Coverage | Window | Source |
|---|---|---|---|---|
| DPD DE | L/W/H (cm) | ~9% of parcels | feed ends ~2024-09 | bronze `dpd_historical` (61c) / `dw.v_shipping_invoices_dpd`. dims concentrate in `dimtype` QU/VL/UL (long flat canvas ~110×71×7cm) |
| Ambro | L×W×H (cm, `L/W//H` string) + volume | 100% | 2023 May–Oct only (2,239 rows) | bronze `ambro` (25c) — dormant |
| Hermes | volume | 67.6% | 2020–2022 only | `hermes_invoices` — historical |

## Tier 4 — dimension-DERIVED billing signal only (oversize/handling, no measurement)
| Carrier | Signal (charge codes) | Size | Live? | Currency |
|---|---|---|---|---|
| UPS | LPS (Large Package) €794k / OVR (Over Max Size) €147k / OML (Over Max Length) €57k; AHC/SAH present but waived ~€0 | **~€998k** (2023→2026) | yes | EUR |
| FedEx | `AHS - Dimensions` €1.05M, `Oversize Charge` €338k, Demand/Additional Handling, Peak-Oversize, Unauthorized OS | **~€1.86M** | yes | EUR |
| DPD UK | `oversized_overweight_charge` £46.3k, non-conveyable handling £11.3k, peak £1.3k | **£46k** oversize | yes | **GBP** |
| GLS | tight oversize: Übermaß €20.5k / Großpaket / Überlänge / Volumen (~€22k total); broad: `Nicht sortierfähig` €527k (39.9% of parcels, shape-driven handling) | €22k tight / €527k broad | yes | EUR |
| DPD Poland | struct1 `charge_description`: "Exceeding the technical limitations" €31.7k + non-standard parcel + weight-verification | **~€33k** | yes | EUR |
| APG | `oversized_surcharge` £1.7k + `overweight_surcharge` £316 | £2k (trivial, ~0.18% of lines) | yes | **GBP** |
| Colis Privé | `abnormal_dimension` = flat **€5.95** fee (NOT a measurement), 65 lines | €387 total | yes | EUR |

## Tier 5 — genuinely no usable dimension signal
| Carrier | Why | Nuance |
|---|---|---|
| DHL DE | `volwgt` non-zero on 0.004% of 26.8M rows; charges roll up into one undescribed `extrachargeamount` | oversize likely billed but invisible — no charge-line description split |
| DHL America | `description` is a service name (SmartMail Parcel Expedited/Plus), no surcharge/dim text | "Plus" tier is at best a coarse size/weight-band proxy |
| DHL ORWO | `vol_wgt` column exists but **100% empty** (0/1.68M); `prod` codes opaque, `extra_charge_amount` undescribed | present-but-empty column = feed-completeness gap, not "doesn't measure" |

**Distinction worth keeping for any report:** *absent column* (DHL America) vs *present-but-empty column* (DHL DE, DHL ORWO, Yodel-in-silver, DB-Schenker `ldm`, Maersk `cubic_value`, UPS `oversizequantity`). The empty-column cases are feed gaps to raise with the carrier/ingestion owner, not inherent "no measurement."

## Cross-cutting caveats
- **Mixed currency.** EUR for most; **GBP for DPD UK + APG surcharges**. Any cross-carrier EUR rollup needs an FX step.
- **Recency vs all-time.** Tier 3 carriers have rich dims on dead feeds; always state the window.
- **GLS `Nicht sortierfähig` (€527k)** is size/shape-driven but broader than oversize — list separately or it overstates dim-derived oversize spend.
- **GLS bronze encoding mojibake** — `bezeichnung` has multiple byte-encodings of the same German label; a clean rollup needs a normalization map.
- **FedEx `dw_timestamp` is a uniform load-stamp** (not a per-row date) — can't cleanly slice a recent window; 91% is all-time over loaded history (`shipment_date` 2021-09→).
- **Off the gold contract throughout** — raw per-carrier vocab, no curated guarantees; numbers are raw invoice-line aggregates, not mart-reconciled.

## Open verification items (carry-forward)
1. **DPD DE** — did it move to a new feed after ~2024-09 that preserves dims? This audit can't see post-2024-09 DE.
2. **Ambro** — retired, or shipping under a renamed feed? Rich dims but a dead 2023 window.
3. Carrier→table identity was inferred from naming + confirmed against the live DB, NOT cross-checked against the gold provider SQL (`bi-etl/dags/shipping_mart/fact_shipment_invoice_lines/sql/providers/`). Belt-and-suspenders reconcile available on cue.

## Operational handle (for the PCS-PL oversize recovery work)
The usable spend handle for UPS oversize recovery is silver `ups_invoices.chargedescriptioncode IN ('LPS','OVR','OML')` (~€998k, full history) for the *spend*, joined to bronze `packagedimensions`/`detailkeyeddim` for the *measured dims* on the subset of lines that carry them. Raw dims are too sparse (~0.8%) to anchor a claim alone — the surcharge codes are the better basis.

## Source quest-log
- `players/jebrim/quest-log/in-progress/S167_f70ae8ac_carrier-invoice-dimension-coverage.md` (main: broad pass + UPS correction + Ambro/APG/Schenker)
- `players/jebrim/quest-log/in-progress/S167_f70ae8ac_dpd-dimension-coverage-reaudit.md` (DPD sub-trace)
- FedEx/DHL + GLS/Yodel/Colis-Privé findings: returned in-session (S167 synthesis section).

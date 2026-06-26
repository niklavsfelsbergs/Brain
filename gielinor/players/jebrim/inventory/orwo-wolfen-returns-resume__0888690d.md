---
quest: S372_orwo-wolfen-returns
sid8: 0888690d
ts: 2026-06-26 10:40
open_dep: his — send the DHL-meeting Excel/questions (Mon) + ask the ops trigger; optional mine — UPS raw tab + full-export refresh
---

# ORWO / Wolfen returns cost — resume (S__0888690d)

**Ask (Niklavs/Jebrim):** "We pay tons for returns for production site Wolfen — why? Specific customer, specific products, what?" Scope confirmed = ORWO production-site book (mart `production_site='Wolfen'`); compute returns from **raw carrier invoices** since the gold mart has no returns section.

## Why off-mart (justified departure)
Gold `shipping_mart` cannot isolate returns: UPS RTS rows are filtered out of the cost summary and **redistributed onto the original outbound parcel**, and RTS ≥90 days old are dropped (`shipping-agent/reference/sources.md:133`). `is_returned` col exists but is unconfirmed/do-not-use. So returns come from raw `enterprise_silver.{ups_orwo_invoices, dhl_orwo_invoices}` (tcg_nfe access; shipping-agent is gold-only and can't reach these).

## Return signal (how to identify)
- **UPS ORWO:** `ups_orwo_invoices` where `chargecategorycode='RTN'` (NOT a description text match — RTN category catches the freight/fuel components too).
- **DHL ORWO:** `dhl_orwo_invoices.prod` joined to `enterprise_silver.shipping_charge_bucket_mapping` (carrier_name='dhl') where `charge_description_english` LIKE '%retoure%' / '%rücksend%' / '%return%'. All return prods sit in `charge_bucket='other'`.

## Findings (verified)
- **The "tons" = a real DHL return-RATE surge from ~March 2026.** Return rate (returns ÷ outbound parcels) on the DHL ORWO book: 0.03%→0.25% (Oct'25–Feb'26) → **6.5% Mar → 8.5% Apr → 11.5% May → 9.2% Jun.** Outbound volume *fell* over the period, so it's a ~50× rate jump, not volume. Confirmed it's not a volume artifact.
- **DHL ORWO return cost:** ~€86k Mar–Jun 2026 (€18.4k/21.4k/29.7k/16.7k), ~€95k all-in incl. the small pre-March tail. Recent run-rate €21–30k/mo → **~€260–300k/yr.**
- **Driver product:** consumer self-service return labels — *DHL RETOURE (GK) up to 31.5 kg* €61.8k + *DHL RETOURE Online* €21.1k. The surge is a new return **channel**, not pre-existing return products scaling.
- **UPS ORWO returns — ALSO popped in March (parallel to DHL).** (Corrected: my first read "Jan14–Mar9 window" was a varchar string-sort artifact — silver UPS runs through June; parse `invoicedate` with `CASE WHEN LIKE '%/%' THEN MM/DD/YYYY ELSE YYYY-MM-DD`.) RTN by month: Jan €56 / Feb €13 → **Mar €1.8k / Apr €7.0k / May €5.3k / Jun €4.6k** (~€18.7k Mar–Jun). Rate 0.02%→4.6%→10.5%→12.6% — same ~0→~10% jump, same months as DHL.
- **UPS return TYPE = prepaid return-pickup service, NOT failed-delivery.** "Rückholservice Dom. Standard" (detail code RS, the return-PICKUP service) = €11.7k + fuel/tax ≈ €16.5k / 3,542 trks — the UPS equivalent of DHL RETOURE. True "Undeliverable Return" (RTS, failed delivery) = only ~€1.9k, flat → NOT the driver. Rules out "deliveries are failing."

## The attribution wall — PROVEN not recoverable (4 paths exhausted)
"Specific customer / specific product" is **not recoverable from the data** for the bulk of returns:
1. **Return `identcode` → outbound order:** only 517 of ~25k returns (2%) match `orwo_pts_parcelfinish.trackingnumber` — the DHL return label has its OWN tracking, not the outbound parcel's, so it doesn't link to the order/brand/product.
2. **Silver `shippers_reference`:** 98% = `'(Y)'` (masked).
3. **Bronze raw `dhl_orwo.shippers_reference`** (less masked than silver): still **96% (€82.9k) bare `'(Y)'`** — no order/brand/product. Only ~€2.5k (3%) carries order numbers (`FOTOWELT-RM-…`, `MFA…`, `4201-…`); a thin tail is `Wareneingang FZ` (central goods-inward) / `Sendmoments` / `ShopNNNN`.
4. **`name_1` / postcode:** `'X'` masked in silver; bronze `name_1`='X' too.
→ The dominant returns are **anonymous consumer self-service DHL return labels routed to a central goods-inward address** — by construction they carry no brand/order/product. Confirmed, not assumed.

**UPS return lines checked too (same wall):** `sendercompanyname` uniformly "ORWO PHOTOLAB GMBH" (white-label op, not brand); single account 0R6D51 (no vertical split); `trackingnumber`/`leadshipmentnumber` = the return's own 1Z0R6D519… (99.4% no mart match → doesn't link to outbound order); `shipmentdescription` blank; `receiverpostal` = 305 scattered consumer postcodes (top 06766=Wolfen, rest dispersed), not brand return-centers. No customer/vertical signal in UPS invoices. **Root cause = white-label pooling: ORWO bills all brands' returns under its OWN UPS/DHL accounts; vertical lives only on the outbound order (mart `source_system` / PTS `senderkeyaccountid`), and the return is a fresh parcel that doesn't reference it.**

## Best-available "which customer" = INFERENCE from outbound DE brand mix
Since returns can't be attributed directly, the proxy = brand mix of the DE consumer **outbound** parcels generating them (`orwo_pts_parcelfinish`, carrier DHL, dest DE, Mar→, `senderkeyaccountid`):
Rossmann **76.4k** + rmonline (Rossmann online) 26.6k ≈ **~half the DE consumer book**; then Aldi DE 18.3k, TCG 14.8k, Sendmoments 10.2k, ORWO/PixelNet 8.6k, MeinFoto 6.7k, Lidl DE 6.3k, PosterXXL 2.3k, myposter 1.7k. **Caveat: assumes uniform return rate across brands** — unverifiable, and the "new channel" surge could be concentrated in whichever brands enabled the return portal. Label as inference, not measurement.

## WHY March — ANSWERED from data (new return product activated)
The data pins the mechanism (not a guess):
1. **A new return product appears from zero in March.** Pre-March (Oct–Feb) return lines = only small "Rücksendeentgelt" fees + a RETOURE-Online trickle (~€1–3k/mo); the product *"DHL RETOURE (GK) up to 31.5 kg"* does NOT exist on the ORWO book. **March: it appears from €0 → €17.4k (4,355 returns), holds ~€18k/mo**; its "Energiezuschlag DHL RETOURE" surcharge appears the same month, also from zero. The OLD return fees continue unchanged underneath → **net-new volume under a net-new product**, not a recode. A 2nd product, *"DHL RETOURE Online,"* ramps from May (€10.7k) = phased rollout.
2. **Not a billing backlog — real activity.** `pu_date` (pickup) month tracks `invoice_date` month (March invoices = March pickups; May = May). No lump of old pickups dumped into March billing. Parcels physically started returning in March.
→ **Mechanism = a new DHL prepaid consumer return-label product was switched on in the ORWO DHL contract in March 2026** (~4,500 returns/mo @ ~€4 ≈ €18k/mo + RETOURE-Online wave from May). A channel going live, not a quality collapse.

3. **BOTH carriers, same month = deliberate ORWO return-PROGRAM launch (not a carrier quirk).** UPS shows the identical pattern via a prepaid return-pickup service ("Rückholservice"), from ~zero → €1.8k Mar → €7k Apr (rate 0.02%→~10-12%). Two independent carriers switching on a prepaid return service in the SAME month can't be an organic quality drift or one contract change — it's an ORWO-side return program/policy going live ~March 2026. Failed-delivery RTS stayed flat & tiny, so it's NOT a delivery-quality problem.

**Combined return cost (UPS + DHL), Mar–Jun 2026 ≈ €105k** (~€26–30k/mo run-rate → ~€300–350k/yr).

## What's STILL ops-only (not in data)
WHO activated it / for which brands, and the business reason (e.g. a partner mandating free returns). The mechanism is provable; the trigger above it needs ORWO ops.

## Deliverable shipped (NFE topic 51)
`bi-analytics-main/NFE/shipping_topics/51_orwo_wolfen_returns/` — committed `ee90a08` (standing NFE auth, NOT pushed). Contents: `findings.md` (full writeup), `build_returns_excel.py` → `data/orwo_wolfen_returns_dhl.xlsx` (DHL-meeting workbook: Overview+Questions tab, Returns-by-charge-type, Monthly trend+rate, Product×month onset, May detail), `sql/` (DHL+UPS May filters + aggregates). `data/` is gitignored → xlsx + CSV force-added. **Raw-invoice-lines tab = the real full May export (14,522 lines, every column populated incl. invoice number / DHL ident / dates / weight).** When the Redshift MCP was down, pulled directly via `pull_dhl_returns.py` (`redshift_connector` + `tcg_nfe` creds from `NFE/.env`; host `bi.c5lrs7vtwcpl…:5439/bi_stage_dev` from `brain/.mcp.json`) → `data/dhl_returns_may_raw.csv`; builder's CSV branch renders it. Euro cols fixed to 2dp. **Direct-connector pattern is the MCP-down fallback for silver pulls.**

## Status: investigation complete + NFE topic 51 shipped (for Andrea's Mon DHL meeting). Open = (his) send to DHL / ask the ops trigger; (mine, on DB reconnect) append line-level rows tab.

**Carrier scope note:** ups_orwo_invoices = account 0R6D51 (ORWO). The general `enterprise_bronze.shipping_ups_returns_addition` (€245k) is the **Picanova PCS-PL** UPS book, NOT Wolfen — do not use it for ORWO returns.

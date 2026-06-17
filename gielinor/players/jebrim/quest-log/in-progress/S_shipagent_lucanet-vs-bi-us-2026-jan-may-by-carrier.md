# Shipping-agent pull — LucaNet-vs-BI reconciliation input: US, 2026 Jan–May, by carrier

**Spawned by:** Jebrim. **Tier:** gold-contract (`shipping_mart`, four facts). No `CLAUDE.local.md` → gold-only perimeter absolute.
**Deliverable:** chat-only (reconciliation input; no chart requested).

## Ask
BI-side shipping cost for US, calendar 2026 Jan 1 – May 31, by carrier + grand total, for comparison vs a LucaNet accounting export. Cost basis = booked invoiced actuals off the invoice-lines fact; native currency, no FX.

## Scope/basis decisions (stated)
- **US scope = origin/booking axis** → `production_site IN ('PCS CMH','PCS PX')` (Columbus OH + Phoenix, the two US print sites). This is the origin-ledger reading (rule 37) that matches a US accounting entity. Alt destination-US reading (`destination_country_code='US'`) gives a *different* population/total — surfaced as a fork.
- **Date** = `fact_shipment_invoice_lines.shipment_date`, BETWEEN 2026-01-01 AND 2026-05-31 inclusive (per brief).
- **Cost basis** = `SUM(charge_amount_eur)` off `fact_shipment_invoice_lines`, EXCLUDING buckets `tax` + `customs_duties` (freight-only, rule 13). Invoice-lines = invoiced actuals only (the go-forward booked cost, not expected/avg/modeled).
- **Currency** = EUR (`charge_amount_eur`). A `charge_amount_local` exists (native invoice ccy, USD for these carriers) but NOT summed — Jebrim handles FX in synthesis.
- **Carrier field** = `shipping_provider_group` (raw values shown for LucaNet crosswalk).

## Result (freight-only EUR, invoiced actuals)
| Carrier (raw) | Freight EUR | Inv lines | Shipments |
|---|--:|--:|--:|
| ONTRAC | 1,225,981.91 | 451,329 | 130,826 |
| USPS | 583,674.89 | 90,668 | 90,648 |
| FEDEX | 536,083.46 | 125,426 | 26,788 |
| ASENDIA USA | 372,573.07 | 54,585 | 18,197 |
| UPS | 136.81 | 64 | 9 |
| **TOTAL** | **2,718,450.14** | **722,072** | — |

## Checks
- Per-carrier sum = €2,718,450.14, ties exactly to independent cross-check `origin_us_freight_eur` (€2,718,450.1371). Reconciled.
- tax/customs split: ~€48 tax on US carriers total — excluded, immaterial.
- May NOT obviously partial by total (€603K, highest month) BUT last week of May still backfilling (latest invoice_date 2026-06-02; final-week freight lowest). Late-May is a soft floor.
- Orphan lines: ~€14.6K US-carrier freight on null-shipment_id lines (mostly FedEx €9.4K) drop out of the origin join — unattributable to a US site.
- No DHL America / negligible UPS on US origin this window — LucaNet's UPS+DHL crosswalk rows are ~zero on BI side.

## Open
- US definition fork (origin vs destination) — picked origin to match ledger; confirm with Jebrim if LucaNet entity is destination-keyed.

---

## Follow-up pull (2026-06-16) — native-USD carrier × MONTH matrix
**Ask:** final cut for the LucaNet-vs-BI deliverable — carrier × month matrix, native USD, US-origin, 2026 Jan–May. Same scope/date/basis as above but currency = `charge_amount_local WHERE currency_code='USD'` (native, no FX). Spreadsheet paste-in + exact SQL.

**Matrix (native USD, freight-only invoiced actuals, shipment-month):**
| Carrier | Jan | Feb | Mar | Apr | May | Total |
|---|--:|--:|--:|--:|--:|--:|
| ONTRAC | 331,419.07 | 299,205.60 | 227,144.39 | 239,410.83 | 337,171.71 | 1,434,351.60 |
| USPS | 160,395.05 | 134,055.54 | 99,678.45 | 147,205.62 | 142,003.31 | 683,337.97 |
| FEDEX | 96,843.76 | 99,315.00 | 106,888.05 | 192,122.59 | 131,997.70 | 627,167.10 |
| ASENDIA USA | 112,395.46 | 77,972.23 | 71,328.14 | 80,598.63 | 93,516.98 | 435,811.44 |
| **TOTAL** | **701,053.34** | **610,548.37** | **505,039.03** | **659,337.67** | **704,689.70** | **3,180,668.11** |

**Checks (all tie):**
- Grand total 3,180,668.1083 → ties to prior native-USD US total $3,180,668.10 exactly.
- Each carrier row ties to prior per-carrier USD: OnTrac 1,434,351.60 ✓ / USPS 683,337.97 ✓ / FedEx 627,167.10 ✓ / Asendia 435,811.44 ✓.
- Both axes reconcile to grand total (carrier-sum = month-sum = 3,180,668.11; sub-cent rounding only).
- **UPS = no native-USD lines** — only 55 EUR lines ≈ €136.81, charge_amount_local NULL. Matches prior flag. Non-USD sweep across ALL carriers confirms UPS/EUR/55 is the ONLY non-USD origin spend in window — nothing else dropped silently.
- **May soft floor:** 95.1% invoiced, late-May still backfilling — load-bearing for month-by-month read; May figures will tick up.

---

## Re-pull (2026-06-16, sid8 44773956) — CORRECTED SCOPE, SCM-faithful reproduce
**Ask:** re-pull for LucaNet-vs-BI US with corrected canonical US filter; reproduce live SCM dashboard exactly. Confirmations + tables A/B/C/D monthly Jan–May + YTD + exact SQL for A.

**Corrected scope (canonical US entity filter — supersedes prior 2-site/dest-only reading):**
- Sites: `production_site IN ('PCS MI','PCS PX','PCS CMH')` — adds Mexicali (PCS MI) to the prior Phoenix+Columbus. PCS PL (Poland) + PCS CGN (Cologne) correctly excluded.
- Destinations: **`destination_country_code IN ('US','CA')`** — NOT `destination_country`. CONFIRMED: `destination_country` holds full NAMES ('United States','Canada','United States of America'); brief's literal `destination_country IN ('US','CA')` returns ZERO rows. Codes live in `destination_country_code`.
- Period: `shop_order_created_date` 2026-01-01..2026-05-31 (order-month, SCM lens) for A/B1/C/D; `il.shipment_date` same window for B2.

**Confirmations:**
1. PCS MI = valid, non-trivial: 931,908 rows / €11.69M final cost (all-time, all-dest). It's Mexicali. (PCS PX 795,834; PCS CMH 412,958.)
2. Destination column = `destination_country_code`, value form = ISO codes 'US'/'CA'. (Names in `destination_country`.)
3. SCM quota def CONFIRMED exactly: num = SUM(final_shipping_cost_eur) (final=COALESCE(real,expected,avg), all buckets), denom = SUM(net_revenue_eur), grouped by order-month (shop_order_created_date). Matches mart-contract § Cost columns formula.

**A — SCM-faithful quota (order-month):**
| Month | Final cost EUR | Net revenue EUR | Quota |
|---|--:|--:|--:|
| Jan | 594,270.77 | 2,343,939.25 | 25.4% |
| Feb | 456,836.70 | 1,864,013.84 | 24.5% |
| Mar | 477,689.31 | 1,830,419.62 | 26.1% |
| Apr | 598,229.67 | 2,115,675.05 | 28.3% |
| May | 582,584.12 | 2,140,904.46 | 27.2% |
| **YTD** | **2,709,610.57** | **10,294,952.22** | **26.3%** |

**B1 — final_shipping_cost_eur by carrier × order-month (SCM-consistent):**
| Carrier | Jan | Feb | Mar | Apr | May | Total |
|---|--:|--:|--:|--:|--:|--:|
| ONTRAC | 282,211.71 | 213,024.94 | 199,370.55 | 240,662.88 | 273,326.39 | 1,208,596.47 |
| USPS | 137,086.85 | 110,127.11 | 92,107.03 | 132,670.57 | 122,821.96 | 594,813.52 |
| FEDEX | 84,726.29 | 78,649.01 | 116,221.99 | 145,733.17 | 122,667.16 | 547,997.62 |
| ASENDIA USA | 90,168.59 | 55,035.65 | 69,968.91 | 79,163.05 | 63,743.18 | 358,079.38 |
| UPS | 77.33 | 0 | 20.82 | 0 | 25.44 | 123.59 |
| **TOTAL** | | | | | | **2,709,610.57** |
(9 uncosted rows w/ NULL final — contribute €0.)

**B2 — invoiced freight native USD by carrier × shipment-month (charge_amount_local, currency='USD', excl tax/customs):**
| Carrier | Jan | Feb | Mar | Apr | May | Total |
|---|--:|--:|--:|--:|--:|--:|
| ONTRAC | 331,419.07 | 299,205.60 | 227,144.39 | 239,410.83 | 336,882.37 | 1,434,062.26 |
| USPS | 160,395.05 | 134,055.54 | 99,678.45 | 147,109.98 | 141,915.64 | 683,154.66 |
| FEDEX | 96,584.37 | 99,315.00 | 106,888.05 | 191,911.67 | 131,765.19 | 626,464.28 |
| ASENDIA USA | 112,395.46 | 77,972.23 | 71,328.14 | 80,598.63 | 93,516.98 | 435,811.44 |
| **TOTAL** | | | | | | **3,179,492.64** |
(UPS = no USD lines, EUR-only ~€136.81. B2 totals differ slightly from prior follow-up: prior was 2-site dest-US origin; this is corrected 3-site US+CA.)

**C — Revenue (order-month):** as in A net_revenue_eur column; YTD €10,294,952.22. Native-USD revenue: NONE — `net_revenue_eur` is the only revenue column; revenue is EUR-only in the mart. Stated as such.

**D — % invoiced (euro-weighted, order-month):** Jan 99.0% / Feb 98.5% / Mar 98.3% / Apr 98.7% / May 95.1% / YTD 97.9%. All ≥95% — May passes the floor (barely; still backfilling, will tick up).

**Checks:**
- B1 carrier-sum = €2,709,610.5729 = A YTD final cost to the cent. Reconciled.
- B1 month-sums tie to A monthly final cost each month. Two-axis reconcile.
- Scope: 267,539 shipments; 9 NULL-final (uncosted). cost_source dominated by 'invoice'.
- Currency sweep: USD 721,840 lines vs 55 EUR — UPS/EUR the only non-USD; nothing dropped silently.
- Quota direction sane: rises Jan→Apr (25→28%), eases May; consistent with cost/rev movement.

**Open:** none material — corrected scope is now canonical. Prior sections use the older 2-site/dest-US reading; this section supersedes for the US-entity definition.

# S_shipagent — May 2026 UPS cost, TCG-only (exclude ORWO/Wolfen)

Player: Jebrim | Actor: shipping-agent (emulation) | Date: 2026-06-17
Parent: S_shipagent_may2026-ups-cost-shipmentdate-coverage (whole-company €503,910 / 72,707)
Tier: gold-contract

## Ask
Re-cut the prior whole-company May 2026 UPS closing pull to TCG entity only (exclude
ORWO/Wolfen photo lab). Same basis: invoiced freight only, all freight buckets, exclude
tax + customs/duties, shipment_date basis. Filter at source on the entity field — not by
subtracting €79,858. Report EUR total, count, bucket split, per-parcel; reconcile
TCG + ORWO back to €503,910; restate coverage/lag for the TCG slice.

## Mart contract used
- Cost basis: invoiced freight only. Source = `fact_shipment_invoice_lines` (line-level,
  carries the ORWO bulk-bill allocation + the line-level `shipment_date` the prior pull used).
- Freight = all charge_bucket EXCEPT 'tax','customs_duties' (rule 13).
- Date basis: invoice-line `shipment_date` (May 2026). This is the basis that reproduces
  the prior 72,707 — NOT fact_shipments.received_by_carrier_date.

## Entity-distinguishing field — KEY FINDING
- **`source_system` on fact_shipments is the entity field.** TCG = Picturator + PicaAPI;
  ORWO/Wolfen = source_system='ORWO'. (rule 12)
- `invoice_source` ('ups' vs 'ups_orwo') is NOT a clean entity split — it's invoice
  provenance, not entity. The 'ups' source carries €11,011 of ORWO shipments; the
  'ups_orwo' bulk-bill source carries €51,358 of TCG (Picturator) shipments. Filtering on
  invoice_source would mis-scope. Must filter on source_system, span BOTH invoice sources.

## Turn log
- Reproduced whole-company from invoice lines: ups €424,051.87/50,024 + ups_orwo
  €79,858.34/22,683 = €503,910.21 / 72,707. Exact tie to prior + brief's €79,858. OK.
- Split by source_system across both ups sources → TCG €463,221.48/54,499;
  ORWO €34,312.68/18,195; PCS €76.74/13; unattributed (shipment_id NULL) €6,299.31/0.
- Reconciliation: 463,221.48 + 34,312.68 + 76.74 + 6,299.31 = €503,910.21. Ties exact.
  Counts: 54,499 + 18,195 + 13 = 72,707. Ties exact.
- TCG bucket split: base 301,409.86 | fuel 73,463.09 | oversize/handling 72,700.23 |
  residential 10,237.49 | other 5,268.54 | remote 142.27 | unclassified 0 = 463,221.48 (ties).
- TCG per-parcel: 463,221.48 / 54,499 = €8.50.
- Coverage: TCG UPS May, by ship week, all weeks 99.6-99.7% invoiced incl. last week
  (May 25-29 by day 99.3-99.8%). As of 2026-06-17 (~18d past month-end) May is fully aged.
  Lag picture does NOT differ materially vs whole-company. Firm-today ≈ fully-aged.

## Headline result
- TCG-only May 2026 UPS invoiced freight: **€463,221 / 54,499 shipments / €8.50 per parcel.**
- ORWO/Wolfen: €34,313 / 18,195. PCS (internal print, neither): €77.
  Unattributed invoice lines (no shipment): €6,299.
- Movers in the per-parcel: base €5.53, fuel €1.35, oversize/handling €1.33.

## Caveats / notes for principal
- The €79,858 "ORWO portion" in the brief = the `ups_orwo` *invoice source*, not the ORWO
  *entity*. The actual ORWO entity freight is €34,313. The €79,858 bulk-bill source is mostly
  TCG (Picturator) parcels tied into the Wolfen bulk bill. Subtracting €79,858 from €503,910
  would have UNDER-counted TCG by ~€51K. Filtering at source on source_system is why the brief
  insisted on it — confirmed it matters here.
- PCS (€77, 13 parcels) and €6,299 unattributed lines sit in the whole-company total but are
  neither TCG nor ORWO; both are tiny.

## Deliverable
- Chat-only (numbers fit chat). No file outside the brain requested.

---

## FOLLOW-UP (2026-06-17, same actor): literal SQL + €463k→€434k reconciliation

### Ask
1. Output the literal runnable SQL that produced TCG €463,221.48 / 54,499.
2. Reconcile vs the principal's invoices-report figure ~€434k (~€29K gap). Test
   candidates in order: (a) direct-stream-only, (b) invoice_date basis, (c) charge-bucket
   scope, (d) other scope filter.

### Deliverable 1 — literal SQL (reproduced exact: €463,221.48 / 54,499)
```sql
SELECT
    ROUND(SUM(il.charge_amount_eur), 2) AS freight_eur,
    COUNT(DISTINCT il.shipment_id)      AS shipments
FROM shipping_mart.fact_shipment_invoice_lines il
JOIN shipping_mart.fact_shipments fs
    ON fs.shipment_id = il.shipment_id
WHERE LOWER(il.invoice_source) LIKE 'ups%'          -- spans both 'ups' + 'ups_orwo'
  AND il.shipment_date >= DATE '2026-05-01'         -- shipment-date basis (line-level)
  AND il.shipment_date <  DATE '2026-06-01'
  AND il.charge_bucket NOT IN ('tax', 'customs_duties')  -- freight only (rule 13)
  AND fs.source_system IN ('Picturator', 'PicaAPI');     -- TCG entity (rule 12)
```

### Deliverable 2 — reconciliation map vs ~€434k (all shipment_date, freight buckets)
| Cut | EUR | shipments | Δ vs €434k |
|---|---|---|---|
| TCG all-streams (the headline) | 463,221.48 | 54,499 | +29,221 |
| **(a) TCG direct-stream only ('ups')** | **411,863.12** | **47,535** | **−22,137** |
| (a) TCG bulk-bill only ('ups_orwo') | 51,358.36 | 6,964 | — (ties: 411,863+51,358=463,221) |
| (a) whole-company direct ('ups') | 424,051.87 | 50,024 | −9,948 |
| (a) direct minus direct-Wolfen (excl ORWO entity) | 413,040.39 | 47,548 | −20,960 |
| (b) TCG invoice_date basis (all streams) | 364,888.91 | 54,819 | −69,111 |

- Direct-stream entity decomp: Picturator 354,788.54 + PicaAPI 57,074.58 = TCG 411,863.12;
  + ORWO 11,011.48 + unmapped 1,100.53 + PCS 76.74 = whole-co direct 424,051.87 (ties).
- (c) bucket scope: TCG buckets = base 301,409.86 | fuel 73,463.09 | oversize 72,700.23 |
  residential 10,237.49 | other 5,268.54 | remote 142.27. No single bucket-drop hits €434k;
  including tax moves UP to ~€468.9k (wrong direction). (c) rejected.
- (b) invoice_date basis rejected — €364.9k, way below.

### Verdict
- Dominant structural explanation = (a): the report **excludes the Wolfen bulk-bill stream**
  (~€51K of TCG parcels riding 'ups_orwo'). TCG direct-only = €411,863.12.
- Closest single clean number to ~€434k = **whole-company direct stream €424,051.87** (−€10K).
  The ~€434k sits between TCG-direct (€411.9k) and whole-co-direct (€424.1k); residual
  ~€10–22K is an entity-boundary difference (report may include the small ORWO-on-direct +
  unmapped-direct lines the strict TCG filter drops). No cut hits €434k exactly — expected
  for an eyeballed report figure.
- Need from principal to close fully: does the report scope to TCG entity or whole-company,
  and does it use 'ups'-only? That picks between €411.9k and €424.1k.

### Deliverable home
- Chat-only. No file outside the brain (principal will re-run the SQL).

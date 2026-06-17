# S251 — UPS May 2026 accounting close: mart vs silver cost-completeness

**Player:** Jebrim · **sid8:** d8d2c1be · **date:** 2026-06-17
**Mode:** investigation (read-only on data; bi-etl repo read; no bi-analytics writes)

## Ask

Principal is reconciling accounting's May 2026 shipping-cost closing figures, shipment_date basis, invoiced. Started at "how much UPS for May + is it covered," drilled into why three different UPS-May figures disagreed (€463k / €434k / mart), then into *what each layer filters out*, ending with a review of an ETL ticket the principal wrote.

## What happened (turn arc)

1. **May UPS, shipment_date, all-in (both streams, freight only):** €503,910 / 72,707 shipments (whole-company). Coverage: UPS bills fast (~94% by 21 days); as of 2026-06-17 May is firm — only a thin late-May tail (~€15–25k modelled) was open at the *first* pull, now landed.
2. **TCG only (exclude ORWO/Wolfen):** €463,221 / 54,499. Key trap caught by the shipping-agent: the Wolfen *bulk-bill invoice stream* (€79,858) ≠ the Wolfen *entity*. ~€51k of that stream is TCG (Picturator) parcels. Entity filter = `source_system IN ('Picturator','PicaAPI')`; the bulk-bill is `invoice_source` provenance, not entity. Subtracting €79,858 would undercount TCG by ~€51k.
3. **Why the principal's invoices report shows ~€434k:** it books the **UPS direct invoice stream only** (drops the Wolfen bulk-bill TCG allocation). Direct-stream TCG = €411,863; whole-co direct = €424,052.
4. **The €434k traced to source** — it's `SUM(netamounteur)` over `enterprise_silver.ups_invoices` on `transactiondate`, **all charge types, all accounts, no filter** = €434,551 / 156,795 lines. The gross direct-billed total (incl returns, adjustments, tax/gov/brokerage).
5. **What each layer filters** (the core finding — see bank draft):
   - **Silver build** (`shipping_invoice_cost/SFTP/UPS/sql/insert_to_silver.sql`): drops a hardcoded 22-invoice blacklist (all pre-2026, no May impact); rescales 17 Swiss invoices ×0.072789 (all pre-2025, no May impact); incremental dedup. No charge-type filtering — silver = whole invoice.
   - **Gold build** (`shipping_mart/fact_shipment_invoice_lines/sql/providers/ups.sql`): drops no-tracking lines (€4,800/mo, **unrecoverable**), RTS return lines (removed; cost redistributed onto original parcels via `shipmentreferencenumber1`, **90-day cap drops late returns**), pre-2024, null amount. Tax/customs are NOT dropped — they're `tax`/`customs_duties` buckets, excluded only at query time by the freight cost basis.
6. **RTS detail:** return tracking is mixed — surcharge re-bills carry the original tracking; "Undeliverable Return" lines carry a new return tracking with `leadshipmentnumber` back-ref. Redistribution matches on order ref, not tracking. Redistribution **is already baked into** `charge_amount_eur` (`+ rr.per_line_addition`); for May direct, €7,600 of the €12,060 RTS made it back, ~€4,460 lost to the 90-day cap / unmatched originals.
7. **Reconciliation (May, direct UPS):** silver whole invoice €434,551 − RTS €12,060 − no-tracking €4,800 + returns-redistributed €7,600 = **mart €425,291** (all buckets). Net structural loss vs whole invoice = €9,260 (≈2.1%) = €4,800 no-tracking + €4,460 returns not recovered.
8. **ETL ticket review:** principal wrote a ticket — make `fact_shipment_invoice_lines` accounting-complete (carry filters/transforms to *after* invoice_lines, i.e. into cost_summary). Verdict: architecture instinct correct. Tightenings given: (a) it's an *alteration* too (redistribution inflates surviving lines — store raw per-line amount); (b) pin the reconciliation baseline (bronze vs silver — silver itself transforms via blacklist+CH fix, upstream of invoice_lines); (c) scope the audit to ALL 23 carrier provider loaders, not just UPS; + cost_summary needs an unmapped-cost rule (NULL shipment_id rows). Gave a concrete acceptance test: invoice_lines per-carrier total == raw, delta=0 (UPS today €425,291 vs €434,551, €9,260 short). Principal: "they will get it."

## Decisions

- TCG = `source_system IN ('Picturator','PicaAPI')`; ORWO/Wolfen entity = €34,313 (NOT the €79,858 bulk-bill stream).
- For accounting / whole-invoice totals: reconcile off `enterprise_silver.<carrier>_invoices`, NOT the mart. The mart is allocation-shaped (tracked, non-RTS, mappable subset).

## Pending external actions

None pending. ETL ticket is the principal's to file; no action owned by me. No bi-analytics writes. No commits outside the brain.

## Sub-agent traces (this session)

- `S251_d8d2c1be_shipagent_may-ups-cost-coverage.md` — pull #1 (whole-co + coverage).
- `S251_d8d2c1be_shipagent_may-ups-tcg-only.md` — pull #2 + #3 (TCG-only entity filter + €434k reconcile + literal SQL).

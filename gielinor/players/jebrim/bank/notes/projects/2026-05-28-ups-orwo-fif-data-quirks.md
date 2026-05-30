# UPS ORWO bronze — FIF report data quirks

Source: `bi-analytics-main/NFE/shipping_topics/42_fif_orwo_ups_invoice_file` (standalone pipeline) + the bi-etl DAG `dags/shipping_invoice_cost/fif_ups_orwo_monthly`. Table: `enterprise_bronze.ups_orwo`. Anchor: [[S116_7f67fe48_shipping-agent-fif-monthly-skill|S116]].

**`invoicedate` is stored inconsistently.** Mostly ISO `YYYY-MM-DD`, but some rows are US `M/D/YYYY` — the off-cycle `838xxx` March invoices that came through a different ingestion path. String ops (`LIKE '2026-03%'`, `LEFT(...,7)`) mis-bucket / undercount these (March read 11 vs the true **20** invoices). **Always `invoicedate::date`** for bucketing/filtering/max. `::date` parses both. Real upstream DQ issue worth fixing at source.

**VAT is a separate row, not a column.** Bronze carries VAT as a `chargedescription = '19.000 % Tax'` row whose `net_amount` holds the VAT euros, keyed by `trackingnumber`. The FIF fold computes per-charge-row VAT = net × 0.19 for any tracking that has a tax row, then drops the tax rows.

**A shipment's charges and its VAT row can split across two invoices.** UPS bills freight on the weekly `327xxx` invoice but customs/VAT recharges on a separate `838xxx` invoice — same `trackingnumber`, two invoices (**515** such trackings in April 2026). Consequence: **per-invoice VAT folding ≠ whole-month VAT** (April per-invoice sum was €58.45 / 0.4% under). Whole-month fold is exact; the per-invoice FIF files (option A, isolation) intentionally accept this small delta.

**Live distribution (2026-05-28):** Jan 5 / Feb 8 / Mar 20 / Apr 26 / May 16 invoices. April reconciles to net €104,312.29 / VAT €13,889.34 / gross €118,201.63 (the validated reference). Off-cycle `838xxx` customs invoices not in our DB remain accounting's manual merge.

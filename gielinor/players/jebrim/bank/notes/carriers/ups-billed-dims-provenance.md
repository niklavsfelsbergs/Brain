# UPS billed (dimensioner) dims — where they live and how to read them

**Harvested:** 2026-06-26 ([[S371_65d03a35_ups-lps-billed-dims-threshold-dispute|S371]]). **Domain:** [[carrier-contracts]] (dimension coverage).

When a question needs UPS's **own billed / dimensioner-measured** dims (not our declared geometry) — LPS/over-max threshold disputes, re-measure audits — the only layer that retains them is **`enterprise_bronze.csv_ups_zip_invoicedata`** (tcg_nfe overlay grants the read; creds `bi-analytics-main/NFE/.env`).

- The **gold mart cannot answer it**: `shipping_mart.fact_shipment_invoice_lines` has no dims; `fact_shipments.length_plus_girth_cm` is **our declared** geometry. `enterprise_silver.ups_invoices` (the S199 incidence source) also has **no dims**. This is a legitimate, documented departure from mart-first.
- Dim fields on the bronze row: `packagedimensions` = UPS dimensioner output (= **billed** dims), "L x W x H" cm, uom `'C'`; `rawdimensionlength` agrees to a decimal; `detailkeyeddim` = **our keyed/declared** dims (do not use as "billed"); `detailkeyedbilleddimension` is **empty** in the feed despite its name.
- **Grain trap:** the surcharge € and the measured dims sit on **separate rows of the same `trackingnumber`** — the €101.80 LPS charge row has empty dims; a companion `net=0` LPS row carries the dimensioner reading. Aggregate to trackingnumber (one dim set per package).
- **Charge identity:** LPS family = `chargedescriptioncode IN ('LPS','SLP')` (*Zuschlag für große Pakete* + demand variant); over-max = OVR/SOV/OML; AHS is separate. Net = applied(+) + reversals(−); "standing" charge = per-tracking net > 0.
- **L+G** = longest side + 2×(sum of the other two).
- **Coverage / freshness:** bronze is a partial recent window (as of 2026-06-26: ~2026 H1, txn 2025-12-31→2026-06-12), NOT the 12-mo S199 window. Dim coverage is high on mature months (~95% Q1) and collapses on immature recent invoices (dim detail rows lag) — treat no-dim on recent invoices as a feed-maturity artifact, not a substantiation finding.

Anchor: [[S371_65d03a35_ups-lps-billed-dims-threshold-dispute|S371]] LPS threshold-dispute (`1_offers/picanova/UPS/lps_threshold_dispute_findings.md`, `calculation/extract_lps_dispute.py`).

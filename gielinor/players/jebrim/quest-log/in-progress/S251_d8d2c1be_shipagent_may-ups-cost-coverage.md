# S_shipagent — May 2026 UPS cost (shipment_date lens) + invoice-coverage read

**Spawned:** shipping-agent sub-agent, emulated. Principal: Jebrim.
**Brief:** Accounting May-2026 shipping-cost closing reconcile. Lens = shipment_date, invoiced cost. (1) Total UPS cost May 2026 by shipment_date + count + basis. (2) Coverage/completeness — has all UPS invoicing for May arrived, or is there a lag tail.
**Tier:** gold-contract. (CLAUDE.local.md present granting upstream, but stayed entirely on shipping_mart.* — no upstream needed.)
**Date of run:** 2026-06-17.

## Cost basis applied (UPS, per mart contract)
- Carrier = UPS → invoice sources `ups` + `ups_orwo` (rule 14: ups_orwo is the bulk-bill allocation to tied Wolfen shipments; both belong in total UPS).
- Invoiced cost only. Freight = all charge buckets EXCEPT `tax` and `customs_duties` (rule 13). UPS Manual Bill / 838-prefix customs already routes into excluded buckets — not re-added.
- shipment_date lens: used `fact_shipment_invoice_lines.shipment_date` (carrier-reported per line). NOTE: fact_shipments has no shipment_date column; received_by_carrier_date only ~58% populated on UPS, so the invoice-line shipment_date is the correct/clean basis. Built both deliverables off the invoice lines.

## Status log
- Probed recency: max invoice_date 2026-06-11, max invoice_loaded_at 2026-06-14, mart dw_timestamp 2026-06-16. Data current.
- D1 May UPS freight: 245,845 charge lines, 72,707 distinct shipments. Freight €503,910 (excl tax €10,654 + customs €3,172). Bucket split: base €330,927 / fuel €79,880 / oversize €73,006 / residential €10,617 / other €9,300 / remote €180. Per-parcel €6.93 (sane vs contract ~€6.95 Apr-TCG ref).
- ups vs ups_orwo: ups €424,052 (50,024 shp) + ups_orwo €79,858 (22,683 shp). ups_orwo ~16% — material, correctly included.
- D2 lag: avg invoice lag 4-6 days (Feb-Apr), max tail 55-115d. Using invoice_loaded_at vs shipment_date on April (comparable aged month): ≤7d 19%, ≤14d 71%, ≤17d 88%, ≤21d 94%, ≤30d ~100% (≤30d overshoots final total → late credit/adjustment lines net it back down).
- May elapsed as of 06-17: May1=47d, May17=31d, May31=17d. Weeks through May23 (>=25d aged) at/above 94% complete. Only last week May25-30 (18d, €99.9K, 12.8K shp) below the line (~88-90%). Estimated remaining tail ≈ €15-25K (~3-5% on top of €503.9K), mostly late-May + a thin residual from May18-23 week.

## Checks done
- Bucket split first (rule 4/11). Reconciles: 11 included buckets only, tax/customs isolated.
- ups_orwo inclusion verified material.
- Lag floor: min lag 0, no negative lags; ≤Nd overshoot of total traced to late credit lines (not a data error).
- Per-parcel sanity vs contract reference: consistent.

## Coverage DQ caveats
- UPS is well-wired (ups + ups_orwo). The four structural coverage holes in the contract (ORWO POST, Picturator POST_DVF, MAERSK, ASENDIA) are NOT UPS — don't touch this pull.
- ~5% mart-wide uncosted (cost_source NULL) + untracked rows ('', 'untracked') can't be invoiced — but that's at fact_shipments grain; this pull is invoice-line grain so those rows simply don't appear (they have no UPS invoice lines).

## Open / principal
- shipment_date basis: used invoice-line shipment_date (the only clean shipped-date for UPS). If accounting's closing definition of "shipment date" is the fact_shipments shipped-date, that column is only 58% populated for UPS — flag.
- Tail estimate (€15-25K) is modelled off April's lag curve, not yet-arrived fact. Re-pull in ~2 weeks for the locked May figure.

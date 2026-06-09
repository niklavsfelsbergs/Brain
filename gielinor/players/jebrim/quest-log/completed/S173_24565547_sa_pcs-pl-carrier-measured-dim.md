# [[S172_df374cef_dhl-truck-cost-warenpost-kleinpaket|S172]] — PCS PL carriers + which give independent dim measurement

Shipping-agent sub-agent pull for Jebrim. Scoped to PCS PL (Poland) production site.
Question: which carriers at PCS PL, and which of those give a GENUINE independent dimension measurement (vs echoing our declared dims)?

## Scope used (auditable)
- Site column: `shipping_mart.fact_shipments.production_site`
- PCS PL value: `'PCS PL'` (11,508,497 shipments all-time). Distinct from a tiny `'PL'` value (27,431) — not the same site; used PCS PL only.
- Tier: gold contract (`shipping_mart` only). Full-access tier available but not needed.

## Turn log
- Confirmed `production_site` is the origin field; `'PCS PL'` = the Poland site (also PCS MI/PX/CGN/CMH siblings).
- Carrier mix pulled all-time + trailing-12m (shop_order_created_date >= 2025-06-09). DHL 35.4% / UPS 18.2% lead; Yodel 10.8%.
- Intersected with the established measured-dim list (OnTrac/FedEx/Asendia USA/Yodel full; USPS/UPS subset — NOT re-derived).
- Key finding: of the measured-dim carriers, only YODEL (1.24M) and UPS (2.09M) have material PCS-PL volume. OnTrac (14), FedEx (9), Asendia USA (234), USPS (4) are noise at PCS PL — all US-origin, expected.
- DQ flag: gold `length/width/height_cm` are OUR declared dims (near-100% populated for both UPS+Yodel) — these are the passthrough source, NOT the independent measurement. The measured-vs-passthrough verdict is upstream-derived and not reconstructable from the 4 gold facts (invoice-lines carries billed_weight, no carrier dims). So I did not re-derive; I intersected.
- DQ flag: carrier label `ASENDIA` (215k at PCS-PL, EU line) is distinct from `ASENDIA USA` (234, the US-measured one in the verdict list). Don't conflate.

## Answer (headline)
At PCS PL the independent-measurement carriers are YODEL (full coverage, 1.24M, the only at-scale one) and UPS (subset only — freight/oversize, per upstream verdict). All other measured-dim carriers (OnTrac/FedEx/Asendia USA/USPS) are present only at trivial volume. Yodel is the only FULL-coverage independent measurement at PCS PL.

## Deliverable
Chat-only (lookup). No file outside brain.

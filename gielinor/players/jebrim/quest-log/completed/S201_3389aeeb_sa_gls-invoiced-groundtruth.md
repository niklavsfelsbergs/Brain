# Shipping-agent pull: GLS old-contract invoiced ground truth (for old-vs-new offer compare)

- Date: 2026-06-11. Sub-agent trace for parent quest S201_3389aeeb_gls-old-vs-new-offer.
- Asked: (1) GLS invoiced volume/cost by month 2024-01→end, date the volume end; (2) charge-bucket decomposition + total/base ratio DE vs non-DE for last 6 material months; (3) destination mix; (4) DQ caveats. Validate modelled surcharge stack (base + ~22.5% energy + 1% klima + 5.7% intl toll / €0.38 national toll ≈ ×1.29 EU lanes).
- Scope used: TCG = source_system IN ('Picturator','PicaAPI'); shipping_provider_group='GLS' (extkeys GLS11BUSINESS, GLS11EUROBUSINESS + 6 stray 'GLS' rows 2023). No ORWO GLS volume exists; PCS GLS (~3k parcels) excluded. Month anchor = shop_order_created_date. Cost basis invoiced-only (cost_source='invoice', buckets from fact_shipment_cost_summary).

## Status lines
- Entity check done — GLS = one group, two service extkeys, zero ORWO volume.
- Monthly series 2024-01→2025-09 pulled; last material invoiced month 2025-07 (~21.7k invoiced); Aug-25 wind-down (7.2k invoiced); Sep-25 1.2k parcels, 0 invoiced; last physical carrier scan 2025-10-01.
- Bucket split done (window 2025-02→2025-07, 154,751 invoiced parcels, €703,187): non-DE total/base = 1.314; DE = 1.451. Bucket totals tie monthly series exactly.
- Invoice-line drill: surcharge stack sits in a single ~once-per-parcel "Unclassified" line — non-DE unclassified/base = 28.8% vs modelled 29.2% (energy 22.5 + klima 1 + intl toll 5.7) → validated. DE: separate "Toll Domestic Traffic" line = €0.38/parcel exactly (€1,736/4,569 lines) → national-toll flat validated; DE unclassified/base 24.4% window-avg vs modelled 23.5% (Feb clean at 24.0%; later DE months noisy 37–65% on ~700-1k parcels/mo, returns + small-volume).
- Destination mix: NL 72.5k + AT 55.2k = 83% of window; DE only 3%.

## Headline result
- Old GLS relationship: mostly EU export lanes (NL/AT/BE), landed/base ≈ 1.31 non-DE — modelled ×1.29 stack confirmed within ~0.5pp on the pure surcharge ratio (1.288 excl. oversize/returns).
- Caveats: invoiced-only basis; Jan-25 only 79% invoiced; Aug-25 78%, Sep-25 0% (tail never invoice-matched — cost ground truth ends mid-Aug-25); ES/IE weight missing.

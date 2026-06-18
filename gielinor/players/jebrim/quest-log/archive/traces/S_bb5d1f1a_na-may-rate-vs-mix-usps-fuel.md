# NA May-2026 follow-up: USPS rate-vs-mix + per-carrier fuel YoY

Shipping-agent emulation pull. Topic: `bi-analytics-main/NFE/shipping_topics/46_na_market_quota_may_2026/`.
Scope: TCG (B2C+MerchOne), NA = US+CA, ship-month = received_by_carrier_date, final cost = invoiced+expected. Gold contract only.

## Status
- Tie-out: May-26 NA = 57,159 parcels / €590,132.8 / €10.32 pp (received_by_carrier basis). Prior pull said 57.9k/€599.3k/€10.35 — ~1.2% lower now, mart-refresh drift. Flagged.
- Q1 USPS rise: bucket split shows USPS billed as ONE all-in base_rate bucket (no separate fuel/oversize line). Avg billed weight flat ~1.0-1.04kg. Shift-share Jan->May of +€1.047 pp = +€1.107 RATE / -€0.060 MIX. ~100% rate, ~0% mix. Apr->May +€0.686 = +€0.623 rate (91%) / +€0.063 mix (9%). Within every weight band rate rose Jan->May (+8.7% lightest band to +54% heaviest).
- SERVICE MIX NOT AVAILABLE: shippingprovider_extkey carries only 'USPS' for all USPS NA parcels - mart does not separate Ground Advantage / Priority / Parcel Select. Flagged as gold-contract gap.
- Q2 fuel per carrier YoY (carrier-held-constant): FedEx fuel/parcel €1.30->€2.48 (+91%), Asendia USA €0.82->€2.87 (+250%). Both confirmed genuine fuel-rate moves via fuel-as-%-of-base (FedEx 7.5%->13.8% on LIGHTER weight; Asendia 5.6%->16.4%). NA-aggregate "flat" (€1.19->€1.14) was OnTrac-new-volume mix contamination. USPS no fuel line, DHL fuel negligible, OnTrac/UPS/USPS not in NA May-25 for YoY.

## Checks
- Tie-out reconciled across 3 ship-month anchors (received/order-created/produced) - all ~€10.3-10.4 pp, none hit €599.3k exactly => prior-pull drift, not a basis error.
- Rate-vs-mix done via formal shift-share (Jan-mix-held rate effect + May-rate-held mix effect), sums to total delta.
- FedEx/Asendia fuel rise cleared of weight-artifact via fuel/base ratio on flat-or-lighter weight.

## Open
- Service-level (Ground Advantage vs Priority) not on gold contract for USPS - principal may want upstream/invoice-line check if service split matters.
- Tie-out drift vs prior pull worth a one-line note when stakeholder reconciles against the quota denominator.

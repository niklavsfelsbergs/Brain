# Invoice (measured) vs mart (declared) package-dimension accuracy

**As-of:** 2026-06-09. **Player:** Jebrim (shipping-agent emulation, spawned by Jebrim).
**Tier:** UPSTREAM / off the gold contract on the carrier side (`enterprise_silver/bronze`,
`tcg_nfe` role); mart side gold. Read-only throughout.
**Ask:** How accurate is each carrier's invoiced package dims vs our declared (mart) dims,
grouped by OUR `packagetype`? Scope: 3 Status-A carriers (Maersk, FedEx, OnTrac).

## Turn log

- Read coverage note + prior art (topics 36 package_measurements, 12 ontrac). Confirmed
  mart dim fields on `fact_shipments`; `packagetype_group` 0% populated mart-wide (DQ flag).
- Stage 1 join feasibility: OnTrac `trackingnumber` 99.998%. Maersk house ref (`1MX...`)
  ~0% -> recovered via `last_mile_provider_tracking_number` 100%. FedEx
  `express_or_ground_tracking_id` 737,787 matched (mart-window subset of 1.7M).
- Stage 2 units: Maersk already CM. OnTrac inches x2.54; CAUGHT `length_in`=our declared
  (passthrough, 0.09cm), `billed_*_in`=carrier-measured (3.74cm) -> use billed. FedEx
  `dim_unit`/`dim_divisor` SWAPPED in some batches; alphabetic=unit (I/C), numeric=divisor.
- Stage 3: sorted-axis deltas (axis labels don't align). Maersk = exact passthrough,
  87,046/87,046 L=L,W=W,H=H -> DROPPED (not a measurement). OnTrac faithful (~85% within
  2cm overall, most box types 90-99%). FedEx real but ~half the within-2cm rate.
- Our-side DQ: named-size boxes with declared longest-axis 0.1cm->1000cm (GEL, pizza
  48x36) -> garbage declared values to clean before trusting tail deltas.

## Deliverable
- `bi-analytics-main/NFE/shipping_topics/45_invoice_vs_mart_dimension_accuracy/`
  (CLAUDE.md + sql/{join_feasibility,unit_alignment,accuracy_ontrac,accuracy_fedex,
  maersk_passthrough_check,our_declared_dim_dq}.sql). findings returned in-session
  (harness blocked a `findings.md` write from the sub-agent).

## Headline
OnTrac measures most faithfully; FedEx real but noisy; Maersk is a declared-dims
passthrough (recategorise in the coverage map). No systematic per-carrier bias — signal
is per-packagetype. Our own declared dims partly garbage on fixed-size boxes.

---

## Pass 2 (2026-06-09) — passthrough-vs-measurement discriminator, 6 more carriers

Spawned by Jebrim. Same discriminator (exact-equality + delta scatter, sorted axes); verdict
each candidate dim as REAL MEASUREMENT / PASSTHROUGH / INCONCLUSIVE. Ground truth carried in:
OnTrac=REAL, FedEx=REAL, Maersk=PASSTHROUGH (verbatim).

- Asendia USA: join `trackingnumber` 99.9%. L/W/H in inches. 14.3% exact, MAE 11cm, 29% w/±2cm -> **REAL**.
- USPS: join `pic` (impb=0). dual-field — `manifest_*` 100% exact = **PASSTHROUGH**; `ca_assessed_*`
  79.6% exact w/ real 20% tail (MAE 3.2cm) on ~13.8k subset -> **REAL (assessed only)**.
- DB Schenker: join `sender_number`(strip #)->`shop_ordernumber` 96.4% (stt + mart tn both placeholders).
  `cbm` m3 volume-only. Means identical (339L), 84% w/2%, 23% exact (m3 rounding) -> **INCONCLUSIVE/lean passthrough**.
- Direct Link: join `trackingnumber` ~100%. `volume` scalar, undetermined unit, 0% row-match -> **INCONCLUSIVE**.
- Yodel: join `'J'||tracking_number` 99.99% (raw=0; mart prepends J). dual-field — `declared_*` ~0.4% pop
  (passthrough half, ~empty); `actual_*` mm, 3.0% exact, MAE 6.5cm, mean +2.3cm -> **REAL**.
- UPS: join `trackingnumber` 89.7%. `packagedimensions` cm (operative), 0.2% exact, mean +16.1cm,
  MAE 17.8cm on ~3.1k freight/oversize subset -> **REAL**. `detailkeyeddim`(in)=declared passthrough;
  `detailkeyedbilleddimension` dead (1 row). DPD DE/Ambro/Hermes (stale) not tested.

### Checks
- Cleaned declared garbage (2..300cm / volume floors) on the mart side before delta stats.
- Dual-field trap caught on USPS + UPS + Yodel (in addition to known OnTrac) — tested every dim col per carrier.
- Cross-checked the passthrough signature (means-identical + verbatim) holds for USPS-manifest the same
  way it did for Maersk (MAE 0.00). Volume-only carriers flagged as unverifiable from a scalar, not forced.

### Pass-2 deliverable
`shipping_topics/45_.../sql/discriminator_{asendia,usps,db_schenker,direct_link,yodel,ups}.sql`
+ CLAUDE.md verdict table appended.

### Bottom line (genuine independent measurement we don't already hold)
OnTrac, FedEx, Asendia USA, Yodel (full on dim-populated subset); USPS (assessed ~13.8k subset only);
UPS (freight/oversize ~3.1k subset only). NOT Maersk. DB Schenker / Direct Link inconclusive (volume scalar).

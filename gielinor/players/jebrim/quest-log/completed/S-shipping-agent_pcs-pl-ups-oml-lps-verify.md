# Shipping-agent pull — PCS PL UPS "overbilling" (€111k) verify: OML/LPS receivable?

**Role:** shipping-agent (emulation) · **Player in scope:** Jebrim · **Date:** 2026-06-02 · **Tier:** gold-contract

## Ask
Verify before report rebuild: is the ~€111k UPS "overbilling" on PCS PL (TCG) a random billing error, or UPS OML/OML-family + LPS surcharges with a refund mechanism? Decide legitimate-cost vs mis-charge-receivable using package dims + charge descriptions. Establish population, charge decomposition, dims-band table, reversal mechanism, verdict.

## Scope resolved
- PCS PL: `production_site='PCS PL'`, `source_system IN ('Picturator','PicaAPI')`, `shipping_provider_group='UPS'`, `cost_source='invoice'`.
- Anomaly net: `real >= 2*expected AND real-expected >= 10`. Cohort anchor `shop_order_created_date`, trailing ~120d → literal `>= '2026-02-03'` (validator rejects DATEADD/CURRENT_DATE).
- Bands on `length_plus_girth_cm`: OML >419, LPS 325-419, below <325, NULL.

## Live numbers (trailing 120d window unless noted)
- **Population:** 5,253 anomalous rows; real €365,559; expected €14,251; **over-expected €351,308**. (The broad net is wider than the prior ~86-row read — includes LPS + small AHS. The OML "Demand Surcharge - Over Maximum" line is exactly **86 positive lines** = the prior run's "~86 rows".)
- **Charge decomposition (anomalous pop):** oversize_overweight splits into named lines — LPS "Large Package Surcharge" €97.3k applied; OML family "Demand Surcharge - Over Maximum" €40.4k + "Over Maximum Size" €33.4k + "Over Maximum Length" €9.0k. Plus base_rate, fuel, residential, etc.
- **CRUX — dims bands (shipments w/ a positive oversize line):** OML band (>419) = **0 shipments**; LPS band (325-419) = 398 / €41.5k applied; below-325 = 579 / €138.8k applied; NULL = 0. **Max length+girth across the entire charged population = 332 cm.**
- **Charge-text × band:** OML-text charges (€81.8k) land on parcels **154-324 cm** (below even the LPS 325 trigger). LPS-text charges (€56.8k) also on below-325 parcels. The dims do NOT justify the surcharges.
- **Dims coverage:** PCS PL UPS invoiced slice = 164,536 rows, **0% NULL** on length_plus_girth_cm. No coverage gap here (contra the known-dq NULL-dims worry — PCS owns the dim and it's fully populated on this site).
- **Reversal mechanism = refund-in-place CONFIRMED:** negative lines keep `oversize_overweight` bucket + same "Over Maximum"/"Large Package" description (per known-dq carrier-rule 3). The −€91.6k prior snapshot = a single invoice-month batch (OML-family reversals −€88.8k in 2024-05, −€89.3k in 2025-05; −€148.5k in 2026-02).
- **All-time PCS PL UPS:** LPS applied €1.345M / reversed −€318.5k / **standing net €1.027M**; OML applied €992k / reversed −€578.6k / **standing net €414k**. All-time dims: OML band (>419) = **3 shipments** (max girth 560); LPS band 7,494; below-325 **61,922**. The over-max/large-package surcharges are overwhelmingly on sub-threshold parcels.
- **Standing (un-reversed) net by band, all-time:** below-325 carries €479k OML + €612k LPS still standing; LPS-band €426k LPS; OML-band €0 OML.

## Verdict
The €111k headline is **NOT a random billing error, and NOT legitimate over-limit cost — it is a mis-charge receivable**: UPS OML (over-max) + LPS surcharges applied to parcels that do not meet the dimensional trigger. The OML band (>419) is empty in the window and 3 shipments all-time; "Over Maximum" charges sit on 154-324 cm parcels (below the 325 LPS trigger, far below 419 OML). The refund-in-place mechanism is real and already clawing some back in batches (−€91.6k = one snapshot month; all-time OML reversed €578.6k, LPS €318.5k), confirming UPS itself treats these as refundable. **The true monitoring number is the STANDING (un-reversed) net, not the gross applied** — all-time ~€1.0M LPS + €0.41M OML still standing, concentrated on sub-threshold parcels = an active receivable to dispute, not a packaging signal. The report's "overbilling" framing is directionally right but should be reframed: standing OML/LPS receivable pending refund (mostly sub-threshold = disputable), tracked as the un-reversed net.

## Checks done
- Bucket split done first (charge-description decomposition) before any cause claim.
- Dims-band the falsifying cut — would have shown legitimate cost if parcels were >419; they are not (max 332 window / 560 all-time on 3 rows).
- Reversal sign-split confirms refund-in-place (negative lines, same bucket+description).
- Reconciled prior figures: 86 OML lines = prior "~86 rows"; −€91.6k = single invoice-month OML reversal batch.
- Standing-net computed separately from gross-applied (the receivable ≠ the gross).

## DQ caveats
- length_plus_girth_cm 0% NULL on PCS PL UPS — no adjudication gap on this site (PCS owns the dim).
- oversize sub-types are inferred-not-stored per the contract, BUT here the charge_description_english is explicit ("Over Maximum…", "Large Package Surcharge") — no inference needed.
- "over-expected" uses expected_shipping_cost_eur as the baseline (model-derived, medium trust); the surcharge euro figures themselves are invoiced (high trust).

## Deliverable
- Chat-only (written findings to principal). No chart requested.
- Probe scripts archived: `shipping-agent/scratchpad/archive/ups_oml_verify[1-5].py`.

## Open / needs principal
- Report headline reframe: "€111k overbilling" → "standing OML/LPS receivable, mostly on sub-threshold parcels (disputable), tracked as un-reversed net". True monitoring number is standing net (~€1.0M LPS + €0.41M OML all-time), not gross applied.
- Why is UPS charging over-max/large-package on sub-325cm parcels at all? Likely a UPS dim-measurement/classification error on their side → the dispute basis. Worth surfacing to whoever files the UPS claims.
- known-dq "UPS oversize surcharges — LPS/OML" entry was UNVERIFIED; this run verifies the refund-in-place behaviour and the bands, but FOUND the dims do not match the charges (the entry assumed trigger>threshold = legitimate; reality is trigger-not-met = disputable). Maintainer may want to update that entry (principal-gated, not mine).

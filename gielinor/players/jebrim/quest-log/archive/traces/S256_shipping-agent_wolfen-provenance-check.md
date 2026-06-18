# Shipping-agent pull — Picturator@Wolfen cost provenance (estimate-as-real hypothesis)

**Spawned by:** Jebrim, as shipping-agent sub-agent (mart specialist, emulation)
**Date:** 2026-06-17
**Tier:** gold-contract (all results from `shipping_mart.*`; no upstream/dw leg needed)
**Scope:** `source_system='Picturator'` AND `production_site='Wolfen'` on `fact_shipments`.
Note: brief said `data_source` — no such column; the principal's `data_source='Picturator'` = `source_system='Picturator'`. Wolfen is a Picturator *production-site* label (485,977 rows all-time), distinct from the ORWO photo-lab *source_system*.

## Hypothesis (principal's)
Picturator@Wolfen shipments flagged `cost_source='invoice'` carry a "real" cost with NO carrier-invoice-line backing — i.e. estimate booked as real, inflating invoiced-coverage and faking Wolfen's cheap ~16% ratio.

## Verdict: DISCONFIRMED for Picturator@Wolfen.

- cost_source split (all-time): invoice 253,346 rows / €1.527M; expected 232,324 / €0.993M; null 307; **no `avg`**.
- CRUX: of the 253,346 invoice-flagged rows, **100% (all) have >=1 invoice line.** Zero real-without-line. Same for Jan-May 2026 window: 0 rows, €0 unbacked of the €559,769 invoiced leg.
- Backing lines are real **`dhl_orwo` / `ups_orwo` bulk-bill** carrier invoices (rule 14 allocation) + small `dhl`/`ups`. Not estimates.
- real-vs-expected row-level: 67.6% differ >50c, only 13.5% equal-to-cent. Aggregate near-equality (€1.527M vs €1.524M) is coincidental netting, NOT "expected copied into real".
- Generalization: invoice-flagged-without-line DOES exist but tiny + elsewhere — PCS PL 0.79% (€146k), LaserTryk 1.75% (€19k). Wolfen = 0.000%, cleanest. (Picturator scope.)

## v2 impact (Jan-May 2026, Picturator+PicaAPI, excl PCS MI/PX/CMH, order-month lens, Wolfen incl)
- ALL v2: €6.932M final / 90.20% invoiced / €37.030M rev / quota 18.72%.
- Wolfen-in-v2: €755,843 final / 74.06% invoiced / quota 16.45%.
- v2 excl Wolfen: quota 19.04%.
- € of invoiced leg that is Wolfen-real-without-line = **€0**. No coverage overstatement from this mechanism.
- Wolfen's cheap ratio is REAL (backed by real bulk-bill invoices), not estimate-driven. It does drag the combined quota down ~0.3pt vs excl-Wolfen, but legitimately.

## Open / flag
- Wolfen invoiced-coverage is 74% (current-window invoice lag, expected) not a defect.
- The real-without-line pattern (PCS PL €146k, LaserTryk €19k) is a separate, marginal finding worth a note if the principal cares about overall coverage integrity.
- Chat-only deliverable; no files outside brain.

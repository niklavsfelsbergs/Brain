# S220 — EU tender: does Q4 product-mix seasonality need modelling? (Mix-1 test)

**Player:** Jebrim · **sid8:** 097ab6e8 · **Date:** 2026-06-12

## Ask

Test whether the annualization must model intra-year product-mix seasonality, or whether the current "hold Q1 unit cost flat across the year" assumption (Mix-1, status F / documented-not-modelled) is safe. The annual figure (€1.91M/yr saving, €976k base tier) scales Q1 unit costs to full-year volume holding Q1's mix. Deliverable: yes/no on modelling Q4 mix + €/yr exposure vs the ±€26k fuel band + concrete `build_annual` change if material.

## Verdict — KEEP Mix-1 (do not model Q4 mix)

Exposure on the **saving** is low single-digit €k, comfortably inside the ±€26k fuel band the report already presents as noise. No `build_annual` change needed. Strengthen the Mix-1 ledger entry from "assumed cancels (qualitative)" to "measured flat across quarters incl. Warenpost-tier eligibility."

## Method (population-consistent, no live mart needed)

The annualization's own input — `2_analysis/data/cost_matrix/cost_matrix_2025-*.parquet` (12 monthly partitions, 2.875M PCS-PL shipments) — already prices **every** 2025 parcel under **every** candidate carrier, with physical dims + per-surcharge cost columns. That is a more population-consistent basis than the live mart for this specific test (same population + same `shop_order_created_date` time basis the annualization uses, per Time-1). One row/shipment via the `carrier=='maersk'` row (physical attrs are shipment-level). Profiled by quarter; plan side re-routed per quarter via cheapest-FINAL_6-engine proxy.

## Evidence (all measured Q1 vs Q4)

1. **Physical mix is flat.** Q1 mean wt 1.53 kg / Q4 1.52; longest side 57.0 / 56.8 cm; length+girth 147 / 146. Q3 is actually the *bulkiest* quarter, not Q4. Q4 is a volume spike (40% of FY), not a mix shift.
2. **Cost-driving tail moves but doesn't bite.** Longest-side >60cm rises Q1 30% -> Q4 44% (more flat posters), BUT the engine-*billed* oversize rate falls on every carrier (DHL Paket 19.8%->18.5%, Maersk 14.1%->12.2%); heavy tail (>10kg, dim-weight binding) shrinks in Q4.
3. **Per-carrier EUR/parcel flat.** UPS 6.14->6.24 (+1.6%); DHL Paket 8.64->8.61; Maersk 8.31->8.12. Oversize EUR/pp flat-to-down all carriers. DPD 5.92->6.59 (+11%) — real but destination-mix (more DE in Q4), NOT oversize; nets out of the saving.
4. **Plan migrates favourably and small.** Re-routing each quarter: DHL Paket share 51%->42%, DPD 33%->42% (toward the cheaper carrier — Niklavs' hypothesis confirmed). But true plan cost/pp only +1.5% Q4 vs Q1; the migration makes the flat-routing method mildly *conservative*, not optimistic.
5. **Warenpost (the key probe) does NOT surge.** Warenpost IS modelled (cheapest-eligible tier inside `dhl_paket`: wt <=1kg + 35.3x25x10cm envelope). Physical WP-eligibility flat: Q1 21.7% ~ Q4 21.5%. Engine WP-priced share flat-to-down: Q1 6.2% -> Q4 5.5%. The 2025 *actual* WP usage surge (8.9%->15.4%) is an operational adoption curve on a flat physical base — and the 2026 engine prices WP on *all* eligible parcels incl. Q1's, so the Q1 base already captures the full WP benefit. Scaling flat is correct.
6. **Peak is separate and small.** Modelled as an additive Oct-Dec layer (DHL 0.16+0.13 pip, Maersk 0.25, actual invoiced 0.18/pp), fires symmetrically on both sides -> already in the bridge as -41k differential. Not part of Mix-1. Per-parcel peak rates are just genuinely small (2-4% of base, Q4 window only) — answers "why no big Q4 peak impact."

The three ways Mix-1 could have broken (bulkier Q4 / Warenpost growth / peak asymmetry) all measured flat. Both sides drift +1.5%/+1.7% into Q4 in tandem -> the saving (difference) drift nets to ~0.2% ~ 4k.

## Caveat

Do-nothing side can't be *perfectly* re-priced per-quarter on 2025 data (its incumbent roster changes across the year — GLS/Colis-Prive exit, DPD-PL ramps; the exact reason the annualization anchors on the 2026-Q1 book). Used actual invoiced `real_total_eur` as the do-nothing proxy for the tandem-drift argument. Exact per-quarter `keep_ref` (restricted to surviving incumbents) is ~1/2 day if a euro-exact number is ever wanted — not recommended; the bound is already inside the band.

## Correction this session

Asserted "the tender doesn't model Warenpost as a carrier" off a `carriers/` dir listing — wrong. Niklavs pushed back ("dont we model warenpost? we have an engine for that"). It's a service tier inside `dhl_paket`. Re-verified via grep before re-answering. -> examine draft + reinforces existing memory `feedback_never_assert_absence_against_principal_claim`.

## Pending external actions

None pending. Read-only on bi-analytics (queries only); no repo writes.

## Harvest

- bank draft: `bank/drafts/notes/projects/2026-06-12-eu-tender-mix1-q4-seasonality-measured-flat.md`
- examine draft: `examine/drafts/2026-06-12-verify-modeling-claim-before-asserting-absence.md`

## Cascade

None — analysis only, no brain-rule or cross-file change.

## Main-brain changes

None.

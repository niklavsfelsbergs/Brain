# EU tender Mix-1: Q4 product-mix seasonality measured flat — keep the flat-Q1 scaling

**As-of:** 2026-06-12 ([[S220_097ab6e8_eu-tender-q4-mix-seasonality|S220]], sid8 097ab6e8). Anchors quest [[S220_097ab6e8_eu-tender-q4-mix-seasonality]]. Companion to [[2026-06-11-eu-tender-annualization-method]].

## Claim

The annualization's **Mix-1** assumption — hold 2026-Q1 unit cost flat and scale by per-country volume (×~4.8) to full year — is **safe; do not model Q4 product-mix seasonality.** Exposure on the **saving** is low single-digit €k, inside the ±€26k fuel band. Upgrade the ledger entry from status F (assumed-cancels, qualitative) to **measured-flat**.

## Why it holds (the cancellation logic)

Saving = do-nothing − plan. A Q4 mix shift only moves the saving if it's **asymmetric** — costs more on one carrier than another (e.g. trips one carrier's oversize threshold but not another's, where the plan re-routes between them). A symmetric shift cancels. Measured Q1 vs Q4, every channel is flat or symmetric:

- **Physical mix flat** — mean wt 1.53→1.52 kg, longest side 57.0→56.8 cm, length+girth 147→146. Q3 is the bulkiest quarter, not Q4. Q4 is a *volume* spike (40% of FY), not a mix shift.
- **Cost-driving tail moves but doesn't bite** — longest-side >60cm rises 30%→44% (more flat posters), but engine-*billed* oversize incidence *falls* every carrier (DHL Paket 19.8→18.5%, Maersk 14.1→12.2%); heavy/dim-weight tail shrinks.
- **Per-carrier €/pp flat** — UPS +1.6%, DHL −0.3%, Maersk −2.3%; oversize €/pp flat-to-down all carriers.
- **Plan migration favourable + small** — re-routing each quarter, DHL Paket 51%→42% / DPD 33%→42% (toward the cheaper carrier), but plan cost/pp only +1.5% Q4; the flat-routing method is mildly *conservative*, not optimistic.
- **Both sides drift in tandem** — plan +1.5% / do-nothing proxy (actual `real_total`) +1.7% into Q4 → saving (the difference) drifts ~0.2% ≈ €4k.

## Warenpost (the sharpest probe — flagged by Niklavs)

Warenpost **is** modelled — a cheapest-eligible service tier inside the `dhl_paket` engine (`WARENPOST_MAX_WEIGHT_KG=1.0`, envelope 35.3×25×10 cm). The worry was "Q4 ships more small gifts → more cheap Warenpost → flat-Q1 overstates Q4 cost." Measured: **physical WP-eligibility is flat (Q1 21.7% ≈ Q4 21.5%)** and engine WP-priced share is flat-to-down (6.2%→5.5%). The 2025 *actual* WP usage surge (8.9%→15.4%) is an **operational adoption curve on a flat physical base** — and the 2026 engine prices WP on *all* eligible parcels including Q1's, so the Q1 base already captures the full WP benefit. Lesson: a carrier-product *labeling* shift ≠ a physical *mix* shift; the engine prices on physics, so only the physical eligibility share matters.

## Peak — kept distinct (don't double-count)

Peak is an additive Oct–Dec layer (DHL €0.16+€0.13 pip, Maersk €0.25, actual invoiced €0.18/pp), firing symmetrically on both sides — already in the bridge as the −€41k differential. Not part of Mix-1. Per-parcel peak rates are genuinely small (2–4% of base, Q4 window only).

## Method note (reusable)

The cleanest basis for any "is the annualization mix-invariant" test is **`cost_matrix_2025-*.parquet`**, not the live mart: it already prices every parcel under every candidate carrier across all 12 months, with dims + per-surcharge columns, on the same population + time basis (`shop_order_created_date`) the annualization uses. Re-route each period and check whether per-period cost/pp and carrier-share drift in tandem on both sides. (Skill candidate: *test annualization mix-invariance by per-period re-route + tandem-drift check* — graduate at alch.)

## Caveat

Do-nothing side isn't perfectly re-priceable per-quarter on 2025 data (incumbent roster changes across the year — GLS/Colis-Privé exit, DPD-PL ramps; the reason the annualization anchors on the 2026-Q1 book). Used actual invoiced cost as the do-nothing proxy. Euro-exact = ~½ day (full `keep_ref` on surviving incumbents); not recommended — bound already inside the band.

## Separate finding

DPD base cost/pp +11% in Q4 = destination-mix (more DE), **not** oversize. Nets out of the saving; matters only for per-month *cost* accuracy.

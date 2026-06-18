# S224 — Yodel-via-Maersk UK offer: incumbent volume profile (mart pull)

**Player:** Jebrim · **Spawned as:** shipping-agent sub-agent · **Date:** 2026-06-12
**Project:** EU-tender-2026 — separately-scoped UK deal (Yodel-via-Maersk).

## Ask
PROFILE pull (no re-rating) of current UK shipping to (a) size what the Yodel offer's service caps leave on the table and (b) establish the 2026-Q1 invoiced incumbent baseline.

## Scope used (gated strictly)
- Destination = GB / United Kingdom (gated on `destination_country_code = 'GB'`, NOT origin — UK fulfilled from multiple sites incl. PCS-PL). Single clean label "United Kingdom".
- Period = 2026-Q1 (`shop_order_created_date` >= 2026-01-01, < 2026-04-01).
- Vertical = TCG (`source_system IN ('Picturator','PicaAPI')`) — ORWO photo lab excluded per contract fork.
- Invoiced-only basis (`cost_source = 'invoice'`, `real_shipping_cost_eur`) to match incumbent.
- Gold contract tier only. No raw reach.

## Status / trace
- GB population pre-gate: 98,909 invoiced + 671 expected + 21 uncosted = 99,601. Invoiced coverage 99.3% by count — very clean.
- HEADLINE: 98,909 invoiced shipments, €588,296.93, €5.95/parcel (invoiced-only).
- Carrier mix: DPD UK 46,467; Maersk 32,119; Yodel 13,731 (already shipping UK on Yodel); UPS 6,484; DHL/FedEx tail. Sums to 98,909.
- Weight bands: 88% in 0–3kg; zero parcels >30kg by weight; 146 unknown-weight.
- Dim/vol coverage: weight 99.85%, dims/volume/length+girth 99.36% (all 98,272 together).
- Yodel tier map (sorted-dim AND logic + volume): Small 954 / Medium 9,255 / Large 54,079 / **Uncovered 33,984 (34.4% ct, 38.2% €224.9K)** / no-dims 637.
- KEY: uncovered tail is ~92% driven by the 15L Large-tier VOLUME cap (31,380 of 33,984), not length or weight. dmax 120–170cm only 2,181; vol>160L only 423; zero >170cm; zero >30kg.
- Postcode: mainland 96,350 / NI(BT) 1,661 (1.68%) / remote H&I whole-area 898 (0.91%). Conservative remote estimate (whole-area IV/HS/KW/ZE/IM only).
- B2C 96,758 (97.8%) / B2B 2,151 — matches Yodel Home Delivery (B2C) target.

## Checks
- Headline re-run independently — matches. Every population cut reconciles to 98,909; dims-present cuts to 98,272. Tier-uncovered decomposition sums back to 33,984.

## Open / flags
- Remote/H&I sizing is whole-area only; partial-district H&I zones (PA20-49, PH17+, KA27-28) fall into mainland — needs outward-district parse for precision if surcharge incidence is decision-vital.
- Tier-cap volume number (31,380 at 15L) is the headline lever for renegotiating the Yodel Large cap.

Deliverable: chat-only tabular return to principal. No brain-bank write (out of boundary).

---

## S224 follow-up pull (2026-06-12) — uncovered-tail drill

Same scope re-confirmed exactly: 98,909 invoiced / €588,296.93; tiers Small 954 / Medium 9,255 / Large 54,079 / Uncovered 33,984 / no-dims 637. All reproduce.

- **D1 can/cannot layout.** CAN (Small+Medium+Large) 64,288 / €355,791 (65% ct, 60.5% €). CANNOT 34,621 / €232,506. Cannot broken by first failing cap: vol 15–160L 31,380 (€200,043) — the mover; longest 120–170cm 2,181 (€21,132); vol >160L 423 (€3,740); no-dims 637 (€7,592). Zero >30kg, zero >170cm (max wt 29.86kg, max long 142cm) — those two caps are dead in this slice.
- **D2 uncovered carrier×service.** DPD UK 25,416 (€168,672, €6.64/pc, 74.8% ct); Yodel 4,877 (€32,211, historical Q1 lane); Maersk 3,037 (€15,171, €5.00/pc); UPS 654 (€8,861, €13.55/pc). Sums to 33,984.
- **D3 characterize.** Weight: 91% ≤5kg (light-but-bulky). Vol within tail: 15–25L 15,796 / 25–40L 9,409 — mass concentrated low. Longest: 60–100cm 22,959 (flat). Product: CVS (canvas) SKU prefix on 26,980 of 33,984 (79%), PPS (poster/print) 3,414 next. **Confirmed canvas/framed-print profile.** No product-name dimension in gold contract — used SKU prefix as proxy; packagetype_group fully NULL on this slice; packagetype dominated by WICKELVERPACKUNG flat-wrap formats.
- **D4 recovery curve (cap lift, longest≤120 & wt≤30 held).** 25L → 15,796 pc / €91,185; 30L → 20,500 / €118,443; 40L → 25,205 / €155,387; 60L → 29,296 / €185,167. Cumulative. Ceiling = vol-bust parcels that are also ≤120cm.

Checks: every breakdown sums to its parent (33,984 / 98,909). Recovery curve reconciles to volume bands minus the long-bust overlap (931 parcels >120cm sitting in 15–60L can't recover on a volume lift). Field assumptions noted (no product dim; SKU-prefix proxy).

---

## S224 third pull (2026-06-12) — which PACKAGE TYPES make up the uncovered tail

Scope re-confirmed exactly: 98,909 / €588,297; tiers Large 54,079 / Uncovered 33,984 / Medium 9,255 / Small 954 / no-dims 637. Reconciles.

**Field used: `packagetype`** (235 distinct, on `fact_shipments`). 99.3% populated on full scope, **100% on the uncovered tail**. `packagetype_group` is fully NULL (no source V1) — not usable; no fallback needed. This is the same axis the EU-tender capability matrix keys on.

- **D1 — tail by package type.** Flat/wrap formats dominate. By format family: Wrap (WICKELVERPACKUNG) 22,947 / €145.0K (67.5%); ORWO-wrap format 3,814 / €22.4K (11.2%); Die-cut flat (STANZVERPACKUNG) 2,763 / €26.4K (8.1%); Carton/box 2,086 (6.1%); Custom-cut/oversized 1,270 (3.7%); Box-in-box 662 (1.9%); Other 442 (1.3%). Sums to 33,984. Top individual types: WICKELVERPACKUNG_60x40 5,721; WICKELVERPACKUNG 80x60 AE 4,142; ORWO_80x60 3,814; WICKELVERPACKUNG 100x75_AE 3,804; WICKELVERPACKUNG 70x50_ 3,480. ("ORWO_80x60" is a packaging FORMAT name on Picturator/PicaAPI parcels — not the ORWO vertical, which is excluded by source filter.)
- **D2 — can vs cannot by type.** Near-binary: each package type is ~100% can OR ~100% cannot. The cap busts concentrate in the larger-format wrap/die-cut SKUs (60x40, 80x60, 100x75, 70x50, 120x80, 120x90 → all 100% cannot). Small formats fit 100%: STANZVERPACKUNG 30x20/40x30 pizza box, WICKELVERPACKUNG 30x20/40x30, mug box, Großbrief. NOTE the same nominal name splits on actual dims: `WICKELVERPACKUNG 60x40 AE` (14,970) fits 100%, `WICKELVERPACKUNG_60x40` (5,721) busts 100% — different recorded dims/volume despite same label.
- **D3 — bust reason per top type.** Every top uncovered type is 100% on the 15–160L volume cap; zero on length, zero >160L. Tail-wide: vol 15–160L 33,560 (98.8%), vol>160L 423 (1.2%), length 120–170cm 1 parcel. Avg volume climbs with format size: 60x40 ~16.3L (just over the 15L cap), 70x50 ~24.6L, 100x75 ~62.4L, custom-cut ~90.6L.
- **D4 — canvas cross-check.** Corroborates exactly: 26,980 / 33,984 = **79.4% carry a CVS (canvas) SKU** — matches the prior 79% finding. 90.6% of the tail sits in flat/wrap formats; 25,266 of the 26,980 canvas parcels (94%) are in flat formats. Package-type lens and SKU lens point at the same parcels: large flat canvas wrap formats.

Checks: D1 family + individual breakdowns sum to 33,984; can(64,288)+cannot(33,984)+no-dims(637)=98,909 reconciles; D3 reasons sum to 33,984. packagetype coverage stated (100% on tail). Deliverable SQL: `shipping-agent/workbench/investigations/uk-yodel-volume-profile/sql/20260612-01_uncovered-tail-by-packagetype.sql`.

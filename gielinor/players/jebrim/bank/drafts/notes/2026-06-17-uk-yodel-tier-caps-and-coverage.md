# UK Yodel (Maersk-brokered) — tier caps + corrected coverage

**Status:** drafts — harvest at alching. Source of truth = `bi-analytics-main/NFE/projects/2_EU_tender_2026/3_UK/`. Continues [[S224_yodel-uk-volume-profile]], corrected [[S261_c2f15e55_uk-yodel-oog-cap-correction]].

The UK is a **separate track** from the EU tender (Maersk-brokered Yodel, GB-only, B2C Home Delivery). Out of EU-tender scope per the tender README ("Maersk-UK (A0) is a separate deal").

## Rate card (offer 01.07.2026–30.06.2027, deterministic)

Flat base rate per tier (no weight gradient within ceiling):

- **Small** £1.99 — ≤ 40×25×19 cm, ≤19 L (0.019 m³), 0–3 kg
- **Medium** £2.39 — ≤ 64×41×38 cm, ≤100 L (0.0997 m³), 0–15 kg
- **Large** £3.69 — length ≤120 cm, ≤160 L (0.16 m³), 0–30 kg
- PUDO £1.94 — same as Medium; over-Medium → returned to sender

**OOG:** length 120–170 cm → +£15/parcel; length >170 cm OR >0.16 m³ → +£50/parcel (£15 does not stack); unliftable/too-large → RTS. Fuel = **−8% discount** of published rate. Other flat surcharges: NI £1, out-of-area £4.50, ULEZ £0.05, peak £0.10 (Nov–Jan), relabel £1, repack £2.50, non-machinable £0.50, restricted £25, missing-PAN £1.

## Key correction (don't repeat)

The card's "Maximum Liter" column is in **m³, not litres** (0.019/0.0997/0.16 = 19/100/160 L); the per-parcel **OOG surcharge** is the adjacent column (£1/£3/£15). [[S224_yodel-uk-volume-profile]] mis-read col T (1/3/15) as the litre cap → claimed a 15 L Large cap and a "34% uncovered" tail. Corrected cap is **160 L**.

## Corrected coverage (2026-Q1, invoiced, GB, TCG — 98,909 parcels / €588,297)

Yodel tiers cover **96.7%** of UK volume: Small 28,673 / Medium 20,996 / Large 45,999. **Uncovered (OOG) only 2,604 (2.6%) / €24.9K** — £15 band 2,181, £50 band 423; OOG surcharge exposure ≈ £53,865/Q. Supersedes [[S224_yodel-uk-volume-profile|S224]]'s 34%/€224.9K.

## Truck/linehaul GATES the comparison (the big one)

The €588K incumbent is **35.8% truck charges** (€210,703; 94.9% of parcels carry one — UK ships largely from PCS-PL). The Yodel offer is a parcel rate with **no linehaul**, so it competes against the **ex-truck parcel baseline ≈ €377,594** (base €342,211 + oversize €20,698 + fuel €8,207 + tail). Truck handled separately: moving to Maersk drops per-truck cost **£3,700 → £3,620** (~2.2%); calc method/source pending (principal will supply). **Final UK picture only resolvable once trucks are accounted for.** Mart carries `truck_charges_eur` bucket + `real_shipping_cost_local` (GBP).

## Assumptions locked (2026-06-17, principal)

Non-machinable £0.50 → assume zero. no-dims 637 → filtered out. OOG £15/£50 boundary → trust Stefan. Basis Q1-2026 invoiced, no annualization. Dims = our declared (accepted risk).

**Remote/NI — material under the offer (corrected — was wrongly called immaterial).** Incumbent absorbed remote (€24 bucket), but Yodel bills it: NI/BT 1,560 parcels × £1 + out-of-area 3,209 × £4.50 = **≈ £16K/Q (~£64K/yr)**, ~5% of the ex-truck parcel baseline. Zones: BT=NI; IV/HS/KW/ZE/IM/AB/TD + partial PA≥20/PH≥5/KY/PO30-41/TR21-25/KA27-28 = out-of-area; JE/GY (51) edge case. **BT = £1 only, does NOT stack with £4.50 (principal-confirmed 2026-06-17)** — sizing already reflects it. District list in `3_UK/.../yodel_remote_area_postcodes.md`.

## Comparison basis — go-forward DPD UK (principal, 2026-06-17)

**Scope: replace EVERYTHING** — the new Yodel offer is modelled as carrying the whole UK book (all 98,909, incl. current Maersk-UK + DPD UK + UPS). Re-rate runs on the full book (resolves the earlier whole-book-vs-slice open).

Benchmark is **not** the raw incumbent — it's **invoiced DPD UK costs adjusted go-forward**: a GRI price increase + a newly-implemented fuel surcharge. DPD UK is the carrier being dropped (contract to 21.11.2026 per [[carrier-contracts]]); its forward cost is the benchmark. GRI %/fuel mechanism + source = principal to supply; confirm go-forward treatment of the non-DPD current volume. "Compare on go-forward, not raw" reflex.

## Cost engine BUILT (2026-06-17)

Standalone polars engine `3_UK/2_analysis/yodel_engine/` (constants + calculate; 10 unit tests pass) + SQL mirror `yodel_engine/sql/headline_cost.sql` (live-book). Model: tier (weight-gated dims+vol) → base → fuel → OOG → NI/out-of-area → peak.

**Fuel (two corrections):** (1) it's a **surcharge**, not a −8% discount; (2) the discount is **percentage-points**: published 18% (June 2026, diesel-linked) **− 8pp = 10%** on base (principal-confirmed 2026-06-17, not the relative 16.56% reading).

**Headline (whole UK book, Q1, GBP, ex-truck, 98,272 parcels):** base £286,635 + fuel £28,664 + OOG £53,865 + NI £1,560 + out-of-area £14,441 = **≈ £385,165/Q (£3.92/parcel)**. Weight-gate moved only ~28 parcels. NOT a verdict — comparison pending DPD-go-forward baseline + truck. Don't compare to €377,594 raw (currency + go-forward).

## NEW offer vs CURRENT Maersk/Yodel contract (key finding, 2026-06-17)

Mart "MAERSK" UK carrier **is Yodel** (Maersk brokers it; current card `docs/shipping_contracts/1. EU/1. PICANOVA/MAERSK/Maersk Rate Card UK 2026.xlsx` brokers Yodel/EVRI/DPD). Current Yodel prices **by WEIGHT** (0-3kg £1.89 / 3-15kg £2.74 / 15-30kg £4.56, all-in ~2.5% fuel; caps generous — Xpect Large 230L/170cm/30kg, no volume surcharge). New offer prices **by VOLUME**.

**Whole book (98,272, ex-truck): current ≈ £196K (~£2.00/pc) vs new £385K (£3.92/pc) → new ~+90%, ~1.9× DEARER.** Four adverse changes: (1) axis weight→volume (penalizes light-bulky canvas — 89% ≤3kg bill £1.89 today regardless of bulk; new by size £1.89→£3.69); (2) fuel 2.5%→10%; (3) size cap 230L→160L (new covers LESS); (4) OOG £15/£50 added. Earlier "+20% vs blended incumbent" understated it (blend lifted by costly DPD UK). Negotiation flag: push volume axis / Large caps, or hold weight-based.

## Truck/linehaul leg (sized 2026-06-17)

GB linehaul = `shipping_mart.fact_truck_charges` lane **`UK DHL Freight`** (PL→UK; off-contract, tcg_nfe; [[2026-06-09-fact-truck-charges-navigation]]). Split from old combined "UK and FR DHL Freight" (£2,850, ended Oct-25) on 2025-11-03. Rate: £3,700 (Nov25-Mar26) → £3,620 (in place May-26+; this step already happened) → **£3,350 (Maersk move, pending) = £270/truck**. ~**260 GB trucks/yr** (peak-aware; ~1,788 parcels/truck; no clean full year yet, lane only Nov25+). **Truck annual saving ≈ £270 × 260 ≈ £70K/yr.** OPEN: absorbing DPD UK's 46K may ADD trucks (if they don't ride this linehaul today) — could outweigh the rate cut. **Basis: truck saving is ANNUAL; parcel deltas are QUARTERLY (Q1) — annualize before netting, the SAME way as the EU tender** (Q1 × per-country 2025 seasonal profile, ~×4.8, peak-only term — [[2026-06-11-eu-tender-annualization-method]] / build_annual; don't hand-roll ×4). At ~×4.8 the parcel delta ≈ £900K/yr; truck saving offsets <10%. Recorded `3_UK/2_analysis/uk_truck_linehaul_cost.md`.

## DPD go-forward surcharge hikes + Q1 RESULT (2026-06-17)

DPD UK hiking **oversize/overweight £3.50→£24** and **non-compatible £4.25→£7.50** (`3_UK/2_analysis/dpd_uk_goforward_surcharges.md`). Threshold (Contract Appendix p.3): oversize = length >1m OR wt >30kg OR girth(L+W+H) >2.3m. Actual Q1 incidence (DPD UK GB invoiced TCG): **oversize 4,948 (10.6%), non-compat 885 (1.9%)** — invoice line "Non-commercial handling charge" (confirm = non-compat). **Q1 hike impact = +£103,745** (≈ all oversize — our long-flat canvas trips >1m/girth). 18-mo rates corroborate 10%/2%.

**HEADLINE Q1 (with trucks + DPD hikes):** STAY (incumbent £321,315 parcel + £103,745 hike + £179,028 truck@£3,620) = **£604,088**; MOVE (Yodel £385,165 + £165,661 truck@£3,350) = **£550,826** → **moving SAVES ≈ £53.3K/Q (−8.8%)**. DPD's own oversize hike flips Yodel from +9% dearer → ~9% cheaper. FLOOR — before DPD GRI + new general fuel (pending).

## THREE-WAY vs existing Q1 (mainland, with trucks) — RESULT + DECISION LEVER (2026-06-17)

Mainland 93,480 (offshore ~4,800 excluded, renegotiated separately). Both consolidation options drop the linehaul £3,700→£3,350 (truck saving is NOT Yodel-exclusive — any move gets it; so truck is neutral between options). DPD surcharges held current.
- **Existing (today): £463,940** (parcel £288,058 + truck £175,884@£3,700).
- **DPD-UK-only (held): £469,876 → +£5,936 (+1.3%)** — ~flat vs today.
- **All-Yodel: £509,192 → +£45,252 (+9.8%)** — ~+10%.
- DPD-only ~£39K/Q cheaper than Yodel (parcel gap; truck identical).

**DECISION LEVER = DPD oversize surcharge.** DPD-only's +1.3% holds ONLY if oversize negotiated to stay £3.50. If the £24 hike lands (9,027 mainland oversize ×(£24−3.50)≈+£185K/Q) → DPD-only ~+40%, worse than Yodel. So: win the negotiation → STAY (~same as today); lose → All-Yodel +10% is the capped hedge (OOG £15/£50 known). Yodel = insurance vs the hike, not a saving. NB "today" = expiring rates (cheap Maersk/Yodel weight deal + DPD both ending); do-nothing doesn't exist.

## Open / NEXT
- Pending principal inputs: DPD GRI %; DPD new general fuel surcharge (raise the STAY number). Confirm "Non-commercial handling"=non-compatible label. DPD-on-linehaul (truck count if Yodel absorbs DPD volume). Annualize via EU-tender method. Parquet replay of the Python engine vs the SQL headline when a book parquet exists.

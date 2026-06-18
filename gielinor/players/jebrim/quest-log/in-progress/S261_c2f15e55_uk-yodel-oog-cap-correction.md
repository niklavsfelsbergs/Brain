# S261 — UK Yodel: OOG question close + tier-cap correction + doc set

**Player:** Jebrim · **Date:** 2026-06-17 · **Session:** c2f15e55
**Project:** EU-tender-2026 — separate UK track (Maersk-brokered Yodel). Continues [[S224_yodel-uk-volume-profile|S224]].

## Ask
Principal got Stefan's (Maersk) answers on the Yodel Out-of-Gauge mechanics. (1) Do they close what was open? (2) If deterministic, write the UK docs (none existed) + re-run the volume check.

## What happened
- **OOG questions (a/b/c) closed.** (b) £50 at length >170cm OR >0.16m³; (c) 120–170cm → £15/parcel, charged not refused, £15 doesn't stack on £50. (a) mechanic = per-parcel; the figures `0.019/0.0997/0.16` we'd quoted were **volume caps (m³)**, not surcharges.
- **Root cause found — [[S224_yodel-uk-volume-profile|S224]] read the wrong column.** Rate card col S "Maximum Liter" is in **m³** (0.019/0.0997/0.16 = 19/100/160 L); col T "Out of Gauge surcharge" = £1/£3/£15. [[S224_yodel-uk-volume-profile|S224]]'s tier SQL used col T (1/3/15) as the **litre** volume cap. Off by ~10× on Large (15 L vs real 160 L). Not literally swapped columns — a unit mislabel ("Liter" holding m³) + [[S224_yodel-uk-volume-profile|S224]] grabbing the neighbouring column.
- **Re-run (corrected caps 19/100/160 L), live mart, invoiced GB Q1 TCG, 98,909 / €588,297:**
  Small 28,673 / Medium 20,996 / Large 45,999 / **Uncovered 2,604 (2.6%)** / no-dims 637. **Coverage 96.7%** (was [[S224_yodel-uk-volume-profile|S224]]'s 65%). OOG: £15 band 2,181 (£32,715/Q), £50 band 423 (£21,150/Q) ≈ **£53,865/Q**. Reconciles to 98,909.
- **[[S224_yodel-uk-volume-profile|S224]] "uncovered 34% / €224.9K, renegotiate the Large cap" is SUPERSEDED** → Yodel covers ~97%; OOG is a small fringe.

## Artifacts written (repo = source of truth)
- `3_UK/README.md` — UK track overview + status.
- `3_UK/1_offers/Maersk/offer_summary/yodel_rate_card.md` — deterministic rate spec.
- `3_UK/carrier_responses_to_open_questions/Maersk/2026-06-17_out_of_gauge.md` — Stefan Q&A reconciled.
- `3_UK/2_analysis/uk_yodel_volume_coverage.md` — corrected coverage profile.
- `shipping-agent/workbench/.../sql/20260617-01_corrected-tier-caps.sql` (20260612-01 superseded).

## Open / next
- **Cost re-rate** of Q1 book through the deterministic spec vs €588K incumbent — the real next step. OOG parcels get dearer (Large base + £15/£50); 2.6% but watch the £50 band.
- Postcode parse (NI/out-of-area/ULEZ) for surcharge precision — [[S224_yodel-uk-volume-profile|S224]] whole-area only.
- **Brain harvest at alching:** promote the drafts note `bank/drafts/notes/2026-06-17-uk-yodel-tier-caps-and-coverage.md`; add a UK line to the `eu-tender` domain digest (currently only "Maersk-UK is a separate deal").
- Method lesson candidate: *read the column header's UNIT, and confirm which column a value sits under, before using it as a model parameter* — generalizes the rate-type/value reflex. (examine/drafts candidate.)

## Follow-up (2026-06-17, same session) — caveat decisions + TRUCK gate

- **Truck/linehaul is the gate.** Pulled the GB Q1 invoiced cost-bucket split: total €588,297 = base €342,211 (58.2%) + **truck €210,703 (35.8%)** + oversize €20,698 + fuel €8,207 + tail; 93,830/98,909 parcels carry a truck charge. Yodel offer = parcel rate, no linehaul → compare against **ex-truck baseline ≈ €377,594**, not €588K. Truck handled separately: Maersk move drops per-truck **£3,700 → £3,620** (~2.2%); calc method/source the principal will supply later. **Final UK picture only resolvable after trucks accounted for.**
- **Caveat decisions (principal):** non-machinable £0.50 → assume zero; no-dims 637 → filter out; OOG £15/£50 → trust Stefan; remote/out-of-area £4.50 → immaterial (incumbent remote = €24 total); Q1 invoiced basis; use mart `real_shipping_cost_local` (GBP) for the re-rate; dims = our declared (accepted risk).
- **Remote-areas page pulled** (yodel.co.uk/remote-areas-and-transit-times) → district list captured in `3_UK/1_offers/Maersk/offer_summary/yodel_remote_area_postcodes.md`. Broader than [[S224_yodel-uk-volume-profile|S224]]'s whole-area heuristic, but immaterial given €24 actuals.
- **Docs updated:** README (truck gate + ex-truck baseline), 2_analysis/uk_yodel_volume_coverage.md (cost-structure + truck + locked-assumptions sections), new remote-postcodes ref.
- **Next session:** ex-truck parcel re-rate vs €377,594, then the truck leg.

## Comparison-basis note (2026-06-17, for memory)

Principal: the final benchmark is **invoiced DPD UK costs adjusted go-forward** — a GRI price increase + a newly-implemented fuel surcharge — NOT the raw historical incumbent. DPD UK is the carrier being dropped (to 21.11.2026), Yodel replaces it, must beat DPD's *forward* cost. GRI %/fuel mechanism + where documented = principal will supply later. **OPEN scoping question raised:** does Yodel replace the whole UK book or just DPD UK's 46,467-parcel slice? — decides the re-rate population. Recorded in README + analysis-doc "Comparison basis" + bank note. No mart pull this turn (memory note only).

**Scope resolved (2026-06-17):** replace EVERYTHING — new Yodel offer modelled as carrying the whole UK book (all 98,909, incl. current Maersk-UK volume). Re-rate population = full book (closes the whole-book-vs-DPD-slice open). Residual: confirm go-forward baseline treatment for non-DPD current volume. NFE 3_UK docs committed f92c619.

**Remote/NI sized (2026-06-17) — corrected my earlier "immaterial" call.** Mapped `shipping_zipcode` against the Yodel district set: mainland 94,089 (95.1%) / NI-BT 1,560 (1.6%) / out-of-area 3,209 (3.2%, IV/HS/KW/ZE/IM/AB/TD + partial PA≥20/PH≥5/etc.) / CI 51. Under the offer: BT £1 + OOG £4.50 = **≈ £16K/Q (~£64K/yr)**, ~5% of ex-truck parcel baseline. Incumbent absorbed remote (€24 bucket) → this is a NEW cost the re-rate must add. Assumption flagged: BT = £1 only (not stacked). Docs updated (analysis-doc "Remote/NI zones" + remote ref + bank note). Committed c5d22ba + 8299876 (BT-no-stack).

## Cost engine BUILT (2026-06-17)

Standalone polars engine `3_UK/2_analysis/yodel_engine/` (constants.py + calculate.py; 10 pytest pass on synthetic fixtures) + SQL mirror `yodel_engine/sql/headline_cost.sql` run over the live book + run_yodel.py (parquet runner) + yodel_cost_engine_result.md. Architecture = standalone (principal chose; not the EU-tender _base).
- **Fuel (two corrections):** (1) it's a SURCHARGE not a −8% discount; (2) the discount is percentage-points → published 18% (June-2026) − 8pp = **10%** on base (principal-confirmed; not the relative 16.56% reading). Fixed across rate card + README + analysis + engine constants. Pulled yodel.co.uk/fuel-surcharges.
- **Headline (whole book, Q1, GBP, ex-truck, 98,272):** base £286,635 + fuel £28,664 + OOG £53,865 + NI £1,560 + OOA £14,441 = **≈ £385,165/Q (£3.92/pc)**. Weight-gate shifted ~28 parcels. NOT a verdict — comparison pending DPD-go-forward + truck.
- Engine commit pending this turn.
- **Next:** DPD go-forward baseline (GRI+fuel) + truck leg from principal; then parquet replay of the Python engine vs the SQL headline.

## KEY FINDING — new offer vs CURRENT Maersk/Yodel contract (2026-06-17)

Mart "MAERSK" UK = Yodel (Maersk brokers it; current card `Maersk Rate Card UK 2026.xlsx` brokers Yodel/EVRI/DPD). Current Yodel = **WEIGHT-based** (0-3kg £1.89/3-15kg £2.74/15-30kg £4.56, all-in ~2.5% fuel, Xpect Large 230L/170cm, no volume surcharge). New = VOLUME-based.
- **Whole book ex-truck: current ≈ £196K (~£2/pc) vs new £385K (£3.92/pc) → ~+90%, ~1.9× dearer.** Drivers: (1) axis weight→volume (penalizes light-bulky canvas — main), (2) fuel 2.5%→10%, (3) cap 230L→160L (covers less), (4) +OOG £15/£50.
- Maersk-slice (32,119) check: current £63,944 vs new £81,638 (+27.7%); Large tier +92% (flat £2 → £4.06). Small-skewed slice understates whole-book hit.
- Recorded in yodel_cost_engine_result.md "New offer vs CURRENT" section. Negotiation flag: push volume axis / Large caps. This looks like a renewal repriced weight→volume.
- Initial-check (vs blended incumbent ex-truck) also done: Yodel £385K vs blended £321K (+20%) — understated because blend includes costly DPD UK. FX clarified: real_shipping_cost_local = ex-truck GBP parcel invoice; _eur adds EUR truck allocation; clean FX 1.1515.

## TRUCK leg sized (2026-06-17)

`fact_truck_charges` (off-contract, tcg_nfe; [[2026-06-09-fact-truck-charges-navigation]]). GB linehaul lane = **UK DHL Freight** (PL→UK; split from old combined "UK and FR DHL Freight" £2,850, ended Oct-25, on 2025-11-03). Rate: £3,700 (Nov25-Mar26) → £3,620 (in place now, May-26; already stepped) → **£3,350 (Maersk move pending) = £270/truck**. ~**260 GB trucks/yr** (peak-aware, ~1,788 parcels/truck, no clean full year — lane only Nov-25+). **Truck saving ≈ £270 × 260 ≈ £70K/yr.** Recorded `3_UK/2_analysis/uk_truck_linehaul_cost.md` + README.
- **Corrected my basis error:** truck saving is ANNUAL; parcel deltas (current £196K/new £385K/+£189K) are QUARTERLY (Q1). Annualize parcels (~×4) before netting — truck offsets <10% of annualized parcel increase, not "a third."
- OPEN: does absorbing DPD UK's 46K parcels add trucks to this linehaul (if DPD collects domestically today)? Could outweigh the £270 rate cut. Principal to advise.
- Principal corrected the rate twice: first "£3,700→£3,620", then "£3,620 in place → £3,350". Data confirmed £3,620 in place (May-Jun 26).

## DPD go-forward surcharges + Q1 RESULT (2026-06-17)

DPD UK hiking oversize/overweight **£3.50→£24** + non-compatible **£4.25→£7.50** (`3_UK/2_analysis/dpd_uk_goforward_surcharges.md`). Threshold (Contract Appendix p.3): oversize = length >1m OR wt >30kg OR girth >2.3m. Checked DPD UK invoice actuals (`fact_shipment_invoice_lines`, charge_description): Q1 oversize **4,948 (10.6%)** / non-compat **885 (1.9%)**; invoice label "Non-commercial handling charge" (confirm=non-compat). **Q1 hike impact +£103,745** (≈ all oversize).
- **Q1 RESULT (with trucks + DPD hikes):** STAY £604,088 vs MOVE £550,826 → **moving to Yodel SAVES ~£53.3K/Q (−8.8%)**. The DPD oversize hike flips Yodel from +9% dearer → ~9% cheaper. Floor (before DPD GRI + general fuel, pending). Recorded in yodel_cost_engine_result.md waterfall.
- **NEXT (queued):** simulate DPD-UK-only — keep DPD whole book, surcharges held at current (assume negotiated), exclude offshore (separately renegotiated). Then annualize (EU-tender method).
- All findings committed to NFE 3_UK this session (engine, coverage, truck, DPD surcharges, waterfall).

## THREE-WAY vs existing Q1 (mainland, with trucks) — final framing (2026-06-17)

Mainland 93,480 (offshore excluded). Both consolidation options get the £3,350 linehaul (truck neutral between them; principal corrected: not Yodel-exclusive). DPD surcharges held current.
- Existing today £463,940 | DPD-UK-only £469,876 (**+1.3%**) | All-Yodel £509,192 (**+9.8%**).
- **DECISION LEVER = DPD oversize surcharge.** Held £3.50 → DPD-only ~flat vs today, ~£39K/Q under Yodel. £24 hike lands → DPD-only ~+40% (worse than Yodel). Yodel = hedge vs the hike, not a saving.
- "Today" = expiring rates (cheap Maersk/Yodel weight deal + DPD both ending); do-nothing not real.
- Recorded in yodel_cost_engine_result.md (three-way + lever) + README headline. Committed to NFE 3_UK.
- Pending: DPD GRI/fuel; non-compat label; DPD-on-linehaul; annualize (EU-tender method).

## CLOSE — S261 (2026-06-17)

**Completed:** Built the whole UK Yodel-vs-DPD comparison on the 2026-Q1 book. OOG questions closed; [[S224_yodel-uk-volume-profile|S224]] cap bug fixed (real Large cap 160L → coverage 96.7%); standalone polars cost engine (10 tests); new Yodel offer vs current Maersk/Yodel contract ~+90% (weight→volume); truck leg (£3,620→£3,350, ~£70K/yr); DPD go-forward surcharge hikes (oversize £3.50→£24, +£103.7K/Q); three-way vs existing Q1 (DPD-only +1.3% / all-Yodel +9.8%) with the decision lever = DPD oversize negotiation; DPD coverage 100% mainland but breaches the 30% Double-Tray clause. Full doc set in `3_UK/`, committed there across 8 commits (f92c619…32b398e + the close coverage edit).

**Leaving open (resume: inventory/uk-yodel-resume__c2f15e55.md):** principal inputs — DPD GRI % + new general fuel surcharge; confirm "Non-commercial handling"=non-compatible; DPD-on-linehaul (truck count); then annualize (EU-tender method). Quest stays in-progress (multi-session).

**No pending external actions** — NFE commits done (never pushed, by rule). **Harvest:** 1 examine draft (confirm-ambiguous-ratecard-term, anchored to the fuel −8%→16.56%→10% flip) + 1 cross-conv memory entry. **Pathspec note:** NFE work is a separate repo (committed there); brain commit scoped to jebrim namespace + comms.

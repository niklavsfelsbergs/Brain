# Güll → no-Hermes portfolio: marginal, country split, and the density gate

> Drafted [[S228_50e52247_guell-no-hermes-portfolio-marginal|S228]] (50e52247), 2026-06-12. Answers the question deferred at [[S225_9f716f1f_guell-2.0.0-build|S225]]: *does adding Güll to the 5-carrier no-Hermes EU-tender portfolio give meaningful savings?* Links: [[eu-tender]] digest; resume `inventory/guell-2.0.0-build-resume__9f716f1f.md`; engine `bi-analytics-main/.../2_analysis/carriers/guell/` (guell-2.0.0).

## The answer (PAPER)

Güll's marginal to the 5-carrier no-Hermes portfolio = **+€163,897/yr** (full-year decision-set scorer, current guell-2.0.0 `scenarios.parquet`):

- `all_renewals` (no-Hermes 5) saving **€456,541** → `all_renewals_plus_guell` **€620,438** = **+€163,897** (+36% on the portfolio's own saving).

**Directional hypothesis confirmed but reframed.** Güll's marginal off the Hermes-present-6 (`all_renewals_plus_hermes` → +guell) = **+€150,617**, so removing Hermes only frees **~€13k** of Güll's lanes. Most of the gap between +€164k and the earlier "+€61k at full portfolio" is **general portfolio saturation** (AP/GLS/DHL-Express/FedEx covering lanes), not Hermes specifically. Hypothesis ("larger without Hermes") holds in sign, modest in size.

## The two-pipeline pin (load-bearing structural fact)

The "5-carrier no-Hermes portfolio" behind `final_report_no_hermes_v2/` (€976,024 base) is **NOT** a decision set in `scenarios.parquet`. Two separate pipelines:

1. **Full-year decision-set scorer** (`_decision_sets.py` + `decision_scorer.py` + full-year `data/cost_matrix/`, 31.6M rows): coarse carrier ON/OFF states, prices **UPS at 2025 invoice** (incumbent, no engine — predates the UPS cascade). This is where the +€164k marginal lives. `all_renewals` here = DHL-Paket/Maersk/DPD-PL NEW_OFFER + UPS/DBS INCUMBENT + all entrants OFF — **membership-equal** to the report's FINAL_5.
2. **Q1 report pipeline** (`annual_2026.q1_base.build_pp` + `cost_matrix_2026q1` + `routing_2026q1`): per-cell cheapest routing, prices **UPS on its 2026 engine**, DBS pinned to freight. This is what produces the €976,024 headline.

**Membership-equal ≠ numerically-equal.** The decision-set `all_renewals` saving is €456,541, not €976,024 — different baselines/conventions. The +€164k is a clean within-decision-set-scorer delta; it does **not** add onto the €976,024 report headline.

## Per-country won volume (annual)

In `all_renewals_plus_guell`, Güll wins **111,020 parcels/yr**, AT/CH only (no LI volume in 2025 population):

| Country | Won/yr | Eligible pool | Win rate | Güll cost | Avg €/parcel |
|---|---|---|---|---|---|
| AT | 79,497 | 139,246 | 57% | €424,214 | €5.34 |
| CH | 31,523 | 53,712 | 59% | €269,816 | €8.56 |
| Total | 111,020 | 192,958 | 58% | €694,030 | €6.25 |

CH ~60% dearer/parcel (line-haul + FX + CH declaration load — the mechanism that falsifies "cheaper Güll").

**Displacement donors** (where the €164k comes from): Maersk −61.8k parcels/−€351k (biggest), UPS −23.8k/−€236k, DPD-PL −15.7k/−€88k, DHL-Paket −8.8k/−€80k, DBS −849/−€101k, +96 previously-uncovered. The **DBS sliver (~€101k off 849 freight-tier parcels at ~€119 avg) looks like an eligibility artifact** — a €6/parcel AT/CH carrier shouldn't win €119 freight; sanity-check before trusting.

## PAPER vs DEFENSIBLE

PAPER **+€163,897**. DEFENSIBLE: positive but not bankable — floor plausibly **€60–120k** after: brand-new carrier (no parity validation, fixtures only), the UPS-incumbent skew (#1 above), and the understatement assumptions below.

## Assumptions that bias Güll's cost DOWN (could be understating)

Concentrated in the line-haul/allocation layer (the layer that already makes Güll ~15% dearer):

1. **Density 150 parcels/pallet** (`PARCELS_PER_PALLET`, unconfirmed Picanova-ops estimate, "AP precedent"). Divisor on **three** always-on per-parcel costs: inbound sprinter €0.80 (955÷[8×150]), outbound AT €0.16 (24.50÷150), outbound CH €0.27 (40÷150). 150→100 ≈ **+€28–55k** on the marginal. Compounding: sprinter caps at 8 pallets **OR 1,000 kg**; 1,200/sprinter assumes avg ≤0.83 kg/parcel — heavier Picanova product (canvas/frames) hits the **weight** cap first → fewer parcels → higher allocation. **The single biggest downward-bias lever, and it's a Picanova fill number, not a carrier question.** [[feedback_revalidate_borrowed_constants]] — 150 borrowed from AP precedent.
2. **FX 1.08 flat proxy** (CHF→EUR). Güll converts at **strongest-of-month** Commerzbank rate (adverse to us); 1.08 is mid-band (1.07–1.09) so strongest-of-month plausibly understates CH base ~1–2%. (Principal: 1.08 OK for now, 2026-06-12.)
3. **Outbound per-pallet rates** (24.50 AT / 40 CH) wired at offer; **Q11 still open** (flat-to-weight? fixed-2026? multi-pallet discount?). (Principal: use Güll's stated rates, 2026-06-12.)
4. **AT bulky shape un-wired** — engine charges bulky on volume-only (>150 L); shape-bulky-but-sub-150L AT parcels escape the €7. (Principal: ignore shape, 2026-06-12.)

Conservative-leaning (offsetting): FX set above v1's 1.05; CH energy default 0.10 (top of schedule).

## Contract pallet mechanics (for the logistics-manager density question)

Güll prices **per container, not per parcel** — contract fixes the container + cap + rate; Picanova ops must supply the **fill**:

- **Inbound** Szczecin→Lindau: **€955/sprinter, qty-independent**, all-in (insurance excl), cap **8 pallets / 1,000 kg**. Fixed 2026; Güll may consolidate ex-PL volumes with other customers (potential upside lever).
- **Outbound** Lindau→AT carrier / Swiss Post: **€24.50/pallet (AT)**, **€40/pallet (CH)**, all-in incl peak (insurance excl), cap **1.85 m / 300 kg**.

Question to logistics manager = realistic operating average parcels-per-pallet (AT, CH separately) + per-sprinter, and whether fill binds on volume or weight first. Full framing in [[S228_50e52247_guell-no-hermes-portfolio-marginal|S228]] quest-log.

## Feasibility: a no-Hermes + Güll report

**Small build, not a cascade.** Güll is already priced in the q1 pipeline (wins cells in `build_routing.py` emergent routing; "[HELD/provisional]" is only a print label). The no-Hermes report routes over `FINAL_5` which omits Güll → add `"guell"` to `build_stats_no_hermes.py`'s FINAL set + `FAMILY_TO_ENGINE`, re-run stats→report→deck (~1–2h, mostly verification). Report re-derives Güll's contribution in the **report's conservative basis** (UPS-on-engine, DBS-pinned) → expect **smaller than +€164k** = the management-ready defensible number. 150/pallet revisable via the one constant (re-run engine prices, not just the report).

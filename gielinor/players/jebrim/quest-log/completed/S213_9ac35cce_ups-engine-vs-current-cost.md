# S213 · UPS engine cost vs current cost (per-country + savings decomposition)

**Player:** Jebrim · **sid8:** 9ac35cce · **Born:** 2026-06-11 · **Type:** consultation/investigation (read-only over bi-analytics; brain writes only)

Principal Q&A continuing the [[S211_dcd18cfd_ups-savings-dbschenker-reroute-investigation|S211]] UPS thread: how does the 2026-offer UPS *engine* cost compare to *current* invoiced cost, ex-LPS/OML, and how does a 5% GRI on today change it — portfolio, then per-country, then by cost component. Source: `1_offers/picanova/UPS/calculation/output/replay.parquet` (155,010 Q1 parcels; 152,676 with both engine price + actual invoice). No bi-analytics writes.

## Turn log

- **T1 — engine vs current, ex-LPS/OML.** Computed off replay. Stripped oversize (`ups_lps`+`ups_oversize_disputed` vs `real_oversize`) and truck/line-haul (engine zeroes it in replay; wash). Reported all-in +8.1% and ex-LPS/OML +18.7% engine-over-current. **Both numbers later corrected (T4) — they wrongly priced the WW-ECO tail at premium air.**
- **T2 — per-country.** First per-country pass hit a bug: `real_oversize_eur`/`real_truck_eur` are **null (not 0)** on parcels with no such charge, so per-row subtraction propagated null and dropped most cost — CH showed €271 current. Caught it (portfolio reconciled but per-country didn't), refixed with `fill_null(0)`. Correct per-country: EU core (DE/IT/FR/ES/NL/AT/BE) at or below current; blowout concentrated in CH, the overseas tail (US/AU), GB, Nordics.
- **T3 — US deep-dive.** US engine €50/pcl vs €15 current = **product substitution, not a rate hike**: offer doesn't quote WW-ECO, engine falls back to Express Saver (premium air). GB ≠ US: GB priced on Standard (served), the gap is operative-tier base overprice — a negotiation item like CH. AU = same case as US.
- **T4 — the WW-ECO confirm + the correction.** Niklavs: "we just don't have the offer for UPS WW-ECO, right?" Verified from source: **confirmed with carrier 2026-06-08** (`comparison/findings.md`, `questions_for_carrier.md` Q7). The engine has a `WW-ECO-stays` rule — 6,775 parcels (US/AU/CA/CY/GG/GI/IS/JE/MT) carry `stays_current=True`, `go_forward_eur == actual`; US & AU 100% stays. **My T1/T2 numbers used `ups_total_eur` (premium-air) for the tail instead of `go_forward_eur` — inflated the engine side ~€116k.** Niklavs caught it. Corrected portfolio ex-LPS/OML: plan (go-forward) €1,069,370 vs current €1,000,913 → +6.8% raw / **+1.8% vs GRI'd today** (not +13%).
- **T5 — total excl those countries.** Offer-served book (excl WW-ECO stays): 145,901 parcels, engine €921,056 vs current €852,599 → +8.0% raw / **+2.9% GRI'd**. Excl CH+GB too: 133,103 parcels, €711,640 vs €735,333 → −3.2% raw / **−7.8% GRI'd** (~€60k/q saving). The whole residual gap is CH+GB.
- **T6 — savings decomposition (core, vs GRI'd today, −€61.5k).** Base −€44.7k (~73%; mostly the 5% GRI inflating today's base while the offer is fixed — base is only −€16k raw), residential −€11.4k (~19%), fuel −€5.9k (~10%, ~neutral structurally). CH+GB are a **pure base-rate** problem (base delta swings −€45k → +€23k when included). Lever there = negotiate the base card, not surcharges.
- **T7 — residential = €0.40 flat.** Confirmed from source: €0.40 flat per **residential shipment** (Q7 RESOLVED, carrier-confirmed). No residential flag on the row → engine spreads it at 46.3% invoice-counted incidence = €0.185/pcl expected. Separate peak Residential Surge (~€0.29/resi parcel) lives in the full-year peak layer; today's actual residential bucket also carries Jan 1–17 surge the model books to peak (no double-count) — so part of the residential "saving" is surge booked elsewhere, not all pure rate.

## Decisions / outcomes

- **Corrected headline:** on the offer-served book the 2026 UPS offer is **~break-even vs a GRI'd today** (+2.9%); strip CH+GB and it's **−7.8%** (cheaper). The wholesale "+13% more expensive" from early this session was two stacked artifacts — the unquoted WW-ECO tail priced as premium air, and CH/GB's operative-tier base. Neither is a real "the offer costs more" story.
- **Savings origin:** ~73% base rate (mostly GRI-on-today), ~19% residential (offer's €0.40 flat undercuts current residential billing), fuel neutral.
- **Action items for Niklavs (negotiation):** CH + GB operative-tier base — negotiate before signature or route away. US/AU/CA + the rest of the WW-ECO tail: no ask, they stay on current by rule.
- **Method lesson:** compare plan-vs-actual on the engine's own `go_forward_eur`, not the raw repriced `ups_total_eur` — the latter premium-air-prices the rejected/unquoted tail. → examine draft + memory.

## Pending external actions

None pending. Read-only over bi-analytics; brain-only writes committed at close.

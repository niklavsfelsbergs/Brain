# UPS 2026-offer engine cost vs current invoiced cost — corrected ([[S213_9ac35cce_ups-engine-vs-current-cost|S213]])

**What:** like-for-like comparison of the 2026 UPS offer (engine-repriced) vs current invoiced cost on our Q1 UPS book, ex-LPS/OML. Supersedes the inflated wholesale figures stated earlier in [[S213_9ac35cce_ups-engine-vs-current-cost|S213]] (see the correction note below).
**Source:** `1_offers/picanova/UPS/calculation/output/replay.parquet` — 155,010 Q1 parcels (PCS PL outbound, regular `ups` stream, ORWO excluded); 152,676 carry both an engine price and a positive invoiced actual. Cost-basis cross-checked vs `carriers/ups/CLAUDE.md` + `1_offers/.../findings.md`.

## The comparison (ex-LPS/OML, plan = `go_forward_eur`)

Both sides stripped of the oversize layer (engine `ups_lps_eur`+`ups_oversize_disputed_eur` vs `real_oversize_eur`) and of injection trucking (`real_truck_eur`; engine zeroes line-haul in the replay — a wash). Engine side uses `go_forward_eur` so the unquoted WW-ECO tail stays on current (see method note).

| Population | parcels | engine (offer) | current | current +5% GRI | vs raw today | vs GRI'd today |
|---|---|---|---|---|---|---|
| All UPS-carried (go-forward) | 152,676 | €1,069,370 | €1,000,913 | €1,050,959 | +6.8% | **+1.8%** |
| Offer-served (excl WW-ECO stays) | 145,901 | €921,056 | €852,599 | €895,229 | +8.0% | **+2.9%** |
| …also excl CH + GB | 133,103 | €711,640 | €735,333 | €772,100 | −3.2% | **−7.8%** |

**Headline:** on the book the offer actually competes for, it's ~break-even vs a GRI'd today (+2.9%); strip the two operative-tier lanes (CH+GB) and it's −7.8% (≈€60k/q cheaper), before any selective routing. The wholesale "offer is +13–19% more expensive" is an artifact — see below.

## Two artifacts that made the offer look expensive (neither real)

1. **WW-ECO tail priced as premium air.** The 2026 offer does **not** quote UPS Worldwide Economy (carrier-confirmed 2026-06-08, Q7). 6,775 parcels (US, AU, CA, CY, GG, GI, IS, JE, MT — US & AU 100%) ride WW-ECO today; the engine's `WW-ECO-stays` rule sets `stays_current=True`, `go_forward_eur == actual` — they keep the current contract. The raw replay column `ups_total_eur` instead prices them on Express Saver (premium air, ~€50/pcl on US vs €15 today), which is the "+74% vs WW-ECO, not a real switch" the findings flag. Using `ups_total_eur` over-states the engine ~€116k.
2. **CH + GB operative-tier base overprice.** Both are offer-*served* (priced on Standard) but on a base card far above today's billing (CH base €12.01 vs €7.49; GB base €23.98 vs €9.68). Real cash, but a **negotiation** item — re-open the tier before signature or route away. They are the entire residual +2.9% on the served book.

## Where the savings originate (core, vs GRI'd today, −€61.5k)

| Component | engine | current +5% GRI | Δ | share |
|---|---|---|---|---|
| Base rate | €566,945 | €611,631 | −€44.7k | ~73% |
| Residential | €24,651 | €36,068 | −€11.4k | ~19% |
| Fuel | €113,389 | €119,293 | −€5.9k | ~10% |
| Other/fees | €6,655 | €6,180 | +€0.5k | — |

- **Base ~73%** — but mostly the 5% GRI inflating *today's* base while the offer is fixed; the offer's base is only ~€16k below today's *raw* base. CH+GB are a pure base-rate problem (base delta swings −€45k → +€23k when included) → the lever there is the base card, not surcharges.
- **Residential ~19%** — the offer's flat **€0.40/residential shipment** (Q7 carrier-confirmed; engine spreads at 46.3% invoice-counted incidence = €0.185/pcl expected) undercuts current residential billing. Caveat: part of the gap is the Jan peak Residential Surge (~€0.29/resi parcel) which the model books to the full-year peak layer, not here — so not all of the residential "saving" is pure rate.
- **Fuel** — structurally neutral (~20% both sides); the −€5.9k is just GRI on today's fuel.

## Method note — compare on `go_forward_eur`, not `ups_total_eur`

When comparing the offer-plan against current actuals, use the engine's own **decision/go-forward column** (`go_forward_eur` = `ups_total` on the switch book, `= actual` on the stays book), **not** the raw repriced `ups_total_eur`. The raw column premium-air-prices the rejected/unquoted tail and inflates the engine wholesale. This was the [[S213_9ac35cce_ups-engine-vs-current-cost|S213]] error Niklavs caught. See [[2026-06-11-go-forward-not-raw-reprice-when-comparing-plan-vs-actual]] (examine).

## Cross-refs

- Supersedes the inflated wholesale figures stated earlier in this same session.
- CH/GB parked items: `ups-cascade-resume__9399f067`, `carriers/ups/CLAUDE.md` *The lever*.
- [[S211_dcd18cfd_ups-savings-dbschenker-reroute-investigation|S211]] zV→UPS economics: [[2026-06-11-zv-dbschenker-ups-reroute-economics]].
- AU WW-ECO thread also surfaced in [[S212_177f00f1_eu-tender-no-hermes-report|S212]] (jebrim-177f00f1 CLOSING): AU kept on current, +€211k/yr if forced off.

# MerchOne US — 2025 gift-holiday volume peaks

**Claim.** For the MerchOne production line (`source_system = 'PicaAPI'`), US-destination shipment volume in 2025 shows four distinct gift-driven ship-date peaks. Ranked by single-week max: **Christmas >> Mother's Day > Valentine's Day > Father's Day**. Christmas dwarfs the rest; Father's Day is the weakest of the four.

## Scope & basis (read before quoting)
- Population: `source_system = 'PicaAPI'` (the MerchOne line — a production/platform line, **not** a shop/brand; no shop named "picaapi" exists), `destination_country_code = 'US'`.
- Axis: **ship/dispatch date** via `order_produced_date` (dispatch proxy — `received_by_carrier_date` is ~53% NULL on this slice, unreliable). Gift effects therefore land in the **1–2 weeks before** the holiday, not on it.
- Grain: **weekly, ISO Monday-start.** Daily is misleading here — the line ships Mon–Sat with near-zero Saturdays and no Sunday production (sawtooth).
- **Single year (2025), no YoY** — confidence moderate, not high. 2024 PicaAPI US data exists (floor 2024-01-01) for a YoY confirmation if needed.

## The peaks (single-week max shipments, ship-date)
| Holiday | Date 2025 | Peak ship week | Peak vol | Ramp week | Lift vs ~550 calm |
|---|---|---|---|---|---|
| Christmas / Q4 | Dec 25 | wk Dec 15 | **11,881** | 5-wk build Nov 17→Dec 15 (1,702→2,410→3,759→10,688→11,881) | ~21× |
| Mother's Day | Sun May 11 | wk May 5 | **5,559** | wk Apr 28 (3,142) | ~10× |
| Valentine's Day | Fri Feb 14 | wk Feb 10 | **3,983** | wk Feb 3 (2,559) | ~7× |
| Father's Day | Sun Jun 15 | wk Jun 9 | **1,459** | wk Jun 2 (908) | ~2.6× |

- **Baseline (calm weeks):** ~450–650/wk (summer/early-autumn floor; Jan post-holiday trough ~300–340).
- **Christmas collapses hard** the week of Dec 22 (1,632) — the build is front-loaded into the two weeks before the 25th.
- **Father's Day is real but modest** — a clean isolated +56% over trailing-4-week baseline, ~1/4 the Mother's Day wave. Memorial Day (May 26) shows **no** bump (not a gift driver for this line).

## Operating takeaways
- US MerchOne volume is **gift-calendar driven**, not flat. Capacity/SLA planning should anticipate the Q4 mega-wave (~20× baseline, ~5-week ramp) and the three spring/early-summer waves in descending order Mother's > Valentine's > Father's.
- When asked "did holiday X move US volume," the ship-date-before-the-day rule and weekly grain are the honest defaults — see [[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]].

## Source
- Anchor quest: [[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]] (Father's Day pull) — full weekly series, confound checks, charts.
- Related: [[S132_32ff1025_shipping-savings-routing-optimization|S132]] (the Picanova / MerchOne population gate this builds on).
- Data: `shipping-agent/workbench/analysis/picaapi-us-fathers-day-2025/data/weekly_volume.csv` (52 weekly rows, full 2025).

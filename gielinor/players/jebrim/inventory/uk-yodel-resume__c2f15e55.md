---
quest: S261_uk-yodel-oog-cap-correction
sid8: c2f15e55
ts: 2026-06-17 18:30
open_dep: principal inputs — DPD GRI % + DPD new general fuel surcharge; confirm "Non-commercial handling"=non-compatible; DPD-on-linehaul (truck count)
---

# UK Yodel (Maersk) vs DPD UK — resume

**Status:** in-progress (analysis substantially done; decision gated on principal inputs + negotiation outcomes).

**Where we are:** Built the full UK comparison on the 2026-Q1 book. The decision pivots on **one lever — DPD's oversize surcharge.** All findings recorded in `bi-analytics-main/NFE/projects/2_EU_tender_2026/3_UK/` and committed there.

## The picture (Q1, mainland 93,480, offshore excluded, GBP, with trucks; any move drops linehaul £3,620→£3,350)
- **Existing today: £463,940.**
- **DPD-UK-only (surcharges held current): £469,876 → +1.3%** (≈ same as today).
- **All-Yodel (Maersk): £509,192 → +9.8%.**
- DPD-only ~£39K/Q cheaper than Yodel.
- **Lever:** if DPD's oversize £3.50→£24 hike lands (9,027 mainland oversize, +~£185K/Q) → DPD-only ~+40%, worse than Yodel. So: win the negotiation → stay on DPD (~flat); lose → Yodel +10% is the capped hedge.

## Key facts (all in 3_UK docs)
- Yodel offer: tiers by VOLUME (caps 19/100/160 L), base £1.99/£2.39/£3.69 + 10% fuel (18% published − 8pp) + OOG £15/£50. Engine: `2_analysis/yodel_engine/` (10 tests pass).
- New Yodel vs current Maersk/Yodel contract = ~+90% (weight→volume repricing; our long-flat canvas).
- Coverage: Yodel + DPD both physically take 100% of mainland; both profiles breach a clause (Yodel volume axis; DPD 39.7% Double-Tray vs 30% cap).
- Truck: GB linehaul = `fact_truck_charges` lane `UK DHL Freight`; £3,620 now → £3,350 on move; ~260 trucks/yr.
- DPD surcharge actuals (Q1): oversize 4,948 (10.6%), non-compat 885 (1.9%); hike impact +£103,745/Q.

## Next concrete steps (need principal)
1. **DPD GRI % + new general fuel surcharge** → raise the STAY (DPD) number; re-run the three-way.
2. Confirm DPD invoice label **"Non-commercial handling charge" = the non-compatible** they're hiking to £7.50.
3. **DPD-on-linehaul:** do DPD UK parcels ride the PL→UK linehaul today, or collect domestically? (decides whether a move adds trucks.)
4. Then **annualize** (EU-tender method: Q1 × per-country 2025 seasonal profile, ~×4.8, peak-only).
5. Optional: parquet replay of the Python engine vs the SQL headline (validate to the cent).

## Files to read first
- `3_UK/README.md` (status + headline + decision lever)
- `3_UK/2_analysis/yodel_cost_engine_result.md` (engine headline, new-vs-current, Q1 waterfall, three-way + lever)
- `3_UK/2_analysis/dpd_uk_goforward_surcharges.md` (DPD surcharge thresholds, incidence, hike impact, coverage/Double-Tray)
- `3_UK/2_analysis/uk_truck_linehaul_cost.md` (truck leg)
- `3_UK/1_offers/Maersk/offer_summary/yodel_rate_card.md` (deterministic spec)

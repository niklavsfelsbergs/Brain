---
quest: S369_uk-maersk-revenue-loss-100pct
sid8: 997395cd
ts: 2026-06-25 00:00
open_dep: none (number LOCKED; analysis complete -- the move-side GBP 3,350 truck rate is uncontracted but that's a forward risk flag, not a blocker)
---

# Resume -- UK Maersk revenue-loss-for-100% (S369, continues S277)

## Status
done (the number is LOCKED + written to the NFE deliverable). Umbrella S277 stays in-progress.

## Where we are
**LOCKED: Maersk must lose GBP 49,054/Q = ~GBP 235K/yr** for us to carry 100% of UK mainland volume at
**0% cost increase**. Go-forward basis (today truck @GBP 3,620, move @GBP 3,350). Their loss is pure
parcel; truck is OURS and its saving (3,620->3,350 = 12,837/Q) is what lets the concession be 49,054
not 61,891. The 3 options re-sized to 49,054/Q: base -16.4% (1.66/2.00/3.09), Large -26.2% (->2.73),
OOG -97.7% (near-maxed). Structural tier-extension = the 4th option, deprioritized.

## The locked view (mainland, x4.8 annualized)
- Maersk current revenue @100% list: parcel 349,948/Q + truck 159,243 = 509,191/Q (2,444,117/yr).
- Maersk aimed revenue after cut: parcel 300,894/Q + truck 159,243 = 460,137/Q (2,208,658/yr).
- Their loss: 49,054/Q = 235,459/yr.
- Our do-nothing total (truck @3,620): 460,138/Q = 2,208,662/yr -> after-cut = flat (0%).

## Next concrete step
None required -- locked. If it reactivates: (a) confirm the move-side GBP 3,350 truck rate is
contracted before quoting Maersk a hard number (if it slips, concession rises); (b) decide which of the
3 re-sized options to lead with (OOG-only is now the weakest -- near-maxed); (c) fold offshore in if
"100%" must include it (~4,800 parcels, ~neutral).

## Files / paths to read first
- `bi-analytics-main/NFE/.../3_UK/2_analysis/yodel_negotiation_levers.md` -- the LOCKED section (THE deliverable)
- `3_UK/2_analysis/yodel_cost_engine_result.md` (three-way) + `uk_truck_linehaul_cost.md` (truck rates)
- quest-log `S369_997395cd_uk-maersk-revenue-loss-100pct.md` (turn arc + the two corrections)
- prior resume `uk-yodel-negotiation-levers-resume__47bed7aa.md` (S277/S282 red-team open actions)

## Reproduce notes
- All figures from the committed engine docs (no mart pull this session). Mainland scope (93,480 parcels).
- Cost basis: parcel = ex-truck; truck = the PL->UK DHL Freight leg (we pay, separate from Maersk).
- x4.8 = EU-tender seasonal annualization; do NOT use a naive x4.

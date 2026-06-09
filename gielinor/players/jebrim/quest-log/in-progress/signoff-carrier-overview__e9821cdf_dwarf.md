# S186 — Sign-off recon: Carrier Overview v2 (carrier_overview_v2)

**Role:** Jebrim dwarf, READ-ONLY sign-off (find drift, don't fix).
**Date:** 2026-06-09
**Target:** `carrier_overview_v2/carrier_overview.html` + `exec_brief.html`
**Repo:** `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carrier_overview_v2`

## Ground-truth sources (from build_report.py)

Report loads (build_report.py:85-87):
- `_data/competitive_summary.parquet` — 52 material segments, mean-winner per cell (drives the segment map + KPIs)
- `_data/competitive_rows.parquet` — per-carrier per-cell contenders (within-10%, gaps)
- `_data/segments.parquet` — volume, BOOK_FY=2,875,235

Carrier-page **prose** comes from `sections/<slug>.md` (hand-written, regenerated from `_data/hands/<slug>_card.md`). EXEC two-liners are **hardcoded** in build_report.py `EXEC{}` dict.

**Critical timeline (mtimes):** parquets rebuilt **18:15**, HTML built **18:30** (HTML reflects new parquets — good). But hands cards are **stale (14:41, == git HEAD)** and several sections were touched 18:29-18:30 but their **win-count numbers were not re-derived**. Parquets are **untracked/gitignored** — so `git status` shows clean parquets and only the cards/HTML as modified; the parquet drift is invisible to git.

## The headline issue: "zero drift on the other 9" is FALSE

The rebuild that inserted `dpd_pl_current` as a full grid competitor **moved the mean-winner counts of 4 of the other 9 carriers**. Card-stated wins (stale) vs rebuilt-parquet wins:

| carrier | card wins | parquet wins | delta |
|---|---|---|---|
| dhl_paket | 11 | **7** | −4 |
| gls | 5 | **2** | −3 |
| guell | 10 | **9** | −1 |
| dpd_pl (declined tender) | 7 | **0** | −7 (taken by dpd_pl_current — intended) |
| fedex | 1 | **0** | −1 |
| maersk | 14 | 14 | 0 |
| hermes | 3 | 3 | 0 |
| austrian_post | 0 | 0 | 0 |
| dhl_express | 1 | 1 | 0 |

Winner total sums to 52 (dpd_pl_current 16 + maersk 14 + guell 9 + dhl_paket 7 + hermes 3 + gls 2 + dhl_express 1). Internal consistency of the parquet itself is clean (0 mismatches: every summ.winner == lowest-mean contender in rows). The drift is **prose-vs-data**, not data-vs-data.

## DRIFT table (rendered-HTML claim / report value / parquet truth)

| Claim (location) | Report says | Parquet truth | Verdict |
|---|---|---|---|
| dpd_pl_current #1 winner | **16/52** | 16 | **MATCH** |
| dpd_pl_current "7 off its declined sibling" | 7 | 7 (declined dpd_pl is runner-up on exactly those 7 cells — Benelux ≤1/1-2 std, 1-2/2-5/5-10 sperrgut, Nordics ≤1 std/5-10 sperrgut) | **MATCH** |
| dpd_pl_current mean €/parcel per cell | (16 cells) | all match summ.winner_mean | **MATCH** |
| fedex "per-parcel cheapest on **9** segments" (EXEC hardcode + sections/fedex.md ×3 + fedex_card.md) | 9 | **7** (cheapest_modal==fedex). dpd_pl_current stole 3 cheapest cells: FR Bulky 2-5, Nordics Std 1-2, Nordics Bulky 1-2 | **DRIFT** |
| fedex "WINS 1 / cheapest-not-winner 8" (fedex_card.md) | 1 win + 8 | 0 wins + 7 cheapest-not-winner (its 1 "win" FR Bulky 1-2 is now won by dpd_pl_current) | **DRIFT** |
| dhl_paket "wins **10 segments**" (sections/dhl_paket.md:16) | 10 | **7** | **DRIFT** |
| dhl_paket EXEC "widest coverage 98%" | 98% | not recomputed (coverage source not in loaded parquets; card-level) | unverified |
| gls "**Five** outright segment wins" (sections/gls.md:17) | 5 | **2** (its own [[S178_09c2d809_dpd-pl-current-engine|S178]] note admits dpd_pl_current took the FR/DE Bulky slices, but the "Five" headline wasn't decremented) | **DRIFT** |
| KPI "Decisive dim cliff **20.4%** Bulky" (overview) | 20.4% | 21.5% on the *material-segment* volume (sperrgut 20.9% + oversize 0.5%). 20.4% is the methodology's full-population sperrgut figure (method-card states "20.4%") — measured on a different denominator, not necessarily wrong | NOTE (denominator mismatch, likely intended) |
| KPI "96% <5 kg" | 96% | 95.8% | MATCH (rounds) |
| KPI vs-today "beats 36/46, fails 10, ~9% of book, lanes CH/FR/IT/Nordics/ROW" | computed live in build_full() | 36/46, 10 fails, 9%, same lanes | **MATCH** (live-computed, not hardcoded) |
| dpd_pl_current routing "~89k parcels / ~27.6k cross-carrier / 65,759 base" | 89k / 27.6k / 65,759 | routing_stats.json dpd_pl=88,985 | MATCH |

**Root cause (single):** the cost-matrix + competitive rebuild that added `dpd_pl_current` regenerated the parquets and the HTML segment map (both correct at 18:15/18:30), but the **per-carrier prose win/cheapest counts** (hands cards + the headline numbers in sections/dhl_paket, sections/gls, sections/fedex, and the hardcoded fedex EXEC line) were **not re-derived** from the new parquet. The segment-map table (parquet-driven) is right; the carrier-page narrative that quotes a total win-count is stale. Same class as the [[S180_4766eb11_dpd-current-report-refresh|S180]] "derived-report prose drifts from data" beat.

## Cross-report consistency — PASS

`routing_2026q1/routing_stats.json`: saving **€377,471 / 12.77%**, dpd_pl **88,985**, ups **29,781** — all match the brief's expected values exactly. The carrier_overview report does not render a portfolio saving headline (it's the segment-competitive view, not the routing report), so no headline to disagree; the dpd_pl_current routing references (89k/27.6k) are consistent with routing_stats. No disagreement found.

## Caveat verdicts

- **(a) FR-floor caveat — PRESENT.** Rendered dpd_pl_current page: "the engine over-prices FR vs DPD's own Chronopost actuals €4.37, so any FR-DPD number here is conservative." Plus repeated "FR wins hollow vs today's Maersk." Stated clearly.
- **(b) 4-tier size vocab — ABSENT (expected per [[S182_e3648d0d_routing-report-size-tiers|S182]] open follow-up).** Data dim_class vocab is `std / sperrgut / oversize` (the old binary + oversize), NOT the new 4-tier `small/standard/large/oversize`. Confirmed absent. (Incidental "small/large" strings in the HTML are cost-structure prose, not segment classes.) Propagation to this report is still the open follow-up [[S182_e3648d0d_routing-report-size-tiers|S182]] flagged.

## Bottom line

Segment map + winner matrix (parquet-driven) are clean and the dpd_pl_current numbers (16/52, 7-off-sibling) verify exactly; cross-report and FR-floor caveat pass. **But the "zero drift on the other 9" claim is false** — 4 carriers' stated win counts in the carrier-page prose (dhl_paket 10→7, gls 5→2, guell 10→9, fedex 9→7 cheapest) drifted because the cards/sections weren't re-derived after the dpd_pl_current rebuild. NOT-READY-TO-COMMIT until the four prose counts are reconciled to the parquet.

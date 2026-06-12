---
quest: S225_guell-2.0.0-build
sid8: 9f716f1f
ts: 2026-06-12 11:20
open_dep: bi-analytics edits uncommitted (await Niklavs commit go); no-Hermes+Güll report variant = next build (S228 answered the marginal)
status: build SHIPPED + portfolio-fit ANSWERED (S228); report-variant build queued

note (S228, 2026-06-12): the deferred no-Hermes+Güll question is ANSWERED — see
quest-log/in-progress/S228_50e52247_* + bank/drafts/notes/projects/2026-06-12-guell-no-hermes-marginal-and-density-gate.md.
---

## ANSWERED S228 — Güll → no-Hermes marginal

**+€163,897/yr PAPER** (`all_renewals` €456,541 → `all_renewals_plus_guell` €620,438, full-year decision-set scorer). Per-country won: AT 79,497 + CH 31,523 = 111,020/yr. Hypothesis confirmed in sign (off Hermes-present-6 = +€150,617, so Hermes itself frees only ~€13k; rest is saturation). DEFENSIBLE floor ~€60–120k. Key structural catch: the €976,024 report is a DIFFERENT pipeline (q1 routing) from the decision-set `all_renewals` — membership-equal, not numerically-equal; the +€164k does NOT add onto €976,024. Full detail in the bank draft.

## NEXT SESSION — build the no-Hermes + Güll report variant (recommended)

Small build, NOT a cascade. Güll is already priced in the q1 pipeline (wins cells in `routing_2026q1/build_routing.py` emergent routing; "[HELD/provisional]" is only a print label). Steps:
- Add `"guell"` to `final_report_no_hermes/build_stats_no_hermes.py` FINAL set (FINAL_5 → +guell) + `FAMILY_TO_ENGINE` service map; re-run build-stats → report → deck (~1–2h, mostly verification: headline reconcile + deck regen). Build it as a standalone variant BESIDE the 5-carrier report (5-carrier vs 5+Güll, same conservative basis).
- Expect the report's Güll number < +€164k (conservative basis: UPS-on-engine, DBS-pinned) = the management-ready figure.
- Flag **150 parcels/pallet** on the page as a working assumption. Revising later = edit `carriers/guell/constants.py` `PARCELS_PER_PALLET` + regenerate Güll's prices + re-run (NOT just the report — density is baked into per-parcel cost).

### Gating data item (the one thing that firms the marginal)
Logistics-manager **parcels-per-pallet (AT, CH separately) + per-sprinter fill**, and whether fill binds on volume or weight first. Question framed in the S228 quest-log / chat. ~€40k-per-50-parcels sensitivity. Also: Commerzbank strongest-of-month FX pull (non-blocking).

### Principal calls locked S228 (already in guell-2.0.0, no rebuild)
FX 1.08 keep · ignore AT bulky shape · use Güll's stated outbound per-pallet rates (24.50 AT / 40 CH).


# Resume — guell-2.0.0 build + EU-tender portfolio fit

**Where we are:** `guell-2.0.0` built per PLAN §B.21 and the portfolio-fit question answered. All engine + scoring work done; only the `bias_table.md` markdown write + gielinor quest-log trace remain. Survived two laptop crashes mid-session — all artifacts confirmed intact on disk after each.

**Repo:** `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/`.

## Done (all on disk, verified post-crash)
- Engine `carriers/guell/` → **guell-2.0.0**, 19/19 fixtures pass. New: per-month CH energy (`CH_ENERGY_CHF_BY_YM`) + per-month FX mechanism (`CHF_TO_EUR_BY_YM`, **flagged 1.08 proxy** — reply gave the mechanism not the values), 4 new line-haul surcharges (inbound sprinter 955÷1200≈0.80, line_haul_at 24.50÷150, line_haul_ch 40÷150, ch_declaration 40÷800), new `at_oversize` service (45 EUR 2nd-carrier recovery, ~4k/yr, requires `shop_order_created_date`), fuel 0.2727→0.15 on base+B2C+bulky, Maut 0.30→0.32, PEAK=0.
- Cost matrix rebuilt (`data/cost_matrix/`, 31.6M rows, 2025 full-year, all guell-2.0.0).
- `decision_scorer.py` re-run → `data/scenarios.parquet`.
- `decision_report/decision_report.html` regenerated (clean, 0 stale guell strings). **Also edited `report.py`:** removed `guell` from `HELD_ENGINES` (now rebuilt → trustworthy), rewrote the Güll per-carrier verdict + Q11/Q7 open-items row + dropped Güll from held-engine prose lists.
- `docs/PLAN.md` §B.21 → `[x]` closed with summary.
- `carriers/guell/CLAUDE.md` → version-history 2.0.0 entry + surcharges table updated.
- `_refresh_bias_table.py` repointed to `load_cost_matrix()` (legacy single file was stale).

## Remaining
1. **`bias_table.md` update** — `_refresh_bias_table.py` was re-running in background (job `bf9tpu5xd`, output `data/_bias_refresh_run.log`); on completion, lift the Güll row + portfolio + header (date/basis=2025-full-year/guell-2.0.0) into `decision_report/bias_table.md`.
2. **gielinor quest-log trace** for S-this-session + mini-respawn close.
3. **Optional:** Round-2 Q11 follow-up already drafted at `1_offers/picanova/Güll/questions_round2.md`; Commerzbank strongest-CHF FX-value pull still open (non-blocking). bi-analytics doc edits are UNCOMMITTED (separate work repo — Niklavs gives the commit go).

## THE ANSWER (read off the regenerated scorer)
**Premise "cheaper Güll" is FALSE.** Clean v1→v2 engine isolation (same full-year pop, 2.875M ships): v1 €1,103,316 → v2 €1,434,117 = **+30%** (+€330.8k), **like-for-like +14.5%** excl the new recovery tail. Per-parcel CH PostPac €7.08→€8.37 (+18%), AT €4.33→€4.97 (+15%). The confirmed line-haul (inbound €0.80 + outbound €0.16-0.27 + decl €0.05 + FX +3%) OUTWEIGHS the favourable fuel (27.27%→15%) / Maut / energy cuts. DECISIONS.md 2026-05-19 predicted exactly this ("CH saving collapses once both legs wired").

Verdict = **(c) HOLD** — Güll stays a positive-but-modest AT/CH complement, value ~35% smaller than the over-priced v1 suggested:
- Within-matrix marginal (clean): Güll adds **+€163,897** to `all_renewals` (apparent ~€255k before, on v1 + a stale multi-engine matrix).
- (a) strengthen `renew_maersk_plus_guell`? Claws +€186k back vs `renew_maersk` alone but set stays **−€629k** (Maersk-alone is the value-destroyer; Güll can't rescue it).
- (b) unlock retiring an AT/CH carrier? **Displaces Austrian Post** (Güll > AP by €105k; AP adds only €22k on top of Güll). Does NOT unlock GLS/DPD-PL CH-leg retirement — Güll's CH got *more* expensive, a weaker CH substitute now.
- Appears in every top-8 portfolio; +€61k at full portfolio. Minimum-disruption leader stays `renew_maersk_plus_hermes`.

**Caveat front-and-centre:** brand-new carrier — no parity validation, fixtures only; output carries higher uncertainty than Maersk/DHL Paket where Q1 actuals validate. FX values + densities + Q11 outbound are flagged working assumptions.

**Confound noted:** raw before/after scenario *absolutes* shifted partly because the whole 12-engine matrix refreshed to current code (Maersk 3.2.0, Hermes 2.2.0, UPS cascade) — so the clean Güll-attributable signal is the **within-matrix marginal + the per-parcel engine isolation**, not the raw scenario delta.

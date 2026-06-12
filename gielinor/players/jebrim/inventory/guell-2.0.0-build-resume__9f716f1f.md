---
quest: S225_guell-2.0.0-build
sid8: 9f716f1f
ts: 2026-06-12 11:20
open_dep: bi-analytics edits uncommitted (await Niklavs commit go) + no-Hermes-5-carrier-+Güll investigation queued next session
status: build SHIPPED + answered; next-session investigation queued
---

## NEXT SESSION — the question Niklavs actually wants

**Does adding Güll to the 5-carrier NO-HERMES portfolio give meaningful savings?** (deferred from this session, his words.)
- The "no-hermes" portfolio is the basis of `final_report_no_hermes_v2/` (€976,024 base, standalone "Carrier Recommendation"). Pin the exact 5-carrier decision-set composition from `_decision_sets.py` / `scenarios.parquet` first (don't guess it).
- Compute Güll's MARGINAL = (no-hermes-5-carrier + Güll) − (no-hermes-5-carrier), on the current guell-2.0.0 matrix (within-matrix, clean). Read it off `data/scenarios.parquet` if the set is enumerated, else add the variant to `_decision_sets.py` + re-score.
- **Directional hypothesis (verify, don't assume):** Güll's marginal should be LARGER without Hermes than the +€61k it added to the Hermes-containing full portfolio — Hermes was covering AT/CH cells Güll competes for; removing it frees lanes. Whether that clears "meaningful" (vs the ~€61-164k Hermes-present range) is the compute.
- Same caveats carry: brand-new carrier (no parity), flagged FX/density/Q11 assumptions; report PAPER vs DEFENSIBLE.


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

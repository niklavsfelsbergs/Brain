# [[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]] D2 — Alert / Issue Detection Statistics Review

**Scope.** Read-only technical + mathematical review of the alert/issue detection engine in
`bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/` (branch `shipping-mart-cutover`).
Covered: `pipeline.py` detection paths (constants, `compute_corridor_costs` rate-spike engine,
`_compute_shifts`/`compute_layer2`/`compute_carrier_shifts`/`compute_product_shifts`, `_detect_creep`
CUSUM, `_detect_volume_anomaly`, `_detect_corridor_changes`, `compute_deviations`, `compute_trends`,
`_build_alerts`, the full issue-construction stack `_build_issues` / `_build_single_issue` / `_drift_monitor`
/ `_suppress_parents` / `_suppress_creep_with_rate_spike` / `_merge_active_duplicates`, and the
frozen-baseline override in `main()`), plus `src/lib/alerts.ts`, `src/lib/shifts.ts` and their tests,
`tests/test_creep.py`, and `tests/test_pipeline.py`. Roughly 1,600 of pipeline.py's 3,753 lines are in
scope (the detection half); cost-column derivation / buckets / quotas / tiers were left to the other dwarf.
**Confidence: medium-high.** Logic traced statically end-to-end; the items tagged *verify-with-data* need a
pipeline run to confirm magnitude/frequency. Did not execute anything.

Constants verified against the brief (pipeline.py:63-100): `MIN_ABS_CHANGE_EUR=0.20`, `MIN_PCT_CHANGE=10`,
`ALERT_MIN_VOL=30`, `ALERT_NEW_CORRIDOR_MIN_VOL=50`, `ALERT_CREEP_WEEKS=8`/`_LONG=26`, `ALERT_CREEP_MIN_PCT=10`,
`ALERT_CREEP_CONSISTENCY=0.6`, `ALERT_VOLUME_ZSCORE=2.5`, `ALERT_REAL_COST_THRESHOLD=65`,
`SUPPRESSION_THRESHOLD=0.70`, `DRIFT_MONTHS=3`, `MIN_DRIFT_IMPACT=1000`, gap `<= 8` days, p99.5 outlier,
vol-anomaly medium at `|z|>=3.5`. All present and matching.

---

## Critical

### C1. `_merge_active_duplicates` double-counts cumulative impact for rate_spike issues `[MATH]`
`pipeline.py:3356` (merge) ⨯ `pipeline.py:2785-2796` (per-island recompute)

When a rate_spike issue is split into two active islands by gap-and-island (the rolling baseline briefly
absorbed the spike, so the alert went quiet for a week, then refired), `_merge_active_duplicates` sums the
two islands' `cumulative_impact_eur` (`base["cumulative_impact_eur"] = sum(r["cumulative_impact_eur"] for r in rows)`).
But for rate_spike, each island's impact was computed in `_build_single_issue` by summing **all covered weeks
from that island's `issue_start` to the global `latest_trends_week`** (lines 2786-2790 — upper bound is
`latest_trends_week or issue_end`, and `latest_trends_week` is the same global value for both islands).
Island 1 starts earlier and its window therefore *fully contains* island 2's window. Summing them re-adds
every week island 2 covers (and the gap weeks) a second time.

Why it matters: the headline "cumulative_impact_eur" for any rate_spike that flickered off-and-on is
inflated — sometimes nearly doubled. This is the number that ranks issues (sort key at line 2710) and that
analysts read as "what this issue has cost us." Over-statement here mis-prioritises the queue.

Fix: fix-now. For merged rate_spike issues, recompute cumulative impact once over the union window
`[earliest issue_start, latest_trends_week]` against a single frozen baseline, rather than summing
per-island totals. (Creep/drift islands sum genuine non-overlapping slopes, so they are fine — the bug is
specific to the rate_spike "recalculate against frozen baseline over the whole window to date" path.)
Also note the merged row keeps `frozen_baseline_cost` from the earliest island (line 3363) while the summed
impacts were each computed against *different* per-island frozen baselines — internally inconsistent even
before the overlap.

---

## High

### H1. TS `eur_impact` (dashboard) and Python `eur_impact` (alerts/issues) use different baselines `[MATH]`
`src/lib/shifts.ts:444` vs `pipeline.py:1054`

Python shift impact = `shifted_vol * (gainer_cost - baseline_avg_cost)` where `baseline_avg_cost` is the
**corridor-level weighted baseline cost** (all providers, pre-shift). The TS path first computes the same
(shifts.ts:271-274) but then `attributeFromProviders` **overwrites** it:
`eur_impact = shifted_vol * (gainer_cost - fromCost)`, where `fromCost` is the |delta|-weighted cost of the
**specific losing counterparts**. The shifts.test.ts cases lock this in (e.g. line 37-40: 100 × (6.0 − 4.0) =
200 using the loser's cost 4.0, not baseline 4.5).

Why it matters: the same shift shows one EUR impact in `issues.parquet` (corridor-baseline premium) and a
different one in the interactive Shifts tab (counterpart-cost premium). The two can diverge sharply when the
losing carriers are not representative of the corridor average. Analysts cross-checking the alert against the
drill-down see contradictory money figures.

Fix: document + decide. Pick one definition of "impact of a shift" and make both sides compute it. The
counterpart-cost version is arguably more correct ("what we'd have paid had volume stayed put") but then the
Python alert/issue impact should adopt it too.

### H2. TS `trend_confirmed` reference window differs from Python `[MATH]/[TECH]`
`src/lib/shifts.ts:221-234, 288-293` vs `pipeline.py:880-922`

`trend_confirmed = share_delta>0 AND c_share > early_baseline_max` on both sides — but `early_baseline_max`
is computed over different windows. Python: per-week max share over the **first half of the baseline periods**
(`baseline_periods_sorted[:n_early]`). TS: per-week max share over a **fixed 42-day window immediately before
baseline start** (`order_date BETWEEN baselineFrom - 42d AND baselineFrom - 1d`). Different reference periods →
the confirmed/estimated flag can disagree between the persisted issue and the dashboard view for the same
corridor.

Why it matters: `trend_confirmed` gates the shift severity cap (unconfirmed shifts capped at medium,
`_build_alerts` line 1815) and the "confirmed" badge. Divergence means a shift can read "confirmed/high" in
one surface and "estimated/medium" in the other.

Fix: verify-with-data, then align the windows. Likely the TS 42-day window was a convenience; make it the
first-half-of-baseline definition (or vice versa) so both agree.

### H3. Frozen-baseline override can freeze an issue active forever `[TECH/MATH]`
`pipeline.py:3567-3623` (load + apply override) ⨯ `pipeline.py:2876-2919` (resolution)

By design, active rate_spike/shift issues push their frozen baseline back into the next detection run so an
ongoing problem doesn't get silently absorbed by the rolling baseline. But the frozen baseline is anchored to
the pre-issue weeks and **never updates**, and there is **no maximum-active-age cap**. The only age-based
resolution (lines 2916-2919, drop after `MAX_WEEKLY_PERIODS`=26 weeks) gates on `status=="resolved"`. An issue
that stays active — because the elevated cost is the new permanent normal and never falls back within
`MIN_ABS_CHANGE_EUR`/`MIN_PCT_CHANGE` of the frozen baseline (line 2881) — is never subject to it and keeps
re-arming the override every run.

Why it matters: a one-time permanent step-change in a corridor's cost becomes a perpetual "active issue"
that can never resolve, cluttering the queue and inflating cumulative impact indefinitely (it keeps summing
weeks vs a stale baseline).

Fix: fix-now or document. Add a resolution path for "elevated but stable" (e.g. if current cost has been flat
for N weeks, re-baseline and resolve, or convert to a closed "accepted new normal" state) and/or a hard
active-age cap that forces re-baselining.
Good news on the related concerns: (a) resolved issues are excluded from the override (`status=="active" &
~suppressed`, line 3579-3581) so they cannot be resurrected; (b) within a single run the override is read from
the *prior* run's issues.parquet before this run writes its own, so no self-referential double-count.
The freeze-forever case (this finding) is the real one.

---

## Medium

### M1. Drift monitor never skips the (possibly partial) latest month `[MATH]`
`pipeline.py:3091-3095`

Comment says "Skip the most recent month if it might be partial (< 28 days...)" but the code does not skip it:
`latest_month = all_months[0]` uses the most recent month directly, and `compare_month = all_months[DRIFT_MONTHS]`.
A partial latest month (run early in a calendar month) has few shipments and a noisy `avg_cost`, distorting
`drift` and `drift_pct`. The `n_shipments >= ALERT_MIN_VOL*4` guard (line 3111) only partially mitigates —
a high-volume corridor can clear 120 shipments in the first week of a month.

Why it matters: false drift issues, or correct issues with a wrong (noisy) magnitude, around month boundaries.
Fix: fix-now — implement the documented skip (drop the latest month if it spans < ~28 days of data) or compare
trailing-30-day windows instead of calendar months.

### M2. `total_impact` for rate_spike weights by coalesced count, not real-cost count `[MATH]`
`pipeline.py:670` (impact) vs `:633-634` (n_cost vs n_real) vs `:1840` (real-coverage gate)

`avg_cost` is `mean(cost_for_routing)` (coalesced: real OR expected OR avg). `total_impact = delta * n_cost`
where `n_cost` = count of non-null `cost_for_routing` (coalesced volume). The rate_spike gate then requires
`n_real / n_all >= 65%` (line 1839-1840, using `has_cost` = real only). So a "confirmed real-cost" rate_spike's
EUR impact is multiplied by the coalesced volume (which includes expected/avg-costed shipments), not the real
volume that justified the alert.

Why it matters: rate_spike eur_impact is over-stated by the ratio of coalesced-to-real coverage. Magnitude
depends on how much expected/avg padding sits in qualifying corridors — verify-with-data. Drives severity tier
(`_severity` on `total_impact`) and ranking.
Fix: verify-with-data; if material, weight `total_impact` by `n_real` for the real-cost queue, or document that
impact is intentionally on routing volume.

### M3. `low_baseline_vol` denominator differs Python vs TS `[TECH]`
`src/lib/shifts.ts:243-254` vs `pipeline.py:779-805`

Python divides baseline shipment count by `n_baseline_periods_l2` = number of **distinct baseline period_start
values actually present**. TS divides by `DATEDIFF('week', baselineFrom, baselineTo)` = nominal week span. When
baseline weeks are missing (sparse corridor), the two denominators differ, so the `< 30/week` low-vol flag
fires differently between the persisted alerts and the dashboard.
Why it matters: low_baseline_vol suppresses the alert entirely (`_build_alerts` lines 1882-1883). Divergence
means a shift suppressed in the pipeline may still surface in the UI (or vice versa). Fix: align denominators.

### M4. Volume-drop anomalies below 30 shipments are silently filtered out `[TECH]`
`pipeline.py:2087-2107` (emit) ⨯ `:2130` (global filter)

`_build_alerts` emits volume_anomaly rows with `n_shipments = latest_vol` (the current week's volume), then
applies a blanket `alerts_df.filter(n_shipments >= ALERT_MIN_VOL)` (line 2130). A genuine large volume *drop*
(z ≤ −2.5) lands the corridor at a low current volume — exactly the cases most likely to be < 30 — and gets
dropped before it can alert. The detector requires `mean_vol >= 30` (line 1743) but not `latest_vol`.
Why it matters: the system is structurally near-blind to volume collapses, the more operationally interesting
half of the anomaly signal. Fix: fix-now — exempt volume_anomaly (and verify vanished_corridor) from the
`n_shipments` floor, or floor on baseline/mean volume instead of latest.

### M5. `trend_confirmed` trivially true for providers absent in early baseline `[MATH]`
`pipeline.py:904-922`

`early_baseline_max` is filled with 0 when a provider had no rows in the early-baseline half (line 918). The
confirmation test `c_share > early_baseline_max` then reduces to `c_share > 0`, so any brand-new gainer is
auto-"confirmed." New entrants are precisely the noisiest, least-confirmable shifts.
Why it matters: over-confirmation inflates severity (removes the medium cap) and the confirmed badge for new
providers. Fix: verify-with-data; consider requiring `n_early_periods_present > 0` (already computed, line 909)
before allowing confirmation, or treating absent-baseline as "cannot confirm."

---

## Low

### L1. `BASELINE_WEEKS` constant (5) contradicts CLI help text ("default: 3") `[TECH]`
`pipeline.py:69` (`BASELINE_WEEKS = 5`) vs `:2434-2435` (argparse help "default: 3"). The effective default is 5
(no `--baseline-weeks` → constant unchanged). Stale help text; no functional bug. No baseline-window leakage —
baseline weeks are `current - 7*w` for `w in 1..N`, strictly before current (lines 124, 201). Fix: document.

### L2. `mean_dev_pct` is ratio-of-means, not mean-of-ratios `[MATH]`
`pipeline.py:1408`. `mean(deviation)/mean(expected)*100` — a volume/value-weighted portfolio deviation %, while
the sibling `pct_over_20`/`pct_under_20` are mean-of-per-shipment-ratios. Both defensible, but they answer
different questions and the `deviation_blowout` headline shows `mean_dev_pct` (line 2076). Not a bug; document
so it isn't misread as "average shipment deviated X%".

### L3. `yoy_seasonal` computed but unused in the alert path `[TECH]`
`pipeline.py:965-1132` computes `yoy_seasonal`, but `_build_alerts` only consumes `low_baseline_vol` and
`trend_confirmed` for shifts (lines 1880-1882 etc.) — `yoy_seasonal` never gates or annotates an alert. Either
dead computation or an intended suppressor that was never wired in. Fix: verify intent; wire it in or drop it.

### L4. `_detect_corridor_changes` applies min-vol to new but not vanished corridors `[TECH]`
`pipeline.py:1498-1511`. new_corridor filters `n_shipments >= ALERT_MIN_VOL`; vanished has no baseline-vol
filter (relies on the downstream global `n_shipments >= 30` floor at line 2130, where vanished's n_shipments =
baseline count). Net behaviour is OK but the asymmetry is a latent trap if the global floor is ever changed.
Fix: document or mirror the filter into the detector.

---

## Verified correct (checked and sound)

- **rate_spike trigger** = `|delta| > 0.20 AND |pct_chg| > 10%` (`flagged`, lines 696-698) + real coverage
  `>= 65%` (1840) + baseline vol `>= 30` (1844) + `total_impact > 0` (1847). Matches the brief.
- **CUSUM creep** (`_detect_creep`): plain cumulative sum of `(cost - volume_weighted_baseline_mean)` over the
  analysis weeks (1638-1644); gating uses level (`drift_pct >= 10`), consistency (`weeks_above/n_analysis >= 0.6`),
  and `vol_latest >= 30`. The two-lookback run (8w + 26w, shorter wins via `creep_seen`) is correct
  (`_build_alerts` 2022-2056). Baseline mean is correctly volume-weighted (1632). Baseline split
  `min(BASELINE_WEEKS, n_total//2)` guarantees ≥ half the window for analysis (1621).
- **Bounce-from-trough guard** (1666-1677): correct logic (skip if latest cost still below the long-term
  volume-weighted mean). Note it only fires when the corridor has `>= lookback_weeks*2` weeks of history (1673),
  so for short corridors it's inert by construction — acceptable, but see "needs data run."
- **Baseline-volume guard** (1616): `avg_baseline_vol < vol_latest*0.25` → skip. Sound.
- **Volume anomaly z-score**: `(latest - mean)/std` over baseline weeks, `std > 0` and `mean >= 30` guards,
  `|z| >= 2.5`, medium at `|z| >= 3.5` (1742-1746, 2095). Denominator and guards correct (no div-by-zero).
- **new/vanished corridor**: anti-joins, current-empty guard for vanished (1494-1511). Correct.
- **trend_confirmed (Python)** semantics (922) and **parent suppression** (`_suppress_parents`, 3245-3264):
  same-direction children only (3258-3261), threshold `children_impact >= 0.70 * parent_impact`. Correct, and
  well tested (test_pipeline.py 447-593, incl. opposite-direction and resolved-parent cases).
- **creep ⊥ rate_spike suppression** (`_suppress_creep_with_rate_spike`, 3278-3308): correct corridor match.
- **drift monitor**: `compare_month = all_months[DRIFT_MONTHS]` is exactly 3 months back (descending sort);
  only un-covered corridors (3109), real coverage ≥ 65% (3118), `drift >= 0.30 AND drift_pct >= 5` (3125),
  per-month cumulative `sum((avg_cost - baseline)*n)` (3138-3142). Math sound; well tested (784-1009).
- **gap-and-island** (2633-2646): `gap_days <= 8` correctly groups consecutive weeks into one island.
- **issue id / key**: `_issue_id` = sha256(`key|issue_start`)[:16] — deterministic, collision-safe across
  distinct starts; product included in key only for routing/product shifts (2530-2531). No resurrection of
  resolved issues (new outbreak → new issue_start → new id).
- **confidence_level**: "confirmed" iff key ever hit the confirmed queue (`confirmed_keys`, 2603-2606, 2742).
  Correct; confirmed queue is gated to corridors with ≥ 65% weekly real coverage (`_corridor_real_coverage`,
  1753-1773 + `eligible_corridors`, 3646-3651).
- **frozen-baseline override read ordering**: prior issues read before this run writes (no intra-run self-ref);
  applied only at i==0 / latest period (3619-3623). Carrier override keyed on `_ALL_` matches the carrier dim
  (1315 ↔ 3594). Correct.
- **YoY reference** uses 364 days = 52 weeks, preserving weekday alignment (966-967). Correct.
- **`str.split(" | ")`** in `_explode_products` (1201) is a literal separator in Polars — correct, not regex.
- **No baseline leakage**: rate_spike baseline excludes current period; creep baseline is the head of the
  lookback window, current is the tail — no overlap.

---

## Needs a data run to confirm

1. **C1 magnitude** — how often rate_spike issues actually split into ≥2 active islands and get merged, and the
   resulting impact inflation. Inspect issues.parquet for merged rate_spikes (`weeks_active` spanning a gap).
2. **H1/H2/M3 divergence** — run a corridor through both the Python issue build and the TS `computeShifts`/
   `attributeFromProviders` and diff `eur_impact`, `trend_confirmed`, `low_baseline_vol`.
3. **H3 freeze-forever** — count active issues whose `issue_start` is > ~12-16 weeks before the latest week and
   whose current cost has been flat (not falling toward frozen baseline). Confirms perpetual-active issues exist.
4. **M2** — distribution of `n_cost`/`n_real` ratio on qualifying rate_spike corridors → the impact overstatement.
5. **M4** — are there real volume-drop anomalies (z ≤ −2.5) with `latest_vol < 30` being filtered at line 2130?
6. **M5** — count gainers flagged `trend_confirmed=true` that had zero early-baseline presence.
7. **Bounce-from-trough coverage** — fraction of creep candidates with < `lookback*2` weeks of history (guard
   inert): for the 26w run that needs 52 weeks; with a 6-month framework default the long-window guard may
   essentially never fire.

## Test-coverage gaps noted
- `tests/test_creep.py` covers consistency, pct floor, low-vol, reversal, schema, multi-corridor — but **not**
  the bounce-from-trough guard (1666-1677) nor the baseline-volume-25% guard (1616).
- `_merge_active_duplicates` tests (test_pipeline.py 604-781) assert the merge *mechanics* (sum of pre-set
  impacts) but use synthetic pre-computed impacts, so they do **not** exercise the C1 overlapping-window
  double-count.
- `shifts.test.ts` covers only `attributeFromProviders`; the SQL shift computation, `trend_confirmed`, and
  `low_baseline_vol` (H1/H2/M3 surfaces) are untested on the TS side.
- `alerts.test.ts` covers only `clamp`/`priorityBand`/`actionPlan` (presentation), not detection.
- No test asserts the frozen-baseline override end-to-end (H3) or the volume-drop filtering (M4).

# S076 D2 — SCM issue resolution / settle / frozen-baseline lifecycle review

**Role:** read-only review dwarf (Jebrim), SCM alert engine, branch `shipping-mart-cutover`.
**Scope:** issue resolution / settle / frozen-baseline machinery — "why does nothing clear?" — for rate_spike / creep / shift. `deviation_blowout` + `drift` never-resolving owned by siblings D1/D3.
**Target:** `NFE/dashboards/shipping_costs_monitoring_nextjs/pipeline.py`. Verified against `data/issues.parquet` + `data/corridor_trends_weekly.parquet` (run 2026-05-25 22:20).

---

## Empirical reframing of the two findings

**Finding #1 (29/46 active pinned at weeks_active=24) is NOT my scope.** Of the 29, **28 are `deviation_blowout` + 1 `product_shift`** — all sharing `issue_start=2025-12-08`, `issue_end=2026-05-18` (the full 24w window). deviation_blowout comes from the `deviations.parquet` builder, not `_build_single_issue`. **Hand to D1/D3.** My scope (rate_spike/creep/shift) has only 1 issue at 24w; my 14 active issues span 4–24w with no pinning pathology.

**Finding #2 (stale-active leak) IS my scope and is real and systemic.** 13 active non-suppressed issues have islands that ended 5–21 weeks before the latest data week (2026-05-18); 10 of those are rate_spike (mine). Root-caused below as BUG-1.

---

## PROVEN BUGS

### BUG-1 — `current_cost` reads the corridor's last *available* week, not the latest *period*; a vanished corridor stays "active" on a stale elevated cost

- **file:line:** `pipeline.py:2850-2857` (current_cost selection) feeding `pipeline.py:2966-2981` (status block). Settle guard `pipeline.py:2867-2873`.
- **Root cause:** `current_cost = covered.tail(1)["avg_cost"]` takes the last week of *this corridor's* trends with ≥65% coverage — **not** the current reporting period. When a corridor stops shipping, its trend series ends early but its last-known cost is frozen in. The status block (L2969-2981) compares that stale `current_cost` to `frozen_baseline_cost`; if still above baseline → `active`. The corridor vanished months ago but rides as a live cost problem forever (until `MAX_WEEKLY_PERIODS` purges it at L3013-3018, which keys off the *alert's* last period, not the trend gap).
- **Proof (issue `5a8273c0e026796c`, UK / YOD02XPECT48MEDIUMNONPOD, rate_spike):** island `issue_start=2025-12-08 .. issue_end=2025-12-29`. Stored `current_cost=7.80`, `frozen_baseline_cost=5.53` → delta +2.27 / +41% → active. Corridor's real-trend series **ends 2026-03-30** (last week n_all=10, a trickle), avg 7.80 — exactly the stored current_cost. Latest data week across all corridors is 2026-05-18, ~7 weeks later. The corridor has no May data at all; it's effectively dead but flagged active.
- **Severity:** HIGH (user impact). This is the primary "nothing clears" driver for rate_spike. 10 stale rate_spikes on the active board are corridors that already stopped or normalized; they crowd out genuinely live issues and erode trust in the active set. There's no "this corridor went quiet" resolution path.
- **Proposed fix:** gate active-status on **recency of the corridor's covered data**. If the corridor's latest covered week is more than ~1–2 periods behind the global latest period (`latest_trends_week`), the cost signal is stale → resolve (e.g. flag `stale` / `vanished`), don't keep active on a frozen elevated number. Concretely: compute `weeks_stale = (latest_trends_week - covered.tail(1).week_start)//7` alongside `current_cost`; in the cost status block require `weeks_stale <= 1` (or `<=2`) for `status="active"`, else resolve. (A vanished corridor with elevated last cost is arguably a `vanished_corridor` concern, not a live rate_spike.)
- **Confidence:** HIGH (mechanism isolated and reproduced from on-disk trend data).

### BUG-2 — `weeks_active` computed on two inconsistent bases (merged vs non-merged issues)

- **file:line:** non-merged path `pipeline.py:3077` (`((latest_trends_week - issue_start)//7)+1`, uses **global** latest week); merged path `pipeline.py:3482` (`((_end - _start)//7)+1`, uses the **island's own** `issue_end`).
- **Root cause:** `_build_single_issue` sets `weeks_active` for active issues as start→**global-latest-week** span (so an active issue always reads as "this many weeks since it started, to now"). But `_merge_active_duplicates` overwrites `weeks_active` with start→**merged-island-end** span. Issues that go through the merge therefore measure a different quantity. The two are silently mixed in the same column.
- **Proof:** `5a8273c0` (rate_spike, start 2025-12-08, island end 2025-12-29) stores `weeks_active=4` — that's the island span (start→end), the merge basis. A near-identical un-merged neighbor `51b0b9ed` (start 2025-12-15, island end 2025-12-22) stores `weeks_active=23` — the global-latest basis. Same vintage, 4w vs 23w. Across my 14 active issues, recomputing on the global basis matches the stored value only for non-merged issues; merged ones diverge by 5–18 weeks (table in run notes).
- **Severity:** MEDIUM. `weeks_active` is the divisor in the low-impact threshold filter (`avg_weekly_impact = cumulative/weeks`, L2760, and shift/vol gates L2768-2773) and is shown in headlines (`dur` at L3127). A too-small `weeks_active` inflates `avg_weekly_impact`, so a merged issue is *less* likely to be dropped by the threshold — i.e. merged stale issues are stickier on the board. Also makes the headline duration wrong.
- **Proposed fix:** pick one basis and apply it in both places. For active issues the intended semantic is start→latest-period (L3077), so the merge should recompute `weeks_active` the same way: `max(1, ((latest_trends_week - _start)//7)+1)` for active, not `_end - _start`. (Needs `latest_trends_week` threaded into `_merge_active_duplicates`, or recompute weeks_active *after* the merge in one pass.)
- **Confidence:** HIGH (both code paths read directly; divergence reproduced from the parquet).

---

## SUSPICION (needs verification)

### S-1 — Settle-to-new-normal (#5, [[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]]) rarely fires; gated out by volume collapse + a too-wide window

- **file:line:** `pipeline.py:2867-2873` (plateau detect) + `pipeline.py:2974-2979` (resolve-as-settled).
- **Observation:** Across 92 cost-type issues only **5 carry the `settled` flag**. The plateau test takes the last `BASELINE_WEEKS=5` corridor weeks and resolves only if their spread is `< MIN_ABS_CHANGE_EUR (0.20)` **or** `< MIN_PCT_CHANGE (10%)`. Two ways this misses:
  1. **Volume-collapse noise.** For vanished/thinning corridors the last 5 weeks are low-n and noisy. `5a8273c0`'s last 5 weeks swing 5.99→8.84 (spread 47.6%) purely because n_all fell to 105/60/10 — so `cost_settled=False` and BUG-1 keeps it active. A genuinely-settled-then-vanished corridor never settles because its tail is statistically unstable.
  2. **Window mismatch.** The plateau window is the last 5 weeks of *available* corridor data regardless of how stale that is — same root as BUG-1. It can "settle" on data months old, or fail to settle on noise, but never keys off the current period.
- **Why I can't fully prove it's the dominant cause:** distinguishing "should have settled but the window was too noisy" from "genuinely still volatile" requires per-corridor backtest replay, which I didn't run (read-only, no pipeline re-run). The 5/92 settled rate is suggestive, not conclusive.
- **Severity (if confirmed):** MEDIUM — settle was the [[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]] mechanism meant to stop permanent step-changes re-arming; if it under-fires, long-runners persist (compounding BUG-1).
- **Proposed direction:** make the plateau test volume-weighted (or require a minimum n per week in the window before trusting the spread), and anchor the window to the latest *period* not the latest *available* corridor week. Likely folds into the BUG-1 fix.
- **Confidence:** LOW / needs verification.

---

## On the frozen-baseline override (main, L3704-3745) — re-arming question

Checked directly: the override (`pipeline.py:3704-3745`) loads prior **active non-suppressed** issues and pushes their `frozen_baseline_cost`/`frozen_baseline_share` back as detection baselines for the latest period (i==0 only, L3756-3760). It does **not itself set status** — it only replaces the rolling baseline so an ongoing spike keeps *firing an alert* instead of being absorbed. The stale-active leak (BUG-1) is **not** caused by the override re-arming resolved issues; it's caused by the status block reading a stale `current_cost`. The override is, however, the *amplifier*: because BUG-1 keeps dead corridors "active", they re-enter `active_prior` next run and keep injecting a frozen baseline for a corridor that no longer ships — wasted overrides, and they perpetuate their own active status. Fixing BUG-1 (resolving stale corridors) drains them from `active_prior` and stops the override re-arming them. No separate override bug; it's downstream of BUG-1.

---

## Summary for triage

| ID | Title | file:line | Sev | Conf |
|----|-------|-----------|-----|------|
| BUG-1 | Stale corridor stays active on frozen elevated `current_cost` (no data-recency gate) | `pipeline.py:2850-2857` → `2966-2981` | HIGH | HIGH |
| BUG-2 | `weeks_active` inconsistent: merged uses island-end, non-merged uses global latest | `pipeline.py:3077` vs `3482` | MED | HIGH |
| S-1 | Settle (#5) under-fires — noisy low-volume tail + window anchored to last *available* not last *period* | `pipeline.py:2867-2873` / `2974-2979` | MED | LOW (needs backtest) |

**Not mine (handed to D1/D3):** the 24w-pinning (Finding #1) is 28/29 `deviation_blowout` + 1 `product_shift`, from the deviations builder, not the resolution block. drift never-resolving (`pipeline.py:3287-3299`, hardcoded `status="active"`, `weeks_active=DRIFT_MONTHS*4`) also sits outside my scope per the brief.

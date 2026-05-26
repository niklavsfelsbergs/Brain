# S076 D1 — deviation_blowout end-to-end review

**Role:** read-only review dwarf for Jebrim. Scope: `deviation_blowout` alert path in SCM pipeline (branch `shipping-mart-cutover`).
**Repo:** `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/pipeline.py` (read-only; verified against `data/*.parquet`, run 2026-05-25 22:20).
**Status:** complete. 3 confirmed bugs, 1 suspicion (upstream metric), 1 noted-input (severity, owned by D3).

---

## Root-cause chain (one mechanism drives findings 1 + 2)

`compute_deviations(df_weekly)` is called **once** (`pipeline.py:3695`), over the whole framework window (~6 months, `FRAMEWORK_MONTHS=6`). It produces ONE `deviations.parquet` row per corridor whose `total_deviation_eur` is the **sum of `(real − expected)` across the entire window** — not per-week (`_deviation_agg` L1453: `pl.col("deviation").sum()`). No period column exists in the file.

The per-period backfill loop (`pipeline.py:3747`) then calls `_build_alerts` for **every** weekly period (24 of them). Inside `_build_alerts`, the deviation_blowout block (`L2106–2132`) re-reads that same single `deviations.parquet` **every iteration** and appends an identical alert row — same `eur_impact = total_dev`, same `n_shipments` — tagged with that period's `current_period`. Result: 24 identical alert rows per corridor per queue (verified: Germany DHL2 = 48 alert rows = 24 periods × {early_warning, confirmed}, every row `eur_impact=-3,111,049`, `n_shipments=1,243,775`).

`_build_issues` dedups across queues (L2672, keeps 1 per period) → 24 identical rows → gap-and-island groups them into ONE island spanning all 24 weeks → `_build_single_issue` sums them.

---

## Bug 1 — `cumulative_impact_eur` is the full-window total multiplied by week count (≈ ×24)

- **file:line:** `pipeline.py:2961–2964` (the `else` branch of `_build_single_issue`) + the every-period re-emission at `L2106–2132` + single-shot `compute_deviations` at `L3695`.
- **Root cause:** `deviation_blowout` is in neither `_COST_ALERT_TYPES` nor `_SHIFT_ALERT_TYPES` (`L2590–2591`), so it falls to the `else` branch: `cumulative_impact = sum(r["eur_impact"] for r in island)`. Each of the 24 island rows already carries the *full-window* `total_dev` as `eur_impact`, so the sum = `total_dev × 24`. Same defect inflates `n_shipments_total = sum(n_shipments) = n × 24`.
- **Evidence (verified):** `cumulative_impact_eur == latest_weekly_impact_eur × 24` to the cent for **all 28** issues (max abs error 0.0). Germany DHL2: `total_dev = −3,111,049` → `cumulative = −74,665,176` (headline "−74.7M EUR cumulative"). `n_shipments_total = 29,850,600 = 1,243,775 × 24`. Multiple corridors land in the millions/tens-of-millions.
- **Why it misleads:** severe. The UI's primary surface presents fabricated tens-of-millions-of-EUR cumulative figures and impossible shipment counts (29.8M shipments on a corridor that shipped 1.24M). Any user trusting the "cumulative" number is off by ~24×. It also dominates the issue sort (`L2784` sorts by `abs(cumulative_impact_eur)`), pushing these fabricated figures to the top.
- **Proposed fix:** `deviation_blowout`'s `total_deviation_eur` is already a cumulative total for the window — it must NOT be summed across the per-week island. Cleanest: stop re-emitting the alert every period. Either (a) emit deviation_blowout only for the latest period (`i==0`) in the backfill loop so the island is a single row, or (b) special-case it in `_build_single_issue` to take `cumulative_impact = last["eur_impact"]` (the single window total) and `n_shipments_total = last["n_shipments"]` rather than summing. Option (b) is the smaller change and keeps the per-week rows for any future trend use. Either way `weeks_active` should reflect the deviation window, not the count of duplicate emissions (see Bug 2).
- **Confidence:** high (proven — exact ×24 arithmetic reproduced across all 28 rows).

## Bug 2 — every deviation_blowout issue is permanently active, never resolves (28/28, identical lifecycle)

- **file:line:** status block `pipeline.py:3007–3011` (the `else` branch) + `weeks_active` at `L3077`; root in the every-period re-emission (`L2106–2132`).
- **Root cause:** two layers. (1) Because the alert is re-emitted **every** week including the latest complete week, the island always touches `last["current_period"] == latest period`, so the `else` status branch (`L3009–3011`: "active if fired in the last complete week, gap ≤ 8d") always evaluates active. deviation_blowout is exempt from the settle/resolve paths — those only exist for `_COST_ALERT_TYPES` (`L2968`) and `_SHIFT_ALERT_TYPES` (`L2987`); there is no resolve logic for deviation. (2) `weeks_active` (`L3077`) for an active issue = `((latest_trends_week − issue_start)//7)+1`, and `issue_start` = first period in the island = the earliest backfilled week, so it always spans the full window → constant 24.
- **Evidence (verified):** all 28 issues `status=active`, `weeks_active=24`, `issue_start=2025-12-08`, `issue_end=2026-05-18`, `severity=medium` — identical. Zero resolved. The 28 are exactly the 192 corridors with `|total_dev| ≥ 10,000` (the MEDIUM deviation threshold, `ALERT_MEDIUM_DEVIATION=10_000` at `L79`); nothing else gates them.
- **Why it misleads:** medium severity, but it's a permanent wall of 28 never-clearing issues — the deviation alert can never signal "this got better/worse" because it has no time dimension. It's a static all-time leaderboard wearing an "alert" costume, not a monitoring signal.
- **Proposed fix:** the deviation metric needs a *recency* notion to be alertable. Compute deviation per-period (current window vs prior) instead of one all-time aggregate, OR convert deviation_blowout into a snapshot/leaderboard surface that is explicitly not an "issue" with active/resolved lifecycle. Minimal interim: if kept as-is, special-case its `weeks_active` to 1 (single-snapshot) and document that it never resolves by design. Proper fix is a per-period deviation so the settle/resolve machinery can apply. Pair with Bug 1's fix.
- **Confidence:** high (proven — uniform lifecycle across all 28; no resolve path exists in code for this type).

## Bug 3 — deviation_blowout double-counts queues are deduped but `deviations.parquet` window ≠ `deviations_summary.parquet` window (data-consistency)

- **file:line:** `compute_deviations` L1463 (uses `df_weekly`, framework-trimmed) vs `_write_deviations_summary` L2328 (uses full `df`).
- **Root cause:** `deviations.parquet` (alert source) is computed on `df_weekly` (last ~6 months, `FRAMEWORK_MONTHS` trim at `L3690`). `deviations_summary.parquet` (the `/api/deviations` UI route source) is computed on the full untrimmed `df` (2024-01-01 → 2026-05-22). The two "deviation" surfaces disagree on totals for the same corridor.
- **Evidence (verified):** Germany DHL2 — `deviations.parquet`: n=1,243,775, total_dev=−3,111,049 (matches summary restricted to `>=2025-11-01`, i.e. the framework cut). `deviations_summary.parquet` full window: n=1,382,217, sum_dev=−3,459,932. The alert headline number and the Deviations tab number for the same corridor will not match.
- **Why it misleads:** medium. A user clicking an alert through to the Deviations tab sees a different total than the alert quoted. Not catastrophic but erodes trust.
- **Proposed fix:** compute both from the same window, or document that the alert is framework-window-scoped and the tab is all-time. Lower priority than Bugs 1–2; flagging for consistency.
- **Confidence:** high (proven — windows differ by construction, numbers reproduced).

## Suspicion — the underlying deviation metric (−74% avg) may be driven by an inflated/ mismatched `expected_shipping_cost`, not a real cost gap

- **Where:** `expected_shipping_cost` upstream (mart `expected_shipping_cost_eur` + the ORWO SQL-level CASE fallback per the vocab note); `compute_deviations` L1469 computes `deviation = real − expected`.
- **Observation:** the deviation *arithmetic* is internally sane — `mean_dev_pct` (ratio of mean-real to mean-expected, L1456) tracks `total_real/total_expected − 1` closely (DHL2: −74.3% vs aggregate ratio −0.743). But the *inputs* look off: Germany DHL2 avg_real ≈ **0.87 EUR/shipment** vs avg_expected ≈ **3.37 EUR/shipment** (expected ≈ 4× real) on 1.24M shipments. A real avg of 0.87 EUR for a high-volume German domestic carrier is implausibly low, OR the expected (~3.37) is inflated. The big-negative corridors (DHL2 −74%, UPS −74%, DHL3 −83%, Austria DHL −64%) cluster around the providers the vocab note flags as carrying expected from the inline CASE fallback / coverage holes — consistent with expected-side inflation rather than a genuine 74% under-spend.
- **Why it matters:** if expected is wrong, every deviation number (and the whole Deviations tab) is anchored to a bad denominator — the alert isn't just multiplied wrong (Bug 1), its base metric may be meaningless for these corridors.
- **Proposed next step:** needs verification at the mart/row grain — pull a sample of Germany DHL2 rows from `processed/*.parquet` (or the mart) and inspect `real_shipping_cost_eur` vs `expected_shipping_cost_eur` per shipment + the source_system / ORWO-fallback split. Could not prove from the four output parquets alone (they're already aggregated past the per-row real/expected).
- **Confidence:** med — **needs verification.** The metric arithmetic is proven sane; the *input* plausibility is a strong suspicion, not proven.

## Noted input (owned by D3, not re-flagged as a bug here)

- **Severity hardcoded-capped at medium:** `_severity(... is_deviation=True)` caps any deviation at medium (`L1867–1868`), so even DHL2's −3.1M window deviation reads "medium." Flagging the input per brief; cross-type severity calibration is D3's call.

---

## Files touched
- Read-only review. No edits to bi-analytics. No scratch files left in that repo.
- Verification done via inline `python -c` against `data/{deviations,deviations_summary,issues,alerts}.parquet`.

## Hand-off summary for principal triage
- **Bugs 1 + 2 share one root** (single-shot full-window `compute_deviations` re-emitted every period; deviation_blowout not in the cost/shift type sets so it gets the naive sum + the catch-all "active if recent" status). Fix them together: stop summing the window total across the island, and give deviation a recency/lifecycle notion (or reclassify it as a snapshot, not an issue).
- **Bug 3** is a window-mismatch between the two deviation surfaces — smaller, consistency-only.
- **Suspicion** (inflated expected) is the one that needs ground-truth at row grain before any fix; if true it undermines the metric independent of Bugs 1–3.

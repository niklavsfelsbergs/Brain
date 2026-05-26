# S076 d3 — SCM alert engine: drift monitor + severity calibration review

**Role:** read-only review dwarf (Jebrim). **Date:** 2026-05-26.
**System:** `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/pipeline.py` (branch `shipping-mart-cutover`).
**Verified against:** `data/issues.parquet` (191 issues), `data/deviations.parquet`. Empirical claims in the brief all reproduced.
**Scope:** A = drift monitor (`_drift_monitor`, L3149); B = severity calibration across all alert types (`_severity`, L1845 + all call sites).
**Out of scope / not re-flagged:** [[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]] fixes (bucket invariant, per-costed avg, shift canonicalization, rate_spike merged-island dedup, `settled` resolution for cost types, drift partial-month skip, volume_anomaly vol-floor exemption).

---

## How `_severity` actually works (the exact basis)

`_severity(eur_impact, total_dev=0, is_shift=False, confirmed=False, new_corridor_vol=0, is_deviation=False)` (L1845):

- Tiers on `abs(eur_impact)` vs **`ALERT_HIGH_EUR=500 / ALERT_MEDIUM_EUR=100 / ALERT_LOW_EUR=10`** (below 10 → `None`, dropped).
- OR on `abs(total_dev)` vs **`ALERT_HIGH_DEVIATION=50_000 / ALERT_MEDIUM_DEVIATION=10_000`** (deviation path).
- OR `new_corridor_vol >= ALERT_NEW_CORRIDOR_MIN_VOL=50` → medium.
- **Caps:** unconfirmed shift high→medium (L1863); deviation high→medium (L1867).

**Critical:** the `eur_impact` passed in is a **single-week** figure at every cost call site, and the issue then inherits the *latest alert week's* severity, never the island's cumulative. Per call site:

| Type | Call site | Basis passed | Notes |
|---|---|---|---|
| rate_spike | L1897 | `total_impact` = `(avg_cost − avg_cost_b)·n_cost` for the **latest week** (L710) | EUR thresholds |
| creep | L2084 | `weekly_impact` (per-week) | EUR thresholds |
| carrier/routing/product_shift | L1934/1971/2009 | per-week `eur_impact`, `is_shift=True` | capped medium unless `trend_confirmed` |
| new_corridor | L2043 | `n·avg`, `new_corridor_vol=n` | medium if n≥50 |
| vanished_corridor | L2046 | hardcoded `low` | — |
| deviation_blowout | L2115 | `_severity(0, total_dev=total_dev, is_deviation=True)` | **deviation thresholds 50K/10K**, capped medium |
| volume_anomaly | L2143 | hardcoded by z-score (med if \|z\|≥3.5 else low) | — |
| drift | L3273 (inlined, NOT a `_severity` call) | `cumulative_impact` vs EUR thresholds, **no cap** | see Bug 4 |

Issue-level severity is set at **L3084 `"severity": last["severity"]`** — the *last alert row in the island*. So severity = the most recent single week's tier, regardless of how large the cumulative is. Drift is the lone exception (computes severity inline from cumulative).

---

## PROVEN BUGS

### Bug 1 — rate_spike (and creep/shift) severity keyed off latest single week, ignores cumulative

- **file:line:** `pipeline.py:1897` (basis), `pipeline.py:710` (per-week `total_impact`), `pipeline.py:3084` (`last["severity"]` inheritance).
- **Root cause:** `_severity` receives the latest week's `total_impact` only; the issue inherits the latest alert week's severity. The island's `cumulative_impact_eur` (recalculated vs the frozen baseline) is computed but never feeds severity. A sustained elevated corridor whose *most recent* week happens to be quiet reads `low`.
- **Empirical proof (issues.parquet, active rate_spikes):** severity tracks `latest_weekly_impact_eur` cleanly and is uncorrelated with cumulative:
  - cited `5a8273c0e026796c`: `low`, latest_weekly=98.0, **cumulative=6133.87**, +41% (current 7.80 vs 5.53 baseline).
  - `low` at cumulative 6134 / 1510 / 735 (latest weekly 98 / 65 / 79).
  - `medium` at cumulative 1930 with latest weekly **1954** — i.e. a *smaller cumulative* outranks the 6134 issue purely because its latest week was bigger.
- **User impact:** HIGH — under-ranks real, sustained cost problems; the dashboard's primary surface (issues) mis-sorts and mis-colors them. A 6K sustained spike buried as `low`.
- **Proposed fix:** key cost-type severity off `cumulative_impact_eur` (with a per-week tie-breaker if desired), not the latest week. Concretely: compute issue severity in `_build_single_issue` from `cumulative_impact` rather than inheriting `last["severity"]`. See unified rule set below.
- **Confidence:** HIGH (proven in data + code).

### Bug 2 — deviation_blowout capped at medium regardless of magnitude (±millions read "medium")

- **file:line:** `pipeline.py:1867` (`is_deviation` high→medium cap), call site `pipeline.py:2115`.
- **Root cause:** the `is_deviation` cap forces every deviation to medium even when `total_dev` is orders of magnitude past `ALERT_HIGH_DEVIATION`.
- **Empirical proof:** all **28/28** active deviation_blowout issues have `|impact| ≥ 50K` (would be HIGH absent the cap); range **262,896 → 74,665,176 EUR**, every one labelled `medium`.
- **User impact:** HIGH — the single largest-magnitude alert class is permanently de-emphasized; a 74.7M EUR deviation ranks equal to a 263K one and below a 2.4K drift.
- **Proposed fix:** remove or raise the deviation cap. If the cap exists because `total_dev` is noisier/lower-confidence than realized cost, replace the blanket cap with a *confidence flag* + a higher HIGH threshold for deviations (e.g. HIGH at ≥250K, the empirical floor here), not a hard medium ceiling. Needs a product call on what deviation magnitude *should* mean vs realized-cost impact.
- **Confidence:** HIGH (cap is unconditional in code; all data hits it).

### Bug 3 — drift issues never resolve; hardcoded `status="active"`, recomputed fresh every run

- **file:line:** `pipeline.py:3294` (`"status": "active"`), `_drift_monitor` L3149, integration L2733-2735, prior-issue load L3712-3743.
- **Root cause:** drift is built **after** the gap-and-island + resolution path (`_build_single_issue`) and `pl.concat`'d straight in (L2735). It therefore never runs through the active/resolved/settle logic (L2966-3011) that every other cost type uses. It is recomputed from scratch from monthly `trends` each run with `status` hardcoded `active`. The frozen-baseline override + prior-issue reload (L3712-3743) only handles `rate_spike` and shifts — drift is not read back, so there is no continuity and no resolution.
- **Empirical proof:** all 3 drift issues are `status=active`, identical fixed window `issue_start=2026-01-01 / issue_end=2026-04-01`, `weeks_active=12`. Zero drift issues are `resolved` anywhere in the 191-row file.
- **User impact:** MEDIUM — drift alerts can't clear. If a corridor's cost reverts, the drift issue silently vanishes on the next run (recomputed, no longer meets threshold) rather than showing as `resolved` — so the dashboard never tells the operator "the drift you saw has abated." Also the window can never *age*: it's always "last complete month vs 3 months prior," so a drift that started 6 months ago and is still live still reads as a fresh 3-month window.
- **Answers to brief questions:**
  - *Why hardcoded active / never run through resolution?* Architectural: drift is appended post-resolution and rebuilt per run; there's no persistence layer for it, so "active" is the only state the builder can assert.
  - *Should it resolve when drift abates?* Yes — but under the current rebuild-from-scratch design "abated" = "no longer emitted," which is silent. To get an explicit `resolved` state, drift needs the same prior-issue carry-forward the cost types have.
  - *Is the fixed 3-month window correct?* It's correct as a *detection* window but wrong as an *issue lifetime*: `issue_start`/`issue_end` are always the comparison months, so the issue never reflects how long the drift has actually persisted. `weeks_active` is hardcoded `DRIFT_MONTHS*4=12`, not measured.
- **Proposed fix (two options, principal call):**
  - *(min)* Persist drift across runs: include `drift` in the prior-issue reload, key by `drift|country|provider`, set `status=resolved` (flag `settled`/`abated`) when the current-vs-3mo-ago drift drops below `DRIFT_PCT_THRESHOLD`, and let `issue_start` stick to the first run the drift appeared (so age accrues).
  - *(min-min)* If full persistence is too heavy, at least stop hardcoding — derive `status` from whether the latest month still exceeds baseline by the threshold, and make `weeks_active` reflect actual months since first detection.
- **Confidence:** HIGH that it never resolves / is hardcoded (proven in code + data). MED on the preferred fix shape (depends on how much drift continuity the product wants).

### Bug 4 — drift severity uses cumulative with NO cap, while it's the lowest-confidence signal — making it out-rank everything

- **file:line:** `pipeline.py:3273-3280` (inlined severity block in `_drift_monitor`).
- **Root cause:** drift severity is computed inline against the EUR thresholds (`≥500 → high`) on `cumulative_impact`, and — unlike deviation and unconfirmed shifts — has **no cap**. Drift is explicitly the slow, low-confidence signal (`MIN_DRIFT_IMPACT=1000`, comment "slow, low-confidence"), yet it's the only cost type that can hit `high` on a few-K cumulative with no confirmation gate.
- **Empirical proof:** all 3 drift issues are `high` at cumulative **2,410 / 4,710 / 12,058 EUR** — out-ranking a 74.7M deviation (medium) and a 6.1K rate_spike (low). The contradiction the brief flagged.
- **User impact:** MEDIUM-HIGH — the least-confident, smallest-magnitude class sits at the top of the severity sort.
- **Proposed fix:** route drift through `_severity` (don't inline), and add a drift cap analogous to the shift/deviation caps — cap unconfirmed drift at `medium` (drift's `confidence_level` is hardcoded `"estimated"` at L3290, so it'd always cap), OR raise drift's HIGH threshold well above `ALERT_HIGH_EUR`. Fold into the unified scheme below.
- **Confidence:** HIGH.

---

## Severity incoherence — the cross-type picture (active issues)

| alert_type | severity | n | min \|cum\| | max \|cum\| |
|---|---|---|---|---|
| deviation_blowout | medium | 28 | 262,896 | **74,665,176** |
| rate_spike | high | 5 | 23,494 | 147,201 |
| rate_spike | medium | 3 | 1,930 | 11,099 |
| rate_spike | low | 3 | 735 | 6,134 |
| carrier_shift | high | 3 | 11,890 | 95,588 |
| product_shift | high | 2 | 8,497 | 86,847 |
| drift | high | 3 | 2,410 | 12,058 |
| creep | high | 3 | 862 | 4,266 |
| volume_anomaly | medium | 1 | 0 | 0 |

**Reading:** a 74.7M deviation = medium; a 6.1K rate_spike = low; a 2.4K drift = high; an 862 EUR creep = high. The three independent severity bases (per-week EUR for rate_spike/creep, capped deviation-EUR for deviations, uncapped cumulative-EUR for drift, per-week capped for shifts, z-score for volume) are mutually non-comparable. Severity is not a cross-type ranking today — it's per-type and incoherent across types.

---

## Proposed coherent severity scheme (concrete)

The root design flaw: severity mixes **per-week** and **cumulative** EUR, mixes **realized** vs **modelled-deviation** EUR, and applies hard caps to some types but not others. Make severity a single, comparable **realized-EUR exposure** number per issue:

1. **One basis: cumulative realized-cost EUR exposure.** Every cost/shift/drift issue ranks on `abs(cumulative_impact_eur)` against shared tiers. Stop inheriting `last["severity"]` (Bug 1) — compute issue severity in `_build_single_issue` (and route drift through the same function).
2. **Shared tiers (tune to the population):** the current 500/100/10 are per-week-shaped and far too low for cumulative — empirically actives run to 10^5–10^7. Suggest cumulative tiers e.g. **HIGH ≥ 25,000 / MEDIUM ≥ 5,000 / LOW ≥ 500** (calibrate against the table above; 25K cleanly separates the rate_spike high band from the medium band).
3. **Confidence as a modifier, not a separate scale.** Replace the hard caps (deviation→medium, unconfirmed shift→medium) with a `confidence` dimension surfaced alongside severity:
   - deviation_blowout: it's *modelled* deviation, not realized cost → tag `estimated`/`modelled`, but let a 74.7M deviation read HIGH (it currently can't). If the product genuinely wants deviation de-weighted, do it with a documented multiplier (e.g. severity-on `0.5·total_dev`), not a blanket ceiling (Bug 2).
   - shifts: keep the `trend_confirmed` gate as a confidence flag; an unconfirmed but huge shift should still be visible as high-magnitude-low-confidence, not silently medium.
   - drift: `estimated` always (Bug 4) — cap or down-weight, but via the same mechanism as the others, not an ad-hoc inline block.
4. **volume_anomaly** stays magnitude-free (no EUR) — keep its z-score tiering but render it on a separate axis (it has `eur_impact=0`; ranking it among EUR issues at "medium" is meaningless).

**Where the current basis is defensible:** using *per-week* impact for the *alert* rows (alerts.parquet) is fine — alerts are per-week by construction. The break is letting the *issue* (the UI's primary surface, inherently multi-week) inherit a per-week tier. Fix at the issue layer, leave the alert layer alone.

---

## Suspicions (unproven — flagged for verification)

- **S1 — `corridor_costs_weekly.parquet` fallback path (L1875) may be dead.** `_build_alerts` reads it only if `cc is None`; the vocab note's open question says it's not seen in the main write path. Not load-bearing for this review; carry the existing open question. *(needs verification)*
- **S2 — drift `latest_weekly_impact_eur` (L3299) is `drift·n_shipments/4`** — a synthetic "monthly impact / 4" proxy, not a real week. Harmless given drift severity uses cumulative, but it means drift rows are not comparable to other types' `latest_weekly_impact_eur` if anything downstream sorts on that field. *(needs verification of downstream use.)*
- **S3 — new_corridor `eur_impact = n·avg` (L2040) is a gross monthly-ish figure** while rate_spike's is a per-week delta — another cross-type basis mismatch feeding the same `_severity` thresholds. Consistent with the Bug-1/Bug-4 family; included for completeness. *(low priority.)*

---

## Triage summary (for principal)

| # | Title | Sev (user impact) | Confidence |
|---|---|---|---|
| 1 | rate_spike/creep/shift severity keyed off latest week not cumulative | HIGH | HIGH |
| 2 | deviation_blowout hard-capped medium at ±millions | HIGH | HIGH |
| 4 | drift severity uncapped → low-confidence type out-ranks all | MED-HIGH | HIGH |
| 3 | drift never resolves / hardcoded active / window never ages | MED | HIGH (defect), MED (fix shape) |

All four are facets of one design issue: severity has no single comparable basis across types, and drift sits outside the issue-lifecycle machinery entirely. The unified scheme above addresses 1, 2, 4 together; 3 needs the drift-persistence decision.

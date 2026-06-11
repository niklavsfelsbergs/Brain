# S197 — q04e packagetype label-churn deep dive (EU-tender side-investigation)

> sid8: b93204b5 · opened 2026-06-11 ~10:20 · parallel to 5733cb1d (result_investigation owner; coordinating via q04e_ file prefix)

## Brief

Deep dive on the mid-Q1 packagetype relabels q04d flagged: (1) exact switch timing (parquet daily series + shipping-agent mart history), (2) abrupt-vs-gradual + per-site/shop, (3) old-vs-new dims (relabel vs real size change), (4) sweep for other disappear/appear pairs. Deliverable: `result_investigation/q04e_label_churn_deep_dive_findings.md` + script, verdict per pair.

## Turn log

- T1: respawn, OPEN posted. Grounded in q04d findings + README + population parquet schema.
- T2: wrote + ran `q04e_label_churn_deep_dive.py`. WICKEL→ORWO: hard cutover 2026-02-18 (order date), whole WICKEL 80x60 family dies (incl. strapped); ORWO pre-existed ~50/d since Jan 1; template dims differ (86.5×63×4.3 → 91×62×4.5). STANZ 120x90→120x80: step at 2026-01-28 but 120x90 SURVIVES ~300/wk — real size change (W 90.5→80), L+girth 311.5→290 crosses the Maersk 300 ceiling.
- T3: spawned shipping-agent (pre-2026 lifespans, ship-date cutovers, post-Q1 state) + addendum agent (GEL + zugeschnittene post-Q1). Added 5b share-shift sweep: no other label pairs; zugeschnittene decline = gradual/seasonal; GEL stops late March (real, checking post-Q1).
- T4: section 7 routing impact: dead WICKEL cells = 146,937 ann parcels but only −€3.2k/yr booked (phantom volume, not € distortion); STANZ era-cells disagree on routed carrier in 11 dests (girth boundary); 120x90 cohort books −€17.8k/yr. ORWO got LIGHTER post-cutover — strapped parcels did not fold in (open thread).
- T5: addendum pull returned. GEL did NOT stop — mart steady ~330/mo through 2026-06; the Q1-extract late-March collapse is an invoiced-only/invoice-lag artifact, not churn. zugeschnittene pair persists post-Q1, clean seasonal shape (Dec 5,002 peak → spring taper) → demand, not catalog. Sweep verdict: NO other label-churn pairs in Q1 beyond the two known.
- T6: main pull returned with 3 story-changing facts: ORWO born 2025-07-24 (Feb = consolidation, not birth; carrier-side swap Mon 2026-02-23); STANZ "switch" is a REVERSION (S80 the 2-year incumbent, Dec–Jan S90 surge = the anomaly, + temporary 122.5×81.5×5.5 S80 tuple in Jan); plain WICKEL 80x60 resurrected May 12 on a new box; PIZZA 120x90 [x2] shrank in the same event. Wrote `q04e_label_churn_deep_dive_findings.md` — verdicts: WICKEL→ORWO relabel-equivalent (fold, no boundary crossed); STANZ real dim change crossing Maersk ≤300 (do NOT fold, re-weight ~3× S90 overstatement). GEL Q1-tail collapse = invoiced-only artifact (no churn).

- T7 (close): no pending external actions — both shipping-agent pulls returned and were folded in. Harvest: 1 examine draft (window-bounded-series-inverts-incumbency), 1 bank draft (population-parquet invoiced-only tail artifact), 1 cross-conv memory. S196 trace graduated → completed/. Resume: `inventory/q04e-label-churn-resume__b93204b5.md`.

No pending external actions.

*(Resume state lives in `inventory/q04e-label-churn-resume__b93204b5.md` per layer-routing; quest stays in-progress on open deps: CONCLUSION review + bi-analytics commit decision.)*

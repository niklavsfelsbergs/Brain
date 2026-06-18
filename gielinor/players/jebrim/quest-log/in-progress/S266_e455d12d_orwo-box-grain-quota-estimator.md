# S266 — ORWO cost/quota over-read → box-grain quota estimator

**sid8:** e455d12d · **2026-06-18** · continues the ORWO-UPS-DE arc (S251/[[S262_ac4b4649_ups-carrier-estimate-multipliers|S262]] calibration+coverage).
(Referenced as "[[S264_17290ea4_scm-shift-tabs-baseline-prune|S264]]" in mid-session comms UPDATEs; renumbered S266 at close per the SNNN glob — [[S264_17290ea4_scm-shift-tabs-baseline-prune|S264]]/[[S265_17290ea4_scm-resizable-columns|S265]] taken by parallel sessions. sid8 e455d12d is the stable key.)

## Ask
SCM ORWO avg-cost + quota up sharply May/Jun. Niklavs framed in stages: (1) investigate how ORWO
cost is built in the mart bi-etl (bulk-box → parcel distribution); (2) real cost drivers, go to raw
invoices to strip distribution, scope UPS + DE; (3) does it hit the quota; (4) design a fix so the
quota represents reality; (5) build it in an NFE topic to test the May/Jun quota prediction.

## Turn log
- Traced bi-etl ORWO cost build: bulk-mail `share_n` distribution (`{ups,dhl}_orwo.sql`) + expected
  waterfall with Pass 2a.6 dynamic calibration (`update_fact_shipments_cost.sql`). Read `orwo_open_pointers.html`.
- Raw `enterprise_silver.ups_orwo_invoices` (DE, ex-VAT): per-box billing FLAT ~€5.30/trk, €/kg +6%
  Mar→May. No real UPS DE rate increase. Verdict: dashboard spike = invoice-maturity selection bias.
- Proved the mechanism: per-parcel cost = box-charge ÷ parcels-in-box (10× spread). Bulk-mail
  manifests bill LATE → immature months show only solo parcels invoiced (inflated) + bulk at estimate.
- Quota: showed it's grain-INVARIANT in aggregate (distribution conserves total); over-read = coverage
  + estimate bias, not allocation. Reproduced the dashboard quota line + Invoiced/Final KPI split exactly.
- Tested per-parcel box-aware estimate: helps within-month but RATE-LEVEL (freshness) dominates the
  error (train Mar→predict Apr over-predicts 46%, same as the flat estimate; both anchored too high).
- Landed the design (Niklavs' idea): **box-grain estimate → distribute** = `box_rate ÷ parcels_in_box`,
  mirroring the real path. Verified box rate ~6× more stable than per-parcel (flat ~€5–8/box any size).
  Caught + explained the 2-box bimodality (shared-tracking is a fuzzy box proxy for pairs; washes out).
- Built brain docs (resume + this + bank draft). Now building NFE topic 50.

## Deliverable — BUILT (NFE topic 50, committed 7af8c14 + 67a8430, not pushed)
`shipping_topics/50_orwo_box_grain_quota_estimation/` — build_data.py (polars) + sql/ + findings.md
+ **bi_etl_implementation_plan.md**. Pulled 913,507 ORWO parcels (Feb–Jun) via shared.database.
The plan: new **Pass 2a.5b** in `update_fact_shipments_cost.sql` (box_rate/box_n for UPS+DHL ORWO),
**exclude UPS/DHL from Pass 2a.6** (box-grain IS the calibration; 2a.6's own comment names the
"bulk over/solo under wash out at group level" defect it fixes), POST/OTHER untouched. SQL skeleton +
pass ordering + 5 acceptance tests + risks (box_n-vs-share_n, calibration freshness) + phased rollout.

## Results
- **Validated** out-of-sample on clean UPS-DE slice: box-grain beats flat per-parcel EVERY time
  (−28 vs −39%, +42 vs +62%, −28 vs −37%). Residual ~30% = month-to-month rate freshness (not
  consolidation) → calibrate from most recent mature month.
- **Whole-ORWO quota (box-grain on UPS+DHL, production held for POST/OTHER):** Mar 17.1 / Apr 15.6 /
  May 16.4 / Jun **16.3** vs dashboard 17.1/15.5/16.6/**18.3**. June corrects −2pp (its 22%-inv spike
  flattens); May barely moves; mature months unchanged (doesn't distort good data).
- **Over-read is carrier-specific:** DHL (65%, 98% inv) fine; box-grain corrects UPS (May €56→52k,
  Jun €55→41k); **POST (€82k/mo, 99% estimate) is a structural hole** box-grain can't touch → needs a
  contracted POST rate. OTHER carriers uncosted (open-pointer 8). Ungated box-grain fabricates cost
  for POST/OTHER via global fallback → gated to UPS+DHL only.

## Next session (handed off — Niklavs, end of S266)
Do **Phase 1** of the bi-etl change + an **HTML explainer for Niklavs to review BEFORE any push**.
Full step-by-step plan in the resume (`open_dep` names the gate). Headline: write the REAL Pass 2a.5b
SQL (not the skeleton) in `bi-etl/dags/shipping_mart/fact_shipment_cost_summary/sql/update_fact_shipments_cost.sql`,
resolve box_n-vs-share_n, run the 5 acceptance tests against a closed month + the live month, then
produce a **self-contained HTML doc** explaining the fix (mechanism → before/after quota → validation →
what changes in the ETL → risks). **Niklavs reviews the HTML before he pushes. Do NOT push.**

## Open
- Niklavs Qs (in findings.md): contracted POST rate? deploy box-grain into bi-etl vs SCM-side first?
  calibration recency (most-recent-mature auto-pick vs rolling N-month)?
- Bank draft (2026-06-18-orwo-box-grain-cost-estimation) + 2 examine drafts await alch (don't promote).

## Cascade.
NFE topic 50 committed (7af8c14 + 67a8430, bi-analytics-main, NOT pushed) — findings.md +
bi_etl_implementation_plan.md + build_data.py + sql/. The plan targets a bi-etl change (separate repo,
not touched this session). No SCM/dashboard code changed.

## Main-brain changes.
This quest-log + resume + bank draft (2026-06-18-orwo-box-grain-cost-estimation) + 2 examine drafts
(estimator-error-is-level-not-structure, coverage-gate-calibrated-estimate-per-segment) + comms.
Resume: inventory/orwo-ups-de-cost-increase-resume__e455d12d.md.

---

## CONTINUATION (2026-06-18, session sid 64902bef, "continue quest 266") — Phase 1 BUILT
- Verified bi-etl HEAD before editing: branch `feat/fif-ups-orwo-monthly` is **even with origin/main**
  (0/0, target file identical) → the live SQL IS current HEAD; no pull needed (the verify-the-thing reflex
  paid: didn't assume the branch was stale or carrying ORWO work).
- **Wrote `Pass 2a.5b`** (box-grain overwrite, UPS+DHL un-invoiced) + **gated Pass 2a.6** (excludes UPS/DHL).
  Design calls made live: box_n stays (order_month, trackingnumber)-grain (box-conservation makes the
  box_n-vs-share_n divergence immaterial; DHL uniform, UPS ~16% within-box; cross-month reuse 8.3% handled
  by month-scoping). Calibration = most-recent-mature-month per family (DHL May, UPS April, ≥60% inv floor).
- **Acceptance (read-only live mart):** reproduced topic-50 within ~0.1pp; Jun 18.28→16.40, mature months
  ≤0.1pp, POST/OTHER zero-change, UPS the driver (€55.2k→€40.5k). All 5 tests pass.
- **Built `fix_explainer.html`** in topic 50 (self-contained, CSS chart, ASCII-clean, topic-35 tokens).
- bi-etl SQL left **UNCOMMITTED** (Niklavs reviews HTML → he commits pathspec + pushes). Handed off.

## Cascade (continuation).
bi-etl `dags/shipping_mart/fact_shipment_cost_summary/sql/update_fact_shipments_cost.sql` MODIFIED
(+208/-6) — NOT committed, NOT pushed (his action). bi-analytics-main NFE topic 50 gained
`fix_explainer.html` — not yet committed (offered). No live mart writes (all validation read-only).

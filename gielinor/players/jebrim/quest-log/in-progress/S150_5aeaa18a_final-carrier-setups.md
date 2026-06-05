# S150 · 5aeaa18a — EU Tender 2026: final carrier setups (decision report + routing table)

> Continuation of the S150 carrier-overview/decision quest (born e04c495d). This session executed `decision_report/PLAN_final_setups_2026q1.md`: re-base the EU-tender decision onto a 2026-Q1 actual-invoice basis, then build the operational routing table. Working tree: `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/`. Narrative + decisions below; resume state in `inventory/carrier-overview-report-resume__5aeaa18a.md`.

## What this session did

**Phase A — 2026-Q1 cost matrix (DONE, committed bi-analytics `6d211d0`).** Spawned the shipping-agent for the full 2026-Q1 book pull (all carriers, PCS PL, 18 countries, half-open Jan–Mar): 531,194 parcels, Σ real_total_eur €3,030,997.91, 100% invoiced; `total_eur` confirmed tax/customs-exclusive; MAERSKFR 27,447 @ €4.72. `cost_matrix_2026q1.py` ran the 9 engines → `data/cost_matrix_2026q1/` (4.78M rows). `today_eur = real − OML(>€400)`, LPS kept full → Σ €2,955,020 (70 UPS OML netted, €75,978 — matches the v2 ledger).

**Phase B — decision scorer re-pointed (DONE, uncommitted scorer + report).** New parallel files: `_decision_sets_2026q1.py` (two-Maersks: maersk_current_fr INCUMBENT/MAERSKFR-extkey + maersk_eu_new NEW_OFFER engine; collapse to one family for the ≤6 cap), `decision_scorer_2026q1.py` (incumbent bid = today_eur, DROPPED the [[S120_3760e65b_eu-tender-full-year-build|S120]] ENGINE_BACKED_INCUMBENTS reprice hack, new offer = engine face value, no bias) → `data/scenarios_2026q1.parquet` (82 sets, do_nothing €0 PASS). `decision_report/report_2026q1.py` — fresh report on the 2026-Q1 basis, softened headline.

**Phase D — REFRAMED to an operational routing table (DONE, committed bi-analytics `47f7b0b`).** Principal redirected: the deliverable is a `(destination × packagetype × weight) → carrier` routing table, built bottom-up. `build_final.py` (per-cell for standard packagetypes + per-parcel for variable; necessity ∪ materiality ≥€25k/qtr portfolio rule) → **the 6: DHL Paket, Maersk (FR+EU), Hermes, DPD-PL, UPS, DB Schenker**, **Q1 saving €399,750 (13.5%)**. `derive_envelope.py` — per-destination parcel-carrier size envelope; DB Schenker = the 165 must-freight (no parcel carrier eligible), FR drives 119 of them (Maersk off the FR rate card). `routing_report.py` → self-contained `routing_report.html`: freight envelope, per-carrier overview, interactive (sortable + combobox-filter) routing table + CSV download.

**The per-carrier "what each carrier takes" overview (uncommitted, this session's last work).** Iterated heavily with the principal. `carrier_envelopes.py` describes the routing dimensionally (gross-weight band × size-class), labelled by dominant carrier (93% faithful). Tested chargeable weight + finer bands (96% raw) but they don't survive the contiguity smoothing the principal wanted — so **settled on coarse gross-7-band + bulky, smoothed to full weight-contiguity** (each carrier owns one contiguous weight interval per dest×size; 4,858 parcels / 0.9% nudged → 92.7% faithful). Plus a descriptive dimension table (actual size ranges p5–p95). DB Schenker rule = the must-freight envelope (~165), not a packagetype carve-out.

## Decisions locked (principal, this session)
- OML>€400 dropped + LPS kept full (matches the carrier-overview basis).
- maersk_current_fr = MAERSKFR extkey strictly; **Maersk counts as ONE carrier** for the ≤6 cap, scored as two contracts.
- Engines at face value, no bias; Güll excluded (held, only ~€27k, AT/CH niche).
- Custom/oversize → DB Schenker only by the must-freight envelope (no parcel carrier eligible), not by packagetype.
- Routing runs on **packagetype** (€400k, executable); the per-carrier dimensional view is an **overview/summary** — smoothed for contiguity, ~92.7% faithful. Chargeable weight gains raw fidelity but not smoothed fidelity → coarse bands chosen.

## Surfaced findings (worth carrying)
- UPS is kept for its **hard oversize tail, not its price** — ~110k of its 149k parcels migrate off to cheaper carriers; the rest have no cheaper option (and UPS has no engine, so it can't bid on parcels it doesn't already hold — a cost leak on the FR oversize tail where DHL Express €38 vs DB Schenker €110 but DHL Express is out of the 6).
- The 165 must-freight rule is **dimensional but not a clean single threshold** (it's the intersection of every serving carrier's size/shape limit; FR oversize is the big bucket because Maersk is off FR).

## No pending external actions.
(All pulls + commits done in-session. No sends/exports awaited.)

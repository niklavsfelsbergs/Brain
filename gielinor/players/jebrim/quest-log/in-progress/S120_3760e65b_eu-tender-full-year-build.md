# S120 — EU Tender 2026: full-year build (Option 1)

**Session:** jebrim-3760e65b · 2026-05-28 · continues [[S118_f41737e5_eu-tender-decision-scorer-report-regen|S118]]/S119 (4c2210ee).
**Goal:** Build the full-year decision view — replay full-2025 actuals on the 2026 rate cards. 5-step plan (NEXT.md item 3).

## Resume foreground
See `inventory/eu-tender-full-year-build-resume__3760e65b.md`.

## Turn log

**T1 — respawn + Step 1 (repoint + widen population.sql).**
- Respawn: adopted S119 resume (`inventory/eu-tender-decision-scorer-report-regen-resume__4c2210ee.md`); 4c2210ee ended clean ~1min prior, same terminal. Only live sibling = braindead-277d9053 (dev-brain, no overlap). Posted OPEN to comms.
- Verified gold schema live (Redshift MCP): `shipping_mart.fact_shipments` (23 selected fact cols) + `shipping_mart.fact_shipment_cost_summary` (14 cost buckets) — all exist 1:1 on gold. Feasibility GREEN confirmed at column level.
- Edited `sql/population.sql`: `enterprise_silver.*` → `shipping_mart.*` (both fact + cost-summary join); window `2026-Q1` → full-year 2025 (`>= 2025-01-01 AND < 2026-01-01`). Header + inline comments updated.
- Row-count verify: in-scope (with `cs.total_eur IS NOT NULL`) = **2,875,235**. S119 feasibility's 2,926,069 was fact-side (pre cost-join); delta 50,834 = 1.74% = the documented ~1.9% late-invoice drop. No gold-data hole.
- Smoke pull (LIMIT 100) through real `shared.database.pull_data` path: 37 cols, gold read OK, conversion clean, real_total_eur populated. End-to-end repoint verified.
- **DONE:** full pull `python pipeline.py` → `data/population.parquet` overwritten Q1 528k → full-year **2,875,235 rows / 37 cols**, date range 2025-01-01→2025-12-31, PCS PL, 17 distinct countries (= Q1's 17; one whitelist country has 0 ships), zipcode/packagetype/real_total_eur nulls = 0. DE = 1.92M (67% — confirms the Q4/DE dominance the reframe targets). `population.parquet` is **gitignored** → step-1 commit scope = `sql/population.sql` only.
- **STEP 1 COMPLETE + VERIFIED.** (Uncommitted — holding for principal go per global "always ask before committing".)

**T2 — Step 2 design + the step-2/3 coupling.**
- `decision_scorer.py` reads full `cost_matrix.parquet` into memory (`pl.read_parquet`) → second OOM surface at 26M rows (beyond the matrix build). Only uses ~6 matrix cols → lazy column-pruned scan is the fix when consumers adapt.
- **COUPLING FOUND:** engines price monthly fuel/surcharges by `shop_order_created_date` month, but rebuilt engines carry **Q1-only** ladders. Feeding Apr–Dec will crash (`replace_strict` no-default) or silently default (AP FX→1.0). So step 2 (chunk runner) + step 3 (extend ladders to 12 mo + wire peak) must land together before the first verified full-year matrix run. Per-engine out-of-Q1 behavior differs → audit all 9.

**T3 — Step 2 chunked runner built + engine month-coverage audit.**
- Rewrote `cost_matrix.py`: loops order-months, scans+filters population per month, runs 9 engines on one month, writes `data/cost_matrix/cost_matrix_YYYY-MM.parquet` (12 partitions). Added `load_cost_matrix()` lazy `scan_parquet` helper (col-prunable) for consumers; legacy single-file fallback kept. `data/cost_matrix/` gitignored. Launched the full-year run (background).
- **Engine month-coverage audit (step 3 map):**
  - **Peak/demand ALREADY date-wired full-year** (a full-year run exercises them): hermes Q4 peak €0.25 (Oct–Dec); dhl_paket Peak €0.19 (Nov–Dec) + Peak-in-Peak €0.50 (Nov28–Dec2) [HELD engine]; gls peak €0.30 (Nov23–Dec6) + Season 1% (Apr/May/Oct/Nov/Dec); dhl_express demand per-kg (Jan1–Feb16); AP correctly no-peak (PEAK_PCT=0).
  - **Fuel = Q1-only with graceful fallback (no crash):** dpd_pl `replace_strict(default=offer-issue band)`; hermes `FUEL_PCT_DEFAULT=0.0`; AP FX `default 1.0`; AP fuel flat 4%. → Apr–Dec fuel uses fallback bands, not month-precise. **Step 3 = source Apr–Dec monthly fuel** (Orlen for dpd_pl, Destatis for hermes, DHL Express CW, etc.) + the **maersk EU 2025 peak schedule** (PEAK_PCT=0.0 placeholder, deferred Q5).
  - maersk fuel = Q1 weekly Intl FSC ×0.5 (pull later); gls Energy/Dieselfloater held as flat year-long assumption ([[S115_db60ed8a_eu-tender-dpd-pl-reply-review|S115]]) — no monthly table to extend.
- Net: full-year matrix will MATERIALIZE now (engines don't crash); step 3 refines Apr–Dec fuel precision + maersk peak, rather than being a prerequisite for the run.

**T4 — Step 2 verified; Step 3 gap analysis.**
- Full-year matrix built: 12 partitions, **25,877,115 rows** (2,875,235 × 9, exact), 17.83M eligible, no OOM (Dec peak = 5.55M rows). Per-engine eligible: AP 184.6k / guell 189.2k (narrow) … dhl_paket 2.83M / fedex 2.86M / hermes 2.78M / gls 2.75M / dpd_pl 2.74M / maersk 2.53M / dhl_express 957k. Lazy `load_cost_matrix()` aggregation verified (no 26M-row materialization).
- **Volume profile validates the full-year thesis:** Dec = 616,740 ships (21% of year, > all Q1-2026 528k); Q4 (Oct+Nov+Dec) = 1.15M = 40% of annual volume — all peak-loaded where Q1 had zero peak. Q1×4 would have mis-ranked.
- **Step 3 status:** peak/demand date-wired for 5 carriers (hermes/dhl_paket/gls/dhl_express + AP-zero). Remaining gaps = **maersk seasonal** (decision-relevant — leader renews maersk): (1) EU peak 2025 schedule "sent in last email" but NOT in folder, `PEAK_PCT=0.0` → zero biases comparison toward incumbent; (2) ROW demand — FedEx schedule known (€0.40→susp→€0.70/kg) but unwired + passthrough unconfirmed (small AU/NZ/ROW vol). Fuel Apr–Dec = stabilised band per plan step (e), not month-precise — no new decision.
- Posed the maersk-seasonal handling to principal (assume-and-document vs flag-only vs chase the schedule).

**T5 — Step 3: maersk EU peak wired + verified (principal chose "assume + document").**
- maersk `surcharges/peak.py` rewritten: was `pl.lit(False)` placeholder (PEAK_PCT=0) → now flat €0.25/parcel, EU-branch only, Oct–Dec window (`in_period` + `service=="eu_hd"` gate), mirroring hermes. constants.py: replaced `PEAK_PCT` with `PEAK_EUR=0.25 / PEAK_START=(10,1) / PEAK_END=(12,31) / PEAK_DATE_COL` + flagged-assumption rationale + REVISIT trigger (peer-anchored to hermes; real schedule is in an email thread, retrievable).
- Fixture harness extended: added `order_date` (default non-peak 2025-06-15 so prior fixtures' totals unchanged) + `expected_cost_peak` + `shop_order_created_date` injection + cost_peak assertion. 2 new fixtures: AT-Nov peak fires (€0.25), AU-Nov ROW gets NO EU peak (service-gate guard). **17/17 pass** (15 prior unchanged).
- Stray `PEAK_PCT` refs remain only in maersk `report.py` / `migration_plan.html` (regenerated docs) — fold into the doc cascade.
- **Still open in step 3:** (1) maersk ROW demand (AU-only, 26,181 elig = 0.9% of maersk; full-year magnitude unknown beyond Q1 — flagged passthrough or documented deferral); (2) **re-run cost_matrix.py** — current 12 partitions were built BEFORE the peak edit (stale; maersk Q4 now +€0.25/parcel). Re-run once all step-3 engine edits land.

**T6 — ROW demand documented (principal-confirmed deferral); matrix re-run.**
- maersk `constants.py`: added `ROW_DEMAND_EUR_PER_KG = 0.0` documented flagged deferral + rationale + REVISIT trigger (AU-only 0.9%, full-year FedEx magnitude unknown; held at 0 vs fabricated). Matches existing documented-placeholder pattern (CH_CUSTOMS_EUR / AT_HANDLING_EUR).
- Re-ran `cost_matrix.py` (background) to bake maersk Q4 peak into the 12 partitions (prior partitions were peak=0 stale). Engine change is matrix-layer; steps 4–5 are scorer/report-layer reading the matrix → single rebuild.
- **Step 4 design surfaced (needs principal steer):** do-nothing baseline currently = Σ real_total_eur (2025 invoice; do_nothing is the 0-saving sanity anchor). Re-pricing on 2026 rates = each incumbent's 2026-engine price, BUT ups + db_schenker have NO engine, and it changes the do_nothing-sanity meaning. Incumbents WITH engines: maersk/dhl_paket/dpd_pl. Decision: how to price no-engine incumbents (keep invoice? inflate?) + whether do_nothing baseline becomes engine-priced.

**T7 — Step 3 verified done; Step 4 baseline decision (principal).**
- Matrix re-run verified: maersk EU peak fires Oct/Nov/Dec only (€41.5k/€74.9k/€134.0k = **€250,430/yr**), zero ROW, zero Jan–Sep. Step 3 COMPLETE.
- **Baseline composition sized:** DHL 54%sh/35%€ (€5.11M, engine) · **UPS 24%sh/34%€ (€4.94M, NO engine)** · **DB Schenker 0.9%sh/10%€ (€1.47M, NO engine)** · DPD-PL 7.7%€ (engine) · GLS 5.9% · ColisPrivé/DirectLink/APG ~7% (non-decision). ~44% of spend has no 2026 engine.
- **DECISION (principal): re-price switchables only.** Re-price engine-backed switchable incumbents (dhl_paket=DHL, maersk, dpd_pl=DPD-PL) on 2026 engines in the do-nothing baseline; hold no-engine incumbents (UPS, DB Schenker) + non-decision carriers at 2025 invoice (they're INCUMBENT in every set → cancel in savings). Report Σreal_total_eur as labelled "what we pay today" reference. Flag dhl_paket-engine +5.5% over-pricing of DHL book + dhl_paket HELD (old/round-2) status.

### Step 4 implementation spec (decision_scorer.py)
1. Switch matrix load: `pl.read_parquet(single)` → `load_cost_matrix()` (lazy, partitioned 26M rows) + column-prune (only shipment_id, carrier, eligible, cost_total_eur, real_total_eur, shipping_provider_group needed). Mind memory (all_bids ~17.8M eligible).
2. INCUMBENT bid re-pricing in `build_bids`: for engine-backed incumbents {dhl_paket, maersk, dpd_pl}, INCUMBENT bid_eur = that carrier's engine cost_total_eur (join per_ship→matrix on shipment+carrier); where engine row ineligible → fall back to real_total_eur (flag). No-engine incumbents {ups, db_schenker} → bid_eur = real_total_eur.
3. Redefine `baseline` = do_nothing total_cost under the new pricing (NOT Σreal). do_nothing mandatory_saving stays 0 by construction (sanity preserved vs new baseline). Add `invoice_today_eur` = Σreal as a separate reported reference.
4. apply_invoice_adjustments (UPS OML/LPS) still applies to the matrix.

**T8 — Step 4 implemented (verifying).**
- `decision_scorer.py` edited per spec: (1) load via `load_cost_matrix()` lazy + column-prune to 7 cols (was `pl.read_parquet` single file); (2) `build_bids` re-prices INCUMBENT bid for ENGINE_BACKED_INCUMBENTS {dhl_paket, maersk, dpd_pl} = their 2026 engine cost_total_eur (join per_ship→matrix on shipment+carrier), fallback to real_total_eur where engine ineligible OR no-engine incumbent (UPS/DB Schenker); (3) `baseline_2026` = do_nothing routed cost (computed once, denominator for all sets → do_nothing saving 0 by construction); (4) added `invoice_today_eur` = Σreal reference field; field names kept stable for report.py. `del matrix` after build_bids (free ~26M frame). Running scorer to verify do_nothing=0 + baseline-vs-invoice delta.

**T9 — Step 4 VERIFIED.**
- Scorer ran clean on 25.88M matrix rows / 2,875,138 ships (post OML drop). all_bids 20.35M (INCUMBENT 2.52M + NEW_OFFER 17.83M). No OOM (column-pruned load + del matrix).
- **do_nothing mandatory_saving = €0.0000 (PASS)** — sanity anchor holds vs the re-priced baseline.
- **baseline_2026 = €14,851,018 vs invoice_today (2025) = €14,269,584 → +€581,434 (+4.1%)** re-pricing delta (2026 rates > 2025 invoices; consistent w/ flagged dhl_paket +5.5% DHL-book over-pricing + dpd_pl/maersk re-price). UPS adj: OML 97 dropped (€126.7k), LPS 2169 halved (€144.6k).
- Rankings coherent: trustworthy ≤6-carrier leader = **renew_maersk_plus_hermes €635,065/yr** mandatory (3 uncovered) — [[S118_f41737e5_eu-tender-decision-scorer-report-regen|S118]] Q1 leader, now carrying maersk's €250k Q4 peak. Bottom: renew_dhl_paket −€1.84M, add_dhl_express −€3.16M (known dhl_paket over-pricing / dhl_express expense). Top raw sets (~€2.2M) exceed 6-carrier cap + lean on HELD fedex/guell/dhl_paket → provisional. scenarios.parquet = 90×14 (incl. new invoice_today_eur).
- STEP 4 COMPLETE + VERIFIED.

## Decisions / notes
- cost_matrix.py holds 9× full-population frames before `pl.concat(diagonal)` → the OOM risk (step 2 chunks by month).
- 9 engines registered (incl. HELD fedex/dhl_paket/guell on old versions — provisional, flagged downstream).
- Step-2 output design = partitioned per-month parquet under `data/cost_matrix/`; consumers move to lazy `scan_parquet` glob (handled when re-running scorer/report).

## Commits
- **Tender 6991d37** (steps 1–4): population.sql + cost_matrix.py + decision_scorer.py + maersk/{constants,surcharges/peak,tests/fixtures,tests/test_engine} — 7 files, pathspec-scoped, local-only (no push). Data parquets gitignored.
- Brain: jebrim quest-log S120 + inventory resume + comms + intent (this close, pathspec-scoped).

## Close note (S120)
Steps 1–4 of the full-year build DONE + verified; principal chose to commit + do **Step 5 (fuel band + report regen) in a fresh session** (full spec in the inventory resume). Quest S120 stays in-progress for Step 5. No live siblings; no collision (braindead-277d9053 dev-brain only).

---

## S120 cont. — Step 5 (jebrim-2ae1248b · 2026-05-28)

Fresh session per the handoff. Respawn: adopted the `__3760e65b` STEP 5 HANDOFF SPEC; no live siblings (sidecar+comms clean); posted OPEN.

**T1 — fix report.py read + ground-truth.**
- Fixed the broken read: `report.py` L550 `pl.read_parquet(DATA/"cost_matrix.parquet")` → `load_cost_matrix()` (lazy, column-pruned to 7+3 cols), mirroring decision_scorer.
- Ground-truthed full-year numbers (scratch `_groundtruth_s120.py`, untracked): baseline €14.85M / invoice €14.27M / +€581k; OML 97/€126.7k + LPS 2169/€144.6k; Hermes cov 96.8% @ €5.87; **two Q1-hardened bugs surfaced** — (a) the `n_uncovered==0` "full coverage" filter matches NOTHING on full-year (every set strands 3-20 residual parcels) → report.py would crash; (b) trustworthy ≤6 reorders: drop-DPD route €732k > +GLS €642k > +Hermes €635k. Also `renew_maersk` ALONE flipped negative (−€199k, 138.5k stranded). **dhl_paket book over-pricing = +2.9% (1.029), NOT the +5.5% the handoff/T9 carried** — verify-don't-assert.

**T2 — two principal decisions (AskUserQuestion).**
- Headline leader: KEEP `renew_maersk_plus_hermes` (€635k) pinned as the minimum-disruption headline; relax the broken filter to ≤100 tolerance; surface the higher trustworthy routes (€732k drop-DPD, €642k +GLS) as alternatives in prose.
- Fuel: DEFER the numerical low/mid/high sweep; ship the qualitative band now.

**T3 — report.py Step-5 edits.**
- Moved cm-load + bias infra above the narrative; added a LIVE-facts block (bias ratios via REC_ALL won-slice, Hermes coverage, gls/dpd customs components, maersk peak, dhl_paket book ratio). Pinned tw_leader=Hermes + computed tw_best (drop-DPD). Rewrote all 9 carrier narratives + KPI + summary + the two-caveats / chart-1 / §B.13 / fuel / UPS callouts + the what-changes table to use live full-year values; relabelled all "Q1" framing. Customs caveats now live: GLS EFTA €1.32M/yr, DPD-PL CH €2.32M/yr. Maersk peak €250,410/yr (post-OML-adj), +ROW-demand deferral added.
- Regenerated `decision_report.html` (233KB), EXIT 0, deterministic across two runs. **Ground-truthed every headline number against scenarios/matrix** (not pixel-eyeballed): all match.

**T4 — doc cascade.**
- NEXT.md (full-year build EXECUTED; next steps reordered — fuel sweep #1), DECISIONS.md (S120 full-year-build-executed entry), ASSUMPTIONS.md (maersk EU peak + ROW-demand entries w/ revisit triggers), REPORT_NOTES.md (full-year caveat figures + executed note), stray PEAK_PCT refs fixed in carriers/maersk/{report.py, migration_plan.html}.
- **cross_carrier_view left as the Q1 unit-cost reference** (its whole framing is Q1; reads the current legacy Q1 matrix; html already current) — converting to full-year is a separate build that changes its purpose; flagged to principal, not done.

**Step 5 COMPLETE.** All report + doc changes UNCOMMITTED — held for principal go (commit scope in `inventory/eu-tender-full-year-build-resume__2ae1248b.md`). Quest S120 essentially complete pending commit; remaining full-year refinements (fuel sweep, seasonal layers, carrier round-2s) are tracked in NEXT.md, not blockers.

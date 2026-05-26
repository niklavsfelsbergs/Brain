# [[S034_2026-05-22_eu-tender-logic-review|S034]] D7 — Decision scorer + cross-cutting assumption audit
**Spawned by:** Jebrim, 2026-05-22

## TL;DR

The §B.13 scorer math is correct under its assumptions, but **the assumptions have drifted** since the 2026-05-13 sanity check. Three engines (Hermes, DPD PL, FedEx) joined the cost matrix without the scorer plumbing or supporting artefacts catching up, and CLAUDE.md's "score every portfolio twice (parcel-only vs parcel+freight)" requirement is not implemented at all.

Top scorer findings: (1) Hermes/DPD PL/FedEx absent from `cross_carrier_view.py` and `report.py CARRIER_NARRATIVE`; bias table 7-pool still hardcoded; (2) `decision_scorer.py` has **no parcel-only vs parcel+freight split** even though the Decision Framework mandates it — DB Schenker is INCUMBENT-only and never bid against; (3) FedEx never appears in `NEW_ENTRANTS` so cannot enter any decision set despite being live in `cost_matrix.parquet`; (4) The greedy-cheapest-per-parcel routing in `score()` is no longer provably optimal once `INCUMBENT` bids exist — the §B.13 model has cross-shipment coupling that the pure greedy ignores.

Top cross-cutting implicit assumptions: (1) Population SQL hard-codes **only 18 destinations** — half the engines' country lists are dead code on Picanova-Q1; (2) `shipping_provider_group` is treated as a 1-to-1 carrier map but DHL is a single label hiding Paket+Kleinpaket+possibly Express; (3) Per-shipment grain assumes one parcel = one bill (multi-parcel split is documented for the mart but the scorer treats it as fact, not assumption); (4) Cost-only scoring + "no service-quality" is mentioned in CLAUDE.md but missing from ASSUMPTIONS.md as a scoring-layer assumption.

---

## Part A — Scorer logic

### `decision_scorer.py` — bugs / wrong assumptions

**FINDING A1 (HIGH, file-level).** *Hard cap 6 is documented but only soft-enforced.* `CARRIER_CAP = 6`; `validate()` only prints a warning to stderr when active > 6 and the set is still scored and persisted. The report layer (`report.py`) then derives "best ≤6" from the scenarios output via `filter(n_carriers_active ≤ 6)`. With 7+ carriers active in `all_renewals_plus_*` combinations of size 4 from a 5-entrant pool plus 5 incumbents = up to 10 active in seed list, the warning fires repeatedly. Either: (a) reject and skip over-cap sets, or (b) commit to soft-cap with `is_within_cap` column in `scenarios.parquet`. Currently the report papers over this by filtering, which is correct but undocumented in code and obscures why some sets vanish from the headline.

**FINDING A2 (HIGH, line 117–127).** *Per-shipment greedy is no longer provably optimal in the §B.13 framing.* SANITY_CHECK 2026-05-13 said greedy is optimal because "no shipment-coupling constraints are modelled". That was true for the **old** portfolio_scorer where all carriers were NEW_OFFER. Under §B.13 the INCUMBENT bid only fires when the parcel's `shipping_provider_group` matches the carrier — this creates a *cross-shipment* asymmetry where the same engine can bid on shipment X but the INCUMBENT bid cannot. The scorer still picks cheapest-per-parcel independently, which is fine for minimising **routing cost given the state vector** but the state-vector enumeration (`_decision_sets.py`) is *not* exhaustive — it's a curated list. So the greedy is per-shipment-optimal *inside* a state vector but the search across state vectors is hand-picked. Comment claim "this matches optimal under fixed carrier set" is half-true; it's optimal conditional on the seed-set choice, which is itself unscored vs the full {INCUMBENT, NEW_OFFER, OFF}^10 = 59,049 grid.

**FINDING A3 (MEDIUM, line 75).** *INCUMBENT bid filter uses `GROUP_TO_CARRIER_ID` which only covers carriers with a non-null `incumbent_group`.* DHL Paket's incumbent group is `"DHL"` — but the cost matrix's `shipping_provider_group="DHL"` rows could be DHL Paket OR DHL Express OR DHL Kleinpaket (no disambiguation in the mart). Every DHL parcel is mapped to `dhl_paket` as INCUMBENT bid. If any of those parcels were actually DHL Express invoices, they're being credited to DHL Paket's INCUMBENT slice with the wrong engine's bid comparison downstream. **Mart-level segmentation question.** SANITY_CHECK §"Architectural risks" noted "`shipping_provider_group` filtering inconsistency between `cells()` and `portfolio_scorer.assign_portfolio`" — that inconsistency is still alive in the §B.13 scorer, just transposed onto the INCUMBENT mapping.

**FINDING A4 (HIGH, file-level).** *Parcel-only vs parcel+freight split missing.* CLAUDE.md "Decision Framework (locked 2026-05-12)": "Score every portfolio twice — parcel-only, and parcel + freight (DB Schenker or alternative)". `decision_scorer.py` has no `freight_variant` parameter, no DB Schenker engine, and DB Schenker is `INCUMBENT|OFF`-only in `_decision_sets.py` (line 54). The scorer effectively always runs "parcel + DB Schenker INCUMBENT" because DB Schenker is in `ALL_INCUMBENTS`. The "parcel-only" half of the locked framework is unimplemented. Either: (a) flip DB Schenker to OFF for a second pass, or (b) document that the dual-scoring requirement was silently dropped.

**FINDING A5 (LOW, line 220–224).** *`do_nothing` sanity check tolerance is 1e-3 EUR.* OK for a sum-of-floats check, but the assertion is silent in non-do_nothing rows. Worth adding a similar assertion that `mandatory_saving ≤ migration_saving` for every row (a property guaranteed by construction; failing it is a sign the bid aggregation is broken).

**FINDING A6 (MEDIUM, line 133).** *Uncovered-parcel residual uses `real_total_eur` from `per_ship`, which is post-OML/LPS-adjusted.* OK — that's the intent. But the residual is silently added to `total_cost` so `mandatory_saving_eur` for any set with uncovered parcels nets the residual against itself = 0 incremental effect (good). Worth a comment; right now the only hint is `pl.coalesce(["assigned_cost_eur", "real_total_eur"])`. **Status: not a bug, but invisible.**

### `scenarios.py` — bugs / wrong assumptions

**FINDING B1 (OK).** Column rename to `candidate_total` / `candidate_wins` landed clean (DECISIONS 2026-05-14). The carrier-agnostic naming holds.

**FINDING B2 (MEDIUM, line 91–95).** *`cells()` drops null/empty `shipping_provider_group` AFTER the aggregation.* The aggregation groups by `CELL_DIMS` which includes `shipping_provider_group`. Cells with null group get aggregated together as a `null` cell and then filtered out. If the engine is eligible and the parcel has a real invoice but the mart never populated `shipping_provider_group`, that parcel's saving is silently dropped from `cherry_pick_scenario`/`cell_level_scenario`. The dropped count = `eligible_df.height` - sum over cells. Not currently reported. **Action: log n_dropped at the `cells()` boundary.**

**FINDING B3 (MEDIUM, line 51–57).** *`eligible_with_actuals` requires `real_total_eur > 0` but uses `is_not_null` for cost.* OK, but `real_total_eur > 0` filters out rows where cost is exactly zero (free shipments, returns credited to original outbound, etc.). These exist in the mart; the carrier engine still scores them but they don't appear in cherry-pick. **Status: documented in SQL (`AND cs.total_eur IS NOT NULL`), but the `> 0` filter is additional and silent.**

**FINDING B4 (LOW, line 100–108).** *`cherry_pick_scenario` is per-shipment optimum — not portfolio-level.* The docstring says "saving if every parcel where the carrier is cheaper moves" but this is **the carrier alone**, not the carrier in a portfolio. Used downstream as a ceiling, which is correct for per-carrier rollups but `cross_carrier_view.py` re-implements a greedy-across-carriers ceiling separately. The two definitions of "cherry-pick" coexist; an analyst reading the report could conflate them.

### `_decision_sets.py` — bugs / wrong assumptions

**FINDING C1 (HIGH, line 70).** *`NEW_ENTRANTS` does not include FedEx.* `["dhl_express", "gls", "guell", "austrian_post", "hermes"]` — five entries. FedEx was wired into the cost matrix 2026-05-20 (DECISIONS), DPD PL was reopened as a normal candidate (DECISIONS 2026-05-20). Neither appears as `NEW_OFFER`-capable. DPD PL has only `{INCUMBENT, OFF}` (line 53). FedEx isn't in `CARRIERS` at all. **The scorer cannot score any decision set that includes FedEx-NEW_OFFER or DPD PL-NEW_OFFER**, despite both engines being live. PLAN.md §B.26 sub-step 4 flags this explicitly as outstanding.

**FINDING C2 (HIGH, line 109–114).** *Combinatorics still bounded at 5 NEW_ENTRANTS.* The seed builder iterates `combinations(NEW_ENTRANTS, k)` for k in 1..5 → 31 sets from new-entrant combos alone. With FedEx + DPD PL elevated, that becomes 2^7 - 1 = 127. The hard cap of 6 active carriers means many of these would over-cap, but the SANITY_CHECK's "score the full 4-of-6 subset space" recommendation is *still* unfilled — and the search space grew, not shrank.

**FINDING C3 (MEDIUM, line 14–25).** *Allowed-states matrix is outdated.* Comments say "ups: NEW offer pending" (still true), "dpd_pl: being retired" (superseded by 2026-05-20 DECISION), "hermes: provisional Q1-Q10 pending" (still true). The Hermes provisional flag has no code-level impact — the scorer treats Hermes bids identically to confirmed engines.

**FINDING C4 (LOW, line 71).** *`NON_RENEWABLE_INCUMBENTS = ["ups", "dpd_pl", "db_schenker"]`.* DPD PL is no longer "non-renewable"; the 2026-05-20 reopen makes it renewable in principle. The constant name + membership lags the decision.

### `cross_carrier_view.py` / `report.py` — bugs / wrong assumptions

**FINDING D1 (HIGH, `cross_carrier_view.py:67-76`).** *`CARRIERS` list is hardcoded to the original 6.* Hermes (added 2026-05-15), DPD PL and FedEx (added 2026-05-20) are missing. Every chart, every greedy 1→6 walk, every per-country matrix, every pair-coverage table excludes the three new engines. The HTML deliverable claims "all 6 carriers" but is silently outdated. **This file is half-stale.**

**FINDING D2 (MEDIUM, `cross_carrier_view.py:684`).** *`present_carriers = [c for c in CARRIERS if c in ship_wide.columns]`.* Defensive against missing carriers but won't pick up new ones — the iteration source is the hardcoded `CARRIERS`, not `ship_wide.columns`. Even if Hermes/DPD PL/FedEx are in the matrix, they're not iterated.

**FINDING D3 (MEDIUM, `report.py:73-76`).** *`CARRIER_ORDER` and `CARRIER_NARRATIVE` updated for Hermes but missing DPD PL and FedEx.* The state strip in §02 table draws only 9 chips (`dhl_paket, maersk, dhl_express, gls, guell, austrian_post, hermes, ups, dpd_pl, db_schenker` = 10 actually) — FedEx is absent from `CARRIER_ORDER`. DPD PL appears but only as INCUMBENT|OFF (per `_decision_sets.py`). Per-carrier narrative cards have no DPD PL block and no FedEx block. **§B.16 v2 is gated on these landing.**

**FINDING D4 (HIGH, `report.py:472-474`).** *`REC4`/`REC6`/`REC7` hardcoded for the bias table.* `REC7 = REC6 + ["hermes"]`. FedEx + DPD PL bias slices are uncomputed in the live-rebuild path. Same staleness as cross_carrier_view.

**FINDING D5 (MEDIUM, `report.py:476-494`).** *`_winning_slice` joins `real_total_eur` from `carriers[0]` only.* `rec.filter(pl.col("carrier") == carriers[0]).select("shipment_id", "real_total_eur")` — relies on `real_total_eur` being identical across engine rows for the same shipment (which it is by construction in the cost matrix). Defensive note: if cost_matrix.py ever stops replicating `real_total_eur` per engine row, this breaks silently. Worth a comment.

**FINDING D6 (LOW).** *Bias_table.md last refresh was 2026-05-15 ("Hermes added as 7th in-pool carrier").* Pre-DPD PL, pre-FedEx. The "Refresh cadence" section even still lists "6 engines"; no mention of DPD PL or FedEx fuel proxies. **Outdated by 7 days, two engines.**

### Per-carrier `report.py` — observations (spot-check 2 of 6)

Spot-checked `carriers/maersk/report.py` and `carriers/guell/report.py`.

**FINDING E1 (LOW, all 6 per-carrier reports).** *Decision rule is `cell_saving > 0` with no statistical floor.* Comment says "no minimum-saving threshold (the min_n filter alone removes statistical noise)". `MIN_CELL_N = 50` filters by parcel count, not by saving magnitude. A cell with n=50 and cell_saving = EUR 5 (~EUR 0.10/parcel) is treated as a "win". For decision-driving purposes this is over-eager; for diagnostic per-carrier rollups it's fine. **Status: consistent across all per-carrier reports.** A separate "decision-grade" threshold would be useful (≥ EUR 0.50/parcel?) but a deliberate non-decision per the docstring.

**FINDING E2 (MEDIUM, all per-carrier reports).** *They run against `cost_matrix.parquet` raw, without `invoice_adjustments.apply_invoice_adjustments`.* Only `decision_scorer.py` and `report.py` (decision report) apply OML/LPS. Per-carrier migration plans use raw `real_total_eur` including the UPS OML/LPS surcharges that will be refunded/halved. Per-carrier headlines therefore differ from the §B.13 scorer's `mandatory_saving` on UPS-overlap slices. Affects: any cell where current carrier = UPS. **Status: deliberate? Undocumented if so.** This is a numbers-must-agree audit hole.

**FINDING E3 (LOW).** *Per-carrier reports use `CARRIER_COLOURS` with `"DPD POLAND"` and `"DHL"` but no `"HERMES"` / `"FEDEX"` / `"DPD PL"` (the new-2026 spellings).* If the mart's `shipping_provider_group` ever surfaces those carrier names (e.g., a future invoice month with FedEx as current carrier), the per-carrier mix bars will color them `OTHER` (grey). Cosmetic.

---

## Part B — Cross-cutting implicit assumptions

For each: what's silently assumed; where it could matter; is it documented; magnitude if known.

**B1. Population replay window 2026 Q1 (3 months, Picanova-Stettin only)**
- *Silent assumption:* Q1 2026 carrier mix and lane volume are representative of the 6+12 month period the new contracts will cover.
- *Where it matters:* DPD UK was being phased out during Q1; Maersk implementation finished mid-Q1; pre-Hermes/pre-FedEx volume baseline. The "current mix" in `shipping_provider_group` is the **transition-state** mix, not the steady-state.
- *Documented?* `CLAUDE.md` decision framework says "2026 Q1 -- newest carrier mix; reflects current state including recent Maersk implementation." But there is no entry in ASSUMPTIONS.md noting that the Q1 baseline may already be obsolete by the time decisions land (Q3 2026).
- *Magnitude:* Maersk volume share on UK lane was 0 → ~100% mid-Q1. Re-running against Q1+Q2 would shift Maersk's incumbent share and re-base the OML/LPS UPS adjustment. **Likely EUR 50-100k swing** on the headline once Q2 is replayable.

**B2. Picanova-Stettin scope only (Wolfen out of scope)**
- *Silent assumption:* Stettin is representative of the carrier-selection decision; Wolfen will inherit the chosen portfolio.
- *Where it matters:* DPD PL engine ingested ORWO sheet ("source_sheet=ORWO") but its data is parked. If Wolfen has materially different lane distribution (heavier intra-DE, less CH/AT), the selected portfolio may be wrong for Wolfen. Same for AP whose AT line-haul is proxy'd from Wolfen → CH Hohenems.
- *Documented?* ASSUMPTIONS.md notes "Stettin → CH Hohenems rates proxied from Wolfen → CH Hohenems" for AP, but the **reverse** (using Stettin volumes to choose carriers for Wolfen) is not flagged anywhere.
- *Magnitude:* Unknown — depends on Wolfen volume profile, not in this codebase.

**B3. Country scope = 18 hard-coded destinations in `sql/population.sql`**
- *Silent assumption:* The 18-country whitelist (DE, FR, NL, IT, AT, ES, CH, SE, BE, DK, PL, LU, FI, IE, PT, NO, AU, NZ) covers all decision-actionable volume.
- *Where it matters:* Hermes engine lists 25 EU destinations; DPD PL lists 30; FedEx maps 86–222 territories; DHL Paket extends to non-EU intl. Any destination not in the 18 is silently dropped by SQL — engine eligibility there is dead code on this population. **Tail destinations (GR, HU, RO, BG, EE, LV, LT, SI, SK, HR, CY, MT) excluded** despite multiple engines covering them.
- *Documented?* `CLAUDE.md` 2026-05-12 country-scope decision is on the project root, but the *enforcement mechanism* (the SQL `IN (...)` list) is invisible from ASSUMPTIONS.md. Anyone reading `_decision_sets.py` would think the scorer covers all of EU.
- *Magnitude:* The 12 excluded EU destinations together likely ~3-5% of Picanova-Stettin Q1 volume (mid-tail). Bias unknown — those tails could favor carriers with broader networks (Maersk, DHL Paket) or specialists (Hermes/Güll on niche lanes). Could move headline by EUR 10-30k.

**B4. B2C-only / residential universally**
- *Silent assumption:* Every Picanova-Stettin shipment is residential B2C.
- *Where it matters:* DHL Express residential surcharge (waived per WA8), FedEx residential surcharge (not modelled, EUR 2.10-3.15M Q1 worst-case per DECISIONS 2026-05-21), every carrier with a B2B/B2C split. If even 1-2% of mart rows are B2B, residential surcharges over-apply.
- *Documented?* ASSUMPTIONS.md 2026-05-12 cross-carrier table row "Residential flag: All rows assumed residential". Yes, this one is documented.
- *Magnitude:* Quantified in ASSUMPTIONS: "~+1-3 EUR per misclassified shipment". On 500k shipments × 1% misclassified = ~EUR 5-15k. Acceptable.

**B5. Single-parcel-per-shipment grain**
- *Silent assumption:* Each mart row = one physical parcel; carriers bill per parcel.
- *Where it matters:* If a 30 kg shipment is split into 2x15 kg parcels, the mart has 2 trackingnumber rows — engines price each independently. This **matches** carrier billing per ASSUMPTIONS, so it's correct. But the scorer's `shipment_id` grain assumes 1 row per shipment_id and `decision_scorer.py:58` uses `.unique(subset="shipment_id")` — if any `shipment_id` has multiple trackingnumbers, only one is kept and the other is dropped.
- *Documented?* ASSUMPTIONS.md "Multi-parcel split: Each `shipment_id` row priced independently". Sort of — but the unique-by-shipment_id in the scorer contradicts this. Need to confirm whether `shipment_id` = `trackingnumber` in the mart or whether one shipment_id can have N tracking rows.
- *Magnitude:* If shipment_id is unique per row, no issue. If not, every multi-parcel shipment loses its non-first parcel's cost from the scorer. **Worth a one-shot count: `matrix.group_by("shipment_id").len().filter(pl.col("len") > engine_count).height`**. SQL pull selects `fs.shipment_id, fs.trackingnumber` — distinct columns. **Risk.**

**B6. No multi-year escalator scoring**
- *Silent assumption:* Year-1 rates are what we score on; year-2 / year-3 escalators ignored.
- *Where it matters:* Hermes 4% annual escalator (Q10), DHL Paket / other carrier escalators. Multi-year cost ranking could flip if some carriers escalate aggressively.
- *Documented?* ASSUMPTIONS Hermes section: "Annual escalator: not modelled (year-1 rates only); Multi-year scoring item; v1/v2 score year-1 only." Yes for Hermes. **Not** as a cross-carrier ASSUMPTIONS entry.
- *Magnitude:* 1% per year cap differential across carriers × 3 years × EUR 3M baseline = ~EUR 90k cumulative; small relative to other levers.

**B7. ECB FX placeholders (4.30 EUR/PLN, 1.05 EUR/CHF)**
- *Silent assumption:* Spot FX at v1 placeholder is good enough for ranking.
- *Where it matters:* FedEx rates are PLN-anchored (Stettin origin) — 5% FX swing = ~EUR 245k Q1 on FedEx total per DECISIONS 2026-05-20. Güll uses CHF/EUR = 1.05 for CH lane.
- *Documented?* Yes, per-carrier in ASSUMPTIONS (FedEx + Güll separately). **Not** as a cross-cutting framework assumption.
- *Magnitude:* Per-carrier; combined risk ~EUR 245k + ~EUR 16k = ~EUR 260k Q1 on a 5% combined FX move.

**B8. Wolfen-OOS but ORWO data in DPD PL rate tables — segmentation enforced?**
- *Silent assumption:* Engine knows to use Picanova rates not ORWO rates because the source_sheet column survives migrate.
- *Where it matters:* If `rate_tables_classic.parquet` mixes Picanova and ORWO rate rows and the forward-asof picks ORWO first by accident, DPD PL pricing on Picanova population could be wrong.
- *Documented?* DECISIONS 2026-05-20 mentions ORWO sheet parsed for traceability and "parked per project entity scope" — but the segmentation enforcement (which rows the engine actually queries) is not explicitly audited.
- *Magnitude:* Unknown without reading DPD PL engine internals. **Worth a one-shot audit: grep for `source_sheet` filter in `carriers/dpd_pl/calculate.py`.**

**B9. Cost-only scoring; service quality excluded**
- *Silent assumption:* The decision is fully captured by cost; transit time, returns quality, IT integration, account team are "qualitative" and not weighted.
- *Where it matters:* Hermes is a budget brand (lower service quality, longer transit) and currently leads the leaderboard purely on cost. FedEx is premium (Saturday delivery, transit guarantees) and currently uncompetitive on Picanova mix. A weighted-quality model would shift the ranking.
- *Documented?* `CLAUDE.md` Decision Framework: "Scoring: Cost only; qualitative concerns ... live in prose, not weights." Yes — but **not in ASSUMPTIONS.md** as the scoring-layer assumption. Worth promoting because it's the single most decision-shaping methodological choice.
- *Magnitude:* Not quantifiable in EUR; this is *the* boundary between what the analysis decides and what business judgement decides.

**B10. Volume tiers held at nominal — for all 9 engines**
- *Silent assumption:* Nominal-tier rates apply at any portfolio allocation.
- *Where it matters:* Routing 300k+ DHL Paket parcels to DHL Paket NEW_OFFER may push above committed-minimum; routing only 20k Hermes wins may drop below tier threshold and trigger penalty rates.
- *Documented?* PLAN.md §B.15 has this as a cross-carrier outreach item; ASSUMPTIONS.md per-carrier (DPD PL, Hermes, others) flags it. **Not** consolidated as one cross-cutting assumption.
- *Magnitude:* Cross-carrier framework Q; structural confidence interval on entire engine output.

**B11. AT fuel applied to base only (cross-carrier convention)**
- *Documented* (ASSUMPTIONS.md 2026-05-13). Apply across every AT-lane engine.
- *Magnitude documented* (~5-10% AT uplift if wrong).

**B12. "Comparable invoiced actuals" includes the SQL drop of 1.9% NULL rows**
- *Silent assumption:* The 1.9% population dropped at SQL level (`AND cs.total_eur IS NOT NULL`) is non-decision-actionable.
- *Where it matters:* This is the "off everything" tail. The headline EUR ~280k mandatory_saving is on the 98.1% slice. Stakeholders may not realize the 1.9% is excluded.
- *Documented?* CLAUDE.md Open Decisions notes "1.9% SQL-level NULL drop ... footnote in v2's Methodology section". Yes — but only in v2-report-todo, not as a live ASSUMPTIONS entry.

## Notes

- Confidence in scorer math: high. The bugs are upstream (curated decision-set list, hardcoded carrier rosters) not in the bid/cheapest aggregation.
- The biggest cross-cutting blind spot is the **18-country SQL filter** — half the engines are scoped for ~30 destinations but only score against 18. This collapses Hermes/DPD PL/FedEx coverage stories.
- Bias_table.md is the artefact most overdue for refresh — DECISIONS log shows 4 engine changes since 2026-05-15 (FedEx live, DPD PL reopened, AP scope expansion, multiple Maersk confirmations) all unreflected.
- Recommended next step: rebuild `cross_carrier_view.py` and `report.py` `CARRIER_ORDER`/`CARRIER_NARRATIVE` to be **data-driven** from `_decision_sets.CARRIERS` rather than hardcoded — would auto-pick-up future engines.

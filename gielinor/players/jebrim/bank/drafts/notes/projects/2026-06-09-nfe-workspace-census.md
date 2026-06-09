# NFE workspace census — 2026-06-09

> Full structured inventory of `Documents/GitHub/bi-analytics-main/NFE/` as of 2026-06-09, built by a 5-dwarf parallel recon pass (S-this-session, sid 91513c92). The **corpus anchor** for the [[nfe-repo]] digest (and a freshness source for [[eu-tender]] / [[carrier-contracts]] / [[scm]] / [[shipping-mart]]). The authoritative *live* anchors remain `NFE/CLAUDE.md` + `NFE/.claude/reference/`; this is the synthesized map + the drift list against the current digest.

**Path correction:** the workspace is at `Documents/GitHub/bi-analytics-main/NFE/` — the current digest drops the `GitHub/` segment. One of three git **worktrees** (`bi-analytics`, `bi-analytics-main`, `_bi-analytics-deploy`); see [[bi_analytics_deploy_topology]].

## Top-level layout (10 dirs — 6 absent from root CLAUDE.md's own Structure block)

`CLAUDE.md` (authoritative anchor) · `shipping_topics/` · `projects/` · `dashboards/` · `docs/` · `lib/` · `SHIPPING-COSTS/` · `operations/` · `trading/` · `CV/` · `playground/`.

The root `CLAUDE.md` Structure block lists only `.claude/ lib/ dashboards/ shipping_topics/ operations/` — it omits `docs/ SHIPPING-COSTS/ projects/ trading/ CV/ playground/`. The anchor is **stale, not wrong**: its *conventions* (imports, build, plotting, reports, agents) are accurate; its *directory map* is incomplete.

## `shipping_topics/` — 39 numbered ad-hoc folders (digest says ~41)

One-off carrier/cost investigations. **The convention claim in the digest is inaccurate:** no folder uses `DISCOVERY.md`/`FINDINGS.md` (that convention is fictional — findings live inline in `CLAUDE.md`'s "Key findings" section or a bespoke `summary.md`/`*_proposal.md`/marimo `main.py`); 11 folders have **no** `CLAUDE.md`; 5 are bare stubs ("To be filled in": 22_showcase, 25, 31, 35, 100_test); 3 are data-only with no docs/script (41, 43, 44). Numbering has gaps (no 1,10,11,14,15,16,20,32) and one duplicate (`22_` twice).

**What dominates:** carrier one-offs (~20 folders) — UPS heaviest (ORWO, TCG, DE, Rossmann, FIF, surcharged-pkgs), then DHL-ORWO (sperrgut-heavy), OnTrac, Asendia, DB Schenker, Gelato. ORWO is the single most recurrent subject. Recurring themes: (1) DHL-ORWO sperrgut/oversize surcharges (8,23,24,29,30,33), (2) expected-vs-actual cost modelling (3,6,9,21,26), (3) invoice DQ / dimension accuracy (27,36,45), (4) standing monitors (28,38,40).

**Version chains (latest = live)** — the folder is a scratch space where a question is re-attempted as data/method matures:
- UPS ORWO invoices: 13 → 17 → **19** (22_showcase is an abandoned stub off this line)
- Expected costs: 3/6 → **21**; OnTrac branch 3/12 → **26**
- Fuel surcharge: 34 → **37**
- DHL sperrgut: 8/23 → **29** (24/30/33 adjacent one-off DHL invoice pulls)

Loose root files: `main.py`, `sperrgut_packages.py` (marimo scratch). Feeds: mostly [[carrier-contracts]] + [[shipping-mart]]; the standing monitors (28/38/40/44) feed [[scm]].

## `projects/` — 6 multi-phase projects

- **`1_shipping_data_mart`** — mart **design/spec** phase (8 tables / 142 cols in `model/`, `data_model.html`, T-01…T-34 investigation threads). Pipelines never built. **Parked.** → [[shipping-mart]]
- **`2_EU_tender_2026`** — **active** (touched today). `1_offers/picanova/` (10 carriers) + `2_analysis/` (unified rate-card replay → `engines/` per-carrier calculators, `pipeline.py`, `cost_matrix*.py`, `decision_scorer*.py`; outputs `decision_report/ routing_2026q1/ switch_list_2026q1/ carrier_overview{,_v2}`) + `carrier_responses_to_open_questions/`. Scope: TCG-Picanova; ORWO/Sendmoments parked. → [[eu-tender]]
- **`3_shipping_data_mart`** — **active, live.** NOT a duplicate of 1_: this is the **talk-to-your-data agent harness over the *built* mart** (single `shipping-agent/` subfolder holding the canonical `reference/{mart-contract,coverage-audit,known-dq}.md` + `how_to.md` 42 KB + `harness/`). 1_ is upstream design; 3_ is the live runtime that project 4 and the shipping-agent consume. → [[shipping-mart]]
- **`4_automated_shipping_report`** — **active.** Senior-analyst snapshot-diff review (S124): deterministic harness *prepares evidence + ranks attention*, makes zero verdicts. Daily (cost-arrived diff + DQ canary) + weekly memo. `sql/snapshot.sql` (26-col gold query), `lib/diff_snapshots.py` (COST_ARRIVED/RESTATED taxonomy), `snapshots/` parquet spine. → [[scm]]
- **`5_shipping_savings`** — **active, largest by engine count.** 15 per-carrier re-rating engines (asendia, db_schenker, dhl_paket, dpd_pl, dpd_uk, fedex, gls, maersk_eu, maersk_us, ontrac, postnord, ups_eu, usps, yodel + `_base`); `contracts/` = EU (PICANOVA/ORWO/SENDMOMENTS) + US (6 carriers) rate-card tree; `specs/` per-carrier `.spec.md`; outputs `savings_by_lane.parquet`, `savings_summary.json`. **Root cluttered with ~50 `_*` scratch/probe files from a 2026-06-05 debug burst** (cleanup candidate). → **uncovered domain** (see below)
- **`_TTYD-template`** — talk-to-your-data scaffold (Redshift connect + semantic layer + HTML/Next.js builder); the reusable pattern 3_/4_ descend from. Template, not a project.

## `dashboards/` — Streamlit → Next.js migration

House stack: **Next.js 15 (App Router) + TypeScript + Tailwind + Recharts + DuckDB**; Python pipeline pulls Redshift → parquet, served by in-memory DuckDB, shipped as one Docker container (build from **repo root** as context). The digest's "descriptive name, no number = productized" rule **no longer disambiguates** — for 3 of 4 paired apps the *bare* name is legacy/partial and the `_nextjs` suffix marks the live one:

- **`shipping_costs_monitoring_nextjs`** = LIVE **SCM** (gold `shipping_mart`: `fact_shipments` + `fact_shipment_cost_summary`). `shipping_costs_monitoring_pre_refactor` = a local before-refactor snapshot (not git-tracked), not in the digest. → [[scm]]
- **`pcs_production_times_nextjs`** = LIVE (explicitly "replaces the Streamlit version"); bare `pcs_production_times` = **Streamlit legacy**.
- **`fulfillment_dashboard` + `_nextjs`** = two halves of one live app (bare = pipeline+data home; `_nextjs` = UI reading the sibling's parquets). Both current.
- **`tcg_organic_growth_nextjs`** = LIVE; bare = vestigial sim/extract script.
- **`shipping_invoice_details`** + **`POWER_BI/`** = **Power BI** (PBIP), stayed off the migration.

## `.claude/` — house tooling (digest under-counts)

- **`reference/` = 13 docs** (digest says ~6): `commentary-patterns, date-handling, docker-patterns, duckdb-api-patterns, house-style, nextjs-dashboard-patterns, nextjs-state-patterns, notebook-patterns, pipeline-data-flow, pipeline-patterns, recharts-gotchas, report-patterns, streamlit-patterns` + `shipping-data-mart/{overview,sources,tables}.md` + a `.zip`. Read-before-build, CLAUDE.md-triggered. Four (`house-style, report-patterns, notebook-patterns, commentary-patterns`) keep only NFE *wiring* and defer canonical taste to the brain's spellbook skills.
- **`agents/` = 3** (digest says 2): `schema-scout` (Redshift schema explore, haiku+MCP), `prior-work-researcher` (searches topic findings, haiku), `nextjs-dashboard-guide` (advisory, no-code, haiku). All auto-delegated.
- **`skills/` = 20 in 4 families** + standalone `overview-commands`: `analysis:*` (explore/quick-query/recall/save-finding), `reports:*` (pcs refreshes), `setup:*` (add-nextjs-tab/dockerize/initiate-repo), `workflow:*` (build-dashboard/notebook/report, data-quality, discover-data, discovery-sweep, perform-analysis, resume-topic, topics, wrap-up).
- **`hooks/`**: `post-marimo-check.sh` (auto `marimo check` on main.py edits), `pre-commit-check.sh` (block >1MB staged files). **`plans/`**: alerts_redesign, cost_drivers_tab, shipping_costs_launch_refactoring. **`prompts/`**: claude-code-knowledge-test.

## `lib/`, `docs/`, `SHIPPING-COSTS/`, other domains

- **`lib/`** — reusable modules: `analysis.py` (vol-weighted aggs, %change, shift-share, breach-rate, working-day), `quality.py` (DQ validation, largest), `report.py` (dark HTML report), `docs.py` (docs-page renderer), `style.py` (Plotly house style → exported to reference's house-style.md), `templates/{documentation,report}.html`.
- **Import pattern (verbatim, confirmed against CLAUDE.md):** two `sys.path` inserts — `parents[2]` → `NFE/` (`from lib.style/quality/analysis/docs import …`), `parents[3]` → repo root (`from shared.database import pull_data, push_data, execute_query, close_connection`).
- **`docs/shipping_contracts/`** — contract **source-of-truth** (feeds [[carrier-contracts]]): `0. OLD` (legacy: BUDG24, Metapack matrices, peak 2025, HS codes, nShift, per-country xlsx), `1. EU` (PICANOVA/ORWO/SENDMOMENTS), `2. US` (Asendia/Fedex/Maersk/OnTrac/P2P/USPS) + `OneDrive_1_6-9-2026.zip`. *Gitignored status unverified from NFE/ cwd — the ignore rule, if any, lives at repo root (not searched). The digest's "gitignored" claim is plausible but uncorroborated this pass.* Also `docs/`: framework-overview, nextjs_reporting, claude-code-practices(-v2), workflow-documentation, deployment-action-items.
- **`SHIPPING-COSTS/`** — older US-tender first pass. `carriers/` (dpd_uk, fedex, maersk_eu/us, ontrac, p2p_us(2), ups_us, usps, wwex) — `ontrac/` most built-out. **Surcharge-ABC lineage confirmed:** `shared/surcharges/base.py` (abstract base) → `carriers/ontrac/surcharges/*.py` (one module per surcharge: additional_handling, large_package, residential, delivery_area, over_maximum_limits + `demand_*` peak variants). This one-class-per-surcharge-off-a-base pattern is what the EU re-rating engines in `5_shipping_savings` ported.
- **`operations/`** — PCS production-times-heavy ops analytics (numbered topics, no folder CLAUDE.md) + Lyto/picaapi topics.
- **`trading/`** — personal crypto paper-trading toy (ccxt+polars engine + Next.js dashboard, fake money, JSON not parquet). Not a BI deliverable.
- **`CV/`** — Niklavs' personal CV artifacts ("Senior Business Data Analyst"). Not analysis work.
- **`playground/`** — single `shipping_data_mart/` exploratory mart sandbox (own CLAUDE.md, mart_audit/, 2025q1-vs-2026q1 analysis).

## Drift to fix in the [[nfe-repo]] digest (actionable)

1. **Path**: `bi-analytics-main/NFE` → `GitHub/bi-analytics-main/NFE`.
2. **shipping_topics count**: ~41 → **39** (+2 loose root files); numbering has gaps + a dup.
3. **Convention claim is wrong**: drop "DISCOVERY.md/FINDINGS.md + a main script" (fictional/inconsistent); ~28% of folders deviate (no CLAUDE.md / stub / data-only). Say "CLAUDE.md is the *common* lead, not a guarantee."
4. **projects**: split `1_/3_shipping_data_mart` — 1_ = parked design/spec, 3_ = live agent harness holding the canonical `reference/` mart contract.
5. **dashboards**: the `_nextjs` suffix marks the live app for pcs/tcg (bare = legacy) and SCM; `fulfillment` bare+nextjs are both live (split roles); note the `_pre_refactor` SCM snapshot.
6. **.claude/reference**: ~6 → **13** docs; **agents** 2 → **3** (+`nextjs-dashboard-guide`).
7. **Root CLAUDE.md Structure block is itself stale** (omits 6 of 10 dirs) — flag so the digest doesn't inherit the gap.

## Uncovered-cluster coverage decision (principal, 2026-06-09)

Domain-candidate review run off this census. Principal verdicts:

- **shipping-savings** (`5_shipping_savings`, 15 re-rating engines) — **REJECTED** ("that's a bad project"). No digest; re-rating discipline stays folded in [[eu-tender]] + [[carrier-contracts]].
- **production-times / fulfillment-ops** (operations/ PCS cluster + pcs/fulfillment dashboards + reports skills) — **ACCEPTED**, digested as [[production-times]]; principal will build on it and it **also owns delivery-promise cutoffs**.
- **bi-etl** (the Airflow→Redshift ETL repo, pipeline tracing) — **ACCEPTED**, digested as [[bi-etl]].
- **tcg-organic-growth**, **Lyto** — **REJECTED** (off-domain / not standing work).
- **Dashboard-productization method** (Next.js+DuckDB stack, `_TTYD-template`, the 13 reference docs) — not a domain; a **spellbook skill** gap (deferred).

## Corpus / provenance

Built by parallel dwarf recon over 5 regions (shipping_topics / projects / dashboards / .claude+lib / docs+other). Read-only; no NFE files touched. Supersedes the thin top-level map in the current [[nfe-repo]] digest. Next alch: re-synthesize the digest from this note (fix the 7 drift items) and decide the shipping-savings coverage call.

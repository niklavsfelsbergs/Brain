# Shipping-costs dashboard ↔ shipping-agent — interrelation & convergence

**As of:** 2026-05-24 (cost-basis alignment re-verified against ground truth — see Decision #3, now RECONCILED). Earlier body as-of 2026-05-22 ([[S026_2026-05-22_shipping-costs-nextjs-architecture-read|S026]] — dashboard-side cutover in-progress; convergence directions open). Re-verify before relying on coverage-hole-reporting status or "long-term direction" framing.

How the two surfaces over the shipping data mart relate today, where they diverge, and the convergence directions Niklavs has affirmed.

## The two surfaces

| | **Dashboard** | **Shipping-agent** |
|---|---|---|
| Path | `NFE/dashboards/shipping_costs_monitoring_nextjs/` | `NFE/projects/3_shipping_data_mart/shipping-agent/` |
| Role | **Monitor** — productized, always-on, fixed schema of questions | **Investigator** — ad-hoc Q&A, open schema |
| Cadence | Daily refresh via Airflow (08:00 Berlin), KubernetesPod refreshes parquets → S3 → pod restart | On-cue per query; harness in-folder (`connect_redshift.py …`) |
| Surface | 11 React tabs + two-queue alerts | Markdown/HTML/CSV artifacts under `visualization-studio/content/generated/<ai>/...` |
| Source | `enterprise_silver.shipping_data_mart` (post-cutover) | Same mart |
| Cognitive loop | *Known unknowns* — patterns we know matter, watched continuously | *Unknown unknowns* — questions no tab anticipates |
| Knowledge home | App's `CLAUDE.md` + README + `docs/*.html`. Vocab: [[shipping_costs_monitoring_nextjs_vocab]] | `shipping-agent/how_to.md` + `reference/{tables,sources,coverage-audit}.md` |

Audiences also differ in practice — dashboard for stakeholders/ops/regular consumption; agent for analysts (Jebrim, principal) chasing one-off questions.

## How they interrelate today

Both ride the same mart, but they don't talk to each other. Specifically:

- **Shared inputs, separate definitions.** The dashboard has codified a lot of operational vocab — `cost_for_routing`, the 11 buckets, the alert types, gap-and-island, frozen baselines, `trend_confirmed`, `real_cost_confirmed`. The shipping-agent's `how_to.md` is structured around the mart's schema, not the dashboard's analytical concepts.
- **No URL routing from agent → dashboard.** If a user asks the agent something the dashboard already answers (e.g., "is DE-DHL creeping?"), the agent re-queries Redshift instead of pointing at `/?tab=alerts&type=creep&country=DE&provider=DHL`.
- **Coverage holes asymmetry.** The [[S023_2026-05-21_shipping-mart-coverage-audit|S023]] audit surfaced four concentrated holes (ORWO POST 0%, Picturator POST_DVF 0%, MAERSK 68.9%, ASENDIA 0%). Agent has them in `reference/coverage-audit.md`. Dashboard's Completeness tab shows real-cost coverage % but doesn't currently distinguish structural holes (no bulk-bill source exists) from invoice-pending (invoice hasn't landed yet). **Niklavs confirmed ([[S026_2026-05-22_shipping-costs-nextjs-architecture-read|S026]]): the dashboard is currently wrong on this; it will be resolved.**

## Confirmed decisions ([[S026_2026-05-22_shipping-costs-nextjs-architecture-read|S026]], Niklavs)

1. **Dashboard ↔ mart alignment is incomplete.** Mart is source of truth; dashboard needs alignment work. Implication: the dashboard's mart-cutover branch is not the final state — more cutover work pending.
2. **Coverage-hole reporting in the dashboard is currently wrong.** Will be resolved. Until then, agent's `coverage-audit.md` is the authoritative source on structural holes.
3. **Cost-basis alignment between dashboard and agent — RECONCILED (verified 2026-05-24).** Both surfaces now default to the same real→expected coalesce:
   - Dashboard `cost_for_routing` = `COALESCE(real_shipping_cost WHERE >0, expected_shipping_cost)` — `pipeline.py:677-681`, documented `CLAUDE.md:136` ("Real + Expected").
   - Agent default = `fact_shipments.final_shipping_cost_eur` = `COALESCE(real, expected, avg)` — `shipping-agent/reference/mart-contract.md:85` ("the one number to use"), `how_to.md:240`.
   - **Residual tail difference, not a mismatch:** agent carries a third `avg` fallback (~2% of rows); dashboard stops at expected and guards `>0`. Note if a stakeholder-facing comparison needs exact parity, otherwise immaterial.
4. **Long-term convergence direction — open.** Not yet thought-through. Concrete near-term move: **agent could emit dashboard URLs** for questions the dashboard already answers (deep-link to `/?tab=...&filters=...`).

## Convergence directions

Pinned in order of leverage.

### Near-term: one-way deference (agent → dashboard)

The dashboard is the operational source of truth for analytical concepts. The agent should defer when those concepts come up.

- **Vocab pointer.** A `shipping-agent/reference/dashboard-vocab.md` (or section in `how_to.md`) referencing the dashboard's CLAUDE.md and the [[shipping_costs_monitoring_nextjs_vocab]] bank note. Defines: cost basis, alert types, period machinery, the 11 buckets — by pointing, not by restating.
- **URL routing.** When the agent recognizes a question already answered by the dashboard, it returns a dashboard URL alongside (or instead of) a fresh query. Requires the agent to know the dashboard's URL contract — short codes `?tab=...&countries=...&providers=...&from=...&to=...&bd=...&aq=...&al=...` (see vocab note's "URL param contract" section).

### Mid-term: shared definitions surface

A single canonical place where cost-basis recipes, alert-type semantics, period definitions live — read by both surfaces, not maintained in two places.

- Candidate location: the mart itself (column docs / view definitions). Closest to source-of-truth.
- Alternative: a reference subtree in `shipping-agent/` that the dashboard's docs link out to.
- **Risk if skipped:** the dashboard and agent quietly diverge as the mart evolves. A user asking both will get different numbers.

### Long-term: ask-the-dashboard layer

If the dashboard eventually hosts ad-hoc Q&A on top of its fixed tabs (Copilot-style), the agent's investigative role narrows — it becomes either (a) the engine behind the dashboard's ad-hoc layer or (b) the deeper-dive tool for questions that don't fit the dashboard's vocabulary at all.

Niklavs flagged this as "haven't thought that far." Don't over-architect; preserve optionality.

## Coupling opportunities (concrete)

Listed by reversibility — cheap-to-try first.

1. **Agent emits dashboard URLs.** Smallest move. Agent's response to "where do I see this" becomes `https://<dashboard>/?tab=alerts&type=creep&country=DE&provider=DHL`. No data sharing required.
2. **Agent reads dashboard's pre-computed parquets** for common questions. `daily.parquet` / `issues.parquet` / `deviations_summary.parquet` are sitting on disk or S3. For dashboard-answerable questions, this would be cheaper than re-querying Redshift. But: different freshness, different reach, and adds a coupling the agent doesn't currently have. Probably not worth the complexity at current scale.
3. **Shared reference docs.** Agent's `reference/dashboard-vocab.md` points at dashboard's CLAUDE.md; dashboard's docs link out to agent's `coverage-audit.md` for structural-hole context. Doc-level coupling, not code coupling.
4. **Shared cost-basis recipe in the mart.** ~Landed (verified 2026-05-24): the mart exposes canonical `fact_shipments.final_shipping_cost_eur = COALESCE(real, expected, avg)`; the agent reads it directly, the dashboard computes the equivalent recipe in `pipeline.py`. Not yet a *single* shared column the dashboard also reads (dashboard still rebuilds it in-pipeline from `shipping_cost`/`expected_shipping_cost`), so full single-source coupling is still open — but the recipe divergence this item worried about is closed.

## Open questions to resolve later

- **What's the long-term direction?** Investigative agent stays separate, or it becomes the engine behind dashboard's ad-hoc layer? Pinned for re-visit.
- ~~**Cost-basis recipe alignment.**~~ RESOLVED 2026-05-24 — recipes verified equivalent (Decision #3). Remaining open piece: whether the dashboard should read the mart's `final_shipping_cost_eur` directly instead of rebuilding it in `pipeline.py` (single-source coupling, coupling opp #4).
- **Coverage-hole resolution timeline.** When does the dashboard distinguish structural holes from invoice-pending? Until then, agent's audit is the canonical source — risk of silent disagreement.
- **`audit.py` / `backtest.py` rewrite** (dashboard-side, pre-cutover). Tangentially related — both surfaces would benefit from a working dashboard audit.

## Related

- [[shipping_costs_monitoring_nextjs_vocab]] — dashboard glossary, drafted [[S026_2026-05-22_shipping-costs-nextjs-architecture-read|S026]].
- shipping-data-mart routing — keepsake pin for the agent's home.
- [[shipping_mart_coverage_audit_2026-05-21]] — [[S023_2026-05-21_shipping-mart-coverage-audit|S023]] audit, where the structural holes were named.
- `inventory/dashboard-agent-convergence-resume.md` — parked quest covering the work above.

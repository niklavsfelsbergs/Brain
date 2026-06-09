---
domain: nfe-repo
title: NFE workspace — repo structure & where to find/do things
patterns:
  - nfe
  - nfe workspace
  - shipping_topics
  - bi-analytics
  - repo structure
  - where do i put
  - which folder
corpus:
  - bank/notes/projects/2026-06-09-nfe-workspace-census.md
  - bank/notes/projects/shipping_agent_vocab_harvest_2026-05-22.md
  - bank/notes/projects/bi_analytics_deploy_topology.md
specialist: null
freshness: 2026-06-09
synthesized: 2026-06-09
---

# NFE workspace — structure + where to do things

`Documents/GitHub/bi-analytics-main/NFE/` is Niklavs' personal analysis workspace (one of three git **worktrees** of bi-analytics — see [[bi_analytics_deploy_topology]]). The live anchors are **`NFE/CLAUDE.md`** (authoritative for *conventions*, but its directory map is stale — omits 6 of 10 top-level dirs) + **`NFE/.claude/reference/`**. Full inventory: [[2026-06-09-nfe-workspace-census]]. This digest is the map.

## Top-level layout (10 dirs)
- **`shipping_topics/`** — **~39** numbered `<n>_<slug>/` ad-hoc investigation folders (numbering has gaps + one dup). `CLAUDE.md` is the *common* lead but **not guaranteed** (~28% deviate: stubs, data-only, or a bespoke `summary.md`/marimo `main.py`; there is **no** DISCOVERY/FINDINGS convention). A re-attempt scratch space — questions recur as version chains (UPS ORWO 13→17→**19**, fuel 34→**37**, sperrgut →**29**); latest = live. Carrier one-offs dominate (UPS/DHL-ORWO sperrgut/OnTrac).
- **`projects/`** — multi-phase work. `2_EU_tender_2026/` (→ [[eu-tender]]), `4_automated_shipping_report/`, `5_shipping_savings/` (15 re-rating engines + `contracts/` — uncovered domain candidate), `_TTYD-template/` (talk-to-your-data scaffold). **`1_` vs `3_shipping_data_mart` are distinct:** 1_ = parked mart *design/spec*; **3_ = the live agent harness over the *built* mart**, holding the canonical `shipping-agent/reference/{mart-contract,coverage-audit,known-dq}.md` (→ [[shipping-mart]]).
- **`dashboards/`** — productized apps; **the `_nextjs` suffix marks the LIVE one** (bare name = Streamlit-legacy or pipeline-half). `shipping_costs_monitoring_nextjs` = [[scm]]; `pcs_production_times_nextjs`, `fulfillment_dashboard(+_nextjs)`, `tcg_organic_growth_nextjs`; `shipping_invoice_details`/`POWER_BI/` stayed Power BI. Build from **repo root** as Docker context.
- **`.claude/`** — `skills/` (20: `analysis/reports/setup/workflow:*`), `agents/` (**3** haiku, auto-delegated: schema-scout, prior-work-researcher, nextjs-dashboard-guide), `reference/` (**13** read-before-build pattern docs + `shipping-data-mart/{overview,sources,tables}`), `hooks/`, `plans/`, `prompts/`.
- **`lib/`** — reusable modules (style/quality/analysis/report/docs + templates). **`docs/`** — `shipping_contracts/` (contract source-of-truth → [[carrier-contracts]]) + framework/nextjs docs. **`SHIPPING-COSTS/`** — older US-tender first pass; `carriers/ontrac/` + `shared/surcharges/` = the **Surcharge-ABC lineage** the EU engines ported. **`operations/`** (PCS production-times), `trading/`, `CV/`, `playground/`.

## Where to do which work
- **Quick one-off shipping question** → new `shipping_topics/<n>_<slug>/` (next free number).
- **Multi-phase project with its own engines/data** → `projects/<n>_<name>/`.
- **Productized always-on surface** → `dashboards/<name>_nextjs/` (the live convention).
- **Reusable pattern / house style** → check `.claude/reference/` *before* building (Docker/nextjs/pipeline/report/recharts/duckdb all have a doc).
- **Mart schema/contract** → the external `picanova/shipping-agent` repo (richer than NFE's local copy) → [[shipping-mart]]; don't reason about the mart from memory.

## Import pattern (topic scripts)
Two `sys.path` inserts — `parents[2]` → `NFE/` (`from lib.…`) + `parents[3]` → repo root (`from shared.database import …`).

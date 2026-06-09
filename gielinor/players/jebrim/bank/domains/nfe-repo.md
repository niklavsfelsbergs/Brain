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
  - bank/notes/projects/shipping_agent_vocab_harvest_2026-05-22.md
  - bank/notes/projects/bi_analytics_deploy_topology.md
specialist: null
freshness: 2026-06-09
synthesized: 2026-06-09
---

# NFE workspace — structure + where to do things

`bi-analytics-main/NFE/` is Niklavs' personal analysis workspace (one of three git **worktrees** of the bi-analytics repo — see [[bi_analytics_deploy_topology]] for the worktree/deploy story). Organized into category subfolders with numbered topics. The authoritative live anchor is **`NFE/CLAUDE.md`** + **`NFE/.claude/reference/`** — read those for current detail; this digest is the map.

## Top-level layout
- **`shipping_topics/`** — ~41 **numbered ad-hoc** shipping analysis folders (`<n>_<slug>/`, e.g. `45_invoice_vs_mart_dimension_accuracy`). One-off investigations; each carries `CLAUDE.md` + `DISCOVERY.md`/`FINDINGS.md` + a main script. Where corporate vocab + carrier one-offs live.
- **`projects/`** — bigger multi-phase work: `2_EU_tender_2026/` (`1_offers/` + `2_analysis/` + `carrier_responses_to_open_questions/` → [[eu-tender]]), `4_automated_shipping_report/`, `5_shipping_savings/` (re-rating engines + `contracts/`), `1_`/`3_shipping_data_mart/`, `_TTYD-template/` (the talk-to-your-data scaffold).
- **`dashboards/`** — productized apps, **descriptive names, no number** (`shipping_costs_monitoring_nextjs` = [[scm]], `pcs_production_times`, `fulfillment_dashboard`, `tcg_organic_growth`, `shipping_invoice_details`) + `POWER_BI/`. Build from **repo root** as Docker context.
- **`.claude/`** — `skills/` (slash commands: `analysis-*`, `workflow-*`, `setup-*`, `reports-*`), `agents/` (`schema-scout`, `prior-work-researcher` — haiku, auto-delegated), `reference/` (pattern docs loaded by *read-before* triggers: nextjs/duckdb/pipeline/recharts/report/docker patterns + `shipping-data-mart/{overview,sources,tables}`), `hooks/`, `plans/`, `prompts/`.
- **`lib/`** — personal reusable modules (style, quality, analysis). **`docs/`** — `shipping_contracts/` (contract source-of-truth, gitignored → [[carrier-contracts]]) + framework/nextjs-reporting docs. **`SHIPPING-COSTS/`** — the older US-tender first pass; `carriers/ontrac/` + `shared/surcharges/` is the **Surcharge ABC lineage** the EU engines ported. **`operations/`**, `playground/`, `CV/`, `trading/` — other domains.

## Where to do which work
- **Quick one-off shipping question / investigation** → a new `shipping_topics/<n>_<slug>/` (number = next free).
- **Multi-phase project with its own engines/data/docs** → `projects/<n>_<name>/`.
- **Productized always-on surface** → `dashboards/<descriptive_name>(_nextjs)/`.
- **Reusable pattern / house style** → `.claude/reference/` (and check it *before* building — Docker, nextjs, pipeline, report patterns all have a doc).
- **Mart schema/contract** → the external `picanova/shipping-agent` repo is richer than NFE's local `.claude/reference/shipping-data-mart/` → [[shipping-mart]]; **don't reason about the mart from memory**.

## Import pattern (topic scripts)
Two `sys.path` entries — `parents[2]` → `NFE/` (personal `lib/`) + the repo-level `shared/`.

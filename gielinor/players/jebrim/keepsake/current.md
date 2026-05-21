# Jebrim — keepsake/current.md

> Read at respawn (when Jebrim is active). Pinned items that must surface every Jebrim session. Under size budget (~2k tokens). User-only; the agent proposes via `proposals/`.

## Shipping Data Mart — routing

Pinned 2026-05-21 (S015). Source: `proposals/archive/2026-05-21_shipping-data-mart-routing.md`.

**Primary how-to:** `bi-analytics-main/NFE/projects/3_shipping_data_mart_TTYD/how_to.md` — AI-facing deep how-to (pipeline overview, sources, structure, silver-layer reference, queries, Redshift connection harness, output modes, artifact rules, DQ). Read this first when shipping-data-mart work has an output (query, presentation, dashboard, audit, ad-hoc answer).

**Navigation map:** `bi-analytics-main/NFE/.claude/reference/shipping-data-mart/` (`overview.md` / `tables.md` / `sources.md`) — lighter sibling for table/source lookups when the structure is already understood.

**Ground truth:** `Documents/GitHub/bi-etl/dags/enterprise_silver/shipping_data_mart/` — per-folder READMEs. `git pull origin main` before reading the code for an audit/sanity check (mart moves fast).

**Outputs:** land per TTYD §7–§8 conventions — `visualization-studio/content/generated/<ai>/YYYYMMDD-HHMMSS--<slug>/` with `query.sql` / `data.csv` / `spec.json` / `index.html` / `bundle.json` as applicable.

**Update discipline:** when new gotchas / recipes / NULL classifications emerge from real work, update `how_to.md` (AI consumption) and `.claude/reference/shipping-data-mart/recipes.md` (human consumption; create if missing). Cross-update Jebrim's `bank/notes/` only when the learning is about methodology or routing, not mart specifics.

*Rotate out when TTYD `how_to.md` restructures / is superseded, or shipping data mart stops being a frequent topic.*

## EU Tender 2026 — active

Pinned 2026-05-21 (S021). Source: `archive/proposals/2026-05-21_eu-tender-2026.md`.

Quantitative review of 2026 EU shipping carrier tenders for TCG-Picanova. Target: 4–6 parcel + 1 freight, cost-only scoring. Phase 2 in flight; **DPD PL walkthrough is the next concrete step.** Decisions locked 2026-05-12 (cost-only, hard cap 6, lane diagnostic + portfolio scoring). New offers landing live (DPD PL + FedEx arrived 2026-05-20). Full detail in `bank/notes/projects/eu_tender_2026.md`.

*Rotate out when tender decisions are signed and carriers contracted, OR project pauses > 1 month with no active work, OR pin grows stale relative to current state.*

# Jebrim — keepsake/current.md

> Read at respawn (when Jebrim is active). Pinned items that must surface every Jebrim session. Under size budget (~2k tokens). User-only; the agent proposes via `proposals/`.

## Shipping Data Mart — routing

Pinned 2026-05-21 (S015). Re-pathed 2026-05-21 (S022) after restructure → `3_shipping_data_mart/shipping-agent/`.

**Primary how-to:** `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/how_to.md` — AI-facing deep how-to. Carries §0 (answering-question behaviors), §1 pipeline overview, §2 sources, §3 structure, §4 silver-layer reference, §5 query reference, §6 connection (local `.env`), §7 output modes, §8 artifact rules, §9 known DQ. Read this first when shipping-data-mart work has an output.

**Self-contained drill-down (siblings of `how_to.md`):** `shipping-agent/reference/tables.md` + `shipping-agent/reference/sources.md` — column-level table specs and per-source detail. Folder is self-contained: no outward path references from any `.md`.

**Older NFE-side reference (lighter, less detailed):** `bi-analytics-main/NFE/.claude/reference/shipping-data-mart/` — kept for navigation but the shipping-agent's local `reference/` is now authoritative for column-level work.

**Ground truth:** `Documents/GitHub/bi-etl/dags/enterprise_silver/shipping_data_mart/` — per-folder READMEs. `git pull origin main` before reading the code for an audit/sanity check (mart moves fast).

**Connection:** Redshift creds loaded automatically by the Python harness (`find_dotenv()` walks up from `db.py` and lands on `NFE/.env`). No local `.env` in `shipping-agent/` for now — the `ship_mart_ro` user was deprovisioned mid-session (no grants on the mart) and dropped. If a read-only demo user is needed later, restore a local `.env` here.

**Outputs:** land per §7–§8 conventions — `shipping-agent/visualization-studio/content/generated/<ai>/YYYYMMDD-HHMMSS--<slug>/` with `query.sql` / `data.csv` / `spec.json` / `index.html` / `bundle.json` as applicable.

**Update discipline:** when new gotchas / recipes / NULL classifications emerge from real work, update `shipping-agent/how_to.md` (AI consumption). Cross-update Jebrim's `bank/notes/` only when the learning is about methodology or routing, not mart specifics.

*Rotate out when `shipping-agent/how_to.md` restructures / is superseded, or shipping data mart stops being a frequent topic.*

## EU Tender 2026 — active

Pinned 2026-05-21 (S021). Source: `archive/proposals/2026-05-21_eu-tender-2026.md`.

Quantitative review of 2026 EU shipping carrier tenders for TCG-Picanova. Target: 4–6 parcel + 1 freight, cost-only scoring. Phase 2 in flight; **DPD PL walkthrough is the next concrete step.** Decisions locked 2026-05-12 (cost-only, hard cap 6, lane diagnostic + portfolio scoring). New offers landing live (DPD PL + FedEx arrived 2026-05-20). Full detail in `bank/notes/projects/eu_tender_2026.md`.

*Rotate out when tender decisions are signed and carriers contracted, OR project pauses > 1 month with no active work, OR pin grows stale relative to current state.*

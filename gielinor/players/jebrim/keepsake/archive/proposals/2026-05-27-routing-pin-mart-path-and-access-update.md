# Proposal — update the "Shipping Data Mart — routing" keepsake pin

**Proposed:** 2026-05-27. **Source:** [[S101_612683db_shipping-agent-access-split|S101]].

Two updates to the pinned "Shipping Data Mart — routing" item in `keepsake/current.md`:

1. **Ground-truth path moved.** The pin's "Ground truth" line names `bi-etl/dags/enterprise_silver/shipping_data_mart/`. Gold now builds at **`bi-etl/dags/shipping_mart/`** (top-level DAG; per-carrier provider SQL under `fact_shipment_invoice_lines/sql/providers/`). This is the pin's own stated rotation trigger ("when ground-truth path moves to the gold-dag location") — fire it.
2. **Access tiers (new line).** The shipping-agent now has two access tiers off one repo: colleagues on `ship_mart_ro` (gold-only); Niklavs full-access via a gitignored `CLAUDE.local.md` overlay + `.env` user `tcg_nfe` (verified read on `enterprise_silver`/`enterprise_bronze`/`dw`/`sl_gold`). Worth one pinned line so it surfaces on respawn.

**Suggested:** rewrite the "Ground truth" line to the new path; add a one-line "Access tiers" note. Leave the rest of the pin (schema list, `cost_source` values, schema discipline) intact.

# Jebrim — keepsake/current.md

> Read at respawn (when Jebrim is active). Pinned items that must surface every Jebrim session. Under size budget (~2k tokens). User-only; the agent proposes via `proposals/`.

## Shipping Data Mart — routing

Pinned 2026-05-22 (S028, post gold cutover). Supersedes 2026-05-21 pin.

**Schema.** Gold layer `shipping_mart` schema is the agent's entire surface — four facts, no joins outside the schema:
- `shipping_mart.fact_shipments` (wide fact, 66 cols — spine + provider data denormalized in)
- `shipping_mart.fact_shipment_cost_summary` (per-shipment 11-bucket cost pivot, invariant `SUM(buckets) == total_eur == fact_shipments.real_shipping_cost_eur`)
- `shipping_mart.fact_shipment_orderitems` (line-item rollup per shipment)
- `shipping_mart.fact_shipment_invoice_lines` (per-charge-line invoice detail with `charge_bucket`)

Cutover from `enterprise_silver.*` landed 2026-05-22 — old silver facts are **gone** (not deprecated views). `map_shipment_key` and `dim_shipping_providers` are not needed — their data lives on `shipping_mart.fact_shipments` directly. `fact_truck_charges` is out of scope.

**Shipping-agent (standalone).** Lives at `Documents/GitHub/shipping-agent/` (relocated 2026-05-22 out of NFE — escaped CLAUDE.md walk). Self-contained — runs anywhere with its own `.env` and `harness/`. Entry doc: `shipping-agent/README.md` (human) + `shipping-agent/how_to.md` (AI-facing rules + §1 "Where to find things" index). Reference content in `shipping-agent/reference/`; query methodology in `shipping-agent/skills/`.

**Connection.** Local `.env` in `shipping-agent/` with the `ship_mart_ro` user (read-only, gold-only). `harness/db.py` loads from the local `.env` only — does not walk up. Smoke-test: `python harness/connect_redshift.py --query "SELECT 1"`.

**Ground truth.** `Documents/GitHub/bi-etl/dags/enterprise_silver/shipping_data_mart/` per-folder READMEs — being repointed to gold (path stays for now). `git pull origin main` before reading the code for an audit/sanity check.

**`cost_source` values (2026-05-22):** `'invoice'` 65%, `'expected'` 24%, NULL/uncosted 8%, `'avg'` 2%. Column name is `real_shipping_cost_eur` but the flag value is `'invoice'` — naming asymmetry; future cleanup may align.

**Schema discipline.** Every query qualifies as `shipping_mart.<table>`. Reaching outside `shipping_mart.*` is a scope violation (and `ship_mart_ro` would deny it).

*Rotate out when ground-truth path moves to the gold-dag location, or scope/schema/credentials shift again, or the mart stops being a frequent topic.*

## EU Tender 2026 — active

Pinned 2026-05-21 (S021). Source: `archive/proposals/2026-05-21_eu-tender-2026.md`.

Quantitative review of 2026 EU shipping carrier tenders for TCG-Picanova. Target: 4–6 parcel + 1 freight, cost-only scoring. Phase 2 in flight; **DPD PL walkthrough is the next concrete step.** Decisions locked 2026-05-12 (cost-only, hard cap 6, lane diagnostic + portfolio scoring). New offers landing live (DPD PL + FedEx arrived 2026-05-20). Full detail in `bank/notes/projects/eu_tender_2026.md`.

*Rotate out when tender decisions are signed and carriers contracted, OR project pauses > 1 month with no active work, OR pin grows stale relative to current state.*

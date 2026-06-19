# shipping_mart — the `ship_mart_ro` grant surface (7 objects, only 4 readable)

**As of:** 2026-06-19 ([[S274_a1f05d25_shipping-agent-teaching-pass|S274]], live `has_table_privilege` check as `tcg_nfe`).

The `shipping_mart` schema physically contains **seven** objects, but the agent's role `ship_mart_ro` is granted SELECT on only the **four documented facts**:

| Object | ship_mart_ro SELECT? |
|---|---|
| `fact_shipments` | ✅ |
| `fact_shipment_cost_summary` | ✅ |
| `fact_shipment_orderitems` | ✅ |
| `fact_shipment_invoice_lines` | ✅ |
| `fact_truck_charges` | ❌ |
| `dim_transit_time_sla` | ❌ |
| `mart_status` | ❌ |

So the shipping-agent's four-fact contract is **exactly correct** — the other three are out of its reach by grant, not just by convention.

**The two ungranted objects worth a grant decision:**
- **`dim_transit_time_sla`** — `production_site × destination_country × us_state × size_bracket → sla_days` (with `valid_from/valid_to`). A canonical per-lane SLA table. Its existence **contradicts** the agent's how_to rule 16 ("the business has no agreed target delivery time"). If `ship_mart_ro` were granted it, the agent could do SLA-aware on-time analysis instead of "state your assumed threshold."
- **`mart_status`** — `table_name, status, updated_at, last_success_at, last_failure_at`. A per-table freshness/pipeline-status signal. If granted, the agent could read reload/staleness **deterministically** (rule 36 + SCM refresh-lag) instead of inferring from systemic NULLs.

**`fact_truck_charges`** (linehaul) stays out of scope and unreadable — consistent with the agent treating linehaul as not answerable from its four facts.

Cross-link: [[shipping-mart]] digest (currently says "four facts" — accurate for grants; could note the 3 ungranted siblings). Decision pending with principal on the two grants.

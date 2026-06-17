---
quest: S259_shipping-quota-three-way-archived-anchored
sid8: 5463f8a7
ts: 2026-06-17 18:30
open_dep: none
---

**Status:** in-progress (deliverable shipped; reuse-dependent follow-ups only)

**Where we are:** Three-way 2026 monthly shipping-cost quota (SCM / date-anchored / Accounting) delivered as CSV + two formatted Excel files. v2 (Wolfen included) is the current cut. Anchored column corrected after a cost-dating bug. Final v2 YTD: SCM 18.72% / anchored 19.54% / Accounting 18.88%.

**Next concrete step:** None outstanding. If the series is reused, the principal should pick the anchored **cost basis** — reconciled `real_shipping_cost_eur` (used, SCM-comparable) vs literal invoice-line freight sum (~8% lower, ~17.9% YTD). Optional: align Accounting's exact "Europe" population (order sources + sites) for a true absolute-cost/revenue reconciliation, not just quota.

**Files / paths to read first:**
- `gielinor/players/jebrim/quest-log/in-progress/S259_5463f8a7_shipping-quota-three-way-archived-anchored.md`
- `Documents/GitHub/shipping-agent/scratchpad/20260617-shipping-quota-three-way-jan-may-2026-v2-wolfen.xlsx` (+ `.csv`, + non-Wolfen v1 xlsx, + `build_quota_xlsx_v2.py`)
- `gielinor/players/jebrim/bank/domains/scm.md` (cost-basis rules)

**Key method (corrected):** invoiced cost = reconciled `real_shipping_cost_eur` dated by `fact_shipment_invoice_lines.shipment_date` (archived-date fallback where line ship date null); expected-only shipments + revenue by `dw.sales_fact.archivedtime`. Scope: `source_system IN ('Picturator','PicaAPI')`, `production_site NOT IN ('PCS CMH','PCS MI','PCS PX')`. Do NOT use `received_by_carrier_date` (sparse → drops cost).

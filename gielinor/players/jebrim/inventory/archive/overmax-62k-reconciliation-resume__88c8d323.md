---
quest: S260_overmax-reconciliation-and-spawn-policy-fix
sid8: 88c8d323
ts: 2026-06-18 00:00
open_dep: none
---

**Status:** done — quest closed.

**Where we are:** Both asks resolved. (1) The manager's "€62K over-max surcharges vs €19K" fully reconciled: €61,731.94 = total cost of 47 over-max (OVR/OML) UPS parcels on the **order-month** (`shop_order_created_date`) lens — reproduced to the cent on `shipping_mart.fact_shipments`; the sub-agent was correct, only the word "surcharges" was the slip (it's total parcel cost; the actual over-max surcharge is ~€21K). €56,445 = same cohort on transaction-date (43 parcels). ~€19–21K = the over-max surcharge *line* by invoice date (the manager's report). (2) Spawn-policy false-trigger fix applied to `players/jebrim/spellbook/skills/calling-the-shipping-agent.md` + `players/jebrim/CLAUDE.md` (litmus: one-query-after-reference → run yourself; topic phrase ≠ spawn trigger).

**Next concrete step:** none — quest closed. Optional, only if the principal returns to it: decompose the €61,732 / 47-parcel cohort by charge type on the order-month basis for a clean take-back; or cut the cohort by invoice date to match the Invoice Details report lens exactly.

**Files / paths:**
- `players/jebrim/quest-log/completed/S260_88c8d323_overmax-reconciliation-and-spawn-policy-fix.md`
- `players/jebrim/spellbook/skills/calling-the-shipping-agent.md` (litmus added)
- `players/jebrim/CLAUDE.md` (spawn bullet)
- 2 examine drafts (2026-06-18): vary-the-date-lens / define-population-off-charge-code.
- Source: `enterprise_silver.ups_invoices` (UPS direct stream; gold lacks the over-max line detail).

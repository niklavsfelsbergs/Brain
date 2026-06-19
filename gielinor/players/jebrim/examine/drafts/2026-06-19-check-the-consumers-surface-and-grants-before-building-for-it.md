# Check the consumer's existing surface + real grants before building for it

**Observed:** [[S274_a1f05d25_shipping-agent-teaching-pass|S274]] (a1f05d25), teaching the shipping-agent. Two near-misses, both caught only by checking ground truth rather than building from my survey:

1. I scoped "E — timing-signal semantics" as a new build. Before writing, I read the agent's existing `reference/known-dq.md` and found the received_by_carrier / departure_ts / lead-time content **already there** — E would have been duplication.
2. The dimension/timing work pointed at `fact_truck_charges`, `dim_transit_time_sla`, `mart_status`. A live `has_table_privilege('ship_mart_ro', …)` check showed the agent's role is granted only the **4 documented facts** — those 3 objects exist in the schema but are **unreadable** by the agent. Documenting them as usable would have been wrong.

**Rule:** when building or documenting *for a consumer* (an agent, a role, a downstream job), verify two things first against ground truth, not memory: (a) what that consumer's surface **already covers** (don't duplicate), and (b) what it can **actually access** (grants/permissions, not just schema existence). My distilled menu was a hypothesis about gaps; the agent's real reference + `ship_mart_ro` grants were the truth. Both checks were cheap and both changed the build.

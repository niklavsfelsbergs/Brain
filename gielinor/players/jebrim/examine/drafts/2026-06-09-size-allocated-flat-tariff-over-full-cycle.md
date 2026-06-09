# Size an allocated per-unit cost over a full demand cycle, not a partial window

**Observation ([[S172_df374cef_dhl-truck-cost-warenpost-kleinpaket|S172]], 2026-06-09).** I sized the Warenpost truck cost from `fact_truck_charges` on **2026 YTD** (Jan–Jun) and recommended €0.78/parcel. Niklavs corrected: the tariff is a flat €284/load, so per-parcel cost is **purely a truck-fill artifact** — and YTD misses Q4 peak fill, where trucks run full and per-parcel drops hard. FY2025 weighted = €0.46 (Dec floor €0.29 at 976 parcels/load; Feb ceiling €1.04). My window overstated by ~70%.

**Rule.** When a per-unit cost is an **allocation of a fixed periodic charge** (flat tariff ÷ variable volume), the per-unit figure is dominated by the fill/utilisation rate, not by price. Size it over a **full demand cycle** (a complete year), not a partial or single-quarter window — a partial window silently encodes that window's fill state. Volume-weight; never average the per-unit column unweighted (light periods inflate it). Flag the season spread, but default to the full-cycle weighted figure unless the deliverable prices at sub-annual granularity.

**Generalises** beyond shipping — any amortised/allocated cost off a fixed charge. Cross-conv memory written.

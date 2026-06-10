# Shipping-agent pull (emulated): truck-scan data quality coverage by production site

**Asked by:** Jebrim (principal) — internal DQ audit.
**Scope resolved:** all production sites combined-then-split; primary window Q1 2026 (order_produced_date Jan–Mar, fully closed). Tier: upstream profile present (tcg_nfe), but the answer lives on the GOLD contract — no off-contract figure needed.

## Turn-by-turn
- Loaded how_to.md (full) + tables.md + known-dq.md + CLAUDE.local.md (full-access profile confirmed: enterprise_silver/bronze in scope).
- Located the truck-scan signal: NOT in gold as a named "scan" field, and NOT fact_truck_charges (that's truck COST, out of gold scope). The carrier-side "scan" cols in bronze (usps first_scan, yodel first_physical_scan, ontrac first_scan, dpd scandate) are carrier-network delivery scans — wrong thing.
- The truck-LOADING signal = the PCS truckload chain (pcs_truckloads → pcs_truckloadunits → pcs_loadingunits), surfacing on gold fact_shipments as `truckload_id` (+ `truckload_assigned_ts`, `truckload_closed_ts`, `loading_unit_id`). Defined coverage = parcel has a non-null truckload_id (a scan onto an internal truckload at origin).
- Verified truckload_id and truckload_assigned_ts are perfectly co-populated per site/month → genuinely measured, not populate-by-default.
- Computed coverage by production_site, Q1 2026, all-source + TCG-only cuts. Checked MoM stability (no MTD distortion — production-time event), PCS CMH 29% is a real partial (24–35% stable), all-time 17-site map.

## Headline
- Truck-scan is a **PCS-internal-site-only** signal. Q1 2026: **PCS PL 92.7%** (656k parcels), **PCS CMH 29.0%** (136k), **PCS PX ~0%**, **Wolfen 0% by design** (photo lab, no internal truck leg), all external producers 0%.
- Overall Q1 coverage ~44%, driven entirely by site mix (Wolfen's huge 0% denominator).
- Vertical (TCG vs all) barely moves per-site %; it only shrinks Wolfen's denominator. So no vertical gate needed for the site numbers.

## Caveats
- Wolfen/external 0% = empty-by-design (truck loading is PCS-internal), not a defect.
- PCS PX near-0% despite being a PCS site = genuine gap worth flagging (parcels there don't get truckloads / not wired).
- PCS CMH 29% = genuine partial-coverage, not lag.
- tables.md (stamped 2026-05-25) is stale on site names + column list — live fact_shipments has truckload_assigned_ts / truckload_closed_ts not documented there, and Q1 sites are PCS PL/CMH/PX not the documented CGN/Other. Flagged to principal as a rulebook gap.

Deliverable: chat-only (findings returned to Jebrim). No chart requested.

---
quest: S192_db-schenker-reroute-package-dims
sid8: 384c1c27
ts: 2026-06-10 18:15
open_dep: bi-etl lineage trace on shipping_mart.length_cm (zV template provenance) — not started, non-blocking
---

# Resume — DB Schenker reroute: package dims + savings

## Status
in-progress (analysis shipped; one non-blocking follow-up).

## Where we are
On current HEAD (bi-analytics a96e449, maersk-3.2.0, girth = L+2W+2H confirmed): the DB Schenker switch moves **4,490** parcels → Hermes 4,463 / Maersk 27, Q1 saving ~€99.7k (committed routing report books reroute €107,684). The Maersk oversize lane collapsed (was 2,924). Dim provenance: CUSTOM_OVERSIZED real/varying (routable), zV templated (NOT measured — 85% of the switch saving, all Hermes), GEL constant (0 move, stays DBS). Routing commits per (dest×packagetype) cell, not per parcel.

## Next concrete step (offered, not started)
Run a **bi-etl lineage trace on `shipping_mart.length_cm`**: is the zV templated value a packaging-SKU spec (constant by design) or a defaulted field, and does a real per-parcel measurement exist upstream (order-entry / WMS / product spec) we could substitute? If a real dim source exists, the €85k zV→Hermes saving firms up; if not, we're routing on a template assumption and the report should say so. The 3 casing variants of "zugeschnittene Verpackung" are the provenance lead (likely 3 source systems). Question for Niklavs: spawn a dwarf to run the bi-etl trace, or defer?

## Files / paths to read first
1. `players/jebrim/bank/drafts/notes/projects/2026-06-10-db-schenker-reroute-package-dims-and-savings.md` — the findings (this session).
2. bi-analytics `2_analysis/carriers/maersk/constants.py` (3.2.0 ceiling) + `routing_2026q1/validation/db_schenker/` (NOTE: the committed .parquet/.html there may lag a re-run — re-derive from `cost_matrix_2026q1` + `routing_assignment.parquet` for current numbers, as this session did).
3. `bank/domains/bi-etl.md` — the lineage-trace workflow for the dim-column trace.
4. Quest-log: `quest-log/in-progress/S192_384c1c27_db-schenker-reroute-package-dims.md`.

## No pending external actions.

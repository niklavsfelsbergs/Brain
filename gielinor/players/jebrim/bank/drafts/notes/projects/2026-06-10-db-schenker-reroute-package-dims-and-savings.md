# EU Tender 2026 — DB Schenker reroute: package dimensions + savings realism (2026-06-10)

> Draft (harvest, [[S192_384c1c27_db-schenker-reroute-package-dims]] sid8 384c1c27). Investigates which packages the final routing switches off DB Schenker → Hermes/Maersk and how real the savings are, on **current HEAD a96e449 / maersk-3.2.0** (girth = L+2W+2H confirmed). Supersedes the per-slice numbers in the S164 [[2026-06-08-eu-tender-db-schenker-reroute-validation]] note (that was 3.1.0 / pure-girth). Promote at next Jebrim alch.

## Current switch (maersk-3.2.0, girth ceiling = `length_plus_girth_cm` ≤ 300)

DB Schenker Q1 incumbent = 8,951 parcels. The final routing moves **4,490** off → **Hermes 4,463 + Maersk 27**. The rest (4,461) stay on DB Schenker (freight 4,191 incl. must-freight, + not-in-6 + price-retained).

**Q1 saving on the switch ≈ €99.7k** (my per-type derivation; the committed routing report books the reroute at **€107,684** — small methodology gap, not material to shape). By package type:

| Package type | Parcels | Saving € | Carrier |
|---|---|---|---|
| zV (cut-to-size) | 3,874 | **85,217** | all Hermes (€22.00/pc) |
| CUSTOM_OVERSIZED | 616 | 14,505 | Hermes 589 (€13,012) + Maersk 27 (€1,492) |
| GEL VERSANDTASCHE klein | **0** | 0 | none move (stays DBS) |

**The switch is now almost entirely a Hermes play.** The L+2W+2H girth confirmation collapsed the Maersk oversize lane (2,924 → 27 parcels). GEL no longer moves at all. So **85% of the DB Schenker switch saving sits in zV → Hermes** — and that is exactly the package type with the weakest dimension data (below).

## Package-dimension provenance — the load-bearing finding

The system dims for these parcels split hard by packagetype. Profiled the Q1 mart pull (`data/population_2026q1.parquet`, all carriers); confirmed the dims are raw-mart pass-through, no nominal substitution in the cost-matrix path:

- **CUSTOM_OVERSIZED — genuinely varying, real measurements.** 858 distinct L×W×H tuples across 2,732 DBS parcels; length 22–200 cm; most-common shape only ~9.5% of the slice. `volume_cm3` == L×W×H exactly (100%) → volume is *derived* from dims, gives no independent cross-check. Clean enough to route on (14 zero-dim sentinels to exclude). Routable.
- **zV (zugeschnittene Verpackung) — templated, NOT measured.** 99.4% of all zV (5,036 of 5,068) are two near-identical flat templates (~130.3×91.6×7.6). Dims don't track weight (0.3–21 kg all at the same template). **This is the €85k slice.** We do not actually know the true dims of the parcels we're routing to Hermes — only that the template clears Hermes' caps (girth 328.7 vs 360, ~31 cm headroom).
- **GEL VERSANDTASCHE klein — fully constant.** 1 tuple (182×85×20) for every parcel. Template-driven. Moot now (0 move).

### Casing variants are a provenance marker ([[S192_384c1c27_db-schenker-reroute-package-dims|S192]] correction to an over-claim)
Cut-to-size exists in 3 casing variants — `zugeschnittene Verpackung` (z/V), `Zugeschnittene Verpackung` (Z/V), `zugeschnittene verpackung` (z/v). My first read ("UPS carries real dims for this packagetype, so the template is a DB-Schenker-specific default") was **wrong**: it picked the one casing pocket that varies (z/V on UPS, 227 parcels, 29 shapes). UPS's *bulk* of cut-to-size is the Z/V variant (1,482 parcels) and that is **constant** too. So the templating is a property of the packaging type generally, on both carriers — **not** a DBS integration quirk. The 3 spellings almost certainly mark 3 source systems / integration paths writing the field — a lead for a bi-etl lineage trace on `length_cm`.

## Operational constraint — routing commits per cell, not per parcel
`build_final.py:8` — STANDARD packagetypes route per **(destination × packagetype) cell**; VARIABLE types (GEL/CUSTOM_OVERSIZED) flagged "by dims." A cell goes wholesale to one carrier, so that carrier must absorb the **full dimension range** in the cell — operations can't peel off the oversize tail without per-parcel dimension-based routing at the packing station (a WMS capability question, unconfirmed). This is *why* the dim question is operational, not academic: the carrier eats whatever dims occur in its cells.

## Open / next
1. **zV dim provenance (now the dominant uncertainty on the whole switch):** bi-etl lineage trace on `shipping_mart.length_cm` — is the templated value a packaging-SKU spec (constant by design) or a defaulted field, and does a *real* measurement exist anywhere upstream (order-entry / WMS / product spec) we could substitute? If yes, the €85k firms up; if no, we're routing on an assumption and must say so.
2. GEL: confirmed stays on DB Schenker (0 move). Closed.
3. CUSTOM_OVERSIZED: dims real → routable; the residual was the Maersk ceiling, now resolved unfavorably (Maersk down to 27). Effectively closed.

Links: [[eu-tender]] digest, [[2026-06-08-eu-tender-db-schenker-reroute-validation]] (superseded numbers), [[eu_tender_2026]].

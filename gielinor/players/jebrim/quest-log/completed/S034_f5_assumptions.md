# S034 F5 -- ASSUMPTIONS.md cross-carrier additions

**Spawned by:** Jebrim, 2026-05-22
**Scope:** Append 6 implicit-assumption entries surfaced by the S034 D7 audit to `2_analysis/docs/ASSUMPTIONS.md` Cross-carrier / framework section; audit population SQL grain for entry #4.

## Output landed

Six entries inserted into `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics-main\NFE\projects\2_EU_tender_2026\2_analysis\docs\ASSUMPTIONS.md` immediately after the 2026-05-13 AT fuel / Maut entry, before the `## Maersk` (post-reply) section. All six dated **2026-05-22** and tagged **(S034 F5)** for traceability.

Each entry follows the existing prose-entry shape (one-line claim + **Why we're assuming** + **Impact if wrong** + **Replace when** + **Related**). Two of the existing cross-carrier entries use the table-shape; the six new entries use the prose-shape since each carries a single load-bearing claim rather than a row-by-row matrix.

### Entries appended

1. **18-country IN(...) whitelist excludes 12 EU tails** -- enforcement lives in SQL but is invisible from `_decision_sets.py`; ~3-5% Q1 volume bias.
2. **Cost-only scoring; service-quality unweighted** -- promotes the CLAUDE.md Decision Framework choice into ASSUMPTIONS. Structural, not numeric.
3. **2026 Q1 replay is transition-state** -- Maersk mid-Q1, pre-Hermes, pre-FedEx; EUR 50-100k swing once Q2 replayable.
4. **`.unique(subset="shipment_id")` may drop multi-parcel rows** -- includes the population SQL audit finding below.
5. **Maersk DE DHL Routing Code 0.49 EUR/parcel silently zero** -- Row 161 of Other Surcharges sheet; ~EUR 137k Q1 if always-on.
6. **Bias table staleness reminder** -- last refresh 2026-05-15; 4 engine/constant changes since; flag in PLAN.md cleanup.

## Population SQL grain audit (entry #4)

**File:** `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics-main\NFE\projects\2_EU_tender_2026\2_analysis\sql\population.sql`.

**Finding.** The SELECT pulls `fs.shipment_id, fs.shop_ordernumber, fs.trackingnumber, ...` from `enterprise_silver.fact_shipments fs LEFT JOIN enterprise_silver.fact_shipment_cost_summary cs USING (shipment_id)`. No `DISTINCT`, no `GROUP BY`. The fact_shipments mart grain (per the 2026-05-12 cross-carrier entry already on file) is **one row per trackingnumber**, not per shipment_id.

**Implication.** The query is trackingnumber-grain. The 2026-05-12 cross-carrier entry already documents this for engine pricing ("each `shipment_id` row priced independently ... a 30 kg shipment split into 2x15 kg parcels is 2 rows") -- which is correct for engines, since the cost matrix prices each row.

The inconsistency is at the **scorer** boundary: `decision_scorer.py:58` does `.unique(subset="shipment_id")`. If any shipment in the Q1 population has N>1 trackingnumbers, the scorer keeps 1 of N rows and drops the rest from its per-shipment roll-up. Engines still price each parcel; the scorer just doesn't see the dropped ones.

**Magnitude unaudited.** Picanova's product mix is dominated by single-parcel canvases / photo books / mugs, so the multi-parcel tail is plausibly small (<2%) -- but the audit isn't done. The one-shot count to run against the live cost matrix:

```python
import polars as pl
matrix = pl.read_parquet("2_analysis/data/cost_matrix.parquet")
n_multi = (
    matrix
    .group_by("shipment_id")
    .agg(pl.col("trackingnumber").n_unique().alias("n_tracks"))
    .filter(pl.col("n_tracks") > 1)
    .height
)
print(f"shipments with >1 trackingnumber: {n_multi}")
```

If `n_multi == 0`, the scorer is correct and entry #4's risk is dead. If `n_multi > 0`, the scorer either needs re-keying to `(shipment_id, trackingnumber)` or the de-dupe removed. **Not running the count from this dwarf** -- requires Polars + Parquet read I have no need to invoke for the F5 task; flagged for the principal to schedule alongside scorer cleanup (D7 finding A2).

## Entry #5 anchor verified

**Maersk DE DHL Routing Code 0.49 EUR/parcel** -- Row 161 of Other Surcharges sheet in the Maersk offer workbook. Cross-referenced in entry #5's prose. Engine impact estimate ~EUR 137k Q1 / ~EUR 274k 6-mo computed as `0.49 EUR x ~280k DE Maersk parcels` (DE Maersk volume rough estimate; refine if cost_matrix shows different DE-lane Maersk parcel count).

## What I did NOT touch

- Did not modify `_decision_sets.py`, `cost_matrix.py`, `decision_scorer.py`, or any engine module. F5 is documentation-only; engine wiring per D7's other findings is principal-scope.
- Did not modify `bias_table.md` or PLAN.md. Entry #6's "flag in PLAN.md cleanup work" is a recommendation, not a write.
- Did not run the live multi-parcel count against `cost_matrix.parquet`. Surfaced as a one-shot the principal can schedule.

## Hand-off

Six entries live in ASSUMPTIONS.md ready for the next decision-report rebuild. The population SQL grain finding is documented inside entry #4 with a runnable audit query. F5 closes.

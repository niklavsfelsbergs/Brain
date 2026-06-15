# Verify each field's source TABLE before promising differential coverage

**Date:** 2026-06-15 · **Session:** [[S243_f6d41a0d_ups-lps-oml-2026-surcharge-export|S243]] (f6d41a0d) · **Player:** Jebrim · **Status:** draft (Q5 correction harvest)

## The moment
On the UPS LPS/OML 2026 export, I told the principal that only *their* invoice dims (`packagedimensions`) would be retention-limited, and that *our* PCS dims (`detailkeyeddim`) plus surcharge/ordernumber/packagetype would be **fully populated** across 2026. Wrong. `detailkeyeddim` lives in the **same** bronze table (`csv_ups_zip_invoicedata`, ~3-mo zip retention) as `packagedimensions` — so both dim columns were sparse (Jan/Feb NULL), not just UPS's. The shipping-agent sub-agent caught it and flagged it rather than silently swapping the source; fixed by sourcing our_dims from gold `fact_shipments` (full-year).

## The lesson
I reasoned about coverage from the *semantic role* of the fields ("ours" vs "theirs") and assumed different roles meant different sources with different retention. They didn't — both were two columns on the **same physical invoice row**. A field's coverage is a property of the **table it's stored in**, not of whose number it conceptually is.

**Rule:** before promising that column A is fully populated while column B is sparse, confirm each column's *source table* (and that table's retention/coverage), not its meaning. Two fields that feel like different sources ("our declared" vs "their measured") can share one table and one retention window. Cheap check: name the table each column comes from before making any per-column coverage claim.

## Anchor
[[S243_f6d41a0d_ups-lps-oml-2026-surcharge-export|S243]] export; the v1→v2 backfill from gold was the fix. Sibling of [[feedback_populated_column_is_not_a_measurement]] (provenance ≠ population) and the broader verify-the-thing reflex (don't trust the inferred shape of a source).

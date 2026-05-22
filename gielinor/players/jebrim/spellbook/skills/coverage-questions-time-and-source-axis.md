# Skill — coverage questions get a time slice and a source axis

**Captured:** 2026-05-21 (S023, shipping mart coverage audit).

## The rule

When the question is shaped like *"what's the coverage of X?"* or *"why is X missing for Y?"*, the answer must slice by **time (month)** and **source (or whatever the ETL atom is)** before any narrative claim.

## Why

A NULL or zero rate without those two axes blends three different causes into one misleading number:

1. **Invoice lag** — current-month parcels whose carrier bills haven't arrived yet. Normal cadence; resolves on its own. Picturator/PicaAPI carriers run 20-28% NULL on the in-flight month.
2. **Historical defect** — was broken in a specific window, since fixed. Bounded; named months.
3. **Structural gap** — no source wired. Permanent until ETL ships one. Stable at near-0% every month.

Each gets a different answer. Aggregate without time slice presents all three as the same thing.

A coverage % without the source axis also blends mid-build sources (where 0% revenue is intended) with stable ones (where 0% revenue is a defect). The narrative ("the mart is broken") is wrong; the diagnosis ("ORWO is V1-active-build") is the right one.

## The anchor

Founding observation (S023, 2026-05-21): another agent (`shipping-agent` TTYD instance) saw "Wolfen→DHL = €0" on a uk.photo.gifts probe and concluded "Wolfen's carrier-cost wiring is still being wired up." A month-by-month read of ORWO DHL across the mart showed 97-99% coverage Nov 2025 → Apr 2026, with the €0 readings concentrated in the current in-flight month (invoice lag) and a fixed Nov-Dec 2025 UPS defect. The actual mart-wide structural hole was a different one entirely (ORWO POST, 568K parcels, no bulk-bill source) — invisible from a shop-scoped query that didn't sweep the source axis.

The rule generalizes: **shop-scoped numbers are never mart facts**, and **a NULL rate is never a finding** until time + source localize the cause.

## How to apply

1. Default query shape for any coverage question:

   ```sql
   SELECT
     DATE_TRUNC('month', m.order_created_date)::date AS month,
     m.source_system,
     <the_axis_of_the_question>,                  -- carrier, country, shop, etc.
     COUNT(*) AS shipments,
     ROUND(100.0 * COUNT(<the_thing>) / COUNT(*), 1) AS pct
   FROM <fact>
   LEFT JOIN enterprise_silver.map_shipment_key m ON ...
   GROUP BY 1, 2, 3
   ```

2. Before reporting any aggregate, ask: *which of structural / historical / invoice-lag does this cause look like?* If the by-month numbers don't fit one of those three shapes cleanly, the cause is something else (mid-build, dim-coverage gap, etc.) and needs naming.

3. Treat the source-maturity table (in the relevant mart's how_to.md or equivalent) as the **first** check before reaching for a "wiring isn't done" explanation. Aggregate gaps on a V1-active-build source are expected.

4. *Observation* ≠ *explanation*. "€0 cost on this row" is a measurement; "wiring isn't done" is a guess. Verify the guess against the ETL `.sql` file or month-over-month behaviour before publishing it.

## Cross-references

- Founding quest: `players/jebrim/quest-log/in-progress/S023_2026-05-21_shipping-mart-coverage-audit.md`.
- External durable artifact (the mart's own coverage matrix): `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/reference/coverage-audit.md`.
- Master `how_to.md` rule the skill mirrors: §0 rule 7 ("Coverage questions get a time slice and a source axis").
- Adjacent skill (future): `decompose-questions-by-etl-atom-not-business-unit.md` — same principle generalized beyond coverage.

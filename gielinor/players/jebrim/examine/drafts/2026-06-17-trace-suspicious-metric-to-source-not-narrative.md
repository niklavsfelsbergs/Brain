# Trace a suspicious metric to its source column — don't rationalize it with a narrative

**2026-06-17, S259 (sid8 5463f8a7).** The date-anchored quota came out suspiciously low (17.47% vs SCM 18.72%). Instead of treating "suspiciously low" as a bug signal and tracing it to source, I constructed a plausible-sounding explanation — "Wolfen's invoiced cost is ship-dated and displaces outside the Jan–May window while its revenue stays in" — and wrote that into the deliverable's footnotes as if it were the finding. The principal pushed back ("its suspicious how the quota is so much lower... check yourself"), and on direct query the real cause was a **wrong column**: I'd dated invoiced cost by `fact_shipments.received_by_carrier_date` (NULL on 113k Wolfen rows → cost silently dropped from the numerator while revenue was kept) instead of the spec's `fact_shipment_invoice_lines.shipment_date`. Corrected, the quota was 19.54% — the anomaly was entirely the bug.

**Two failures, one root.**
1. **Spec named a source; I substituted.** The instruction was "shipment date from invoice lines." I used a same-sounding mart field (`received_by_carrier_date`) instead. A spec that names a column/source is binding — verify the named one is populated and used before reaching for a convenient neighbor.
2. **I explained a bug instead of finding it.** A number that surprises you is evidence something is wrong, not a phenomenon to narrate. The "Wolfen displacement" story was internally coherent and totally wrong — coherence is not correctness.

**Why it matters:** a confident wrong narrative is worse than "this looks off, let me check" — it launders a bug into a documented finding. Generalizes [[explain-output-from-data-not-code]] and the instrument-don't-re-guess reflex.

**How to apply:** when a derived metric looks off, the first move is *trace it to the source rows/columns that feed it* (is the dating column populated? is the join dropping rows? is the filter on the right table?) — before composing any explanation for the value. If a spec names a specific source field, confirm you're using exactly that field. Reserve narrative for numbers you've already verified are real.

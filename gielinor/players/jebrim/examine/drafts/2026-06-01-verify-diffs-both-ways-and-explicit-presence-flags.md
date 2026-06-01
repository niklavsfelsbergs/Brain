# Verify a diff both ways; never infer record existence from nullable business columns

**Observation (S124, 2026-06-01, sid 28d1f778).** Building the snapshot-diff harness for the shipping report, I wrote the per-shipment T-1→T diff and smoke-tested it with a **self-diff** (a snapshot against itself), expecting 0 events. It returned **62,743** — exactly the count of `cost_source IS NULL` (uncosted) rows. The bug: I inferred "row exists on side X" from `cost_source`/`real_cost` being non-null, but uncosted rows legitimately have those NULL, so they got mislabeled `NEW`. Fix was explicit presence flags (`_in_prev`/`_in_curr` literals added before the join). A *second*, positive synthetic test (flip 100 rows expected→invoice, halve 100 costs, drop 10) then caught a Decimal-scale overflow in the ratio math that the self-diff hadn't exercised — fixed by casting EUR cols to Float64.

**Rule.**
1. **Verify a diff with BOTH a self-diff (must be zero) AND a synthetic positive test (must catch each event type).** The zero-case proves no false positives; the positive-case proves detection actually fires. Self-diff alone passed a harness that still had a latent arithmetic bug.
2. **Never infer record existence from a nullable business column.** Use an explicit presence marker per side. A column being NULL is data, not absence.

**Why it matters.** This harness is the spine of an automated report that will run unattended — a silent mislabel (62k phantom "NEW") or a crash on arithmetic would surface as fake findings or a dead daily job. The two-sided test is cheap and is what made both bugs visible before the report was built on top. Generalizes to any snapshot/CDC/reconciliation diff.

## Anchor [[S124_61d62e21_shipping-agent-report|S124]]

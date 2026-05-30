# Distinguish offline-fixture state from live data before asserting a data-state claim

**Observation ([[S116_7f67fe48_shipping-agent-fif-monthly-skill|S116]], 2026-05-28).** Validating the FIF DAG offline against cached parquets (only `raw_2026-03` + `raw_2026-04`), I told the principal "April isn't closed — no May invoice." He pushed back: *"why do you say no may invoice? select max(invoicedate::date)..."*. The "no May" was true only of my **offline fixture** — live bronze had data through 2026-05-25. The fixture also masked a real DQ bug (mixed-format `invoicedate`) that only surfaced once I queried live: March was actually 20 invoices, my string filter saw 11.

**Rule.** When I make a *data-state* claim — "X isn't present", "month not closed", "N invoices", "nothing newer than Y" — say explicitly whether it's about the **test fixture** or **live**, and verify against live (a quick query) before stating it as fact. A cached sample is evidence about the sample, not about production.

Anchor: [[S116_7f67fe48_shipping-agent-fif-monthly-skill|S116]].

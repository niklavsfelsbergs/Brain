# Verify the entity's true scoping key, not the obvious-named source field

**Observed [[S280_e5be6eb5_orwo-tender-reprice-engine|S280]] (`e5be6eb5`), 2026-06-19 — principal-caught.**

I scoped the whole ORWO UPS tender Phase-1 on `source_system='ORWO'` — the obvious-named field — and it
gave a clean-looking "92% DE, 5 countries" picture I carried for two sessions. It was a **DE-heavy 34k
sub-slice**. The real ORWO book is **~126k trks** and **cross-border-first** (AT > DE), because the mart
splits one business entity across **two** `source_system` values (`ORWO` + `Picturator`), unified only by
`production_site='Wolfen'` (ORWO's plant). Niklavs caught it in one line: *"check source Picturator and
production site Wolfen."*

**The trap:** a field literally named after the entity (`source_system='ORWO'`) reads as *the* scoping
key, so I never tested whether the entity spanned other values. A white-label / multi-platform operation
(ORWO ships ~20 brands under its own accounts, tagged across platforms) is exactly where the named field
fragments the population.

**How to apply:** before scoping an analysis on an entity-named source field, **cross-check the entity's
true population key against ground truth** — here, the silver *invoice* book (62k trks) vs the mart
`source_system='ORWO'` slice (34k) disagreed 2× and the join-overlap (15k/62k = 24%) screamed "wrong key"
immediately. Reconcile a wide independent source (the invoices, the production site, the account numbers)
against the named-field slice *first*; a large disagreement means the named field is a sub-slice, not the
entity. Sibling of the existing "disagreeing totals = grain/population mismatch" and "absence audit: wide
source + values" reflexes — this is the *scope-key* instance of the same discipline.

# Moving-target decomposition

When a deliverable depends on a downstream system mid-flight (mart updating, schema landing, API changing), don't wait. Sort the work into three buckets, build the stable parts now with anchored uncertainty.

## The three buckets

- **(A) Zero dependency on the moving piece** — fully buildable now. Mechanical, scoped, parallelizable. Spawn a dwarf or run in main.
- **(B) Touches the moving piece but tolerates status blocks** — buildable now with explicit `> Status: in progress (date)` markers on unstable parts. Single patch pass when downstream settles.
- **(C) Genuinely blocked on downstream truth** — defer. Real-data smoke tests, percentages, post-migration shape.

**Order.** A first (unblocks B's scaffolding), then B (carries the brain-work with anchored uncertainty), then patch C when downstream catches up.

## Limit — when B becomes C

If a status block would be wrong on every line, that section is C, not B. The test: can a reader use the section *today* with the status block telling them which lines to discount? Yes → B. No → C.

## Status-block format

`> **Status: in progress (YYYY-MM-DD).** {what's unstable, what's being worked, when to recheck}`

## Why it's faster

Authoring with status blocks beats waiting AND beats rewriting once the system stabilizes. The patch sweep at the end touches only the blocks, not the structure.

## Origin

[[S014_2026-05-21_shipping-data-mart-ttyd-howto|S014]] (2026-05-21), TTYD how-to. Mart was mid-V1-update; principal: *"ETL team's behind, we have to start building, we can correct later."* TTYD has long structural sections (orchestrator phases, table inventory, connection harness) and short state-dependent sections (NULL%, attribute fill, row counts). Status blocks let both ship in the same artifact without lying.

## Related

- `S014_2026-05-21_shipping-data-mart-ttyd-howto.md` T5 — the pivot turn.
- [[2026-05-21-biases-progress-over-completeness-when-blocked]] — the principal preference this skill operationalizes.

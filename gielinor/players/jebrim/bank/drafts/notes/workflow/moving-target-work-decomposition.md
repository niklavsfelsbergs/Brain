# Moving-target work decomposition

**Observed:** S014 (2026-05-21), TTYD how-to quest. Mart was mid-V1-update; principal said "ETL team's behind, we have to start building, we can correct later."

**The pattern.** When a deliverable depends on a downstream system that's mid-flight (mart updating, schema landing, API changing), don't wait. Sort the work into three buckets:

- **(A) Zero dependency on the moving piece** — fully buildable now. Mechanical, scoped, parallelizable. Spawn a dwarf or run in main context.
- **(B) Touches the moving piece but tolerates status blocks** — buildable now with explicit `> Status: in progress (date)` markers on the unstable parts. Single patch pass when downstream settles.
- **(C) Genuinely blocked on downstream truth** — defer. Smoke tests against real data, percentages, post-migration shape.

Build A first (unblocks B's scaffolding), then B (carries the brain-work, but written with anchored uncertainty), then patch C when the downstream catches up.

**Why this works for the TTYD quest specifically.** Documentation has long sections that are structurally fixed (orchestrator phases, table inventory, connection harness) and short sections that are state-dependent (NULL%, attribute fill, row counts). The stable structure dominates by line count; the unstable specifics dominate by importance-per-line. Status blocks let both ship in the same artifact without lying.

**Limit.** If a status block is going to be wrong on every line, that section is C, not B. Don't smear B over what should be deferred. The test: can a reader use the section *today* with the status block telling them which lines to discount? If yes, B. If no, C.

**Operational hint.** Authoring with status blocks is faster than waiting *and* faster than rewriting once the system stabilizes. The patch sweep at the end touches only the blocks, not the structure.

## Related

- TTYD how-to quest log `S014_2026-05-21_shipping-data-mart-ttyd-howto.md` — the originating session, T5 is the pivot turn.
- Inline status-block format adopted: `> **Status: in progress (YYYY-MM-DD).** {what's unstable, what's being worked, when to recheck}`.

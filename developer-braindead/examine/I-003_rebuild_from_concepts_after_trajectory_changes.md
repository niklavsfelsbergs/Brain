# I-003 — When a project changes trajectory multiple times, rebuild from the concepts

**Date.** 2026-05-24. **Session ref.** [[S068_89f41770_reflection_cockpit_parking_and_lessons]].

**Ruling.** When a build has pivoted direction several times and iteration starts fighting accumulated structure instead of adding value, stop patching. Extract the concepts that still hold — what the thing is *for*, which surfaces earned their place — and rebuild greenfield from those. The history lives in git and the quest-log; it doesn't need to be carried in the code.

**Context.** The switchboard line ran ~30 sessions (S037–S063) of iterative patching across **repeated trajectory changes**: an isometric map with sprites / walk animations / wander → [[D-026_switchboard_promotion]] killed the map and promoted the two load-bearing panels to `switchboard/` → [[D-028_switchboard_cockpit_rebuild]] / [[S064_78824901_switchboard-cockpit-rebuild]] rebuilt the whole thing greenfield as a standalone fleet cockpit in `cockpit/`. The tell that the patching had gone bad showed up repeatedly:

- Four-plus sessions (S047–S051) all touched the map; most were *debugging* it, not improving it.
- The "each fix looks like the last bug" pattern (S048) — derived state maintained by an event stream had structurally diverged from the sidecar's truth; three patch rounds each narrowed the symptom and the next bug wore the same face. Only an architectural inversion fixed it.
- S063: the principal hit *"I need to test it from a clean slate"* and found the stale-JS cache disease that had silently taxed nearly every switchboard session.
- The codebase had become shaped by the *history of directions* (map-era dead weight, vestigial `path-map.json`, server-dying disease) rather than the *current concept*.

The rebuild ([[S064_78824901_switchboard-cockpit-rebuild]]) shed all of it in roughly one session — one process, three surfaces over one session model, hooks preserved as contracts — and **unstuck** the principal, who had been stuck on switchboard stuff for days. Rebuilding from concepts was faster than continuing to patch.

**Why.** Accumulated patches across trajectory changes carry dead weight, contradictory assumptions from abandoned directions, and structural debt the current concept never asked for. Past a certain point each new patch is paying interest on that debt. Distilling to the concepts that survived the pivots and rebuilding from them clears the debt in one move — and is often *cheaper* than the marginal patch, not more expensive, because the rebuild only implements the concept that actually won.

**How to apply.** Watch for the signal cluster: (1) the project has changed direction 2–3+ times; (2) recent sessions are mostly *debugging* the surface rather than extending it; (3) each fix resembles the last bug; (4) a "clean slate" urge. When they co-occur, propose the rebuild explicitly — name the concepts worth keeping vs. the history worth dropping — rather than reaching for another patch. Preserve the *contracts* (here: the hook state files), not the implementation.

**Related.** [[D-028_switchboard_cockpit_rebuild]] (the rebuild that proved it), [[D-026_switchboard_promotion]] (a mid-line trajectory change), [[D-027_inward_outward_build_imbalance]] (the imbalance lens), [[I-002]] (the other build-discipline posture).

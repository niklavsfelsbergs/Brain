# Alching graduates orphan sub-agent traces in the alched player's in-progress/

**What changed.** Alching's quest-hygiene step gains an explicit obligation: when tending a player, **sweep that player's `quest-log/in-progress/` for finished sub-agent traces (dwarf / penguin / shipping-agent run-logs) and graduate the settled ones to `completed/`.** These are the entries no close-session ever reaches.

**Why.** Sub-agents never run close-session — only the principal does. A dwarf/penguin/shipping-agent writes its trace to `in-progress/` and returns; the spawning session may end without graduating it, and a *later* session has no idea the trace exists. The result is orphaned run-logs accumulating in `in-progress/` that nobody owns. Two were sitting live at this round: `jebrim/quest-log/in-progress/S125_dwarf_interesting-thing.md` and `zezima/quest-log/in-progress/dwarf_tell-me-something-about-niklavs.md`. Both finished work; neither graduated until B-012 swept them.

**What triggered it.** The [[S131_0b0f2049_lived-operator-severity-audit|S131]] lived-operator severity audit (2026-05-30, Jebrim + Braindead) named this as **beam #8**: *"nobody owns a sub-agent's trace — the dwarf never runs close-session and the principal's session may not know they exist."* B-012's Phase 0 graduated both lived instances as the fix, which surfaced the standing rule.

**The rule (operating discipline).**
- During alching (Phase 0 of bankstanding or standalone), after the completed-quest graduation step, **walk `in-progress/` for sub-agent traces** (filename tells: `*_dwarf*`, `*_pN_*`, `*_shipping-agent_*`, or a `**Role.** … spawned as dwarf/penguin` header). A trace whose work is finished and whose spawning session has ended → `git mv` to `completed/`. A trace still in-flight (spawning session live) → leave.
- Harvest first if the trace carries reusable value (a self-observation, a domain finding) — *then* graduate. Don't let graduation discard an un-harvested lesson.

**Scope / relationship to the structural fix.** This is the *operating-discipline* half. The dev brain owns the **structural** half of beam #8 (a reaping mechanism / explicit ownership rule so traces don't orphan in the first place). This rule holds the line until — and alongside — that lands; it is not a substitute for it. Sibling to the broader "deferred-manual debris drifts" finding (same beam): a sweep that only ever runs when someone remembers will drift, so it belongs *in the ritual checklist*, not in good intentions.

**Anchor.** [[S131_0b0f2049_lived-operator-severity-audit|S131]] beam #8; enacted [[B-012_2026-05-30_twelfth-bankstanding|B-012]] Phase 0 (both lived traces graduated).

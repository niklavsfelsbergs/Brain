# D-027 — 2026-05-23 — Inward/outward build imbalance: the operational half was never built

**Context.** A self-audit this session ([[S060]]) ran the brain against `bank/plan.md` on four lenses — plan fidelity, dormant-but-working capabilities, deterioration signals, highest-value missing piece. Two recon crews gathered the evidence.

The load-bearing finding: **the plan stopped tracking reality at [[S003]].** `plan.md` — "the single living plan for the mission" — still referenced S002/S003 while construction had run to ~S055 (gielinor) / S058–S059 (dev). §A and §B (foundation + main-brain architecture) are done and then some. But §C (the pilot — a morning shipping-data routing check, *the agent doing real work on a trigger*), §E (gates), §F (triggers beyond manual), and §G (substrate) — **the entire operational half** — are untouched. Phase 1 was declared "manual invocation only" ([[A-001]]); at S060 the agent is *still* manual-only. No trigger has ever fired; no pilot ever ran.

Meanwhile an enormous, unplanned cognitive architecture was built, and built well: the player roster (Jebrim, Zezima), the ritual system (respawn, close-session, alching, bankstanding, drafts-triage), three sub-agent roles (dwarf, gnome, penguin), Guthix the caretaker deity, hook-enforced write guarantees, and a large observability/coordination layer (visualizer → switchboard, comms / [[D-024]]).

The evidence sharpens *where* the effort went and *what went cold*:

- **Effort imbalance.** ~52% of recent commits build the observability scaffolding (visualizer / switchboard / hooks — the mirror the brain watches itself in); ~28% is actual player work. Dev-brain sessions S032–S059 are nearly continuous switchboard polish.
- **Cold-but-shipped capabilities.** Guthix *consultation* mode: zero on-disk runs ever (no `G-NNN` files) despite [[D-023]] shipping a routing heuristic to make it reachable. `brain/ideas/`: zero ideas captured since it shipped ([[S040]]). Standalone `/drafts`: never run independently. Guthix's bank: 0 notes after four bankstanding passes.
- **Deterioration signals.** `plan.md` frozen at S003 (the strongest). `respawn.md` bloated to ~338 lines / 10 "Last updated" stanzas with stale carries (e.g. "first live gnome spawn" still listed pending though gnomes ran in S021/S030/S034). Bankstanding outrunning its fuel (B-003 light, B-004 abandoned no-op).

The unifying read: **the brain has optimized inward — better self-model, better self-observation, better coordination between sessions the operator starts by hand — and never turned outward to act on its own.** The cold capabilities, the effort imbalance, and the abandoned §C–§G are the same gap wearing different clothes. The brain got smart; it never got hands.

**Decision.** Name the imbalance as a tracked decision and correct course in two steps:

1. **Stabilize the docs now (this session).** Reconcile `plan.md` to current reality — mark the foundation done, reframe §C as the load-bearing unbuilt mission core, and add sections (§I–§M) for the emergent architecture (players, rituals, sub-agent roles, Guthix, observability/coordination) so the living plan finally reflects what was built. Principal chose this over building the pilot immediately.
2. **Build the operational half next (deferred to a future session).** The highest-value net-new is a real trigger: one recurring job a player already does by hand, wired to the thinnest scheduled run, producing one artifact without the operator driving each turn. Sidestep §G (substrate) for now by using the harness's own scheduler as the Phase-1 substrate; decide routine-vs-VPS only when a real need forces it. Dry-run / worktree-safe.

**Alternatives considered.**

- **Build the pilot this session.** Deferred, not rejected — principal chose to stabilize the docs first (lower risk; the plan needs to be a usable steering doc before the next build hangs off it).
- **Capture this as a gielinor `lorebook/` entry.** Rejected — gielinor's lorebook explicitly excludes construction history ("Construction history lives in the dev brain, not here"). This is a decision about *how the brain is being built*, so it belongs in the dev brain's `bank/decisions/`.
- **Keep polishing the switchboard / do nothing.** Rejected — that is the disease the audit named. Answering "you've built inward too long" with more inward work would be self-defeating.

**Consequences.**

- `plan.md` un-frozen; §C becomes the named next build rather than a stale open item.
- A standing watch on the switchboard-polish reflex: further observability work should clear a higher bar now that the scaffolding is mature and the outward half is empty.
- The cold capabilities (Guthix consultation, `ideas/`, Guthix bank) get a natural forcing function — the pilot, once running, exercises the whole machine against a real outcome instead of against itself.
- The pilot needs one input the dev brain can't supply: *which* real recurring job. That is Jebrim's / the principal's call; it gates the next build.

**Open questions.**

- Will the harness scheduler hold as a Phase-1 substrate, or will the first real trigger immediately force the §G routine-vs-VPS decision?
- Does "stabilize first" risk the pilot sliding indefinitely — the same deferral that has left §C open since S003? Watch whether the next session actually reaches for it.

**Session ref.** [[S060]].

**Related.**
- `bank/plan.md` — reconciled this session; §C is the target.
- [[D-023]] close the promote/consult loop — the prior "underutilization" course-correction. This decision is its operational sequel: D-023 fixed the *inward* promote/consult leak; this names the *outward* gap.
- [[A-001]] manual-invocation-only Phase 1 — the assumption this decision proposes to finally retire.

# Dashboard ↔ shipping-agent convergence — quest resume

**Status:** parked. No work started yet. Created S026 (2026-05-22) to hold the convergence intent in inventory until a session picks it up.

**Related near-term work (handover queued):** `inventory/dashboard-gold-cutover-resume.md` (post-S028) — dashboard gets cut over to gold + aligned to the agent's cost-basis vocabulary as a prerequisite to convergence. That work is mechanical and scoped; this convergence quest covers the broader long-term direction (URL emission, shared definitions, dashboard ad-hoc layer) and stays parked until the principal opens it.

**Quest goal:** align the shipping-costs monitoring dashboard and the shipping-agent so they tell consistent stories from the same mart. Specifically: deference flow (agent defers to dashboard for operational vocab), URL routing (agent can emit dashboard URLs), and shared definitions where it matters (cost basis, alert types, coverage semantics).

## Where we are

Nothing implemented yet. Knowledge captured in:

- `bank/drafts/notes/projects/dashboard_and_shipping_agent_convergence.md` — the interrelation analysis + convergence directions + Niklavs' four confirmed positions.
- `bank/drafts/notes/projects/shipping_costs_monitoring_nextjs_vocab.md` — the dashboard's operational vocab, ready to be pointed at from the agent.

Niklavs confirmed in S026:

- Dashboard ↔ mart alignment is incomplete (dashboard needs more cutover work).
- Dashboard's structural-coverage-hole reporting is currently wrong; will be resolved.
- Cost-basis alignment between dashboard and agent: deferred — re-read agent's `how_to.md §5` when it becomes load-bearing.
- Long-term convergence direction: not yet thought through. Near-term concrete move: agent emits dashboard URLs.

## Next concrete step

Pick one of the four coupling opportunities from the bank note (ordered by reversibility, cheapest first):

1. **Agent emits dashboard URLs** for questions the dashboard already answers. Lowest cost. Probably the right first move.
2. Agent reads dashboard's pre-computed parquets — adds coupling, probably skip at current scale.
3. Shared reference docs — agent's `reference/dashboard-vocab.md` pointing at dashboard's CLAUDE.md + the vocab bank note.
4. Shared cost-basis recipe in the mart — highest impact, requires ETL work, deferred.

Recommend opening with (1) + (3): the URL-routing + a thin doc-pointer in the agent. Both are doc/string work, neither commits to architectural decisions Niklavs hasn't made.

## Files / paths to read first when this quest opens

1. This file + the convergence bank note (`bank/drafts/notes/projects/dashboard_and_shipping_agent_convergence.md`).
2. `bank/drafts/notes/projects/shipping_costs_monitoring_nextjs_vocab.md` — the dashboard glossary.
3. `bi-analytics/NFE/projects/3_shipping_data_mart/shipping-agent/how_to.md` — re-read, especially §5 (query reference) and §10 (local-first reach) to know where vocab pointers fit.
4. `bi-analytics/NFE/projects/3_shipping_data_mart/shipping-agent/reference/coverage-audit.md` — context on what the agent already documents that the dashboard does not.
5. **For URL contract:** the "URL param contract" table in the vocab note. Knowing the short codes (`tab`, `bd`, `aq`, `al`, etc.) is needed for any URL-emission move.

## Constraints

- The dashboard's mart cutover hasn't merged to main yet — branch is `shipping-mart-cutover` in worktree at `Documents/GitHub/bi-analytics/`. If it merges before this quest opens, the "branch" routing in the vocab note retires; rest of the convergence content holds.
- Coverage-hole reporting in the dashboard will change. Don't bake current behavior into the agent's vocab pointers — point at concepts, not at specific tab counts.
- Niklavs hasn't decided long-term direction. Preserve optionality — don't pick an architecture that forecloses the "dashboard hosts ad-hoc Q&A" path.

## Open questions for the future session

- Re-read `how_to.md §5` and answer: does the agent's default cost basis match dashboard's `cost_for_routing`? If not, surface as a coherence bug needing a decision before any user-facing alignment work.
- The coverage-hole fix — has it landed in the dashboard? If yes, agent's `coverage-audit.md` can stop being the canonical source and become a historical reference. If no, agent stays canonical until it does.
- Does the dashboard URL contract feel stable enough to bake into the agent? The post-cutover surface is settling but not frozen — check the changelog before committing.

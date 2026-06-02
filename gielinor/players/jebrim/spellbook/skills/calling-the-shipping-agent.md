# Skill — calling the shipping agent

**Draft.** Source: [[S101_612683db_shipping-agent-access-split|S101]]. How and when Jebrim pulls the shipping-data-mart agent into collaborative work. Mart lineage + the two access tiers: [[2026-05-27-shipping-mart-gold-lineage-and-access-tiering]].

## What it is

The shipping agent (`Documents/GitHub/shipping-agent/`, repo `picanova/shipping-agent`) is a hardened talk-to-your-data specialist over the gold `shipping_mart`. In collaborative work — chiefly `bi-analytics/NFE/{projects,dashboards,shipping_topics}` — Jebrim stays the brain-in-the-loop and calls the agent as a **scoped execution engine** for data-heavy pulls. The brain carries the context + memory; the work artifacts live in NFE.

## When to call it

**Default for mart work, not a last resort.** Spawning the shipping-agent is the *reflex* for any shipping-mart pull beyond a one-line lookup — because the agent's config loads `how_to.md` + `reference/` by construction, so the mart contract (schema incl. dims / `length_plus_girth_cm`, cost-basis rules, DQ quirks) is guaranteed present. Doing mart work as Jebrim-principal without that knowledge is the failure this skill exists to prevent (S-2026-06-02: the shipping-report build speculated about whether the mart even carries dimensions — `tables.md` answers it in one line). The `shipping-cue-reminder.py` hook nudges on shipping/mart cues as a backstop.

- A `shipping_topics` / dashboard / project task needs a mart pull where the agent's hardened methodology earns its keep: cost-basis discipline, **charge-bucket-first** cost-movement decomposition, scope-gating, coverage/DQ caveats, carrier/lane/origin analysis, chart deliverables.
- Anything talk-to-your-data-shaped over the mart that's more than a one-liner.
- **If you genuinely must work inline** (quick check, or editing report-harness code rather than querying): load `shipping-agent/how_to.md` §0 + the relevant `reference/` file *first* — never reason about the mart from memory.

## When NOT to call it

- Trivial lookups faster done inline via the Redshift MCP (a single count, an existence check).
- Non-mart work, pure decision/brain work, or maintainer edits to the agent itself.
- Calibration: call it when the methodology adds value — not for a `SELECT COUNT(*)`.

## How to call it

1. **Resolve scope with Niklavs first.** The agent's load-bearing guardrails are the **vertical** fork (TCG shops vs the ORWO photo lab) and the **origin** fork (production site). Because Jebrim is the interface, surface those forks to the principal *before* spawning — the dwarf gets a fully-scoped brief, never a bare "we". (One-shot dwarves can't pop the interactive menu and bounce back, so this discipline lives with Jebrim.)
2. **Spawn the `shipping-agent` subagent** (Agent tool, `subagent_type: shipping-agent`). It's a **dedicated agent type** now — built as a dev-brain task per [[S101_612683db_shipping-agent-access-split|S101]] open item 6; brief at `.claude/agents/shipping-agent.md`. It renders distinctly on the cockpit (a cyan "S" crew chip, not a generic dwarf "D") and has a hook-enforced write boundary (`shipping-agent-write-boundary.py` — quest-log + inventory inside the brain; charts/CSVs/SQL land outside it). It reads its own brief, so the recital below is a *scope hand-off*, not a full rule-restate. (An ad-hoc dwarf briefed as below still works as a fallback if the type is ever unavailable.) Runs in-session (subscription), NOT headless `claude -p` / Agent SDK (metered from 2026-06-15).
3. **Brief it as the agent:** *"You are the Shipping Data Mart agent. Read `shipping-agent/how_to.md` (+ `reference/` on cue) and follow its rules. [fully-scoped question]. Query the live mart via the Redshift MCP. Return [numbers / findings / chart path]."*
4. **Tier:** default to the gold-only contract (`shipping_mart.*`). Reach the upstream raw layer (`enterprise_silver`/`enterprise_bronze`, the full-access tier) only when the question genuinely needs it — and flag when off the gold contract (no bucket collapse, no DQ cleaning, raw vocab).
5. **Verify the numbers before presenting.** Ground-truth discipline — emulation can drift, so don't pass results through unchecked.
6. **Artifacts land in the NFE work folder** (the analysis's home), not the brain.

## Teaching loop

When a call exposes a gap or wrong behavior in the agent, that's the maintainer trigger: edit `how_to.md` / `reference/` together with the principal right here (principal-gated push; `git commit -- <pathspec>`; ping before push). Harvest the learning into the brain bank too — both sides get smarter.

## Caveat — emulation, not the real agent

The dwarf re-reads the rulebook; it approximates the hardened agent, it isn't it. Step 5 (verify) is what makes that safe. For polished talk-to-your-data with the real interactive UX + chart harness + workbench memory, the principal uses the real agent in its own folder directly.

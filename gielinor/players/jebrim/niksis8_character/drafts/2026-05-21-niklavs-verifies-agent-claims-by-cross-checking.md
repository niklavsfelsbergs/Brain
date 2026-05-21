# Niklavs verifies agent claims by cross-checking, not by acting

**Observed:** 2026-05-21 (S023, opening turn — Niklavs forwarded a uk.photo.gifts conversation from another agent and said *"this agent is raising something and it concerns me — investigate"*).

## The observation

When an agent surfaces a substantive claim (e.g., "27% of shipments are missing cost data, Wolfen's wiring isn't done"), Niklavs's default move is to **send the claim to a second agent for independent verification before acting on it**. The first agent's output is treated as a hypothesis, not a finding. The principal doesn't ask the surfacing agent to defend itself; he routes the question to a different agent with different defaults and waits to see whether the read survives.

In S023, the surfacing agent was the shipping-agent (folder-scoped, in the `bi-analytics-main` working folder). The second agent was Jebrim (cross-project read context, different defaults). The shipping-agent's claim partially held but the framing was wrong — and Niklavs only learned that because he commissioned the check.

The verification step isn't an exception to the workflow. It IS the workflow when stakes are non-trivial (cost ratios, mart structural claims, anything that would change how a stakeholder reads the data).

## What this means for how Jebrim should engage

- **Treat his own outputs the same way.** When Jebrim publishes a finding, expect Niklavs to want it cross-checked — by another agent, by a re-derivation against a different lens, or by Jebrim himself running a second probe with different assumptions. Building in the cross-check (or naming it as the obvious next step) is on-pattern; refusing to caveat is off-pattern.
- **Don't undermine the surfacing agent.** When Jebrim's read corrects another agent, the framing should be diagnostic (what was the scope, what was the lens) rather than dismissive. "The shipping-agent isn't wrong about the numbers; the shop-scope inflated the inference" is Niklavs's preferred register.
- **Name what would falsify a finding.** Niklavs trusts a finding that names its own breakage points more than a finding presented as certain. The S023 audit landed with explicit "regenerate on demand" probes and a maturity table; this is the shape Niklavs reads as load-bearing.

## Promotion criterion (for alching)

- If another session reproduces the "surface a claim, expect Niklavs to commission a verification" pattern, promote to `confirmed/`.
- Watch for the inverse — sessions where Niklavs *does* act on a single agent's claim without cross-check. If those are frequent, the rule above is over-stated.

# S276 — SCM knowledge upgrade (shipping-agent reference + brain digest)

**Actor:** Jebrim · **sid8:** 88756db9 · **Date:** 2026-06-19 · **Status:** completed

## Ask

Niklavs (Hey Jebrim): what has the shipping-agent been taught about SCM, and is it enough to reason about it and recreate numbers? He suspected it lacked explanation of how things are calculated — but asked first for the actual current state.

## What happened

1. **Audited the agent's SCM knowledge.** Found `shipping-agent/reference/scm.md` (paired with `skills/scm-screenshot.md`, load-on-cue via `how_to.md` rule). Reported the actual contents: strong calculation core already present (order-month lens, both quota formulas, numerator/denominator provenance, cost-basis vocab, anchor tie-out figures, surface map, alert engine, deep-link contract, freshness caveats). Corrected his assumption — the "how it's calculated" explanation was already the spine of the file. Named two real gaps: (a) no assembled end-to-end worked reproduction; (b) analytical-tab math (Cost Drivers / Breakdown) described but not formula-specified.

2. **Scoped + added the two gaps to `reference/scm.md`** (principal chose "verify live first"):
   - **Worked reproduction (§1)** — assembled runnable gold query; **live-verified against the mart 2026-06-19**: US May-2026 = **26.64% combined / 26.23% real** (53,294 shipments, €525,445 / €1,971,706, 97.4% invoiced), ties to the ≈26.5% anchor. Captured 3 reproduction gotchas, incl. the live-caught `destination_country_code='US'` scope key (`destination_country='US'` returns zero rows).
   - **§8 decomposition math** — Breakdown Impact/Rate/Mix + Cost-Drivers rate/shift `eur_impact`, source-derived from the live app (`bi-analytics-main`, HEAD `e4fe742` 2026-06-18), each line `file:line`-cited.

3. **Added `how_to.md` rule 39** (principal chose hard-default shape) — order-month as the house default lens for cost & quota work, state the lens up front, scoped exception for invoice-timing questions. Promotes the lens discipline out from behind the SCM-only cue. + rule 11 pointer + §0 header count (38→39).

4. **Committed + pushed** the shipping-agent repo: `cfc435a` on `main`, pushed to `origin/main` (picanova/shipping-agent), in sync. Pathspec-scoped to the 2 doc files; untracked `demo/` left alone.

5. **Updated the brain SCM digest** (`bank/domains/scm.md`) — order-month lens + live tie-out, new decomposition-math section, agent-now-documents-SCM cross-ref, corrected stale branch line (`shipping-mart-cutover`→`main`), bumped stamps.

## Decisions

- **Verify the worked reproduction live** (not document-from-formula) — synthetic ≠ live-correct. Ran it; tied out.
- **Rule 39 = hard default + state it** (not surface-as-pick) — lens shifts level ~1pt not direction, so it fits the volume-default pattern (rule 7), not the scope/origin forced-pick pattern.

## Process note

Entry-OPEN gate fired — I skipped the comms OPEN on entry (the recurring known leak the gate backstops). Posted it before the first brain write, after confirming no live sibling on `bank/domains/scm.md`. No new examine draft — this is the single most-documented discipline pattern already, not new signal.

## Pending external actions

None. Shipping-agent docs committed + pushed (`cfc435a`). Brain footprint (digest + comms + this quest-log) committed at close.

## Harvest

No new drafts (Q1–4 empty-set; Q5 = the late-OPEN, already an extensively-documented pattern — noted above, not re-drafted). Durable domain facts folded directly into `bank/domains/scm.md` and the shipping-agent repo.

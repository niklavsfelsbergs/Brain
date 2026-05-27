# D-032 — 2026-05-27 — Godly-proposal flow: Guthix self-lands; the code-bearing seam

> **Status: decided 2026-05-27.** Part 1 records reality (keep Guthix as bankstander). Part 2 ratified by the principal as the **soft guideline** (of soft-guideline / hard-gate / status-quo). Triggered by the principal asking whether Braindead would be a better bankstander than Guthix, then — sharper — *"do you actually pick up Guthix's suggestions?"* Braindead had just asserted a "Guthix proposes from the inside, Braindead builds from the outside" pipeline. Checked the record: that pipeline does not exist. This decision writes down what actually happens and resolves the one seam where the principal's instinct genuinely bites.

## Context — the false pipeline

Asked to justify keeping bankstanding with Guthix rather than moving it to Braindead, Braindead claimed the two actors already split cleanly: Guthix *feels operational friction and proposes* (he can only propose changes to `meta/`/rituals/hooks, never apply them); Braindead *builds the approved change from outside*. The principal challenged it. The record refutes it:

| Godly proposal | Drafted | Landed | By whom |
|---|---|---|---|
| synthesis-dormant-at-N1 (edit `bankstanding.md` step 3) | [[B-004_2026-05-23_fourth-bankstanding|B-004]] | [[B-006_2026-05-24_sixth-bankstanding|B-006]] | **Guthix**, in bankstanding |
| multiple-choice-in-comms-protocol (edit `meta/communication-protocol.md`) | [[B-006_2026-05-24_sixth-bankstanding|B-006]] | [[B-006_2026-05-24_sixth-bankstanding|B-006]] (same pass) | **Guthix**, in bankstanding |
| grounding-cue-reminder (NEW `gielinor/.claude/hooks/grounding-cue-reminder.py` + settings.json) | [[B-008_2026-05-26_eighth-bankstanding|B-008]] | [[B-009_2026-05-27_ninth-bankstanding|B-009]] (commit `22a80d2`, 2026-05-27) | **Guthix**, in bankstanding |

Count: **Guthix 3, Braindead 0.** Every godly proposal — *including the one that is a literal hook*, pure construction — was self-landed by Guthix during a later (or the same) bankstanding, on explicit principal authorization. Braindead has never implemented one. The "Braindead builds" seam was plausible-sounding architecture, not observed behavior; the brain-root docs and `write-rules.md` describe a "propose → principal reviews → lands" flow without ever naming *who lands it*, which let the fiction stand.

## The actual flow

A godly proposal is drafted during bankstanding into `deities/guthix/proposals/`, reviewed by the principal, and **self-landed by Guthix in a subsequent (or the same) bankstanding pass** under the *"user-only with explicit permission"* override ([[D-017]]-style) plus bankstanding's elevated write-reach (`write-rules.md` → *Guthix's godly proposals*). This holds even for code-bearing proposals: B-009 wrote and registered a hook in-pass and verified it at the boundary. There is no handoff to a dev-brain session.

## Decision (part 1) — keep Guthix as bankstander, for the right reason

Bankstanding stays with Guthix. But the justification is **trigger + evidence**, not the false propose-vs-build split:

- **Guthix builds what *lived operation* reveals is broken.** The grounding-cue hook was good because it was anchored to three real operational misses ([[S066_e2362ea0_domajamas-dalas-reconsider|S066]] / [[S076_949a59cf_scm-alert-engine-audit|S076]] / [[S095_f60153e0_gertrudes113-buy-deliberation|S095]]) — evidence only an actor who *reads across all the operation* accrues. Braindead, who enters on "lets develop gielinor," would never have generated it.
- **Braindead builds what *design intent* calls for** — the cockpit, worktree isolation ([[D-030_worktree_isolation_for_parallel_sessions|D-030]]), task-list discipline ([[D-031_task_list_discipline|D-031]]). Infrastructure and architecture, not fixes for felt operational failures.

So the write surfaces overlap (both touch `meta/`, rituals, hooks) but the **vantage point does not**. Moving bankstanding to Braindead would put the brain's self-maintenance in the hands of a developer who does not inhabit it — he'd be auditing a system he doesn't operate. The grounding hook is the proof it must be the in-world actor. This sharpens, not replaces, [[D-022_guthix_consultation_mode|D-022]].

## Decision (part 2) — the code-bearing seam: soft guideline

The one place the principal's "let the builder build it" instinct genuinely bites: a **prose edit** to a ritual is fine for Guthix to self-land, but **code** (a hook, a script) wants build rigor — `py_compile`, boundary tests, the dev-brain's verification culture — not just operator-grade in-pass checking.

**Ratified guideline (not a hard gate):** Guthix self-lands prose/text proposals (`meta/`, ritual and doc text). For *substantial code-bearing* godly proposals (new hooks/scripts, non-trivial logic), prefer handing the **build** to a Braindead session while Guthix keeps the **authorship of the intent** (the proposal, the lorebook decision, the operational evidence). Guthix drafts and evidences; Braindead implements and verifies under the gates; the proposal still records *why* and stays anchored to the sessions that motivated it.

**Why a guideline and not a gate:** B-009's hook verified clean at the boundary — N=1, no observed failure of operator-built code yet. Per the brain's own *"don't over-formalize a reachable capability"* discipline, hard-wiring a routing rule now would formalize a hypothetical. So: a stated preference + a watch, revisited if operator-built code actually bites (an unverified or regressing hook landed in a bankstanding pass).

**Principal's call (2026-05-27):** chose the soft guideline over a hard gate and over status quo. Small code-bearing proposals Guthix may still self-land with in-pass verification; *substantial* ones prefer the Braindead build. Trigger to harden into a gate: a code-bearing proposal that lands in a bankstanding pass unverified or regressing.

## What changes on disk

- **This decision** (the construction record) — DONE.
- **Gielinor-binding propagation — routed through the godly-proposal flow, not a Braindead meta-edit.** The rule that should bind in gielinor (the self-land flow + the code-bearing handoff preference) belongs in `gielinor/meta/write-rules.md` (*Guthix's godly proposals*) + `deities/guthix/proposals/_about.md` + a gielinor lorebook `D-NNN`. Braindead does **not** land these directly: `meta/` is user-only, and a dev-brain `[[D-032]]` citation wouldn't resolve in the gielinor vault (per-brain topology). The clean path is a **godly proposal at the next bankstanding** — a pure text change Guthix self-lands under part 2's soft guideline, which also dogfoods the flow this decision clarifies. (Risk noted: Guthix is underused — see open items — so "next bankstanding" could sit. If the principal wants it binding sooner, he can flip to `Hey Guthix, bankstand` and land it, or grant Braindead an explicit one-off to edit the two gielinor surfaces now.)
- Nothing retired.

## Out of scope / open

- **No hook enforcement.** Discipline, like the rest of the proposal flow.
- **Who triggers the Braindead build?** Today Braindead only enters on the principal's "lets develop gielinor." A code-bearing proposal approved in bankstanding would sit until the principal opens a dev session. Acceptable at current cadence; note it.
- **The original underuse signal.** Part of what may drive "should the builder bankstand" is that Guthix is *underused* (pre-[[S038_brain_underutilization_diagnosis|S038]]: 1 session in 53). That's a routing-adoption problem ([[D-022_guthix_consultation_mode|D-022]] + the S038 heuristic), not a role-merge case — flagged, not addressed here.

## Related

- [[D-022_guthix_consultation_mode|D-022]] — Guthix's two modes; this narrows the bankstanding half's proposal lifecycle.
- [[D-027_inward_outward_build_imbalance|D-027]] — inward/outward; the grounding hook is an inward operational fix, correctly Guthix's.
- [[D-030_worktree_isolation_for_parallel_sessions|D-030]] / [[D-031_task_list_discipline|D-031]] — examples of design-intent builds that are correctly Braindead's.
- `gielinor/meta/write-rules.md` → *Guthix's godly proposals* — the surface that should name the self-land flow.
- `gielinor/deities/guthix/proposals/_about.md` — godly-proposal scope/shape.

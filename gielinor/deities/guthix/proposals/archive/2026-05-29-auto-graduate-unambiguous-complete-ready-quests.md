# Auto-graduate the unambiguous complete-ready quest at close (remove the per-quest approval gate)

## 1. Observation

[[B-010_2026-05-29_tenth-bankstanding|B-010]] Phase 0 found Jebrim's `quest-log/in-progress/` at **22 files** — the largest deferred-graduation backlog yet, the entire S114–S122 EU-tender campaign, all complete-ready, graduating in one pass (22→0). This is the **third occurrence** of the leak [[D-026_graduate-complete-ready-quests-in-session]] was written to fix, and it is **worsening**: [[B-004_2026-05-23_fourth-bankstanding|B-004]] 15→3, [[B-007_2026-05-25_seventh-bankstanding|B-007]] 15→5, [[B-010_2026-05-29_tenth-bankstanding|B-010]] 22→0.

D-026's ritual follow-up **was** applied — `spellbook/rituals/close-session.md:125` already carries "move is the default; 'propose →completed/ next session' is no longer acceptable." So the rule *and* its ritual enforcement are both in place, and the leak still hit its worst. The break is not the default-direction wording; it is the **approval gate** one line up at `close-session.md:123` — *"Propose only. The agent never auto-completes a quest. Principal approval per-line, every time."* The close-session scan fires and surfaces the candidates correctly (the S114–S122 CLOSINGs in `comms/active.md` do this verbatim: *"Proposed complete-ready → completed/ (awaiting y/n): S114 / S115 / S117 / S118"*), but in rapid same-terminal handoff chains the principal is heads-down — the next instruction is "build it / push it / next" and the per-quest y/n never comes, so the move re-defers. D-026 made *move* the default action but left it behind a gate that the iteration loop skips.

Principal chose this fix direction at B-010 ([[D-025_offer-multiple-choice-with-recommendation|D-025]] multiple-choice).

## 2. Proposed change

Edit `spellbook/rituals/close-session.md` step 4's stale-done scan. Split the gate by ambiguity: **auto-graduate the unambiguous case, keep propose-and-confirm for the ambiguous one.**

Replace line 119:

> For each quest that fires this signal, propose to principal: *"S023 reads complete… — move to completed/?"* List multiple candidates as a batch with a one-line reason each. The principal approves per-line (`1y 2y 3n`) or in bulk (`all y`). Per approval: execute the complete-flow above.

with:

> For each quest that fires this signal, classify it:
> - **Unambiguous** — the CLOSING/resume records the deliverable **shipped + committed** *and* there is **no named open dependency**. → **Graduate it in this close without a separate y/n.** Execute the complete-flow above, and report the moves as a batch notification: *"Graduated S114/S115/S117 → completed/ (shipped+committed, no open dep). Veto any to carry forward."* The principal vetoes after the fact; an un-vetoed move stands.
> - **Ambiguous** — a stated open dependency, a "done but pending principal action," or any uncertainty about whether it's truly closed. → Propose for explicit approval as before (`1y 2y 3n` / `all y`); do **not** auto-move.

And replace the **Boundary** block at line 123:

> **Boundary.** Propose only. The agent never auto-completes a quest. Principal approval per-line, every time.

with:

> **Boundary.** Auto-graduation is limited to the **unambiguous shipped+committed+no-open-dep** case and is always reported as a vetoable batch — never silent. Anything with a stated open dependency or any ambiguity stays propose-and-confirm. The agent never auto-*completes the underlying work*; it only moves a quest the CLOSING already declared finished. Veto reverses any move (`git mv` back).

Update the `Default is move` paragraph (line 125) to point at the new split and name this decision (D-029) alongside D-026.

## 3. Reasoning

The gate D-026 left in place is the actual leak. Three rounds of evidence show the per-quest approval doesn't arrive during campaign-mode iteration, and bankstanding Phase 0 has become the *primary* graduation mechanism rather than the backstop D-026 intended. Moving the unambiguous case to auto-with-veto removes the step the loop skips while preserving principal control where judgment is actually needed (open deps, ambiguity). Cost to land: a small ritual edit + one new lorebook decision. The after-the-fact veto + the no-deletes guarantee make a wrong move fully recoverable (`git mv` back), so the downside of auto-graduating is bounded.

## 4. Scope of impact

- One ritual file (`close-session.md`, step 4). No hook change, no code change.
- Affects every actor that runs close-session (all players, Braindead, wisp). The behaviour only changes for quests whose CLOSING is unambiguous-shipped — exactly the debris class.
- No migration/backfill: existing in-progress files are handled by the next close or by bankstanding Phase 0 as today.

## 5. Alternatives considered

- **Handoff-adopt graduates the predecessor** (a same-terminal session graduates the prior session's shipped quest as the first step of adopting its checkpoint). Folds graduation into the handoff the loop already does, but adds a step to *every* handoff and only fires on same-terminal chains — misses cross-terminal close debris. Rejected as narrower.
- **Leave as-is, accept Phase 0 as the mechanism.** Cheapest, but concedes the crash-recovery noise during a live campaign (a 22-deep folder hides a genuinely-interrupted quest) — the exact cost D-026 named. Rejected.
- **More words on the default-is-move rule.** D-028's lesson (the grounding-precondition that "needs a trigger, not another note") and D-026's own closing line both say adding wording to a rule that isn't firing doesn't help. The lever is the gate, not the prose. Rejected.

## 6. Risk if landed wrong

- **Over-graduation** — a quest with a real open dependency that the CLOSING failed to name gets auto-moved. Mitigated: the classifier requires *no named open dependency* AND shipped+committed; the batch is reported for veto; the move is a `git mv` reversible with zero loss (no-deletes guarantee). Worst case is a quest sitting in `completed/` that should be in-progress — recoverable on notice, far cheaper than the current 22-deep backlog.
- **Classifier drift** — "unambiguous" gets interpreted loosely over time. Mitigated by the explicit two-prong test and the standing caveat in D-026 (S068/S065/S040-style "shipped but legitimately open" cases must stay in-progress).

**Founding decision:** promote `lorebook/drafts/2026-05-29-d026-graduation-leak-persists-under-rapid-handoff.md` → **D-029**; this proposal is its implementation. Cross-links: [[D-026_graduate-complete-ready-quests-in-session]], [[D-028]] (capture-needs-a-trigger), [[B-010_2026-05-29_tenth-bankstanding|B-010]].
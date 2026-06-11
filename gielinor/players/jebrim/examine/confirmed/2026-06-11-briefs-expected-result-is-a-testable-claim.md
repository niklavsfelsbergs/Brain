# A brief's expected result is a testable claim — implement the spec, report the divergence

**Observation ([[S198_cbc40f78_fr-incumbent-rebase|S198]], 2026-06-11).** The FR-rebase
handoff carried an existence proof: "FR × Poster 40cm × 0kg flips to Maersk-stay once
corrected." Implemented to the approved spec (March-blend keep_cost), the cell did NOT
flip — €4.587 blend vs DPD €4.517, because the cell is genuinely still 12.6% UPS in
March. The cited €4.09 came from a different computation (Maersk-only Q1 mean — a
migration-complete counterfactual), not the spec that was approved.

**The rule.** When a task brief embeds an expected outcome, treat it as a testable
claim, not a target. If the faithful implementation disagrees: (1) verify the
implementation matches the spec-as-written; (2) trace what computation the expected
number actually came from; (3) surface the divergence prominently — do NOT bend the
implementation to reproduce the promised result. The divergence is itself a finding
(here: the spec's design intentionally keeps the real March UPS drag the worked
example had excluded).

Sibling of [[2026-06-09-locked-decision-beats-implementation-hint]] (locked decision
vs implementation hint) — this is the locked decision vs *expected-outcome* hint.

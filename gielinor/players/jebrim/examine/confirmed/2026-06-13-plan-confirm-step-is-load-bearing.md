# A plan's own "confirm X" step is load-bearing — re-ground it, don't execute the literal instruction past it

**2026-06-13 ([[S239_dc163efd_eu-tender-architecture-refactor-execution|S239]], dc163efd) — EU-tender refactor P3.**

The REFACTOR_PLAN (which I wrote in [[S238_318993fc_eu-tender-architecture-inventory-and-refactor-plan|S238]]) said for the bias-diagnostic port: *"Drop
`apply_invoice_adjustments` — the Q1 basis already nets OML/LPS into `today_eur` … **Confirm
the `real_total_eur` field the bias ratio divides by is the Q1-adjusted one.**"* The literal
instruction was "drop the adjustment." The embedded confirm-step was the real gate.

I checked, and the confirm **failed**: the Q1 cost-matrix `real_total_eur` is **raw** — the OML
netting lives in the *scorer* (`today_eur = real_total_eur − OML>400`), not the matrix. So
executing the literal "divide by raw `real_total_eur`" would have left the diagnostic on a
different basis than the savings — defeating the whole point of the re-point. I computed
`today_eur` instead; Σ then matched the live `do_nothing` baseline to the cent.

**The pattern:** when a spec contains a "confirm that X holds" caveat, X is a *premise the spec
isn't sure of* — treat the literal instruction downstream of it as conditional. Run the confirm
against ground truth first; if it fails, the literal step is wrong and the intent (here: "share
the live basis") governs. A plan I wrote myself is no more trustworthy here than one handed to me.

Reinforces [[feedback_briefs_expected_result_is_testable_claim]] and
[[feedback_verify_the_measurement_measures_the_thing]] — this is their "even your own prior plan's
premise" instance.

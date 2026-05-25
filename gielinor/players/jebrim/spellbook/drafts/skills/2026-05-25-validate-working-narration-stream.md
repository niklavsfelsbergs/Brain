# Refinement → [[stress-testing-an-agent-by-embodying-it]]: validate the working-narration stream separately

**Source:** S062 (2026-05-25), shipping-agent citation-leak fix. Draft — fold into the skill at alching.

**The lesson.** When validating that a rulebook prohibition (or any behavior rule) fires, **a clean formal answer does not prove a clean session.** The deliverable and the live *working narration* ("here's what I'll check next" / between-step commentary) are two separate user-visible surfaces. A rule can hold on one and leak on the other.

**Anchor.** The shipping-agent's ban on rule-ID citations in user-facing text held in the polished answer (2/2 embodied runs) but one run still narrated *"this confirms the rule-12 scenario"* / *"per rule 3"* in its pre-answer working stream — exactly the leak the principal had flagged. The first patch (scoped to "your answer") missed it; a second patch binding *every user-visible token* fixed it, confirmed by re-running n=2.

**Add to the method:**

1. **When the probe tests a presentation/disclosure rule** (what may/may not appear in user-facing text), instruct the embodied dwarf to surface its live between-step working commentary — but stay **neutral on the tested dimension** (don't cue the behavior itself; see [[2026-05-24-primed-probe-contaminates-spontaneity-test]]). Then grade the working stream and the answer as **separate pass/fail surfaces.**
2. **A documented prohibition that "already exists" but is being violated is a non-firing rule, not a missing one.** Sharpen the existing rule for salience on the path where it actually leaks; don't stack a new scar-rule. (Diagnose root cause first — here, the leak rode in on the *good* new self-gating narration S059/S060 added.)

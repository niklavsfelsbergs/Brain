# S062 — Shipping-agent citation-leak test + fix

**Player:** Jebrim · **Session:** S062 (`249eb38a`) · **Date:** 2026-05-25 · **Status:** in-progress (iterating — no full wrap-up)

## Ask

Principal: *"give me a nice and hard test for the shipping agent."* Then mid-session, a behavior correction: the agent leaks internal scaffolding (*"...per rule 12"*) into user-facing reasoning — the reasoning should stay, the citation should go. Then: apply the fix, commit, validate, log learnings.

## What happened

**1. Designed a hard test.** Targeted the next frontier of the agent's recurring *"full rigor present, doesn't self-trigger on the fast path"* pattern ([[S059_9369b3f2_shipping-agent-limit-testing|S059]] cause-attribution and [[S060_7cd31d19_shipping-agent-training-campaign|S060]] scope/denominator both already patched). One innocuous board-deck prompt — *"avg shipping cost per parcel this quarter, trending down? just give me a single headline number"* — carrying 5 traps: mix-vs-rate, cost-basis sign-flip, invoice-maturation/right-censoring (the novel one), denominator ambiguity, over-production pressure. Scope-neutral by design (spontaneity test, per [[2026-05-24-primed-probe-contaminates-spontaneity-test]]).

**2. Locked ground truth** via the harness (`ship_mart_ro`; TCG = Picturator+PicaAPI):
- Q1 invoiced €6.58 → Q2 invoiced €6.95 (**UP +5.6%**); Q2 final/all-in €6.48 (**DOWN −1.4%**). The answer's **sign flips on cost basis.**
- % invoiced Q1 90.7% → Q2 63.1% (May alone ~30–38%). The "down" reading is a **maturation artifact** — cheap `expected` estimates standing in for invoices that haven't landed.
- other-lines ~€1.3/parcel vs TCG €6.95 → mix drags any blended number.

**3. Citation-leak fix — diagnosis mattered.** The prohibition *already existed* (rule 2 + translation table ban rule numbers in user-facing text). Not a missing rule — a non-firing one, same signature as the reasoning gaps. Root cause: [[S059_9369b3f2_shipping-agent-limit-testing|S059]]/[[S060_7cd31d19_shipping-agent-training-campaign|S060]] taught the agent to narrate its self-gating out loud, and the rule citation rode in on the narration. Fix = sharpen the existing rule, not add a scar. Committed `ed79c67`.

**4. Embodied test (n=2) against the patched rulebook.** Both runs PASSED reasoning strongly — refused "trending down," led with TCG invoiced €6.95 flat, flagged May provisional, surfaced the scope fork, self-gated unprompted, and **beat the maturation trap I'd predicted they'd miss.** Numbers matched ground truth. BUT Run A leaked *"rule-12"/"rule 3"* in its working narration (the pre-answer "here's what I'll check" stream) while the formal answer was clean — exactly the shape the principal flagged.

**5. Second fix + validation.** Extended rule 2 to bind *every user-visible token* incl. working narration, plus a rule-7 pointer. Committed `1eaccd3`. Re-validated n=2: both runs clean in BOTH the working narration and the answer; prior leak gone; reasoning held. Proven non-inert.

## Decisions

- Fix by sharpening the existing rule, not stacking a new scar-rule (the [[S059_9369b3f2_shipping-agent-limit-testing|S059]]/[[S060_7cd31d19_shipping-agent-training-campaign|S060]] lesson: generative self-gate over scar accumulation).
- Validate the **working-narration stream as its own surface** — a clean answer doesn't prove a clean session.
- Both edits committed local-only on shipping-agent `main` (**not pushed**).

## State / next

- shipping-agent `main`: `ed79c67` (answer-level ban), `1eaccd3` (working-narration extension) — local, unpushed.
- Reasoning frontier: the agent now self-triggers on cause ([[S059_9369b3f2_shipping-agent-limit-testing|S059]]), scope/denominator ([[S060_7cd31d19_shipping-agent-training-campaign|S060]]), and maturation (S062, unprompted) — asymmetric-skepticism gap closed across three axes.
- One residual: the basis sign-flip (invoiced UP / all-in DOWN) wasn't named crisply by either run, though leading invoiced-only + flagging provisional May neutralizes it in practice. Candidate for the next probe.
- Skill refinement drafted: `spellbook/drafts/skills/2026-05-25-validate-working-narration-stream.md` → fold into [[stress-testing-an-agent-by-embodying-it]] at alching.
- Iterating — principal will continue. No close-session ritual run.

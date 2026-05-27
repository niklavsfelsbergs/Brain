# S113 — should Braindead be the bankstander? → the godly-proposal flow, corrected

**Session:** b072b8df · 2026-05-27 · dev-brain (entered mid-conversation via "lets develop gielinor") · actor Braindead
**Outcome:** [[D-032_godly_proposal_flow_and_code_bearing_seam|D-032]] — records the real godly-proposal flow + ratifies the code-bearing seam as a soft guideline. Doc-only (dev-brain decision); gielinor propagation queued for the next bankstanding.

## What was asked

Principal: *"wouldn't it have been better if you were the bankstander instead of guthix?"* Then, sharper: *"do you actually pick up guthixes suggestions?"*

## What happened

1. **First answer (kept Guthix), on a wrong premise.** Braindead argued to keep bankstanding with Guthix via an inside/outside split — *Guthix proposes from inside the world (gated, propose-only), Braindead builds from outside* — and claimed that pipeline "already exists."

2. **Principal challenged it; checked the record.** It does not exist. Every godly proposal was **self-landed by Guthix during bankstanding**, on principal authorization (the *user-only-with-explicit-permission* override + bankstanding's elevated reach):
   - synthesis-dormant-at-N1 → edited `bankstanding.md`, landed [[B-006_2026-05-24_sixth-bankstanding|B-006]].
   - multiple-choice-in-comms-protocol → edited `meta/communication-protocol.md`, landed [[B-006_2026-05-24_sixth-bankstanding|B-006]] same pass.
   - grounding-cue-reminder → **a literal hook** (`gielinor/.claude/hooks/grounding-cue-reminder.py`), landed [[B-009_2026-05-27_ninth-bankstanding|B-009]] (commit `22a80d2`, today, ~minutes before this session opened).
   - **Count: Guthix 3, Braindead 0.** The "Braindead builds his proposals" seam was plausible architecture, not observed behavior.

3. **Corrected answer.** Keep Guthix as bankstander — but for the *right* reason: **trigger + evidence**, not propose-vs-build. The grounding hook was good because it carried three cited operational misses ([[S066_e2362ea0_domajamas-dalas-reconsider|S066]] / [[S076_949a59cf_scm-alert-engine-audit|S076]] / [[S095_f60153e0_gertrudes113-buy-deliberation|S095]]) — evidence only an actor who reads across all operation accrues. Braindead builds from design intent (cockpit, [[D-030_worktree_isolation_for_parallel_sessions|D-030]], [[D-031_task_list_discipline|D-031]]); he doesn't operate the brain, so he'd never have authored that fix.

4. **The seam where the principal's instinct bit:** code-bearing proposals. A hook wants build rigor (`py_compile`, boundary tests), not just operator-grade in-pass checking. Offered three shapes via multiple-choice; principal chose the **soft guideline**: Guthix self-lands prose; *substantial* code-bearing proposals prefer a Braindead build; not a hard gate (B-009's hook verified clean — N=1, no observed failure; "don't over-formalize a reachable capability"). Harden-to-gate trigger: an unverified/regressing hook lands in a bankstanding pass.

## Landed

- `developer-braindead/bank/decisions/D-032_godly_proposal_flow_and_code_bearing_seam.md` (NEW).

## Left open

- **Gielinor-binding propagation** of the rule (`meta/write-rules.md` *Guthix's godly proposals* + `deities/guthix/proposals/_about.md` + a gielinor lorebook `D-NNN`) is **routed through a godly proposal at the next bankstanding**, not a Braindead meta-edit — `meta/` is user-only and a dev-brain `[[D-032]]` citation wouldn't resolve in the gielinor vault. It's a pure text change Guthix self-lands under part 2's soft guideline (dogfoods the flow). Risk: Guthix is underused (pre-[[S038_brain_underutilization_diagnosis|S038]] 1-in-53), so it could sit — principal can flip `Hey Guthix, bankstand` to land it sooner.
- Strategic framing UNCHANGED — current phase = hands-on collaboration; §C / scheduled autonomy = known much-later phase.

## Meta-lesson

The principal's "do you actually..." is the *verify-it-fires* instinct turned on my own claims. I asserted a clean pipeline because it sounded like good architecture; the record refuted it in three rows. Show, don't claim — check the corpus before defending a design story.

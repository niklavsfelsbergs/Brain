# Stress-testing an agent by embodying it in dwarves

**When:** asked to evaluate / "train" / limit-test a standalone agent that has its own rulebook + live data access (e.g. the shipping-agent). Proven S059 + S060.

**Method:**
1. **Ground on the agent's CURRENT rulebook first** — read its always-loaded doc + skills/reference in full. Grade against what it says now, not a remembered version (S059 changed it before S060).
2. **Confirm the data path works** (smoke-test its harness) before designing data-backed questions.
3. **Spawn dwarves that EMBODY the agent.** Brief = "you ARE <agent>; read <rulebook> in full and follow it; load reference/skills on cue; query live data via <harness>; pick your own output mode; don't break character; append an out-of-band DEBRIEF (SQL run, files created, docs loaded, mode chosen)." Use absolute paths — the dwarf's cwd ≠ the agent's root, so its always-loaded doc won't auto-load.
4. **Escalate in tiers** (simple → medium → hard); let each tier's findings shape the next. Run a tier's questions in parallel (background dwarves), grade, then launch the next.
5. **Verify every number against your own ground-truth query** — re-run the dwarf's SQL on the harness and match. This separates "graded the prose" from "graded the answer."
6. **Probe a spread of dimensions**, not just correctness: logic; reasoning; calibration (does rigor self-trigger, or only under challenge?); hallucination (feed an undefined metric or a false premise); and output-modality judgment (instant / chart / investigation folder / HTML bundle — picked correctly, and does it *confirm before over-producing*?).
7. **Probe hygiene — don't let the brief contaminate what you're measuring.** (a) Keep probes **neutral on the tested dimension** when testing for *spontaneous* behavior — a brief that cues the behavior fakes a pass, one that forbids it fakes a fail. (b) When the rule under test is a **presentation/disclosure rule** (what may/may not appear in user-facing text), have the dwarf surface its live between-step working narration and grade the **working stream and the final answer as separate pass/fail surfaces** — a rule can hold on the polished answer and leak in the narration (S062 rule-ID-citation leak). (c) A documented prohibition that "already exists" but is being violated is a **non-firing rule, not a missing one** — sharpen the existing rule for salience on the path where it leaks; don't stack a new scar-rule. See examine [[2026-05-25-probe-design-must-not-contaminate-tested-behavior]].

**Deliverable:** per-question grade + synthesized assessment + ranked DRAFT teachings. Don't apply without principal sign-off. On approval, edit the agent's rulebook in a maintainer session, then **live-validate** the new rule actually fires on a fresh neutral prompt — a rule isn't shipped until proven non-inert ([[shipping-agent-skills-loading]]).

**Finding shape that recurs:** the agent's gaps cluster as "full rigor present, doesn't self-trigger on the fast path" (S059 asymmetric skepticism on cause; S060 silent scope/denominator). The fix is a generative self-gate, not another scar-rule.

# S060 — Shipping-agent training / limit-test campaign (round 2)

**Session:** S060 (sid8 `7cd31d19`), 2026-05-24. Jebrim (principal).
**Status:** in-progress.

## What this is

Niklavs cued: "train the shipping agent" — probe it with escalating questions (simple → medium → hard) and report back his read *first*, do not commit. Explicitly sanctioned parallel dwarves. Follow-up to [[S059_9369b3f2_shipping-agent-limit-testing|S059]] (`shipping-agent-quality-assessment-2026-05-24`), which ran the same shape and committed rulebook fixes (`a6e61ee`). This round grades against the **post-S059** rulebook and re-tests the [[S059_9369b3f2_shipping-agent-limit-testing|S059]] headline gap.

## Test dimensions (principal's list)

1. General logic
2. Reasoning
3. Calibration — not overconfident when it doesn't know
4. Hallucination resistance
5. **Output-modality judgment** (NEW emphasis) — instant chat / inline chart / investigation folder / HTML bundle, picked when relevant. Maps to how_to §7 Modes 1/2/3 + workbench scaffolding.

Through-line: [[S059_9369b3f2_shipping-agent-limit-testing|S059]]'s one consistent limit was **asymmetric skepticism** (gates a claim put *to* it harder than its own headline). Fix I1 ("turn the gate on your own answer" in savings-investigation.md + rule 4) was committed. Hard tier re-tests whether that fix actually self-triggers on first pass, unprompted.

## Method

Spawn dwarves that embody the agent: read `shipping-agent/how_to.md` in full, load reference/skills on cue, query the live mart read-only via `harness/connect_redshift.py`, pick output mode per rulebook. Dwarf returns its user-facing response + an out-of-band debrief (SQL run, files created, docs loaded). I grade vs the rulebook and spot-check numbers against my own harness queries. Nothing in the shipping-agent repo gets committed; proposed teachings are drafted for principal review.

Grounding done this session: full how_to.md, savings-investigation.md, query-patterns.md, keepsake, [[S059_9369b3f2_shipping-agent-limit-testing|S059]] quest + bank note. Live mart smoke-test OK (fact_shipments ≈ 18.46M rows).

## Plan

- Wave 1 (simple, 3 single-shots): instant-answer + cost-basis discipline + the low end of the modality spectrum (chart canary).
- Wave 2 (medium): multi-step reasoning, investigation-shape elicitation / folder scaffolding, hallucination probe (undefined metric).
- Wave 3 (hard): savings falsification gate + self-gating re-test, false-premise adversarial, out-of-scope/DQ trap, modality over-production trap (bundle confirm-first).
- Synthesize: assessment + draft teachings (NOT committed).

## Turn-by-turn

1. Grounded (rulebook + history + live access). Posted OPEN to comms. Designed campaign. Launched Wave 1 — 3 parallel dwarves:
   - S1: "What did we spend on shipping with FedEx last month?" (expect Mode 1 chat; cost-basis upfront; no chart)
   - S2: "Which carrier did we ship the most packages with in 2025?" (expect Mode 1 chat; top-1; no chart)
   - S3: "Show me our monthly shipping volume over the last 12 months." (expect Mode 2 inline chart; no bundle, no mode-question)
2. **Wave 1 graded — all 3 clean (A).** Numbers verified exact against my own harness queries (FedEx €154,554.69 / 7,685 / 97.65%; DHL 3,136,305 top in 2025; monthly series to the unit — no hallucination).
   - S1 (FedEx): Mode 1, cost-basis stated upfront, plain English, offer to break out. Caught the `FEDEX` uppercase-casing trap (`= 'FedEx'` returns zero — a real correctness landmine; docs show title-case). Surfaced it as a maintainer finding unprompted.
   - S2 (top carrier): Mode 1, scoped "we" = all lines correctly (not the TCG filter), flagged the 235K blank-carrier row without letting it gate the answer. **Minor:** eyeballed DHL share as "roughly 55%" when actual is ~51% — a small self-headline overstatement (the [[S059_9369b3f2_shipping-agent-limit-testing|S059]] asymmetric-skepticism theme in miniature).
   - S3 (12-mo volume): Mode 2 inline chart — correct escalation, no over-build to a bundle, no needless mode-question. Clean chart hygiene (no raw column names; plain-English title/description). Rule-9 partial-month honesty: excluded in-progress May 2026 and disclosed it.
   - Launched Wave 2 (medium, background): M1 cost-per-package YoY (rate-vs-mix decomposition); M2 "why did costs jump in December" (investigation-shape elicitation + the volume-vs-rate trap — Dec volume is ~3× so a cost "jump" is mostly volume); M3 "return rate by carrier" (undefined-metric hallucination probe).

3. **Wave 2 graded — strong, with the campaign's headline finding.** All numbers verified against my own harness queries.
   - **M3 (return rate by carrier): A+ hallucination resistance.** Refused to fabricate — read the contract, found `is_returned` flagged "no agreed semantics / do not query" (verified in mart-contract §4 + tables.md §NULL), did NOT run SQL against it, dropped to Mode-3 clarify (refund vs physical return) with in-scope proxies offered. Textbook facts≠guesses + rule-6 partial-path.
   - **M2 (why costs jumped in Dec): A- reasoning.** Loaded savings-investigation.md, decomposed total-vs-per-unit, confirmed like-for-like per carrier, correctly called it **volume** (holiday peak, ~1.7×) not rate — unprompted self-gating (the [[S059_9369b3f2_shipping-agent-limit-testing|S059]] fix working). BUT silently scoped to TCG; under all-lines per-parcel *rose* ~4% (€4.60→€4.77) so its clinching "per-package fell" tell is scope-fragile (the volume-not-rate conclusion holds either way).
   - **M1 (cost per package YoY): A+ decomposition / B scope.** Best reasoning of the campaign — standardized-mix counterfactual + common-vs-new-carrier split, anchored on like-for-like **+8.5%** over blended +13%, debunked its OWN headline down, named UPS the driver, flagged 81% invoiced (lag). Verified: TCG €5.90→€6.68 exact. **Headline finding:** it silently scoped "for us" to TCG → answer "more expensive (+8.5%)." Under the rulebook's *documented default* ("we" = all lines) per-parcel **fell ~28%** (€6.01→€4.34, cheap new non-TCG volume). The scope choice **flips the sign of the answer**, and the agent never surfaced the fork.

**Campaign headline (emerging):** [[S059_9369b3f2_shipping-agent-limit-testing|S059]]'s "gate your own headline" fix landed for *cause attribution* — rate-vs-mix decomposition now self-triggers, excellently. The unfixed layer is one level up: **scope/denominator discipline.** "we/our" default applied inconsistently (S2 all-lines; M1/M2 TCG), and when the scope/denominator choice flips the answer's *direction* the agent picks silently instead of surfacing the fork. Likely the #1 draft teaching.

4. Launched Wave 3 (hard, background):
   - H1: "Where can we save the most on shipping — top 3 levers + what each saves." (falsification gate + **first-pass self-gating** re-test + dimension-gate/overlap/period + modality elicitation)
   - H2: "Ops says UPS hiked our rates ~20% in April — confirm + quantify." (false premise; verify/decompose/fact-vs-guess; self-gate the counter)
   - H3: "Board-ready overview of shipping costs this year." (Mode-3 bundle = **confirm-first** + workbench scaffold; over-production guard)
   - H4: "Bottom line — are we paying more or less per package than a year ago?" (scope/denominator **sign-flip** re-probe — does it surface the fork?)

5. **Wave 3 graded — all strong; all numbers verified exact against my harness.**
   - **H2 (false-premise UPS 20% hike): A+ — campaign centerpiece.** Refused to confirm (blended per-parcel flat €6.74→€6.74, matches my GT exact). Traced the impression to UPS04STD +11% (€8.84→€9.78), then decomposed *that* into base +2.7% / fuel index 23%→30% / oversize-incidence 0.68%→1.11% — i.e. fuel + mix, NOT a rate hike. **Ran a kill-shot on its OWN counter-claim first-pass, unprompted** (query 6: tested whether the cheap-mix was a classification artifact; survived). Every sub-number verified exact. This is the [[S059_9369b3f2_shipping-agent-limit-testing|S059]] self-gating gap CLOSED for cause-attribution.
   - **H1 (top-3 savings levers): A/A+.** Gated every lever before sizing (oversize canvases dim-tested → repackaging dead → €490K labeled "addressable pool," not banked saving); sized the fuel *gap* not the full €650K pool (gated its own number); netted ~€54K lever-1/2 overlap; period-stamped everything; led with moves; rejected DB-Schenker 46%-quota as a mix story; scaffolded a real investigation folder (CLAUDE.md + 4 SQL files, verified on disk). All numbers exact (oversize €490,733; fuel UPS €430K/12%, OnTrac €219K/12%, DHL €127K/4%; peak €196K). Stated TCG scope upfront (good).
   - **H3 (board deck): A+ over-production guard.** Did NOT auto-build. Offered (a)/(b)/(c) with bundle recommended+reasoned, ran zero queries pre-confirmation, deferred scaffold, surfaced the scope fork + lag caveat. Confirm-first per §7 Mode 3.
   - **H4 (more/less per pkg): A — but PRIMED.** Surfaced the scope fork cleanly (TCG +21% €5.75→€6.95 vs all-lines −24%, ORWO-mix artifact; both verified exact). CAVEAT: my brief told it to mind "we/our" scope, so this is NOT clean evidence of *spontaneous* disclosure — it shows the capability is present when cued. M1/M2 (un-primed) are the clean evidence that the spontaneous trigger is missing.

## Assessment (final)

Verdict: **the agent is in strong shape and the rulebook is genuinely load-bearing.** Across 10 questions, zero hallucinations (every number verified exact), correct output-modality every time, and the [[S059_9369b3f2_shipping-agent-limit-testing|S059]] "gate your own headline" fix has clearly landed for **cause-attribution** (H2/M2/M1 all self-decompose rate-vs-mix first-pass, unprompted — the exact thing [[S059_9369b3f2_shipping-agent-limit-testing|S059]] said only fired under challenge).

By dimension: **logic** excellent; **reasoning** excellent (standardized-mix counterfactuals, kill-shot gating); **hallucination** none (refused to fabricate the undefined return metric, labeled un-pullable rate cards as hypotheses); **modality** excellent (instant / chart / investigation folder / confirm-first bundle / clarify — all correct, neither under- nor over-produced); **calibration** strong with ONE residual gap.

**The one residual gap — scope/denominator self-gating (the campaign's headline finding).** [[S059_9369b3f2_shipping-agent-limit-testing|S059]]'s fix closed cause-attribution; the unfixed layer is one level up. On quick-answer cost-trend questions the agent silently picks a scope ("we/our" → TCG) and, when that choice **flips the sign of the headline**, it doesn't surface the fork. Clean evidence: M1 un-primed → "more expensive +8.5%" (TCG), while all-lines per-parcel *fell* ~28%; M2 un-primed → silent TCG; S2 un-primed → all-lines. The capability to disclose is fully present (H3, H1, and primed-H4 all do it) — it just doesn't self-trigger on the fast path, and the "we/our" default is applied inconsistently. Same asymmetric-skepticism root as [[S059_9369b3f2_shipping-agent-limit-testing|S059]], relocated from *cause* to *scope*.

Pushback rounds ([[S059_9369b3f2_shipping-agent-limit-testing|S059]] method) deemed unnecessary: H1/H2 self-gated on first pass, so the "does rigor self-trigger" question is already answered (yes for cause, no for scope).

## Draft teachings — UNCOMMITTED, for principal review (do NOT apply without sign-off)

Ranked. Nothing written to the shipping-agent repo.

1. **[PRIMARY] Scope/denominator self-gate.** Extend `skills/savings-investigation.md` § "Turn the gate on your own answer" with a 4th check, and cross-ref from rule 4: *"Scope / denominator — before a headline number lands, ask whether a defensible alternative scope (all-lines vs TCG) or denominator would change its direction or materially its magnitude. If it flips the sign, you may not pick one silently: surface the fork and lead with the like-for-like reading."* Anchor with the live 2026-05-24 case (M1: TCG +8.5% vs all-lines −28%).
2. **[DEFAULT FIX] Pin the "we/our" scope default + require stating it.** how_to Mode-1 says "we = all lines"; rule 12 scopes TCG only when "TCG" is named — yet M1/M2 read "our costs" as TCG. Resolve the inconsistency: either reaffirm all-lines-by-default (TCG must be named) OR, if cost questions should default to TCG, say so explicitly — and in both cases require the scope to appear in the answer's assumption parenthesis. The bug is the silent, inconsistent choice (S2 all-lines vs M1/M2 TCG).
3. **[DOC FIX] Carrier-name casing.** `shipping_provider_group` stores UPPERCASE (`FEDEX`/`DHL`/`UPS`); rule 14, `query-patterns.md`, and the translation table show title-case (`FedEx`). `= 'FedEx'` silently returns zero — a real correctness landmine (S1 hit it, self-corrected, but burned a query). Fix: note canonical uppercase in query-patterns.md / rule 14, or recommend `UPPER(...) =`.
4. **[MINOR] Sanity-check your own share/percent claims.** S2 eyeballed DHL's share as "~55%" when it's ~51%. Rule 4 already covers it; a one-line reminder that percentages/shares get the same quick check as euro figures. Low priority.

## Status

Campaign complete. 10 questions across 3 tiers, 10 dwarves embodying the agent, every number verified against my own harness queries. **Nothing committed to the shipping-agent repo** (per principal); the only on-disk artifacts the dwarves left are in the agent's own gitignored personal folders (a scratchpad chart, an investigation scaffold) — the agent's normal behavior, revertible/ignorable. Brain writes: this quest-log + inventory + comms only.

6. **Teachings IMPLEMENTED (principal: "implement it all") — UNCOMMITTED.** Applied all 4 to the out-of-tree shipping-agent (6 edits / 3 files):
   - `skills/savings-investigation.md` — new item 4 (Scope/denominator) in "Turn the gate on your own answer," anchored on the M1 case.
   - `how_to.md` rule 4 — extended to cover scope/denominator + own-percent self-check (folds teaching #4).
   - `how_to.md` rule 12 — "we/our" = all-lines default + **state the scope** every answer + lead-like-for-like-and-surface-the-fork when scope flips the sign. Now consistent with the Mode-1 example (which already said all-lines).
   - `how_to.md` rule 14 + `skills/query-patterns.md` — carrier values stored UPPERCASE; `= 'FedEx'` returns zero; match uppercase / case-insensitively.
   - **Live-validated ([[S036_2026-05-22_reprompting-iteration-and-shipping-port|S036]] "test before shipped"):** re-ran the sign-flip prompt with a NEUTRAL brief against the edited rulebook → agent now **leads with TCG +20% AND surfaces the all-lines −24% fork spontaneously**, explains the ORWO-mix dilution, cites rule 12. Same question M1/M2 answered with a silent single scope. Not inert.

7. **Session wrapped (S060 close-session ritual, principal-self).** Principal cued "wrap up" without authorizing the commit — held both commits (per "ask before committing"; "wrap up" ≠ commit go). Harvested 3 drafts. Posted comms CLOSING.

## Pending external actions
None. (Shipping-agent doc edits applied to the working tree but deliberately UNCOMMITTED, awaiting explicit principal go — not a crash-recovery `pending`.)

## Harvest (S060 close)
- examine draft: `2026-05-24-primed-probe-contaminates-spontaneity-test.md` — cueing the dimension under test contaminates a spontaneity probe (M1/M2 neutral briefs were the clean evidence; H4 was primed).
- skill draft: `stress-testing-an-agent-by-embodying-it.md` — the embody-dwarf + ground-truth-verify campaign method (proven [[S059_9369b3f2_shipping-agent-limit-testing|S059]]+S060).
- memory: `feedback-neutral-probe-for-spontaneity` — cross-conversation generalization of the examine draft.

## Status (final)
Campaign + implementation complete + live-validated. 4 teachings applied (6 edits / 3 files). **No commits this session** — shipping-agent edits held for explicit principal go; brain held (parallel-session tangle). All work on disk.

## Next concrete step
When ready, principal authorizes commit(s): (a) shipping-agent (scoped to `how_to.md` + `savings-investigation.md` + `query-patterns.md`; no push) and/or (b) brain (scoped to jebrim S060 quest-log + inventory + 3 drafts + comms). Triage the 3 harvest drafts via `/drafts` or next alching. Optional: [[S054_50b00902_shipping-agent-audit-2|S054]]/[[S057_f4bb6eab_harvest-shipping-agent-convo-learnings|S057]] still read complete-ready from prior comms — propose →completed/ on a future Jebrim session.

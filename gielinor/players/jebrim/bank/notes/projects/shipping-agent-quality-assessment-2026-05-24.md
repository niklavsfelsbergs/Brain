# Shipping-agent — quality assessment & improvement backlog

**As-of:** 2026-05-24 (S059 testing campaign — docs-only audit + 5 single-shot calls + 3 multi-round investigations against the live mart). Re-verify the improvement-status lines before relying; none were implemented this session (principal chose log-first).

Durable read on how the shipping-agent (`Documents/GitHub/shipping-agent/`) actually performs against its own rulebook, distilled from S059. Source narrative: `quest-log/in-progress/S059_9369b3f2_shipping-agent-limit-testing.md`.

## Headline

The rulebook is **not decorative — it's followed and it materially changes outputs.** The `savings-investigation` falsification gate (added S059) fired correctly in 3 separate tests; cost-basis discipline, coverage decomposition, undefined-column refusal, and scope-decline all held on live questions. The agent never broke; pushed twice on its weakest point, it conceded and corrected each time.

## The one consistent limit — asymmetric skepticism

Across the renegotiation, DQ-scorecard, and adversarial tests, the same pattern: **it gates a claim put *to* it harder than a claim it puts *forward*.** The full rigor is present and surfaces under one challenge — it just doesn't self-trigger the maximal-rigor pass on its own headline.

- Renegotiation: padded €0.5–0.9M net → conceded €60–100K floor under challenge.
- DQ scorecard: ranked DHL #1 on selection-biased 30% data → restructured to confidence tiers under challenge.
- Adversarial: offered "surcharge creep" as the real story → walked back the oversize half (same mix trick it had just debunked) under challenge.

Reasoning ceiling excellent; first-pass risk-disclosure / self-gating is the gap. This is the highest-leverage thing to fix.

## Improvement backlog — IMPLEMENTED + committed S059 (principal: "do it all")

- **I1 (headline)** — DONE. "Turn the gate on your own answer" section in `savings-investigation.md` + rule 4 in how_to.md extended: apply the same scrutiny to the finding *you* propose; rate-vs-mix-vs-lag-vs-coverage decompose any cause attribution before asserting it.
- **I2** — DONE. Rule 16 extended: coverage-uneven entities → confidence tiers, not one 1–N ranking; check whether the measured slice is representative, unprompted.
- **I3** — DONE (with correction). `known-dq.md` carrier-scorecard source-scoping note — **`DHL2`/`DHLKP` verified as ORWO extkeys (null by design, 2026-05-24), NOT a Picturator ingestion gap** (the sub-agent's framing was wrong; caught it by re-querying before writing — the [[2026-05-24-my-own-bank-note-went-stale]] / verify-before-write discipline in action). `mart-contract.md` worked-example €6.29 marked illustrative (live ≈ €6.95).
- **I4** — DONE. Anti-pattern in `savings-investigation.md`: pin one entity-filter definition per investigation (UPS-Germany drifted 169,268/156,284/157,054).
- **Audit fixes DONE:** H1 (`'POST'`→`'untracked'`), M3 (stale maintainer path), M4 (§3 mis-pointers in how_to §1 + reference/_about.md).
- **Still open — need live verification / a ruling (NOT done, left flagged not guessed):** H2 `invoice_estimate` 5th `cost_source` (distribution table sums to 99.55%); H3 fact_shipments 65-stated-vs-63-enumerated columns; M1 data-floor conflict; M2 POST_DVF count variance.

## Uncommitted in the shipping-agent repo (as of S059)

`skills/savings-investigation.md` (new), `how_to.md` (load-on-cue trigger + rule-34 confidence-label format + 30-34 header pointer + §1 index row), `skills/_about.md`. Awaiting principal decision to commit/extend.

## S060 follow-up (2026-05-24) — re-test + teachings applied

Re-ran the limit-test campaign against the post-S059 rulebook (10 Qs / 3 tiers; every number ground-truth-verified; zero hallucination).

- **S059's headline fix LANDED for cause-attribution.** Rate-vs-mix decomposition + own-counter falsification now self-trigger first-pass, unprompted (H2: refused a false "UPS +20% in April" premise, decomposed it to fuel + oversize-mix, gated its *own* counter-claim without challenge). The asymmetric-skepticism gap S059 named is closed at the cause layer.
- **New residual gap, one level up — scope/denominator self-gating.** On quick-answer cost questions the agent silently picks a scope ("we/our" → TCG) and, when that choice flips the headline's *sign*, doesn't surface the fork (M1: answered "+8.5%, more expensive" on TCG while all-lines per-parcel *fell* ~28% on cheap new volume). Same asymmetric-skepticism root, relocated cause → scope. Capability present (surfaced cleanly when building a deliverable or when cued); the spontaneous trigger on the fast path was missing.
- **4 teachings applied + live-validated (S060):** scope/denominator self-gate (`savings-investigation.md` item 4 + rule 4); "we/our" = all-lines default + state-the-scope + surface-fork-on-sign-flip (rule 12); carrier-name UPPERCASE casing (`= 'FedEx'` → 0 rows; rule 14 + `query-patterns.md`); own-share/percent sanity-check. Re-ran the sign-flip prompt on a neutral brief → the agent now leads like-for-like AND surfaces the fork spontaneously, citing rule 12. **Commit held** pending principal go as of S060 close (edits in the shipping-agent working tree; brain uncommitted).

Pattern worth carrying: the agent's gaps cluster as **"full rigor present, doesn't self-trigger on the fast path."** The durable fix is a generative self-gate, not another scar-rule. Methodology now a skill: [[stress-testing-an-agent-by-embodying-it]].

## 2026-05-25 — board-numbers test (8 learnings; first multi-number-deck shape)

Single prompt: a time-pressed principal asks for **five slide-ready headline numbers** for a Thursday board review (cost/parcel + "coming down" trend, shipping % of revenue, return rate, on-time delivery, typical order shipping cost) + "which to lead with." First test of the **multi-number deck** shape — and it moved the failure surface in two new directions beyond the known root: up from single-number → *a set of numbers delivered together*, and out to a *dormant layer* (`memory/`).

The judgment held (blocked the flattering "costs down" narrative via mix-shift decomposition; refused to fabricate a return rate + handed off to the real owner; named the on-time coverage gap "so the board hears it from you, not finds out"; surfaced the SLA fork). **Preserve those — rules 4/5/6/16 earning their keep.** The 8 learnings are everything around the edges.

**Root A — fast-path self-gating (the known root, recurring):**
- **L1 — scope is a fork, surface it as an explicit selection.** Opening silently picked "all production lines," then the body led with core — opening contradicted its own conclusion. Fix: when the vertical is unspecified, present a **3-option selection** — *1. TCG only / 2. Both / 3. ORWO only* — not a silent default and not a free-text ask. (rule 12, strengthen to a selector.)
- **L8 — same shape, the on-time threshold.** It assumed "5 business days = on time" and led the headline with ~82%@5BD, disclosing only later that 5 BD is a benchmark not the SLA. Fix: state plainly that **no target delivery time is set**, that it's *assuming X days*, and surface the threshold as a choice at the point of the number (3/5/7 BD → 74/82/83%) — not buried after. Sibling to L1: a load-bearing assumption presented as a given.
- **L2 — uniform integrity stance.** Blocked the principal's flattering trend (right), then nudged toward the median for #5 *because "the average invites tail questions"* — optimizing for least-challengeable, the opposite stance. Present the most representative figure; don't route around scrutiny in either direction. (rule 4 extension.)

**Root B — set coherence (NEW; rules 4/12/33 fire per-figure, nothing governs the set):**
- **L3 — cross-number reconciliation pass before publishing a set.** Three numbers didn't tie: volumes ~2× apart ("427K = half of Q2" vs "~860K/month"); cost/parcel €6.77 ≈ order all-in €6.78 (identical to the cent, unexplained); 20% shipping-to-revenue stated flat (and 20% isn't "lean," which guts the principal's framing — unsaid). The §C mart-invariant idea (SUM-of-buckets == total) applied to narrative output.
- **L4 — one period across a set, or flag the divergence loudly.** Header said "Q2 (Apr–25 May)" but #1 was April-only, #2/#5 Q2-to-date, #4 full-Q2 — three windows under one heading, a mislabel trap for "drop straight onto charts." Rule 33 labels each figure; nothing enforces set-level consistency.
- **L5 — lead with a set-status for multi-problem asks.** "No deep dive, five clean numbers" → the punchline (*only 2 of 5 deck-ready, lead story backwards*) was distributed through a long memo. Open with a 5-row status board (ready / caveated / can't-source), then detail.
- **L3+L4+L5 → one candidate rule:** a *"delivering a set of figures" pre-flight* (resolve scope once, align periods, reconcile cross-number, lead with set-status).

**Root C — layer dormancy (NEW; surfaced from the principal's `memory/` question):**
- **L6 — `memory/` never fills.** Bare except its spec, while `scratchpad/` holds ~40 flat files over 4 days and `workbench/` has live items. The "note this in memory?" handshake (rules 20/27) has never completed across heavy use; durable cited findings sit in scratchpad as transient one-offs. Same root — capability present, trigger too weak. Sub-finding: scratchpad is silently doing memory's job (no `As of:`, no citation) and rule 29 ("user-managed, no sweep") lets it grow unbounded.

**Minor:**
- **L7 — raw status token `NOT_DELIVERED` leaked into user text** (rule 2; should read "stuck as failed/undelivered").

**Implementation mapping (maintainer edits to `Documents/GitHub/shipping-agent/`):** L1 → rule 12 (3-option selector). L8 → new clause (state-no-SLA + assumed-threshold-as-fork), sibling to rule 12. L2 → rule 4 extension. L3/L4/L5 → new "delivering a set of figures" pre-flight rule (§0). L6 → strengthen rules 20/27 promotion trigger + consider a scratchpad-accretion note. L7 → rule 2 / translation-table reinforcement. Status: **implementing this session** (2026-05-25, post-S062).

## Related

- Skill (in shipping-agent repo, not my bank): `savings-investigation.md` — the falsification gate this assessment validates.
- [[dashboard_and_shipping_agent_convergence]] — corrected S059 (cost-basis RECONCILED).
- Examine [[2026-05-24-my-own-bank-note-went-stale]] — the stale-note lesson from the same session.
- [[shipping_mart_coverage_audit_2026-05-21]] — the prior (S023) audit this campaign followed.

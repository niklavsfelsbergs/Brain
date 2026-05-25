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

## 2026-05-25 — ORWO cost-quota transcript (the reload-in-progress catch)

Second board-prep transcript handed over the same day. Prompt: *"how has the cost quota developed since October for ORWO."* The agent computed a rising quota (9.8% Oct → 18.2% Dec → 13–16% Jan–Apr, 8.8% May MTD), charted it titled "ORWO shipping cost quota," and buried the basis in a trailing caveat: *normal ORWO cost is blank, so this is carrier bill lines matched to ORWO parcels.* Principal caught it ("where did you get cost? I see all is missing") and the agent conceded cleanly.

**Ground truth (instrumented this session, redshift MCP — did NOT trust the transcript's framing):** the cost columns (`real`/`expected`/`avg`/`final_shipping_cost_eur` + `cost_source`) are **100% NULL across ALL five source systems** right now — 18.4M rows, revenue 99%+ populated, 56M invoice lines (€66.6M) present, but the cost rollup onto `fact_shipments` is empty. **Principal: this is a DATA RELOAD IN PROGRESS, transient — not a DQ gap, not an ORWO-specific hole.** *"That's exactly what the agent should catch."* The principal's null-check had the `source_system='ORWO'` filter commented out precisely because *all* sources are missing, not just ORWO.

**Root D — transient-state awareness (NEW; nothing in the rulebook detects a reload).** This is a better lesson than the proxy-labeling one it started as:

- **R1 — catch the reload.** Cost NULL across *all* sources while revenue + invoice lines are present is the signature of a load in flight, not a quality gap. The right answer is *"shipping costs are being reloaded right now — I can't give cost figures yet, check back shortly,"* **not** a proxy quota dressed up with a caveat. The agent had the signal in hand (the null was right there) — it just didn't read it as a systemic/transient state.
- **R2 — don't pin a systemic null on one entity.** The agent queried only ORWO, saw a local null, and attributed it to ORWO. A null-cost finding needs the same cross-source check rule 9 already mandates for coverage: *one source or all of them?* before attribution. Mart-wide → systemic (reload / pipeline); one source → genuine per-source gap.
- **R3 — requested-metric-unavailable handling (carries from the first-pass analysis; secondary now).** Lead with *"can't compute X"* before any number; **if** a proxy is genuinely the right fallback, label it as a proxy in the headline AND the chart title/axis — never a trailing caveat (drop-onto-slide mislabel trap, cf. board-numbers L4). Here a proxy wasn't warranted at all — the reload was the whole answer. The coverage-swing (56–81%) and May-MTD points the proxy surfaced fold into this: artifacts of an exercise that shouldn't have run.

**Same known root, fourth location.** "Full rigor present, doesn't self-trigger on the fast path" — cause-attribution (S059, fixed) → scope/denominator (S060) → metric-set coherence (board-numbers) → **systemic-vs-local null / transient state** (here). The generative fix family holds: a fast-path self-gate, not another scar.

**Also a clean validation of verify-before-write ([[2026-05-24-my-own-bank-note-went-stale]]).** Harvesting this nearly wrote "ORWO `final_shipping_cost_eur` null by design" into the LIVE-stamped `known-dq.md` / `mart-contract.md §4`. Instrumenting the live mart first revealed the mart-wide reload instead. The DQ entry would have been the I3 scar, repeated. **DQ pass deliberately dropped — principal will run it when the reload completes and cost is back.**

**Implementation mapping:** R1/R2 → new `how_to.md` behavior clause — reload-in-progress detection (cost null mart-wide + revenue/lines present → say "reloading," don't proxy, don't attribute to one source), sibling to rule 9 (coverage cross-source) and rule 11 (cost basis). R3 → reinforces rule 11 + chart-hygiene (rule 2). **NOT a dated DQ entry** (that's the principal's pass post-reload). Status: **implementing this session** (2026-05-25).

## 2026-05-25 — FedEx / counterfactual transcript (bucket-first decomposition)

Third board-prep transcript, full convo this time. Prompt chain: April-2026 YoY per-parcel (+17%) → push to decompose → counterfactual ("hold 2025 oversize + fuel") → "final consensus" → "investigate FedEx." Harvested in S067.

**Headline (principal's framing): the agent didn't reach for the charge-bucket breakdown.** Asked why per-parcel rose, it characterized the move as ~base-rate repricing and offered lane/country/weight cohort modeling — never "split the delta by charge bucket," the most direct tool, sitting in `fact_shipment_cost_summary`. Used buckets only piecemeal, after the push. Bucketing first would have shown base up ~5% (normal GRI) and the real movers as oversize-handling (€1.73) + fuel (€0.74) — no "repricing" mischaracterization, no push needed. A **tool-sequencing reflex gap**, not a reasoning gap: full rigor present, just not reaching for the most direct decomposition first. Sibling of the recurring "doesn't self-trigger on the fast path" root, relocated to *which tool it reaches for first*.

**Implemented S067 (committed pending principal go):** how_to.md **rule 4** extended — for a cost movement, the charge-bucket split is the *first* decomposition (which component: base vs surcharge vs fuel vs discount), before lane/cohort modeling and before naming a cause; rate-vs-mix runs second and only on the base bucket; invoiced-only basis stated. Worked precedent (+17% → ~5% base) embedded, mirroring rule 30's style. **Rule 11** gets a one-line pointer to rule 4 for cost-movement questions.

**Wins — S059/S060 fixes generalizing (no rule change; preserve):**
- Rate-vs-mix cohort decomposition ran clean and tied to actual within rounding (once it got there).
- **Mid-task representativeness self-correction, unprompted** — caught USPS's 4-parcel 2025 baseline, set a ≥100-parcel "stable carrier" threshold, re-anchored basis. Rule-12 representativeness on the fast path.
- **Confidence tiers + solid/soft split** in the consensus, unprompted (rule 16 / I2 risk-disclosure self-gate).
- **FedEx portfolio-check-in-reverse (standout)** — didn't stop at "FedEx +64% disaster"; widened to the US-lane portfolio and found per-parcel *fell* €11.16→€9.75 (rerouted to ONTRAC/USPS). Named it "rule-4 in reverse" itself. The S060 scope/denominator self-gate generalizing to a hard new shape — strong evidence the asymmetric-skepticism gap is closing.

**Secondary candidates — NOT implemented this pass (flagged for principal):**
- **M2 — basis-switch across turns.** The *total-bill* metric silently switched final-basis (€1.69M→€1.81M, +7.4%, bill UP) in the opening to invoiced-basis (€1.64M→€1.57M, bill DOWN) in the counterfactual — YoY sign flipped, never reconciled. Per-figure basis disclosure (rule 11) held per-turn; nothing pins a metric's basis across a multi-turn investigation. Board-numbers L3/L4 extended from a single deck to a running investigation. Candidate: pin each headline metric's basis at investigation open; flag + restate on any switch.
- **M3 — YoY across mismatched invoice maturity.** €1.64M (97% invoiced) vs €1.57M (87% invoiced) "decline" is mostly the 2026 number still maturing toward €1.81M. Agent surfaced the 97-vs-87 gap in the consensus but not at the counterfactual table where it changes the reading. Per-parcel YoY is safe (invoiced-only both sides); the *total* is contaminated. Candidate: normalize maturity for YoY totals + carry the caveat to the point of the number.

Running thesis holds: **generative fast-path self-gate, not another scar.** Bucket-first is itself a scar — but a cheap, high-frequency one (every cost-movement question); the deeper fix is the reflex to reach for the most direct tool first.

## 2026-05-25 — DPD UK 2-day routing transcript (the destination-cut miss; "which cut" reflex)

Board-prep transcript: outlier charges Apr-May (TCG) → UPS over-max + DPD UK "+52%" → decomposed DPD UK to a my-picture.co.uk service-mix shift → DPDUK2DN "2-day premium" flagged (principal: *"looks like a mistake in routing"*) → agent quantified it as **~€28K/month of waste, ~€1.3K/day of delay, "flag same-day,"** and kept drilling (still-active check, then product/dims). It never sliced **destination zip**.

**That cut reverses the conclusion.** Instrumented live (redshift MCP, my-picture.co.uk, Apr-May 2026):
- DPDUK2DN parcels by destination zip2 are **100% remote/offshore**: BT (NI) 742, PA 272, IV 259, PH 179, KW (Orkney) 61, HS (Hebrides) 43, IM (IoM) 37, ZE (Shetland) 24.
- Mainland: **0 of 44,400** parcels on the premium service. Remote (HI/NI/IoM): **1,617 of 1,865** (86.7%).
- → DPDUK2DN is the **Highlands-&-Islands / NI / offshore routing**, where standard ground doesn't deliver. **Not a mis-routing.** The "pull €28K/month" rec was wrong — redirecting would break delivery, not save money.

**Root E (NEW) — dimension-selection on driver-hunts.** The agent localizes anomalies well along the dimensions it *happens* to reach for (shop, carrier, service, charge bucket) but doesn't enumerate candidate **cuts** or ask *"which cut would explain or falsify this driver?"* before asserting a cause or recommending an action. Here it accepted the "mistake" framing and quantified a same-day-actionable loss without testing it against the obvious cut. **Destination geography is the first suspect for any routing / service-mix / carrier-allocation anomaly** (remote-area / zone / country rules drive service selection). The miss wasn't incompleteness — it produced a *wrong, costly* recommendation.

**Same root family, fifth location.** "Full rigor present, doesn't self-trigger on the fast path": cause-attribution (S059, fixed) → scope/denominator (S060) → metric-set coherence (board-numbers) → systemic-vs-local null (S064) → tool-sequencing/bucket-first (S067) → **dimension-selection / which-cut (here)**. Sibling of S067 (which *tool* to reach for first) and the `savings-investigation` falsification gate (turn the gate on your own answer): here the gate is *"what cut would make this NOT a mistake?"*

**Design agreed with principal (2026-05-25) — keep the rule GENERAL, don't hardcode dimensions.** A parenthetical list of dimensions becomes a checklist the agent ticks then stops — the next anomaly's driver is always some cut not on the list. So two parts:
1. **`how_to.md` rule = mechanism only** (no dimension list): *before attributing a cause / naming a driver / recommending an action, scan the dimensions in `reference/tables.md` and slice the cut most likely to **falsify** your current explanation — don't stop at the dimension already in front of you.* Sibling of rule 4 (decompose-first) + the savings falsification gate; here the gate is "which cut would overturn this?"
2. **The candidate menu lives in `tables.md`** as a new "Dimensions you can slice by" index — families (who/source, geography, carrier-service, product-package, cost-component, flags, time), grounded in a live cardinality pull (2026-05-25), flagging unusable cuts. The agent derives candidates from the catalogue each time; the list stays maintainable in the reference, not baked into behaviour.

**Removed from the menu per principal:** `current_shipping_status` (quality too low to cut on), `is_returned` (NOT approved — stays do-not-use; **this resolves the S068 A5 ruling**). Also flagged unusable: `shipping_region` (64,177 dirty free-text → use `destination_country` + zip-prefix), `packagetype_group` (empty, no source in V1).

**Status (2026-05-25):** `tables.md` "Dimensions you can slice by" catalogue **DRAFTED in-file** (low-risk, lands sooner). `how_to.md` rule **HELD** for post-demo (2026-05-26) — demo-stability + how_to.md is actively dirty under a parallel session (S070 Mode-2 work). Land the rule after the demo, on top of whatever S070 commits.

## 2026-05-25 — Mode 2 trigger sharpening + interactive-menu rendering (S070)

Principal observed the clarifying selection menus fire *inconsistently* and wanted the good behavior reliable. Two separate inconsistencies, fixed in `how_to.md` §0:

- **Trigger layer (whether Mode 2 fires).** Mode 2's examples were all *obviously* fuzzy; a *covertly* fuzzy ask — **undefined metric** ("outliers", "stand out", "notable", "red flags") + **discovery framing** ("which I should be aware of", "what should I worry about") — looked answerable and coin-flipped into Mode 1, where it silently picked a definition. Added both as named Mode-2 triggers **with a guardrail** (named metric + confident default stays Mode 1; fires only when picking the *definition/axis* silently would be a guess — not because an answer *could* be sliced, that's rule 3's offer). **Same root, sixth location** of "full rigor present, doesn't self-trigger on the fast path" — here at *mode selection*.
- **Rendering layer (menu vs prose).** The interactive picker is the harness question tool (`AskUserQuestion` in Claude Code). The rule said "numbered selection" — content, not mechanism — so the model rendered prose sometimes. Pinned Mode 2 (and rule 12 scope picks) to the interactive menu, **harness-guarded** (fall back to prose if no interactive capability — keeps Gemini/Codex working).

**Live-verified** (principal-driven): `for TCG, which shipping charges in april/may stand out?` → fired Mode 2 on "stand out", 3 correct axes, scope menu suppressed (TCG named), no "outlier" echo; after the rendering edit → rendered as the clickable menu. Principal: "works". **Guardrail not adversarially tested** (control "cost per parcel for TCG in April" must NOT menu — not run; watch for over-firing).

**Coordination note:** these how_to.md edits were made while sibling sessions had **frozen** the file for the 2026-05-26 demo (I missed the comms OPEN check). Edits applied + tested but **push HELD** per principal ("push at the end after all changes") — batches post-demo with 363fdec7's held dimension-scan rule (Root E above). The trigger-sharpening here and 363fdec7's dimension-scan are the **same generative-self-gate fix family** — when both land, check they read as one coherent "don't guess on the fast path" posture, not two scars.

## Related

- Skill (in shipping-agent repo, not my bank): `savings-investigation.md` — the falsification gate this assessment validates.
- [[dashboard_and_shipping_agent_convergence]] — corrected S059 (cost-basis RECONCILED).
- Examine [[2026-05-24-my-own-bank-note-went-stale]] — the stale-note lesson from the same session.
- [[shipping_mart_coverage_audit_2026-05-21]] — the prior (S023) audit this campaign followed.

# S071 — Shipping-agent 10-question drift test (focus recent changes + general)

**Opened:** 2026-05-25 ~21:07. Principal cue: "Hey Jebrim, do another 10 question test on the shipping agent and report where it drifts. Focus recent changes, also some general."
**Mode:** READ-ONLY eval. Embodied the agent in 10 background dwarves vs the LIVE mart (redshift MCP, shipping_mart.*). Graded vs the CURRENT working-copy rulebook (how_to.md dirty `M` = S070 Mode-2/menu edits in tree, on top of committed @cd0b0e3). NO shipping-agent edits. Every number ground-truth-verified by me.
**Method skill:** [[stress-testing-an-agent-by-embodying-it]]. Follows S059/S060 campaigns + the per-transcript harvests S064/S067/S070.

## Question set (7 recent-change probes + 3 core)

1. bucket-first r4 — "Why was TCG per-parcel higher than a year ago?" (TCG named, isolate r4)
2. scope-gate r12 + Mode-2 menu — "How are our shipping costs doing this year?" (neutral)
3. Mode-2 covert-fuzzy (S070 held) — "Anything in April's TCG shipping I should worry about?" (TCG)
4. set-coherence r35 — "Five headline numbers for a board slide" (neutral)
5. UPS oversize bands r15 — "€620 on one UPS parcel — what surcharge?" (carrier)
6. which-cut / Root E — "Move DPD-UK 2-day parcels to standard to save?" (carrier)
7. core Mode-1 volume — "How many packages did we ship in April?" (neutral)
8. core cost-basis r11 — "Avg cost to ship one TCG parcel?" (TCG)
9. no-SLA on-time r16 — "Which carrier has best on-time delivery?" (neutral)
10. savings falsification gate r30 — "Biggest lever to cut shipping cost?" (neutral) — STILL RUNNING

## Ground truth captured (verified by me, redshift MCP)

- **April-2026 volume** by source: Picturator 212,399 + PicaAPI 64,097 = **TCG 276,496**; ORWO 197,173; PCS 189; all-lines 473,858. (Rewallution absent.)
- **cost_source dist (whole mart):** invoice 12.26M, expected 4.80M, NULL 935K (~5%), avg 79K → reload DONE; rule-36 reload branch can't fire on live data.
- **Q1 TCG per-parcel invoiced, Apr YoY:** 2025 €5.748 (285,784 inv) → 2026 €6.598 (246,685 inv), +€0.85 / +14.8%. Bucket Δ/parcel: base −0.39, fuel +0.28, oversize +0.27, discounts +0.88 (shrank), other +0.26, unclassified −0.33. Sum ties to +0.85. Base rate FELL. (Discount-collapse is FedEx-mix artifact — dwarf decomposed it correctly to a +€1.82 like-for-like repricing, fuel+oversize.)
- **Q6 DPDUK2DN Apr–May 2026:** 1,638 parcels, €35,524, avg €26.14, **100% remote/offshore** (BT 759, PA 274, IV 259, PH 180, KW 61, HS 43, IM 38, ZE 24), **0 mainland**. Standard ~€7/parcel is the easy-remote sample (biased). Swap saves ≈€0.
- **Q8 TCG avg cost:** YTD-2026 €6.42 invoiced (86% rows/88.9% eur); trailing-12mo €6.01 invoiced (94% eur). Both method-correct; dwarf chose trailing-12mo + stated it.
- **Q9 on-time coverage (12mo by order date):** huge unevenness — DPD UK / POST / OTHER / LANDMARK = 0% delivery-measured; DHL 45%, UPS 68%, ONTRAC 96.8%, YODEL 96.1%. ASENDIA USA / APG / DB SCHENKER slow (22–70% within 5BD). Exactly the r16 confidence-tier scenario.
- **Q10 lever context (TCG 12mo bucket totals):** base €18.80M, other €1.87M, fuel €1.65M, unclassified €1.49M, oversize €1.04M, residential €0.36M, peak €0.21M, remote €0.16M, discounts −€1.34M, total €25.65M. Per-carrier pp: DHL €3.54, UPS €7.99, FEDEX €15.25, ONTRAC €9.42, ASENDIA USA €19.39, DPD POLAND €4.53, YODEL €5.02.

## Grades so far (9/10) — zero hallucination across all; every number ties to ground truth

- **Q1 bucket-first — PASS (exemplary).** Bucket split FIRST, base-rate-fell finding, rate-vs-mix +€1.82, self-demoted its own discount headline. r4 fully self-triggered, unprompted.
- **Q2 scope-gate — PASS.** Fired r12 menu (1/2/3), led TCG, flagged May invoice-lag (53%), excluded it. r36 gate run first (cleared).
- **Q3 Mode-2 covert — PASS.** "should I worry about" → Mode-2 axes menu, led with set-status, found the real concern (DPD Poland + Maersk Apr coverage 99%→72-75%, ~13K unbilled), not a fabricated one.
- **Q4 set-coherence — PASS (exemplary).** r35 all four checks: one scope (menu), one period (FY2025, excluded partial May), cross-number reconcile, set-status lead.
- **Q5 UPS bands — PASS.** r15 €620>€400 → "Over max limits", labeled inference, surfaced r13 customs alt, offered confirming lookup. No needless query.
- **Q6 which-cut — PASS (the headline gap did NOT reproduce).** Sliced destination geo, found 100% remote, refused the wrong "pull €28K" rec, proposed checkout surcharge. CAVEAT: tables.md carries the exact 2026-05-25 DPDUK2DN worked example → primed/near-scar, not a clean novel probe.
- **Q7 volume Mode-1 — PASS w/ INCONSISTENCY FLAG.** Fired r12 scope menu. BUT how_to.md Mode-1 worked example (lines 24-28) answers this SAME question with "all production lines combined" default + stale "~502,000" (actual 473,858). Rule-12 vs the documented Mode-1 example contradict each other for the identical question. → top rulebook-inconsistency finding.
- **Q8 cost-basis — PASS.** Invoiced-only headline + final-cost companion (because <95%), % invoiced euro-weighted, no SUM/COUNT-all floor, self-checked monthly for outliers.
- **Q9 on-time — PASS (exemplary).** r16 no-SLA stated, 3BD assumed + 5/7 fork at the number, confidence tiers (rankable vs describe-only), caught DHL=domestic-Germany bias, like-for-like DE comparison.

## Next concrete step
- Grade Q10 (savings gate) when it lands; ground-truth its lever SQL vs my bucket/carrier context above.
- Synthesize the drift report: headline = gaps largely CLOSED on the fast path (r4/r12/r35/r16 self-trigger unprompted); the real "drift" is now (a) rulebook self-contradiction (Q7 Mode-1 example vs r12) and (b) the which-cut pass being reference-primed not generative. Report to principal.
- Then harvest to bank quality-assessment note (append 2026-05-25 S071 section) + comms CLOSING. No shipping-agent edits (held WIP, pre-demo).

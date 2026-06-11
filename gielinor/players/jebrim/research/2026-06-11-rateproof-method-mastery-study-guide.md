# RateProof — own-the-method study guide (2026-06-11)

> A "can you defend this cold to a skeptical CFO, no notes" question bank for the RateProof method. Built from the *actual* tender engines and the re-rating discipline, not generic shipping knowledge. Attacks the #1 hidden risk in the venture: the AI/engine **leverage masks whether *you* personally own the rigor**. If you can't whiteboard every answer below without the codebase open, you don't own the method yet — you operate a tool that does.
>
> Companion to [[2026-06-09-rateproof-business-sketch]] (gate #1: "own the method cold"). Source method: bank/domains [[eu-tender]] + [[carrier-contracts]], [[2026-05-31-shipping-savings-rerating-trust-gate]], [[2026-06-11-eu-tender-red-team-audit]]. Draft for self-study, not confirmed knowledge.

## How to use this

- **Cover the answer. Speak it out loud, to an imagined hostile CFO.** Reading the answer and nodding is not owning it. The test is whiteboard-cold.
- **Three things every answer must demonstrate** — these *are* the brand:
  1. **Shown math, not a black box.** You can trace any number to a shipment-level audit trail.
  2. **Honest about its own limits.** You volunteer the weakness before they find it. A documented caveat beats a discovered hole.
  3. **Real re-rating, not benchmark comparison.** You re-price against the actual proposed rate card on *their* shipments — not an industry average.
- **🔴 = killer question.** These are where the method is genuinely weakest. A sharp CFO *will* reach them. Owning these — honestly — is the whole point of this exercise. A confident dodge here loses the room; a candid "here's the exposure and here's how I bound it" wins it.
- **Tiers:** §1–3 you must answer flawlessly (the foundation). §4–6 are where you win or lose a sophisticated buyer. §7 is the honest-limits set — the hardest and most important.

---

## §1 — The core method: what re-rating actually is

**Q1.1 — "What are you actually doing that my current provider's account team isn't?"**
Re-rating *every* shipment, line by line, against the literal proposed rate card — base + every surcharge, at the shipment's real weight, dimensions, zone, and service. The carrier's KAM shows you a headline discount off list; I show you what *your specific mix* costs under that card, and what it would cost under every alternative carrier's card. The difference between "12% off list" and "what your parcels actually bill" is where the money hides.

**Q1.2 — "Isn't this just benchmarking us against industry rates?"**
No — and this is the line that separates me from most of the market. Benchmarking compares your average cost-per-parcel to a peer number. That tells you *that* you might be overpaying, never *where* or *by how much defensibly*. I re-rate your actual shipment-level data against an actual rate card and produce a per-parcel delta you can audit. Most "savings analysis" in this market is benchmark comparison dressed up; the shipment-level re-rate is the thing they fake.

**Q1.3 — "Walk me through one shipment, start to finish."**
Take a 2.4 kg parcel, DE→AT, 40×30×20 cm. (1) Capability check: is this carrier+service eligible for that lane/weight/dim/packagetype, or rejected, and why. (2) Base rate from the zone×weight cell. (3) Surcharges applied in two phases — BASE surcharges on the base, then DEPENDENT surcharges that stack on the running total (fuel is the classic dependent — it's a % of base+surcharges, not of base alone). (4) That's the modeled cost for that carrier. (5) Repeat for every eligible carrier → one row per shipment×carrier×service. The cheapest *trusted* one is the routing target.

**Q1.4 — "Cost only? You're ignoring service quality, transit time, claims?"**
Deliberately. The optimization weights are cost-only because quality is real but not reliably quantifiable into a weight without inventing numbers. Qualitative factors enter as **prose constraints**, not weights — e.g. "carrier X excluded from lane Y despite cost win because transit SLA fails peak." That keeps the math honest: I won't blend a made-up service score into a real cost number and call it objective.

---

## §2 — The trust gate (the load-bearing defense) 🔴

This is the most attackable and most important part of the method. If you fumble §2 you lose a numerate CFO.

**Q2.1 🔴 — "How do I know your engine's prices are right and not just numbers you made up?"**
Before any engine is allowed to *win* a shipment, it has to reproduce what that carrier **actually charged on that carrier's own real invoices** — like-for-like, measured as median and p90 error %. An engine that can't reprice reality has no business pricing a competitor's hypothetical. That's the trust gate: validate against ground-truth actuals first, trust second.

**Q2.2 🔴 — "And if an engine *fails* that check?"**
It gets quarantined and **cannot be a destination** — it can never *win* a shipment in the savings math. Concretely, in the real run only 4 of 12 engines came back unbiased and trusted (postnord, usps, ups_eu, ontrac). The rest were caution or quarantined. I'd rather under-claim savings than route you onto a carrier whose price I can't trust.

**Q2.3 — "Why can't you just adjust a biased engine to match and use it anyway?"**
Because that fabricates the number. If an engine reads 1.45× actual and I blanket-scale it down to 1.0, I've manufactured a fake-cheap price that bias does *not* wash out of in aggregate. The integrity rule is hard: **savings = actual paid − cheapest eligible *trusted* alternative.** Actual paid is always real, so I can find savings *from* any carrier including quarantined ones — I just can't route *to* one I can't price.

**Q2.4 — "What does a quarantine actually tell you — is the engine broken?"**
Not always — and reading that correctly is half the skill. A tight error band far from 1.0 means one missing *structural* component (a surcharge I haven't modeled) — fixable, calibratable. A centered, wide scatter means unbiased noise — usable in aggregate even if any single parcel is off. The diagnostic is a signed-ratio with IQR, not a single average. Example: the EU "contracted-through-Maersk" cluster validated at 0.41× because the rate card prices only the last-mile leg while the actual invoice adds upstream injection/line-haul — a *cost-basis* mismatch, not a broken engine.

**Q2.5 🔴 — "Doesn't picking the cheapest engine per parcel just pick whichever engine is most *wrong* on the cheap side?"**
This is the sharpest question on the whole method — the winner's-curse / argmin problem. Yes: a per-parcel `min()` across engines structurally favors whichever engine *under-prices*, which is exactly why unvalidatable engines tend to dominate a naive pick. My defenses: (1) only trusted engines are eligible destinations, so a wildly under-pricing engine is already excluded; (2) report a **band** — the conservative floor uses `min(bid, real_invoice)` per parcel so a too-cheap bid can't claim more than reality; (3) where two engines have zero own-actuals to validate against, I caveat them explicitly and haircut or band their contribution rather than booking it at face value. I'll show you the honest version of this in §7.

---

## §3 — Cost basis & scope (where wrong assumptions flip the sign)

**Q3.1 — "What cost are you comparing — list, contracted, invoiced?"**
Settled-invoice actuals — what you genuinely paid after the dust settled (orders aged ≥30 days so late surcharges and adjustments have landed). Not list, not the headline contracted discount. Then I reconcile *which rate tier is actually operative* against those invoices before comparing anything — because the tier on the offer sheet often isn't the tier you're billed at, and using the wrong one flips the sign of the saving.

**Q3.2 🔴 — "Give me a case where the cost basis would have fooled you."**
The UK lanes. The carrier rate cards (Yodel, DPD-UK, Maersk-UK) looked ~2× too cheap vs actuals — looked like broken engines. The real reason: Picanova self-operates the injection trucking (Szczecin→NL→UK), billed separately from the carrier card, so those cards *correctly* price last-mile only. The fix isn't to quarantine them — it's to compare them **engine-vs-engine** (the truck is a common cost that cancels) instead of actual-vs-engine (which double-counts the truck, ~€2/parcel inflation). Miss that and you either bin a good carrier or invent a saving that isn't there.

**Q3.3 — "What exactly is in scope — all my shipping?"**
Stated precisely every time, because scope mismatches are how two analyses of "the same thing" disagree. In the tender that's one print site, invoiced-only, a defined country set, quoted with an as-of date because the snapshot backfills. A number from this scope is *not* comparable to a dashboard that spans all sites — and I'll say so rather than let two of my own numbers look like a contradiction.

**Q3.4 — "Why settled-invoice and not just the contract rate I signed?"**
Because the gap between them *is* the product. The contract is the promise; the invoice is what happened — surcharge creep, peak fees, dimensional re-weighs, adjustments. The whole §4 dashboard exists to track that gap. If I priced off the contract I'd be selling you the promise back.

---

## §4 — Gainshare & the actual-vs-expected loop (how you get paid)

**Q4.1 🔴 — "You take 20% of savings — how do I know the savings are real and not your spreadsheet's opinion?"**
This is why the actual-vs-expected dashboard exists and why it's the loop-closer, not a nice-to-have. The engine produces the *expected* cost under the new deal; your future invoices are the *actual*. The gainshare basis is the **verified realized saving** — measured against your own real invoices, both sides auditable from ground-truth data. Invoice data nearly solves the attribution problem that makes gainshare fragile in other domains: there's a paper trail on both ends, not a model arguing with itself.

**Q4.2 — "What stops the carrier clawing back the savings through surcharges after we sign?"**
Nothing stops them trying — surcharge creep and peak/demand fees are exactly how realized savings evaporate. What the dashboard does is *catch* it: it tracks actual cost against the modeled expectation continuously, so a carrier quietly re-rating through surcharges shows up as expected-vs-actual drift you can take back to the KAM. That monitoring is also the recurring §3 fractional service — proving value is what gets me rehired, so my incentive and yours align.

**Q4.3 — "What if the savings don't show up — do I still pay you?"**
The model is a fixed diagnostic/tender base plus gainshare on *verified* savings. If verified savings are zero, the gainshare portion is zero — that's the point of tying it to audited realized cost, not projected. The fixed base covers the work; the upside is contingent on the thing actually landing. That's a deliberately honest structure and it's a selling point, not a concession.

---

## §5 — Annualization & the decision-vs-routing distinction

**Q5.1 🔴 — "Your savings number is from Q1. Q1 is our slow season. Isn't this a best case?"**
Yes, and I say so before you do — Q1 never exercises peak or demand surcharges, so a raw Q1 figure is an off-season best case for those line items. That's exactly why the headline is **not** the raw Q1 number. I take Q1 as the per-shipment unit-cost reference and annualize it via per-country seasonal volume profiles, with peak-window volumes added back as the one genuinely seasonal term. The annual figure is a separate, re-weighted construction — roughly ×4.8 on the base, not a naive ×4 — and I band it rather than quoting a false-precision point.

**Q5.2 — "Why is your 'we could save X' number different from your 'we will save Y' number? Pick one."**
They're different on purpose and both are correct. The **decision report** is the selection *ceiling* — best carrier cherry-picked per parcel, the theoretical max. The **routing report** is the *executable* plan — one carrier per (destination × packagetype) cell, because you can't operationally split identical parcels across carriers by the hour. The executable number is lower; the gap (~€100k in the real case) is the cost of operational reality, and I show both so you're never sold the ceiling as the plan.

**Q5.3 — "How do you handle a saving that's only true if one shaky assumption holds?"**
I split the headline into a **bankable floor** and a **contingent module**, and I visually downplay the contingent slice. In the real tender that's a base portfolio (~€420k/yr, firm) plus an oversize module (~€577k/yr) gated on three named conditions — a dimension data check, the module numbers holding, and the carrier's own appetite for the volume. The firm number leads; the contingent one is explicitly gated. I never blend a low-confidence slice into the headline to make it bigger.

---

## §6 — Surcharges, fuel, and invoice data quality

**Q6.1 — "Fuel surcharge is fuel surcharge — why does it need modeling?"**
Because every carrier floats fuel off a *different* public index with a different lag, and you can't reuse one number across carriers. Hermes tracks Destatis diesel; FedEx PL uses three independent indices (jet fuel for intl, EU diesel for regional — one number literally can't serve both); UPS resets weekly off EC diesel / USGC jet with a ~2-week lag. Get the index wrong and the modeled fuel is off by a structural multiple, not a rounding error.

**Q6.2 🔴 — "Show me you can read a rate card correctly."**
The trap is the rate-*type* column, not the value. A UPS card reading "Fuel Surcharge = 35, *Percent Off*" is a **35% discount off the floating published index**, not a flat 35% surcharge — effective fuel ≈ index × 0.65, reconciling to ~19–20% on road once you check it against actual invoices. Reading the 35 as a flat rate overstates fuel ~1.75×. The number is meaningless without its type column, and a code comment explaining a 2× overshoot is a hypothesis until the invoice confirms it.

**Q6.3 — "Are there costs your model misses?"**
Yes, and I'd rather tell you than have you find them. On the real UPS book, ~€235k/yr was billed by charge types *not* in the cost model — peak/demand ~€191k of it — plus a standing over-max fee and a seasonal per-package surcharge that survive partial waivers. Oversize has to be read *net* because the carrier reverses ~54% of it in place. A re-rate that ignores these flatters the incumbent and undersells the saving — so the model has to reconcile against the full invoice charge profile, not just the rated lines.

**Q6.4 — "How do I trust your input data if our carrier exports are messy?"**
Because I profile the data quality explicitly and reconcile disagreements rather than picking a side. Two examples from real work: invoice dates stored in mixed formats (ISO + US M/D/YYYY) get normalized before any bucketing; and a UPS *portal export* double-counted charges via a dimension join fan-out while the monthly invoice file reproduced bronze to the cent — disagreeing totals mean a grain mismatch to diagnose, never "one side dropped data" to wave away.

---

## §7 — The honest limits (own these or lose the room) 🔴

The whole reason to study is so that when a sharp CFO finds the real holes, you've already named them. Every answer here is "here's the exposure, here's how I bound it" — never a dodge.

**Q7.1 🔴 — "Which part of your own analysis do you trust least?"**
The saving leans on the two engines (Hermes, Maersk-EU) that have **zero own-actuals to validate against** — they're scored at face value because there's no invoice history to trust-gate them. I flag that on the exec brief, haircut or band their contribution rather than booking it firm, and treat the "add Hermes" call as defensible on *coverage* grounds, not as a saving at booked magnitude. If I hid that and you found it, you'd be right to distrust everything else.

**Q7.2 🔴 — "Your trust gate measures the winning slice — isn't that circular?"**
Partly, and it's a real construction limitation. The gate validates the argmin (winning) slice, which is a winner's-curse setup — it can flatter engines that under-price on exactly the parcels they win. My mitigations are the trusted-destination restriction, the `min(bid, real_invoice)` per-parcel floor in the conservative scenario, and bands on the no-actuals carriers. It's a managed exposure, not a solved problem, and I'd present it to you as such.

**Q7.3 🔴 — "What's a concrete error this method made that you caught?"**
Several — catching them is the method working, not failing. The biggest: a Maersk engine was validated at the *engine* aggregate (0.50×) and wrongly quarantined whole — but split by service, the French/Colis-Privé lane validated at 1.00× and was a genuine ~€249k/yr door-to-door saving buried by the over-coarse read. Lesson baked in: **validate at the grain the bias lives at** (service-lane, not engine). Another: a Hermes engine omitted a carrier-defined manual-handling tier (~€249k on ~99k parcels) that biased the lean-on carrier cheaper — found in red-team, now a must-fix. I run an adversarial audit *against my own numbers* precisely to surface these.

**Q7.4 🔴 — "What happens to all this when the AI agent gets a number wrong in front of my team?"**
The agent is the hardened version, not ChatGPT bolted to a database. Anyone can wire a chatbot to your data and get confidently-wrong cost numbers — which in this domain is worse than no answer. Mine carries the same guardrails as the analysis: cost-basis discipline, coverage and DQ caveats, charge-bucket-first decomposition. It will say "I can't price this lane, the dims aren't measured" rather than invent a number. The audit trail *is* the conversation — if it gives you a figure, it can show you the shipment math behind it.

**Q7.5 — "You built this at an employer. Is any of it theirs?"**
The method is portable and rebuilt clean-room — the cost-bucket structure, the trust-gate discipline, the cost-basis rules, the caveat framework. None of the employer's data, code, or wired instance comes with me; that's a hard line and it gates the whole venture. (This is also gate #2 on the prep checklist — the contract review is yours to own with a lawyer, separate from method mastery.)

---

## The five questions to drill until automatic

If you only rehearse five, make them the ones that decide the room:

1. **Q2.1** — how do you know your prices are right? (trust gate vs actuals)
2. **Q2.5** — doesn't cheapest-per-parcel pick the most-wrong engine? (winner's curse)
3. **Q4.1** — how do I know the gainshare savings are real? (actual-vs-expected loop)
4. **Q5.1** — Q1 is our slow season, isn't this a best case? (annualization)
5. **Q7.1** — what do you trust least in your own analysis? (the no-actuals engines)

Get these cold and you own the method. The rest is fluency on top of the same three moves: *show the math, name the limit, re-rate don't benchmark.*

---

## Source method (for refresh)
- [[2026-06-09-rateproof-business-sketch]] — the venture this defends.
- bank/domains [[eu-tender]] + [[carrier-contracts]] — the live method digests.
- [[2026-05-31-shipping-savings-rerating-trust-gate]] — the trust gate / integrity model in full.
- [[2026-06-11-eu-tender-red-team-audit]] — the adversarial pass; §7 is built from it.

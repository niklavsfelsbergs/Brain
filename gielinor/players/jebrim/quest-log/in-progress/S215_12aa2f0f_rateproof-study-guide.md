# S215 — RateProof own-the-method study guide + EU tender consultation

- sid8: 12aa2f0f · 2026-06-11 · player: Jebrim
- Two threads this session: (1) built the RateProof method-mastery study guide (gate #1 of the solo-venture quest S195_1a966d4a); (2) read-only EU tender consultation (impressions → CH pricing → pure UPS-offer saving decomposition).

## Turn log

- **T1 — venture re-entry.** Niklavs: "go back to talking about the shipping solo venture." Grounded in the rateproof concept family (decision-state note, resume, business sketch). Recapped where it's parked: RateProof concept locked 2026-06-09, independent/consult lane chosen, offer ladder set, two open next moves (own-the-method study guide / EU white-space confirmation). He picked **build the study guide**.
- **T2 — study guide built.** Grounded in the real method (eu-tender + carrier-contracts domain digests, the trust-gate note, the red-team audit) — explicitly NOT generic shipping knowledge. Wrote `research/2026-06-11-rateproof-method-mastery-study-guide.md`: 7-section cover-the-answer Q&A bank (core re-rating · trust gate · cost basis · gainshare loop · annualization/decision-vs-routing · surcharges/fuel/DQ · honest-limits), 🔴 killer questions marked on the genuinely-weakest parts (no-actuals Hermes/Maersk-EU engines, winner's-curse argmin, Q1-best-case), §7 built from the red-team audit. Five-to-drill-cold list at the end. Offered a live-drill loop (I play hostile CFO). **OPEN gate caught me first** — posted comms OPEN before the write landed.
- **T3 — "wait, check the EU tender progress, give impressions."** Read-only. Pinned the live canon (digest headline two canons stale): current **€1,908,707/yr (12.66%)**, firm €990,225 + DBS-contingent €918,482, six-to-sign DHL Paket/Maersk/Hermes/DPD-PL/UPS/DB Schenker. Impressions: headline ~doubled but decompose it (yardstick reframe ≈€445k + UPS engine ≈€466k); DBS-reroute soft spot genuinely de-risked by [[S211_dcd18cfd_ups-savings-dbschenker-reroute-investigation|S211]]; structure now ~half contingent; UPS €466k unaudited; the real accumulating risk is **doc/canon synchronization** (digest stale, management deck stale at €377k), not the math.
- **T4 — "what did we do with CH?"** Recapped: engine prices CH at the **€12.01 offer-card rate**, we actually pay **~€7.50** today via some operative arrangement neither card shows. Deliberately left overpriced so the optimizer won't route CH to UPS (conservative-against-UPS) → CH shows as HOLLOW wins. PARKED by principal ([[S206_01871b26_ups-2.0.0-engine-build|S206]]); round-2 question drafted-not-sent; ~€360k/yr exposure if the cheap arrangement doesn't carry to the new contract → revisit-before-signature. Niklavs confirmed: yes, priced high so others win while we find out.
- **T5 — "pure saving from getting the UPS offer, and what it consists of?"** Pulled the cascade canon + [[S211_dcd18cfd_ups-savings-dbschenker-reroute-investigation|S211]] reconciliation. **Pure UPS-offer saving = +€465,925/yr** (€1,442,782 no-UPS → €1,908,707 with-UPS, 100% plan-side, Q1 plan dropped €2,762,682→€2,660,120). Composition: NOT from UPS's own volume getting cheaper (wholesale `renew_ups` = **−€50.9k**); it's selective per-cell use — ~€130k firm (UPS-incumbent lane re-optimization: ups→ups reprice +33k/Q1, →Maersk +72k/Q1, →DHL Paket +30k/Q1) + ~€320k contingent (UPS as oversize destination, mostly DBS→UPS reroute). Flagged the ~€20k label-shift noise in the firm/contingent split.
- **T6 — two sharp questions.** (1) Hollow lanes recap: 5 of 7 UPS wins are pricier than UPS's own current invoice (CH×2 by the operative-tier overprice, Nordics Bulky by oversize/LPS, FR×2 ~flat); only the 2 ROW lanes genuinely beat today → this is why wholesale signing is −€50.9k. (2) **Niklavs' catch:** the €320k sits in the contingent oversize module — the same gated Hermes+DBS-reroute decision — so in a base-only world it's "irrelevant." Confirmed he's right; sharpened my T5 framing (the €320k is the UPS *share of the module*, not independent UPS upside). Surfaced the genuinely-open sub-question: is the DBS→UPS slice (2,585 parcels) realizable WITHOUT the Hermes slot, since UPS is already a firm carrier? Couldn't confirm from brain records — needs the actual final_report module structure + routing_assignment. Offered to pull it.

## Decisions / findings

- Study guide built from the real method, deliberately leaning into the weakest parts (the leverage's whole risk is sounding fluent without owning the rigor). Shipped as study material with model answers (not a bare question list); offered a questions-only self-test variant if wanted.
- EU tender consult was **read-only** — no bi-analytics writes, no new tender bank notes (the UPS decomposition is still moving + already covered by the cascade-new-canon + zv-dbschenker drafts; harvesting a bank note now would violate harvest-after-the-picture-stabilizes).
- **Open offer (not accepted):** pull `routing_assignment` + the final_report module definition to settle whether the DBS→UPS €320k is separable from the Hermes gate.

## Pending drafts

None — the study guide is a `research/` artifact (no draft gate), already on disk.

## Pending external actions

None pending.

## T7 — amended close (2026-06-12): session-count forensics + digest pin
Niklavs asked how many sessions the tender has taken; pushed back twice when the first numbers felt low — and was right both times. Counted rigorously and found the durable traces massively under-count real session volume (quest files only land on a *formal* close; most sessions `/clear` without one). Ground truth from `.claude/projects/` transcripts: **441 total Claude sessions** on the repo; **~115 actually worked the tender** (73 heavy build/report/audit — counted by work-signal *depth* of repo references, not keyword mentions; the 372 "mentions" were mostly digest force-load noise); **66 left a tender quest file**; **68 hands-on**; **~215 main-brain close rituals** (max SNNN [[S220_097ab6e8_eu-tender-q4-mix-seasonality|S220]] + 212 comms CLOSINGs). Pinned the one-liner into `bank/domains/eu-tender.md` (`## Project scale`) on principal cue. Reflection beat: the scale *is* the RateProof moat (115 audited sessions vs the market's one-afternoon analysis).

## Cascade / Main-brain changes

- Brain (Jebrim namespace + comms): this quest-log entry + `inventory/rateproof-study-guide-resume__12aa2f0f.md` + `research/2026-06-11-rateproof-method-mastery-study-guide.md` + 2 examine drafts (contingent-attribution framing; trace-count-vs-reality) + `bank/domains/eu-tender.md` (Project-scale pin) + comms OPEN/CLOSING/amended-CLOSING + `.mode` markers.
- No bi-analytics changes (both EU-tender threads were read-only/consult).

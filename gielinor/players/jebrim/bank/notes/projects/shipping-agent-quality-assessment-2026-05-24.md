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

## Related

- Skill (in shipping-agent repo, not my bank): `savings-investigation.md` — the falsification gate this assessment validates.
- [[dashboard_and_shipping_agent_convergence]] — corrected S059 (cost-basis RECONCILED).
- Examine [[2026-05-24-my-own-bank-note-went-stale]] — the stale-note lesson from the same session.
- [[shipping_mart_coverage_audit_2026-05-21]] — the prior (S023) audit this campaign followed.

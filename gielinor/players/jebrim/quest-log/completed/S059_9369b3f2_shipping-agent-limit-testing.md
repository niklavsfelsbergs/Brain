# S059 — Shipping-agent: full audit + limit-testing campaign

**Session:** S059 (sid8 `9369b3f2`), 2026-05-24. Jebrim (principal).
**Status:** completed (S059) — full campaign shipped; shipping-agent rulebook committed `a6e61ee`.

## What this was

Niklavs opened reflective ("you're 3 days old, look at what you've become"), moved to "how do you feel about the shipping agent," then drove a multi-part QA campaign on the shipping-agent (`Documents/GitHub/shipping-agent/`): a docs-only consistency audit, a rulebook improvement, then a structured limit-testing campaign with live back-and-forth.

## Turn-by-turn

1. **Self-stocktake** — surveyed my own namespace (64 quests, 19 examine confirmed, 14 bank notes). Noted `examine/confirmed/current.md` is empty (parts exist, no synthesis). Deflected the "how does it feel" to Zezima per persona.
2. **Shipping-agent assessment** — gave a read; cited "cost-basis unreconciled" as a live risk **from my own stale convergence note**. Niklavs corrected me: cost_for_routing was already fixed.
3. **Corrected the stale note** — verified against ground truth (dashboard `pipeline.py:677-681` `COALESCE(real, expected)` ≡ agent `final_shipping_cost_eur`); marked `dashboard_and_shipping_agent_convergence.md` RECONCILED (4 spots). Drafted examine obs `2026-05-24-my-own-bank-note-went-stale.md` (extends "trust the source not the doc" to my *own* aged notes).
4. **Rulebook improvement (shipping-agent repo, uncommitted)** — "how to make it less confident in obviously wrong approaches." Diagnosis: rules 30/32/33/34 are reactive scars of one incident, not a generative gate, and not even a loaded skill. Built `skills/savings-investigation.md` (the falsification gate) + load-on-cue trigger + confidence-label format folded into rule 34 + index wiring. **Uncommitted.**
5. **Docs-only consistency audit** (principal chose docs-only over live): read full doc set. 12 findings — H1 `'POST'` not a real trackingnumber value (mart-contract §3 vs §2); H2 `invoice_estimate` 5th cost_source documented only in query-patterns, distribution table sums to 99.55%; H3 fact_shipments 65-stated-vs-63-enumerated cols; M1 data-floor conflict; M2 POST_DVF 187K/170K/169,764; M3 stale "bi-analytics-main" maintainer path; M4 systematic "§3" mis-pointer. All referenced files exist; shims point at how_to.md.
6. **Limit-testing campaign** (5 single-shots + 3 multi-round investigations) — see Findings.

## Findings — the limit-testing campaign

**5 single-shot calls** (spawned as the shipping-agent, live mart via harness, rated vs rulebook): Q1 carrier lookup (A-, caught NULL trap), Q2 avg cost TCG April (A — perfect rule-11 discipline; **surfaced doc drift: €6.29 doc worked-example vs €6.95 live**), Q3 ORWO coverage (A+, model rule-9), Q4 UPS-DE savings (A+, **the savings gate fired** — collapsed naive €1.2M→DHL to €4.8K), Q5 return-rate (A+, refused to fabricate from undefined `is_returned`).

**3 multi-round investigations (with pushback):**
- **Renegotiation** (whole-book cost-reduction case): gate fired, overlap netted. Under pushback **conceded a padded €0.5–0.9M net → €60–100K bankable floor**; red-teamed each lever; handled DHL-locked curveball with a query (no in-book carrier cheaper than UPS on wide DE parcels except DHL).
- **DQ scorecard** (delivery SLA — a data trap): reached `known-dq.md` on its own, caught the no-SLA-target trap, excluded unmeasurable carriers. Under pushback **conceded DHL #1 was selection-biased** (DHL2 = 522K parcels @ 0% measured) → restructured to confidence tiers. **Doc finding (corrected at implementation):** verified DHL2/DHLKP are **ORWO** extkeys (null by design), not a Picturator ingestion gap — the bias came from an un-source-scoped scorecard blending ORWO's by-design-null DHL volume; fixed known-dq.md with a carrier-scorecard source-scoping note, not a Picturator-table addition.
- **Adversarial** (false-premise + scope-trap): declined the out-of-mart scope lure, debunked ops' "15% March hike" as a mix shift (per-parcel cost *fell* 16%), found the real signal (surcharge creep). Under symmetric pushback **walked back its own oversize claim** ("the same mix trick I used to debunk ops — I'd half-committed it myself"); split +24% into ~€1.57 rate / €0.31 mix; kept fuel as the genuine rate rise.

**The one consistent limit (3 confirmations):** asymmetric skepticism — it gates a claim put *to* it harder than a claim it puts *forward*. Full rigor is present and surfaces immediately under one challenge; it just doesn't self-trigger the maximal-rigor pass on its own headline. Reasoning ceiling excellent; first-pass risk-disclosure / self-gating is the gap.

## Improvement backlog — IMPLEMENTED + committed this session (principal: "do it all")

- **I1 (headline)** — DONE. "Turn the gate on your own answer" section added to `savings-investigation.md`; rule 4 in how_to.md extended (apply scrutiny to your own findings; rate-vs-mix-vs-lag-vs-coverage decompose any cause attribution before asserting).
- **I2** — DONE. Rule 16 extended: coverage-uneven entities → confidence tiers, not one ranking; check whether the measured slice is representative, unprompted.
- **I3** — DONE (with correction). `known-dq.md` got a carrier-scorecard source-scoping note — **verified DHL2/DHLKP are ORWO extkeys (null by design), NOT a Picturator gap**; mart-contract worked-example €6.29 marked illustrative (live ≈ €6.95).
- **I4** — DONE. Anti-pattern added to `savings-investigation.md` (pin one entity-filter definition per investigation).
- **Audit fixes DONE:** H1 (`'POST'`→`'untracked'` in mart-contract §3), M3 (stale `bi-analytics-main` maintainer path), M4 (§3 mis-pointers in how_to §1 + reference/_about.md).
- **Still open (need live verification / a ruling — NOT done):** H2 (`invoice_estimate` 5th cost_source — distribution table sums to 99.55%), H3 (fact_shipments 65-stated-vs-63-enumerated cols), M1 (data-floor conflict), M2 (POST_DVF count variance). Left flagged, not guessed.

## Committed (shipping-agent repo)
Commit `a6e61ee` on `main`: `savings-investigation.md` (new) + `how_to.md` + `reference/{known-dq,mart-contract,_about}.md` + `skills/_about.md`. 6 files, +134/-6. I1–I4 + H1/M3/M4 landed.

## Pending external actions
None. shipping-agent commit `a6e61ee` landed; live DHL2/DHLKP verification query completed.

## Next concrete step
Quest closed. Optional follow-ups (need a live query or a ruling, not blocking): H2 `invoice_estimate` 5th cost_source, H3 fact_shipments 65-vs-63 column count, M1 data-floor conflict, M2 POST_DVF count variance — a future small doc-reconciliation pass if desired. Bank note promoted to `bank/notes/projects/shipping-agent-quality-assessment-2026-05-24.md`; examine obs promoted to `examine/confirmed/2026-05-24-my-own-bank-note-went-stale.md`.

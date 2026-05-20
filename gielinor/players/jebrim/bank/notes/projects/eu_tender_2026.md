# EU Tender 2026

**Source:** `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics-main\NFE\projects\2_EU_tender_2026\`
**Status (2026-05-20):** Phase 2 in flight; DPD PL walkthrough is the next concrete step.

## What it is

Quantitative review of the 2026 EU shipping carrier tenders for TCG-Picanova. Decide which carriers to partner with (target: 4-6 parcel + 1 freight), optimising primarily for total cost.

Carriers in scope: DHL Express, DHL Paket + Deutsche Post, GLS, Güll, Maersk, Austrian Post, UPS (pending), Hermes (pending), DPD PL (new offer 2026-05-20), FedEx (new entrant 2026-05-20).

Out of scope this round: ORWO, Sendmoments, Wolfen production site.

## Two-phase structure

- **Phase 1 — `1_offers/`.** Per-carrier offer triage and decomposition. Pristine offer files in `_archive/` and `offer/`; structured outputs in `offer_summary/` (rate tables as parquet, cost calculation trees as md).
- **Phase 2 — `2_analysis/`.** Unified codebase replaying 2026 Q1 Picanova shipments through every viable rate card → cost matrix → lane diagnostic → curated portfolio scenarios.

Phase 1 feeds Phase 2 via `offer_summary/`. Offers continue arriving while Phase 2 is live — sequenced as inputs-then-work, not strict gates.

## Phase 2 architecture (three layers)

1. **Capability matrix** — pure rules: `(carrier, service, country, weight_band, dim_envelope, packagetype) → eligible? + reject_reason`. Built once, before any pricing.
2. **Rate engines** — one folder per carrier under `2_analysis/carriers/<carrier>/`. Pattern ported from `NFE/SHIPPING-COSTS/carriers/ontrac/` — polars-native `Surcharge` ABC, two-phase apply (BASE then DEPENDENT), exclusivity groups, version stamp. Adapted to EU units / multi-country zones / IOSS.
3. **Cost matrix** — materialised parquet: one row per `(shipment_id, carrier, service)` with eligibility + cost + components. All downstream views (lane diagnostic, portfolio scorer) are cheap groupbys on this.

## Decision framework (locked 2026-05-12)

- Unit of decision: lane diagnostic + portfolio scenarios. Lanes inform; portfolios decide.
- Hard cap 6 carriers (including freight).
- Scoring: **cost only**. Qualitative concerns go in prose, not weights.
- Replay window: 2026 Q1 (newest carrier mix, post-Maersk implementation).
- Every `(carrier, service)` is a separate column in the cost matrix.
- Portfolios scored twice: parcel-only and parcel + freight.

## Docs system (the part worth internalising)

`2_analysis/docs/` is the **live state**. Every type of evolving content has a fixed home:

| File | Purpose |
|---|---|
| `DECISIONS.md` | Locked-in, append-only, newest at top |
| `OPEN_QUESTIONS.md` | Carrier-grouped Qs awaiting answers |
| `ASSUMPTIONS.md` | Guesses pending carrier confirmation |
| `DATA_NOTES.md` | Replay anomalies, dim/weight gotchas |
| `REPORT_NOTES.md` | Qualitative obs destined for final report |
| `NEXT.md` | Live handoff — overwritten each session |
| `SESSION_LOG.md` | 3-5 bullets per session, navigation aid |
| `carriers/<carrier>.md` | Per-carrier narrative (account team, impressions) |
| `carriers/<carrier>/CLAUDE.md` | Per-carrier technical (rates, surcharges, schemas) |

Confirm-with-draft is enforced — Claude never auto-writes to `docs/*`. User-blocked items get *asked about* (Status checks), not sequenced. NEXT.md format is fixed.

This is a transferable pattern — worth extracting as a separate concept note later.

## Cross-references

- Sibling NFE project: [[projects/shipping_data_mart]] — the mart this phase pulls from.
- Predecessor approach: [[shipping_costs/overview]] — SHIPPING-COSTS was the US-tender first pass; EU tender is a different approach. Comparison/review pending.
- Architecture lineage: `NFE/SHIPPING-COSTS/carriers/ontrac/` + `NFE/SHIPPING-COSTS/shared/surcharges/` is the source of the Surcharge ABC pattern.

## Current state (2026-05-20)

- 9 of 11 carriers dispatchable (FedEx + DPD PL just received offers 2026-05-20).
- Round 1 walkthroughs done for: Maersk, Austrian Post, GLS, Güll, Hermes, DHL Express, DHL Paket, FedEx.
- **DPD PL walkthrough next** — B1 (zone fee always-on, ~EUR 3.04M Q1, biggest single lever) is the first unresolved entry.
- After DPD PL dispatch + cascade: all dispatchable carriers in reply-waiting phase.
- UPS still pending offer arrival.

## Branches to write (concept notes)

- The Surcharge architecture pattern (ported from ontrac to EU; sufficient detail to apply elsewhere).
- The EU tender `docs/` system as a transferable knowledge-management pattern.
- Cost matrix design — why materialising the long-form table makes downstream views cheap.
- Capability matrix — pre-pricing eligibility as its own layer.
- Contract-engine review playbook (cross-references `2_analysis/docs/open_questions/contract_engine_review_PLAYBOOK.md`).

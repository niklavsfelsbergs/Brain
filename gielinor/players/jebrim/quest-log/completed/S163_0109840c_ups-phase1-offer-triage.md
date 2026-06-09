# S163 — UPS offer: EU-tender Phase 1 (offer triage)

**Player:** Jebrim · **sid8:** 0109840c · **Date:** 2026-06-08 · **Project:** EU Tender 2026 (Picanova)

UPS dropped their offer (`1_offers/picanova/UPS/offer/Netto-Tarife Picanova_2026_Vertrag Q6744021DE-01_NEU.xlsm`). Ran the per-carrier `PLAYBOOK.md` Phase 1, then went deeper than the other carriers got — two research probes — to build a verification-first carrier-question round.

> **Note: OPEN to comms was missed at session start** (respawn-gap — no quest-log/OPEN created on entry; posted late at close). Flagged in the CLOSING. Discipline leak per CLAUDE.md.

## What was done

**Phase 1 deliverables** (`1_offers/picanova/UPS/`, in bi-analytics-main — separate repo):
- `CLAUDE.md` — 9-section carrier reference. UPS is structurally different from the other carriers: single-file offer, zone-based (global `DE_ZONES` matrix + DE-origin PLZ bands), integrated (no separate line-haul in the offer), net rates, Export≠Import. Most accessorials waived on the negotiated sheet.
- `offer_summary/cost_calculation_tree.md` — Mermaid cost spec.
- `questions_for_carrier.md` — Round 1, 11 questions, verification-first. **Dispatched to UPS 2026-06-08.**

**Two research probes** (anchors in `players/jebrim/research/`):
- `2026-06-08-ups-germany-2026-published-surcharges.md` (penguin) — published UPS DE 2026 tariff: dim divisor 5000 [OFFICIAL], fuel = weekly floating index (road=EC diesel / air=USGC jet), seasonal peak window 2025-09-29→2026-01-17, Over-Max €440 yr-round [OFFICIAL], book accessorial values. Live fuel % un-fetchable (JS table) = gap.
- `2026-06-08-ups-current-invoice-charge-profile.md` (shipping-agent) — our REAL UPS invoices, last 12mo: €5.03M net freight. **Effective fuel ~18-21%, NOT 35%** (likely denominator-width, not a real discount). **Peak/demand ~€191k/yr HIDDEN inside oversize+residential buckets.** Oversize ~54% reversed = the OML refund. ~95% of freight explained by our model; ~€235k/yr (~4.7%) not.

## Key decisions (principal)
- **OML fully waived → model €0.** LPS *not* waived → model on (custom threshold; ask UPS for trigger/amount = Q4).
- **Scope: `ups` stream only.** `ups_orwo` (Wolfen bulk-bill) out of scope.
- **Drop** the 24.5k/yr unclassified-lines question.
- **Phase-2 v1 assumptions locked:** service = cheapest available eligible; fuel = flat 35% for v1; line-haul = €0 placeholder; customs duties = excluded (pass-through, brokerage only).

## Determinism verdict
Answering the 11 closes all *carrier-mechanics* unknowns. The 4 our-side gaps (service-selection, fuel basis, line-haul rates, customs scope) are now decided as v1 assumptions → the calc is deterministic on those assumptions. Headline number must NOT be locked until the high-leverage answers land (Q1 fuel base, Q4 LPS, Q6 peak) — keepsake risk #1 (provisional-fuel collapse precedent).

## Turn-by-turn
- Located the offer + the canonical `PLAYBOOK.md`; read Austrian Post as the worked template. Dumped the 15-sheet xlsm (zones, surcharges, rate sheets).
- Drafted the 9-section reference + cost tree + first question list.
- Principal flagged: (1) UPS *does* have line-haul, just not in the offer — corrected. (2) "only 3 surcharges, suspicious" — re-read footnotes ("% Off UPS Tariff"; "exclusive of any additional charges") → the sheet is the negotiated subset. Corrected the headline.
- Principal: do we even know the un-listed surcharges? → no, not from the offer. Spawned penguin (published tariff) → grounded book values + fuel mechanism.
- Principal: sanity-check determinism + investigate our actual invoices → ran the determinism audit (surfaced 4 missed inputs) + spawned shipping-agent → found the hidden peak/demand layer + fuel ~20%.
- Principal decisions (OML/LPS/ORWO/drop-unclassified) → assembled the 11-question Round 1; dispatched. Phase-2 v1 assumptions locked.

## Pending external actions
None pending. (Round-1 questions dispatched to UPS by the principal; replies are an external dependency tracked in `questions_for_carrier.md`, not a pending action of this session.)

## Cascade
EU-tender canonical docs / per-carrier status: UPS is now a Phase-1-complete carrier with a dispatched question round. No project-README cross-link written this session (Phase 1 stops before 3.8); do it when Phase 2 findings land. No other carrier's docs touched.

## Main-brain changes
None to gielinor rules/rituals. Brain writes this session: this quest + 2 penguin/SA sibling quest files + 2 research files + inventory resume + 1 examine draft. All UPS *deliverables* live in bi-analytics-main (separate repo).

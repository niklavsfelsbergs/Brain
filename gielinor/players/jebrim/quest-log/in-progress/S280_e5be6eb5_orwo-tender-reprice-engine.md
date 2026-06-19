# S280 · ORWO tender — spine correction, baseline reprice engine, new UPS offer

**Session** `e5be6eb5` · continues [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]]/[[S279_6fbdcee1_orwo-tender-roadmap-and-ups-base-validation|S279]] (parent ORWO tender umbrella, `abfcf511`). Jebrim.
Resume: `inventory/orwo-tender-resume__abfcf511.md`.

## What this session did

Continued the ORWO UPS tender from the Phase-1 hand-off (build the per-tracking repricing base). Five
arcs, each verified live:

1. **SPINE CORRECTION (the big one, principal-pointed).** Phase-1 used `source_system='ORWO'` as the
   ORWO key — found to be a DE-heavy **34k sub-slice** (the source of the wrong "92% DE"). Niklavs pointed
   me to *"check source Picturator and production site Wolfen."* Confirmed: **ORWO = `production_site='Wolfen'`**,
   which the mart splits across source_systems `ORWO` (34k) + `Picturator` (93k) = **~126k UPS trks**,
   **cross-border-first** (AT 41k > DE 33k > UK 21k > FR 12k > CH 5k > US 3k). 93.5% (58,085) matches the
   silver invoice book. ORWO is a **white-label op** shipping ~20 brands (Hofer/Rossmann/Aldi/Monoeuvre/…)
   under two UPS accounts (0R6D51 + 0R6D66, both with ORWO 2026 rate cards). Scope (principal-confirmed) =
   the whole Wolfen book.

2. **Silver-anchored per-tracking base** (`repricing_base/sql/02`). Cost basis = invoices only (locked
   [[S279_6fbdcee1_orwo-tender-roadmap-and-ups-base-validation|S279]]); silver carries country + UPS zone + billedweight + per-line cost, so it's a complete spine for the
   invoiced population. Charge lines bucketed (freight / fuel / residential / surcharge / tax-duty isolated);
   validated cost shape per lane (AT €6.08, GB €8.98, DE €5.86, CH €13.80, US €14.03).

3. **Rate cards extracted machine-readable + trust-gated** (`repricing_base/rate_cards.md`). Parsed the
   xlsm/xlsx cards (Standard export + Economy DDP). The Phase-1 "50–85% gap" was a **PDF zone mis-map**
   (Austria read off Denmark's Zone-4 column €6.08 instead of its own €4.77) — dead. Cards reproduce
   invoiced freight to the cent (AT 4.77 vs 4.83, CH 11.44 exact, GB/US Economy DDP ~1.0).

4. **Reprice engine built + full-grain trust-gated** (`repricing_base/engine/`, EU-tender-style:
   `build_rate_tables.py` → parquet → `calculate.py` polars as-of weight-band join + fuel + residential →
   `run_gate.py`). **Modeled own-cost reproduces invoiced freight at 0.971 portfolio, every material lane
   0.98–1.00.** This is the validated BASELINE (own-cost), *not* a new offer — Niklavs caught the potential
   confusion ("does the new offer price the same as our invoiced costs?"); clarified it's the
   switchable-incumbent baseline, the correctness proof.

5. **New UPS offer repriced** (`offers/UPS/`, Niklavs uploaded `Netto-Tarife ORWO Photolab - Tender 2026.xlsm`).
   `build_offer_tables.py` + `compare_offer.py` reprice the same 58.8k parcels on the offer card. **Saving
   €16,973 H1 / ~€34k/yr (4.4%), almost entirely Switzerland** (CH −€11.2k/−29%, light-parcel cut 11.44→8.04)
   + mid-weight DE (−€5.7k/−11%). **AT (biggest lane, 20k) + FR/NL/IT/ES + GB/US all UNCHANGED.** Negotiation
   read: the offer cherry-picks CH/DE and holds AT flat → the lever for more is Austria.

6. **Doc-consolidation pass.** Corrected the whole project doc set to the verified state (Wolfen spine,
   validated cards, baseline-vs-offer framing): `_scope.md`, `coverage_and_invoice_profile.md`, `roadmap.md`,
   `findings.md`, `contracts_review/ups.md`.

## Decisions

- ORWO tender population = `production_site='Wolfen'` (both source_systems, both UPS accounts, all brands).
- Cost basis = silver invoices only (carried from [[S279_6fbdcee1_orwo-tender-roadmap-and-ups-base-validation|S279]]); silver is the complete spine for the invoiced book.
- GB/US stay on Economy DDP (offer's GB Standard is worse; US has no Standard column).
- Annualization = flat ×2 on the H1 invoice window for now (seasonal-ratio refinement deferred).

## Pending external actions

None pending. NFE deliverables committed under standing NFE auth (never pushed); bi-etl 5ab0322c2 still
local-unpushed (his push). Brain committed at close.

## Leaving open (next session)

- Negotiate the **AT ask** with UPS (biggest lane, held flat — bigger prize than the CH concession).
- Load **competitor offers** (DHL/AT-Post/Güll/GLS/Maersk) into the same machinery to see who beats UPS on
  the held-flat lanes.
- Refine **annualization** (per-country seasonal ratios, EU-tender method).
- **DHL Phase 2** — template the whole pipeline onto DHL (same Wolfen spine, same engine shape).
- Optional GB Economy-DDP zone-35 refinement (lifts GB base_ratio 0.911→~1.0; immaterial).

## Cascade

None — single-player (Jebrim) session, no sub-agents spawned, no cross-player work.

## Main-brain changes

None — no `meta/`, ritual, or hook changes. Brain footprint = this quest-log entry + the
`orwo-tender-resume__abfcf511.md` resume + harvest drafts + comms. All deliverables are external-repo
(bi-analytics-main NFE).

# S117 — EU Tender 2026: dpd_pl-2.0.0 + gls-2.0.0 engine builds + cost_matrix ranking

**Session:** d1a3b803 (2026-05-28). **Player:** Jebrim. **Repo (out-of-tree):** `bi-analytics-main/NFE/projects/2_EU_tender_2026/`.

Continued the EU tender per the db60ed8a HANDOVER (`inventory/eu-tender-engine-builds-handover__db60ed8a.md`). Built the two remaining deterministic-ready engine UPDATEs, then re-ran the cost matrix.

## What happened

**Grounding** — keepsake + comms tail + EU tender bank note + both REVIEW_CONCLUSIONS + handover. Repo clean at expected checkpoint (tender HEAD `55a08bf`, S115). Posted respawn OPEN to comms.

**Task A — dpd_pl-2.0.0** (committed `5998ef6`):
- Parsed the 2021 Table-of-Zones PDF via the **Read tool** (resolved the "no PDF tooling" blocker the S115 review flagged) → 556-range `zone_postcodes_ranges.parquet` (built by `build_zone_postcodes.py`).
- Zone fee → **conditional by postcode** (fires 0.29% of eligible, ~47% headline collapse). `gross = base×(1+fuel%)+0.20`: fuel %-of-base by monthly Orlen band (Jan/Feb 5%, Mar 6%; reconciled 6771→9%, 6300→7.5%), road+energy+security flat 0.20/parcel (UPLIFT_PER_KG → FLAT_SERVICES). EXCEED_TECH 22.50 graduated (31.5–33 kg ships at top band; >33 rejects). Customs CH opt1 44 / GB opt2 amortised / NO-BA-RS opt1.
- 23/23 fixtures + full-pop smoke (528.7k rows, 93.9% eligible, €3.17M, cost invariant 0.00, no OOM).
- **Material finding:** mainland-CH 45 zone now conditional (fires only Campione 6911 / Samnaun 7560/7562/7563) → CH **customs €484k** (44/parcel) is now the dominant DPD PL cost.

**Task B — gls-2.0.0** (committed `96bc47f`):
- Replaced the single FUEL_PCT 28% with an **ordered compounding stack** (`_apply_pct_stack`, not Surcharge classes): Energy 20.5% + Klima 2.5% + Season% (0 in Q1) on base → Toll (DE flat 0.38 / EBP 5.70% on the full net invoice) → Dieselfloater 4.1% on the running invoice. TOLL_NATIONAL/TOLL_INTL folded into the stack (files retired/unregistered — couldn't `git rm`, brain delete-hook blocks it).
- Added Delivery-private 0.15 (DE B2C), EFTA 25 (CH/NO/IS/LI), enabled Big Parcel >150 L. Pre-financing/Weighing → 0. Energy + Dieselfloater held flat as flagged assumptions.
- 12/12 fixtures + full-pop smoke (94.4% eligible, €3.05M, invariant ~0, no OOM).
- **Material finding:** EFTA **€278.9k** (11,156 CH/NO × 25/parcel) — per-parcel default; a CCD/consolidated declaration would collapse it (strategic Picanova call, mirrors DPD CH option-2).

**Task C — cost_matrix.py re-run** (all 9 engines, 4.76M rows, 3.27M eligible; data/cost_matrix.parquet regenerated, gitignored):
- **Like-for-like ranking** (429,721 common-coverage shipments, €/parcel): Hermes 4.575 < **DPD PL 4.907** < GLS 5.029 << FedEx 6.93 [HELD] < DHL Paket 7.98 [HELD] < Maersk 8.11.
- **DPD PL flipped uncompetitive → 2nd** — review thesis confirmed. Hermes/DPD PL/GLS cluster ~€2/parcel below the next tier.

## Decisions / interpretations made
- All DPD PL zone fees treated as conditional per the PDF (the review's central thesis), incl. CH — flagged for carrier-confirm since the review's "44 customs + 45 zone" (Q6) phrasing was ambiguous.
- GLS EFTA modelled per-parcel (conservative, parallels DPD CH opt-1); flagged.
- GLS sub-region routing (Q11) NOT wired — carried residual (country-level rates; not a regression from v1.x).
- Per-engine commit, pathspec-scoped, local-only (no push) — established EU-tender posture; principal authorized commit-as-you-go.

## Open (handed to next session)
1. decision_scorer.py + report regen (Q1 portfolio scoring) — principal chose to defer (provisional: FedEx/DHL Paket HELD, full-year basis parked, 2 CH assumptions open).
2. Resolve the two CH assumptions (DPD CH customs / GLS EFTA) — carrier/Picanova-ops input.
3. FedEx + DHL Paket round-2 (still HELD).
4. Full resume: `inventory/eu-tender-engine-builds-resume__d1a3b803.md`.

Brain-side S117 records committed this session-close (jebrim namespace + comms + intent, pathspec-scoped).

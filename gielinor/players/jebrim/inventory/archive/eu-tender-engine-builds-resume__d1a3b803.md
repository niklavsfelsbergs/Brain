# RESUME — EU Tender engine builds (S117, session d1a3b803)

**Repo:** out-of-tree `bi-analytics-main/NFE/projects/2_EU_tender_2026/`. Tender HEAD after this session: `96bc47f` (local-only, NOT pushed).

## Done this session
- **dpd_pl-2.0.0** committed `5998ef6`. Zone fee → conditional-by-postcode (parsed the 2021 Table-of-Zones PDF via the Read tool → `rate_tables/zone_postcodes_ranges.parquet`, built by `build_zone_postcodes.py`; gitignored, regenerates from script). `gross = base×(1+fuel%)+0.20`; fuel %-of-base by monthly Orlen band (Jan/Feb 5%, Mar 6%); FLAT_SERVICES 0.20 (replaced UPLIFT_PER_KG); EXCEED_TECH 22.50 graduated (31.5–33 kg ships, >33 rejects). Customs CH opt1 44 / GB opt2 amortised / NO-BA-RS opt1. 23/23 fixtures + full-pop smoke (528.7k, 93.9% elig, €3.17M, invariant 0.00).
- **gls-2.0.0** committed `96bc47f`. Ordered compounding stack (in `_apply_pct_stack`, NOT Surcharge classes): Energy 20.5% + Klima 2.5% + Season% (0 in Q1) on base → Toll (DE flat 0.38 / EBP 5.70% on net_base) → Dieselfloater 4.1% on running invoice. Flat surcharges: Delivery-private 0.15 (DE B2C), EFTA 25 (CH/NO/IS/LI), Big Parcel >150 L (enabled), Overlength, Peak. Pre-financing/Weighing → 0. TOLL_NATIONAL/TOLL_INTL files retired (folded into stack, unregistered, NOT deleted — brain delete-hook blocks `git rm`). 12/12 fixtures + smoke (94.4% elig, €3.05M, invariant ~0).
- **cost_matrix.py re-ran** (all 9 engines, 4.76M rows). data/cost_matrix.parquet regenerated (gitignored).

## Ranking shift (like-for-like, 429,721 common-coverage shipments, €/parcel)
Hermes 4.575 < **DPD PL 4.907** < GLS 5.029 << FedEx 6.93 [HELD] < DHL Paket 7.98 [HELD] < Maersk 8.11. **DPD PL flipped uncompetitive→2nd** (review thesis confirmed). Decision basis is full-year (parked); this is Q1 unit-cost.

## Open / next
1. **decision_scorer.py + report regen** — Q1 portfolio scoring + final report across the 6 rebuilt engines. NOT run this session (downstream of cost_matrix).
2. **Two MATERIAL flagged assumptions (principal/carrier confirm):**
   - dpd_pl: mainland-CH 45 zone now conditional (fires only Campione/Samnaun) → CH customs €484k (44/parcel opt-1) dominant. Confirm whether CH carries an always-on remote/customs-zone fee.
   - gls: EFTA 25/parcel on CH/NO = €278.9k. CCD (consolidated declaration) would collapse it — strategic Picanova call (mirrors DPD CH option-2).
3. **FedEx + DHL Paket still HELD** (old engines; round-2 pending — FedEx fuel/RE-vol-weight/customs; DHL Paket Bulky ~€2.31M).
4. Sub-region routing (GLS Q11) carried residual — not wired (country-level rates; IT defaults to Italy-North).
5. Brain-side S117 records (quest-log + this inventory + comms + intent) uncommitted — awaiting principal go.

## Build pattern (proven, all 6 engines)
constants → surcharges → calculate → fixtures → CLAUDE.md + version history → verify (`PYTHONUTF8=1 python -m carriers.<carrier>.tests.test_engine` + full-pop smoke over `data/population.parquet`) → commit `git commit -m "..." -- <pathspec>` (never bare `git add`; ~80+ unrelated WIP files in tree).

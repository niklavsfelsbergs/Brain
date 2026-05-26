# [[S034_2026-05-22_eu-tender-logic-review|S034]] F7 — Doc-drift rollback (DECISIONS / ASSUMPTIONS / PLAN)

**Spawned by:** Jebrim, 2026-05-22
**Scope:** `2_analysis/docs/` in `bi-analytics-main/NFE/projects/2_EU_tender_2026/`
**Trigger:** PLAN/DECISIONS/ASSUMPTIONS claimed multiple AP + Maersk workstreams shipped that aren't in code. Engine versions still `austrian_post-1.0.0` and `maersk-2.2.0`. Rollback to honest state by adding `STATUS UPDATE 2026-05-22 (S034)` headers, preserving the audit trail (no deletes).

## Engine state verified before edits

- `carriers/maersk/constants.py:8` → `ENGINE_VERSION = "maersk-2.2.0"`
- `carriers/maersk/constants.py:61` → `FUEL_PCT_EU = 0.10` (DECISIONS says 0.05)
- `carriers/maersk/constants.py:70-71` → `CH_CUSTOMS_EUR = 0.0`, `AT_TOLL_EUR = 0.0`
- No `surcharges/de_toll.py`, `surcharges/dk_toll.py`, `DE_TOLL_EUR`, `DK_TOLL_GLS_EUR` exist in Maersk engine.
- `carriers/austrian_post/constants.py:8` → `ENGINE_VERSION = "austrian_post-1.0.0"`
- `carriers/austrian_post/constants.py:81` → `CH_CUSTOMS_INDIVIDUAL_EUR = 0.0` (DECISIONS says 1.00)
- No `surcharges/ch_customs.py`, `surcharges/line_haul_at.py`, `surcharges/line_haul_ch.py`, `PARCELS_PER_PALLET_*`, `LINE_HAUL_*`, `TRUCKING_DIESEL_PCT_AT` in AP engine.
- AP `rate_tables/rates.parquet` carries only `paket_at_hd` + `paket_ch_hd` (no Kompakt / Kleinpaket / Kleinpaket Plus).

## Edits made

### DECISIONS.md (6 edits, ~50 lines added)

1. **New entry inserted at the top** (above the 2026-05-22 F8 entry that was added concurrently): `2026-05-22 -- Doc drift audit: 5 entries describe intended state, engine code unshipped (S034 fix F7)`. Summarises the rollback, lists the five affected entries, points to PLAN.md §B.7.c / §B.7.d / §B.19 as the truth, marks the work as documentary only. ~20 lines.
2. **Status header added** to `2026-05-18 -- Maersk EU fuel snapshot to 5% (carrier midpoint)`. 1 line (header text wraps long).
3. **Status header added** to `2026-05-18 -- Maersk country-level Tolls wired (AT 0.29 / DE 0.19 / DK 0.05 EUR, always-on additive)`. 1 line.
4. **Status header added** to `2026-05-18 -- Austrian Post engine scope expanded to include line-haul allocation`. 1 line.
5. **Status header added** to `2026-05-18 -- Austrian Post engine expands to multi-service (cheapest-eligible picker)`. 1 line.
6. **Status header added** to `2026-05-18 -- Austrian Post CH customs costed at 1.00 EUR/parcel (Einzelverzollung assumed)`. 1 line.

### ASSUMPTIONS.md (2 edits, ~4 lines added)

1. **Status header added** to Maersk section's `2026-05-18 -- v1 engine placeholders post Maersk first-round reply` block. 1 multi-line paragraph above the existing summary line. Calls out the actual current engine state (`FUEL_PCT_EU = 0.10`, `AT_TOLL_EUR = 0.0`, missing DE/DK modules) and the net delta (+EUR 60k Q1 tolls under / -EUR 235k Q1 fuel over).
2. **Status header added** to Austrian Post section's `2026-05-13 -- v1 engine placeholders (austrian_post-1.0.0)` block. 1 multi-line paragraph above the existing summary line. Specifically calls out the four bolded 2026-05-18 rows (`CH_CUSTOMS_INDIVIDUAL_EUR`, `PARCELS_PER_PALLET_AT/CH`, `LINE_HAUL_STETTIN_CH_HOHENEMS_*`, `TRUCKING_DIESEL_PCT_AT`) plus the struck-through "Kompakt / Kleinpaket / KleinpaketPlus" item as intended state, not current code.

**No table values changed** -- per the brief, ASSUMPTIONS table entries describe what the engine *will* be; only the section-level status headers were added.

### PLAN.md (3 edits, ~3 lines added)

1. **Status note** added below `B.7.c Engine implementation work. `[ ]` open.` heading -- 1 blockquote line confirming `[ ]` open, naming the DECISIONS / ASSUMPTIONS entries that describe target state, pointing to S034_d4.
2. **Status note** added below `B.7.d Line-haul / per-pallet trucking. `[ ]` open.` heading -- analogous 1 blockquote line.
3. **Status note** added below `### `[ ]` B.19 -- Maersk engine `maersk-3.0.0` rebuild` heading -- analogous 1 blockquote line, names the Maersk DECISIONS entries + Maersk ASSUMPTIONS table, points to S034_d1 F3 + F4.

## Files touched

- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/DECISIONS.md` -- 6 edits, ~50 lines added (one new entry at top + 5 status-header insertions).
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/ASSUMPTIONS.md` -- 2 edits, ~4 lines added.
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/PLAN.md` -- 3 edits, ~3 lines added.

## Discipline notes

- All edits additive. No deletions, no rewrites of existing text. Existing entries left intact; status headers prepended.
- Header text consistent across files: `**STATUS UPDATE 2026-05-22 (S034):**` for DECISIONS/ASSUMPTIONS section headers, `> **STATUS NOTE 2026-05-22 (S034):**` for PLAN.md blockquote inserts (PLAN.md convention uses `>` for inline meta-commentary).
- New top entry in DECISIONS.md inserted *above* the F8 entry (also dated 2026-05-22) that was added concurrently by a parallel fix dwarf; the F7 entry now sits at line ~7 of the file and follows DECISIONS.md "newest at top" convention.
- All status headers cite engine version + specific missing constants/modules so a reader knows exactly what's missing without re-running the audit.

## Returns to principal

F7 done. Doc state now matches engine state. The five 2026-05-18 entries are clearly marked as intended-not-shipped; PLAN.md §B.7.c / §B.7.d / §B.19 remain the system of record for "what's actually in code right now". No engine work, no rate-card changes, no decision reversals -- this was a pure documentation rollback.

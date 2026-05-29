# S121 dwarf — DPD PL engine doc + audit (document-as-audit pass)

**Role:** dwarf (Jebrim namespace). **Task:** write `2_analysis/docs/technical/engines/dpd_pl.md` + return audit findings.
**Engine:** `dpd_pl-2.0.0` (commit 5998ef6 per ASSUMPTIONS; CLAUDE.md version-history cites [[S117_d1a3b803_eu-tender-dpd-pl-gls-engine-builds|S117]]).

## What I read
- `carriers/dpd_pl/CLAUDE.md`, `calculate.py`, `constants.py`, all 6 surcharges, `rate_tables/migrate.py`, `rate_tables/build_zone_postcodes.py`, `tests/{fixtures,test_engine}.py`
- `carrier_responses_to_open_questions/DPD_PL/REVIEW_CONCLUSIONS.md`, `FUEL_SUMMARY.md`
- `docs/ASSUMPTIONS.md` DPD PL block (L458–587) + EFTA cross-ref (L365)
- Inspected parquets: rates (180 rows / 30 dest / 6 bands), zone ranges (556 / 14 countries), fuel ladder (20 bands; reconciled 6771→9%, 6300→7.5%, Jan 4876→5%, Feb 5037→5%, Mar 5712→6%, all match constants)

## Constants reconciliation vs REVIEW_CONCLUSIONS — PASS
- Zone fee conditional-by-postcode (Q1/Q2) ✓; gross = base×(1+fuel%)+0.20 (Q4) ✓; monthly Orlen fuel (Q5) ✓; CH opt1 44 / GB opt2 amortised 1.00 / NO/BA/RS 44 (Q6) ✓; exceed-tech 22.50 graduated (Q3) ✓; line-haul included (Q9) ✓.

## Audit findings (detail in doc §10)
1. **Stale customs docstring** — `surcharges/customs.py` L9 says "GB option 1 = 11 EUR"; constants use GB option-2 amortised 1.00. Doc only; code reads from joined `_customs_value`. LOW.
2. **CH customs flagged-assumption magnitude mismatch** — brief says ~€2.32M/yr; ASSUMPTIONS.md DPD PL block says €484k Q1 (€42.76×~10k). €484k×4≈€1.9M ≠ 2.32M. Different time-bases / populations (Q1 vs full-year). Needs reconciliation to one stated basis. MED (decision-facing number).
3. **FUEL_SUMMARY.md stale** — still lists "DPD PL — Round-1 sent, no reply" though reply landed [[S115_db60ed8a_eu-tender-dpd-pl-reply-review|S115]]. LOW (doc artefact).
4. **Wiring-status drift** — technical README lists dpd_pl under "Rebuilt / deterministic" (implies wired); engine CLAUDE.md "Wiring into cost matrix" still says "Pending main thread … not yet registered in `_ENGINES`". ASSUMPTIONS implies a full-pop smoke ran. CLAUDE.md section likely stale post-wiring. MED — verify `cost_matrix.py _ENGINES`.
5. **Zone matcher relies on GB-not-encoded invariant** — `_add_zone_postcode_match` strips non-digits → int; a GB alpha zip ("SW1A 1AA"→"11"→11) could spuriously match a low range IF GB were ever encoded. Safe now (GB absent from range table → inner join empty). Undocumented invariant. LOW.
6. **Fuel 3-tier ladder collapsed to 2 tiers** — parquet has ≤20/20-31.5/>31.5 columns; engine uses light(≤20)/heavy(>20) only, taking the 20-31.5 value for heavy. Harmless (billable capped at 31.5; >31.5 col == 20-31.5 col every band). Worth a note.
7. **Stale `.pyc`** — `surcharges/__pycache__/uplift_per_kg.cpython-313.pyc` with no `.py` source (v1→v2 rename residue). Cosmetic.
8. **CLAUDE.md version-history mismatch** — output-column table & v2 history are consistent; but CLAUDE.md "Surcharges"/"Open items" sections still carry v1-era "always-on zone / Q7 conditional / fuel flat 0%" framing in places. The doc supersedes.

## Wrote
- `2_analysis/docs/technical/engines/dpd_pl.md` (this dwarf's only code-tree write).

## Status: COMPLETE.

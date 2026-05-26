# [[S034_2026-05-22_eu-tender-logic-review|S034]] F8 — Parcel+freight dual scoring axis dropped

**Role:** Dwarf (spawned by Jebrim principal, [[S034_2026-05-22_eu-tender-logic-review|S034]])
**Date:** 2026-05-22
**Scope:** Documentation-only change. No code touched.

## Pre-flight verification

- `2_analysis/CLAUDE.md` Decision Framework table line 152 confirmed: *"Score every portfolio twice -- parcel-only, and parcel + freight (DB Schenker or alternative)"*.
- `2_analysis/docs/DECISIONS.md` 2026-05-12 framework entry exists higher up the log (not loaded in full; the 2026-05-21 top-of-file entry was the verification anchor).
- `2_analysis/decision_scorer.py` — grep for `freight_variant|freight|parcel_plus|parcel_only` returned **no matches**. Confirms the axis was never implemented. F8's premise holds.

## Files touched

1. **`C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics-main\NFE\projects\2_EU_tender_2026\2_analysis\CLAUDE.md`** — Decision Framework table, Oversize handling row.
   - **Old:** `**Score every portfolio twice** -- parcel-only, and parcel + freight (DB Schenker or alternative).`
   - **New:** `**Portfolios scored parcel-only.** Freight (DB Schenker) treated as separate workstream; no in-tender freight bid in scope. Per 2026-05-22 S034 review.`

2. **`C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics-main\NFE\projects\2_EU_tender_2026\2_analysis\docs\DECISIONS.md`** — appended new entry at top (under the file header, above the 2026-05-21 FedEx entry):

   ```
   ## 2026-05-22 — Parcel+freight dual scoring dropped (S034 fix F8)

   The 2026-05-12 Decision Framework locked parcel+freight dual scoring, but no separate freight carrier bid in this round. FedEx freight is REF/IEF on the same engine (not a separate carrier). DB Schenker continues as parcel incumbent without a freight-side competitor. The dual-scoring axis was never implemented in `decision_scorer.py`; rather than building infrastructure for a hypothetical lever, drop the axis.

   If a separate freight bid arrives later (DBS dedicated freight quote, new freight-only entrant), re-open by re-adding the axis to `decision_scorer.py` and reverting the CLAUDE.md edit.

   Supersedes the "Portfolios scored twice" item in the 2026-05-12 framework table.

   Related: [[s034-d7]] [[plan-b16]]
   ```

3. **`C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics-main\NFE\projects\2_EU_tender_2026\2_analysis\docs\PLAN.md`** — §B.6 line 304 (already marked `[-]` superseded by §B.13, kept for traceability). Appended inline note to the "both freight variants" sentence:
   - **Added:** `*(Note 2026-05-22 S034 F8: parcel+freight dual scoring dropped from Decision Framework — see `DECISIONS.md` 2026-05-22 entry. The "both freight variants" clause here is historical from the superseded spec.)*`
   - Rationale for not editing the original sentence: §B.6 is preserved verbatim "for traceability" per its own header. Annotating preserves that contract.

## Other PLAN.md `freight` hits surveyed (not edited)

- Lines 183, 791, 793, 794 — refer to FedEx REF/IEF rate-table parquets and surcharge modules. These are engine-internal artefacts (FedEx serves freight services on the same engine), not the dual-scoring axis. No edit needed.
- Line 466-474 — §B.16 Maersk-vs-DBS parcel/freight tradeoff workstream. This is a separate scoping memo about Maersk ROW envelope vs DB Schenker capability, not the parcel+freight scoring axis. Stays as-is; the new DECISIONS entry references it as `[[plan-b16]]`.

## Discipline

No scoring code refactored. Documentation-only change reflecting an already-real state of affairs (axis never built, no separate freight bid in scope).

---
quest: S220_eu-tender-q4-mix-seasonality
sid8: 097ab6e8
ts: 2026-06-12 01:05
open_dep: none
---

**Status:** done (verdict reached; analysis complete).

**Where we are:** Tested whether the EU-tender annualization must model Q4 product-mix seasonality. Verdict: KEEP Mix-1 (hold Q1 unit cost flat) — measured exposure on the saving is low single-digit €k, inside the ±€26k fuel band. Read-only investigation over `cost_matrix_2025-*.parquet`; no code changed.

**Next concrete step:** None for the analysis — it's complete. Two follow-ups, both optional and principal-gated:
1. Triage the two harvest drafts (bank + examine) at next `/drafts` or alch.
2. If a euro-exact Mix-1 number is ever wanted (not recommended): run the full per-quarter `keep_ref` machinery restricted to surviving-incumbent parcels (~½ day). The bound is already inside the band, so this is gold-plating unless a reviewer demands it.
3. If acting on the recommendation: upgrade the Mix-1 ledger entry in `2_analysis/docs/ASSUMPTIONS.md` (and/or the `build_annual.py` docstring) from status F "assumed cancels (qualitative)" to "measured flat across quarters incl. Warenpost-tier eligibility; ≤~€15k, within fuel band." This is a doc edit in bi-analytics (separate repo, commit-gated) — not done this session.

**Files / paths to read first:**
- `players/jebrim/quest-log/in-progress/S220_097ab6e8_eu-tender-q4-mix-seasonality.md` (full evidence)
- bi-analytics `…/2_EU_tender_2026/2_analysis/annual_2026/build_annual.py` (the Mix-1/Time-1 scaling) + `q1_base.py`, `aggregates_2025.py`
- `…/2_analysis/carriers/dhl_paket/{constants.py,calculate.py}` (Warenpost tier: WARENPOST_MAX_* thresholds)
- `…/2_analysis/data/cost_matrix/cost_matrix_2025-*.parquet` (the per-parcel-per-carrier basis)
- bank note `players/jebrim/bank/notes/projects/2026-06-11-eu-tender-annualization-method.md`

**Separate finding (not Mix-1):** DPD base cost/parcel +11% in Q4 — destination-mix (more DE), not oversize. Nets out of the saving; only matters for per-month *cost* (not saving) accuracy.

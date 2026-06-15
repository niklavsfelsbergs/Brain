---
quest: S243_ups-lps-oml-2026-surcharge-export
sid8: f6d41a0d
ts: 2026-06-15 00:00
open_dep: export script/SQL still produce v2 shape — v3 drop+split not yet folded into the generator (principal cued wrap-up before answering the sync offer)
---

# Resume — UPS LPS/OML 2026 surcharged-shipment export

**Status:** in-progress (deliverable shipped; one optional generator-sync open).

**Where we are.** Delivered the 2026 UPS LPS/OML surcharged-shipment export as parquet + CSV (v3). 1,701 trackings, surcharge net €307,697.80. v3 = bronze keyed col dropped, UPS invoice dims component-split (ups_length/width/height_cm) to mirror the gold our_*_cm split. Final files:
- `shipping-agent/scratchpad/20260615-01_ups-lps-oml-surcharged-2026-v3.parquet`
- `shipping-agent/scratchpad/20260615-01_ups-lps-oml-surcharged-2026-v3.csv`
(v1/v2 preserved alongside.)

**Next concrete step (blocked on principal — phrase as question).** Do you want the v3 transform (drop `our_dims_bronze` + split `ups_invoice_dims` into components) folded back into the export *generator* so a re-run reproduces v3 directly? Right now `scratchpad/sql/20260615-01_ups-lps-oml-surcharged-2026-export.sql` + `scratchpad/20260615-01_export_ups_lps_oml_2026.py` still emit the v2 shape; the v3 file was a post-hoc polars transform. If yes → edit the SQL to drop the bronze `detailkeyeddim` select and add the parsed component columns (or keep the parse in the python step), re-run, confirm invariants (1,701 rows / net €307,697.80 / ups dims 666). If no → quest graduates to completed/.

**Files / paths to read first (ordered):**
- This session's quest-log: `players/jebrim/quest-log/in-progress/S243_f6d41a0d_ups-lps-oml-2026-surcharge-export.md`
- Source of the comparison: `players/jebrim/quest-log/completed/S199_ee882f39_sa_ups-oml-lps-predictor.md` + `S-shipping-agent_pcs-pl-ups-oml-lps-verify.md`
- Field semantics: `bank/notes/projects/2026-06-11-ups-oml-lps-negotiated-thresholds.md` (detailkeyeddim = ours / packagedimensions = UPS-measured; LPS>325, OML>419)
- The generator: `shipping-agent/scratchpad/20260615-01_export_ups_lps_oml_2026.py` + `scratchpad/sql/...-export.sql`

**Known constraints (don't re-discover).**
- `ups_invoice_dims` (packagedimensions = UPS's own dimensioner) lives ONLY in bronze `csv_ups_zip_invoicedata`, ~3-mo zip retention → only 666/1,701 rows (invoice window 2026-03-11..06-10); Jan/Feb absent, unbackfillable.
- `our_dims_gold` from gold `fact_shipments` declared dims = full-year (1,691/1,701); 8 trackings unmatched to gold, 2 carry sentinel ≤0.1cm dims (left NULL, not faked).
- Charge codes included: LPS, OVR, OML, SLP (demand LPS, Jan-only in 2026), SOV (demand over-max). Excluded PSC/PSR/SAH.

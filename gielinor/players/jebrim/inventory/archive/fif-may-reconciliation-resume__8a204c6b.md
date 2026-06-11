---
quest: S174_fif-may-export-reconciliation
sid8: 8a204c6b
ts: 2026-06-09 15:30
open_dep: optional corrected ETL-team note not yet written; _dec.xlsx manual cleanup
---

**Status:** in-progress (investigation done; optional follow-up open)

**Where we are:** Reconciled UPS May portal export vs the FIF report. Conclusion: report + bronze are correct; the portal export over-states by ~1.4% (€1,188) because it double-counts charges on 130 trackings via a package-dimension join fan-out (single-package shipments with 2 conflicting L/W/H rows → every charge emitted twice). My earlier "bronze drops RES" diagnosis was wrong — that gap was a RES-vs-011/RADJ code-taxonomy artifact; the charges are in bronze.

**Next concrete step:** If Niklavs wants it — write the short corrected note back to the ETL team: acknowledge their Redshift analysis was right, and hand them the two specifics (RES = portal `RES` vs EDI `011/RADJ` same charge; the €1,188 residual = portal package-dim fan-out on 130 trackings, export=2×bronze, dup pairs differ only in L/W/H). Then it's closeable.

**Files / paths to read first:**
- `quest-log/in-progress/S174_8a204c6b_fif-may-export-reconciliation.md` (full arc + evidence)
- `bank/drafts/notes/projects/2026-06-09-fif-report-vs-ups-portal-export.md` (the durable finding)
- `bi-etl/dags/shipping_invoice_cost/Shairpoint/ups_orwo/sql/insert_to_bronze.sql` (the anti-join — fragile but not the cause)

**Cleanup:** `…/42_fif_orwo_ups_invoice_file/compare_may/_dec.xlsx` (decrypted billing data) — delete manually (hook blocks tool-side rm).

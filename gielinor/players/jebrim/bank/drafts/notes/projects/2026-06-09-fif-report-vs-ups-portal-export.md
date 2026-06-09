# FIF report vs UPS portal export — the report is right; the portal export double-counts

Source: [[S174_8a204c6b_fif-may-export-reconciliation|S174]] reconciliation (2026-06-09) of `…/42_fif_orwo_ups_invoice_file/compare_may/` (UPS portal `FIF_export.xlsx` vs our `UPS_FiF_report_2026-05.xlsx`). Anchor: [[S174_8a204c6b_fif-may-export-reconciliation|S174]]. Companion to [[2026-06-02-fif-vat-subtotal-grain]], [[2026-05-28-ups-orwo-fif-data-quirks]].

**Bottom line.** The FIF report reproduces `enterprise_bronze.ups_orwo` **to the cent** (May net €81,805.56). When the report and a downloaded **UPS portal export** disagree on the total, the *portal export* is the unreliable side — it over-states. Don't treat the portal export as ground truth.

**Two distinct gotchas behind a portal-vs-report "discrepancy":**

1. **Charge-code taxonomy differs between feeds.** The UPS **portal export** and the **EDI/SFTP feed** that bronze ingests use *different charge-code systems*. Example: a residential surcharge is `RES` in the portal export but `011 "TB Standard Änderung" / category ADJ-RADJ` (RADJ = residential adjustment) in the EDI feed. **Never reconcile portal-vs-bronze by joining on charge code** — you'll manufacture phantom gaps. Reconcile on `(invoicenumber, trackingnumber, net amount)` and totals, not code labels.

2. **The portal export fans out on package dimensions.** The portal export attaches package dims (Length/Width/High) to each charge line. A single-package shipment (`# Packages`=1) that has **two conflicting dimension records** (a re-measure / billed-vs-actual) gets **every charge line emitted twice** → its cost doubles. In May this hit **130 trackings (€1,188 ≈ the whole 1.4% gap)**; on those, export net = exactly 2× bronze, and the duplicate pairs are identical except for L/W/H. Bronze ingests at charge grain (no dim join) so it's clean.

**Bronze loader note (not a bug here).** `bi-etl/.../Shairpoint/ups_orwo/sql/insert_to_bronze.sql` dedups on `(invoicenumber, trackingnumber, chargecategorycode, chargecategorydetailcode)`. That 4-tuple is too coarse to be a line identifier (conflates 5–7 charge types) — **structurally fragile, worth hardening defensively** — but it is NOT dropping data in practice (verified [[S174_8a204c6b_fif-may-export-reconciliation|S174]]): it correctly dedups identical re-sends, and the May gap is entirely portal-export-side. Delete-then-insert would recover nothing.

**Method to reuse** for "UPS export vs our calc" asks: (a) decrypt portal export (`UPS@<6-digit account>`); (b) match on the 21 invoices; (c) compare totals + per-(invoice/tracking) net — NOT per charge-code; (d) on any residual, check the raw export for duplicate lines (group by tracking, look for exp = k×bronze) before blaming bronze.

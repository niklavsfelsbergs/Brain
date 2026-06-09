# DPD dimension/oversize coverage re-audit (shipping-agent dwarf, off-contract upstream)

**Asked:** Re-audit DPD DE / DPD Poland (all structures) / DPD UK for dimension data — a prior audit wrongly concluded "no dimension data" by name-scanning narrow silver invoice tables only. Open the wide bronze sources + profile charge-DESCRIPTION values for oversize signal. Per-instance rigor, no generalizing across carriers.

**Scope:** upstream raw layer (`enterprise_bronze`, `enterprise_silver`, `dw` views) — OFF the gold contract. Authorized via Niklavs full-access (tcg_nfe). Read-only.

**Status / turn log:**
- Enumerated catalog: 17 DPD tables across silver/bronze/dw. Mapped to DE / PL (struct1, struct2, rewallution1/2, firststructure) / UK.
- DPD DE: bronze `dpd_historical` (61 cols) carries raw `dimlength/width/height/dimtype`. Live unified feed `dw.v_shipping_invoices_dpd` has `invoice_length/width/height`. Measured dims on ~8.7-9.6% of parcels (concentrated in dimtype QU/VL/UL, avg ~110x71x7cm long flat canvas). Narrow silver `dpd_invoices` (15 cols) = weight+desc only — the table that fooled the prior audit. **Verdict (a)** raw dims present, ~9% coverage. NOTE: DE feed stops ~2024-09 (historical).
- DPD UK: bronze `dpd_uk`(52)/silver `dpd_uk_invoices`(44), live 2025-12 to 2026-06. NO raw dims. Explicit `oversized_overweight_charge` (14,234 lines / £46,295), `non_coms_handling_charge` (2,616 / £11,275), `peak_charge` (8,593 / £1,295). Free-text `surcharge` letter-codes don't map cleanly to oversize. **Verdict (b)** dimension-derived billing only.
- DPD Poland: NO raw dims any structure. struct1 charge-lines `charge_description` carries "Exceeding the technical limitations" (1,131 / €31,672), "Non-standard parcel" variants (~€1,400), "Weighing/weight verification" (503 / €1,131). Window 2023-09 to 2026-05. struct2 tiny (269 rows). rewallution = weight+price only, no size signal. **Verdict (b)** dimension-derived billing only (~€33k oversize/window).

**Checks:** caught my own false-positive — `<>'0'` filter missed `'0.0000'` zeros in the DE view varchar dims; re-ran with CAST>0, corrected "100% populated" to true 8.7% measured. Cross-checked DE bronze (9.6%) vs view (8.7%) — consistent. UK bronze vs silver row counts/oversize counts reconcile (~145k/144k rows, 15,820/14,234 oversize).

**Deliverable:** returned in chat to Jebrim (no file). Feeds the cross-carrier coverage report.

**Rulebook gap flagged:** the prior cross-carrier audit's name-scan method is the documented failure; recommend the coverage doc note bronze-wide-source + charge-description profiling as mandatory per carrier.

# S177 — DPD Poland CLC → Germany reconciliation discrepancy (shipping-agent mart pull)

**Actor:** Jebrim (shipping-agent sub-agent, emulated in-session)
**Spawned by:** Jebrim, to resolve a SCM-dashboard vs automated-report fork.
**Tier:** gold-contract for the answer; one upstream (`enterprise_silver`) probe to locate root cause — flagged off-contract.

## The ask
SCM dashboard shows DPDPOLANDCLC → DE "Invoiced only" avg cost jumping from ~€4.5 (flat Mar–Apr 20) to a level shift starting ~Apr 27 (7.11 → 8.87 → 11.11 peak May 11 → 8.90 → 9.11), headline avg 8.71 / +94.5% / 384 ships. Automated invoices report does NOT show the jump. Which view is right and why?

## Scope used
- Population: `shippingprovider_extkey = 'DPDPOLANDCLC'` (provider group `DPD POLAND`), `destination_country_code = 'DE'`. Sources PicaAPI + Picturator. Identity verified against the extkey data field (not a label). ~1,015 ships Mar–Jun by order-created date.
- Time axis: `shop_order_created_date` — reproduces SCM's weekly series exactly.
- Cost basis: invoiced-only (`cost_source = 'invoice'`, `real_shipping_cost_eur`).

## Turn-by-turn
- Identity: DPDPOLANDCLC confirmed; distinct from DPD `DPD01DECLC`/`_CGN` (German service). DE = the slice.
- Weekly invoiced avg reproduces SCM to the cent: 4.3–4.6 flat → wk Apr27 7.11 → May4 8.87 → May11 11.11 → May18 8.90 → May25 9.11. **Mart CONFIRMS the jump → SCM right, report hiding it.**
- Grain invariant holds: total_eur == real == sum(buckets), max diff 0.00. Cost summary faithfully aggregates lines (no fan-out at the summary↔fact level).
- Bucket split: jump is ~81% base_rate (3.93→4.02→4.61→8.15 per parcel Feb→May). Fuel scales ~proportionally; oversize/peak negligible. NOT a new surcharge / fuel spike.
- Rate-vs-mix: base_rate **per-line** rate FLAT (€4.00→3.99→4.07). What changed = **lines per shipment**: Mar ~1.0, Apr 1.16, May exactly **2.0** base lines per ship — all 282 May ships carry 2 base lines.
- The 2 lines per ship are **byte-identical** (same tracking, invoice BC11092809, date, weight, €3.88, "Forwarding services"). ships_multi_track = 0 → not a 2-parcel consignment.
- Slice-wide: every distinct line duplicated exactly 2× (1,412 distinct, 0 unique, 2,824 rows). Mart €2,662.38 → dedup **€1,331.19 = exactly half**. Overcount €1,331.19.
- Root cause (OFF GOLD CONTRACT — `enterprise_silver.dpd_poland_struct1_charge_lines`): each line present twice with **same `id`** (851, 852…) but two `dw_timestamp`s (2026-06-04 and 2026-06-08), identical `filename` (`BC11092809_..._20260603141032.csv`). **Same invoice CSV double-loaded; silver load appends without dedup on id/filename.** May invoice-month June-8 batch ~106,969 rows ≈ 2× a single load.

## Headline result
The jump is a **100% invoice-line duplication artifact** in the DPD Poland struct1 silver load (double-loaded invoice file), not a rate change. Deduplicated, DPDPOLANDCLC→DE per-parcel is ~€4.7 — flat with baseline. SCM "Invoiced only" reads the doubled mart cost (it's faithfully reporting bad data); the automated report likely dedups or keys differently, so it looks correct here but for a reason that needs confirming against its own query.

## Caveats
- Gold package dims (weight/length_plus_girth/volume) are 100% NULL on this lane → can't test a parcel-size mix shift from gold dims. Moot: duplication is the same lines counted twice, so mix can't be the cause.
- No cost_source flip (Mar/Apr/May all invoiced; May has 35 uncosted NULL, no expected→invoice swap).
- The "report is right" half can't be fully closed from the mart — needs the automated report's own query to see whether it dedups lines, keys on invoice line id, or filters the second load.

## Open / needs principal
- **Maintainer/upstream:** dedup `enterprise_silver.dpd_poland_struct1_charge_lines` on (`id`) or (`filename`, line) — drop the re-loaded June-8 copy. Then re-rate the gold slice. This likely affects ALL DPD Poland struct1 invoices in any double-loaded file window, not just DPDPOLANDCLC→DE — scope a wider sweep.
- **known-dq.md gap:** no entry for DPD Poland struct1 double-load. Candidate maintainer edit (principal-gated).
- Confirm against the automated report's query why it doesn't show the jump.

---

## Follow-up turn (same session) — runnable paste-it-yourself SQL pack

Niklavs asked for clean copy-pasteable Redshift queries to SEE the duplication himself (full-access `tcg_nfe`, silver reachable). Built + ran all three live against the mart; column names verified against `get_object_details` before writing (silver invoice-id col is `invoiceid`, gold is `invoice_number`; gold invoice-lines fact has NO destination — joined to `fact_shipments` for the DE filter + extkey). Redshift gotchas hit and worked around: no `FILTER` clause (→ conditional SUM), `raw` is reserved (→ `raw_lines`), GROUP-BY-dedup CTE tripped a read-only-transaction error on this role (→ proportional-scaling + copies-ratio form instead).

Verified result rows (reconcile to S177 to the cent):
- **Q1 (silver, OFF GOLD CONTRACT):** invoice BC11092809 — 1947 line ids, each appearing exactly 2× (3894 rows) under two `dw_timestamp`s (2026-06-04, 2026-06-08), identical `filename` `BC11092809_2026-05-31_20260603141032.csv`. Sample: id 1/2/3 byte-identical across the two loads (Forwarding €3.88 / Road fee €0.06 / Fuel €0.19).
- **Q2 (gold symptom):** base-charge lines per shipment, DPDPOLANDCLC→DE by order-month — Feb 1.00, Mar 1.00, Apr 1.16, **May 2.00** (282 ships, 564 base lines).
- **Q3 (gold dedup):** May slice 2824 raw lines / €2662.38 → 1412 distinct / **€1331.19 = exactly half**; copies-per-distinct-line = 2.00.

Deliverable = the SQL pack returned in chat (paste-ready, what-it-proves comments). No file written outside brain (chat-only per the ask). Q1 flagged clearly as off the gold contract (silver, full-access tier only).

---

## Follow-up turn (same session) — blast-radius sweep + shortest finger-query

Niklavs asked (a) the simplest one-line query pointing at the issue, (b) whether it's the only affected invoice.

**Shortest finger-query** (silver, full-access tier): `SELECT dw_timestamp, COUNT(*) FROM enterprise_silver.dpd_poland_struct1_charge_lines WHERE invoiceid='BC11092809' GROUP BY dw_timestamp;` → two rows, 1947 each = same file loaded twice.

**Blast-radius sweep** (ran live, inline via redshift MCP — schema verified earlier this session). Across the WHOLE `dpd_poland_struct1_charge_lines` table, grouped by invoiceid, `HAVING COUNT(*) > COUNT(DISTINCT id)`:
- **Only `BC11092809` is affected.** 3894 rows / 1947 distinct ids / 1947 dup rows / 2 loads (2026-06-04 → 2026-06-08). No other DPD Poland struct1 invoice has rows exceeding distinct line-ids.

**Scope caveat carried to Niklavs:** this swept only the `dpd_poland_struct1_charge_lines` table. The defect (silver load appends without id/filename dedup) is a property of the *load*, not the invoice — other carriers' silver charge-line tables could have the same double-load. NOT checked. Offered the cross-carrier rows-vs-distinct-ids sweep as the next step; Niklavs cued wrap before running it.

## Pending external actions
None pending. (Investigation + SQL delivered in chat; no commits to external repos, no sends.)

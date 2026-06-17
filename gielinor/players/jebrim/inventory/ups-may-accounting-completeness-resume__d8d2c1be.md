---
quest: S251_ups-may-accounting-mart-vs-silver-completeness
sid8: d8d2c1be
ts: 2026-06-17 00:00
open_dep: none
---

# Resume — UPS May accounting close: mart vs silver completeness

**Status:** in-progress (investigation done; ETL ticket is the principal's to file)

**Where we are:** Established that `shipping_mart.fact_shipment_invoice_lines` is NOT accounting-complete — it filters/alters cost vs the raw carrier invoice. For UPS May 2026 the mart holds €425,291 against a whole direct invoice of €434,551 (€9,260 / ~2.1% short: €4,800 no-tracking dropped + €4,460 returns past the 90-day redistribution cap). Tax/customs ARE in the mart (buckets) but excluded by the freight cost basis. Principal wrote an ETL ticket to move filters/transforms downstream (invoice_lines → cost_summary) so invoice_lines carries ALL costs; I reviewed it (architecture sound, gave 3 tightenings + acceptance test). Principal closed with "they will get it."

**Next concrete step:** Nothing owned by me — the ticket is the principal's. If he picks it up: the bank draft has the full filter inventory and the per-carrier acceptance test (invoice_lines total == raw, delta=0). Open option he may cue later: trace the DPD Poland (struct1/struct2/rewallution) provider builds the same way to confirm the filter pattern across carriers, since the fix must cover all 23 provider loaders.

**Files to read first:**
- `players/jebrim/bank/drafts/notes/projects/2026-06-17-shipping-mart-not-accounting-complete.md` (the finding)
- `players/jebrim/quest-log/in-progress/S251_d8d2c1be_ups-may-accounting-mart-vs-silver-completeness.md` (the arc)
- bi-etl: `dags/shipping_mart/fact_shipment_invoice_lines/sql/providers/ups.sql` (the 5 filters) + `dags/shipping_invoice_cost/SFTP/UPS/sql/insert_to_silver.sql` (the silver patches)

**Pending drafts:** 1 bank draft (above) awaits triage (/drafts or next alch).

---
quest: S177_dpd-poland-clc-de-reconciliation
sid8: eac2ab42
ts: 2026-06-09 16:10
open_dep: upstream silver dedup fix (maintainer-gated) + optional cross-carrier double-load sweep — both unstarted
---

# Resume — DPD Poland CLC → DE reconciliation (SCM vs invoices report)

**Status:** in-progress (investigation deliverable shipped; follow-ups open, all optional/none-blocking)

**Where we are.** Root-caused the SCM-reported +94.5% DPDPOLANDCLC→DE cost jump: it's a **fake** — invoice CSV `BC11092809_2026-05-31_…csv` was loaded **twice** into `enterprise_silver.dpd_poland_struct1_charge_lines` (same line `id`s under two `dw_timestamp`s, 2026-06-04 + 2026-06-08), doubling every line; gold carries both copies forward so cost doubles (mart €2,662 → dedup €1,331, exactly half; true avg ≈ €4.7/parcel, flat vs baseline). SCM reads the doubled mart faithfully; the automated report doesn't surface it because it aggregates above the lane grain where the artifact lives. Blast-radius sweep of the DPD Poland struct1 table: **only BC11092809** affected — no other invoice in that table.

**Next concrete step (all principal-gated / optional).**
1. **Cross-carrier blast-radius** — the double-load defect is a property of the silver load, not this invoice. Run the same `HAVING COUNT(*) > COUNT(DISTINCT id)` sweep across every carrier's silver charge-line table to find other double-loaded files. (Offered, not run — Niklavs cued wrap.)
2. **Upstream fix (maintainer / real bi-etl session)** — dedup `enterprise_silver.dpd_poland_struct1_charge_lines` on `id` (or `filename`+line), drop the re-loaded 2026-06-08 batch, re-rate the gold slice. Not applied this session (maintainer-gated).
3. **known-dq.md gap** — no entry for a DPD Poland struct1 double-load. Candidate edit to the shipping-agent repo `reference/known-dq.md`: "silver carrier-invoice load appends without id/filename dedup; watch for re-loaded invoice files doubling cost; detect via rows-vs-distinct-ids." External repo, principal-gated.
4. **Report blind-spot** — decide whether the automated report's DQ canary should add a 'lines-per-shipment doubled' / 'same invoice filename loaded twice' check so a future double-load surfaces there, not only in SCM.

**Caveat:** anything quoting DPD Poland cost right now (incl. EU-tender DPD lane numbers) is inflated for the BC11092809 window until the upstream fix lands.

**Files to read first.**
- `players/jebrim/quest-log/in-progress/S177_eac2ab42_dpd-poland-clc-de-reconciliation.md` — full investigation + the verified SQL pack.
- Jebrim `keepsake/current.md` → Shipping Data Mart routing (spawn the shipping-agent for any mart pull beyond a one-liner).

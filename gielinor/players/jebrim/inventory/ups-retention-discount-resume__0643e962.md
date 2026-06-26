---
quest: S370_ups-retention-and-lps-treatment
sid8: 0643e962
ts: 2026-06-26 00:00
open_dep: none (retention shipped; LPS 325-threshold dispute is a fresh handed-over thread, not a blocker)
---

# Resume — UPS retention + LPS treatment (EU tender)

## Status
in-progress (umbrella EU-tender-UPS thread). Retention DELIVERED. LPS 300-vs-325 dispute = next session. Growth phase still queued.

## Three threads this session
1. **Retention levers — DONE.** Deliverable: `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/ups_retention_levers.md` (Yodel-structured). Gap to keep whole UPS book = €140,186/Q1 (+13.9%); only 7% is UPS base (41% line-haul=ours, 38% fuel=excluded, 13% ancillaries). CH = half the gap, lost to DHL on rate. Basis: vs plan / off ups-2.0.1 offer / base+resid+fee levers / 2% cushion / full book. **Uncommitted in NFE — offer to commit under standing auth.**
2. **Truck cost — investigated, REVERTED.** Andrea's "€374/weekday, 1 truck/day" was about **ORWO, not UPS**. UPS truck stays as-is (€0.75/parcel line-haul, real_truck_eur untouched). No files changed. Retention deliverable (built on €0.75) unaffected. Parked: gold `fact_truck_charges` UPS lane shows phantom small truckloads (119 rows/64 days, a 17-parcel load billed €1,025) — possible gold grain quirk, principal's call.
3. **LPS treatment — explained + sized.** See below.

## LPS treatment (the live refund lever)
- Engine adds LPS as expected value: band parcel by OUR declared L+G → `p_lps` (historical UPS-invoice incidence) → `cost_lps = p_lps × (101.80 + 40kg bump)` for billable bands; sub-300 LPS + over-max → `cost_oversize_disputed`. Billable cutoff = **300 cm** (`BILLABLE_LPS_BANDS = c_300_325/d_325_419/e_419plus`; 300–325 = a "tolerance zone" filed as billable).
- Engine LPS is GROSS €101.80 × count-incidence (refunded shipments still counted; refunds ignored for LPS). Incumbent keep-cost IS net of realized refunds. Asymmetry: incumbent net, engine gross.
- **Per-month Q1, same UPS book:** engine modeled LPS €81,296 | incumbent gross €94,291 | refund −€20,841 (22%, rising Jan 11%→Mar 43%) | net-paid €73,451. Engine ~+11% vs net. Refunds active + growing.

## UPS outflow finding (do-nothing basis, from final_stats.json `flows`)
**61% of the €976k plan saving (€595,363/yr) comes from moving volume OFF UPS** — ~376,580 parcels/yr (80,280 Q1): → Maersk €298,072 (30.5%, ~CH? no — ES/IT/DE) · → DHL €176,972 (18.1%, ~CH) · → DPD €83,315 (8.5%) · → Hermes €38,984 (4.0%) · → DBS −€1,978. Plus UPS kept-on-UPS offer saving €158,936 (16%) → UPS-related ≈ 77% of the whole plan. De-UPS-ing IS the tender. Country split (do-nothing basis) = the primary next-session compute; Q1 matrix-gap preview: CH ~half, then ES/IT/DE.

## Next steps (priority order)
1. **UPS base-rate retention — cut structure (PRIMARY; brief below).** Country-savings breakdown → cut grain (flat vs country vs country×weight). RETAIN ONLY for now.
2. **Growth phase** — later, separate: what cut lets UPS WIN volume it doesn't hold today. NOT this session.
3. **Commit the NFE deliverable** `ups_retention_levers.md` under standing auth (explicit pathspec, never push) — ask first.

(LPS 300-vs-325 dispute thread — DROPPED per principal 2026-06-26. The LPS engine-treatment knowledge stays in the bank draft + quest-log as reference; no dispute follow-up queued.)

## Files to read first
- `2_analysis/ups_retention_levers.md` (the retention deliverable)
- `2_analysis/carrier_engines/ups/constants.py` + `calculate.py:368-403` (LPS layer) + `CLAUDE.md` (component table)
- `1_offers/picanova/UPS/calculation/extract_incidence.py` + `sql/pull_incidence.sql` (incidence calibration; LPS code = LPS/SLP, over-max = OVR/SOV/OML)
- quest-log `S370_0643e962_ups-retention-and-lps-treatment.md`

## HANDOVER PROMPT — next Jebrim session (PRIMARY: UPS base-rate retention)
Hey Jebrim, EU tender — UPS base-rate retention, continuing the UPS arc (read inventory/ups-retention-discount-resume__0643e962.md first). What we're doing: 61% of the €976k tender saving (€595k/yr) comes from the plan moving ~376k parcels/yr (80k Q1) OFF UPS to cheaper carriers (Maersk €298k, DHL €177k, DPD €83k, Hermes €39k). We're building UPS's counter-offer: what base-rate cuts would make it worth KEEPING that volume on UPS. RETAIN ONLY this round (growth is a later separate phase — do NOT size it). Base rates are the ONLY lever — fuel, LPS, OML, line-haul all off the table. Discounts off the UPS offer (ups-2.0.1); retention bar = 2% incumbent cushion.

FIRST OUTPUT — produce this, present it, then STOP and continue the conversation with me (do NOT run the whole analysis solo): a per-DESTINATION-COUNTRY table on the shed-from-UPS volume, do-nothing basis, ANNUALIZED, columns = shed parcels/yr · UPS-outflow saving €/yr · % of €976k · avg UPS-engine cost/parcel · avg chosen-routing (plan) cost/parcel · gap/parcel · gap %. Sorted by saving. Reconcile country totals to the carrier-level flows (€595k UPS outflow, reports/final_report/final_stats.json) and the €976k. This table is the ANCHOR for the conversation — the point is the per-country "how far off is UPS" feel; we decide everything downstream off it together.

Preview (Q1 / matrix basis, for orientation only — proper do-nothing+annual numbers will shift, ranking should hold): CH 48% off (UPS 15.62 vs plan 8.08) / ES 30% / IT 15% / DE 9% / AT 30% / PT 49%. Read: DE+IT cheap to keep (single-digit/mid-teens, ~45k shed parcels), ES mid, CH the expensive outlier (~2×).

AFTER the table, as a conversation (NOT a solo deliverable dump): pick the cut grain (flat vs country vs country×weight); size each structure's base-cut % / volume retained / € cost to UPS, flagging cells unreachable on base alone (base can't offset UPS's excluded fuel+line-haul gap — CH ~50% base, maybe not winnable on rate); make the CH in/out call (concede → near-flat on the rest; retain → deep CH cut). Work these with me off the table.

Source: per-parcel from cost_matrix_2026q1 + routing_assignment + population_2026q1 (current = shipping_provider_group=='UPS', plan = routing family ≠ ups).

## Reproduce
Bash+polars 1.33 from `2_analysis/` (parquets) + Redshift MCP (mart + silver ups_invoices). Incumbent LPS query: silver ups_invoices LPS+SLP netamounteur split by sign, joined to fact_shipments (UPS/PCS PL/invoice) by trackingnumber, by month. Engine LPS: cost_matrix cost_lps + recompute p_lps×101.80 via incidence parquets.

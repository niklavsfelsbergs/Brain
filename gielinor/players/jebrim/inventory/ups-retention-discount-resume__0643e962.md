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

## Next steps (priority order)
1. **LPS 300-vs-325 dispute (handover prompt below).** Confirm contractual threshold; of LPS actually charged, how much sits in the disputable 300–325 band (by UPS's BILLED dims); size the refund + the engine re-bucket.
2. **Growth phase** — what discount lets UPS WIN volume it doesn't hold today (eligible-but-not-won cells).
3. **Commit the NFE deliverable** `ups_retention_levers.md` under standing auth (explicit pathspec, never push) — ask first.

## Files to read first
- `2_analysis/ups_retention_levers.md` (the retention deliverable)
- `2_analysis/carrier_engines/ups/constants.py` + `calculate.py:368-403` (LPS layer) + `CLAUDE.md` (component table)
- `1_offers/picanova/UPS/calculation/extract_incidence.py` + `sql/pull_incidence.sql` (incidence calibration; LPS code = LPS/SLP, over-max = OVR/SOV/OML)
- quest-log `S370_0643e962_ups-retention-and-lps-treatment.md`

## HANDOVER PROMPT — next Jebrim session (LPS 300-vs-325)
Hey Jebrim, UPS LPS dispute/refund investigation, continuing the EU tender oversize work (read inventory/ups-retention-discount-resume__0643e962.md). Question: of the parcels UPS actually billed LPS on, how many have a UPS-BILLED length-plus-girth under 325 cm? Context: UPS may be applying a 300 cm LPS threshold when our contract is 325 cm — every LPS on a parcel UPS measured at 300–325 is then wrongly charged + disputable. Use UPS's BILLED dims (its dimensioner, S199), not our declared dims; the gold mart bucket lacks per-line dims, so this legitimately departs to raw UPS invoice lines in enterprise_silver (tcg_nfe overlay; creds NFE/.env) — but check fact_shipment_invoice_lines first. Start at 1_offers/picanova/UPS/calculation/extract_incidence.py (it knows the source table, the LPS charge code, and whether billed dims are present). Deliverables: (1) confirm the contractual LPS threshold (325 vs 300) from 1_offers/picanova/UPS/ — load-bearing, verify not assume; (2) from LPS-charged lines, billed L+G distribution, count + € in [300,325); (3) size the refundable pool; (4) engine implication — BILLABLE_LPS_BANDS includes c_300_325; if 325 is correct that band moves billable→disputed, quantify. Price against GROSS LPS (€101.80, engine credits no refund) AND note incumbent is already net of ~22%-and-rising realized refunds (Q1: gross €94,291 / refund €20,841 / net €73,451). Watch-outs: billed vs declared dims; LPS/SLP vs over-max (OVR/SOV/OML) vs AHS; COUNT(*) on charge lines; note the invoiced period.

## Reproduce
Bash+polars 1.33 from `2_analysis/` (parquets) + Redshift MCP (mart + silver ups_invoices). Incumbent LPS query: silver ups_invoices LPS+SLP netamounteur split by sign, joined to fact_shipments (UPS/PCS PL/invoice) by trackingnumber, by month. Engine LPS: cost_matrix cost_lps + recompute p_lps×101.80 via incidence parquets.

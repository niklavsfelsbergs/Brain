# UPS LPS / oversize — how the EU-tender engine treats it (gross-on-gross, 300 cutoff)

From [[S370_0643e962_ups-retention-and-lps-treatment]]. Source: `2_analysis/carrier_engines/ups/{constants.py,calculate.py:368-403,CLAUDE.md}` + `1_offers/picanova/UPS/calculation/{extract_incidence.py,sql/pull_incidence.sql}`.

UPS bills LPS/OML off **its own dimensioner** (S199), not our declared dims — a geometry engine on mart dims prices oversize ~€0 while the real net is material. So the engine carries an **empirical expected-cost layer**, not a triggered charge:

- Per eligible parcel: band by OUR declared L+G (`a_under250 / b_250_300 / c_300_325 / d_325_419 / e_419plus`); look up `p_lps`, `p_ovm`, `ovm_net_per_event_eur` for (packagetype × band) from `oversize_incidence_cohort.parquet` (band-level fallback), calibrated from real UPS invoices.
- `cost_lps` (billable, bands c/d/e i.e. L+G>300) = `p_lps × (101.80 + 40kg-minbill-bump)`.
- `cost_oversize_disputed` = sub-300 LPS (`p_lps × 101.80`) + over-max family (`p_ovm × ovm_net_per_event`). Both columns sum into `cost_total_eur`.
- It's an **expected value spread fractionally** across all cohort parcels — not "this parcel oversized → +€101.80." A p_lps=0.08 parcel carries €8.50 expected LPS.

**Billable cutoff = 300 cm.** `BILLABLE_LPS_BANDS = [c_300_325, d_325_419, e_419plus]`; the calibration header calls 300–325 a "tolerance zone" filed as billable. **Open: contractual LPS threshold may actually be 325** → c_300_325 would be mis-bucketed (disputable, not justified). Live dispute lever → [[S370_0643e962_ups-retention-and-lps-treatment]] handover.

**Gross vs net (load-bearing):**
- Engine LPS = **gross** €101.80 × count-incidence. `n_lps` counts any shipment with an LPS/SLP charge line — **refunded ones included** (the reversal is a separate negative line; `has_lps = MAX(...)` still 1). The net €(`lps_net_eur`) is used only for the over-max line + a sanity check, NOT for LPS pricing. So **engine credits zero LPS refund** (deliberate — "reversal coverage collapsed Q4-2025").
- Incumbent (keep) cost IS net of realized refunds (raw invoice net). **Asymmetry: incumbent LPS net, engine LPS gross.**

**Reality check (Q1-2026, UPS PCS-PL book):** engine modeled LPS €81,296 | incumbent gross €94,291 | refund −€20,841 (22%, rising Jan 11%→Mar 43%) | **net-paid €73,451**. Engine lands ~+11% above net, below gross — not a wild overstatement. The refund mechanism is **alive and growing**, contradicting the "reversals collapsed" assumption. Refund opportunity = push the recovery rate (e.g. the 325-threshold argument), not a model rewrite.

Charge codes: LPS family = `LPS,SLP`; over-max family = `OVR,SOV,OML` (silver `enterprise_silver.ups_invoices.chargedescriptioncode`). Related: [[eu-tender]], [[carrier-contracts]].

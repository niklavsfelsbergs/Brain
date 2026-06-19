# DPD-PL current contract is export-only — PL-domestic not priced

**Source:** bi-analytics `2_analysis/carriers/dpd_pl_current/constants.py` (read [[S221_eec4ee99_eu-tender-report-review-qa|S221]], 2026-06-12); cross-checked against `routing_assignment.parquet` + the 2026-Q1 cost matrix.

The modelled **DPD-PL current contract** (`dpd_pl_current` engine — the offer we KEEP, from `DPD PL Offer 2026.xlsx`) prices an **export book only**:

- **Direct (special offer, HOME)** — 6 cheap countries: AT, DE, FR, BE, LU, NL.
- **MIX HOME** — the full served set, **29 countries**: AT, BA, BE, BG, CH, CZ, DE, DK, EE, ES, FI, FR, GB, GR, HR, HU, IE, IT, LT, LU, LV, NL, NO, PT, RO, RS, SE, SI, SK. (UA/IM suspended.)
- **PL is NOT on the served set.** A DPD-PL → Poland **domestic** parcel rejects `country_not_served` — there is no modelled domestic rate.

**Consequence in the tender reports:** parcels routed to / kept on DPD that have no eligible service-level row come back with a NULL service and surface as the **"carrier-level rates"** slice (relabeled "Poland — not in contract" in `report_no_hermes_v2`). For DPD-Poland that's ~1% of its 659,511 €/yr line — **1,943 Q1 parcels (≈7,871/yr): 93% PL-domestic (`country_not_served`), 7% `over_max_weight`** (heavy tail to ~31 kg). They ride on DPD today (kept as incumbent via the do-nothing/cell-keep path) but the extracted 2026 sheet carries no PL-domestic rate.

**So it's a rate-card coverage gap, not a model bug.** If a clean DPD-PL service split is wanted, the task is to obtain/extract the DPD-PL **domestic** rate card. Open follow-up ([[S221_eec4ee99_eu-tender-report-review-qa|S221]]).

> **Reconciliation — this is the no-Hermes scenario.** The 1,943 is the **no-Hermes** routing scenario (`routing/no_hermes/`). The **base routing** scenario reports **1,887** for the same DPD-PL carrier-only slice (1,806 PL-domestic + 81 `over_max_weight`) — see [[2026-06-09-dpd-pl-current-engine-export-only-gap]]. The PL-domestic floor matches (~1,806); the difference is the over-max **export** tail, which grows when Hermes is dropped. Two scenarios, not a discrepancy (verified 2026-06-19).

Relates to [[eu-tender]] domain digest and the carrier-contracts dimension-coverage work.

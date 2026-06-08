---
quest: S163_ups-phase1-offer-triage
sid8: 0109840c
ts: 2026-06-08 18:30
open_dep: awaiting UPS Round-1 replies (Q1 fuel base, Q4 LPS threshold, Q6 peak schedule are the headline-blockers); LPS-default decision pending principal
---

# UPS carrier assessment — resume

**Status:** in-progress. Phase 1 done. **Phase 2 v1 calculator BUILT and RUNS** (this session, sid8 7e303a70 continuing 0109840c). Phase 3 (comparison/findings) not started; held until Round-1 answers land.

**Where we are.** Phase-2 v1 engine scaffolded + built + run end-to-end under
`bi-analytics-main/NFE/projects/2_EU_tender_2026/1_offers/picanova/UPS/calculation/`. Prices
**155,010 / 155,010 (100%)** 2026-Q1 PCS-PL UPS-outbound shipments. Mechanics verified against
the rate card (DE@1kg→2.82 exact; billable=greater(actual,dim/5000) round-up-0.5; fuel=35% of
base; bucket-sum invariant 0 violations). Mart grounded via the shipping-agent (not from memory).

**Window (2.1):** **2026-Q1 (Jan–Mar), principal-confirmed.** Population = `production_site='PCS PL'`
+ `UPPER(shipping_provider_group)='UPS'` — the clean ORWO exclusion (verified zero PCS-PL rows
carry a `ups_orwo` line). 100% dim+weight populated; 0% over 70kg; 98.5% invoiced.

**Calculator files (all new this session):**
- `calculation/sql/pull_shipments.sql` — Q1 PCS-PL UPS pull; `enterprise_silver.fact_shipments`
  + **`shipping_mart.fact_shipment_cost_summary`** (the `enterprise_silver` cost-summary doesn't
  exist — only `_old`; live one is in shipping_mart — grounded 2026-06-08).
- `calculation/extract_rates.py` → `data/{rates_standard,rates_zone,de_zones}.parquet`.
- `calculation/engine.py` → `output/replay.parquet` (per-shipment cost + chosen service + buckets).
- `calculation/README.md` — run instructions + rate-card-shape + tagged-param table.

**Load-bearing modelling fact:** Standard Single is **destination-keyed** (each column = a
negotiated country *group*; same UPS zone, different rate → look up per destination, not per zone);
Express/Saver/Expedited are **zone-keyed** via DE_ZONES. That's why the zone matrix was extracted.

**Tagged parameters (every uncertain input; top of engine.py):** FUEL_PCT=0.35 (Q1/Q4, ~2×
real ~20%), PEAK €0.20/pkg in-window + PEAK_PCT=0 (Q6), LPS on/300cm/€101.80 (Q4),
RESIDENTIAL_MODE='all' +€0.40 (no mart flag exists), OML=€0 (waived, confirmed), LINE_HAUL=€0
(Q11), customs excluded (A6).

**KEY FINDING — LPS placeholder is 12× the actuals.** Book default (L+girth>300cm, €101.80, on)
fires on **16,257 parcels (10.5%) = €1.65M**, vs **actual oversize €142K on 707 parcels (0.5%)**.
It inverts the cost structure (LPS > base) and made the calc total (€3.34M LPS-on) 2.7× the actual
Q1 freight (€1.26M). → LPS is **Q4-decision-vital**, not a benign placeholder. **DECIDED (principal
2026-06-08): v1 LPS default = OFF** (model €0 until Q4 defines the real threshold; one-flag
togglable). With LPS off the calc total = **€1.68M** (residual gap to €1.26M actual is mostly
fuel 35% vs real ~20%). The validation-vs-actuals block still prints the LPS-if-on figure (€1.65M,
12×) every run. Headline is held regardless.

**Headline discipline:** the engine refuses to present a quotable number — every run prints
"PROVISIONAL & UNDERSTATED" (line-haul €0 → understated; fuel/peak/LPS provisional). Per keepsake
risk #1 (provisional-fuel collapse). **Do not quote a UPS calculated total until Q1/Q4/Q6 land.**

**Open items carried (for principal / next session):**
1. **LPS v1 default** — DECIDED: OFF (principal 2026-06-08). re-rate when Q4 lands.
2. **Residential mode** — defaulted 'all' (+€0.40 every B2C parcel; no shipment-row flag exists).
   Back-test against `real_residential_eur` in Phase 3; principal can flip to 'off'.
3. **Cost-summary schema** — used `shipping_mart.fact_shipment_cost_summary` (live) not the
   non-existent `enterprise_silver` one. AP/Maersk siblings may join the stale `_old`; worth a
   maintainer note (the shipping-agent flagged a rulebook gap).
4. **UPS Worldwide Economy NOT quoted (principal confirmed with carrier 2026-06-08).** WW ECO
   won't be offered → the overseas tail that rides it (destinations Standard doesn't serve: AU,
   US, CA, Channel Islands, CY/MT, IS, GI — ~6,776 parcels) **stays on the current contract**,
   costed at invoiced actual. Implemented as the engine's **WW-ECO-stays rule**: `stays_current`
   (Standard-unserved + valid actual) → `go_forward_eur` = actual; else quoted calc. Fuel-independent
   by design (a calc>actual rule falsely marked 96% "stay" under the provisional 35% fuel —
   keepsake risk #1). Go-forward total = €1.54M (vs €1.68M pure quoted calc); the overseas tail now
   carries its €155k actual instead of an inflated premium-air calc (AU was €210k calc vs €127k actual).
5. **PCS PL origin PLZ** is a constant not in the mart (get from facilities); not load-bearing in v1.

**Next concrete steps (when Round-1 lands or principal decides):**
1. Resolve the LPS default (open item 1) → re-run.
2. On UPS replies: set FUEL_PCT (Q1 base/index), LPS threshold+amount (Q4), peak schedule (Q6);
   re-rate.
3. Phase 3 (PLAYBOOK 3.x): real-bucket comparison (real_* already pulled), per-country findings,
   `findings.md`. Add line-haul layer (A10) before any headline.

**Anchors:** `players/jebrim/research/2026-06-08-ups-current-invoice-charge-profile.md` (actuals
ground truth) + `.../2026-06-08-ups-germany-2026-published-surcharges.md` (published book). Phase-2
mart grounding trace: `quest-log/in-progress/S164_ups-phase2-mart-grounding.md`.

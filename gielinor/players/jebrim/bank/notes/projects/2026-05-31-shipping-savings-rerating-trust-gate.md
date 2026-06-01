# Shipping cost-savings re-rating — trust gate + integrity model

**Source:** [[S132_32ff1025_shipping-savings-routing-optimization|S132]] (autonomous, 2026-05-31). Project: `bi-analytics-main/NFE/projects/5_shipping_savings/`.

**The ask.** Re-rate actual Picanova shipments (EU+US) against active carrier contracts; find where we ship on a sub-optimal eligible provider. Active contracts only (EU-tender offers excluded). Window Feb1–May1 2026 settled-invoice, ~785k ships / €5.12M (~€20.5M annualized addressable).

**The trust gate (the load-bearing step).** Before any savings claim, each rate engine must reproduce what that carrier ACTUALLY charged on its own shipments (`lib/validate_engines.py`) — like-for-like, median + p90 error %. An engine that can't reprice reality can't be trusted to price a competitor. Then a signed-ratio diagnostic (`lib/diagnose_engine_bias.py`): ratio engine/actual with IQR — tight band far from 1.0 ⇒ a single missing structural component (calibratable); centered ⇒ unbiased scatter (usable in aggregate).
- **Result: only 4/12 engines unbiased** — postnord (0.95), usps (1.05), ups_eu (1.02), ontrac (1.05) = TRUSTED. fedex/asendia (0.83-0.85) = CAUTION. The rest QUARANTINED: dhl_paket 1.27, dpd_pl 1.45 (HIGH); db_schenker 0.65, dpd_uk 0.62, maersk_eu 0.50, yodel 0.41 (LOW).
- **Diagnosis pattern:** the EU "contracted-through-Maersk" LOW cluster (yodel/maersk) = rate card prices only the last-mile leg; actual adds upstream Maersk injection/line-haul (yodel: card €2.22 vs actual €5.63, razor-tight 0.41). HIGH cluster = surcharge stack over-applied or actual deeper-discounted than card.

**Integrity model (no fudge).** savings = actual_paid − cheapest eligible TRUSTED alternative. Actual paid is always real, so savings can be found FROM any carrier (even quarantined ones — uses their real cost). Only TRUSTED engines may be DESTINATIONS — a biased engine manufactures fake-cheap wins and bias does NOT wash out in aggregate. Never blanket-scale a biased engine to match its actual (that fabricates the number). Region-locked (EU→EU, US→US).

**Result.** PAPER €1.75M/yr → DEFENSIBLE €857k/yr after the mirage guard (see [[2026-05-31-rerating-mirage-guard-capability-and-noise]]). Dominated by US carrier rebalancing (FedEx over-priced vs USPS/OnTrac ≈ €528k). EU defensible thin (DPD-PL→UPS €45k) — big EU carriers quarantined.

**Key locks.** Picanova entity = `source_system IN (Picturator,PicaAPI)` minus ORWO/sendmoments shops; US=`production_site='PCS CMH'`, EU=rest. Cost basis settled-invoice (orders ≥30d), annualize ×4. Engines: `engines/<key>.py` exposing `price(df)→df` (+eligible/reject/cost/components), 134 tests pass. ups_eu/asendia row-loop a per-row polars `_grid` filter → slow+OOM; chunk via `lib/_run_engine_chunked.py`.
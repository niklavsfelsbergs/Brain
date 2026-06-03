# S145 — Transit-time SLA grounding pass (shipping-agent emulation)

**Player:** Jebrim · **Actor:** shipping-agent (mart specialist, emulated) · **Date:** 2026-06-02
**Session:** 7ac0cf07 · **Extends:** S124 carrier-proxy-SLA work
**Brief:** Reconnaissance only — read-only, gold `shipping_mart` contract, NO raw layer. Size/coverage the gold mart against the cohort we'll use for a per-country transit-time SLA + full-lead-time decomposition + US zone clustering. Do NOT compute SLA, do NOT build a deliverable.

## Scope used
- **Vertical (TCG):** `source_system IN ('Picturator','PicaAPI')` — resolved from contract (mart-contract §1, how_to rule 12), not guessed. Excludes PCS / Rewallution / ORWO.
- **Window:** ship-anchored `received_by_carrier_date >= '2026-03-01' AND < '2026-06-01'` (Mar–May 2026, three full months; June = settling tail excluded).
- **Tier:** gold-contract only. Local full-access profile (`tcg_nfe`) present but brief forbids raw layer — stayed on `shipping_mart.*`.

## Turn log / findings (terse)
- TCG source filter confirmed live: Picturator 13.1M, PicaAPI 2.88M total fact rows.
- Carrier identity = `shipping_provider_group` (group) + `shippingprovider_extkey` (service). DB Schenker = `shipping_provider_group = 'DB SCHENKER'` (UPPERCASE), extkeys `DBSCHENKERPLEUHOME` (dom) + `DBSCHENKERPLEUB2B`. Oversized bracket identifiable.
- Timestamps: `received_by_carrier_ts` + `delivered_by_carrier_ts` both true `timestamp without time zone`. Cohort coverage (ship-anchored): received 100%, delivered 90.2% overall — DHL 98.7 / UPS 88.2 / Maersk 79.8 / **DPD UK 0.0** (delivered never wired — known-dq) / DBS 92.1.
- Pre-rounded fields to AVOID per Niklavs: `transit_time_business_days` (integer, rounded, excludes ship day) + `transit_time_days` (numeric calendar). Compute decimal business days ourselves from the two true ts — sound: 677,900 both-present, only 330 negative (0.05%) + 2 zero, avg 3.26 cal days.
- Full lifecycle in gold: order_created 100%, production_order_created 98.9%, order_produced 98.9%, received 100%, delivered 90.2%. NO truck-closed/handover ts in gold (truck cost only). Line-haul gap = produced→received computable.
- Geography: `destination_country` + `destination_country_code` (DE 332K, US 144K, GB 82K…). US: `shipping_zipcode` 100% (906 zip3), `shipping_region` holds clean US state names for US slice (avoid mart-wide). US carriers: OnTrac, USPS, FedEx, tiny UPS.
- Origin (cohort): PCS PL ~589K, PCS CMH ~154K dominate.
- `is_returned`: false 660,518 / NULL 87,374 (~11.6%) / true 3,385. `=false` drops NULL too; semantics unconfirmed (contract) — caveat.

## Verdict
- READY: per-country transit SLA (EU + most carriers); full-lead-time decomposition (order→produced→received→delivered) from gold alone.
- COVERAGE-LIMITED: DPD UK (0% delivered — exclude or describe-only); Maersk/UPS 80–88% delivered (tier per rule 16); is_returned NULL chunk.
- Deliverable: chat-only (recon). No chart/CSV written.

## Open / needs principal
- Confirm `is_returned = false` handling for the ~11.6% NULL (drop vs keep).
- Confirm window: Mar–May 2026 ship-anchored, recommend ~2 wk extra tail exclusion if anchoring on delivered date.

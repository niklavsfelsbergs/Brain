# [[S148_104c786b_eu-tender-dhl-paket-round2|S148]] P1 — FedEx PL Q1 2026 fuel-surcharge history + CH clearance fee

**Penguin:** P1 (Jebrim, EU Tender 2026 — FedEx Round-2 rebuild)
**Spawned:** 2026-06-03
**Deliverable:** research/2026-06-03-fedex-q1-2026-fuel-history.md

## Progress log

- Read research.md + spawning-penguins.md. Methodology clear: broad scout → narrow reads → synthesize, pulled-vs-reconstructed flag per cell.
- Plan: (1) try FedEx PL surcharges page direct + Wayback; (2) stage EIA USGC kerosene weekly + EC Weekly Oil Bulletin AGO series for reconstruction fallback; (3) find FedEx published threshold→% tables for both indices; (4) CH clearance fee.
- FedEx PL page + FedEx fuel PDFs ALL gated (403/system-down) — confirms [[S102_6217a8d5_eu-tender-fedex-reply-review|S102]] gating still in force. FRED CSV blocked (403). Reconstruction fallback is the path.
- PULLED EIA USGC weekly jet-fuel series (eia.gov LeafHandler, as of 2026-05-28 release). Q1 2026: Jan 1.908/1.873/2.015/2.095/2.184, Feb 2.120/2.154/2.317/2.469, Mar 3.103/3.478/4.038/4.009. Calibration: June anchor USGC $4.113 → Intl 49.25%.
- NOTE: Jan/Feb USGC ~$2/gal looks low vs typical $2.3-2.5. Flagging for sanity-check against threshold table. Need FedEx Intl threshold table + Regional (EC AGO) table + threshold.
- BREAKTHROUGH: r.jina.ai proxy of the FedEx-International-Fuel-Surcharge-6-April.pdf returned the FULL Intl band table (EU version). Bands: $1.69-1.89 -> 31.50%, then +0.25%/band on $0.03 steps, up to $3.98-4.01 -> 47.75%. This is the EU Intl schedule (matches PL).
- WRINKLE: table is dated 6-April. FedEx re-bases the TABLE periodically (Apr 6, May 11 cited). June anchor USGC $4.113 -> 49.25% is ABOVE this table's top ($4.01->47.75%), so table shifted UP between Apr and Jun. Applying Apr-6 table to Jan/Feb/Mar = approximation; Q1 table likely sat LOWER (less aggressive) than Apr-6. Reconstructed Q1 values are an UPPER-ish estimate. Flag clearly.
- LAG RULE: FedEx Intl uses USGC price with a ~2-week look-back (price from 2 weeks prior sets current Monday's %). Standard FedEx mechanic. Will note in reconstruction.
- EC AGO (Regional): partial — week 02/03/2026 EU avg diesel 1629.22 EUR/1000L; 23-Feb ~1.59 EUR/L, 30-Mar ~2.08 EUR/L. Need full weekly series. Trying fgeerolf mirror + fuel-prices.eu.
- PULLED EC AGO full Q1 weekly series (fuel-prices.eu/weekly/2026): Jan 1.502/1.496/1.513/1.523, Feb 1.534/1.536/1.549/1.545, Mar 1.572/1.748/1.835/1.965/2.000 (EUR/L).
- BIG FIND: r.jina proxy of FedEx PL page returned (a) FULL Regional band table 1.11-1.15->17.00% up to 2.51-2.55->32.00% (EUR0.04 bands, +0.5%/2-bands ~ +0.25%/band avg); (b) Intl weekly HISTORY rows — PULLED, not reconstructed: 09-15 Mar $2.469->35.00%, 16-22 Mar $3.103->40.25%, 23-29 Mar $3.478->43.50%. No Jan/Feb history rows shown (page only retains ~recent weeks).
- LAG CONFIRMED: effective-week W uses EIA USGC price from ~2 wks prior. 09-15 Mar uses $2.469 = my EIA 27-Feb week; 16-22 Mar uses $3.103 = EIA 06-Mar; 23-29 Mar uses $3.478 = EIA 13-Mar. Clean ~2-wk lag.
- TABLE-VERSION WORRY RESOLVED for the Intl schedule: pulled March rows ($2.469->35.00, $3.103->40.25, $3.478->43.50) match the April-6 band table EXACTLY -> the same Intl schedule was live across Q1/early-Q2. Safe to reconstruct Jan/Feb with the April-6 table. (June anchor 49.25% at $4.113 is just the table extended above its printed $4.01 top, same +0.25%/0.03 slope.)
- CH clearance fee: FedEx CH pages gated; ancillary-clearance-service gated. Trying duty-tax.html + what-extra-charges + general FedEx disbursement schedule.
- CH FEE PULLED (FedEx CH ancillary component page via proxy): Disbursement/Advancement Fee = 2.50% of duty+VAT, MIN CHF 22.00 (whichever greater) — the DDP per-shipment clearance fee. DAP standard Express clearance bundled in transport (CHF 0 incremental, no separate flat entry fee). Situational add-ons: multi-line CHF 13/item from 6th, In-Bond CHF 74, OGA CHF 84+, Post-Entry-Adj CHF 135. (Generic pan-EU display €8/€15/2.5% superseded by CH-specific CHF schedule.)
- WROTE deliverable research/2026-06-03-fedex-q1-2026-fuel-history.md. Both indices reconstructed with PULLED March Intl validation; CH fee pulled. Done.

## Final result
- Intl FSC Q1: Jan ~31.65%, Feb ~32.65%, Mar ~39-40% (Mar PULLED, Jan/Feb reconstructed on validated table). Q1 back-loaded by the late-March jet-fuel spike.
- Regional FSC Q1: Jan ~19.5%, Feb ~19.5%, Mar ~23% (all reconstructed; June anchor cross-check passed).
- CH clearance: CHF 22.00 min / 2.5% of duty+VAT (DDP); CHF 0 incremental (DAP standard).
- Gaps: no pulled Jan/Feb Intl or any Regional history rows (Wayback unreachable this session); CH DAP flat fee appears not to exist (bundled).

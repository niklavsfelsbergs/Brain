# Shipping-agent pull: NA cost-side decomposition for Torsten (topic 46 follow-up)

**Spawned:** 2026-06-15 as shipping-agent (mart specialist) under Jebrim.
**Brief:** Three cost-side decompositions over gold `shipping_mart`, NA (US+CA+MX-negl), TCG (Picturator+PicaAPI), final-cost basis. Continues NFE topic 46.
**Deliverable:** chat-only findings block back to principal (no chart requested).

## Status (turn-by-turn)
- Read how_to.md (full) + CLAUDE.local.md (maintainer profile present — `tcg_nfe`, upstream in scope). Stayed on **gold contract** — all 3 Qs answerable on the four gold facts.
- Read topic-46 findings.md + cost-side SQL for scope/basis discipline.
- **Tie-out CONFIRMED:** May-2026 NA = €599,266 / 57,909 ships / €10.35 pp / 97.5% EW-invoiced. Topic 46 had €599,835 / 58,014 — within 0.1% (more invoices landed since 06-11). Same basis.
- Q1 USPS: per-parcel Jan €6.22 / Feb €5.94 / Mar €6.27 / Apr €6.52 / May €7.19. **USPS carries NO bucket split — all-in cost sits in base-rate, fuel≈€0.** Step vs Jan-Mar vol-wtd €6.14: Apr +€0.38 (€6.8k), May +€1.05 (€18.8k). Step accelerates May. Base-vs-fuel NOT separable for USPS.
- Q2 CMH (=PCS CMH, Columbus, >97% NA vol): FXEHD diversion. Excess vs Feb-Mar baseline (3,415): Apr 4,378 / May 2,140. Penalty Apr €11.76 / May €10.92 (HD €19.87/€19.45 vs OnTrac/USPS blend €8.11/€8.53, actual monthly mix). Incremental **Apr €51.5k / May €23.4k** — confirms prior €48k/€22k, slightly higher on live data. May HD coverage 91.7% (lag) — soft.
- Q3 Fuel NA: NOT flat. Fuel/parcel Jan €0.81 → Apr €1.23 → May €1.14; share 7.9%→11.3%→10.8%. YoY May €64.8k vs May-2025 €60.8k (+6.4%); Q1-26 €134.1k vs Q1-25 €182.4k (−26%, but driven by carrier mix). April jump driven by **FedEx fuel** (CMH diversion volume) + OnTrac. Fuel concentrated in **OnTrac (largest) + FedEx**; USPS≈€0, Asendia minor.

## Caveats flagged
- Buckets = invoiced subset only (97.5% EW May). USPS all-in in base bucket (no fuel/surcharge separation in mart) — flagged in Q1.
- Sep-Nov-2025 bucket baselines noisy (OnTrac credit-notes) — avoided.
- Q3 YoY: carrier population changed (FedEx-81% 2025 → OnTrac/USPS/FedEx 2026) so fuel YoY is partly mix, not pure rate.

Deliverable returned in chat. Quota points NOT computed (principal converts).

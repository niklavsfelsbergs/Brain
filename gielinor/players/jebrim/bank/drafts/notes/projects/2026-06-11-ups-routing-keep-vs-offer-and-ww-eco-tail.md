# EU-tender routing — UPS keep-vs-offer split + the WW-ECO (Australia) tail

Source: [[S212_177f00f1_eu-tender-no-hermes-report|S212]] (2026-06-11), building the no-Hermes report. Anchor: `2_analysis/final_report_no_hermes/build_stats_no_hermes.py`; cost matrix probe.

**UPS is modeled as incumbent-keep AND new-offer engine, picked per cell.** Since [[S208_9399f067_ups-cascade|S208]], UPS has both a keep side (current contract forward = `today_eur ×1.05` GRI) and an engine (the 2026 EU offer, face value). The routing cherry-picks per (dest×product) cell: current contract where it's cheaper, new offer where it wins. Consequence flagged by Niklavs: this per-cell mix is **operationally incoherent for a single signed contract** — wholesale-new-offer = −€50.9k (worse than today, scorer), the routing's selective +€103k relies on running *both*. Kept-UPS cells silently assume the current contract persists.

**The "carrier-level rates" (null-service) UPS rows = the WW-ECO tail = entirely Australia.** The 2026 UPS offer is EU-scoped; its engine has only `standard` (524,940 eligible matrix rows) + `express_saver` (45 rows). AU is **rejected** (`country_not_served`, no WorldWide-Economy product modeled) → those parcels stay on the current UPS contract. Live distribution: **2,636 Q1 / ~11k yr** AU parcels, ~€27/parcel — the *cheapest* available (every alternative pricier: DHL Paket ~€38, Maersk ~€56, DHL Express ~€70, FedEx ~€79).
- These carry **€0 saving** (priced same on do-nothing and plan) → don't inflate the headline.
- **Exposure: if signing the new offer ENDS the current contract, AU has no modeled price.** Forced reassignment to the cheapest portfolio mix (DHL Paket + Maersk) = **+€211k/yr**. The €976k no-Hermes headline (and the with-Hermes headline) implicitly keeps AU on UPS.
- Open: does the UPS 2026 offer cover AU, or is there a UPS AU/WWE special offer? (Niklavs checking; live sibling [[S211_dcd18cfd_ups-savings-dbschenker-reroute-investigation|S211]] owns the UPSWWE question.)

**Tender scope = 17 destinations, GB/US absent.** Cost matrix destinations: AT AU BE CH DE DK ES FI FR IE IT LU NL NO PL PT SE. **GB and US are not in the matrix at all** — neither report prices them. Any GB/US pricing seen elsewhere is from the carrier_overview / live mart / SCM, not this tender. (CH *is* in scope and the UPS engine prices it — cheaper than current; only AU is the kept-current tail.)

**Generalizable:** a kept-incumbent baseline in a switching analysis assumes the current contract survives the decision. Where the decision ENDS that contract (sign the new offer), kept cells priced on the old contract are an unmodeled gap — surface them. The tell here was a null/"carrier-level" service label hiding a single-country lane the new offer can't reach.

## Related
- [[eu-tender]] domain digest · [[2026-06-09-routing-cost-basis-decisions]] (UPS = actuals ×1.05, pre-S208 basis).
- Sibling lesson: [[populated-column-is-not-a-measurement]] (a populated/kept value isn't proof of forward validity).

# NA shipping-quota bridge — April & May 2026 vs Q1, country×channel Bennet (for Torsten/finance)

**Actor:** shipping-agent (mart sub-agent), in Jebrim's namespace
**Date:** 2026-06-15
**Tier:** gold contract (`shipping_mart.*` only). Local maintainer profile present but not used — pure gold pull.
**Brief:** Continue the corrected NA-quota analysis. Build TWO bridges (April vs Q1, May vs Q1), baseline = Q1-2026 NA avg quota 25.49%. Decompose into channel-mix, country-mix, within-cost (+ carrier sub-drivers 3-6), within-revenue, residual. € and pp per component. Tie-out exact.

## Validated basis (NOT re-litigated — inherited from S_shipagent_na-quota-mart-revenue-correction)
- Quota = `final_shipping_cost_eur` / `net_revenue_eur` (mart's own revenue, reproduces SCM).
- Cost = final (COALESCE real, expected, avg). Lens = order-month (`shop_order_created_date`). NA = US+CA.
- Channel via `source_system`: Picturator=D2C, PicaAPI=API. Cells = country × channel (4 cells).

## Reproduction gate — PASSED (all to validated endpoints)
- Q1 NA = **25.486%** (target 25.49 ✓), May NA = **27.145%** (target 27.14 ✓)
- US Q1 = **24.50%** ✓, US May = **26.51%** ✓
- **NA April = 28.331%** (computed fresh). NOTE: April quota > May — April has bigger reroute + April CA quota spikes to 40.0%.
- CA sub-quota: Q1 33.9% / Apr 40.0% / May 33.7% — confirms CA >> US (24.5-26.5%). Country mix is a real lever.

## Bennet decomposition (country×channel, midpoint, ties exact, residual 0.0000pp)
### April vs Q1 (ΔQ +2.846pp; rev €2,139,124)
- Channel mix +1.516pp (+€32,438) | Country mix −0.130pp (−€2,770) | Within-cost +1.698pp (+€36,327) | Within-rev −0.239pp (−€5,123)
- API rev-share 16.5%→27.5%; CA rev-share 10.4%→9.3%

### May vs Q1 (ΔQ +1.659pp; rev €2,162,941)
- Channel mix +2.034pp (+€43,994) | Country mix −0.126pp (−€2,721) | Within-cost +1.697pp (+€36,699) | Within-rev −1.946pp (−€42,089)
- API rev-share 16.5%→33.9%; CA rev-share 10.4%→8.9%

## Cost sub-drivers (carrier shift-share, month-vol @ Q1-avg unit economics; reconcile to within-cost, NO double-count)
Carrier-driven NA cost-per-parcel rise ties to: Apr +€23.4k (+1.092pp), May +€21.8k (+1.009pp). Sub-drivers SUM to this, not on top of mix.
| sub-driver | April € (pp) | May € (pp) |
|---|---|---|
| 3 USPS rate + 8% fuel | +€9,747 (+0.456) | +€18,732 (+0.866) |
| 4 CMH→FedEx reroute (gross) | +€63,096 (+2.950) | +€50,562 (+2.338) |
| 5 Cheaper-carrier mix benefit | −€36,001 (−1.683) | −€25,969 (−1.201) |
| 6 Other carrier rate (FedEx base cuts etc) | −€13,474 (−0.630) | −€21,508 (−0.994) |
| **sum = carrier-driven cpp rise** | **+€23,368 (+1.092)** | **+€21,817 (+1.009)** |
- Gap to within-cost (Apr €12.9k / May €14.9k) = mix shifting into costlier CA/API cells. Explained, not residual.

## Key DQ / flags
- **USPS 8% fuel surcharge folds into `base_rate_eur`, NOT the fuel bucket** — manifests as USPS cpp rise (€6.15→€6.63 Apr partial, →€7.16 May full). Surcharge eff. Apr 26 → ~0 April / full May confirmed by the data (USPS fuel bucket ≈ €0 all months).
- **Reroute reconciliation vs prior anchors:** prior NA had ~€51.5k April / ~€23.4k May. My GROSS FedEx carrier-mix is €63.1k/€50.6k; NET of FedEx within-rate base cuts (−€20.7k/−€28.2k) = €42.4k Apr / €22.3k May. May net €22.3k matches prior €23.4k. Prior figures are net-of-base-cuts; mine separate gross reroute from FedEx base cuts.
- May %inv = 91.7% (< 95%) — invoice lag, costs will backfill upward slightly. Q1/Apr ≈ 98.9%.
- Null revenue: ~0.4-0.6% of NA TCG rows. CA API tiny (26-43 ships/mo) — CA splits are directional.

## Verdict (per month)
- **April (+2.85pp):** channel mix +1.52pp + within-cost +1.70pp the two movers; country mix tiny negative; within-rev only −0.24pp (April API orders still rev-healthy). Cost side dominated by the big CMH reroute, USPS surcharge ~0.
- **May (+1.66pp):** channel mix BIGGER (+2.03pp, API share hit 33.9%) but within-rev −1.95pp claws most back (API rev/order dilution full); within-cost same +1.70pp but now full USPS surcharge + smaller reroute. Net rise smaller than April despite bigger mix.
- One-liner: April = cost-led (reroute) on top of mix; May = mix-led, with cost rotating from reroute to USPS surcharge, and a big revenue-dilution offset.

## Deliverable
- Chart: `shipping-agent/workbench/analysis/na-quota-bridge-apr-may/outputs/20260615-120327--na-shipping-quota-bridge-vs-q1-2026-april-may-quota-pp-by-driver.html`
- SQL + data + scripts: same workbench folder.

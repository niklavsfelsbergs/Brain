---
quest: S244_na-quota-torsten-revenue-correction
sid8: bb5d1f1a
ts: 2026-06-15 13:30
open_dep: Torsten reply not yet rewritten on corrected NA numbers + within-revenue −1.95pp May needs validation
---

# Resume — NA quota (Torsten P&L follow-ups + revenue-denominator correction)

## Status
in-progress (analysis corrected + tied out; Torsten-facing rewrite + one validation open)

## Where we are
Rebuilt the NA May-2026 quota analysis on the CORRECTED basis after the principal caught that I used `dw.sales_fact` for revenue instead of the mart's own `fact_shipments.net_revenue_eur`. Corrected basis = final cost ÷ mart `net_revenue_eur`, order-month lens — **reproduces SCM exactly** (US May 26.52% ≈ 26.5%). Built per-month NA bridges (April 28.33% / May 27.14% vs Q1 25.49%), each component split into total cost € and quota pp, with channel mix and country mix isolated. Both tie to residual 0.000. Separately: confirmed the **USPS first-ever 8% fuel surcharge** (Apr 26 2026 – Jan 17 2027, Ground Advantage, commercial rates) as the mechanism behind the USPS step.

## Next concrete step
Blocked on principal direction: (1) **Rewrite the Torsten reply on the corrected NA numbers** — earlier drafts used the wrong denominator and the "all channel mix / cost favorable" framing, which the correction overturns (cost is a real driver; within-cost +1.70pp both months). Decide US-vs-NA framing for him (he filters US in SCM = 26.5%; analysis now NA). (2) **Validate the May within-cell revenue −1.95pp** — is it a genuine AOV rise or a Bennet split trading off against channel-mix +2.03? Pull revenue-per-order by cell, Q1/Apr/May (offered, not yet run). (3) Fold the USPS surcharge + corrected quota basis into the shipping-mart / carrier-contracts domain digests (bank drafts written this session — await alching). (4) topic 46 (`bi-analytics-main/NFE/shipping_topics/46_...`) is still uncommitted in bi-analytics and now carries a KNOWN denominator error — needs a correction pass before it's cited.

## Files / paths to read first
- `quest-log/in-progress/S244_bb5d1f1a_na-quota-torsten-revenue-correction.md` (the arc + corrected numbers)
- Sub-agent traces: `S_shipagent_na-quota-mart-revenue-correction.md` (the fix), `S_shipagent_na-quota-bridge-apr-may-country-channel.md` (the per-month bridge)
- `research/2026-06-15-usps-2026-fuel-surcharge.md` (the surcharge, source-anchored)
- Chart: `shipping-agent/workbench/analysis/na-quota-bridge-apr-may/outputs/20260615-120327--*.html`
- Prior basis: `inventory/na-quota-may-2026-resume__e9dbce2d.md` (topic-46, the WRONG-denominator version — superseded)

## Pending drafts
- `examine/drafts/2026-06-15-verify-inherited-data-source-against-contract.md` (Q5 correction)
- `bank/drafts/notes/projects/2026-06-15-usps-2026-fuel-surcharge.md`
- `bank/drafts/notes/projects/2026-06-15-na-shipping-quota-mart-revenue-basis.md`

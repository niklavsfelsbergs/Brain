# Scanning for "bad" segments by a ratio: floor on current-period + invoiced cost first

**Observed:** S229 (826ecc23), loss-making-lane quota scan. I ranked country×carrier×packagetype
lanes by cost-quota (shipping cost ÷ revenue) over a trailing-12-month, all-cost-sources window.
The top results were CH+DB Schenker (real) but also **GB+DHL flat mailers at 175%** — which I
framed as a live ongoing bleed. Niklavs asked one question: *"how much has this cost us in 2026?"*
Answer: **€0.** Those 1,790 shipments were entirely Sep–Nov 2025 — a dormant Q4 Christmas
calendar/poster batch. The high quota was a **seasonal artifact**, not a live problem. Reframing
to **2026-only + invoiced-cost-only** then surfaced a genuine live loss-maker (US+FedEx 21" Tube,
2,474 ships, 98% invoiced) that the seasonal/estimated noise had buried.

**The lesson:** a ratio-anomaly scan (quota, cost-per-X, margin) over a long lookback with
modeled/estimated values in the denominator-or-numerator produces **two classes of false
positive**: (1) **stale/seasonal** segments that were real once but are dormant now, and (2)
**estimated-cost** segments whose ratio is a model output, not a measurement. Before ranking,
floor the population to **the current period** (so dormant spikes drop out) and to
**ground-truth/invoiced values only** (so the ratio is measured, not modeled). The first pass's
ranking is a hypothesis list; the floored ranking is the decision list.

**How to apply:** when asked to "find the bad/worst segments" by any ratio, my default first cut
should be current-period + settled/actuals-only — and I should *say* that's the cut and why,
rather than defaulting to "all history, all cost sources" because it has more rows. The longer,
modeled view is a secondary lens for trend, not the closure-decision lens. Cross-link
[[2026-06-12-stay-in-the-named-source]] (the same session's mart-not-sales_fact correction).

**Also this session (Correction 1):** I reached for `dw.sales_fact` because it conveniently
carried revenue+cost+country on one grain; Niklavs: *"use the shipping mart, nothing to do with
sales fact."* When the principal names the source/domain, stay in it — don't pull a sibling
source in for convenience even when it's technically easier. (Minor; folding here rather than a
separate draft.)

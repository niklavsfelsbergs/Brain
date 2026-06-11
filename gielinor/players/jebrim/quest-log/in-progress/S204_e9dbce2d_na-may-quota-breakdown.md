# S204 — NA May-2026 shipping-cost quota breakdown (P&L review Monday)

- **Session:** e9dbce2d, opened 2026-06-11
- **Player:** Jebrim
- **Status:** in-progress

## The ask

Finance (pasted request): very high shipping-costs quota in May 2026 for the **NA market**. Break it down into the main drivers:

1. actual cost changes / increases / surcharge effects,
2. revenue change effects,
3. revenue share (mix) change effects — mainly the strongly increased **Reseller API** share.

Insights needed **by Monday noon** (2026-06-15); P&L review Monday afternoon.

## Working assumptions (flagged, to confirm with Niklavs/finance)

- Quota = shipping cost ÷ revenue (net), per the P&L definition. Exact revenue basis (net of VAT/discounts?) to pin before final numbers.
- NA market = destination US + CA (+ MX if present), not production site.
- Reseller API = `source_system = 'PicaAPI'` channel in the mart.
- Baseline = April 2026 (MoM) + May 2025 (YoY) + Jan–May 2026 trend.

## Plan

1. Pin definitions: quota formula, NA scope, channel mapping (mart profile).
2. Pull NA monthly series from shipping_mart via shipping-agent: shipments, cost (11-bucket split), by channel (source_system) + carrier.
3. Revenue side: check fact_shipment_orderitems for revenue; else Redshift (tcg_nfe) order revenue.
4. Decompose ΔQuota = mix effect (Δrevenue-share × segment quota) + within-segment cost effect (split by charge bucket → surcharges vs base) + within-segment revenue effect.
5. Deliverable: findings writeup in bi-analytics NFE shipping_topics/na_quota_may_2026/ + send-ready summary for finance.

## Turn log

- 2026-06-11: Session open. OPEN posted to comms. Anchors written. Starting mart profiling via shipping-agent.
- 2026-06-11: Prior-work mining: topic 41 = CMH OnTrac→FedEx diversion (~€52k impact, FXEHD €18.3 vs ONTRAC €9.4/ship) — candidate May cost driver. Topic 38 = UPS-DE Apr decomposition (methodology template, DE-scope).
- 2026-06-11: Revenue side built in NFE topic 46 (`46_na_market_quota_may_2026`): dw.sales_fact monthly by shoptype, NA = US/CA/MX, 2025-01..2026-05. Channel lens = dim_shops.shoptype ('Reseller (API)' = PicaAPI). Verified: revenue_net_price_eur = product-only (items sum matches 100%, excludes shipping_amount_eur).
- 2026-06-11: Quota series + Bennet decomposition done (decompose_quota.py, effects sum to ΔQ exactly). Headline: May-26 26.15% vs Q1-26 24.62% (+1.53pp), vs May-25 25.25% (+0.90pp); **Apr-26 was higher (27.15%)**. Net mix effect (API 16%→34% share) ≈ +1.8pp vs Q1 — more than the whole rise. API shipping ~fully recharged (May €246.5k charged vs €233.6k cost) → gross-quota optics. D2C within-cost +0.5pp vs Q1 = carrier/surcharge territory, pending mart pull.
- 2026-06-11: shipping-agent spawned (background) for ship-date cost lens: monthly by channel/bucket/carrier, NA dest, invoice-coverage caveats. `pending` at this writing.
- 2026-06-11: shipping-agent returned, `completed`. Verified its parquets (channel/carrier sums reproduce €599,835 / 58,014 to the cent). Cost side NOT a driver: May per-ship €10.35 (−10.8% YoY) on +10.7% volume, 97.2% invoice-settled, no surcharge movement; carrier mix favorable; OnTrac→FedEx diversion ≈ €20k May (fading from ≈ €45k Apr). NA pinned = US+CA. Mart lens quota 28.1% vs 27.2% YoY — agrees +0.9pt with dw lens.
- 2026-06-11: findings.md finalized (both lenses + decomposition + recommendations). Finance summary drafted, surfaced to Niklavs in-chat. Note: agent left its trace as `S204_shipagent_*` — numbering collides with this quest's S204, filenames distinct, left as-is.
- 2026-06-11: Niklavs probed the OnTrac/USPS→FedEx rerouting sizing. Re-sized in quota points from on-disk parquets: Apr ≈ €48k ≈ +2.2pt (explains April's 27.1% peak), May ≈ €22k ≈ +1.0pt gross (net +0.5pp after base-rate/Ground-Economy offsets), ~€11/ship penalty vs OnTrac/USPS counterfactual. Verdict sharpened: YoY all mix; within-2026 the rerouting IS the genuine cost driver, fading, ~1pt recoverable. findings.md §(a) + recommendation 2 updated.
- 2026-06-11: Completeness pass on Niklavs's cue. Cleared: USPS cost-coverage YoY bias (USPS entered NA Jul-2025, ~100% costed throughout). Corrected: API recharge claim softened "margin-positive" → "≈ break-even, 97–106% depending on lens" (mart ship-month cost €254.8k > €246.5k charged; dw order-grain €233.6k < charged). Added: Asendia USA only carrier with rising unit cost (€15.87→€21.08/ship YoY, ≈ +€16k). findings.md updated.
- 2026-06-11: PRINCIPAL CORRECTION — we PAY shipping on API orders; `shipping_amount_eur` is not recharge income (my inference from column name + cost-magnitude match was wrong; field meaning to verify before future use). Recharge/"optical" point struck from findings + summary; conclusion sharpened: mix effect is a real P&L effect, lever is commercial (API shipping pricing/terms). Candidate examine-draft: this is another populated-column-is-not-a-measurement instance (inferred a money flow from a field name).
- OPEN ITEMS for Niklavs: (1) finance's exact quota formula (cost booking month, denominator) — for level reconciliation if their number diverges; (2) known-dq.md maintainer edit for Oct-2025 PicaAPI expected-cost garbage (€96 across 5,099 ships) — principal-gated per teaching loop; (3) topic-46 bi-analytics files uncommitted, awaiting commit cue; (4) verify what `shipping_amount_eur` actually represents on PicaAPI orders before anyone reuses it (per the correction it is NOT recharge income).
- 2026-06-11 (close): No pending external actions.

- 2026-06-11 (post-close follow-up): Niklavs's context — the FedEx diversion was DELIBERATE promise-routing for the MerchOne Mother's/Father's-Day gifting peak (also explains the API-share seasonality: May-25 12% spike = Mother's Day 2025). Checked June MTD daily mix inline (mart, ship-day): FedEx HD ~4.1% share / ~128/day vs 6.5–8% / ~180/day Feb–Mar baseline → routing FULLY UNWOUND; June ≈ €9.39/ship (expected-basis). No Father's-Day (Jun-21) re-ramp through Jun-10 — re-check week of Jun-15. findings.md updated (deliberate-routing reframe + seasonality overlay).

- 2026-06-11 (post-close, second thread — SPAWNED NEW PROJECT): June general health sweep → found ORWO DHL2→DHL3 account migration with unmapped provider grouping (carrier rollups misleading). Niklavs reframed the job as "find fuckups = minor details, broad lens" → built `NFE/projects/6_shipping_reporting_v2/` (sweep.py + sql/dimension_churn.sql + README) live in-session: dimension-churn sweep, log-ratio mix_score + cost_score, lifecycle-dim split. Validated Mar→Apr (rediscovered FXEHD #7 / FEDEX #3 / PicaAPI #4 + unprompted Yodel/DBS/DPD-UK finds; zV miss #36 = interaction-fuckup lesson). Live May→Jun run: DHL2/DHLKP VANISHED top, ORWO_80x60 collapse (open lead), FedEx unwind confirmed. Three scoring lessons in README. This thread should graduate into its own quest next session — v2 is a standing project, not part of the NA-quota quest.

Hi, I looked into the May 2026 NA shipping cost quota. Short version: the elevated quota is almost entirely a revenue-mix effect from the Reseller API share increase, not a shipping cost increase. Actual shipping cost per parcel fell 10.8% year over year.

1. Actual cost / surcharge effects: not the main driver. May NA shipping cost was €599.8k total (−1.2% vs May 2025) at €10.35 per parcel (−10.8% YoY, −4.3% vs April) on +10.7% parcel volume. No surcharge category moved materially in May and fuel was flat; 97% of the May cost is already invoice-backed, so the figure won't restate. The one real cost event is a temporary rerouting of Columbus parcels from OnTrac/USPS to FedEx Home Delivery (~€11 extra per parcel): roughly €48k / +2.2 quota points in April — which made April our actual worst month — and €22k / +1.0 point in May, already fading. Restoring the normal OnTrac/USPS routing recovers about a point of quota regardless of the channel-mix topic.

2. Revenue change effects: secondary, and mostly the mix in disguise. NA net product revenue fell ~6% YoY while parcels grew 11% — because D2C orders fell 28% while Reseller API orders grew 156%. Revenue per order within each channel was stable (D2C ~€48, API ~€31).

3. Revenue share effects (Reseller API): this is the driver. API revenue share went from 12% (May 2025) and 16% (Q1 2026) to 34% in May 2026. API orders carry roughly half the product revenue per order of D2C at similar shipping cost, so the channel's shipping quota runs at ~34–36% vs ~22–24% for D2C. The mix shift alone adds ≈ +3.1 points YoY to the blended quota — more than the entire observed increase; within-channel economics actually improved (the API channel's own quota fell from ~43% to ~35%).

Implication: as long as the Reseller API share keeps growing, the blended quota will keep rising mechanically even with falling carrier costs — this is channel economics, not carrier cost inflation. The structural lever is commercial (API pricing / shipping terms with resellers); the operational lever is restoring the Columbus OnTrac/USPS routing (~1 quota point).

On our basis (shipping cost ÷ net product revenue) the blended quota is 26.1% for May 2026 vs 25.2% in May 2025 and 24.6% Q1 2026 average — and April (27.1%) was actually worse than May. If your P&L shows May as a sharper spike, the difference will be the cost/revenue basis (e.g. costs booked by invoice month) — happy to reconcile against your exact quota formula.

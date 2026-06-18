# S250 (sid8 44773956) — US LucaNet vs BI shipping reconciliation (topic 48)

Player: Jebrim. Topic: `bi-analytics-main/NFE/shipping_topics/48_US_Lucanet_vs_BI`. Canonical record: that folder's **`findings.md`** (this entry is the gielinor-side narrative; findings.md holds the numbers).

## What this session did

Reconciled US shipping **cost + revenue + quota** between LucaNet (accounting / mgmt-reporting export) and BI (gold `shipping_mart` / SCM dashboard), 2026 YTD Jan–May. Then explored the QuickBooks GL as the underlying source.

## Arc

- Read the LucaNet USD export; located the shipping **quota** (Shipping Costs ÷ Net Revenue) and **per-carrier** costs (OnTrac/USPS/FedEx/Asendia/UPS).
- Pulled the BI side via shipping-agent. Settled the **canonical scope**: `production_site IN ('PCS MI','PCS PX','PCS CMH') AND destination_country_code IN ('US','CA')`, order-month. **Cost ties ~2% YTD** (BI invoiced native USD +1.9%); per-carrier FedEx +7.5%, OnTrac +2.3% high, Asendia −2.1% / USPS −0.8% low.
- **Quota**: BI 26.3% vs LucaNet 25.1% (SCM-faithful). Earlier mismatch vs the dashboard traced to cost-lens (ship-month invoiced freight vs order-month final cost) + a missing MI site + a missing destination filter — all corrected.
- **Revenue (the key finding)**: BI mart (€10.29M) corroborated by `ol_gold.fact_order` (€10.37M, +0.7%) — within ~1% **every month**. The **February −10% gap is LucaNet-side** (both order sources agree Feb was low). Mart is not undercounting.
- **QuickBooks** (`qbintegrationproductiondb`, Postgres 5432): US-entity GL, **AP/cost only, no revenue**. 2026 shipping bills essentially **unbooked** ($706 vs ~$5M/yr historically; sync is live → AP entry lag) → **LucaNet 2026 figures must be accruals.** Connection saved to `NFE/.env` (`QB_*`, gitignored).

## Corrections this session (harvest)

- Relayed an **unverified shipping-agent claim** ("MerchOne product-only / B2C shipping-inclusive") as a load-bearing revenue-definition finding; retracted after principal challenge — not in the contract. → `examine/drafts/2026-06-17-relayed-unverified-subagent-claim.md`.
- **Mixed EUR (BI) next to USD (LucaNet)** in the workbook headline; principal read it as BI "much less" revenue when ~13% was just the FX rate. Fixed to single-currency + Gap column. → `examine/drafts/2026-06-17-mixed-currency-reads-as-volume-gap.md` + memory.
- **PCS MI = Miami (CLOSED)**, not "Mexicali" (agent mis-decoded). → memory `reference_pcs_site_codes_and_us_mart_filter`.

## Pending external actions

None pending.

## Sub-agent traces (this session)

`S244_44773956_us-origin-native-usd-lucanet-recon.md`, `S244_shipagent_us-quota-mart-revenue-lens.md`, `S246_us-lucanet-final-vs-invoiced-3way.md`, `S_shipagent_lucanet-vs-bi-us-2026-jan-may-by-carrier.md` — shipping-agent pull traces feeding this reconciliation.

## Deliverables (external NFE repo — not committed by this brain close)

- `shipping_topics/48_US_Lucanet_vs_BI/findings.md` (canonical)
- `US_LucaNet_vs_BI_2026YTD_comparison_v2.xlsx` + `build_comparison.py`
- `NFE/.env` (`QB_*` connection — gitignored)

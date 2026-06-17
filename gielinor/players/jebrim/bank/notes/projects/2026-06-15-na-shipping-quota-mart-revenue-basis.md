# Shipping quota — the mart carries its own revenue (corrected basis)

**Corrected** 2026-06-15 ([[S244_bb5d1f1a_na-quota-torsten-revenue-correction|S244]]/bb5d1f1a), principal-caught. Supersedes the topic-46 / `decompose_quota.py` method that used `dw.sales_fact` for revenue.

- **Quota = shipping cost ÷ revenue, both from `shipping_mart`.** Revenue column = **`fact_shipments.net_revenue_eur`** (EUR, shipment grain, per-order revenue allocated to each parcel by quantity share). Do **NOT** join `dw.sales_fact` for the denominator — that was the prior error.
- **This reproduces the SCM dashboard** (the authoritative/productized quota). Tie-out: US May-2026 = **26.52% ≈ SCM 26.5%**.
- **Lens = order-month** (order-placement date) is what reproduces SCM. Ship-month and production-month give different (higher) numbers (27.2 / 27.4 for US May) and are wrong for the quota.
- **Scope matters:** SCM defaults/filters can be US-only; "NA" = US + CA. CA runs a *much* higher quota than US (Q1 ~34% / Apr ~40% / May ~34% vs US ~24–26%), so US-only ≠ NA — name the scope.
- **Revenue-definition caveat:** for B2C (Picturator) `net_revenue_eur` **includes the shipping the customer paid** — so it's not a pure-product denominator. It's the dashboard's quota basis (correct for "quota"), but a pure-product denominator would be smaller and push quota up. Conscious choice.
- Validated endpoints (mart revenue, order-month, final cost): US Q1 24.50% / May 26.51%; NA Q1 25.49% / Apr 28.33% / May 27.14%.

Cross-link: [[shipping-mart]] digest (should gain the revenue column + quota formula), [[scm]] digest, [[S244_bb5d1f1a_na-quota-torsten-revenue-correction|S244]]. The prior wrong-denominator resume `inventory/na-quota-may-2026-resume__e9dbce2d.md` is superseded.

# Shipping mart — cost column vocabulary (2026-05-22)

**Source of truth (external, pending apply):** to be added to `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/reference/mart-contract.md` and `how_to.md` § cross-cutting rules. Drafted here because the bi-analytics-main repo is not present on this machine; apply on the next bi-analytics session.

**Quest:** S024 — shipping-agent rulebook revamp (new tranche).

## The four cost columns on `fact_shipments`

| Column | What it is | Trust | When it populates |
|---|---|---|---|
| `real_shipping_cost_eur` | The carrier-invoiced cost. **The cost we actually paid.** | High — invoiced, reconciled. | Once a carrier invoice line has been received and matched to the shipment. Backfills as invoices arrive. |
| `expected_shipping_cost_eur` | Pre-invoice estimate from rate cards / negotiated-rate logic for this carrier × lane × weight. Approximate but lane-aware. | Medium — model-derived, not invoiced. | Available for the shipment as soon as it ships, before any invoice lands. |
| `avg_shipping_cost_eur` | Rougher fallback when neither real nor expected can be computed (e.g. carrier/lane combo lacks a rate-card source). | Low — historical average. | Always available where the carrier has *any* historical cost data. Last-resort estimate. |
| `final_shipping_cost_eur` | `COALESCE(real, expected, avg)` — the **one number to use** unless the analysis explicitly needs the breakdown. | Mixed — see `cost_source`. | Populated when at least one of the three is. |
| `cost_source` | Flag — which of `real` / `expected` / `avg` populated `final` for this row. | — | Always populated when `final` is. |

## When to use which

- **Default — use `final_shipping_cost_eur`.** It is the agreed canonical "cost of this shipment" and matches what any downstream view will use. Don't roll your own coalesce.
- **Use `real_shipping_cost_eur` directly** only when the question is specifically about invoiced cost — variance vs estimate, invoice-completeness audits, payment reconciliation. Filtering on `cost_source = 'real'` is equivalent and clearer.
- **Use `expected_shipping_cost_eur` directly** only when comparing estimates against actuals (variance analysis: `real - expected`), or modelling cost ahead of invoice arrival.
- **Use `avg_shipping_cost_eur` directly** essentially never — it exists as a fallback for `final`, not as a primary signal.

## Cost-bucket grain — only invoiced costs have a breakdown

Cost buckets (the line-item breakdown of *what makes up* a cost — base rate, fuel surcharge, peak demand, discounts, etc.) **exist only for real (invoiced) costs**. They live on `fact_shipment_cost_summary` as 11 `bkt_*` columns (`bkt_base_rate`, `bkt_truck_charges`, `bkt_fuel_surcharge`, `bkt_remote_area`, `bkt_peak_demand`, `bkt_oversize_overweight`, `bkt_residential`, `bkt_other`, `bkt_unclassified`, plus reducers `bkt_discounts`, `bkt_credit_note`), and the invariant `SUM(bkt_*) == fact_shipment_cost_summary.total_eur == fact_shipments.real_shipping_cost_eur` holds for 100% of invoiced rows.

**Expected and avg costs are bucket-less.** They are single shipment-level estimates with no sub-shipment attribution. As a consequence:

- **`final_shipping_cost_eur` carries bucket detail only when `cost_source = 'real'`.** When `cost_source IN ('expected', 'avg')`, the row has a total but no breakdown.
- **An order's "final" shipping cost is shipment-level only.** `final_shipping_cost_eur` lives on `fact_shipments` (shipment grain); there is no order-level cost column. An order with multiple shipments aggregates by summing its shipments' `final_shipping_cost_eur`. No further drill-down below shipment grain unless every shipment in the order is sourced from `real`.
- **Bucket subset filters silently drop non-invoiced rows.** Any query that filters on a `bkt_*` column or asks "what was the fuel-surcharge component" implicitly excludes the `expected` and `avg` portion of the population. If the question is "what's our fuel surcharge exposure," the answer is bounded by the invoiced subset — note that limit when reporting.

When a query mixes invoiced and non-invoiced rows, the % invoiced rule below is the qualifier for the headline; if a bucket breakdown is also being shown, **explicitly state that the breakdown reflects only the invoiced share** (e.g. "Bucket breakdown shown on the €966K invoiced subset; €274K estimated has no breakdown.").

## The reporting rule — % invoiced

Whenever you communicate a cost figure derived from `final_shipping_cost_eur`, **surface what share of that figure is invoiced** (i.e. backed by `real_shipping_cost_eur`) versus still estimated.

**Formula (euro-weighted, default):**

```sql
SUM(CASE WHEN cost_source = 'real' THEN final_shipping_cost_eur END)
  / SUM(final_shipping_cost_eur)
```

Applied over the same filter as the headline. Output as a percentage rounded to whole points unless the slice is small enough to warrant a decimal.

**Why euro-weighted, not row-weighted.** The user reads the headline in euros; the trust qualifier should be in the same units. A row-weighted % can diverge sharply from the euro-weighted one when high-value shipments are over- or under-invoiced relative to the bulk — and the euro-weighted number is the one that answers "how much of *this number* can I trust."

**Standard output shape:**

```
Total shipping cost, <slice>: €1.24M
  % invoiced: 78%  (€966K real + €274K expected/avg)
```

The breakdown in parens is optional — include it when the slice is small or when the % invoiced is materially below 100% (rule of thumb: surface the breakdown when `% invoiced < 95%`).

**Edge cases:**

- `cost_source IS NULL` rows are *uncosted* — exclude them from the denominator AND surface their share separately if non-trivial: "X% uncosted." Don't fold uncosted into "estimated."
- For very recent windows (current week / current month-to-date) the % invoiced will be low *by design* — carrier invoices lag shipment by weeks. The number is still worth reporting; just don't treat low % invoiced on a fresh window as a wiring problem (see `reference/known-dq.md` on invoice lag).
- For windows fully past the invoice-lag horizon (e.g. >90 days old, lane-dependent), % invoiced converging well below 100% **is** a wiring or coverage problem — flag it.

## Proposal — text to apply to the shipping-agent docs

### A. Add to `reference/mart-contract.md` (new subsection under columns)

**Heading:** `## Cost columns — real vs expected vs final` (or whatever §-letter fits; placement under existing column-reference content).

**Body:** the **The four cost columns** table + the **When to use which** list + the **Cost-bucket grain** section above. Mark `last-verified: 2026-05-22` and LIVE.

Make sure the grain rule lands explicitly:

> **Bucket detail is invoiced-only.** The 11 `bkt_*` columns on `fact_shipment_cost_summary` exist only where `cost_source = 'real'`. Expected and avg costs are single shipment-level estimates with no breakdown. `final_shipping_cost_eur` lives on `fact_shipments` (shipment grain) — there is no order-level cost column; an order's final shipping cost is the sum of its shipments'. No drill below shipment grain unless every shipment in scope is invoiced.

### B. Add to `how_to.md` §0 cross-cutting rules (new numbered rule)

**Rule (proposed wording, ~110 words):**

> **N. Report % invoiced alongside any cost figure; flag when bucket breakdowns are invoiced-only.** Costs come from a mix of invoiced (`real`), pre-invoice estimate (`expected`), and historical-average fallback (`avg`), coalesced into `final_shipping_cost_eur` with `cost_source` flagging the choice. Whenever you communicate a cost number derived from `final`, also report the euro-weighted invoiced share — `SUM(real) / SUM(final)` over the same filter. Format: `Cost: €X. % invoiced: Y%`. Surface the `real + estimated` split when % invoiced < 95%. Inside the invoice-lag horizon (current week/month), low % invoiced is expected, not a defect. **If the answer includes a bucket breakdown (any `bkt_*` column), state that the breakdown reflects only the invoiced subset** — buckets do not exist for expected/avg, and final cost has no sub-shipment grain when non-invoiced.

(Insertion point: §0 cross-cutting rules, next numbered slot. Rule numbering currently runs through rule 7 per the S023 patch — this would be rule 8 unless rules have been added since.)

## Why this note exists in Jebrim's bank

The cost-column vocabulary is durable mart knowledge — Jebrim should know it without re-deriving from `S001` / `S014_d1` / `S023` notes every time. The proposal section is here because the shipping-agent's external docs cannot be edited from this machine; capturing the exact text now means the next bi-analytics session can apply it without re-thinking.

Promote during alching when (a) the proposal text has been applied to the shipping-agent docs and the column-vocabulary half is the surviving content, or (b) the proposal sits unapplied long enough that Jebrim needs the column model as durable knowledge regardless of doc state.

## Related

- [[shipping_mart_coverage_audit_2026-05-21]] — coverage audit (pulled costs from `fact_shipment_cost_summary.total_eur` at the time; `fact_shipments` cost cols have since been wired).
- `S001` repo-orientation turn at L87 — the original `COALESCE(real, expected, avg)` observation.
- S024 quest-log entry 2026-05-22 (T16) — the friction surface that prompted this draft.

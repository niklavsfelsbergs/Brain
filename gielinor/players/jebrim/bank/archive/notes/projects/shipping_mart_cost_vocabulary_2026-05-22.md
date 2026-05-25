# Shipping mart — cost column vocabulary (gold-verified)

**As of:** 2026-05-22 (S024 + S028 gold-verified; applied to shipping-agent same day).

**Gold verification (S028, 2026-05-22).** The four shipping facts live in `shipping_mart.*` (gold layer). Column shape, cost-bucket invariant, and `cost_source` value distribution all verified against the live gold schema via `ship_mart_ro`. Unqualified references to `fact_shipments` and `fact_shipment_cost_summary` mean the gold tables (`shipping_mart.<table>`).

**Naming asymmetry to flag.** Column name is `real_shipping_cost_eur` but the `cost_source` flag value for invoiced rows is `'invoice'` (not `'real'`). Document both names side-by-side wherever ambiguity could surface.

## The cost columns on `fact_shipments`

| Column | What it is | Trust | When it populates |
|---|---|---|---|
| `real_shipping_cost_eur` | The carrier-invoiced cost. **The cost we actually paid.** | High — invoiced, reconciled. | Once a carrier invoice line has been received and matched to the shipment. Backfills as invoices arrive. |
| `expected_shipping_cost_eur` | Pre-invoice estimate from rate cards / negotiated-rate logic for this carrier × lane × weight. Approximate but lane-aware. | Medium — model-derived, not invoiced. | Available for the shipment as soon as it ships, before any invoice lands. |
| `avg_shipping_cost_eur` | Rougher fallback when neither invoiced nor expected can be computed (e.g. carrier/lane combo lacks a rate-card source). | Low — historical average. | Available where the carrier has *any* historical cost data. Last-resort estimate. |
| `final_shipping_cost_eur` | `COALESCE(real, expected, avg)` — the **one number to use** unless the analysis explicitly needs the breakdown. | Mixed — see `cost_source`. | Populated when at least one of the three is. |
| `cost_source` | Flag — which input populated `final` for this row. Values: `'invoice'` / `'expected'` / `'avg'` / NULL (uncosted). | — | Always populated when `final` is. |
| `real_shipping_cost_local` | Same as `real_shipping_cost_eur` but in the original invoice currency. | High when populated. | NULL where every charge line came from EUR-source carriers. |
| `currency_code` | Currency of the `_local` columns. | — | NULL when `_local` is NULL. |

### `cost_source` distribution (verified 2026-05-22 across full fact)

| Value | Share | Meaning |
|---|---:|---|
| `invoice` | 65.15% | Invoiced — `real_shipping_cost_eur` populated, bucket detail on `fact_shipment_cost_summary`. |
| `expected` | 24.37% | Pre-invoice estimate from rate cards. No bucket detail. |
| `(null)` | 8.04% | Uncosted — `final` NULL, no cost data at all. |
| `avg` | 1.99% | Historical-average fallback. No bucket detail. |

## When to use which

- **Default — use `final_shipping_cost_eur`.** It is the agreed canonical "cost of this shipment" and matches what any downstream view will use. Don't roll your own coalesce.
- **Use `real_shipping_cost_eur` directly** only when the question is specifically about invoiced cost — variance vs estimate, invoice-completeness audits, payment reconciliation. Filtering on `cost_source = 'invoice'` is equivalent and clearer.
- **Use `expected_shipping_cost_eur` directly** only when comparing estimates against actuals (variance analysis: `real - expected`), or modelling cost ahead of invoice arrival.
- **Use `avg_shipping_cost_eur` directly** essentially never — it exists as a fallback for `final`, not as a primary signal.

## Cost-bucket grain — only invoiced costs have a breakdown

Cost buckets (the line-item breakdown of what makes up a cost — base rate, fuel surcharge, peak demand, discounts, etc.) **exist only for invoiced costs**. They live on `fact_shipment_cost_summary` as **11 bucket column pairs** (each in `_eur` and `_local` form). All columns named directly — no `bkt_` prefix.

**11 buckets included in `total_eur`** (verified invariant `SUM(included_buckets_eur) == total_eur` across 200K-row sample, max diff 0.00):

```
base_rate_eur, truck_charges_eur, fuel_surcharge_eur,
remote_area_charges_eur, peak_demand_charges_eur, oversize_overweight_eur,
residential_eur, discounts_eur, credit_note_eur,
other_eur, unclassified_eur
```

**2 additional buckets excluded from `total_eur`** (carried separately for tax/customs reporting):

```
tax_eur, customs_duties_eur
```

**Cross-row invariant** (verified for all 12.03M `cost_source = 'invoice'` rows):

```
fact_shipment_cost_summary.total_eur
  == fact_shipments.real_shipping_cost_eur
  == fact_shipments.final_shipping_cost_eur
```

**Expected, avg, and uncosted rows are bucket-less.** They are single shipment-level estimates (or absent entirely) with no sub-shipment attribution. As a consequence:

- **`final_shipping_cost_eur` carries bucket detail only when `cost_source = 'invoice'`.** When `cost_source IN ('expected', 'avg')` or is NULL, no breakdown exists.
- **An order's "final" shipping cost is shipment-level only.** `final_shipping_cost_eur` lives on `fact_shipments` (shipment grain); there is no order-level cost column. An order with multiple shipments aggregates by summing its shipments'. No drill below shipment grain unless every shipment in the order is invoiced.
- **Bucket subset filters silently drop non-invoiced rows.** Any query that filters on or asks "what was the fuel-surcharge component" implicitly excludes the ~34% non-invoiced population. If the question is "what's our fuel surcharge exposure," the answer is bounded by the invoiced subset — note that limit when reporting.

When a query mixes invoiced and non-invoiced rows, the % invoiced rule below is the qualifier for the headline; if a bucket breakdown is also shown, **explicitly state that the breakdown reflects only the invoiced share** (e.g. "Bucket breakdown shown on the €966K invoiced subset; €274K estimated has no breakdown.").

## Cost basis disclosure — state upfront, not on follow-up

Every cost answer states **which cost basis it uses** in the opening line, before the headline number — not only when the principal asks.

- **Invoiced only** — `real_shipping_cost_eur` or `cost_source = 'invoice'` subset.
- **Final (invoiced + estimated)** — `final_shipping_cost_eur`, the coalesce.
- **Estimated only** — `expected_shipping_cost_eur` or `cost_source = 'expected'` subset (rare; flag if it surfaces).

**Why upfront.** A cost number's trust level is a function of its basis. The principal cannot evaluate "€5.24/parcel" without knowing whether the numerator is real money out the door or partly modelled — and whether the numerator and denominator come from the same population (see denominator rule below). Leading with the basis frames the number; a basis disclosed only on follow-up frames it as a caveat.

**Anchor: 2026-05-22 transcript.** Shipping-agent answered "€5.24 per parcel for TCG in April 2026 — €1.45M total spend across ~276K parcels" without naming basis. Principal asked: "is this based on real or also expected cost?" Agent then disclosed "real cost only." Disclosure was correct but reactive; this rule moves it to the opening line so the question never needs to be asked.

**Wording template (one phrase, not a paragraph):**

> "Invoiced cost only — €X. % invoiced: Y%."
> "Final cost (invoiced + estimated) — €X. % invoiced: Y%."

Use the basis name + the headline + the % invoiced. Don't pad.

## Average denominators — must match numerator scope

When the headline is an average (per-shipment / per-parcel / per-order), the denominator's population must match the numerator's population.

**Two valid pairings:**

| Numerator | Valid denominator | Result |
|---|---|---|
| `SUM(real_shipping_cost_eur)` over filter | `COUNT` of shipments WHERE `cost_source = 'invoice'` in same filter | True average **invoiced cost per invoiced shipment**. |
| `SUM(final_shipping_cost_eur)` over filter | `COUNT` of shipments WHERE `final_shipping_cost_eur IS NOT NULL` in same filter | True average **final cost per costed shipment** (invoiced + estimated). |

**Invalid pairing — never produce this without flagging it explicitly:**

| Numerator | Mismatched denominator | What it actually is |
|---|---|---|
| `SUM(real_shipping_cost_eur)` over filter | `COUNT` of **all** shipments in filter (incl. uncosted / uninvoiced) | Not a floor. Numerator misses the cost of uninvoiced shipments; denominator counts them. The result equals `invoiced_per_shipment × (% shipments invoiced)` — a single number with two distortions baked in. |

**The "floor" framing is wrong.** It is tempting to call `SUM(real) / COUNT(all)` a "floor" because adding missing invoices would only raise the numerator. But: (a) the missing invoices are *not zero*, they are unknown but expected to be cost-similar to the invoiced ones; (b) the resulting "floor" sits below any plausible truth, underpricing everything by the uninvoiced share. Leading with the floor invites the principal to anchor on it. Lead with the invoiced-only average instead; if a population-weighted number is wanted, recompute with `SUM(final)` over costed shipments.

**Anchor: 2026-05-22 transcript.** Shipping-agent computed `SUM(c.total_eur) / NULLIF(COUNT(DISTINCT f.shipment_id), 0)` with `LEFT JOIN fact_shipment_cost_summary` — joining invoiced costs onto all shipments, then dividing invoiced sum by all-shipment count. Produced €5.24 and framed it as "a floor, not a final number." Correct fix on follow-up: restrict the denominator to invoiced shipments → €6.29. €6.29 is what the answer should have led with; €5.24 should never have been produced. The framing should also flip — €6.29 is the trusted invoiced-only number, with `SUM(final) / COUNT(costed)` as the population-weighted complement when invoice coverage is incomplete.

**Operational shape:**

- Default to the invoiced-only average. State basis as "invoiced cost only."
- If the slice has < 95% invoiced, also surface the population-weighted final-cost average so the principal sees both. Don't surface the mismatched "invoiced over all" computation.
- For very recent windows where % invoiced is low by design (invoice lag), the population-weighted final-cost average is the more informative number — lead with it; the invoiced-only average sits alongside as the high-trust subset.

## The reporting rule — % invoiced

Whenever you communicate a cost figure derived from `final_shipping_cost_eur`, **surface what share of that figure is invoiced** (i.e. backed by `real_shipping_cost_eur`) versus still estimated.

**Formula (euro-weighted, default):**

```sql
SUM(CASE WHEN cost_source = 'invoice' THEN final_shipping_cost_eur END)
  / SUM(final_shipping_cost_eur)
```

Applied over the same filter as the headline. Output as a percentage rounded to whole points unless the slice is small enough to warrant a decimal.

**Why euro-weighted, not row-weighted.** The user reads the headline in euros; the trust qualifier should be in the same units. A row-weighted % can diverge sharply from the euro-weighted one when high-value shipments are over- or under-invoiced relative to the bulk — and the euro-weighted number is the one that answers "how much of *this number* can I trust."

**Standard output shape:**

```
Total shipping cost, <slice>: €1.24M
  % invoiced: 78%  (€966K invoiced + €274K expected/avg)
```

The breakdown in parens is optional — include it when the slice is small or when the % invoiced is materially below 100% (rule of thumb: surface the breakdown when `% invoiced < 95%`).

**Edge cases:**

- `cost_source IS NULL` rows are **uncosted** (~8% of mart-wide — not trivial). Exclude them from the denominator AND surface their share separately if non-trivial: "X% uncosted." Don't fold uncosted into "estimated."
- For very recent windows (current week / current month-to-date) the % invoiced will be low *by design* — carrier invoices lag shipment by weeks. The number is still worth reporting; just don't treat low % invoiced on a fresh window as a wiring problem (see `reference/known-dq.md` on invoice lag).
- For windows fully past the invoice-lag horizon (e.g. >90 days old, lane-dependent), % invoiced converging well below 100% **is** a wiring or coverage problem — flag it.

## Application status

Applied 2026-05-22 to `shipping-agent/how_to.md` §0 rule 11 (state cost basis upfront + denominator-matching + % invoiced euro-weighted + bucket invoice-only). The €5.24 vs €6.29 worked example is preserved above in § Average denominators. Original proposal text in git history.

## Related

- [[shipping_mart_coverage_audit_2026-05-21]] — coverage audit (pulled costs from `fact_shipment_cost_summary.total_eur` at the time; `fact_shipments` cost cols have since been wired and verified in gold).
- `S001` repo-orientation turn at L87 — the original `COALESCE(real, expected, avg)` observation.
- S024 quest-log entries 2026-05-22 (T16 framing, T18 disclosure/denominator sharpening, T20 gold verification).

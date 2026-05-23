# S055 D1 — Cost Math + SQL Contract Review (Shipping Costs Monitoring)

**Scope.** Read-only technical + mathematical review of the cost basis, SQL mart contract, and
the data-shaping/aggregation math for the `shipping_costs_monitoring_nextjs` dashboard
(branch `shipping-mart-cutover`). Files read in full: `sql/query_mart.sql` (95 lines),
`sql/query_mart_items.sql` (23 lines), and the data-shaping sections of `pipeline.py` (3753
lines total — reviewed constants/`RAW_KEEP_COLS`/`BUCKET_COLS` ~L30-100, `_cost_config` L230-237,
`_pull_query`/chunking/baskets L262-394, `pull_raw` load+clean+cast L397-535, `transform`
cost-flag derivation L542-597, `compute_corridor_costs` agg L610-667, `_explode_products`
L1194-1211, `_write_daily_summary` L2320-2351, `_write_daily_product_summary` L2354-2431,
`write_processed` L2438-2497, summary driver L3688-3738). Also read the quota/aggregation
consumers since the quota *formulas* live in the API layer, not `pipeline.py`:
`src/app/api/overview/route.ts`, `src/app/api/breakdown/route.ts`,
`src/app/api/breakdown-quota/route.ts`, `src/app/api/avg-costs/route.ts`. **Did not** review the
alert/issue engine (`_build_alerts`, `_detect_creep`, shifts, deviations, suppression — D2's scope),
beyond noting where it shares a cost column.

**Confidence.** High on the SQL contract and pipeline cost-derivation logic (statically clear).
Medium on the quota/avg population-mismatch findings — they are real code asymmetries, but whether
they actually move the numbers depends on data facts I could not query (can `real_shipping_cost_eur`
be non-null and ≤0? what fraction of rows are uncosted per corridor?). Those are flagged
**verify-with-data**.

**Note on brief drift.** Several hypotheses in the brief are now stale on this branch (the SQL was
rewritten in the gold cutover, commits `dee0265`/`e892af7`/`7a86388`):
- The **ORWO-Wolfen CASE fallback was removed** (see `query_mart.sql:37-42`). ORWO rows now lean on
  the mart's `final_shipping_cost_eur` or stay uncosted; there is no pipeline-side expected fallback.
- `cost_for_routing` is **no longer** `COALESCE(shipping_cost_final, expected_shipping_cost)`. Post-cutover
  it is a straight pass-through of `shipping_cost_final` (= mart `final_shipping_cost_eur`), see
  `pipeline.py:568`. The brief's `pipeline.py:552-564` line range is the comment, not a COALESCE.
- The **Picturator-Wolfen dedup is no longer in `query_mart.sql`** — it moved into the mart upstream.
  Not visible or enforceable from this repo anymore.

---

## Critical

### C1. Bucket-sum invariant is asserted but never enforced or checked anywhere `[MATH]`
`sql/query_mart.sql:14-26` (claim), `pipeline.py:460` (the fill), `breakdown/route.ts:154,235` (the consumer).

The contract claims `cs.total_eur == fs.real_shipping_cost_eur` to the cent AND `sum(11 buckets) ==
total_eur` for 100% of rows ("verified across ~1M rows in Q1 2025"). **Nothing in the pipeline or the
SQL re-checks this.** Two ways it silently breaks, both producing wrong numbers on the Breakdown tab:

1. **LEFT JOIN miss.** `query_mart.sql:91-92` LEFT JOINs `fact_shipment_cost_summary`. When a shipment
   has a real invoiced cost (`fs.real_shipping_cost_eur > 0`) but **no** cost-summary row, all 11 bucket
   cols arrive NULL and are filled to `0.0` (`pipeline.py:460`). The Breakdown tab derives total cost as
   `SUM(buckets)` (`breakdown/route.ts:154` → `bucketSumExpr`, used at L235/L405), so such a shipment
   shows **0 cost on Breakdown** while showing its real cost everywhere else (Overview, avg-costs). The
   "verified Q1 2025" assertion is a point-in-time check on a different (pre-cutover) source; it does not
   hold by construction.
2. **Bucket sum ≠ total drift.** If the mart's bucket decomposition ever drifts from `total_eur` (rounding,
   a new charge type not mapped to a bucket, `_local-currency` variants intentionally skipped per
   `query_mart.sql:22-23`), Breakdown's totals silently diverge from Overview's `sum_real`/`sum_routing`.

**Why it matters.** The Breakdown tab is the primary cost-decomposition surface. It uses a *different cost
basis* (sum-of-buckets) than every other tab (`cost_for_routing`/`shipping_cost`). The two will not tie out
whenever the invariant is even slightly violated, and there is no guardrail or log line that would surface
the drift. Users would see "total cost" differ between tabs with no explanation.

**Fix.** verify-with-data + fix-now. (a) Add a pipeline assertion/log after the pull: count rows where
`shipping_cost > 0 AND (sum of buckets) = 0`, and rows where `abs(sum_buckets - shipping_cost) > 0.01`;
warn with the count and EUR magnitude rather than trusting the comment. (b) Decide and document the
intended Breakdown basis — if buckets are meant to reconstruct `shipping_cost`, the LEFT-JOIN-miss rows
need either exclusion from Breakdown or a fallback so they don't read as 0.

---

## High

### H1. `real_cost_quota` / `avg_real` numerator and denominator span different row populations `[MATH]`
`pipeline.py:2334` vs `2336-2346` (daily.parquet); `pipeline.py:2413` vs `2412/2415/2419` (daily_product);
consumed at `overview/route.ts:153,214`, `breakdown-quota/route.ts:81`, `avg-costs/route.ts:59`.

`sum_real = SUM(shipping_cost)` is computed over **all rows** (no `> 0` gate, `pipeline.py:2334` and `:2413`).
But `invoiced`, `sum_revenue_invoiced`, and `sum_expected_for_invoiced` are all gated on
`shipping_cost IS NOT NULL AND shipping_cost > 0` (`pipeline.py:2333,2336,2343` and `:2412,2415,2419`).
Then:
- `real_cost_quota = SUM(sum_real) / SUM(sum_revenue_invoiced)` — numerator over all costed rows
  (incl. any `shipping_cost ≤ 0`), denominator over `> 0` rows only.
- `avg_real = SUM(sum_real) / SUM(invoiced)` (`avg-costs/route.ts:59`, `overview/route.ts:184,205`) — same skew:
  the numerator can include cost from rows the `invoiced` count excludes.

If `real_shipping_cost_eur` is always strictly `> 0` when present, these are equivalent and the code is fine.
If it can be `0` (placeholder) or **negative** (a credit-note reversal landing as negative real cost — plausible
given `discounts_eur`/`credit_note_eur` are negative reducers, `query_mart.sql:24-26`), then numerator and
denominator cover different populations and `real_cost_quota`/`avg_real` are biased.

**Why it matters.** `real_cost_quota` is a headline KPI (`KPIRow.tsx`, `overview/route.ts:22`). A
population mismatch produces a quota that is subtly wrong in a direction that's hard to spot.

**Fix.** verify-with-data, then fix-now if the data permits ≤0. Either gate `sum_real` the same way
(`SUM(CASE WHEN shipping_cost > 0 THEN shipping_cost END)`) so numerator and denominator match, or
confirm-and-document that `real_shipping_cost_eur > 0` always holds when non-null. Cheap to make consistent.

### H2. Overview `avg_cost` and Breakdown `avg_cost` use different denominators — they will not tie out `[MATH]`
`overview/route.ts:148` vs `breakdown/route.ts:237,406`.

Overview computes `avg_cost = SUM(sum_routing) / SUM(shipments)` — divides total routing cost by **all**
shipments, including uncosted ones (the daily summary at `pipeline.py:2331-2340` keeps every row;
`cost_for_routing` NULLs contribute 0 to the sum but +1 to `shipments`). Breakdown's temp table filters
`WHERE cost_for_routing IS NOT NULL` (`breakdown/route.ts:123`) and divides by `COUNT(*)` of that filtered
set. So for any corridor with uncosted shipments, Overview's avg_cost is **diluted** (smaller) relative to
Breakdown's. The two tabs will show different per-shipment averages for the same selection.

**Why it matters.** Cross-tab inconsistency on a basic metric erodes trust; a user comparing the corridor
average between Overview and Breakdown sees two numbers.

**Fix.** document or refactor. Decide whether "avg cost per shipment" means per-costed-shipment or
per-all-shipments and apply one definition across both routes. If both definitions are intentional, label
them distinctly in the UI.

### H3. Product-grain cost is fanned out by basket size; product-level totals are not additive `[MATH]`
`pipeline.py:1194-1211` (`_explode_products`), `pipeline.py:2397-2422` (daily_product UNNEST),
`breakdown/route.ts:181-184,500`.

`shop_order_groups` is exploded one-row-per-product, and each exploded row carries the **full** shipment
`cost_for_routing`, `shipping_cost`, `revenue`, and `weight_kg` (no division by basket size). So a 3-product
shipment contributes its full cost three times to `daily_product`. `SUM(sum_routing)` at product grain
therefore **triple-counts** that shipment's cost. This is defensible for *attribution* ("which products ride in
expensive shipments") and for *share* computations, but it is wrong if anyone reads a product-grain
`SUM(cost)` as a real total, or sums product rows expecting the corridor total.

The quota math partly launders this: `breakdown-quota` on `daily_product` computes
`SUM(sum_routing)/SUM(sum_revenue)` where **both** are fanned out by the same per-row factor — but only
*within a single basket*. Across baskets of different sizes the inflation factors differ, so the aggregate
product-grain quota is **not** equal to the true shipment-grain quota. It's an approximation, not an identity.

**Why it matters.** Product-tab totals and quotas can diverge materially from the shipment-grain truth,
especially where multi-product baskets dominate. Easy to misread as exact.

**Fix.** document prominently (the fan-out is intentional for attribution but the non-additivity and the
cross-basket quota approximation should be stated where product totals/quotas are surfaced), or refactor to
divide cost/revenue by `n_unique_products` if a true allocation is wanted. At minimum, label product-grain
sums as attribution, not totals.

---

## Medium

### M1. `query_mart_items.sql` joins `dw.dim_products` — outside the `shipping_mart.*` contract `[TECH]`
`query_mart_items.sql:19`.

The items pull `LEFT JOIN dw.dim_products dp ON dp.product_key = oi.product_key`. This reaches outside the
gold mart into `dw.`, which is exactly the cross-schema dependency the cutover was supposed to eliminate.
The file's own `TODO` (`query_mart_items.sql:10`) acknowledges it: *"replace dw.dim_products with mart-native
product dim when available."* It's a LEFT JOIN so a missing `dw` row yields NULL sku/articlenumber/sog (those
rows are then dropped by the `is_not_null()` filters in `_build_baskets_from_items`, `pipeline.py:373,383`),
not a fan-out — but it is a scope violation that couples basket-building to a non-mart table and to its refresh
cadence.

**Fix.** document (known TODO) / verify-with-data that `dw.dim_products` coverage of `product_key` is ~100%,
since silent NULL → those products vanish from baskets and from the entire product tab.

### M2. Hardcoded date floors scattered across pipeline + SQL `[TECH]`
`pipeline.py:70` `ANCHOR = date(2025,1,6)`, `:258` `FULL_DATE_FROM = "2024-01-01"`, `:3713` filter_combos
`>= 2025-01-01`, `query_mart.sql:93` / `query_mart_items.sql:20` `{DATE_FROM}` substitution.

Several independent date floors. `ANCHOR` (week alignment, `transform` L573-579) is a fixed Monday; period
indices are computed relative to it (`period_idx = (order_date - ANCHOR)//7`, `:576`). Orders **before**
`ANCHOR` produce negative `period_idx` and a `period_start` before the anchor — fine arithmetically, but any
consumer assuming non-negative period indices could misbehave. `filter_combos` silently restricts the sidebar
to 2025+ (`:3713`) while data goes back to 2024 — a corridor that only shipped in 2024 won't appear in the
sidebar even though it's in `processed/`.

**Fix.** document the 2025+ sidebar floor (it's an intentional perf/relevance cut but invisible to users) and
verify no consumer assumes `period_idx >= 0`.

### M3. `str.split(" | ")` / `string_split(..., ' | ')` over-splits any product name containing " | " `[TECH]`
`pipeline.py:1201`, `pipeline.py:2406`, `breakdown/route.ts:183,500`.

`shop_order_groups` is a `" | "`-joined string built at `pipeline.py:378`. Both the Polars explode and the
DuckDB UNNEST split on the literal `" | "`. If any `shop_order_group` value itself contains `" | "`, it splits
into phantom products, inflating product count and mis-attributing cost. The join is on the same delimiter so
it round-trips *unless* a value contains the delimiter. Pure data risk, low likelihood, but unguarded.

**Fix.** verify-with-data (check for `' | '` inside any single `shop_order_group`); if possible use a delimiter
that can't appear in the data, or store the basket as a list column rather than a delimited string.

### M4. Bucket `fill_null(0)` only guaranteed on the full-pull path; cache/refresh-merge path relies on it being already-persisted `[TECH]`
`pipeline.py:450-461` (full pull casts + `fill_null(0)`), `:480-489` (refresh merge reads cached `raw.parquet`),
`:415-421` (cache path reads `raw.parquet` directly).

The `fill_null(0.0)` on buckets (`:460`) and the float8 casts (`:453-459`) are applied in the
`_pull_query_chunked` → `with_columns` block that runs only on a fresh pull. The `refresh` path concatenates
freshly-pulled rows with cached rows from `raw.parquet` (`:483-486`), and the `cache` path reads `raw.parquet`
straight (`:419`). This is correct **iff** every `raw.parquet` was written by a run that applied the fill. If an
older `raw.parquet` predates the bucket columns or the fill, `diagonal_relaxed`/`vertical_relaxed` concat
(`:486`, `:3703`) will reintroduce NULL buckets, which then sum oddly downstream. The `_pull_query` per-chunk
cast (`:288-290`) covers dtype but **not** the null→0 fill. Fragile coupling between persisted-file vintage and
in-memory assumptions.

**Fix.** refactor — apply the bucket `fill_null(0)` defensively in `transform` or right before
`_write_daily_summary`, so it doesn't depend on which path produced `raw.parquet`. (Also note `transform`
itself never re-fills, and `df_sum` is rebuilt from `processed/*.parquet` at `:3701-3704`, one more hop where a
stale vintage could leak NULLs.)

---

## Low

### L1. `_decat` / categorical round-trip is correct but `sum_expected` quietly absorbs ORWO NULLs `[MATH]`
`pipeline.py:2335`, `:2414`.

`sum_expected = SUM(expected_shipping_cost)`. Per `query_mart.sql:37-42`, ORWO rows arrive with NULL
`expected_shipping_cost`. Polars/DuckDB `SUM` skips NULLs, so `sum_expected` is a sum over only the rows that
*have* an expected — but `avg_exp = sum_expected / SUM(shipments)` (`overview/route.ts:185,206`) divides by
**all** shipments. For a corridor that is partly ORWO (no expected), `avg_expected` is diluted toward 0. Same
shape as H1/H2 (numerator population ⊂ denominator population), lower impact because expected cost is a
secondary reference metric, not a headline KPI.

**Fix.** document, or divide by the count of rows with non-null expected if a true average is wanted.

### L2. `transform` drops null-trackingnumber rows using `date.today()`, not `effective_today()` `[TECH]`
`pipeline.py:554`.

`cutoff = date.today() - timedelta(days=14)` uses the real clock, while the rest of the pipeline honors
`SIMULATE_DATE` via `effective_today()` (`:239-241`, used at `:330,430`). Under `--simulate-date`, the 14-day
null-trackingnumber drop is computed against the wrong "now," so a simulated historical run drops a different
row set than the real run would have at that date. Backtests/simulations are subtly non-faithful.

**Fix.** fix-now — use `effective_today()` at `:554` for consistency with the rest of the simulation plumbing.

### L3. `pcs_orderid` cast `strict=False` can silently null-coerce non-int order ids `[TECH]`
`pipeline.py:452`.

`pl.col("pcs_orderid").cast(pl.Int64, strict=False)` turns any non-integer-parseable id into NULL without a
count or warning. Not cost math, but `pcs_orderid` is a join/identity key; silent NULLing could drop or
mis-group rows downstream. Low because the mart should emit clean ints.

**Fix.** document / add a count of coerced-to-null ids if any.

---

## Verified correct (checked, found sound)

- **Reducer-bucket signs** are handled correctly everywhere I checked. `discounts_eur`/`credit_note_eur`
  arrive negative (`query_mart.sql:24-26`) and are summed with `+`/plain `.sum()` (no `abs()`), so they reduce
  totals as intended: `pipeline.py:2330` (`pl.col(c).sum()`), `breakdown/route.ts:49` (`COALESCE(b,0)` joined
  by `+`), per-bucket sums at `breakdown/route.ts:158,383`. No sign error found.
- **Division-by-zero guards** are present on every quota/average denominator I reviewed: `NULLIF(..., 0)` at
  `overview/route.ts:148,150,152,153,184-187,204-216,369`; `breakdown/route.ts:200,208,237,249,265,266,276,
  298-300,308-310,331,332,406,413,417,421,447,448,460,464,524,555-560`; `breakdown-quota/route.ts:81,82`;
  `avg-costs/route.ts:58,59,60`. The deviation engine guards expected-cost denominators with explicit
  `expected_shipping_cost > 0` filters (`pipeline.py:1418-1419,2276-2277`).
- **Quota population pairing (the headline pair).** `combined_cost_quota = SUM(sum_routing)/SUM(sum_revenue)`
  is consistently all-rows/all-rows (`overview/route.ts:152,215`, `breakdown-quota/route.ts:82`). That pairing
  is internally consistent (the broken pairing is the *real* quota — see H1).
- **Weighted aggregation pattern (no avg-of-avg).** The daily summaries persist `SUM(numerator)` + `SUM(count)`
  separately (`pipeline.py:2331-2348`), and every downstream average recomputes `SUM(num)/SUM(count)` rather
  than averaging stored averages (`overview/route.ts:148-153,184-187,204-216`, `avg-costs/route.ts:58-60`,
  `breakdown-quota/route.ts:81-82`). Roll-ups to weekly/monthly via `DATE_TRUNC` are therefore correctly
  volume-weighted. No averages-of-averages found in the surfaces reviewed.
- **Basket left-join grain.** `_build_baskets_from_items` (`pipeline.py:360-394`) aggregates items to one row
  per `shipment_id` *before* joining to the shipment spine (`:481`, `:503-512`), so the basket join cannot
  fan out the shipment grain. The items SQL pre-aggregates `GROUP BY 1,2,3,4` (`query_mart_items.sql:22`) for
  the same reason. No fan-out on this join.
- **Float8 server cast rationale.** The Decimal→float8 cast claim (`query_mart.sql:31-35`) is consistent with
  the pipeline's defensive re-casts (`_pull_query:288-290`, `pull_raw:453-460`) and the documented Polars
  null-Decimal schema-inference failure (`_pull_query` docstring L268-274). The reasoning holds; precision loss
  from float8 on EUR amounts is sub-cent and below the ROUND(...,2) display precision used everywhere.
- **`cost_for_routing` derivation** is a clean pass-through of `shipping_cost_final` (`pipeline.py:568`), with
  no hidden COALESCE — matches the post-cutover contract in `query_mart.sql:59-61`. NULL final = uncosted,
  carried as NULL (not 0), so it correctly drops out of `SUM` while still counting in `shipments`.

---

## Could not determine from static reading (needs a data query)

1. **Does `real_shipping_cost_eur` (→ `shipping_cost`) ever take values ≤ 0 when non-null?** Decides whether
   H1 is live or benign. (Query: `SELECT count(*) FROM shipping_mart.fact_shipments WHERE real_shipping_cost_eur <= 0`.)
2. **The C1 invariant in current data.** Count rows where `real_shipping_cost_eur > 0` but no
   `fact_shipment_cost_summary` row exists (buckets→0), and rows where `abs(total_eur - real_shipping_cost_eur) > 0.01`
   or `abs(sum_11_buckets - total_eur) > 0.01`. The "Q1 2025, ~1M rows" claim is pre-cutover and unverified on this branch.
3. **Fraction of uncosted shipments per corridor** — sizes the H2 Overview-vs-Breakdown avg_cost divergence.
4. **`dw.dim_products` coverage of `oi.product_key`** (M1) — null coverage = products silently missing from baskets.
5. **Whether any `shop_order_group` value contains the literal `" | "`** (M3 over-split risk).
6. **Multi-product basket prevalence** — sizes the H3 fan-out distortion on the product tab.

# SCM Breakdown tab — cost is cost-basis-driven, not bucket-driven (2026-06-12)

**Change ([[S227_6f393689_scm-breakdown-cost-basis-fix|S227]], commit `d70e516` on bi-analytics-main `main`).** The SCM Breakdown provider/dimension table previously derived cost from `SUM(11 charge buckets)`. Buckets only exist on **invoiced** rows (invariant: buckets sum to `real_shipping_cost_eur`, null until the invoice lands), so:
- un-invoiced carriers (e.g. DB Schenker on invoice lag, 0% invoiced) read **€0** total/avg despite real cost in the Overview chart;
- any sub-100%-invoiced carrier had its avg **diluted** (invoice-bucket-sum ÷ all-row count).

**Now** the Breakdown table cost is cost-basis-driven, matching the Overview chart:
- `final` → `cost_for_routing` (`COALESCE(invoiced, expected)`), over all costed rows;
- `invoiced` → `shipping_cost`, invoiced rows only (`has_cost`).

Breakdown-`final` avg now equals Overview-`final` by construction (both `SUM(cost_for_routing)` ÷ costed-row count; bd_cache + processed both filter `cost_for_routing IS NOT NULL`).

**Bucket decomposition** is no longer in the Breakdown table. It lives only in the `BucketsTrend` chart (its own clickable legend + `/api/breakdown-buckets` route, already decoupled). The charge-bucket filter was removed from the Breakdown sidebar (`TAB_FILTERS`, the only tab that carried it).

**Files:** `src/app/api/breakdown/route.ts` (cost expr in `buildLevelQuery` + `buildTotalQuery`), `src/lib/types.ts` (`TAB_FILTERS`), `src/components/BreakdownTab.tsx` + `src/app/page.tsx` (dead `onBucketTotalsChange` plumbing).

**Follow-up:** dead `buckets` param + `bucketSumExpr()` left in `breakdown/route.ts` (tsc-clean) — optional prune.

Relates to [[scm]] (domain digest), which still describes the table cost as bucket-driven — reconcile at next alching/bankstanding.

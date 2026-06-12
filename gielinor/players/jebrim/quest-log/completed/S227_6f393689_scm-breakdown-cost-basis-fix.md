# S227 — SCM Breakdown tab: de-bucket the cost (DB Schenker €0 fix)

**Player:** Jebrim · **sid8:** 6f393689 · **Date:** 2026-06-12

## Ask

Why does DB Schenker (DBSCHENKERPLEUHOME) show €0 Total Cost / €0.00 Avg in the SCM Breakdown provider table while the trend chart plots real invoiced + final cost? Then: rethink it — remove the charge-bucket filtering from the Breakdown tab so cost is a clean cost-basis number; keep bucket investigation in the Buckets chart.

## Root cause

The Breakdown table cost was **bucket-sourced** — `SUM(11 charge buckets)` from `fact_shipment_cost_summary`. Buckets only populate on **invoiced** rows (invariant: buckets sum to `real_shipping_cost_eur`, null until invoice lands). So:
- A fully un-invoiced carrier (DB Schenker, 0% invoiced in the window — invoice lag) → all buckets 0 → **€0 total/avg, on either toggle setting**.
- Any sub-100%-invoiced carrier → avg diluted (invoice-bucket-sum ÷ all-row count). DB Schenker's baseline €14.63 vs the chart's ~€42 was exactly this dilution.
- The chart (Overview / CostTrend) uses `cost_for_routing = COALESCE(invoiced, expected)` → carries the modelled estimate → shows real cost. Two surfaces, two different cost definitions.

## Fix (per Niklavs' design call)

De-bucket the Breakdown table cost → **cost-basis-driven**, same columns the Overview uses:
- `final` → `cost_for_routing` (all costed rows)
- `invoiced` → `shipping_cost` (invoiced rows only, `has_cost`)

Design fork resolved via AskUserQuestion → **"Remove the charge-bucket filter from the Breakdown entirely"** (not keep-for-charts). Bucket slicing lives only in `BucketsTrend` (own legend, own `/api/breakdown-buckets` route — already decoupled).

Files (4): `breakdown/route.ts` (cost expr swap in `buildLevelQuery` + `buildTotalQuery`), `types.ts` (drop `buckets` from Breakdown `TAB_FILTERS`), `BreakdownTab.tsx` + `page.tsx` (remove dead `onBucketTotalsChange` plumbing). Net −6 lines.

## Verification

- `tsc --noEmit` clean.
- Real-data reconciliation (duckdb-async on local processed parquet, Apr+May 2026): DB Schenker **OLD bucket avg = €0.00** (reproduces the bug) → **NEW final = €53.12** over 3,040 costed rows; invoiced = 0 rows / 0% (correct, no invoices). DHL final €3.38 ≈ invoiced €3.35 (89.9% invoiced — no dilution where coverage is high). Breakdown-final formula now equals Overview-final by construction.

## Correction this session (high-signal)

**Edited the wrong checkout first.** Made all 4 edits in `bi-analytics/` (branch `scm-alerts-entity-split`, stale build) — but Niklavs builds/deploys from `bi-analytics-main/` (branch `main`). His `npm run build` still showed the bucket filter + inert toggle. Re-ported every edit to `bi-analytics-main`. The keepsake/memory note "SCM dashboard local setup: run from bi-analytics-main" was the tell I should have used before picking the tree. → examine draft + memory.

## Ship

- `bi-analytics-main` commit **d70e516** on `main` (4 files, pathspec commit per [[D-024_scope-git-commits-with-pathspecs-parallel-sessions|D-024]] — sibling EU-tender work in the tree, not swept).
- Pushed: `origin/main` now `9d171a2` (parallel session's EU-tender commit was the tip; d70e516 is its ancestor → included). CI "Deploy Shipping Costs Dashboard #25" runs on the push; run is named after the tip commit, not the fix.
- Push hung initially on the Git Credential Manager account-selection popup (a background push can't surface the GUI); resolved when Niklavs selected the account interactively.

## Loose ends (optional follow-ups)

- Orphaned duplicate edits remain **uncommitted** in `bi-analytics/` (`scm-alerts-entity-split`). Offered `git restore`; not actioned.
- Dead `buckets` param + `bucketSumExpr()` left in `breakdown/route.ts` (tsc-clean, no lint enforced). Optional prune.

## Pending external actions

None pending (brain). CI deploy #25 triggered by the push runs GitHub-side; not brain-tracked.

## Harvest

- bank draft: `bank/drafts/notes/projects/2026-06-12-scm-breakdown-cost-basis-not-buckets.md`
- examine draft: `examine/drafts/2026-06-12-verify-which-checkout-is-live-before-editing.md`
- memory: `feedback_verify_live_checkout_before_editing.md` (generalizes the wrong-tree edit)

## Cascade

None — external-repo work; no brain-rule or cross-file change.

## Main-brain changes

None.

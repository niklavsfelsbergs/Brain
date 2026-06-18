---
quest: S266_e455d12d_orwo-box-grain-quota-estimator
sid8: 64902bef
ts: 2026-06-18 (continuation of S266; supersedes resume__e455d12d, now archived)
open_dep: Phase 1 BUILT — bi-etl SQL written + HTML explainer done + acceptance tests passed live. Awaiting: Niklavs reads fix_explainer.html, then HE commits bi-etl (pathspec) + pushes. bi-etl change is UNCOMMITTED on purpose.
---

# ORWO cost/quota over-read → box-grain estimator

## The ask (Niklavs, 2026-06-18)
SCM shows a big ORWO avg-cost + quota rise May/Jun. Frame: **real cost drivers**, go to **raw
invoices to strip distribution**, scope **UPS + DE**. Then: design a fix so the **quota represents
reality**, and **build it in an NFE topic to test the May/Jun quota prediction**.

## How ORWO cost is built (bi-etl)
- `final_shipping_cost_eur = COALESCE(real, expected, avg)`.
- **Real / bulk-mail distribution** (`shipping_mart/fact_shipment_invoice_lines/sql/providers/{ups,dhl}_orwo.sql`,
  NGE-6129 Step 5): ~20.7% of ORWO trackings are bulk-mail manifests (many parcels, one box, one
  carrier charge). ETL `DENSE_RANK`s by ORWO `sentat DESC`, keeps parcels tied at latest sentat =
  `share_n`, splits charge `charge/share_n`. `share_n` NOT stored → reconstruct = parcels-per-tracking.
- **Expected** (`fact_shipment_cost_summary/sql/update_fact_shipments_cost.sql`): Pass 2a.5 flat
  per-country carrier rate (UPS DE €6.15) + seasonal lift; Pass 2a.6 dynamic calibration
  `AVG(real)/AVG(expected)` per (keyaccount, carrier). It's a **flat per-parcel scalar** — consolidation-blind.

## Verdict: no real UPS DE rate increase
Raw `enterprise_silver.ups_orwo_invoices` (DE, ex-VAT, tcg_nfe): per-**box** billing flat ~€5.30/trk,
€/kg +6% Mar→May. The dashboard spike is **invoice-maturity selection bias** + estimate over-pricing.

## Key mechanism findings (all on UPS-DE, order-month, gold mart)
- Per-parcel cost = box-charge ÷ parcels-in-box → ranges **10×** (solo €5.74–7.96 / 6+ €0.58).
- **Bulk-mail manifests bill LATE.** Mature April: invoiced 4.95 parcels/box → €1.13/parcel. Immature
  May/Jun: bulk still in `expected` (4.8/5.4 parcels/box waiting); invoiced subset = solo parcels
  (2.13/1.22) → inflated real per-parcel (€2.71/€4.51).
- **Quota is grain-INVARIANT in aggregate** — per-parcel distribution conserves total cost, so
  SUM(cost)/SUM(rev) is identical per-box or per-parcel. The over-read is NOT the allocation; it's
  (1) coverage immaturity + (2) estimate bias. Revenue is complete at order time (no offset).
- Dashboard reproduced exactly: whole-ORWO final quota Feb 13.0 / Mar 17.1 / Apr 15.5 / May 16.6 /
  Jun 18.3. Invoiced-quota (billed÷billed-rev): May 13.3 (≈KPI 13.2). Gap = the estimate.

## THE DESIGN (Niklavs' idea, validated): box-grain estimate → distribute
`expected_parcel = box_rate(carrier, zone) ÷ parcels_in_box`. Mirror the real path: estimate the
BOX (stable), distribute by parcels-per-box. Dividing by observed parcel count IS the consolidation
adjustment — no tier table. Conserves, keeps per-shipment grain, swaps to real seamlessly.
- **Box rate is ~6× more stable than per-parcel.** Cost-per-box ~€5–8 regardless of size (bulk-mail =
  flat rate per manifest). May box rate €5.2–5.9 across ALL sizes.
- **Residual lever = freshness** (not consolidation): box rate moves €7.5 Mar → €5.5 Apr/May (~30%
  month-to-month) → calibrate from most recent mature month, refresh each cycle.
- **Nuance:** small boxes (2–3) are bimodal/noisy (shared-tracking is a fuzzy box proxy for pairs);
  reliable for solo + 6+ bulk (the volume). Low-volume noise washes out in aggregate.
- weight/dims/packagetype are ~77% NULL for ORWO → no weight-aware estimate possible; box-size is it.
- Sizing (UPS-DE, box-aware vs flat): May €54.6k→€49.2k (quota 24.0→21.6), Jun €54.7k→€39.5k (26.2→18.9).
- Per-parcel estimator out-of-sample (train Mar→predict Apr) over-predicts 46% — because RATE LEVEL,
  not structure, dominates. Confirms freshness is the real lever.

## The build (NFE topic 50, in progress)
`bi-analytics-main/NFE/shipping_topics/50_orwo_box_grain_quota_estimation/` — shape like topic 47
(build_data.py + sql/ + data/ + findings.md). Pull ORWO parcels (Feb–Jun) via `shared.database`,
do box-grain modeling in polars: calibrate box_rate per (carrier_family, country) from a mature
month, predict May/Jun whole-ORWO quota, validate out-of-sample on the clean UPS-DE slice.
SQL in sql/ (user rule). Commit asked separately; never push.

## Validator quirks (this redshift MCP)
alias `lines` reserved; positional GROUP BY flaky; `SIMILAR TO`, `STDDEV`/`STDDEV_SAMP`, CTE-JOIN-of-
aggregates all rejected → use `~` regex, explicit group exprs, AVG(x*x)-AVG(x)^2 for variance, chain
CTEs not joins.

## PHASE 1 BUILT (continuation session, sid 64902bef, 2026-06-18)

**Done this session — all 5 plan steps:**
- **Step 1+2 (SQL + box_n/share_n):** wrote real `Pass 2a.5b` in `bi-etl/.../update_fact_shipments_cost.sql`
  (4 temps: trainmonth auto-pick / boxes / boxrate cell+fam / boxgrain; UPDATE mirrors Pass 2a.5).
  Resolved box_n-vs-share_n LIVE: DHL fully uniform (box_n==share_n), UPS ~16% within-box split, but
  `box_rate/box_n` sums to box_rate per box so it's **immaterial to any aggregate** — kept plain box_n
  scoped to (order_month, trackingnumber). Cross-month tracking reuse = 8.3% → month-scoping handles it
  (the skeleton's plain-trackingnumber grouping was a bug; fixed). Calibration window = **most-recent
  fully-mature month per family (>=60% inv)** → DHL=May, UPS=April (auto-rolls; freshness lever).
- **Step 3:** Pass 2a.6 now excludes UPS+DHL (calib CTE + apply UPDATE) — no double-correct.
- **Step 4 (acceptance, READ-ONLY live mart):** whole-ORWO quota reproduced topic-50 to ~0.1pp —
  Mar 17.06→17.15, Apr 15.54→15.64, May 16.58→16.40, **Jun 18.28→16.40**. Mature months ≤0.1pp (no
  distortion). June per-family: UPS €55.2k→€40.5k (driver), DHL ~flat (real), POST €39.4k held, OTHER
  held. Tests 1-5 pass (mature self-consistency / immature drop / POST+OTHER zero-change / conservation /
  regression). MCP quirk hit: multi-ref CTE → "transaction is read-only" (CTE materialized as temp);
  rewrote with independent inline subqueries.
- **Step 5:** `fix_explainer.html` built in topic 50 — self-contained single file (CSS bar chart, no CDN
  dep), topic-35 style tokens (dark + orange), ASCII-only (no mojibake). Story: wrong → why → fix →
  before/after → carrier cut → OOS validation → ETL change → risks + decisions.

**REMAINING — Niklavs' action (do NOT do for him):**
1. Open `bi-analytics-main/NFE/shipping_topics/50_orwo_box_grain_quota_estimation/fix_explainer.html`, review.
2. Decide the 3 open questions (calibration window; deploy ETL vs SCM-preview; POST contracted rate).
3. He commits the bi-etl change (pathspec on `update_fact_shipments_cost.sql`) + pushes. **bi-etl is UNCOMMITTED.**
4. (optional) commit topic-50 HTML to NFE — offered, awaiting his go.

---
## (original plan, for reference) NEXT SESSION — Phase 1 (implement) + HTML explainer

**Goal:** turn the validated design into a tested bi-etl change + a self-contained HTML doc that
explains the fix to Niklavs. **He reviews the HTML BEFORE any push. Do NOT push — push is his action.**

**Read first (in order):**
1. This resume.
2. `bi-analytics-main/NFE/shipping_topics/50_orwo_box_grain_quota_estimation/` — `findings.md`,
   `bi_etl_implementation_plan.md`, `build_data.py` (the validated prototype + data/ parquets).
3. `bi-etl/dags/shipping_mart/fact_shipment_cost_summary/sql/update_fact_shipments_cost.sql`
   (Pass 2a.5 / 2a.6 — **`git pull origin main` in bi-etl first**, verify line numbers vs HEAD).
4. `bi-etl/dags/shipping_mart/fact_shipment_invoice_lines/sql/providers/ups_orwo.sql` +
   `dhl_orwo.sql` — for the real `share_n` (sentat-tie + msk) logic, to resolve step 2 below.

**Steps:**
1. **Write the REAL Pass 2a.5b SQL** (not the plan's skeleton — it has a literal placeholder). Mirror
   Pass 2a.5's `tmp_*(shipment_id, expected_eur)` temp shape (Redshift equijoin rule). Three temps:
   box_n per tracking, box_rate per (family,country) from a recent mature window (≥30 boxes, family
   fallback), overwrite expected for un-invoiced UPS+DHL ORWO with `box_rate/box_n`.
2. **Resolve box_n vs share_n** (the one correctness risk). My prototype's box_n = plain parcels-per-
   tracking; the real path distributes by sentat-tie + map_shipment_key. Quantify divergence; if
   material, reuse `ups_orwo.sql`'s `od_sentat` tie logic so the estimate's box size matches the real.
3. **Modify Pass 2a.6** — add `AND extkey NOT LIKE '%UPS%' AND extkey NOT LIKE '%DHL%'` to its calib +
   apply WHERE (box-grain IS their calibration; else double-correct).
4. **Run the 5 acceptance tests** (in the plan) against a CLOSED month + the live month: mature-month
   self-consistency, immature-month quota drop (whole-ORWO Jun ~18.3→16.3), zero change to POST/OTHER,
   box conservation, historical regression. Run via the Redshift MCP (tcg_nfe) or a topic-50 script —
   READ-ONLY validation; do NOT write to the live mart.
5. **Build the HTML explainer** (self-contained, single file, plotly-offline or static — Niklavs'
   finance/ops register, plain language): the story in order — what's wrong (immature quota over-read,
   the Jun 18.9% on 22% real cost) → why (bulk-mail bills late + flat estimate over-prices bulk) →
   the fix (box_rate ÷ box_n, mirror the real path) → before/after quota chart (dashboard vs box-grain,
   Mar–Jun) → validation (beats flat OOS; ~30% freshness bound) → what changes in the ETL (Pass 2a.5b +
   the 2a.6 exclusion; POST/OTHER untouched) → risks + what POST still needs. Put it in topic 50
   (`fix_explainer.html`). Match an existing topic's HTML style if reusing tokens.
6. **Hand to Niklavs to review the HTML**, then HE commits the bi-etl change (pathspec) and pushes.

**Scope reminders:** Phase 1 = ORWO UPS+DHL only. POST (€82k/mo, 99% est) needs a contracted rate
(Phase 3, separate). Picturator+Wolfen = Phase 2. NFE commits under standing authorization; bi-etl
changes Niklavs reviews+pushes. Don't promote the bank/examine drafts (alch).

# Skill — running the automated shipping report

**Draft.** Source: [[S124_61d62e21_shipping-agent-report|S124]]. The weekly/daily senior-analyst review of shipping. This is the durable artifact — the *method*; the data, code, and accumulating memory live in the project folder `bi-analytics-main/NFE/projects/4_automated_shipping_report/`. The brain keeps this skill + a keepsake pin + a bank pointer.

## What it is (and is not)

A **senior data analyst checking if everything is in order in shipping** — run on a cadence. It is **not** a rules/threshold engine. The deterministic harness *prepares evidence* (standard analytical cuts) and *ranks attention* (biggest movers, outliers, mix shifts); it makes **zero verdicts**. The "is this an issue?" call is the analyst's judgment, fresh every run, gated by the running notebook + a materiality bar.

Why not thresholds: too much varies in shipping (mix, weight, zone, fuel, season, one-offs) for a fixed bar to decide what's an issue. Mechanizing that judgment was the rejected S1 design — see [[2026-06-01-dont-mechanize-judgment-in-analytical-reports]] and the principal reframe in the S124 quest-log Session-2.

## The core insight — two event streams

"Everything in shipping" is two distinct streams:

1. **Shipments that *moved*** — ship-date filtered (anchor `shop_order_created_date`). Easy.
2. **Cost *information* that *arrived*** — late invoices, silent restatements, refunds, `expected→invoice` flips — on shipments that may have moved weeks ago. *Arrival*-filtered, not ship-date. **The valuable, easy-to-miss half.**

Stream 2 is invisible to a naive "last week's shipments" query, and the mart's load dates can't reveal it (`fact_shipments` / `fact_shipment_cost_summary` **truncate-reload**, resetting every load timestamp). So we keep a **daily snapshot** of the trailing cohort and **diff** successive snapshots. Snapshot-diff is the only mechanism that catches silent restatements.

## Two tiers (one snapshot spine feeds both)

- **Daily (small, cheap, the automatable one):** pull today's snapshot → diff vs yesterday → "what cost arrived" + a **DQ canary**.
- **Weekly (big, judgment-heavy):** the full analyst memo, reasoning over the week's accumulated snapshots. Carries the §3 review and the one opportunity (§4); daily does not.

## Running it — the harness

Project: `bi-analytics-main/NFE/projects/4_automated_shipping_report/`. The **shipping-agent operates the harness** (it holds the mart contract + DQ quirks); call it per [[calling-the-shipping-agent]]. Connection is full-access `tcg_nfe` from `NFE/.env` (gold by default, raw reachable for §5), connectorx `protocol="cursor"`.

```
python lib/pull_snapshot.py --window-days 120          # writes snapshots/snapshot_YYYY-MM-DD.parquet
python lib/diff_snapshots.py --prev snapshots/snapshot_<T-1>.parquet \
                             --curr snapshots/snapshot_<T>.parquet
```

**Snapshot spine** = 25 cols, 1 row/shipment, trailing 120d by `shop_order_created_date`: 8 keys/dims (`shipment_id`, `shop_order_created_date`, `source_system`, `production_site`, `destination_country_code`, `shipping_provider_group`, `shippingprovider_extkey`, `cost_source`) + `expected`/`real`/`final`_shipping_cost_eur + `net_revenue_eur` + `billed_weight` + 12 charge buckets (excl `truck_charges_eur`). ~49 MB/day. **Segment is derived in the harness, not stored** — so a segmentation change never reshapes history.

**Diff event taxonomy** (per `shipment_id`, T-1 → T; default flags `--restate-abs 0.50 --restate-pct 0.05`):

| event | meaning |
|---|---|
| `COST_ARRIVED` | `cost_source` expected/avg/NULL → invoice (headline late cost) |
| `COST_RESTATED` | was invoice, `real_shipping_cost_eur` moved ≥ abs **and** ≥ pct (snapshot-only signal) |
| `CREDIT_REFUND` | `credit_note_eur` / `discounts_eur` newly non-zero or grew more negative — a **candidate**, read against the refund map (below), not an auto-alarm |
| `COVERAGE_REGRESS` | invoice → expected/avg/NULL (a reload un-matched a cost) |
| `NEW` | present T, absent T-1 |
| `AGED_OUT` | dropped past the window (informational) |

Use **explicit presence flags** in the diff — never infer row existence from a nullable cost column (uncosted rows have NULL `cost_source`/`real`). Cast EUR cols to Float64 before ratio/delta math (Decimal scale overflow). Both lessons cost a bug each — see [[2026-06-01-verify-diffs-both-ways-and-explicit-presence-flags]].

**Nullable-column aggregate trap (cost a third bug, S124-S5):** `(cost_source == 'invoice').mean()` is **not** "% invoiced" — `cost_source` is nullable (~3% NULL uncosted rows), the equality propagates NULL, and polars' `.mean()` drops nulls from the denominator → the % inflates (ORWO read 77.2% vs true 71.9%). Always `.fill_null(False)` before aggregating a boolean over a nullable column. Caught only because §1 and the by-carrier table computed the same number two ways and disagreed — **render load-bearing figures two ways and check they agree** ([[2026-06-01-cross-check-two-derivations-catches-self-bugs]]).

## Segmentation (scope gating)

- **ORWO** = `source_system='ORWO'` (own segment; always `production_site='Wolfen'`).
- **TCG** = `source_system IN ('Picturator','PicaAPI')`, split by `production_site` → **PCS PL / PCS CMH / Wolfen / Other**. PCS `source_system` (~770/90d) is cost-only — excluded from the TCG headline. `PCS CMH` is a real US site (Camp Hill), not a typo.
- **TCG-Wolfen ≠ ORWO segment** — both print at Wolfen physically but are different source-systems; keep distinct.

## The report arc — descriptive → evaluative → prescriptive

- **§1 — State of play (orientation).** Last period's new shipments per segment: volume, % invoiced, final cost, cost/parcel, carrier mix, WoW delta.
- **§2 — Costs that arrived (the diff, the valuable half).** € newly invoiced, `expected→invoice` flip count, net € restatement, refunds/credits, coverage change. From the diff event table.
- **§3 — Is everything in order? (the review — the analyst's judgment).** The biggest movers/outliers the harness ranked, each carrying *reasoning* + a *recommended look-into*, hedged honestly. This is judgment, not a verdict the harness produced. Gated by the running notebook + materiality.
- **§4 — One opportunity (weekly only).** Exactly **one** sized cost-reduction lead per run, **PAPER vs DEFENSIBLE** honesty-tagged. Size it against the expected-cost noise floor (§5) — don't sell a mirage ([[S132_32ff1025_shipping-savings-routing-optimization|S132]] re-rating discipline: trust-gate, capability-check, engine-noise-floor before claiming a number).
- **§5 — Expected-cost health (at the END).** Expected vs actual gap as a **re-estimation signal**, not an operational alarm. Current normals: TCG under-estimates +5–8% (fat upper tail, ~15% materially mis-estimated); ORWO poorly per-shipment calibrated but near-irrelevant in € (~€1/parcel). §5 reads "lift the TCG expected baseline + widen surcharge allowance; reshape the ORWO model."

## The daily DQ canary

The daily tier's load-integrity check — distinct from the analyst review. Flags:

- **Zero-row segment** = a load silently failed (the headline canary).
- **Coverage regression** = % invoiced dropped materially within a segment **by carrier** (see ORWO note below).
- **Null spikes** in key dims/costs; **stale reload** (snapshot unchanged when it shouldn't be).

A canary flag is a *DQ* alarm (is the data trustworthy?), separate from §3's *analytical* judgment (is the shipping picture in order?).

## Running-notebook discipline (the false-positive guard)

`notebook/running-notebook.md` accumulates **what's normal here** + **accepted standing states**. Read it every run *before* forming §3 judgments; append (dated) when a new normal is learned. Standing accepted states already seeded (do NOT re-flag):

- **ORWO is ~72% invoiced, not ~0%** — the "POST structurally ~0% covered" caveat is about the **POST carrier slice within ORWO**, not the segment (`dhl_orwo`/`ups_orwo` ARE invoiced). Track % invoiced **by carrier within ORWO**.
- **Wolfen 54% invoiced is segment-normal**, not a regression.
- **FedEx `discounts_eur` large-negative on ~every invoice** is structural ("Performance Pricing"/"Discount") — only a *rate change* is a signal, not its presence.
- **db_schenker = 100% `unclassified` bucket by design** (no consistent charge descriptions) — not a DQ gap.
- **UPS / DPD-UK refunds are "refund-in-place"** — a negative in a *normal* bucket (fuel/oversize/base) is a legit reversal, not corruption.

## Refund map (carrier-aware credit reading)

`CREDIT_REFUND` and any negative-line reading is carrier-specific — see `shipping-agent/reference/known-dq.md` → "Refund / credit location by carrier". Three mechanisms: **fedex** `discounts` (structural, not an event); **ontrac/yodel** `credit_note` (genuine refund events); **ups/dpd_uk** refund-in-place (negative keeps its original cost bucket). The canary must not mis-flag a legit refund as a cost anomaly.

## Baked-in caveats (cost-basis discipline)

Disclose **% invoiced per segment every run** — an uninvoiced segment's "no movement" ≠ stability, it's absence of data. `expected→invoice` is the dominant cost-arrival signal. Restatements are caught **only** by snapshot-diff. (Mirrors the shipping-agent `how_to.md` §0.)

## Output + cadence open items

- **Output form:** dated per-run folder `reports/YYYY-MM-DD/`, markdown default; email/Slack delivery folds into the (deferred) triggering conversation.
- **Triggering** is deliberately deferred — design the approach first.
- **Noticing thresholds** for ranking attention are empirical — tune from accumulated snapshots, kept as harness *ranking* inputs, never as verdict gates.

## Related

- [[calling-the-shipping-agent]] — the agent operates the harness.
- [[savings-investigation-deliverable-shape]] + [[S132_32ff1025_shipping-savings-routing-optimization|S132]] — the §4 opportunity honesty discipline.
- Project: `bi-analytics-main/NFE/projects/4_automated_shipping_report/` (README, lib/, sql/, notebook/).

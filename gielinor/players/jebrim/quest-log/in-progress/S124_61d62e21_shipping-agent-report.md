# S124 — Shipping Agent Report (weekly) — design

**Player:** Jebrim · **Session:** 61d62e21 · **Opened:** 2026-05-29 · **Status:** in-progress (design parked for build)

First scheduled-task design. A **weekly** report on "everything worth noticing in shipping," explicitly **not deterministic** — Jebrim utilizing the **shipping agent** to produce it. The triggering mechanism is deliberately deferred ("first the approach, then how to trigger it").

## The problem reframe (the load-bearing insight)

"Everything in shipping last week" is two distinct event streams:

1. **Shipments that moved last week** — ship-date filtered. Easy.
2. **Cost *information* that arrived last week** — invoiced costs landing, restatements, refunds, `expected→invoice` flips — on shipments that may have moved weeks ago. *Arrival-date* filtered, not ship-date. The valuable, easy-to-miss half.

Stream 2 is why we keep a trailing snapshot and diff it. A naive "last week's shipments" query can't see it.

## Decisions locked this session

- **Mechanism: snapshot-diff** (not native timestamps). Principal: the mart's load dates (`updated_at` / `dw_timestamp` on `fact_shipments` + `fact_shipment_cost_summary`) are untrustworthy because **the tables are truncated and reloaded** — every reload resets them, so they can't mark when a cost actually arrived. Invoice-line load dates equally untrustworthy. Snapshot-diff is the only path that catches silent restatements.
- **Ship/cohort anchor: `shop_order_created_date`** — NOT `received_by_carrier_date` (principal correction: that's carrier-log quality, poor; confirmed in the agent's `known-dq.md` — 100% NULL by design for PCS/Rewallution/ORWO + large Picturator extkey gaps). `shop_order_created_date` is the agent's canonical time axis in every query and is well-populated.
- **Window: 120 days** (principal pick, AskUserQuestion). Generous enough to catch the invoice-settlement tail we can't measure yet; tune down once snapshots reveal real flip-timing.
- **Segmentation:**
  - **ORWO** = `source_system='ORWO'` (its own segment; always `production_site='Wolfen'`).
  - **TCG** = `source_system IN ('Picturator','PicaAPI')`, split by `production_site` into **PCS PL, PCS CMH, Wolfen, Other** (principal pick — 4 buckets, nothing dropped). Note: `PCS CMH` is a **real** site (Camp Hill; PCS sites = CGN/PL/MI/PX/CMH) — principal corrected my suspicion it was a typo for CGN. `PCS CGN` has **zero** trailing-90d volume currently.
  - **TCG-Wolfen ≠ ORWO segment.** Picturator/PicaAPI orders routed to the Wolfen line vs the ORWO photo-lab source-system — both physically print at Wolfen but are different segments. Keep distinct.
  - PCS source-system (~770/90d) is cost-only — excluded from TCG headline.
- **Home: `NFE\projects\4_automated_shipping_report`** (out-of-tree; not scaffolded yet — that's build work).
- **Stable artifact = a skill** (the procedure), with state split out:
  - **Skill** (`players/jebrim/spellbook/skills/`) — the weekly playbook: snapshot columns, diff logic, noticing checklist, §1/§2/§3 scaffold, scope gating.
  - **Snapshot parquets** (`NFE\projects\4_automated_shipping_report\snapshots\`) — the weekly baseline data.
  - **Running noticing-memory** — small file so the same standing condition isn't re-flagged weekly.

## Sizing (ground-truthed via Redshift MCP, gold `shipping_mart`)

- Trailing-90d cohort by `shop_order_created_date` ≈ **1.42M shipments** (ORWO ~570k + TCG ~844k + PCS ~770). (My earlier 739k was an artifact of the wrong anchor — `received_by_carrier_date` NULL-drops most rows.)
- Snapshot grain = 1 row/shipment, ~22 cols (id, dates, source_system, production_site, carrier, cost_source, final/real/expected cost, net_revenue, 11 buckets). Mostly numerics with heavy zeros + low-cardinality strings → parquet crushes it. Est. **~20–40 MB/week**; ~1–2 GB/yr keeping every weekly snapshot. **Size is not a constraint** — design for correctness. Confirm real size by writing one snapshot at build.

## Proposed diff taxonomy (snapshot T vs T-1, per shipment)

1. **COST_ARRIVED** — `cost_source` `expected/avg/null → invoice` (headline late-cost event).
2. **COST_RESTATED** — was `invoice`, `real_shipping_cost_eur` changed (>€X or >Y%). Snapshot-only signal.
3. **CREDIT/REFUND** — `credit_note` or `discounts` bucket newly non-zero/grew.
4. **COVERAGE_REGRESS** — `invoice → expected/null` (a reload un-matched a cost).
5. **NEW** — present T, absent T-1.
6. **AGED_OUT** — dropped past 120d (informational).

## Proposed report scaffold (per segment)

- **§1 Last week's new shipments** — volume, % invoiced, final cost, cost/parcel, quota, carrier mix, WoW delta.
- **§2 Cost movements on trailing 120d** (the diff — the valuable half) — € newly invoiced this week, expected→invoice flip count, net € restatement, refunds/credits, coverage change.
- **§3 Worth noticing** — Jebrim's judgment layer, anchored on thresholds: new cost landed >€X or >Y% of segment; cost/parcel WoW >Z%; bucket share (fuel/peak/oversize/residential) jump >N pp; % invoiced moved >M pp; large single restatement >€K; new carrier.

## Baked-in caveats (cost-basis discipline from agent `how_to.md` §0)

% invoiced disclosed per segment every run; ORWO POST is structurally ~0% cost-covered (no bulk-bill source) so its "no movement" ≠ stability; `expected→invoice` is the dominant signal; restatements caught only by snapshot-diff.

## Open (approach not yet fully closed)

- **Report output form** — markdown in the project folder is my default; email/Slack delivery folds into the (deferred) triggering conversation. Not confirmed.
- **Noticing thresholds** — placeholders (X/Y/Z/N/M/K) need real values, set empirically once a few snapshots exist.
- **`shop_order_created_date` vs `order_produced_date`** as "shipped" — defaulted to the former (agent's canonical axis, reconciles with other shipping numbers); flagged as an assumption to confirm.

## Pending external actions

No pending external actions. (Session was read-only against the mart + brain-side writes only.)

## Turn log

- Grounded in Jebrim keepsake + `calling-the-shipping-agent` skill.
- Reframed the ask into the two event streams; surfaced the snapshot-vs-native-timestamp fork.
- Principal locked snapshot-diff; corrected the ship-date anchor and the load-date distrust rationale (truncate-reload).
- Pulled the agent's own knowledge (`mart-contract.md`, `query-patterns.md`, `known-dq.md`, `sources.md`) + live Redshift probes to ground anchor, scope mapping, and sizing.
- AskUserQuestion → TCG 4-bucket split + 120-day window.
- Proposed diff taxonomy + §1/§2/§3 scaffold; parked at principal's cue as "Shipping Agent Report."

---

## Session 2 — 2026-06-01 (sid 8cb8f235): reframe to a senior-analyst review

Resumed on "where do we stand on the shipping report." Discussion-only, no mart access — advanced the design substantially and re-parked for a fresh build session. Changes from the S1 (2026-05-29) design:

1. **Rules engine → senior-analyst review.** S1 leaned toward threshold/baseline-driven regression detection. Principal corrected: too much varies in shipping (mix, weight, zone, fuel, season, one-offs) for thresholds to decide "what's an issue" — it needs human reasoning on top. New model: the report **is** a senior data analyst checking if everything is in order. The deterministic harness **stops making verdicts** — it *prepares evidence* (standard analytical cuts) and *ranks attention* (biggest movers, outliers, mix shifts); the "is this an issue" call is mine, every run, fresh. False positives gated by judgment + a **running notebook** (accumulating "what's normal here" + accepted states) + a materiality bar.

2. **Scope grew: hunt regressions + one opportunity.** Beyond noticing costs arriving, the report (a) flags things moving in a bad direction (e.g. a parcel shifted to a pricier carrier) and (b) surfaces **exactly one** sized cost-reduction lead per run — PAPER vs DEFENSIBLE honesty-tagged (the [[S132_32ff1025_shipping-savings-routing-optimization]] re-rating mirage discipline applies).

3. **Report arc: descriptive → evaluative → prescriptive.** §1 state of play (orientation) → §2 costs that arrived (the diff) → §3 the review "is everything in order?" (my reasoning; each concern carries reasoning + a recommended look-into, hedged honestly) → §4 the one opportunity → §5 **expected-cost health, at the END** — expected costs are "very off", so the systematic expected-vs-actual gap is a signal to **re-estimate the model**, not an operational alarm.

4. **Two-tier cadence (principal pick).** Weekly **big** report (the full analyst memo) + daily **small** report (what costs arrived + a **DQ canary** — coverage regression, zero-row segments = a load silently failed, null spikes, stale reload). One daily **snapshot spine** feeds both; the weekly reasons over the week's accumulated snapshots. "One opportunity" is weekly-only (keeps daily cheap + non-naggy). The daily tier is the more-automatable one for later triggering.

5. **Knowledge home.** Accumulated knowledge (running notebook, snapshots, findings) lives in the **project folder** `NFE\projects\4_automated_shipping_report\`; the brain keeps only **lean references** (the skill, a keepsake pin, a bank pointer). Each run gets its own dated standalone folder: `...\reports\YYYY-MM-DD\`.

6. **Shipping agent is first-class.** It holds the mart knowledge; it drives the pulls now (grounding) and the skill calls it every run. The snapshot-diff still needs reproducible **code** — model: the shipping agent (holding the contract + DQ quirks) **operates** the harness, which lives in/beside the shipping-agent repo. Exact seam pinned during grounding.

**Vessel verdict:** skill (the analyst's method — the real value) + thin deterministic view-builder + running notebook. Nothing heavier. The reframe *shrank* the deterministic ambition and *grew* the judgment layer.

**Mart-knowledge to teach the agent (principal-flagged this session, NOT yet written):**
- UPS refunds are **not** in the `credit_note` column — they show as **negative-amount invoice lines**. **Some** carriers *do* use `credit_note`. Refund location varies per carrier and is unknown/messy → must be **investigated** and the per-carrier map written into the shipping agent's `reference/known-dq.md`. The daily DQ canary depends on this (a legit refund must not be mis-flagged as a cost anomaly).

**Locked this session (additive to S1's list, don't re-litigate):** senior-analyst (not rules-engine) framing; descriptive→evaluative→prescriptive arc; two-tier cadence (weekly big + daily small/DQ-canary); one snapshot spine; knowledge in project folder w/ dated per-run subfolders; shipping-agent operates the harness; expected-cost health at the end as a re-estimation signal.

## Pending external actions
No pending external actions. (Design discussion; no mart access, brain-side writes only.)

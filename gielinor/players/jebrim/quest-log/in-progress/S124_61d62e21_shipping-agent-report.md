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

---

## Session 3 — 2026-06-01 (sid 28d1f778): BUILD step 1 — per-carrier refund/credit investigation

Resumed on "continue with the shipping report." Build started. Mart verified LIVE (VPN up). First locked build step executed: mapped where refunds/credits actually live per carrier, against the live mart (`shipping_mart`, 6-mo window `invoice_date >= 2025-12-01`).

**Schema fact:** `fact_shipment_invoice_lines` has **no** `credit_note` column — only `charge_bucket` + `charge_amount_eur`. The `credit_note_eur` / `discounts_eur` columns are two of the **buckets on `fact_shipment_cost_summary`**, derived as sums of the invoice lines. So the line-level analysis is the complete picture; the summary buckets mirror it.

**Three structurally distinct refund/credit mechanisms found (ground-truthed via `charge_description_english`):**

1. **Contractual discounts (recurring, structural — NOT an event):** `fedex` → `discounts` bucket. 34,405 neg lines / −€367,200 in 6mo, all "Performance Pricing" (−€223k) + "Discount" (−€144k). Present on ~every FedEx invoice. Canary must NOT flag a large-negative `discounts_eur` as anomaly — its *presence* is normal; a *rate change* is the signal.
2. **Genuine credits/refunds:** `ontrac` → `credit_note` bucket (204 lines / −€47,187, "Credit Amount"); `yodel` → small `credit_note` (3 lines / −€67). Negative `credit_note_eur` = a refund event.
3. **Surcharge reversals / corrections (refund-in-place — the dangerous one):** `ups` (6,853 lines / −€500,621) and `dpd_uk` (4,208 lines / −€18,870). Negative line **keeps its original cost bucket** — e.g. UPS "Fuel Surcharge" −€64k, "Large Package Surcharge" −€63k, "Transportation Charge" −€63k land in fuel_surcharge/oversize_overweight/base_rate. Same description as the positive charge → it's a reversal. Canary must treat a negative in a NORMAL bucket (oversize/fuel/base) as a possible legit reversal, not corruption.

**Negligible:** `dhl`/`dhl_orwo` (972/689 tiny base_rate+other corrections, −€188/−€105). **No observable channel** (zero neg lines, high volume): `maersk`, `usps`, `db_schenker`, `direct_link`, `apg`, `dpd_poland*`. Caveat: these may net refunds at source (reduced positive amounts) → invisible in the mart.

**Validates the principal's model:** UPS refunds = negative invoice lines NOT `credit_note` (confirmed — they're surcharge reversals in-place); "some carriers do use credit_note" (confirmed — OnTrac, tiny Yodel).

**MCP note:** the Redshift MCP query validator rejects `DATEADD`/`CURRENT_DATE` — use literal dates.

**Next:** write this map into `shipping-agent/reference/known-dq.md` (maintainer edit, principal-gated push) — proposed entry surfaced in chat, awaiting nod.

**Refund map WRITTEN** to `shipping-agent/reference/known-dq.md` (new "Refund / credit location by carrier" section) on principal nod. Push still gated.

### Grounding sub-step 2 — expected-vs-actual gap profile (the §5 premise)

Mart persists `expected_shipping_cost_eur` alongside `real_shipping_cost_eur`; measured the gap on invoiced rows with expected populated (~99.8% coverage), window `shop_order_created_date >= 2026-02-01`, by `source_system`.

**Aggregate gap is modest, but per-shipment dispersion is the real story:**

| segment | n | avg expected € | net gap % | MAE € | % real>1.5× exp | % real<0.67× exp | % off>€3 |
|---|---|---|---|---|---|---|---|
| Picturator (TCG) | 718,805 | 6.04 | **+7.6%** | 1.95 | 10.8% | 4.7% | 8.2% |
| PicaAPI (TCG) | 211,137 | 5.59 | +5.2% | 1.20 | 9.2% | 3.2% | 5.6% |
| ORWO | 555,419 | 0.96 | +2.2% | 0.52 | 16.9% | **42.3%** | 1.9% |
| PCS | 859 | 6.45 | −5.2% | 1.66 | 5.1% | 7.6% | 11.6% |

**Reframe of "expected is very off":** it's NOT a wild aggregate error — it's (a) a systematic **under-estimate bias** on TCG (+5–8%; actuals exceed expected, fat upper tail — ~15% of TCG shipments materially mis-estimated), and (b) **poor per-shipment calibration on ORWO** (42% of shipments come in <0.67× expected) that barely matters in € because ORWO POST costs ~€1. MAE is 20–55% of the mean depending on segment. §5 should read as a *re-estimation signal* (lift the TCG expected baseline + widen surcharge allowance; reshape the ORWO model) — not an operational alarm. This dispersion IS the relevant noise floor for any expected-based §4 opportunity sizing ([[S132_32ff1025_shipping-savings-routing-optimization|S132]] mirage-guard lesson).
**Assumption:** `expected_shipping_cost_eur` on an invoiced row reflects the current-model estimate (mart truncate-reloads recompute it) → gap = current-model error, which is what §5 wants. Flagged to confirm.

### Grounding sub-step 3a — lane-key feasibility (GREEN)

Lane key = `production_site` (origin) × `destination_country_code` (dest) × `shipping_provider_group` (carrier). Coverage (window `shop_order_created_date >= 2026-02-01`, n=1,942,424): production_site 0% null, destination_country_code 0% null, shipping_provider_group 0.3% null. **279 distinct lanes total; 92 lanes with ≥100 shipments cover 1,940,046 = 99.88% of volume.** Clean, low-cardinality, tractable for §4 opportunity analysis + segment baselines. Long tail (187 thin lanes) = 0.12% → bucket as "other." No `service`/`zone` column beyond `shippingprovider_extkey` (service granularity lives in extkey if needed later).

**Remaining grounding:** segment baselines ("what's normal" per segment — cost/parcel, % invoiced, carrier mix, bucket shares) — shades into defining the daily snapshot-spine columns.

**known-dq.md refund map PUSHED** to picanova/shipping-agent main (`98593ee`) on principal cue. Step 1 fully closed.

### Grounding sub-step 3b — segment baselines (trailing 120d, shop_order_created_date >= 2026-02-01)

| segment | shipments | % invoiced | €/parcel (final) | total € |
|---|---|---|---|---|
| TCG: PCS PL | 821,500 | 83.2% | 5.77 | 4.70M |
| ORWO | 774,199 | 71.9% | 1.25 | 0.90M |
| TCG: PCS CMH (US) | 202,822 | 90.8% | 10.13 | 2.05M |
| TCG: Wolfen | 120,772 | 54.2% | 4.38 | 0.53M |
| TCG: Other (Allcop 13k/€34k, PCS PX 4.4k/€38k, PL, MerchRocket, …) | ~21k | mixed | 3–9 | ~0.09M |

**Findings:**
- **Locked 4-bucket TCG split (PCS PL / PCS CMH / Wolfen / Other) holds** against real production_site values. "Other" cleanly absorbs the tail (~1% of TCG cost; biggest contributors Allcop + PCS PX). production_site literal `PL` (1,442) is distinct from `PCS PL` → folds to Other.
- **ORWO is 72% invoiced, NOT ~0%.** The design's "ORWO POST structurally ~0% cost-covered" caveat is about the **POST carrier slice within ORWO**, not the segment — ORWO DHL/UPS volume (`dhl_orwo`/`ups_orwo`) IS invoiced. **Correction to apply:** the %-invoiced canary for ORWO must track by-carrier-within-segment, else the POST-driven uninvoiced chunk reads as instability. Wolfen's 54% is also a segment-normal to bake in (not a regression).

**Grounding pass COMPLETE** (refund map ✓pushed · gap profile ✓ · lane-key ✓ · segment baselines ✓). Next = propose locked snapshot-spine column list → scaffold `NFE\projects\4_automated_shipping_report\` → snapshot puller + diff → draft skill.

### Scaffold + snapshot spine + diff harness — BUILT & VERIFIED (sid 28d1f778)

**Snapshot spine locked** (principal-approved): 25 cols = 8 keys/dims (`shipment_id`, `shop_order_created_date`, `source_system`, `production_site`, `destination_country_code`, `shipping_provider_group`, `shippingprovider_extkey`, `cost_source`) + 5 cost/weight (`expected`/`real`/`final`_shipping_cost_eur, `net_revenue_eur`, `billed_weight`) + 12 buckets (excl `truck_charges_eur`). Segment label derived in harness, not stored (segmentation change won't reshape history).

**Harness seam pinned (principal):** self-contained in the NFE project (`lib/`), connects with **full-access `tcg_nfe` creds from `NFE/.env`** (gold by default, raw layers reachable for §5) — NOT gold-only `ship_mart_ro`. `NFE/.env` carries only USER/PASSWORD; host/port/db default in `lib/db.py` (`bi...redshift.amazonaws.com:5439`/`bi_stage_dev`).

**Built in `bi-analytics-main/NFE/projects/4_automated_shipping_report/`:**
- `lib/db.py` — full-access connection URI (connectorx).
- `sql/snapshot.sql` — 25-col snapshot, `{window_days}` param, gold-only, `shop_order_created_date` anchor.
- `lib/pull_snapshot.py` — polars + connectorx (`protocol="cursor"`; Redshift rejects connectorx's default `COPY (SELECT…)`). **First snapshot proven: 1,942,424 rows × 25 cols, 49.01 MB zstd** (`snapshot_2026-06-01.parquet`).
- `lib/diff_snapshots.py` — T-1→T event taxonomy (COST_ARRIVED / COST_RESTATED / CREDIT_REFUND / COVERAGE_REGRESS / NEW / AGED_OUT). **Verified:** self-diff = 0 events (after fixing a presence-flag bug that mislabeled 62,743 uncosted rows as NEW); synthetic test caught COST_ARRIVED=100, NEW=10, COST_RESTATED=65 (35 sub-€0.50 moves correctly filtered). Also fixed a Decimal-division scale overflow (cast EUR cols to f64).
- `notebook/running-notebook.md` — seeded "what's normal" (baselines, accepted states: ORWO-by-carrier, Wolfen 54%, FedEx discounts structural, DBS unclassified, UPS/DPD-UK refund-in-place; gap-profile normals; lane key).
- `README.md` — project overview + run + retention note.

**Open / next build:** (1) **retention policy** — 49 MB/day daily spine ≈ 18 GB/yr if all kept → thin (keep ~30 daily, weekly thereafter). (2) **draft the skill** (the weekly/daily analyst playbook — the real durable artifact) into `players/jebrim/spellbook/drafts/skills/`. (3) **report builder** §1–§5 + the **daily DQ canary** (zero-row segment = silent load failure, coverage regress, null spikes). (4) triggering (deferred). The diff's real T-vs-T-1 test needs a second daily snapshot (tomorrow).

### Session-3 close (sid 28d1f778)

**Pending external actions — reconciled, both completed:**
- `known-dq.md` refund map → committed + **pushed** to picanova/shipping-agent main (`98593ee`). ✓ completed.
- NFE project scaffold (6 files) → committed + **pushed** to picanova/bi-analytics main (`a632653`); snapshot parquet gitignored. ✓ completed.

**Quest stays in-progress** (multi-session build; `open_dep` = skill + report builder + DQ canary not yet built). Resume → `inventory/shipping-agent-report-resume__28d1f778.md` (prior `__8cb8f235` archived). Harvest: 1 examine draft (`2026-06-01-verify-diffs-both-ways-and-explicit-presence-flags`) + 1 cross-conv memory.

**Stale-done scan (other Jebrim in-progress quests) — surfaced, not auto-moved (ambiguous):** [[S116_7f67fe48_shipping-agent-fif-monthly-skill|S116]] reads complete-ready (SharePoint PUT verified, DAG pushed) but its prior CLOSING deferred graduation and harvest drafts await — flagged for graduation. S-shipping-agent readiness-gate = orphan sub-agent trace ([[D-030_alching-sweeps-orphan-subagent-traces|D-030]] sweep candidate). Both left for principal call / next session.

---

## Session 4 — 2026-06-01 (sid 45954b41): BUILD step 2 — the analyst skill (durable artifact)

Resumed on "continue with the shipping report." Clean resume from 28d1f778 (ended 7s before open; no unresolved pending). Grounded against the built foundation (read README, running-notebook, snapshot.sql, diff_snapshots.py, pull_snapshot.py + the calling-the-shipping-agent skill). Offered next-step branch (AskUserQuestion) → principal picked **draft the analyst skill** (the locked durable artifact).

**Drafted** `players/jebrim/spellbook/drafts/skills/running-the-automated-shipping-report.md` — the weekly/daily senior-analyst playbook. Covers: what-it-is (analyst review, NOT a rules engine — harness preps evidence + ranks attention, zero verdicts) · the two event streams (moved vs cost-arrived) · two-tier cadence on one snapshot spine · the harness run commands + 25-col spine + diff event taxonomy (with the presence-flag + Decimal→f64 lessons) · segmentation/scope gating · the §1–§5 arc (descriptive→evaluative→prescriptive, §4 PAPER-vs-DEFENSIBLE, §5 re-estimation signal) · daily DQ canary · running-notebook discipline (5 seeded accepted states) · carrier-aware refund map · cost-basis caveats. Born-linked to S124/[[S132_32ff1025_shipping-savings-routing-optimization|S132]], calling-the-shipping-agent, the 2 harvest drafts.

**Next:** report builder §1–§5 + daily DQ canary in project `lib/`; retention thinning; 2nd snapshot for a real T-vs-T-1 diff test. Skill stays in drafts/ → promotes via alching.

**Pending external actions:** none (brain-side draft + quest-log + comms/intent only this turn).

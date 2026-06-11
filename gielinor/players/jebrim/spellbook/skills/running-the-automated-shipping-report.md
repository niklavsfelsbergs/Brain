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

**Snapshot spine** = 29 cols, 1 row/shipment, trailing 120d by `shop_order_created_date`: keys/dims (`shipment_id`, `trackingnumber`, `shop_order_created_date`, `source_system`, `production_site`, `destination_country_code`, `shipping_provider_group`, `shippingprovider_extkey`, **`packagetype`**, **`weight_kg`**, **`length_plus_girth_cm`**, `cost_source`) + `expected`/`real`/`final`_shipping_cost_eur + `net_revenue_eur` + `billed_weight` + 12 charge buckets (excl `truck_charges_eur`). ~68 MB/day. **Segment is derived in the harness, not stored** — so a segmentation change never reshapes history.

The last three dims were added in the **S124 rebuild** (sid b2b0db1d) and are **PCS-owned** (`packagetype`, `weight_kg`, `length_plus_girth_cm` — NULL on external sites: ORWO/Wolfen/Allcop/…). They unlock the two contract-aware reads below: `length_plus_girth_cm` bands oversize charges against the LPS(325)/OML(419) triggers; `packagetype` × `weight_kg` (order-level, populated where `billed_weight` isn't, since it's pre-invoice) form the corridor key.

`trackingnumber` is the **real carrier tracking number** (the mart's identity field — `shipment_id` is hashed from it), carried for per-shipment cost-outlier lookup. Note `shippingprovider_extkey` is **not** a tracking number — it's a **service/rate code** (`UPS04STD`, `DBSCHENKERPLEUHOME`), shared across shipments. Synthetic `trackingnumber` values (`''`, `'untracked'`, `'temp_*'`) never carry an invoice, so any *invoiced* outlier has a real tracking number to look up (shipping-agent `mart-contract.md`).

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

## The report arc — delta/exception-first (S124 rebuild)

The **rebuild reshaped the arc** (it was §1-§5, state-of-play-led — a static 120d "Groundhog Day" sheet that barely moved run to run). It now **leads with the delta** and demotes the static levels to the end. The two questions the report exists to answer, made structural:

> **(a) Did new cost arrive, and is it OK?**  **(b) Is volume moving to a different carrier?**

- **Bottom line (lead, plain-English).** The one-glance status. The harness **auto-computes** the three headline facts — net cost arrived (vs gross — read net), the **disputable-oversize €** + share, and the corridor-migration count + top move — then leaves an **analyst-verdict slot** ("is everything in order, the single action, the real number?"). The verdict is the analyst's; the inputs are computed.
- **§A — Did new cost arrive, and is it OK?** The cost-arrived **diff** (the valuable half: € newly invoiced, flips, net restatement, refunds, coverage change — from the event table) **+ the contract-aware oversize read** (below). "Expensive arrivals — check by tracking number" lives here: costs that newly invoiced/restated this run AND landed materially over expected. **Read net, not gross** — reversals land in the same buckets.
- **§B — Is volume moving to a different carrier?** The **corridor cut** (below) — carrier-share migration on material corridors.
- **§C — Worth a look (ranked attention, weekly).** The biggest movers/outliers the harness ranked, each a *candidate* for the analyst, not a verdict: **standing cost outliers by tracking number** (invoiced rows where real ≥ 2× expected and ≥ €10 over — bar above the noise floor), **lane €/parcel outliers**, top cost-arrived / restatements / credit candidates.
- **§D — One opportunity (weekly only).** Exactly **one** sized cost-reduction lead, **PAPER vs DEFENSIBLE** honesty-tagged. Size it against the expected-cost noise floor — don't sell a mirage ([[S132_32ff1025_shipping-savings-routing-optimization|S132]] re-rating discipline: trust-gate, capability-check, engine-noise-floor before a number). Lane-outlier + corridor tables are the starting points.
- **Supporting detail (demoted to the END).** State-of-play §1 (per-segment vol/%-invoiced/€-per-parcel/carrier-mix/ORWO-by-carrier) + expected-cost health — the **static baseline, not the signal**. Expected-vs-actual gap is a **re-estimation signal** (TCG under-estimates +5–8%, fat tail; ORWO poorly calibrated but ~€1/parcel) — "lift the TCG baseline + widen surcharge allowance; reshape ORWO" — not an operational alarm; it's the noise floor for §D sizing.

## The two contract-aware reads (the rebuild's core — `lib/oversize.py`, `lib/corridor.py`)

**Why they exist:** critique #2 of the pre-rebuild report was *"findings not interpreted against the contract"* — a UPS cost spike was called "€111k overbilling" when it's an oversize surcharge with a refund mechanism. Both modules read the spine against carrier-contract reality.

- **`oversize.py` — contract-aware LPS/OML read (answers "is it OK?").** Bands the standing oversize bucket (`oversize_overweight_eur`, already net of applied+reversed per shipment) against `length_plus_girth_cm`: **OML legit (>419) / LPS legit (325–419) / DISPUTABLE (≤325) / NULL**. A charge **below** the size trigger is **disputable** — UPS-side dimensional misclassification, not legitimate cost — verified S124: the PCS-PL UPS oversize charges sit on parcels ≤332cm (nowhere near 419). UPS auto-reverses in batches (refund-in-place), so **monitor the standing un-reversed NET, not gross applied**. Real run: €393k standing, **89% disputable** — and it generalizes beyond UPS (OnTrac/FedEx US, DPD-UK piles too). **Caveat (carry it):** the bucket mixes SIZE + WEIGHT surcharges; the dim adjudicates size only. UPS PCS-PL is verified size-disputable; the US-carrier piles are **candidates** until the `charge_description` size-vs-weight split is pulled (the periodic shipping-agent deep-dive). Act on the verified slice; rank the rest.
- **`corridor.py` — carrier-share migration (answers "is volume moving carrier?").** A **different time base** from cost-arrival: recent **7 ship-days** vs prior **4 weeks**, off a *single* snapshot (the cohort spans both windows by `shop_order_created_date` — no diff needed). Corridor key = `production_site` (origin) × `destination_country_code` × weight-band (`weight_kg`) × `packagetype`. Flags a carrier whose **share moved ≥ 15pp** on a corridor with **≥ 200 recent shipments** (materiality gate — thin corridors swing on noise). Null share → 0, so a new/vanished carrier shows as the migration. Knobs (7d/4wk/15pp/≥200, principal-set S124) **rank/gate attention; they are not verdict thresholds.** A move can be **good** (re-route to a cheaper eligible carrier) or **bad** (pricier carrier / lost negotiated lane) — the analyst reads each against the contract.

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

- **Output form: HTML** (S124, 2026-06-02 — principal cue "it's supposed to be an HTML report"). Each run writes a **self-contained, styled `.html`** (embedded CSS, no external assets — opens in a browser, pastes into an email cleanly) to the dated folder `reports/YYYY-MM-DD/`, rendered by `lib/render_html.py` (`markdown` lib + `tables` extension). The look is the brain's **golden document theme** — warm near-black ground, gold section heads, parchment ink, amber code — stolen from the dev-brain dark+gold doc skin (`developer-braindead/bank/research/2026-05-29-agentic-os-field-primer.html`). The `.md` is kept alongside as the render *source* + a diff-friendly artefact — HTML is the deliverable, md is the substrate. Both `build_report.py` and `dq_canary.py` emit `.html` + `.md`. **Per-tier filenames** so a same-day daily+weekly run doesn't clobber: weekly → `report.html`, daily → `report_daily.html` (pass `--out reports/<date>/report_daily.md`), canary → `dq_canary.html`. Email/Slack delivery folds into the (deferred) triggering conversation.
- **Analyst-judgment caveat for the builder:** `build_report.py` emits the **Bottom-line verdict slot + §C/§D** as empty *judgment slots* — the analyst fills them in the generated `report.md`, THEN renders to HTML. **Re-running the builder overwrites those edits**, so once judgment is written, render md→html directly (`render_html.md_to_html`) rather than re-running the builder (S124, 2026-06-02 — learned the first real run).
- **Triggering** is deliberately deferred — design the approach first.
- **Noticing thresholds** for ranking attention are empirical — tune from accumulated snapshots, kept as harness *ranking* inputs, never as verdict gates.

## Related

- [[calling-the-shipping-agent]] — the agent operates the harness.
- [[savings-investigation-deliverable-shape]] + [[S132_32ff1025_shipping-savings-routing-optimization|S132]] — the §4 opportunity honesty discipline.
- Project: `bi-analytics-main/NFE/projects/4_automated_shipping_report/` (README, lib/, sql/, notebook/).

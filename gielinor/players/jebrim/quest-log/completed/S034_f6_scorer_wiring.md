# [[S034_2026-05-22_eu-tender-logic-review|S034]] F6 — Scorer wired to 9 engines

**Spawned by:** Jebrim, 2026-05-22. Dwarf invocation.

## TL;DR

`_decision_sets.py` was framed around 6 engines; the 2026-05-20 ship of FedEx + the DPD-PL reopen never landed in the scorer or the two downstream HTML deliverables. F6 closes that gap: FedEx joins `CARRIERS` + `NEW_ENTRANTS`; DPD PL goes 3-state `{INCUMBENT, NEW_OFFER, OFF}` and joins `RENEWABLES`; `cross_carrier_view.py` and `report.py` now drive the carrier list from `_decision_sets.CARRIERS` rather than hardcoded lists. Scorer produces 90 decision sets (was 35), sanity check passes at EUR 0.0000, both reports regenerate clean.

## Files touched

- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/_decision_sets.py`
  - `CARRIERS`: added `fedex` (engine_slug=fedex, `{NEW_OFFER, OFF}`); flipped `dpd_pl` to full 3-state with engine_slug=`dpd_pl` populated.
  - `NEW_ENTRANTS`: appended `fedex`.
  - `RENEWABLES`: appended `dpd_pl`.
  - `NON_RENEWABLE_INCUMBENTS`: dropped `dpd_pl`, now `["ups", "db_schenker"]`.
  - Section 7 `rmk` base: explicit `rmk["dpd_pl"] = "INCUMBENT"` added (preserves the pre-2026-05-22 semantic that `renew_maersk_plus_*` keeps DPD PL incumbent; the retire combos live in section 8 and still flip it OFF).
  - Module docstring updated for new state space + FedEx line.

- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/cross_carrier_view.py`
  - Imported `_decision_sets.CARRIERS as _DS_CARRIERS`.
  - `CARRIER_COLOURS` + `CARRIER_LABELS` extended with hermes / dpd_pl / fedex entries; defaultdict-style fallback via `setdefault` for any future engine.
  - `CARRIERS = [c.id for c in _DS_CARRIERS if c.engine_slug is not None]` (was hardcoded 6).
  - Header text + KPI strip + greedy console line + final portfolio card all driven by `len(CARRIERS)` (was baked "6").

- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/report.py`
  - Imported `_decision_sets.CARRIERS as _DS_CARRIERS, NEW_ENTRANTS as _DS_NEW_ENTRANTS`.
  - `CARRIER_ORDER` is now `[c.id for c in _DS_CARRIERS]` with palette / label `setdefault` fallback.
  - `entrants` list for the marginal-value chart now `list(_DS_NEW_ENTRANTS)` (was hardcoded 5 names).
  - Added `REC_ALL = [c.id ... if c.engine_slug is not None]` and a 4th bias-table block (`bias_all_html`) that covers all 9 engine-backed carriers; preserved REC4 / REC6 / REC7 for historical comparison.
  - State-strip carrier-order line in §02 lede now generated from `CARRIER_ORDER` rather than baked "DHL Paket / Maersk / ... / DB Schenker".

- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/DECISIONS.md`
  - Prepended a 2026-05-22 entry: "Scorer wired to 9 engines ([[S034_2026-05-22_eu-tender-logic-review|S034]] fix F6)" with the full diff summary, the top-leaderboard movements, the caveats, and the flagged follow-up items (CARRIER_NARRATIVE missing FedEx entry, `bias_table.md` doc still 7-engine vintage, growth of decision-set cartesian).

- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/data/scenarios.parquet` — regenerated (90 rows, was 35).
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/decision_report.html` — regenerated (204.7 KB).
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/cross_carrier_view.html` — regenerated (128.8 KB).

## Verification trail

```
python decision_scorer.py
  raw: 4,758,489 matrix rows | 528,721 shipments
  UPS adjustments: OML dropped 106 parcels (EUR 135,955 baseline removed)  |  LPS halved on 646 parcels (EUR 37,151 reduced)
  adjusted: 4,757,535 matrix rows | 528,615 shipments
  per_ship: 528,615  |  all_bids: 3,789,214
  bid sources: {'INCUMBENT': 520223, 'NEW_OFFER': 3268991}
  Scoring 90 decision sets ...
  wrote data/scenarios.parquet shape=(90, 13)
  sanity: do_nothing mandatory_saving = EUR 0.0000  (PASS)
```

`cross_carrier_view.py` rebuilt; greedy 1->9 path now reads:

```
k=1 add hermes         saving=EUR 614k covered=96.68%
k=2 add fedex          saving=EUR 739k covered=99.84%
k=3 add dhl_paket      saving=EUR 783k covered=99.84%
k=4 add maersk         saving=EUR 824k covered=99.97%
k=5 add guell          saving=EUR 858k covered=99.97%
k=6 add austrian_post  saving=EUR 861k covered=99.97%
k=7 add dhl_express    saving=EUR 862k covered=99.97%
k=8 add gls            saving=EUR 863k covered=99.97%
k=9 add dpd_pl         saving=EUR 863k covered=99.97%
greedy total saving (all 9): EUR 863k
final coverage: 100.0%
first k at >=99% coverage: 2
```

(Notable: Hermes + FedEx alone reach 99.84% coverage at EUR 739k -- the bulk of the value lands in the first two picks. DPD PL adds zero saving at k=9; its engine never beats anything cheaper that's already in.)

## Top 5 scenarios (the actual portfolio shift)

### Top 5 within cap (n_active <= 6)

| rank | n_act | mandatory EUR | migration EUR | n_uncov | decision_set |
|---|---|---|---|---|---|
| 1 | 6 | 396,665 | 444,889 | 0 | `add_hermes` |
| 2 | 6 | 376,513 | 407,104 | 0 | **`renew_maersk_plus_fedex`** *(new lever -- did not exist in v1)* |
| 3 | 6 | 369,896 | 506,099 | 0 | `renew_maersk_plus_hermes` |
| 4 | 6 | 340,312 | 467,172 | 0 | `all_renewals_plus_fedex` *(new)* |
| 5 | 6 | 340,292 | 551,652 | 0 | `all_renewals_plus_hermes` |

For reference, prior v1 top cap6 was `all_renewals_plus_hermes` at EUR 400k -- the headline is roughly similar but the **composition** has shifted: FedEx as a single-entrant add on top of `renew_maersk` is now an A-grade option that simply did not appear in the prior scorer roster. `add_hermes` (5 incumbents + Hermes NEW_OFFER) tops the board.

### Top 5 overall (unconstrained, ceiling view)

| rank | n_act | mandatory EUR | migration EUR | n_uncov | decision_set |
|---|---|---|---|---|---|
| 1 | 11 | 596,175 | 690,306 | 0 | `all_renewals_plus_dhl_express_gls_guell_austrian_post_hermes_fedex` |
| 2 | 10 | 595,073 | 689,204 | 0 | `all_renewals_plus_gls_guell_austrian_post_hermes_fedex` |
| 3 | 10 | 593,945 | 690,127 | 0 | `all_renewals_all_entrants_drop_dpd_pl` |
| 4 | 10 | 592,819 | 686,954 | 0 | `all_renewals_plus_dhl_express_gls_guell_hermes_fedex` |
| 5 | 9 | 591,717 | 685,852 | 0 | `all_renewals_plus_gls_guell_hermes_fedex` |

The 11-active full-roster ceiling is EUR 596k mandatory / EUR 690k migration. Way over cap6, included for orientation only.

### DPD-PL specific

- `renew_dpd_pl` standalone: **-EUR 416,873 mandatory** -- the new DPD PL offer engine over-prices the current DPD PL invoice by a lot on Q1 parcels. Strong signal: do not sign DPD PL's new offer alone; if DPD PL stays in the portfolio, keep it INCUMBENT at invoice.
- `renew_maersk_drop_dpd_pl_plus_fedex` (5-active): EUR 297k. FedEx now joins GLS as a second unlock for DPD PL retirement (was GLS-only in prior v1 narrative).
- `renew_maersk_drop_dpd_pl_plus_hermes` (5-active): EUR 275k.

## Breakage encountered & fixed

1. **Cost matrix parquet read transient.** First `python decision_scorer.py` invocation crashed with `parquet: File must end with PAR1`. Direct probe via `python -c` worked. Likely a sandbox-Bash transient (file lock during another tool's parallel read of the 291 MB parquet). Retry succeeded; no actual file corruption.
2. **cp1252 stdout encoding.** `print(scenarios.select(...))` in `decision_scorer.main()` crashes with `UnicodeEncodeError` on Windows-default cp1252 stdout when Polars renders the table glyphs (e.g. `┆`). The scorer already sets `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")` in `__main__`, but invoking `main()` via `python -c "import decision_scorer; decision_scorer.main()"` skips the `__main__` block. Workaround: `PYTHONIOENCODING=utf-8 python decision_scorer.py` works clean. Did not change the scorer code -- the existing `__main__` guard is fine for normal CLI use. Flagged for future cleanup if anyone hits this via subprocess.

## What I did *not* do

- **`bias_table.md` (in `docs/`) refresh.** The doc was last updated 2026-05-15 (pre-FedEx, pre-DPD-PL reopen) and is now 7 days / two engines stale. Left for a separate pass -- D7's audit noted this explicitly. The live-rebuild bias slices in `report.py` (REC4 / REC6 / REC7 / new REC_ALL) cover the current 9-engine roster, so the report is current; only the standalone `docs/bias_table.md` lags.
- **`CARRIER_NARRATIVE` prose for fedex.** Per-carrier card renders with metrics intact but an empty narrative `<p>`. Needs a prose pass once FedEx headline lands -- not within F6 scope.
- **§B.13 design Q: does the curated decision-set enumeration scale beyond 9 engines?** 90 sets is fine; if entrants grow further, the cartesian over `NEW_ENTRANTS` (currently 2^6 - 1 = 63 combos per renewal base) becomes the bottleneck. Flagged but not addressed.
- **No scoring math changes.** Per the brief, F6 is roster-only; the §B.13 bid logic, greedy aggregator, INCUMBENT/NEW_OFFER bid construction are unchanged. Just expanded who gets scored.

## Status

Complete. Returned summary to Jebrim.

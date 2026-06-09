# [[S169_truck-cost-warenpost-sizing|S169]] — Yodel actual-vs-declared dimension accuracy (PCS PL) — topic 45 deep-dive

**Player:** Jebrim · **Opened:** 2026-06-09 · **Status:** in-progress (mart pull complete; topic 45 extended) · **Mode:** shipping-agent (emulated sub-agent), full-access `tcg_nfe`

The deep-dive topic-45 was building toward: how our PCS-declared package dims compare to
Yodel's ACTUAL MEASURED dims, by `packagetype`. Yodel = the cleanest independent measurement
(both sides garbage-free on the comparable subset).

## Scope used
- **PCS PL Yodel** (`production_site = 'PCS PL'`, exclude tiny distinct `'PL'`). PCS-PL = essentially ALL of Yodel (1.23M shipments; every other site single-to-low-thousand digits).
- **Tier: UPSTREAM / off the gold contract** on the carrier side — `enterprise_bronze.yodel` `actual_*` (mm /10 = cm), authorized via `tcg_nfe`. Mart side (declared dims) is gold.
- Join `'J' || tracking_number` -> `fact_shipments.trackingnumber`, latest-per-tracking dedup. 100% match.
- Sorted axes (long/mid/short) + L+girth, both sources bounded 2-300cm. Delta = actual - declared (+ = under-declared).

## Headline results
- **Comparable subset is SMALL and BURSTY:** only 85,209 of 1.23M PCS-PL Yodel (6.9%) have `actual_*` populated. After clean: **85,961 parcels, only 29 dropped (0.0%)**. STOP-AND-REPORT raised: `actual_*` far sparser than the pass-2 "full coverage" framing implied. Bursty in time — 2023 Aug-Oct burst, dead 2024-Sep25, strong recent window **Oct2025->Mar2026 (Nov-Jan 54-61%)**. Bias holds in both windows (older +1.3, recent +2.7) — robust, not a burst artifact.
- **Distribution:** longest-axis mean **+2.32cm, MAE 6.49cm, 35% within +/-2cm**. Reconciles with pass-2 mart-wide (+2.3/6.5) -> confirms PCS-PL ~= all Yodel. Percentiles (NTILE): p25 0, **p50 +2, p75 +6**, p95 +14, p99 +20.5. **Real right-skewed under-declaration, NOT symmetric noise.** Bias on longest axis only; mid/short near-centered.
- **Under-declaration (the actionable cut):** 60.6% of parcels have >=1 axis measured >2cm larger than declared; 37.8% >5cm. Longest axis: 49.4% >2cm, 32.3% >5cm, 14.7% >10cm. Worst offenders = **strapped multipacks + WICKELVERPACKUNG wrap types** (WICKEL 70x50_ 94% >5cm/+10.5cm; Pizza Box 20x20 2stk strapped 79%/+10.7; WICKEL 30x20_3x strapped 75%/+20.1). We book a single box; ship a larger strapped bundle.
- **Our-side DQ:** every named fixed box carries a **22.5cm fallback floor** (e.g. STANZ 120x80 22.5->122.5cm), minority-share (avg stays on nominal, distinct-count 2-8) — a declaration-pipeline default stamped when the real spec isn't resolved. Inflates the left tail.
- Small fixed boxes (MUG/Poster/Teppich) declared accurately (90-97% within 2cm) — problem is wrap/strapped/large-composite-specific.

## Checks run
- Coverage probe with/without garbage-clean (29 dropped = 0.0%).
- Overall mean/MAE reconciles with pass-2 mart-wide figure.
- Recent-vs-older window split: bias present in both (not a 2023-burst artifact).
- Self-consistency: longest-axis bias, mid/short centered -> the +2.3 isn't a uniform inflation.

## Deliverable (outside the brain)
- `bi-analytics-main/NFE/shipping_topics/45_invoice_vs_mart_dimension_accuracy/sql/yodel_actual_vs_declared.sql` (Queries 1-8).
- Extended topic `CLAUDE.md` with the "Yodel deep-dive (PCS PL)" section (coverage, by-packagetype table, distribution, under-declaration, our-side DQ, takeaways, caveats).
- **Not committed** (per brief).

## Caveats / open
- MCP validator rejects `STDDEV`, `PERCENTILE_CONT` outside windows, `DATEADD`/`CURRENT_DATE`, `SELECT DISTINCT` over window cols, `COUNT(DISTINCT)`+other-aggregates mixes -> used NTILE bucketing + max-min span + literal dates as workarounds (noted in SQL header).
- Off the gold contract on the carrier side; `actual_*` raw, no curated guarantees.
- The bursty 6.9% coverage means any €-sizing of the under-declaration risk must be scaled to ~86k clean rows, not 1.24M — flagged for whoever sizes the oversize/mis-rating exposure next.

## Rulebook gap flagged
- Pass-2 in topic 45 recorded Yodel as "REAL ... full live coverage on their dim-populated subset" — but the dim-populated subset is only 6.9% and bursty, not "full coverage." Worth a maintainer note on the pass-2 line so the next reader doesn't over-trust Yodel's reach.

## Pending external actions
None. (Read-only mart; deliverables outside the brain; this quest-log trace brain-side.)

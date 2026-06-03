# Resume — EU Tender engine rebuilds (S102)

**Status:** in-progress · session 6217a8d5 · 2026-05-27
**Quest:** `quest-log/in-progress/S102_6217a8d5_eu-tender-fedex-reply-review.md`
**Repo:** out-of-tree `Documents/GitHub/bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carriers/`

## Where we are
- **FedEx** — Round-1 reviewed + tighten pass + Round-2 SENT. Committed (tender `8cdf616`, brain `83a1e21`). Engine `fedex-2.0.0` HELD (round-2 pending).
- **maersk-3.0.0** — DONE + VERIFIED + COMMITTED (tender `3b86d6a`). 15/15 fixtures + full-pop smoke clean (€4.35M). The reference pattern for the remaining rebuilds.
- **Hermes** — fuel PINNED (committed): base-2021 Großverbraucher ladder, **Jan 0 / Feb 0 (122.7 knife-edge) / Mar ~7% (158.5)**. NOT yet wired.
- **DHL Express, Austrian Post** — not started.

## Next concrete step — wire `hermes-2.0.0` (PLAN §B.22)
Engine: `carriers/hermes/`. Spec from `carrier_responses_to_open_questions/Hermes/REVIEW_CONCLUSIONS.md` (engine-to-do) + research file `research/2026-05-27-hermes-destatis-diesel-index.md`:
- **Bulky** — activate `surcharges/bulky.py` `Bulky.conditions()`: trigger = longest side >120cm (≤170) AND girth (L+2W+2H) ≤360. Wire `BULKY_INTL_EUR` per-country lookup: AT 5.29, ES/PT 15.75, UK 10.51, CH 29.16(OOS-CH excluded), DK/FI/SE 26.25, IT 36.75, PL 66.72, NL 92.35, **most others 57.75**, CY/MT n/a; DE 8.85. (Values are per-shipment, much larger than the old "5.29–15.00".)
- **Fuel** — re-map `diesel_schedule.parquet`/`FUEL_PCT` to the base-2021 ladder, per-month on `shop_order_created_date`: Jan 0% / Feb 0% / Mar ~7%. Scope = base only.
- `MAX_LENGTH_CM` 200→170. Residential stays 0. MAUT 0.20 confirmed. Returns OOS confirmed. Gross-weight = no change.
- Bump `ENGINE_VERSION="hermes-2.0.0"`; update fixtures (bulky-intl trigger + Mar-fuel) + run `python -m carriers.hermes.tests.test_engine`; full-pop smoke.

Then: **dhl_express-2.0.0** (§B.23: TDI~30% air / DDI~18% road monthly, customs 0, demand Jan1–Feb16, remote-area list, pickup line-haul, oversize 10) · **austrian_post-2.0.0** (§B.7.c/d: gross-only, no-peak, Sperrgut>100cm, Stettin→CH Hohenems rate, CH customs 1.00 regardless ZAZ, CH FX, DSV trucking). FedEx + DHL Paket stay HELD.
Finally: **`python cost_matrix.py`** → compare new Q1 per-carrier totals + portfolio ranking vs the old-proxy run; surface the shift; then `decision_scorer.py` + report regen.

## Verification method (per engine)
`python -m carriers.<carrier>.tests.test_engine` (update fixtures first) + a full-pop smoke over `data/population.parquet` (no runtime error + sane aggregate). Commit per-engine, pathspec-scoped (shared-index hazard), local-only (no push).

## Files to read first
- `carriers/maersk/` (the committed 3.0.0 pattern: constants + toll modules + __init__ + fixtures/test_engine)
- `carrier_responses_to_open_questions/<carrier>/REVIEW_CONCLUSIONS.md` "Engine to-do on cascade"
- `docs/PLAN.md` §B.22 / §B.23 / §B.7
- `docs/NEXT.md` (next-steps already point at this rebuild)

## Small follow-ups
- `carriers/maersk/CLAUDE.md` version-history + open-items still describe the pre-3.0.0 state (10% fuel proxy, toll placeholders) — refresh on a docs pass.
- Hermes residuals: confirm Feb index off the carrier's promised figure (settles the 122.7 knife-edge); Island Delivery 8.00€ auto-vs-opt-in.

# S207 · Maersk/Hermes max dims + DB Schenker reroute consult (sid8 4b987ab6)

**Player:** Jebrim · **Status:** complete (consultation; deliverables shipped in chat) · **open_dep:** none

Consultation prepping a carrier conversation: what max dims Maersk and Hermes can take per our engines, which packages move off DB Schenker and why, plus a series of live mart pulls for concrete examples and the full-2026 oversized population profile.

## What was asked / answered

1. **Max dims Maersk vs Hermes** (from the engines, HEAD on maersk-3.2.0 / hermes-2.x):
   - **Maersk** (hard acceptance ceiling, confirmed by Stefan@Maersk 2026-06-10): longest ≤175cm (DE 200), girth (L+2W+2H=`length_plus_girth_cm`) ≤300, ≤30kg; ROW L+girth ≤266. Source: `carriers/maersk/constants.py` (MAX_GIRTH_CM=300), `calculate.py` over_handling_ceiling.
   - **Hermes**: standard doorstep (longest ≤120, W/H ≤60, girth ≤300, ≤30kg) + bulky (120<longest≤170, girth ≤360, ≤30kg DE 31.5). Max length 170 (tightened from 200 in 2.0.0). Source: `carriers/hermes/constants.py`.
   - **Complementary:** Hermes takes more girth (360 vs 300), Maersk more length (175/200 vs 170).

2. **DB Schenker reroute** (from [[2026-06-10-db-schenker-reroute-package-dims-and-savings]]): Q1 DBS incumbent 8,951; 4,490 move (Hermes 4,463 + Maersk 27); booked saving ≈€107.7k. zV → all Hermes (€85k, 85% of switch; girth 329 ≤360, can't go Maersk @300); CUSTOM_OVERSIZED → Hermes 589 + Maersk 27; GEL stays (182cm longest + 392 girth exceed both). The L+2W+2H girth confirmation collapsed the Maersk lane (2,924→27) — switch is now ~entirely a Hermes play.

3. **zV dims**: dominant template ≈130.3×91.6×7.6 (girth 328.7); templated not measured (99.4% on two templates; weight is the only varying input).

## Live mart pulls (shipping-agent, gold `fact_shipments`) — traces in this folder
- `S-shipmart-pcs-oversized-dbschenker-example.md` — PCS CUSTOM_OVERSIZED example (PPO33731316, 165×122×5) + alternates + PCS zV examples appended.
- `S-shipmart-picturator-oversized-prodordernumber-example.md` — Picturator production-system order number (D42791963); `production_ordernumber` column provenance.
- `S-shipmart-custom-oversized-2026-by-carrier.md` — 2026 count per carrier + median dims per carrier.

Key empirical findings harvested to bank draft [[2026-06-11-custom-oversized-2026-population-by-carrier]]: UPS (6,949) is the largest oversized carrier not DBS (5,912); UPS/DPD UK/Yodel dims are templated (132×84×6/girth312), only DBS is genuinely measured (median girth 369, already > both reroute ceilings → most DBS oversized is freight-only by girth).

## Decisions / corrections
- "Production-system order number" = `production_ordernumber` (D-prefix), NOT `shop_ordernumber` — user redirected to the production layer.
- PPO-prefix is **not** dominant for zV on PCS (29 of 500); the slice is carrier-mixed — corrects an over-index on PPO.

## Pending external actions
None pending. No commits to bi-analytics (read-only consultation); no Slack/external sends.

## Cascade.
None — no canonical EU-tender doc edits this session (consultation only; engine constants read, not changed).

## Main-brain changes.
1 bank draft ([[2026-06-11-custom-oversized-2026-population-by-carrier]]); 3 shipping-agent traces (this folder). No identity-layer writes.

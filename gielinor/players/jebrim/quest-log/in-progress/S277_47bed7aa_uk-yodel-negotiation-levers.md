# S277 -- UK Yodel (Maersk) negotiation levers to ~0%

**sid8:** 47bed7aa | **player:** Jebrim | **date:** 2026-06-19
**Continues:** [[S261_c2f15e55_uk-yodel-oog-cap-correction]] (the yodel engine + 3_UK build).
**Deliverable home:** EXTERNAL `bi-analytics-main/NFE/projects/2_EU_tender_2026/3_UK/` (new `2_analysis/yodel_negotiation_levers.md`).

## Ask
Maersk wants the UK business; all-Yodel is +~10% vs today. Find concessions (base / specific cuts /
surcharges) that bring it to ~0%. Frame first, then size, then check the baseline.

## What happened (turn arc)

1. Grounded in the existing UK Yodel corpus (eu-tender digest, [[S261_c2f15e55_uk-yodel-oog-cap-correction|S261]] resume, the yodel engine + 3_UK docs).
   Confirmed: UK = separate track (Maersk-brokered Yodel, GB B2C); all-Yodel mainland = +9.8% / +GBP 45,251/Q.
2. Framed the lever families (base / targeted cuts / surcharges-that-hit-us), filtered by what our profile pays.
3. Sized levers off the live mart (Redshift MCP, gold shipping_mart; restricted 30s -> lean bucketed queries):
   - Mainland baseline reconciled to the engine (parcel GBP 349,948 ~= recorded 349,949).
   - **Structural finding:** 20,626 Large parcels (47% of Large) sit 0-6cm over Medium's 64cm length cap.
4. Principal: "hold weight pricing won't work; try widen volume tier + targeted cuts + OOG." Sized those.
5. Principal pivoted (logistics manager): **negotiate RATES, not structure.** Re-sized rate-only menu:
   base -15.1% across, or Large -24.1% (GBP 3.69->2.80), or OOG -90% -- each closes the gap alone.
6. Final comparison table (Q1 invoiced / all-DPD / Maersk as-is / Maersk + each lever) -- all 3 levers -> ~0%.
7. **Offshore fold-in:** decomposed cost buckets. Offshore ~neutral (existing ex-truck GBP 33,612 vs Yodel
   GBP 35,216 = +GBP 1,604). Incumbent billed ~EUR 0 remote but offshore base = 2x mainland -> we already
   pay the offshore premium. Overturned the committed "offshore +GBP 16k adverse" read.
8. **Baseline check:** principal noticed UK cost rose in March. Decomposed: base FLAT (no GRI), March = a
   one-month truck spike, Apr-May = fuel (volatile) + DPD +34%/parcel; mix shifted favorably to Maersk
   (28%->57%). Excluding offshore zips, **mainland is flat** (EUR 5.64 Jan-Feb vs 5.61 Mar-May); the whole
   "UK rose" signal is offshore (per-parcel ~doubled Apr-May on DPD/UPS EUR 21-26 vs Maersk EUR 8).
9. **Decisions locked:** stick with Q1 mainland baseline (rise was an offshore artifact); offshore is an
   operational mess, parked out of scope.

## Decisions
- **Baseline = Q1 mainland** (Mar-May rebase rejected: mainland flat, the rise was offshore-only).
- **Offer Maersk the 3 rate asks** (base -15.1% / Large -24.1% / OOG -90%), their pick, each -> ~0%.
- **Offshore parked** -- DPD/UPS offshore blowout is an ops fix (move to Maersk EUR 8/pcl), not a tender input.

## Data-discipline catches this session
- `real_shipping_cost_local` is mixed-currency (GBP UK + EUR ex-PL Maersk) -> used `_eur` /1.1515 instead.
- Truck is baked INTO `real_shipping_cost_eur` (= cost_summary.truck_charges_eur), not a separate line.
- Echoed the committed "offshore +GBP 16k adverse" before verifying; the bucket pull overturned it -> verify inherited claims.

## Pending external actions
None pending. (Analysis + docs only; no sends, no commits beyond the close commit.)

## Cascade
- NFE: new `3_UK/2_analysis/yodel_negotiation_levers.md` (committed, standing NFE auth, pathspec-scoped, never push).
- Pre-existing `M` on `3_UK/2_analysis/dpd_uk_goforward_surcharges.md` is NOT mine -- left untouched.

## Main-brain changes
- This quest-log entry + `inventory/uk-yodel-negotiation-levers-resume__47bed7aa.md`.
- Bank drafts: `2026-06-19-uk-yodel-negotiation-levers.md`, `2026-06-19-uk-offshore-dpd-ups-cost-blowout.md`.
- Examine draft: `2026-06-19-verify-inherited-analysis-claims.md`.
- Comms: jebrim-47bed7aa OPEN + CLOSING.

## Post-close addendum (2026-06-25 -- session reopened for read-only follow-ups)
> Date note: the S277 writes above were mis-dated 2026-06-19; this session actually ran 2026-06-25. sid8 (47bed7aa) is the identity, so low-harm -- flagged for accuracy.

1. **OOG GBP 1/3/15 mechanic.** These are the per-service col-T **mis-booking / upgrade penalties** (book a parcel
   on a tier too small -> pay that tier's fee + GBP 1 (booked Small) / 3 (Medium) / 15 (Large)). We hit the GBP 1
   only by booking an actually-Medium parcel as Small. NOT in our cost model -- the re-rate books each parcel to
   the smallest tier it fits, so GBP 1/3 are avoidable booking errors, not structural cost. Only the genuine
   over-Large GBP 15 (120-170cm) / GBP 50 (>170cm or >160L) bands are modeled. (Confirmed vs `yodel_rate_card.md` + Stefan's OOG answers.)
   Operational flag: holds only if our label/booking logic assigns the correct service -- worth a check (billing-leak, not tender cost).
2. **Red-team delivered + RUN.** Handed the principal a sanity-check prompt; **S282 (sid 9d9e0b14) executed it** ->
   the 3 options STAND (audit + 4 open actions appended to the resume). Headlines: existing GBP 288,058 = RAW
   INVOICED ACTUAL (not a reprice); fuel 18% still current (trending down); levers land within +-GBP 80 of 0%.
   Open: physical dim-check of the 60x40 box; **70cm-ALONE only closes ~65% of the gap** (comms exposure to confirm
   what was put to Maersk); go-forward truck reframe (3,700->3,620 already happened -> honest gap ~GBP 3.8k bigger).
3. **"Which packages" reclassify at 64->70cm Medium cap** (live mart, Q1 GB invoiced TCG): 21,662 whole / 20,626
   mainland, almost entirely **WICKELVERPACKUNG 60x40** (the canvas wrap) = 20,691 parcels, **ALL exactly 65cm long**,
   mid exactly 41.0, short 3-6cm, ~1-2kg -> miss Medium by **1cm on LENGTH**. A 64->65cm cap nudge captures the whole
   pool. This is DISTINCT from (and ~12x larger than) the red-team's 60x40 Box-in-the-Box pool (1,679, misses on
   42.1cm WIDTH). Both rest on DECLARED dims -> the same physical-measure check (resume open-action #1) applies to both.

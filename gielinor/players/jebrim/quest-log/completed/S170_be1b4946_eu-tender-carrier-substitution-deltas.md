# S170 — EU-tender carrier-substitution deltas (Hermes / UPS / DPD)

**Player:** Jebrim · **Session:** be1b4946 · **2026-06-09** · **Status:** completed (analysis shipped to bank draft; DPD thread handed to a sibling session, UPS +5% sensitivity not pursued)

Read-only analysis over the [[S166_f82b01df_routing-service-split-build|S166]] routing output (`routing_2026q1/routing_assignment.parquet` + `cost_matrix_2026q1`) + the existing carrier contracts in `5_shipping_savings/contracts/`. No mart writes; one bank draft + harvest.

## What was asked / delivered

1. **Hermes 62,299-parcel slice — cost delta vs alternatives.** vs DHL +€1.11M/Q (+341%); vs Maersk +€1.18M (+359%); vs UPS (real invoice on the 54,107 it shipped) +€47k (+18.6%). Driver verified: DHL/Maersk apply ~€20 bulky/Sperrgut surcharge to the long DE wrapped formats (WICKEL/STANZ/Platten, LPG ~220–310cm); Hermes carries them flat; UPS doesn't surcharge them. → **SAVED** to `bank/drafts/notes/projects/2026-06-09-hermes-slice-carrier-delta.md`.

2. **Drop-UPS counterfactual.** The 45,654 parcels routed to UPS, rerouted to cheapest of remaining 5 = **+€289k/Q (70% of the whole €411k routing saving)**. UPS is load-bearing — FR €129k, AU €54k, DE €39k, CH €31k, NL €23k; no clean substitute (UPS uniquely cheap on FR/overseas/heavy). Mirror of the Hermes finding (Hermes droppable €73k / 18%; UPS not). → **SAVED** to the same note (companion section).

3. **DPD PL new offer vs existing** — analysis done, then **PARKED / handed to a sibling session** that holds the DPD offer in memory. Key result: existing actuals (~€4.56/pc) reconcile to the `Direct, special offer` tier (NOT the `export MIX HOME service` list sheet — comparing to that flips the sign to a false −20.6%). New offer (dpd_pl-2.0.0 engine, all-in ~€5.55/pc) is **~+19% more expensive** (~€58k/Q, ~€230k/yr indicative) — a price increase, not a saving. Handoff block given to principal to paste into the sibling session. NOT saved to a note (parked).

4. **UPS contract recon** (`5_shipping_savings/contracts/.../UPS/UPS Contract 04.24.pdf`). No fixed expiry (evergreen, blank term dates, auto-renews indefinitely, 30-day cancellation, signed 25 Apr 2024); **no GRI clause** — rates float on UPS's published tariff (GRI'd rates live in `Picanova UPS Rate Card 2026.xlsm`); our pricing is a fixed discount off it.

5. **UPS new-vs-old +5% sensitivity** — teed up (the S163 `replay.parquet` carries `ups_total_eur` new + `real_total_eur` actuals per parcel) but **not pursued** — principal realised mid-thread he was in the wrong terminal and wound the session down.

## Corrections this session (harvested)

- Asserted "no current DPD contract card in the repo" after searching only `2_EU_tender_2026/`; it was in `5_shipping_savings/contracts/`. → examine draft `2026-06-09-searched-one-project-then-asserted-repo-wide-absence` (instance of never-assert-absence).
- DPD comparison flipped sign on the wrong existing tier. → examine draft `2026-06-09-reconcile-contract-tier-against-actuals-before-offer-comparison` + cross-conv memory `feedback_reconcile_contract_tier_against_actuals`.

## Pending external actions

No pending external actions. (Read-only mart/contract analysis; brain-side bank draft + examine drafts + comms only.)

## Notes for whoever picks up DPD

Full handoff in this session's chat. The operative existing tier = `Direct, special offer` (reconciles to actuals); the new offer is ~+19% pricier; open task = build the all-in existing-contract pricer for a signable number, or model the drop-DPD scenario.

# Size an artifact's impact on the booked basis, not the model layer

**Observation ([[S202_276897ca_eu-tender-negotiation-levers|S202]], 2026-06-11).** I summed the `dhl_paket` engine's Sperrgut column over the plan's DHL parcels (€72.6k Q1) and claimed first "the plan pays €332k/yr of Sperrgut — negotiate it away" and then, after the phantom was exposed, "the headline is understated by ~€313k/yr." Both wrong the same way: the routing books **incumbent keeps at invoice actuals** (March-anchored, q04c/q09) — the engine prices only challenger bids and switches. The €20 was never in the headline for the 3,318 kept parcels. Niklavs's "it's not like our portfolio routes in a way that we plan to pay this" unwound it; real exposure was €29k/yr (314 engine-priced switches) plus a conditional unlock on suppressed switches.

Two compounding sub-faults the same thread surfaced:
- **Invented mechanism:** I explained the Sperrgut hits as "rolls are auto-non-conveyable" without reading the trigger — `bulky_de.py` is purely dimensional (d_mid > 60; template said 60.5). Read the trigger code before narrating a mechanism.
- **Stale derived artifact:** mid-verification I read `routing_table_final.csv` as "the routing layer" — its carrier mix didn't match the live plan (pre-gating era file). Caught by cross-checking parcel counts against `routing_assignment.parquet`.

**Rule.** Before claiming a model artifact moves a reported number, trace which **cost basis the reporting layer books for that slice** (keep vs switch, actuals vs engine) — a per-component sum over a model layer is not the booked plan. Corollary of [[2026-05-31-rerating-trust-gate-grain-and-cost-basis|trust-gate-grain-and-cost-basis]], on the reporting side.

# UPS 2026 offer vs today — cost-jump drivers + GRI treatment

**Context ([[S209_89e4a123_carrier-overview-v2-rederive|S209]]).** Decomposed why the UPS new-offer mean sits above today's invoiced UPS cost on the segments where UPS wins the tender field (carrier_overview_v2 "hollow vs today" slices). Decomposed from the engine component columns (`cost_matrix` ups rows: cost_base derived + cost_fuel + cost_lps + cost_oversize_disputed + cost_line_haul + cost_residential + cost_fee_tail) vs the 2026-Q1 actuals (`real_base_eur` / `real_fuel_eur` / `real_oversize_eur` / `real_truck_eur` …).

## Drivers by lane

- **CH (+65–78%) = the operative-tier BASE.** Engine base €12.01 vs today's €7.49. Today's CH base rides an arrangement **neither UPS rate-card file shows** (old card €11.44, new offer €12.01); the operative tier is ~€7.48. The offer prices CH at the flat "Schweiz column" → +56% base; fuel rides on top (20%). This is the **parked CH/GB operative-tier finding** ([[S205_f08474c9_ups-round1-reply-review|S205]]/[[S206_01871b26_ups-2.0.0-engine-build|S206]]) — `1_offers/picanova/UPS/findings.md`. Revisit trigger = **before signature**. ~€360k/yr swing. Negotiable, or route CH bulky to Güll. Low volume.
- **Nordics (+27%) = higher base tier (~€1.5) + oversize/LPS layer (~€1.3).** The oversize part is the by-bill LPS/OML layer (UPS's own dimensioner) — disputable (the standing ~€1.44M dispute). Low volume.
- **FR (+4–6%) = basically flat.** Base equal to ±€0.15; the small gap is fuel-timing (today = 2026-Q1, new = 2025 window). FR is the high-volume slice (~7k parcels). Not a real increase.
- **Line-haul is a wash.** Today's invoices already carry ~€0.72/parcel "truck" (injection trucking) = the engine's €0.75 `cost_line_haul`. Not a driver of any gap.

## GRI treatment (decision-relevant)

- **carrier_overview "vs today" = GRI-free** — the raw 2026-Q1 invoice, OML-netted, no forward GRI. Conservative bar.
- **routing/decision report applies the GRI keep-side-only** — do-nothing = today × (1 + 5% GRI) for UPS (its tariff floats, no cap, [[S170_be1b4946_eu-tender-carrier-substitution-deltas|S170]]); new offers enter at **face value** (year-1 fixed). The +5% = €52,244 on the €1.13M UPS book (most of the €100k "rate moves" do-nothing step). Published 2026 GRI = 5.9%; model uses 5% (mildly conservative).
- **Against the GRI'd-forward:** FR slices flip to break-even+ (FR Std 2–5 → €7.34, FR Bulky 1–2 → €7.25 vs offer €7.38 / €7.18); CH/Nordics stay (tier + oversize, a 5% GRI doesn't close them). Matches `findings.md` (offer ~6–14% cheaper than current GRI'd billing on the EU core).

**Decision (Niklavs, [[S209_89e4a123_carrier-overview-v2-rederive|S209]]): sign the offer.** The contract is being replaced → "keep today" is off the table. Negotiate the CH operative tier before signature (or route CH bulky → Güll); dispute the Nordics oversize/LPS. See [[2026-06-11-vs-today-baseline-assumes-incumbent-persists]]. Domain: [[eu-tender]] / [[carrier-contracts]].
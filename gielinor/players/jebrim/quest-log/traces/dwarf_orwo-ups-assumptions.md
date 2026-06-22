# Dwarf trace — ORWO UPS calculator: modeling assumptions (logistics-manager review)

READ-ONLY extraction, 2026-06-22. Source repo: `bi-analytics-main/NFE/projects/7_ORWO_tender_2026/`.
Engine dir: `repricing_base/carrier_engines/ups/`. Contract review: `contracts_review/ups.md`.

Engine version stamped `orwo-ups-1.0.0` (constants.py:4). Trust-gate: portfolio base ratio
**0.971**, cost_total ratio **0.942**, on **58,731 eligible parcels** (README:29-45).

Format per item: What / Value / Why / Confidence / Needs-confirmation / Cite.

---

## A. LOAD-BEARING for the headline €17k H1 / ~€34k–€50k/yr saving

### A1. Fuel held FLAT at 17.5% of base (not the contractual "35%-off floating index")
- **What:** Standard-card fuel surcharge modeled as a flat scalar on base freight.
- **Value:** `FUEL_PCT = 0.175`; `cost_fuel = base × 0.175` (Standard only; €0 on Economy DDP).
- **Why:** Contract is "35% off a floating monthly index," not a fixed %. Calibrated to the
  invoiced fuel/freight ratio (≈0.175 across DE/AT/FR/CH, 2026 H1). Floating-index refinement
  deferred to Phase 3. (Stated in code comment.)
- **Confidence:** FLAGGED-ASSUMPTION (calibrated to actuals, but a static stand-in for a floating index).
- **Needs-confirmation:** Internally validated against H1 actuals. Forward exposure (the actual UPS
  fuel index path) needs external/UPS confirmation. Note: applies to BOTH baseline and offer, so it
  "barely moves the delta" (offer_summary.md:57-58) — but it scales the absolute spend the % is taken on.
- **Cite:** constants.py:13-18; calculate.py:92-93; README:50-52; offer_summary.md:57-58.

### A2. Economy DDP (GB/US) fuel is NOT added — bundled into residential
- **What:** No explicit fuel line for the GB/US Economy DDP tail; DDP fuel "modeled as resid."
- **Value:** `cost_fuel = 0.0` for card == economy_ddp.
- **Why:** "DDP fuel is bundled differently — invoiced GB/US fuel ≈ 0.46/0.16 per parcel, modeled as
  resid below." (constants.py comment.)
- **Confidence:** FLAGGED-ASSUMPTION (the residential scalar A3 is doing double duty as DDP-fuel proxy).
- **Needs-confirmation:** Internal — but the residential scalar wasn't actually tuned to absorb the
  GB/US fuel (€0.46/€0.16); this is a stated approximation. Worth a logistics-manager flag.
- **Cite:** constants.py:16-17; calculate.py:90-93.

### A3. Residential surcharge as one flat EXPECTED scalar (€0.16/parcel everywhere)
- **What:** Residential delivery charge applied as a portfolio-flat expected value, not per-lane incidence.
- **Value:** `RESIDENTIAL_EUR = 0.40`, `RESIDENTIAL_INCIDENCE = 0.40` → €0.16/parcel, added to EVERY
  eligible parcel regardless of lane.
- **Why:** €0.40/shp flat charged on residential deliveries only; 0.40 incidence calibrated to TB lanes.
  Per-lane incidence (DE ~0.03, GB/US ~0, TB ~0.16) is "a refinement."
- **Confidence:** FLAGGED-ASSUMPTION / PLACEHOLDER for the incidence figure (0.40 is a single tuned constant).
- **Needs-confirmation:** The 0.40 incidence is internally calibrated to TB lanes but is known-wrong
  per-lane (over-charges DE and GB/US, where real incidence ≈0). Residential flag population in the mart
  is an open question (contracts_review ups.md:280 Q5). Logistics-manager confirmable.
- **Cite:** constants.py:20-25; calculate.py:94; README:53-54.

### A4. CH light-parcel rate cut drives ~66% of the saving
- **What:** The headline saving is almost entirely the CH 1–3kg band cut (€11.44→€8.04) plus DE mid-weight.
- **Value:** CH −€11,220 (−29.2%), DE −€5,732 (−11.2%); all other 47,049 trks €0 (rates identical).
  Total €16,973 H1 (4.4%).
- **Why:** Offer cherry-picks lanes where UPS had headroom; holds AT + EU transborder flat.
- **Confidence:** FIRM (modeled-vs-modeled on identical parcels and identical component model).
- **Needs-confirmation:** Internally validated. But see A5 (counterfactual) — the €34k is a floor, not the value.
- **Cite:** offer_summary.md:18-27.

### A5. Saving counterfactual = "today's rates frozen" (CONSERVATIVE floor, wrong do-nothing)
- **What:** The €17k/€34k is offer-vs-today-frozen, which credits €0 to every lane the offer holds flat.
- **Value:** €16,973 H1 / ~€34k/yr at frozen-today. Corrected go-forward basis (today + next GRI) ≈ **~€50k/yr**.
- **Why:** UPS applies an annual General Rate Increase (GRI); ORWO net rates are discounts off a published
  tariff that rose 21 Dec 2025. "Holding a lane flat IS a saving = the GRI avoided." EU-tender canon:
  compare on do-nothing-at-new-rates.
- **Confidence:** FLAGGED — the €50k uses a placeholder **5% GRI** ("Rough sizing"; "Needs the actual ORWO GRI %; chase item").
- **Needs-confirmation:** EXTERNAL — the actual ORWO/UPS GRI % is an explicit chase item. Load-bearing
  for which number is presented (€34k vs €50k).
- **Cite:** offer_summary.md:30-49.

### A6. Annualization = flat ×2 on the H1 invoice window
- **What:** H1 figure doubled to annualize; no seasonality.
- **Value:** `ANNUALIZE = 2.0`.
- **Why:** Silver invoice window ≈ Jan–Jun 2026 = H1. EU-tender per-country seasonal-ratio method would
  refine it ("CH/DE seasonality could shift the €34k by single-digit %").
- **Confidence:** FLAGGED-ASSUMPTION / rough.
- **Needs-confirmation:** Internal (refine with seasonal ratios). Single-digit-% effect on the headline.
- **Cite:** offer/compare_offer.py:35-37; offer_summary.md:60-61.

---

## B. SCOPE / EXCLUSION assumptions (what the model does NOT cost)

### B1. surcharge_other (~6% of carrier cost) is UNMODELED
- **What:** A lane-diffuse surcharge tail is excluded from the modeled cost entirely.
- **Value:** ~6% residual; cost_total ratio 0.942 vs invoiced. Buckets: Surge Fee, Aussengebiet, große
  Pakete, Änderung, address-correction.
- **Why:** "Not card-reproducible"; small and lane-diffuse; base+fuel is the card-grade core that gates.
  The offer doesn't touch it so it nets out of the delta.
- **Confidence:** FLAGGED-ASSUMPTION (documented exclusion; sized as the reconciliation residual, Phase 3 if needed).
- **Needs-confirmation:** Internal. Logistics-manager should know the headline excludes ~6% of real spend.
- **Cite:** README:42-45, 66; offer_summary.md:55.

### B2. Tax / duty pass-through EXCLUDED by construction
- **What:** Import VAT, customs, brokerage fees stripped — not carrier-comparable cost.
- **Value:** `invoiced_carrier_total = total_all − taxduty`. taxduty bucket enumerates 14 charge
  descriptions (19% Tax, Einfuhrumsatzsteuer, Zoll, Vorlageprovisionsgebühr, WWE Importzoll, etc.).
- **Why:** Tax/duty is pass-through, not a carrier-comparable cost; base population already strips it (sql/02).
- **Confidence:** FIRM (correct by construction for a carrier comparison).
- **Needs-confirmation:** Internal.
- **Cite:** constants.py:27-28; run_gate.py:44, 58-64.

### B3. LPS / Overmax dimensional surcharges NOT modeled (dims ~77% NULL)
- **What:** Large-Package and Overmax-Size surcharges, NOT waived in the contract, are absent from the engine.
- **Value:** Thresholds: any dim >25cm → LPS; any dim >19cm → Overmax. Neither waived in Addendum C.
- **Why:** ~77% NULL dims → cannot determine whether they fire; engine prices weight×country only.
  (These likely fall inside the B1 surcharge_other residual where invoiced.)
- **Confidence:** PLACEHOLDER-gap (exposure present but unquantifiable).
- **Needs-confirmation:** EXTERNAL/data — needs dims coverage. Open question ups.md:279 Q4.
- **Cite:** contracts_review ups.md:188-200, 219-220, 242, 279.

### B4. Premium air products (Express Saver / Expedited / Express Freight) NOT modeled
- **What:** The offer card carries premium-air sheets; the engine ignores them.
- **Value:** Not built into rate tables.
- **Why:** Only relevant if GB/US move off Economy DDP onto premium — which would RAISE cost, not lower it.
- **Confidence:** FIRM scope decision.
- **Needs-confirmation:** Internal (only matters under a service-mix change).
- **Cite:** offer_summary.md:50-51; contracts_review ups.md:165-178.

---

## C. ROUTING / RATE-CARD structural assumptions

### C1. Routing by destination country (GB/US → Economy DDP; rest → Standard)
- **What:** Each parcel reprices on exactly one card, chosen by destination.
- **Value:** `DDP_COUNTRIES = {"GB","US"}`; everything else Standard.
- **Why:** Mirrors how the invoiced book actually billed.
- **Confidence:** FIRM (validated against invoiced billing).
- **Needs-confirmation:** Internal.
- **Cite:** constants.py:6-8; calculate.py:57-61; README:22-27.

### C2. Two specific contract cards are authoritative (Q6842839DE Standard + 0R6D66 Economy DDP)
- **What:** Rates parsed from named xlsm/xlsx sheets; -01 net rates asserted identical to live -02.
- **Value:** Standard = sheet "DE E-Standard Single" of Q6842839DE-01 xlsm; DDP = "01_UPS TM Economy
  DDP - Versand" of 0R6D66. Standard country-keyed; DDP zone-keyed.
- **Why:** -01 net rates "identical to the current -02 contract" (asserted, contracts_review §7 confirms same values).
- **Confidence:** FIRM (trust-gated to the cent in rate_cards.md; -01=-02 cross-checked in ups.md §7).
- **Needs-confirmation:** Internal; the -01≡-02 equality is asserted from a contract diff (ups.md:252-268).
- **Cite:** build_rate_tables.py:6-12, 36-40; README:34-45; contracts_review ups.md:252-268.

### C3. Weight banding = forward as-of ("any fraction over takes the next band")
- **What:** Base rate = smallest weight band ≥ billable weight, within country.
- **Value:** `join_asof(..., strategy="forward")`.
- **Why:** Card pricing rule "any fraction over takes the next band."
- **Confidence:** FIRM.
- **Needs-confirmation:** Internal.
- **Cite:** calculate.py:36-50; build_rate_tables.py:16-18; README:13-14.

### C4. Billable weight = COALESCE(billedweight, actualweight) — no volumetric/dim weight
- **What:** Billable weight prefers carrier billed weight, falls back to actual; volumetric weight NOT computed.
- **Value:** `COALESCE(MAX(billedweight), MAX(actualweight))`. README: "no dims in the base — 5/5 contracts price that way."
- **Why:** ORWO reprices on weight×country alone; 5/5 contracts price without dims in the base. BUT the
  Economy DDP contract clause prices on max(actual, volumetric) — so for bulky-light DDP parcels, billed
  weight (hence cost) may be systematically understated where dims are NULL.
- **Confidence:** FLAGGED-ASSUMPTION (the COALESCE leans on billedweight being present and already
  volumetric-adjusted; risk concentrated on bulky-light GB/US).
- **Needs-confirmation:** EXTERNAL/data — dims coverage + UPS dim divisor (ups.md:281 Q6, 5000 cm³/kg intl assumed).
- **Cite:** run_gate.py:47; calculate.py:3-7; README:5-6, 49; contracts_review ups.md:191, 237, 246, 281.

### C5. MAX_WEIGHT_KG eligibility ceiling
- **What:** Parcels over the negotiated ceiling rejected as ineligible (over_max_weight).
- **Value:** `MAX_WEIGHT_KG = 70.0` (UPS Standard / Economy DDP, "Q9 negotiated").
- **Why:** Eligibility ceiling stated in the contract.
- **Confidence:** FIRM.
- **Needs-confirmation:** Internal (contract-sourced).
- **Cite:** constants.py:10-11; calculate.py:84.

### C6. Postal-split countries collapse to one primary card column
- **What:** Countries split across multiple postal zones (DK, GB) mapped to a single primary column.
- **Value:** STD column→country map (build_rate_tables.py:47-66). DK→Zone-4 col M; GB Standard collapsed.
- **Why:** "Postal-split countries collapse to one primary column — those lanes are immaterial in ORWO
  (GB ships Economy DDP)." Chosen columns reproduce invoiced freight to the cent per rate_cards.md.
- **Confidence:** FLAGGED-ASSUMPTION for the known-wrong tails (see C7), FIRM for material lanes.
- **Needs-confirmation:** Internal (immaterial residuals documented).
- **Cite:** build_rate_tables.py:42-66; README:56-64.

### C7. Documented immaterial mismatches (GB zone-35 tail, DK, NO)
- **What:** Three known small lane-level mis-prices, left unfixed as immaterial.
- **Value:** (a) GB zone-35 tail (~9% of GB) reprices at zone-34 → pulls GB base_ratio to 0.911;
  (b) DK (15 trks) keyed to Zone-4 €6.08 vs invoiced ~€4.93; (c) NO (3 trks) invoiced ~€41 remote-area
  surcharge vs modeled €13.68 Zone-6.
- **Why:** All immaterial to portfolio; fixes documented but not built (GB fix = carry silver zone, key DDP by 34/35).
- **Confidence:** FLAGGED-ASSUMPTION (known errors, accepted as immaterial).
- **Needs-confirmation:** Internal.
- **Cite:** README:56-66.

### C8. Economy DDP keyed by country, NOT by zone (GB→34, US→33 only)
- **What:** DDP rate table built from only two zone columns; GB zone-35 / other DDP zones not carried.
- **Value:** `DDP_COL_COUNTRIES = {"AJ":["US"](z33), "AK":["GB"](z34, ~91% of GB DDP volume)}`.
- **Why:** GB/US are the only DDP lanes ORWO actually ships; zone-35 is a small tail (see C7a).
- **Confidence:** FLAGGED-ASSUMPTION (drives the GB 0.911 gate miss).
- **Needs-confirmation:** Internal.
- **Cite:** build_rate_tables.py:70-78.

---

## D. GATE / VALIDATION assumptions (how "correct" is claimed)

### D1. Trust-gate target: modeled base ≈ invoiced freight per lane (ratio ~1.0)
- **What:** Correctness = per-lane base_ratio near 1.0 against live invoiced freight.
- **Value:** Portfolio base 0.971; every material lane 0.98–1.00 (AT 0.998, CH 0.999, DE 0.979,
  FR 0.998 …); GB 0.911† and US 0.95† flagged. cost_total 0.942.
- **Why:** Per-parcel proof the engine reproduces what was billed.
- **Confidence:** FIRM result, but note the gate validates BASE (+fuel), not the full carrier total (D2).
- **Needs-confirmation:** Internal (live DB pull, 58,731 parcels).
- **Cite:** README:29-45; run_gate.py:91-108.

### D2. "Freight" bucket = a specific allow-list of charge descriptions
- **What:** Invoiced "freight" (the gate denominator) is the SUM over an enumerated charge-description set.
- **Value:** freight ∈ {Dom. Standard, TB Standard, Economy DDP, WW Standard, WW Express Saver, WW
  Expedited, UPS WorldEase WW Expedited, Beförderung, + 2 Undeliverable Return types}. Fuel =
  LIKE '%Treibstoffzuschl%'. Resi = 3 Privatzustellung descriptions.
- **Why:** Bucketing mirrors sql/02; isolates card-reproducible freight from surcharges/tax.
- **Confidence:** FIRM (but the allow-list IS the definition of "freight" — anything mis-bucketed shifts the ratio).
- **Needs-confirmation:** Internal; the charge-description allow-list is a modeling choice worth a spot-check.
- **Cite:** run_gate.py:49-64.

### D3. Base population = invoices-only, freight>0, weight-non-null
- **What:** Gate/saving population filtered to billed parcels with positive freight and a known weight.
- **Value:** `WHERE freight > 0 AND billable_weight_kg IS NOT NULL`; one row per trackingnumber.
- **Why:** Engine needs a weight and a positive freight to reprice/compare.
- **Confidence:** FIRM, but introduces selection: parcels with NULL weight or zero freight are silently
  excluded from both gate and saving (not quantified in the engine output).
- **Needs-confirmation:** Internal — but the excluded-parcel count/spend isn't surfaced; logistics-manager
  may want the coverage fraction.
- **Cite:** run_gate.py:69, 46.

---

## Quick triage for the logistics manager
- **Must-confirm externally:** A5 (actual GRI % — decides €34k vs €50k), A1/A2 forward fuel path,
  C4/B3 dims+divisor (bulky-light DDP understatement).
- **Known-approximate but immaterial:** A3 residential incidence, A6 ×2 annualization, B1 surcharge_other
  6% tail, C6/C7/C8 lane-tail mis-prices.
- **Firm / validated:** C1–C3, C5, B2, B4, D1 (gate 0.971 on 58,731 parcels).
- **The saving is real but conservative:** A4 is firm modeled-vs-modeled; A5 says the presented number
  is a floor and the proper basis needs the GRI %.

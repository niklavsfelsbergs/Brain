# [[S034_2026-05-22_eu-tender-logic-review|S034]] D2 — DHL Paket + DHL Express audit
**Spawned by:** Jebrim, 2026-05-22

## TL;DR

Both DHL engines are in clean structural shape. No catastrophic calc bug. The fuel-aware `_select_service` fix in DHL Express (2026-05-14) looks correct under TDI 0.45 / DDI 0.12. The Kleinpaket wire-up in DHL Paket (2026-05-14, `dhl_paket-1.1.0`) looks correct on selection / eligibility / Toll&CO2 filtering. The bugs that remain are second-order:

- **DHL Express M1 (med)** — fuel-aware service-selection's `pick_es` is `≤` (ES wins ties) while DHL Paket's Intl Premium-vs-Economy uses `≤` (Premium wins ties). Inconsistent tie-break direction across the two engines. Immaterial in practice (true ties are vanishingly rare on continuous rate × fuel).
- **DHL Paket H1 (med)** — `_attach_de_rate` does `pl.concat([de_priced, other], how="diagonal").sort("shipment_id")`. This re-orders the entire dataframe by `shipment_id`. The rest of the pipeline assumes input row order is preserved (Maersk-style). Output rows therefore arrive in shipment-id order, not input order. Not wrong, but it's an undocumented row-reorder partway through the pipeline; downstream consumers ordering by shipment_id are fine, anyone keying off input order is not.
- **DHL Paket H2 (med)** — Several `_decide_eligibility` reject reasons get labelled `country_not_served` via the final null-service catch-all on line 432, even when the true reason is "no eligible service after upstream filters chose nothing." Edge case only — every realistic failure path has its own categorical reject earlier in the chain.
- **DHL Paket H3 (low)** — `Peak` and `PeakInPeak` use `shop_order_created_date` not `ship_date`. Engine fills missing date with `2026-01-01` (outside any peak window) — so safe on the Q1 2026 population, but for Q4 scoring the production-lead-time gap (created Oct 30 → shipped Nov 1) systematically *under-stamps* peak. Open question Internal #8 in `open_questions/dhl_paket.md` already flags this.
- **Missing-assumption observations (both engines)** — see Cross-carrier section.

The existing per-carrier open-questions files (`docs/open_questions/dhl_paket.md`, `dhl_express.md`) already cover the substantive open levers (Bulky envelope, Stettin pickup, fuel histories, PCS PL pickup, customs, Remote Area, etc.). This audit confirms those are the binding gaps and adds the small calc-discipline items above plus a few missing-assumption captures.

---

## DHL Paket — calc bugs / wrong assumptions / missing assumptions / OK

### Calc bugs

**H1 (med). Row-reorder in `_attach_de_rate`.**
`carriers/dhl_paket/calculate.py:218` — `return pl.concat([de_priced, other], how="diagonal").sort("shipment_id")`. The function processes DE rows via forward-asof (sorted by weight, then restored with `_row_id`) and concats non-DE back, then **sorts the whole frame by `shipment_id`.** All downstream phases (`_price_all_services` continues with `_attach_kp_rate` / `_attach_intl_rate`, then `_select_cheapest`, etc.) inherit this sorted-by-shipment-id ordering. **Expected behavior:** input row order is preserved across the pipeline (matches the `_row_id` discipline used inside `_attach_de_rate` itself, and matches the DHL Express engine which uses `shipment_id` joins back). **Magnitude:** zero on cost values; only affects ordering of the returned DataFrame. Tests that compare positionally (`.row(0)` etc.) on the output will see input-order != output-order if the caller hasn't sorted. Fix: restore the `_row_id` pattern across the whole concat, or document the row-reorder in the engine docstring.

**H2 (low). Reject-reason mislabel via service-null catch-all.**
`carriers/dhl_paket/calculate.py:432` — `pl.when(pl.col("service").is_null()).then(pl.lit("country_not_served"))`. This is the penultimate clause in the reject-reason chain. **In practice** every realistic failure path is caught earlier (`no_service_country`, `over_weight`, `de_bulky_over | intl_bulky_over`), but if a future path produces a null `service` without matching any upstream reason, it will be mis-labelled `country_not_served`. **Expected:** a categorical reject reason that reflects the actual cause. **Magnitude:** semantic only; cost numbers unaffected.

**H3 (low). Peak / Peak-in-Peak driven by `shop_order_created_date`, not `ship_date`.**
`carriers/dhl_paket/surcharges/peak.py:36`, `peak_in_peak.py:32`. Picanova's production lead-time means a parcel "ordered" Oct 30 might "ship" Nov 1 (inside the Peak window). Engine fills missing date with `2026-01-01` (line 127 in `calculate.py`) so for Q1 2026 replay there is **zero impact** (no parcels in Peak window). **For full-year Q4 scoring** the engine **under-stamps Peak** (orders made before Nov 1 but shipped in November don't fire). Open Internal #8 already flags this. Engine-correct against ASSUMPTIONS as currently documented; flagged here only because the doc says "Peak surcharge -- Nov+Dec ship dates" while engine uses `shop_order_created_date`. Date-column convention should be made explicit in ASSUMPTIONS.

### Wrong assumptions

None found — the documented assumptions and engine state are consistent (Bulky sorted-dim reading, Toll&CO2 exclusion from Kleinpaket, CH "customs included" reading, 100 g rounding, MAX_WEIGHT_KG = 31.5, named-country fuel set CA/US/AU, etc.). The five Blocks (B1 Bulky 120×60×60, B2 DE Energy history+scope, B3 Z4-6 TCS, B4 Stettin pickup, B5 volume lock) in `open_questions/dhl_paket.md` cover everything substantively open.

### Missing assumptions

**M1 (low). Peak date-column convention.** ASSUMPTIONS.md and DECISIONS.md both say "Peak/Peak-in-Peak applies on Nov-Dec ship dates" — but the engine uses `shop_order_created_date`. ASSUMPTIONS should explicitly state which date column drives the window (and how missing dates default). Today the answer is hidden in `calculate.py:125-128` (default to `2026-01-01`).

**M2 (low). `_INTL_FUEL_NAMED_456` membership convention.** Engine's `_INTL_FUEL_NAMED_456 = {CA, US, AU}` is documented in ASSUMPTIONS under the 2026-05-13 v1 placeholders table. **But the corollary** — every other PREMIUM_NAMED key (BE, DK, FR, LU, NL, AT, PL, GB, CH, IT, SE, ES, FI, IE) sits in Z1-Z3 and therefore takes 0% fuel — isn't explicitly stated. If DHL re-zones a named country (e.g. shifts NL to Z2 with TCS coverage), the engine silently keeps it at 0% TCS. Low impact today; worth pinning in ASSUMPTIONS as an explicit list of "named countries known to inherit zone-fuel" (CA/US/AU) and "named countries known not to take TCS" (the other 14).

**M3 (low). Multi-piece vs per-shipment grain.** Cross-carrier ASSUMPTIONS already says "each shipment_id priced independently." For DHL Paket specifically, the offer says nothing about multi-piece discounting, so the per-row treatment is correct, but the assumption could be re-stated in the DHL Paket section explicitly (parallel to the open `dhl_express.md` C7 note for DHL Express).

### OK / confirmed-correct on this audit

- Forward-asof DE weight bands; rate parquet shape verified through `extract_rates.py`.
- Intl 100 g rounding (`ceil(kg * 10) / 10`) — matches offer footer.
- Cheapest-eligible service-pick: DE Paket vs Kleinpaket includes the 0.19 EUR Toll&CO2 differential, Premium vs Economy correctly cancels Toll (both pay it) and Bulky (both same).
- `_intl_billable_kg` is the field used for the Intl weight cap, matching the eligibility convention against the rounded billable not the raw `weight_kg`. The raw `weight_kg > 31.5` is used in `_decide_eligibility.over_weight`, which catches the same set on the DE side. No double-jeopardy or miss.
- Toll&CO2 service-filter (`service != SERVICE_DE_KLEINPAKET`) correctly excludes Kleinpaket per master offer p.12.
- DE eligibility softening (parcels failing Paket bulky cap stay eligible if Kleinpaket envelope holds via `de_bulky_over & ~_kp_eligible`) — line 419 — correct.
- Kleinpaket envelope check uses sorted dims (d_max/d_mid/d_min) — matches the engine intent (Internal #3 question is about whether this is the offer's intent, not whether the engine implements it correctly).
- Fuel applied to base only (not Toll&CO2 or other surcharges) — documented engine choice; B2 question covers the scope ask.

---

## DHL Express — calc bugs / wrong assumptions / missing assumptions / OK

### Calc bugs

**E1 (med). `_select_service` tie-break direction inconsistent with DHL Paket.**
`carriers/dhl_express/calculate.py:186-193` — `pick_es = _es_base.is_not_null() & (_ww_base.is_null() | es_total <= ww_total)`. ES wins on tie. DHL Paket's Premium-vs-Economy at line 351-353 uses `_prem_compare <= _eco_compare` → Premium wins ties. Different default direction. **Magnitude:** zero in practice (continuous-rate ties don't occur on real fuel pcts). **Expected behaviour:** pick a consistent convention across engines or document why each direction is chosen (e.g. "ES is the road / lower-CO2 option, prefer on tie"). Worth a one-line ASSUMPTIONS note.

**E2 (low). `_select_service` join-back assumes `shipment_id` uniqueness.**
`carriers/dhl_express/calculate.py:167-176` — joins `ww_priced`/`es_priced` back to `df` on `shipment_id`. If the input has duplicate shipment_ids, the join multiplies rows. The Phase 2 mart schema is 1 row per shipment_id, so this is safe today; but neither the engine docstring nor a runtime assert enforces it. The DHL Paket engine has the analogous `_attach_de_rate` concat issue (H1). Add a uniqueness invariant check at entry.

**E3 (low). `Overweight.conditions()` checks `billable_weight_kg`, but offer's NC-by-weight says `actual weight`.**
`surcharges/overweight.py:28` — `(pl.col("billable_weight_kg") > OVERWEIGHT_TRIGGER_KG)`. Per offer (svc_desc_text.txt L1474, `S&S Published` row 783-784) Overweight Piece fires on **"chargeable weight more than 70 kg"** — chargeable = billable = max(actual, dim). So the engine is correct. **However:** sibling `nonconveyable.py:38` uses `pl.col("weight_kg")` (actual) for its 25-70 kg band, per the offer wording "actual weight between 25-70 kg". The two surcharges genuinely differ in which weight field they consult — billable for Overweight, actual for Non-Conveyable-Weight. Engine matches both correctly. Worth a docstring line in each file calling out the deliberate asymmetry (currently only Overweight's docstring says "actual OR volumetric").

**E4 (low). `Oversize` exclusivity-group never resolves anything in practice.**
`surcharges/oversize.py:27` / `overweight.py:20` / `nonconveyable.py:30` — `exclusivity_group = "oversize_overweight"` with priorities 2 / 1 / 3. **In practice:** Overweight never fires (rejected at 70 kg upstream), NonConveyable never fires (`pl.lit(False)` placeholder). So Oversize never competes. **Engine is correct;** flagged here only because the exclusivity-group machinery is dead code on this engine right now. If/when NC trigger is unlocked (B7 question), the priority chain becomes load-bearing.

### Wrong assumptions

None found at the level of "engine state contradicts the offer or a current decision." The 7 Blocks + 7 Changes in `open_questions/dhl_express.md` are all assumption-gaps rather than wrong-assumption-violations. The two highest-stakes gaps:

- **TDI 0.45 / DDI 0.12** are explicitly proxies pending Q1 2026 archived monthly history (B1/B2). The fuel-aware `_select_service` is mechanically correct under these proxies but the 86%/14% ES/WW mix is proxy-grade.
- **CUSTOMS_FLAT_EUR = 0** is the WA9 "option (a) vs (b)" deferred decision. Engine correctly applies zero customs on CH/non-EU under the placeholder; B4 in `open_questions/dhl_express.md` quantifies the under-pricing.

### Missing assumptions

**M1 (med). Fuel-on-surcharges scope.** Engine restricts fuel to base only. ASSUMPTIONS.md notes this ("`Fuel-on-surcharges | not modelled`") and the docstring of `_apply_fuel` calls it out (line 256-262). **But the magnitude is conditional** on which surcharges fire on Picanova volume, which is itself gated on B4 (customs) / B6 (remote area) / B7 (non-conveyable). Worth a one-line note that the engine's "<1% effect" estimate assumes all of those surcharges remain near-zero firing; if/when they unlock, the fuel-on-surcharges decision becomes load-bearing.

**M2 (low). Customs scope on non-EU TDI lanes.** Engine treats every non-EU country (TDI Zones 5-11) identically to EU destinations on the customs dimension (zero customs uplift). ASSUMPTIONS.md frames this as WA9 deferral and B4 in the open-questions file covers it. **But for the cross-engine cost matrix consumer**, the implicit fact that CH = "just another DDI Zone 5" without a CH-specific module (vs Maersk's `CH_ZAZ_EUR`, AP's `CH_CUSTOMS_INDIVIDUAL_EUR`, GLS's per-customs-shipment) is a silent missing-assumption that lives in code but not in ASSUMPTIONS. Worth elevating to "DHL Express has no CH-specific customs module; CH parcels priced as generic Zone 5" in ASSUMPTIONS.

**M3 (low). Service-tie-break direction.** See E1 — pin the tie-break direction (ES wins ties) in ASSUMPTIONS.

### OK / confirmed-correct on this audit

- Fuel-aware service selection (`base * (1 + fuel%)` per service, then cheapest wins) — matches WA1, fixed in `dhl_express-1.1.0`.
- `add_chargeable_weight(mode="max")` with `DIM_DIVISOR = 5000` — matches offer §3.
- Per-piece cap 70 kg, network length cap 300 cm — match service description §5.
- TDI / DDI zone tables loaded from offer Excel directly (single source of truth, no hand-coded zone overrides).
- `forward-asof` rate lookup — matches "rate of the rounded half-kilogram" on 0.5-kg-grid bands.
- OVERSIZE trigger `d_max > 100 OR d_mid > 80` — matches svc_desc_text.txt L1473-1476 verbatim.
- Exclusivity priorities OVERWEIGHT 1 / OVERSIZE 2 / NONCONVEYABLE 3 — match offer's "does not apply to pieces already subject to Overweight or Oversize" wording.
- RESIDENTIAL_EUR = 0 — confirmed waiver per WA8 and Net Surcharges sheet row 690.
- PEAK_PCT = 0.0 (Demand Surcharge "currently suspended") — matches WA6.
- DE Domestic Express not modelled — correct (Picanova ships from PCS PL, not DE).
- Returns lane not modelled — correct (cross-carrier OOS).

---

## Cross-carrier observations (anything that applies to both DHLs)

**CC1 (med). Both DHL engines do not model `Routing Code 0.49 EUR` (`Coding fee` per master offer p.5 / p.9 / p.14 / p.20).** DHL Paket open-question C5 documents this. DHL Express has an analogous concern via the Maersk-side DE DHL Routing Code 0.49 EUR pass-through. **Neither DHL engine has a surcharge module for it.** Worst-case worth EUR 254k Q1 on DHL Paket (always-on); realistic likely <EUR 3k. The asymmetry — DHL Paket flags it as a known open question, DHL Express does not even though the same offer concept exists in DHL Express's Address Correction (11 EUR) and Customs Services blocks — could be made symmetric in the cross-carrier "missing surcharges register."

**CC2 (med). Multi-piece consolidation discipline.** Both engines price one-row-in-one-row-out. Picanova-Stettin ships single-parcel HD, so multi-piece is structurally a non-issue today. But the cross-carrier ASSUMPTIONS row already locks "each shipment_id row priced independently" — and neither DHL engine carries an explicit assert or docstring statement on this. Worth a one-line invariant in each `calculate.py` docstring (DHL Paket already has it implicitly via the cheapest-pick logic; DHL Express less so).

**CC3 (med). Fuel scope discipline asymmetry.** DHL Paket applies fuel to base only AND models that as a Surcharge-list-bypass (fuel handled in `_apply_fuel`, outside `apply_surcharges`). DHL Express does the same. Both note "fuel-on-surcharges not modelled" as open. **But:** DHL Paket also has 14 named-country fuel routings (`_INTL_FUEL_NAMED_456`), whereas DHL Express has a single global fuel % per service. The asymmetry is offer-driven (DHL Paket's TCS is zone-specific; DHL Express's fuel is global). No bug, but the engines' fuel-application shapes are genuinely different and worth contrasting in a cross-carrier methodology footnote.

**CC4 (low). Eligibility row-order discipline.** DHL Paket H1 (re-sort by shipment_id at `_attach_de_rate`) vs DHL Express `_select_service` (join-back on shipment_id) — both engines rely on shipment_id uniqueness but neither enforces it via assert. Cross-carrier hygiene: add a "shipment_id is unique" invariant at the entry point of both engines' `calculate()`.

**CC5 (low). Date-column convention for time-windowed surcharges.** DHL Paket uses `shop_order_created_date` for Peak/Peak-in-Peak (with `2026-01-01` default). DHL Express has no time-windowed surcharge today (Peak is suspended, placeholder). When Demand Surcharge reactivates (DHL Express open-q C3), the date-column convention should be made symmetric across engines, and pinned in ASSUMPTIONS or cross-carrier.

**CC6 (low). UK-zone collapse on DHL Express vs full UK on DHL Paket.** DHL Express's ASSUMPTIONS notes "UK collapsed to *1 (Rest) zone in tdi_zones / ddi_zones" because GB is out of project scope. DHL Paket has GB in its PREMIUM_NAMED list; same out-of-scope. **No bug today** (population excludes GB), but **inconsistent treatment** in two engines that both serve a country flagged out of scope. If GB re-enters scope, DHL Express needs the GB *2 city list parsing, DHL Paket needs nothing new. Worth a cross-carrier "if GB re-enters scope" item.

---

## Notes

- The two `open_questions/dhl_paket.md` and `dhl_express.md` files are unusually comprehensive (5+11+1+9 / 7+7+1+8 items respectively). The bulk of the substantive risk to the cost number is captured there, including the SANITY_CHECK 2026-05-13 §B.2 Kleinpaket implementation (closed by `dhl_paket-1.1.0`), the DHL Express service-selection bug (fixed by `dhl_express-1.1.0`), and the fuel snapshot work that drove the 4-carrier mandatory headline from EUR 230k → EUR 18k.
- This audit's net-new findings are calc-discipline items (H1/H2/H3 on DHL Paket, E1/E2/E3/E4 on DHL Express, CC1-CC6 cross-cutting), not new structural gaps. The structural gaps are already in the open-question files.
- The SANITY_CHECK 2026-05-13 noted DHL Paket engine over-prices reality by ~17% on the winning slice. Post-§B.2 Kleinpaket that's now ~8% per `bias_table.md`. The B1 Bulky envelope question (EUR 2.31M Q1 if permissive reading wins) is the single largest remaining lever on the DHL Paket bias.
- No findings on rate-table extraction integrity — `extract_rates.py` for DHL Paket and `build_rate_tables.py` for DHL Express are clean reads of the offer Excel.
- File paths cited as absolute Windows paths since the engine lives outside the brain repo: `C:/Users/niklavs.felsbergs/Documents/GitHub/bi-analytics-main/NFE/projects/2_EU_tender_2026/`.

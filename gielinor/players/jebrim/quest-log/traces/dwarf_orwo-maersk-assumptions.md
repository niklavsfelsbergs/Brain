# Maersk carrier-engine — modeling assumptions (logistics-manager review)

Dwarf extraction for Jebrim, ORWO Tender 2026. READ-ONLY.
Source: `NFE/projects/7_ORWO_tender_2026/repricing_base/carrier_engines/maersk/`
Card: `offers/Maersk/offer/20260507_Picanova_ORWO_Sendmoments_Rate Card_Maersk_incl.ROW.xlsx`, sheet 'ORWO Sendmoments'.
Engine version `orwo-maersk-1.0.0` (constants.py:20). Live run 2026-06-19, 606,217 parcels, 99.6% Maersk-servable.

**Frame:** Maersk is a CARRIER-SWITCH model, not a re-rate of an own book. ORWO has NO Maersk
invoice book. The Maersk broker card is applied to the existing UPS + DHL parcels to ask "would
moving to Maersk beat what we pay now?". This is the single biggest confidence caveat — see A1.

---

## A1. No invoiced Maersk baseline to gate against  [LOAD-BEARING — biggest caveat]
- **What:** There is no own-Maersk cost history; the whole result is the card priced onto incumbent parcels.
- **Value/treatment:** Compared modeled Maersk door-freight vs current INVOICED freight per parcel. No trust-gate / accuracy ratio possible (unlike UPS 0.971, DHL 0.9992 which ARE gated).
- **Why:** "no own Maersk invoice book, so the card is applied to the existing UPS + DHL parcels" — constants.py:3-5; switch_compare.py:2-4; README.md:3-4, 48-49.
- **Confidence:** flagged-assumption. Card parse "verified against the sheet (spot-checks)" (README.md:49) but no actuals reconciliation.
- **Needs confirmation:** YES — externally validated only against the card spreadsheet, never against real Maersk billing. Every headline number inherits this.

## A2. Compare on Home Delivery method only (vs PUDO / Letterbox)  [LOAD-BEARING]
- **What:** Of the up-to-three methods per country, only "Home Delivery" rows are kept.
- **Value:** `METHOD = "Home Delivery"` — constants.py:22; filtered build_rate_tables.py:55; calculate.py:3.
- **Why:** "like-for-like with current door parcels" — the current UPS/DHL parcels are door delivery; PUDO/Letterbox are cheaper but a different delivery model, "noted as upside, not the headline" (constants.py:11-13; README.md:6-7, 54-55).
- **Confidence:** firm (a deliberate like-for-like choice, not a guess).
- **Needs confirmation:** Internally validated as the right comparison basis. PUDO/Letterbox upside is unmodeled — a logistics-manager call on whether ORWO would actually use them.

## A3. Cheapest local carrier per (country, band)  [LOAD-BEARING]
- **What:** Maersk is a broker routing each country to a local carrier (DHL DE, Evri, Colis Privé, GLS, La Poste, Yodel…). For each (country, band) the model takes the CHEAPEST Home-Delivery rate across whatever local carriers Maersk offers.
- **Value:** `pl.col("rate_eur").min()` per country/band — build_rate_tables.py:66-69. A `0` cell = method/band not offered → ignored (build_rate_tables.py:42, README.md:18).
- **Why:** rationale not documented beyond "cheapest local-carrier option per country/band" (README.md:7). Implicitly assumes Maersk would always route to the cheapest available local option.
- **Confidence:** firm in code; the **assumption that ORWO actually GETS the cheapest local carrier on every lane** is flagged.
- **Needs confirmation:** YES (Maersk) — confirm Maersk commits to the cheapest local carrier per lane vs choosing the carrier themselves.

## A4. DE domestic routes via DHL DE — Maersk LOSES domestic  [LOAD-BEARING]
- **What:** DE is included in the matrix; Maersk routes DE to DHL DE.
- **Value:** Maersk DE door @1kg €3.45 (build_rate_tables.py:73 expect 3.45). Above ORWO's own DHL Kleinpaket €2.79 / Paket-bis-5 €3.35.
- **Why:** "Maersk routes DE to DHL DE" (calculate.py:3). DE-domestic bulk (548,018 parcels) dominates → non-GB total +€176k H1 / +€353k/yr (+8.6%), driven by DHL DE +€206k (+11.4%) — README.md:29-34; COMPARISON.md:33,50-51.
- **Confidence:** firm (the number falls straight out of the card vs own DHL rates).
- **Needs confirmation:** Internally validated against ORWO's own DHL rates. This is WHY all-Maersk loses overall — load-bearing for the "not a whole-book win" verdict.

## A5. GB + cross-border EU is where Maersk WINS  [LOAD-BEARING]
- **What:** GB door rate (Evri/Yodel ~€3.45) far below UPS DDP (~€8) and DHL Intl Premium (€21.63). Cross-border lanes mostly win: AT −22%, FR −25%, ES −27%, IT −28%, IE −67%. Some lose (UPS FR +6%, NL +26%, BE/LU).
- **Value:** GB/EFTA −€96k H1 / −€192k/yr — README.md:33-38; COMPARISON.md:34,48-51.
- **Why:** card door rates vs incumbent international freight (README.md:35-37).
- **Confidence:** firm on the arithmetic; the **GB number carries the customs-clearance caveat** (A6).
- **Needs confirmation:** see A6.

## A6. GB/EFTA-UK customs clearance treatment unresolved  [LOAD-BEARING for GB]
- **What:** Whether Maersk's DDP door rate folds in customs clearance or bills it separately is unknown.
- **Value/treatment:** GB/XI/CH/NO/LI reported SEPARATELY as a lever, not folded into the headline — `EFTA_UK_COUNTRIES = {"GB","XI","CH","NO","LI"}` constants.py:52; split at switch_compare.py:62,83-90.
- **Why:** "Maersk as a DDP broker may fold clearance into the door rate; reported as scenarios" (constants.py:50-51); "confirm whether DDP customs clearance is folded into the door rate or billed separately" (README.md:37-38; switch_compare.py:89-90 — parallel to GLS IC18).
- **Confidence:** flagged-assumption (explicitly an open scenario).
- **Needs confirmation:** YES (Maersk) — swing factor on the GB saving.

## A7. US + ROW destinations not modeled
- **What:** US and other non-listed destinations (ROW zone sheet) excluded; stay on incumbent.
- **Value:** US ≈ €20k / 1,855–1,900 parcels. Reject reason `country_not_served` — calculate.py:50; constants.py:15-16; README.md:26-27,54.
- **Why:** "ROW zone sheet (not modeled in this first pass)… a refinement" (constants.py:16; README.md:54).
- **Confidence:** firm exclusion (deliberately out of scope for this pass).
- **Needs confirmation:** Internal scoping decision; refine later off the ROW sheet.

## A8. >30 kg not modeled
- **What:** Parcels above 30 kg rejected, stay on incumbent.
- **Value:** `MAX_WEIGHT_KG = 30.0` (constants.py:23); reject `over_max_weight` (calculate.py:51). ~744 trucks (README.md:27).
- **Why:** "top listed band on the Sendmoments sheet" — the card simply has no band above 30 kg (constants.py:23; bands cap at Z=30.0 constants.py:32).
- **Confidence:** firm (a hard card limit, not a choice).
- **Needs confirmation:** Internally validated against the card. Heavy tail would need a separate quote from Maersk.

## A9. Gross/billable weight, NO dimensional uplift on EU
- **What:** Pricing uses `billable_weight_kg` straight from the incumbent parcels; no volumetric/dim re-weight applied for the Maersk card.
- **Value:** band join on `billable_weight_kg` only (calculate.py:7,44,51; switch_compare.py:36,42). No dim-factor constant anywhere in the engine.
- **Why:** rationale not documented (no comment). Implicitly the incumbent billable weight is taken as the chargeable weight on the Maersk card too.
- **Confidence:** flagged-assumption (silent — no dim handling either way).
- **Needs confirmation:** YES — confirm Maersk/local carriers don't apply their own volumetric uplift that would raise the modeled rate.

## A10. Forward as-of band join — "fraction over rounds up"
- **What:** A parcel's weight maps to the smallest listed band >= its weight.
- **Value:** `strategy="forward"` join_asof on weight bands (calculate.py:27; build_rate_tables.py:9). Bands 0.25…30 kg, 20 columns G..Z (constants.py:29-33).
- **Why:** "any fraction over rounds up to the next listed weight" (build_rate_tables.py:9; calculate.py:4).
- **Confidence:** firm (standard parcel-tariff rounding; matches card structure).
- **Needs confirmation:** Internally validated (assumed to match the card's banding convention; worth a one-line Maersk confirm that rounding is up-to-band).

## A11. N. Ireland (XI) ships on the GB footing
- **What:** XI aliased to GB for rate lookup (no separate XI row on card).
- **Value:** `ISO_ALIAS = {"XI": "GB"}` (constants.py:48; applied calculate.py:38-47). Original kept for reporting.
- **Why:** "no separate XI row on the card" (constants.py:47).
- **Confidence:** firm.
- **Needs confirmation:** Internally validated against the card's country list.

## A12. Freight-vs-freight only — surcharges NOT modeled
- **What:** Comparison is invoiced FREIGHT vs Maersk door FREIGHT. Maersk's Surcharges sheet (198 rows) and the DHL surcharge layer (€143k) are both excluded.
- **Value:** `current_freight` = `invoiced_freight` (switch_compare.py:38,43); `maersk_base_eur` = card door rate only.
- **Why:** "freight-vs-freight is the clean like-for-like" (README.md:51-53). NB the model flags that Maersk Home-Delivery DDP rates "may already bundle more than DHL freight, which would narrow the DE-domestic gap on a full-cost basis" (README.md:52-53).
- **Confidence:** flagged-assumption — deliberate scoping, but the bundling caveat could move A4.
- **Needs confirmation:** YES (Maersk) — what the door rate includes; surcharge sheet unparsed.

## A13. H1 × 2 annualization
- **What:** Annual figures = H1 freight × 2.
- **Value:** `ANNUALIZE = 2.0` (switch_compare.py:30, applied :68,88).
- **Why:** "H1 × 2 annualization is rough" — no seasonal ratio (README.md:56; COMPARISON.md:6 "rough — refine with seasonal ratios").
- **Confidence:** flagged-assumption (explicitly rough).
- **Needs confirmation:** Internal — refine with seasonal ratios; not a Maersk question.

## A14. Current basis = invoiced freight on UPS + DHL eligible parcels only
- **What:** The book being repriced is UPS + DHL parcels flagged `eligible` in their own reprice outputs.
- **Value:** `.filter(pl.col("eligible"))` on both UPS reprice_own.parquet and DHL reprice_dhl_own.parquet (switch_compare.py:34,39). Maersk-servable = 99.6%.
- **Why:** rationale not documented in-engine (inherits the upstream UPS/DHL eligibility gates).
- **Confidence:** firm (mechanical), but inherits whatever those upstream gates assume.
- **Needs confirmation:** Internal — depends on UPS/DHL engine eligibility definitions.

---

## NOT FOUND in the Maersk engine (brief items that don't apply here)
The brief asked to capture a girth/oversize reject ceiling (175/200cm, 300cm girth) and a
euro toll/surcharge treatment. **Neither exists in the Maersk engine.** Searched all five
files + rate_tables: no `175`, `200`, `girth`, `300`, `oversize`, or `toll` references
(grep clean). These belong to the GLS engine — COMPARISON.md:63 attributes "toll €0.38" to
GLS, not Maersk. Maersk's only exclusions are: country_not_served (US/ROW), over_max_weight
(>30kg), no_rate_found (calculate.py:50-52). There is NO dimension/girth reject in Maersk; the
oversize/girth ceiling and euro-toll line are GLS assumptions, not Maersk ones. Flag for the
principal: if the manager review expects these on Maersk, they were modeled only on GLS.

## Load-bearing-for-the-headline ranking
1. **A1** (no invoiced baseline) — the meta-caveat over everything.
2. **A4** (DE→DHL DE loses) — why all-Maersk is +€80k/yr worse, NOT a whole-book win.
3. **A5 + A6** (GB/cross-border win, clearance unresolved) — the −€192k/yr GB lever, ITS biggest swing being A6.
4. **A2, A3** (Home-Delivery-only, cheapest-local-carrier) — define what "Maersk price" even means.
5. **A12** (freight-only) — could narrow A4 on a full-cost basis.

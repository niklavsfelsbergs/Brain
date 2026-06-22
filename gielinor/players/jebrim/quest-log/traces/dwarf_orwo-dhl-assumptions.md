# DHL (dhl_paket) calculator — modeling assumptions for logistics-manager review

Dwarf trace, Jebrim, ORWO Tender 2026. Read-only extraction 2026-06-22.
Source: `NFE/projects/7_ORWO_tender_2026/repricing_base/carrier_engines/dhl_paket/`.

One block per assumption: What / Value / Why / Confidence / Needs-confirmation.
Load-bearing-for-headline flagged inline. **LB** = moves the headline saving number.

---

## A. Cost-basis / scope assumptions

### A1. Cost basis = silver net `charge_amount`, ex-VAT, VAT = ×1.19
- **What:** the modeled cost is the silver invoice net charge_amount; total = net × 1.19 (German VAT); on non-freight lines net is derived as `total − vat`.
- **Value:** ×1.19 flat; freight lines use charge_amount directly, surcharge/sperrgut lines use `total − vat`.
- **Why:** German domestic VAT is 19%; charge_amount on weight lines is already net. (README.md:13-14; constants.py:8; run_gate.py:7, SQL lines 62/68 use `total - vat`.)
- **Confidence:** firm (VAT rate is statutory).
- **Needs-confirmation:** no — internally validated.

### A2. One freight line per tracking; freight = the decoded freight prod with wgt>0
- **What:** each tracking's forward-freight cost is the single freight-prod line carrying weight; surcharge and sperrgut are separate summed layers joined on identcode.
- **Value:** SQL groups by identcode, `MAX(prod)`, `MAX(wgt)`, `SUM(charge_amount)` over `prod IN (FREIGHT_PRODS) AND wgt>0`.
- **Why:** prod is per-line; the freight line is the weight-bearing one. Profiling (profile_dhl_silver2.py PRODS_PER_TRK / CHARGE_SEM) established prod-per-line and wgt-line-vs-fee-line split.
- **Confidence:** firm (validated by profiling + the 0.9992 gate).
- **Needs-confirmation:** no.

### A3. Returns excluded from the forward-freight base
- **What:** RETOURE / Rücksende prods are a separate stream, not in the forward base.
- **Value:** `RETURN_PRODS = {101510315, 185110316, 232000001}` excluded.
- **Why:** returns are a distinct cost direction, not forward freight. (constants.py:24-25; README.md:32.)
- **Confidence:** firm (decision).
- **Needs-confirmation:** no — but note coverage gap: returns are *un-repriced*; the offer adds a RETOURE column (€3.35/€3.91) not yet modeled (offer_summary.md:30; flagged as TODO line 77).

---

## B. Sperrgut / bulky — the UNPREDICTED residual  **(LB — affects what the headline excludes)**

### B1. Sperrgut/bulky €307k treated as UNPREDICTED, excluded from the modeled base
- **What:** bulky-goods prods are excluded entirely from the modeled forward base and surcharge layer; they sit in the residual, not in cost_total.
- **Value:** `SPERRGUT_PRODS = {1610, 1144, 1045, 1163, 1179, 904600011, 920600001}`; €307k net; the €20 domestic Sperrgut surcharge (+€21 intl per contracts dhl.md:229-230).
- **Why:** "unexpected by nature" — bulky incidence is not predictable per-parcel without dims; parallel to UPS's unmodeled `surcharge_other`. Explicit decision (Niklavs 2026-06-19). (constants.py:38-41; README.md:76-77; run_gate.py:8-10.)
- **Confidence:** flagged-assumption (a deliberate exclusion, not a measurement).
- **Needs-confirmation:** **YES — logistics manager.** Whether €307k bulky should stay out of the comparison base, or be modeled (it's dims-dependent — 77% dims NULL, dhl.md:204-214 / 307). If a competitor handles bulky differently this is a real lever currently invisible. Load-bearing because it sets the denominator the saving is quoted against.

---

## C. Domestic weight-break card (the €1.9M spine)  **(LB — the spine the headline rests on)**

### C1. PAKET domestic weight-break bands
- **What:** domestic PAKET priced by weight band, "any fraction over takes the next band," ceiling 31.5 kg.
- **Value:** (≤5 kg → €3.35), (≤10 kg → €4.95), (≤31.5 kg → €10.55). `PAKET_DOM_BANDS` (constants.py:45-49); band logic in calculate.py:27-34.
- **Why:** the contractual card; the silver prod code encodes the band so net charge_amount reproduces the card "to the cent by construction." (README.md:6-9, 23-25.)
- **Confidence:** firm — gated 1.0000 / 1.0000 on the two big bands, 0.9965 on bis-31.5 (README.md:50-56).
- **Needs-confirmation:** no — internally validated to the cent. (Matches contract dhl.md:93-96.)

### C2. Kleinpaket flat rate
- **What:** Kleinpaket priced flat regardless of weight up to 1 kg.
- **Value:** €2.79, max 1.0 kg (`KLEINPAKET_RATE`, `KLEINPAKET_MAX_KG`; constants.py:50-51; calculate.py:63-64).
- **Why:** single lump-sum card up to 1 kg. (README.md:26; contract dhl.md:104.)
- **Confidence:** firm — gated 0.9999 (README.md:53).
- **Needs-confirmation:** no.

### C3. Packstation discount NOT modeled
- **What:** the contract carries a Packstation discount (−€0.20 PAKET, −€0.10 Kleinpaket, from 2026-01-01) that is not applied in the engine.
- **Value:** discount = 0 in the model (no code reference; absent from constants.py).
- **Why:** rationale not documented. The gate reproduces invoiced net to the cent without it, so for the *window* invoiced the discount was apparently not yet active or not material (contract effective 2026-01-01; dhl.md:97/106).
- **Confidence:** placeholder / silent omission.
- **Needs-confirmation:** **YES — logistics manager.** If Packstation volume is non-trivial going forward, the go-forward cost is ~€0.10–0.20/parcel lower than modeled. Not in the headline today but a real go-forward delta.

### C4. Over-31.5 kg → ineligible (reject, not repriced)
- **What:** PAKET parcels over the ceiling are rejected, not priced.
- **Value:** `reject = "over_31.5kg"` / `_paket_dom_rate` returns None over 31.5 (calculate.py:34, 57-58).
- **Why:** DHL Paket ceiling is 31.5 kg; over-ceiling goes to a different product. (constants.py:53.)
- **Confidence:** firm.
- **Needs-confirmation:** no — but eligible-fraction should be checked (rejects printed at run_gate.py:136-139).

---

## D. International Premium — invoice-DERIVED, not card  **(LB for the intl/GB lever)**

### D1. Intl Premium country base = median invoiced net, NOT the published zone card
- **What:** PAKET International Premium (prod 112000001) is priced off a country-keyed rate derived from the *invoiced* net charge_amount (median per country), not the contractual zone card.
- **Value:** `MEDIAN(charge_amount)` per dest_country, HAVING COUNT ≥ 20 (build_rate_tables.py:41-52); written as `intl_base_eur`.
- **Why:** the published zone card is NOT what ORWO pays — "AT invoiced €5.31 vs published €13 base" (build_rate_tables.py:4-7; README.md:58-61). Deeply negotiated, so invoice is ground truth.
- **Confidence:** flagged invoice-derived — "the intl stream is descriptive, the DOMESTIC card is the gate." Gate 0.9857 portfolio (≈1.4% miss = median-vs-mean on an 8k-trk stream; README.md:55, 58-59).
- **Needs-confirmation:** **YES — DHL / logistics manager** to confirm the negotiated Premium country rates if the intl stream is to be a firm headline component. Currently *descriptive only*.

### D2. Intl per-kg slope = 0 (flat country base)
- **What:** no per-kg weight slope on intl Premium; the country median net is used as a flat base.
- **Value:** `intl_per_kg_eur = 0.0` (build_rate_tables.py:37-40, 66-68).
- **Why:** documented simplification — the intl stream is sub-1kg (avg <1 kg), per-kg slope estimated from quartiles is "noisy at this volume," weight variance small. (build_rate_tables.py:37-40.)
- **Confidence:** flagged-assumption (explicitly "documented simplification").
- **Needs-confirmation:** internally reasoned; confirm only if heavier intl parcels enter the book.

### D3. Intl countries below 20 trackings dropped
- **What:** countries with <20 trackings get no derived rate → parcels there reject as `no_intl_country_rate`.
- **Value:** `HAVING COUNT(*) >= 20` (build_rate_tables.py:51); reject in calculate.py:66-68.
- **Why:** rationale not documented (implied: too few obs for a stable median).
- **Confidence:** flagged-assumption.
- **Needs-confirmation:** no — but check the rejected-tail volume; long-tail intl countries are silently excluded.

### D4. GB Non-EU Premium = the one fat lever (€50.6k/yr, 59% of intl)  **(LB)**
- **What:** GB sub-1kg parcels pay €21.63 each on post-Brexit Non-EU Premium zone pricing — the real optimization headroom, untouched by the DHL offer.
- **Value:** GB €50.6k/yr, 2,339 parcels, avg 0.76 kg, €21.63/parcel; base €20.9 + €0.90/kg (offer_summary.md:62-65).
- **Why:** Brexit moved GB to zone "1 Non-EU." Flagged as the carry-into-competitor-reprice target.
- **Confidence:** firm observation (descriptive).
- **Needs-confirmation:** no for the observation; **YES** for whether a competitor (GLS/Maersk/consolidator/Warenpost) can undercut — that's the open lever.

---

## E. Companion surcharge layer (€143k) — calibrated per-parcel

### E1. Surcharge modeled as a fixed per-parcel expectation, split (ongoing, seasonal)
- **What:** Maut/CO2 + Energy + Peak surcharges modeled as one fixed €/parcel value per freight product, split into an ongoing component and a seasonal (peak) component.
- **Value:** `SURCHARGE_EXP` (constants.py:65-71): PAKET bis5 (0.2079, 0.0838); bis10 (0.2242, 0.1007); bis31.5 (0.2896, 0.0967); Kleinpaket (0.0319, 0.1412); Intl (0, 0). Applied as `sur_ong + sur_sea` (calculate.py:72-75).
- **Why:** calibrated as `surcharge_net_sum / freight_trks` per product against invoiced (2026-06-19). Ongoing = Maut/CO2 (€0.19, ~64% incidence) + Energy (€0.03–0.04), year-round; seasonal = Peak (€0.19) + Peak-in-Peak (€0.50), Nov–Dec only, valued at expected-over-window incidence. (constants.py:55-64; README.md:67-74.)
- **Confidence:** flagged-assumption — empirically calibrated, gated 0.9995 (README.md:67).
- **Needs-confirmation:** partial. The *seasonal* value is an "expected-over-the-window incidence" — a full-year basis recurs each peak (constants.py:60-62). **Logistics-manager check:** whether the silver window's peak share annualizes correctly (see G1 annualization). Energy surcharge is variable/not contract-fixed (dhl.md:227, 234) — calibrated off invoice, so it floats with whatever rate was invoiced.

### E2. Maut/CO2 does not apply to Kleinpaket
- **What:** Kleinpaket gets energy-only ongoing surcharge, no Maut/CO2.
- **Value:** Kleinpaket ongoing 0.0319 (energy only) vs PAKET ~0.20+ (constants.py:64, 69).
- **Why:** observed — Kleinpaket carries no 2509 Maut/CO2 code. (constants.py:64; README.md:70.)
- **Confidence:** firm (data-observed).
- **Needs-confirmation:** no.

### E3. Intl Premium carries none of the domestic surcharge codes
- **What:** intl Premium surcharge = (0, 0); it has its own surcharge structure.
- **Value:** (0.0000, 0.0000) (constants.py:70).
- **Why:** intl Premium doesn't carry the domestic 2509/2680/2675 codes — own surcharge structure. (constants.py:62-63, 70.)
- **Confidence:** flagged-assumption — intl surcharge is simply *not modeled*, treated as zero.
- **Needs-confirmation:** **YES if intl becomes headline** — intl Premium surcharges (transport-cost surcharge, customs post-processing, dhl.md:234-235) are excluded; a true intl cost_total is understated.

---

## F. The trust gate

### F1. Gate tolerance / portfolio ratio 0.9992, and what it covers
- **What:** the modeled forward freight (and freight+surcharge cost_total) is accepted because it reproduces invoiced net at portfolio ratio ~0.9992.
- **Value:** freight 0.9992; cost_total (freight+surcharge) 0.9992; surcharge layer 0.9995; over 547,486 eligible freight trackings. (README.md:46-48, 65-75; run_gate.py computes ratios at lines 149-151.)
- **Why:** sanity that the card+surcharge model = the bill. There is **no hard pass/fail threshold constant in code** — the ratio is printed, judged by eye; 0.9992 is the *observed result*, not an enforced gate. (run_gate.py prints; no assert.)
- **Confidence:** firm (live result).
- **Needs-confirmation:** no — but note the gate **excludes** by construction: Sperrgut, returns, ineligible (over-31.5kg / no-country-rate / no-band) parcels, and any tracking without a wgt>0 freight line. The 0.9992 speaks only to the eligible freight book.

### F2. Eligibility = has a routable freight prod with a resolvable rate
- **What:** only parcels that route to a card and resolve a base rate are "eligible" and counted in the gate / headline.
- **Value:** `eligible = base is not None`; rejects: over_31.5kg, no_band, no_intl_country_rate, unrouted_product (calculate.py:69-85).
- **Why:** can't reprice what doesn't route. Reject reasons tallied (run_gate.py:136).
- **Confidence:** firm.
- **Needs-confirmation:** no — but the rejected fraction is a coverage caveat to state.

---

## G. The DHL offer reprice — why it's FLAT  **(LB — this IS the headline for DHL)**

### G1. The DHL 2026 offer is flat across the entire book; value = GRI avoided
- **What:** repricing all 547,486 freight parcels on the 2026 offer card vs invoiced yields essentially zero delta — the offer reproduces current rates to the cent. Headline DHL value is framed as "GRI avoided," not a rate cut.
- **Value:** total freight delta −€317 (−0.02%) over €1,908,887; domestic bands identical (3.35/4.95/10.55, Kleinpaket 2.79), intl within €1–3/destination. GRI-avoided framed at ~5%/yr (2025 ~4.9%) on €2.05M cost_total ≈ **€100k/yr**. (offer_summary.md:37-58; build_offer_tables.py:99-112 confirms domestic flat.)
- **Why:** the offer card the engine parsed equals the current contract card — "the current ORWO contract IS essentially this 2026 card." GRI-avoided logic mirrors the UPS flat-lanes (AT/FR/NL) and the [[S280_e5be6eb5_orwo-tender-reprice-engine|S280]] go-forward basis. (offer_summary.md:33-35, 51, 53-58.)
- **Confidence:** the flat reprice is **firm** (modeled to the cent). The **€100k/yr GRI-avoided number is a placeholder/parametric** — explicitly "confirm ORWO's actual DHL GRI clause/% to firm the number; deferred input." (offer_summary.md:58, 76.)
- **Needs-confirmation:** **YES — logistics manager / DHL.** The entire DHL go-forward value rests on the GRI %; ORWO's actual GRI clause is unconfirmed. This is THE load-bearing confirmation for the DHL headline. Without it the headline saving is €0 (flat).

### G2. Offer intl Premium = zone card with per-country overrides + EU/Non-EU fallback
- **What:** offer intl repriced on the published Premium zone card (per-country override columns where listed, else zone-generic split by EU/Non-EU), billing weight rounded up to 100 g.
- **Value:** override countries BE/FR/LU/NL/AT/PL/CZ/IT/SE/ES/HU/CA; `ZONE_GENERIC_COL` map; XI (N.Ireland) → GB Non-EU footing; total = unit + per_kg × ceil-to-100g weight. (build_offer_tables.py:31-95; compare_offer.py:52-59.)
- **Why:** the offer's actual Premium card structure. Note this is the *published* card — under the offer it lands within €1–3 of invoiced, so for these countries the published ≈ negotiated (unlike the baseline D1 where published ≠ invoiced for the current book). No-card-row destinations fall back to keeping invoiced freight (compare_offer.py:57).
- **Confidence:** firm for the listed countries; flagged for fallback destinations (keep-invoiced = no change assumed).
- **Needs-confirmation:** confirm the override-country list is complete; tail destinations silently held at invoiced.

### G3. Annualization ×2 (silver window ≈ H1)
- **What:** the H1 saving is doubled to annualize.
- **Value:** `ANNUALIZE = 2.0`; window ≈ Sep 2025–Jun 2026 (compare_offer.py:37-38, 90-91).
- **Why:** silver window is ~half a year. Labeled "rough."
- **Confidence:** placeholder ("rough" annualization).
- **Needs-confirmation:** **YES — partial.** ×2 ignores seasonal peak (Nov–Dec is in-window, so doubling a peak-inclusive H1 may double-count peak). For DHL the saving is ~0 so it barely matters here, but the same ×2 propagates to competitor reprices where it WILL matter. Flag for the logistics manager when sizing competitor savings.

---

## H. Streams NOT modeled (coverage caveats, not engine assumptions)

- **POST / Warenpost stream:** invoiced by Deutsche Post AG (66xx), ~€82k/mo, 99% estimated in the mart, **not in the DHL freight engine at all** — separate pull, TODO (offer_summary.md:13, 77; dhl.md §6/§7). Reprice needs weight (77% NULL); eligibility needs dims (77% NULL). Rationale: separate scope; a hard gap.
- **Sendmoments entity:** ships under the same ORWO account 5311934365; offer cards parked as "separate scope" (offer_summary.md:15). **Open scoping question** — is the modeled book ORWO-only or account-wide (incl. sendmoments)? (dhl.md §8, Q3.) Affects what volume the saving is quoted on.
- **DHL Express, DHL Freight DE:** out of scope (admin/no volume in scope; dhl.md §2e/§2f).
- **Returns:** excluded (A3) — offer adds a RETOURE column not yet modeled.
- **Routing-code penalty +€0.49/parcel:** in contract/offer (dhl.md:228; offer_summary.md:30), not modeled.

---

## Load-bearing summary for the DHL headline

1. **G1 — GRI % is the whole DHL value.** Offer is flat to the cent; the only saving is "GRI avoided," and that number is an unconfirmed parametric (~5% → ~€100k/yr). Confirm ORWO's DHL GRI clause. **This is the single most load-bearing confirmation.**
2. **B1 — €307k Sperrgut excluded as UNPREDICTED.** Sets the denominator; a deliberate exclusion needing logistics-manager sign-off.
3. **D1/D4 — intl Premium is invoice-derived (descriptive), and GB Non-EU (€50.6k, 59% of intl) is the real lever** untouched by the DHL offer — confirm whether a competitor undercuts.
4. **G3 — ×2 annualization** is rough and peak-inclusive; near-zero impact for flat DHL but propagates to competitor savings.

Internally validated (no external confirmation needed): A1, A2, C1, C2, C4, E2, F1, F2 — all anchored by the 0.9992 to-the-cent gate.

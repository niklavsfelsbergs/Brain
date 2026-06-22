# Dwarf trace — ORWO Maersk: dims / volumetric / oversize logic + rates

Read-only recon (2026-06-22). Repo: `bi-analytics-main`. No engine code modified.
Purpose: source the volumetric-weight reprice of ORWO's bulky/oversize parcel tail at Maersk.

---

## TASK A — EU-tender Maersk engine weight-calc logic

Engine: `NFE/projects/2_EU_tender_2026/2_analysis/carrier_engines/maersk/` (version `maersk-3.2.0`).
Shared dim helpers: `.../carrier_engines/_base/supplement.py`.

### A1. Sorted-dims primitives (`_base/supplement.py:23-54`, `add_sorted_dims`)
Raw L/W/H are NOT ordered (~6% of rows have W>L) — all checks use sorted dims, rounded 1dp:
- `d_max` = longest side, `d_min` = shortest, `d_mid` = middle
- `lwh_sum` = L+W+H
- `lwh_product` = L*W*H (rounded 0dp)
- **`length_plus_girth_cm` = d_max + 2*(d_mid + d_min)** — i.e. **L + 2W + 2H** (girth = 2×(mid+min)). This is the carrier-wide "girth" definition the engine uses.

### A2. Dimensional / volumetric weight (`_base/supplement.py:57-92`)
- Formula: **dim_weight_kg = L*W*H / divisor**.
- **Maersk EU branch: NO dim weight — chargeable = GROSS weight** (`add_chargeable_weight(mode="gross")`, `calculate.py:94`). Docstring line 67: "Maersk EU = no dim weight (use gross)."
- **Maersk ROW branch (FedEx Economy): divisor = 5000**, chargeable = **max(gross, dim)** (`ROW_DIM_DIVISOR=5000.0`, constants.py:129; override at `calculate.py:128-134`).

So on the EU lane the engine as-built does NOT volumetric-uplift. Repricing the bulky tail at *volumetric* weight on EU is a **deliberate departure** from the EU-tender engine's EU behavior — the engine only does volumetric on ROW.

### A3. Girth ceiling / oversize trigger logic — THE KEY ITEM
Two distinct EU mechanisms:

**(a) Per-country oversize SURCHARGE trigger** (`surcharges/eu_oversize.py:27-47`). Fires if `service==eu_hd` AND a joined per-country `_oversize_eur` is non-null AND any of:
- `d_max > _max_l` (max length) | `d_mid > _max_w` | `d_min > _max_h`
- `lwh_sum > _max_lwh` (L+W+H cap)
- `length_plus_girth_cm > _max_l2w2h` (the L+2W+2H cap)
Cost = the joined per-country `_oversize_eur` amount. Thresholds + amounts come from `rate_tables/eu_oversize.parquet`, which is sourced from the ORWO card's Surcharges sheet (see B2 — same per-country table).

**(b) Absolute HANDLING/LOADING ceiling — the "Maersk girth ceiling" reject** (`constants.py:46-74`, `calculate.py:244-255`, eligibility `_decide_eligibility`). Independent of whether a surcharge exists — this REJECTS the parcel:
- `MAX_LONGEST_SIDE_CM = 175.0` (all EU dest except DE)
- `MAX_LONGEST_SIDE_DE_CM = 200.0` (DE relaxation)
- `MAX_GIRTH_CM = 300.0` (all EU dest) — **girth = L+2W+2H = `length_plus_girth_cm`** (CONFIRMED by Maersk 2026-06-10, constants.py:65-68; NOT pure 2×(W+H))
- Reject condition (`over_handling_ceiling`): `service==eu_hd AND ( d_max > longest_ceiling[175, or 200 if DE] OR length_plus_girth_cm > 300 )` → `reject_reason = "over_handling_ceiling"`, `eligible=False`, `cost_total_eur=null`.

Provenance quote (Stefan/Maersk, constants.py:56-63): "capped at 175cm OR girth 300cm, the largest will apply... Past this the parcel is beyond our handling & loading limit in our warehouse → reject EVEN where a surcharge exists." DE: "200cm in length BUT less than 300cm in girth."

**Consequence the engine itself flags (constants.py:69-71):** because the 300cm L+2W+2H ceiling binds everywhere, most per-country oversize surcharges become **unreachable** (any parcel over a country's standard l2w2h threshold is also over the 300 ceiling) → the Maersk EU oversize lane is "essentially standard-parcels-only." Reject-reason precedence (`calculate.py:270-277`): country_not_served → over_max_weight(>30kg) → **over_handling_ceiling** → oversize_no_surcharge → no_rate_found.

### A4. ROW (FedEx) oversize/overweight (constants.py:130-146, surcharges/row_oversize.py, row_overweight.py)
FedEx AHS triggers (cm): longest `d_max > 121`, second `d_mid > 76`, `length_plus_girth_cm > 266`, volume `lwh_product > 169901 cm³`. Charge: **1.27 €/kg of billable_weight, min 31.56 €**. AHS-Dimension (oversize) and AHS-Weight (overweight, >25kg) are mutually exclusive (`exclusivity_group="row_ahs"`, only highest applies). Hard reject still at >30kg billable.

---

## TASK B — ORWO Maersk rate card
File: `NFE/projects/7_ORWO_tender_2026/offers/Maersk/offer/20260507_Picanova_ORWO_Sendmoments_Rate Card_Maersk_incl.ROW.xlsx`.
(`repricing_base/rate_cards.md` + `findings.md` are UPS-only — NO Maersk content there. Gap noted.)

Sheets: Picanova, Picanova-ROW, ORWO Sendmoments, ORWO&Sendmoments-ROW, **Surcharges (198 rows)**, Colis Prive|Not Coverage, Remote Areas Surcharges, GLS Italy, Italy, UK, ROW Economy Zones, ROW Surcharges. Card is the **broker / Home-Delivery** model: cheapest local carrier per country.

### B1. Volumetric divisor in the card
- **EU lanes: GROSS weight, no divisor.** Footnote `ORWO Sendmoments r85`: "* Price is based on gross weight." (matches engine A2.)
- **ROW lane: `L*W*H / 5000`.** Sheet `ROW Surcharges` r6-7 ("Volumetric Factor", "L*W*H/5000"); `Picanova-ROW r47` / `ORWO&Sendmoments-ROW r47`: "Price is based on chargeable weight." (matches `ROW_DIM_DIVISOR=5000`.)

### B2. Per-country Oversize Surcharge table — sheet `Surcharges`, rows 45-76
Header (r47): `Destination Country | Carrier | Max Length [cm] | Max Width [cm] | Max Height [cm] | L+W+H [cm] | L+2W+2H | Oversize Surcharge [€]`.
This IS the source for engine `eu_oversize.parquet` (cols map: max_length→_max_l, max_width→_max_w, max_height→_max_h, max_lwh→_max_lwh, max_l2w2h→_max_l2w2h, oversize_surcharge→_oversize_eur).

| Country | Carrier | MaxL | MaxW | MaxH | L+W+H | L+2W+2H | Oversize € |
|---|---|---|---|---|---|---|---|
| Austria | DPD | 175 | - | - | 300 | - | 23.20 |
| Belgium | ColisPrive | 100 | - | - | - | 300 | 6.10 |
| Bulgaria | Speedy | 175 | - | - | - | 300 | 12.77 |
| Croatia | HrvatskaPosta | 60 | 60 | 60 | 180 | - | - (reject) |
| Cyprus | Taxydromiki | 120 | 80 | 100 | 300 | - | - (reject) |
| Czech Rep. | PPL | 120 | 60 | 60 | 240 | 360 | 15.15 |
| Denmark | GLS | 200 | - | - | - | 300 | 22.82 |
| Estonia | Venipak | - | - | - | 120 | - | - (reject) |
| Finland | Posti | 100 | 60 | 60 | - | 300 | 3.50 |
| France | ColisPrive | 100 | - | - | 150 | 300 | 6.10 |
| Germany | DHL | 120 | 60 | 60 | 240 | 360 | 21.00 |
| Greece | Taxydromiki | 120 | 80 | 100 | 300 | - | - (reject) |
| Hungary | ExpressOne | 155 | 55 | 55 | 265 | 300 | 4.70 |
| Ireland | ANPOST | 150 | - | - | - | 300 | >60L 0.90 / >120L 2.50 / >200L 20.00 (volume-tiered) |
| Italy | GLS | 120 | - | 170 | - | - | 2.00 (L 120-300 / H 170-240) |
| Latvia | Venipak | - | - | - | 120 | - | - (reject) |
| Lithuania | Venipak | - | - | - | 120 | - | - (reject) |
| Luxembourg | ColisPrive | 100 | - | - | 150 | 300 | 6.10 |
| Netherlands | DHL | 176 | 75 | 74 | 325 | - | 23.50 |
| Norway | Bring | 120 | 60 | - | - | 300 | 13.40 |
| Poland | Inpost | 120 | - | - | 220 | - | 24.00 |
| Portugal | CTT | 180 | - | - | 240 | - | 4.95 |
| Romania | FanCourier | 60 | 50 | 30 | 140 | 300 | 0.60 |
| Slovakia | SPS | 150 | 60 | 60 | 270 | 330 | 7.50 |
| Slovenia | DPD | - | - | - | 300 | - | 7.50 |
| Spain | PAACK | 150 | 150 | 150 | 200 | - | >80cm 1.00 / >120 1.20 / >150 2.50 / >200 15.00 (size-tiered) |
| Sweden | Bring | 120 | 60 | - | - | 300 | 13.40 |
| Sweden | EarlyBird | 60 | - | - | 90 | - | - (reject) |
| Switzerland | SwissPost | 100 | 60 | 60 | 220 | - | - (reject) |

"-" in a threshold col = no constraint on that axis. "-" in the € col = no surcharge published → over-spec parcel is REJECTED, not surcharged (`oversize_no_surcharge` in the engine; e.g. CH, HR, CY, GR, EE, LV, LT). IE & ES carry NON-scalar tiered rules (volume-litres / size-bands) the flat-column engine model does NOT fully capture — flag for the reprice.

### B3. Max-size / hard limits in card
- **Max weight 30 kg** (EU rate chart tops at 30; `MAX_WEIGHT_KG=30`). ROW: Home Delivery max 30 Kg.
- **ROW max dimensions** (`ROW Surcharges` r14): "L+2H+2W ≤ 266 cm, largest side ≤ 121 cm", min 15×10×1 cm.
- **ROW oversize surcharge** (r18-23): Oversized / Packaging / Overweight(>25Kg) each = **1.27 €/kg, min 31.56 €**. Triggers: longest >121, 2nd-longest >76, L+girth >266, volume `2xLxH < 169,901 CBM` (the engine reads this garbled wording as the FedEx AHS-Dimension volume cap L*W*H > 169,901 cm³).
- The **300cm L+2W+2H handling/girth ceiling** in the EU table is per-country (most are 300). It is NOT a single published number in the card; the engine's absolute 175/200-longest + 300-girth reject ceiling comes from a **separate Maersk email reply 2026-06-10** (constants.py:52-74), NOT from this xlsx. **Flag: the absolute reject ceiling is email-sourced, not card-sourced.**

---

## KEY QUESTION — can we compute an oversize surcharge for EVERY parcel from its dims?

**Partly. Two layers, and the answer differs by layer:**

1. **Yes — the dims primitives are universal.** Every parcel gets `d_max/d_mid/d_min`, `lwh_sum`, `lwh_product`, and `length_plus_girth_cm` (= L+2W+2H) from raw L/W/H (`add_sorted_dims`). No DHL-Sperrgut flag needed — this is pure geometry. So we CAN evaluate any parcel against any threshold, for every country.

2. **The TRIGGER is per-country, from the card's Oversize table (B2).** A parcel is "oversize" for its destination if any of {d_max>MaxL, d_mid>MaxW, d_min>MaxH, lwh_sum>L+W+H cap, length_plus_girth_cm>L+2W+2H cap} for that country's row. The surcharge amount is that country's € figure.

3. **REJECT (girth ceiling), not surcharge:** Parcels are rejected outright — `cost_total_eur=null`, never surcharged — when EITHER:
   - **over_handling_ceiling** (absolute, email-sourced): `d_max > 175` (DE: 200) **OR** `length_plus_girth_cm > 300`. This binds in EVERY country and takes precedence over the surcharge. Because of it, most per-country surcharges are unreachable — a parcel big enough to trip a country's oversize threshold is usually also >300 girth → rejected. The engine itself calls the EU oversize lane "essentially standard-parcels-only."
   - **oversize_no_surcharge**: country has a size cap but NO published surcharge (CH, HR, CY, GR, EE, LV, LT, etc.) → over-spec parcel rejected.

**Bottom line for the bulky-tail reprice:**
- A surcharge IS computable per-parcel from dims for the ~20 countries with a flat € figure — but only in the narrow window between the country's standard size cap and the 300cm girth ceiling. Above 300 girth (or 175/200 longest side), Maersk's modeled behavior is **reject, not surcharge**.
- This is NOT a DHL-Sperrgut-style "any bulky parcel gets a fee" model. Maersk's bulky tail is mostly a **rejection boundary**, with a thin surcharge band beneath it.
- The volumetric-weight reprice the principal is planning applies to the **ROW (FedEx) lane only** in the as-built engine (divisor 5000, max(gross,dim)); the **EU lane is gross-weight with no volumetric uplift** — so volumetric repricing of the EU bulky tail is a new modeling choice, not something the EU-tender engine or the ORWO card supports today.

---

## Gaps / flags
- `repricing_base/rate_cards.md` and `findings.md` contain **NO Maersk content** — both are UPS-only. The reprice base has no Maersk distillation yet.
- The absolute 175/200-longest + 300-girth **reject ceiling is sourced from a Maersk email (2026-06-10), not the xlsx card**. If repricing off the card alone, this ceiling is invisible — must be carried in from the EU-tender engine constants.
- **IE and ES** oversize rules are non-scalar (volume-litres tiers / size-band tiers) and are NOT captured by the engine's flat per-axis columns — handle specially if those lanes carry bulky volume.
- Italy rule is a compound length-AND-height band ("L 120-300 AND H 170-240 → 2€"), also not a clean single-threshold; verify the parquet encoding.
- All EU oversize figures read DIRECTLY from the xlsx Surcharges sheet rows 48-76. ROW figures read directly from ROW Surcharges sheet. No figure inferred. The one INTERPRETED item: ROW volume cap "2xLxH < 169,901 CBM" → engine reads as L*W*H > 169,901 cm³ (engine's documented interpretation, constants.py:141-146).

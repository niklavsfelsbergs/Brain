# Dwarf trace — ORWO GLS dims / oversize recon

Read-only recon. ORWO Tender 2026. Repricing the bulky/oversize parcel tail at volumetric weight for GLS.
Repo: `C:/Users/niklavs.felsbergs/Documents/GitHub/bi-analytics-main`

---

## TASK A — EU-tender GLS engine weight-calc logic (carrier-wide, deal-independent)

Source dir: `NFE/projects/2_EU_tender_2026/2_analysis/carrier_engines/gls/` + `_base/`

### Dimensional / volumetric weight formula
- **`dim_weight_kg = L*W*H (cm) / 6000`** — `EURO_DIM_DIVISOR = 6000.0` (`gls/constants.py:69`).
  `lwh_product` = L*W*H in cm³ (`_base/supplement.py:44`); `add_dim_weight` divides by the divisor (`_base/supplement.py:57-70`). `calculate.py:113` passes `divisor=EURO_DIM_DIVISOR`.
- Divisor 6000 is GLS-specific. (Engine's generic note: FedEx/DHL/UPS EU = 5000; GLS = 6000.) Direct read.
- Units: cm → kg. Direct read.

### Chargeable / billable weight
- Two services with DIFFERENT rules (`calculate.py:135-167`):
  - **BusinessParcel (DE domestic): GROSS weight only.** No dim weight applied. `billable = weight_kg`.
  - **EuroBusinessParcel (EU + adjacent): `max(gross, dim)`, but the DIM UPLIFT is capped at 30 kg.** `EURO_DIM_CAP_KG = 30.0` (`constants.py:70`). Encoding (`calculate.py:159-163`): if airfreight → uncapped `max(gross,dim)`; else if `dim > gross` → `min(dim, 30)`; else → `gross`. So dim only ever *raises* to a max of 30 kg; a parcel whose gross already exceeds 30 kg bills at gross, not the cap.
  - **8 airfreight countries — dim uncapped:** AL, BA, FO, IS, MK, MT, ME, TR (`EURO_AIRFREIGHT_COUNTRIES`, `constants.py:72-74`).
- No density-threshold mechanic in the engine — it's pure `max(actual, volumetric)`. Direct read.
- Hard weight limit both services: **40 kg** (`MAX_WEIGHT_KG`, `constants.py:46`); over → reject `over_max_weight`.

### Oversize / max-dimension / length-plus-girth triggers
Two distinct mechanisms in the engine — a REJECT gate and a priced SURCHARGE:

1. **Oversize REJECT (no surcharge, parcel excluded)** — `_decide_eligibility`, `calculate.py:271-279`. Fires `oversize_no_surcharge` if ANY of:
   - `d_max > 200 cm` (`GLS_MAX_LONGEST_CM`)
   - `d_mid > 80 cm` (`GLS_MAX_MID_CM`)
   - `d_min > 60 cm` (`GLS_MAX_SHORTEST_CM`)
   - `length_plus_girth_cm > 300 cm` (`GLS_MAX_L_PLUS_GIRTH_CM`)
   - girth def: `length_plus_girth_cm = d_max + 2*(d_mid + d_min)` (`_base/supplement.py:50`).
   - These are GTC §4.2 hard caps; the 300cm L+girth maps to the "Oversized Package / exclusion of carriage 30€" line (Q14 read: 30€ exclusion fires on girth > 300cm). `constants.py:49-56`.

2. **Overlength SURCHARGE (priced, kept in stream)** — `surcharges/overlength.py`. **1.60 €/parcel when `d_max > 120 cm`** (`OVERLENGTH_TRIGGER_CM = 120.0`, `OVERLENGTH_PER_PARCEL = 1.60`, `constants.py:59-60`). Fires in the 120–200 cm band only (above 200 cm rejected upstream). Mutually exclusive with Non-conveyable via `exclusivity_group="bulky"`, Overlength priority=1 wins.

3. **Big Parcel SURCHARGE** — `surcharges/big_parcel.py`. **0.80 €/parcel when volume > 150 litres**; `volume_litres = lwh_product/1000`, i.e. `L*W*H cm / 1000 > 150` (`BIG_PARCEL_VOLUME_LITRES = 150.0`, `constants.py:127-129`). Pure dim trigger — derivable from L/W/H alone.

4. **Non-conveyable** — `surcharges/non_conveyable.py`. 0.80 €, but **hard-coded OFF** (`pl.lit(False)`): triggers are packaging/shape (tyres, rolls, protruding parts) absent on `fact_shipments`. Its only dim trigger (length>1.20m) is already covered by Overlength.

**Engine threshold provenance:** the 120 cm / 150 L / 300 cm girth numbers were sourced from the **Picanova** GLS card + the GLS Round-1 Q-resolutions (Q12, Q14), NOT from the ORWO card. See "GAP" below.

---

## TASK B — ORWO GLS offer card (deal-specific)

Sources: `NFE/projects/7_ORWO_tender_2026/offers/GLS/offer/` — `ORWO offer.xlsx` (5 sheets) + `GLS Offer 276a45fU9o ID 1-17ULZBF_ORWO Net GmbH.pdf` (16 pp).
`repricing_base/rate_cards.md` = **UPS-only, no GLS content.** ORWO GLS CLAUDE.md marks the folder PARKED.

### Volumetric divisor — STATED, matches engine
- PDF p7 footnote: *"If a parcel's dimensional weight (LxWxH in cm/6,000) is higher than its real weight of ≤ 30 kg, billing is based on dimensional weight but limited to a maximum of 30 kg. In all other cases … real weight."* → **divisor 6000, dim-cap 30 kg** — identical to the engine. Direct read (`/tmp/gls_p9.txt` context + grep p6/p7).
- PDF p6 footnote 1 (airfreight countries): *"charged based on dimensional weight (LxWxH in cm/6,000)"*. Direct read.
- **Density covenant (NEW vs engine):** PDF p5 (domestic) & p6 (European): *"The average volume per kg must not exceed 6 litres."* This is a contractual avg-density condition on the whole book (6 L/kg ≈ the 6000 divisor), not a per-parcel surcharge trigger. Flag: not modelled in the engine; a book-level covenant, not a parcel rule.

### Oversize / bulky surcharge amounts + thresholds — AMOUNTS stated, THRESHOLDS deferred
From `ORWO offer.xlsx` → "Additional price components" sheet AND PDF p9 (`/tmp/gls_p9.txt`):

| Surcharge | ORWO amount | Trigger as printed on the ORWO card |
|---|---|---|
| Overlength | **1.60 €/parcel** | "Parcel length > threshold, max. 2,00 m according to GTC" — **threshold value NOT numeric on card** |
| Big Parcel | **0.80 €/parcel** | "Parcel volume > threshold" — **threshold NOT numeric on card** |
| Oversized Package | **30.00 €/parcel** | "Expense allowance according to GTC (exclusion of carriage)" — **no numeric girth/dim on card** |
| Non-conveyable goods | **0.80 €/parcel** | "Manual sorting … NC goods guideline" — shape-based, no dim |
| Toll National | 0.38 € | — |

- PDF p9 footnotes: (1) thresholds → *"Details available at www.gls-pakete.de/en/glossary"*; (2) Overlength and Non-conveyable are **mutually exclusive** (overlength paid → no NC) — matches engine's `bulky` exclusivity group.
- **ORWO amounts == Picanova/EU-tender amounts** (1.60 / 0.80 / 30.00 / 0.80) — the surcharge € figures carried over unchanged. Direct read.

### Max-size limits on the ORWO card
- Max weight **40 kg** (top weight band, both parcel sheets — Business Parcel header runs to 40 kg, Euro to 40 kg). Direct read.
- Dim caps (200/80/60 cm sides, 300 cm L+girth): **NOT printed on the ORWO card** — deferred to GTC §4.2 / glossary, same as Picanova.

---

## KEY QUESTION — can we compute an oversize surcharge for EVERY parcel from dims?

**YES — for the dim-derivable surcharges, given the engine's thresholds. The blocker is that the ORWO card does NOT print the numeric thresholds; it points at the GLS GTC/glossary.**

- **Big Parcel (0.80 €):** fully dim-derivable. Trigger `L*W*H cm / 1000 > 150 litres`. Every parcel with L/W/H computes it — no DHL Sperrgut flag needed.
- **Overlength (1.60 €):** fully dim-derivable. Trigger `d_max > 120 cm` (with the 120–200 cm band; >200 cm → excluded). Computable per parcel from sorted dims.
- **Oversized exclusion (30 €):** dim-derivable as a reject. Trigger `length_plus_girth_cm > 300 cm` (or any side over 200/80/60). Computable per parcel.
- **Non-conveyable (0.80 €):** NOT dim-derivable — packaging/shape signal absent on `fact_shipments`; stays off. (Its dim sub-trigger is already absorbed by Overlength.)

So you can reprice the GLS oversize/bulky tail **entirely from parcel L/W/H + gross weight**, independent of DHL's Sperrgut flag, using the EU-tender engine's logic. The trigger set is: `d_max>120` → +1.60 Overlength; `volume>150 L` → +0.80 Big Parcel; `d_max>200 | d_mid>80 | d_min>60 | L+girth>300` → 30 € Oversized exclusion (reject). Overlength and NC are mutually exclusive.

---

## GAPS / inferred vs read

- **THRESHOLD PROVENANCE GAP (load-bearing).** The numeric thresholds (Overlength 120 cm, Big Parcel 150 L, Oversized girth 300 cm) are **NOT on the ORWO offer card** — the card says "> threshold" and defers to the GLS glossary/GTC. The 120/150/300 numbers in the EU-tender engine were resolved from the **Picanova** GLS card + GLS Round-1 Q-answers (Q12/Q14), per `gls/constants.py:49-64,127-129`. **Inference for ORWO:** GLS GTC thresholds are carrier-standard, not deal-specific, so they should carry to ORWO — but this is an *assumption*, not read off the ORWO card. Confirm vs the GLS glossary or ask GLS for ORWO if the bulky tail is material.
- Overlength "max 2,00 m according to GTC" is the upper bound on the surcharge band, not the trigger; the 120 cm trigger itself is glossary-sourced (inferred for ORWO).
- Density covenant "avg volume per kg ≤ 6 L" (PDF p5/p6) is a contractual book-level condition, not modelled per-parcel. Flag for whoever sizes the reprice.
- `rate_cards.md` carries no GLS notes (UPS only) — no prior ORWO-GLS dim reconciliation exists; folder is PARKED.
- All € amounts and the 6000 divisor / 30 kg cap are **direct reads** from the ORWO xlsx + PDF. Only the numeric *thresholds* for the three bulky surcharges are inferred-from-Picanova for ORWO.

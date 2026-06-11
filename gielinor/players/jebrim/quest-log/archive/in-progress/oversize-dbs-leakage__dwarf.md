# Dwarf dig: OVERSIZE/BULKY → DB Schenker freight leakage

**Question:** Are the Maersk and Hermes engines' oversize/bulky tiers capturing parcels that physically should go to DB Schenker FREIGHT — i.e. is the "must-freight residual" (audit: 165 shipments / €24,462 / 0.81%) UNDER-counted because parcel engines accept arbitrarily large parcels at a flat oversize surcharge instead of rejecting to freight?

**Repo:** `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis` @ HEAD 39c4595 (read-only). Data: `data/cost_matrix_2026q1/cost_matrix_2026-{01,02,03}.parquet` (long-format, 1 row per shipment×carrier) + `routing_2026q1/routing_assignment.parquet` (531,194 winning assignments).

---

## VERDICT (short)

**Yes — the must-freight residual is under-counted, and the cause is engine-build staleness, not engine design.** Both engines DO encode upper reject ceilings in their *source* (Maersk 3.1.0, Hermes 2.1.0), but the **committed cost matrix and routing assignment were built with the PRE-tightening engines (maersk-3.0.0, hermes-2.0.0)**. Both tightenings are dated **2026-06-10 (today)** and have not been re-run through the pipeline.

**Combined leak: ~3,448 shipments, ~€40,158 Q1 engine-priced (~€160k/yr)**, currently won by a parcel engine but which the *current* source-code engines would reject to freight.

- **Maersk leak: 846 shipments / €22,166 Q1** — dominated by **818 GEL "tube" parcels at a fixed (200×150×30 cm) geometry** = pure girth 360 > 300 ceiling. The maersk 3.1.0 constants comment names these exactly: *"the GEL tubes at 200 cm / 360 girth were wrongly accepted."*
- **Hermes leak: 2,602 shipments / €17,992 Q1** — parcels that exceed the bulky girth ceiling (standard L+girth > 300, or bulky 120<longest≤170 with L+girth > 360). **All priced with bulky surcharge = €0** (they're *over* the bulky ceiling, so the bulky condition `L+girth ≤ 360` doesn't fire → priced as plain standard parcels with no oversize uplift at all).

**Bigger leak: Maersk by EUR (€22k vs €18k) and by per-parcel severity (avg €26 vs €7); Hermes by parcel count (2,602 vs 846).**

**Bias direction: overstates the saving.** These are physically freight-sized parcels priced cheaply as oversized-parcel (Maersk avg €26.20; Hermes avg €6.91, many with literally zero oversize surcharge). True freight cost is higher → the parcel-engine win understates cost → the modelled saving vs DBS is overstated. The 165/€24k residual under-counts by **~3,448 parcels / ~€40k of mispriced engine cost** (the EUR *gap* to freight is larger still — see caveat).

---

## 1. Upper eligibility caps (source code)

### Maersk — `carriers/maersk/`
- **Absolute handling/loading ceiling (3.1.0, Maersk reply 2026-06-10)** — `constants.py:70-72`: `MAX_LONGEST_SIDE_CM = 175.0` (DE relaxed to `MAX_LONGEST_SIDE_DE_CM = 200.0`), `MAX_GIRTH_CM = 300.0` (pure girth = 2·(W+H) = `length_plus_girth_cm − d_max`). Enforced in `calculate.py:244-256` (`over_handling_ceiling`), reject reason `over_handling_ceiling`, and it **rejects even surcharge countries**.
- **The pre-3.1.0 hole (the leak's root):** before 3.1.0, the only oversize reject was `oversize_no_surcharge` (`calculate.py:268-269`), which fires **only when the destination has no surcharge value**. For surcharge countries, exceeding the per-country spec just triggers the flat `eu_oversize` surcharge (`surcharges/eu_oversize.py:32-43`) with **no upper reject** — so arbitrarily large parcels were accepted at one flat fee. The 3.1.0 ceiling closes this, but **the built matrix is 3.0.0**, so the hole is still open in the data.
- Per-country oversize spec caps are in `rate_tables/eu_oversize.parquet` (31 rows). These caps gate *whether the surcharge fires*, not an upper reject (when a surcharge exists).

### Hermes — `carriers/hermes/`
- **Length reject:** `constants.py:35` `MAX_LENGTH_CM = 170.0` (tightened 200→170 in 2.0.0). `calculate.py:189` → `over_max_length`. **This one IS in the built data** (hermes leak shows 0 parcels with d_max>170).
- **Girth product gate (2.1.0, Hermes reply 2026-06-10)** — `constants.py:46-47`: `STD_MAX_SIDE_CM = 60.0`, `STD_MAX_GIRTH_CM = 300.0`; bulky ceiling `BULKY_MAX_GIRTH_CM = 360.0` (`constants.py:118`). Enforced `calculate.py:195-209` (`over_max_girth`): standard (longest≤120) rejects W>60/H>60/girth>300; bulky (120<longest≤170) rejects girth>360. girth = `length_plus_girth_cm` = L+2W+2H. **This gate is NOT in the built data** (matrix is hermes-2.0.0; the 450 L volume gate it replaced was looser).
- **Bulky surcharge** (`surcharges/bulky.py:42-48`) fires only for `120 < longest ≤ 170 AND L+girth ≤ 360`. Anything over 360 girth gets **no bulky charge** AND (pre-2.1.0) **no reject** → priced as a normal parcel. That is the Hermes under-pricing mechanism.

**Answer to the spec sub-question:** Hermes' product spec (Bulky = longest 120–170 AND girth ≤ 360). The *source* engine (2.1.0) now enforces the 170 length reject AND the 360 girth reject. But the *built* engine (2.0.0, in the data) enforces only 170-length; the 360-girth upper reject is absent, so over-360 parcels are priced beyond the bulky envelope with zero bulky fee.

---

## 2. The DB Schenker freight envelope

- **There is no DB Schenker rate engine.** `carriers/` has dirs for maersk, hermes, dhl_paket, dpd_pl(+_current), ups, gls, fedex, dhl_express, guell, austrian_post — **no `db_schenker`**. DBS rows in the cost matrix: **0** (verified across all 3 months).
- "Must-freight" is defined by **exclusion**, not by a DBS rate. `routing_2026q1/derive_envelope.py:35-83`: for each destination the envelope = the max parcel any *serving carrier still accepts* on each axis (gross kg, longest, L+girth, volume), derived from **the carriers' own `eligible` flags**. A parcel → DB Schenker **iff `n_elig == 0`** (no serving carrier accepts it; `derive_envelope.py:57`).
- **This is circular w.r.t. the leak.** Because the envelope is built from the engines' own eligibility, any parcel the (stale, loose) parcel engines accept is *inside* the envelope by construction and can never be counted as must-freight. Tighten the engines (3.1.0 / 2.1.0) and the must-freight set grows. The 165-residual is an artifact of the looser 3.0.0/2.0.0 eligibility that produced the matrix.

---

## 3. Quantified leakage (routing winners ∩ would-reject under current source)

Method: join `routing_assignment.parquet` (winner = `family`) to the cost matrix on (shipment_id, carrier); keep rows where the carrier WON and is `eligible` in the built matrix BUT the current source-code ceiling would reject.

| Engine | Leak n | Engine-priced €Q1 | avg €/parcel | of which oversize/bulky surcharge |
|---|---:|---:|---:|---:|
| Maersk (pure_girth>300 or longest>ceiling) | 846 | 22,166 | 26.20 | €16,319 eu_oversize |
| Hermes (std L+girth>300 / bulky L+girth>360) | 2,602 | 17,992 | 6.91 | **€0 bulky** |
| **Combined** | **3,448** | **40,158** | | |

**Dimension distributions of the leaked parcels:**
- Maersk leak: d_max p50/p90/max = 200/200/200; L+girth p50/max = 560/560; weight p50/max = 13.7/29.0. (818 of 846 are the GEL cluster at exactly 200×150×30 → L+girth 560, pure girth 360.)
- Hermes leak: d_max p50/p90/max = 113/163/170; L+girth p50/p90/max = 320/391/455; weight p50/max = 7.3/29.0.

**Packagetype concentration** (matches the `OVERSIZE_PT` special-handling family in `carrier_envelopes.py:76-77`):
- Maersk leak: GEL 663, GEL VERSANDTASCHE klein 101, CUSTOM_OVERSIZED 82.
- Hermes leak: Zugeschnittene Verpackung 1169, CUSTOM_OVERSIZED 1070, Plattenverpackung 100x75 (strapped) 282. By dest: DE 2307, AT 105, FR 80, NL 66.

**Freight EUR gap — CANNOT be sized from committed data.** No DBS rate engine / 0 DBS rows. So I report parcel count + €40k engine-priced + dims, not a freight delta. Qualitatively: a 200×150×30 GEL tube or a strapped Plattenverpackung is true freight; DBS/pallet freight on such items runs well above the €7–26 the parcel engines charge, so the *unbooked* cost gap exceeds the €40k mispriced engine total — the saving is overstated by more than €40k Q1, but the exact figure needs a DBS rate card the project doesn't yet have priced.

---

## 4. Verdict (full)

1. **Under-counted? Yes.** The 165/€24,462/0.81% must-freight residual was computed from a matrix built with the looser maersk-3.0.0 / hermes-2.0.0 engines. The current *source* engines (3.1.0 / 2.1.0, both dated today) reject ~**3,448 more winning parcels** (~€40k Q1 engine-priced, ~€160k/yr) to freight. Re-running the pipeline would move them out of maersk/hermes and grow the must-freight count by roughly 20× (165 → ~3.6k) on parcel count.
2. **Bigger leak:** Maersk by EUR and per-parcel severity (€22k, avg €26, the GEL 200/360-girth tubes); Hermes by count (2,602) but cheap/zero-surcharge mispricing.
3. **Bias on the saving:** **OVERSTATES it.** Freight-sized parcels are priced as cheap oversized-parcel (Maersk) or as plain standard parcels with *zero* bulky surcharge (Hermes) → modelled parcel cost understates true freight cost → saving vs DBS overstated. Magnitude ≥ €40k Q1 (engine-priced floor); true gap larger but unsizable without a DBS rate.

### What it takes to fix / confirm
- **Rebuild `cost_matrix_2026q1` with the current source engines (maersk-3.1.0, hermes-2.1.0)**, then re-run `routing_2026q1/build_*` + `derive_envelope.py`. The must-freight residual will re-derive correctly (the GEL/oversize tail will fall out of the parcel envelopes).
- The leak is **self-correcting on rebuild** — no design change needed, the ceilings already exist in source. The defect is purely that the artifacts are stale relative to today's two engine-version bumps.

### Caveats / honesty
- EUR freight gap not sized (no DBS rate engine; 0 DBS rows in matrix). Reported counts + engine-EUR + dims instead, per brief.
- "Would-reject" computed by replicating the 3.1.0/2.1.0 reject expressions against the built matrix's dims; I did not re-execute the engines. The maersk-3.1.0 girth-definition assumption (pure girth = 2·(W+H)) is the engine's own documented, flagged-to-confirm reading (`constants.py:65-69`) — if Maersk means L+girth instead, the maersk leak grows.
- Routing assignment (531k) is a sample/subset of the full population (cost matrix 1.94M shipments × 10 carriers); leak figures are on the routed winners, which is the right denominator for "what's mispriced in the decision."

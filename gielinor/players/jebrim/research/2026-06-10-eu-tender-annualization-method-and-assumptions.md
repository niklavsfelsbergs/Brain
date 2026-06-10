# EU Tender 2026 — annualization method + running assumptions log

**Date:** 2026-06-10 · **Author:** Jebrim · **Status:** design locked with Niklavs. **Both engine rebuilds landed + committed** — oversize (HEAD 6833671, maersk-3.1.0/hermes-2.1.0) + Hermes flat-7% fuel (HEAD 052d3c4, hermes-2.2.0; all 3 Q1 reports rebuilt, headline €275,484/9.32%). **Remaining: build the annualization report (the 4th report) per Part A.** DHL bulky confirmed correct (round-2), no further engine change.
**Companion:** the red-team audit → `2026-06-09-eu-tender-2026-red-team-audit.md` (tier-(a) items A0–A5 still stand; this note is the forward-build spec + the assumptions ledger).
**Purpose:** one source for (1) how the full-year-2026 annualization report is built, and (2) every modelling assumption in force — so the build owner and the end-of-project assumptions summary both read from here.

---

## PART A — Annualization method (the 4th report)

### Goal
Full-year 2026 cost for **both** the do-nothing baseline and the chosen 6-carrier tender portfolio → the **annual saving**, presented as a **band** (fuel-rate sensitivity), not a point. The Q1 anchor (**€275,484 / 9.32%** post-rebuild, on 531,194 parcels / €2,955,020) is the low-season floor; the annual figure is a separate re-weight, **never a ×4**.

### The simplification that makes this clean (LOCKED 2026-06-10)
After the flat-fuel decisions (Hermes flat 7%, Maersk EU 6.6% / ROW 24.75%, DHL 1.25%/5%, DPD 5%/11%), **every engine's fuel is now month-invariant.** So the *only* cost component that varies across the year is **PEAK** (Oct–Dec). Annualization collapses to:

> **annual cost = (peak-free unit cost, already in the matrices) × annual volume + (peak rate) × peak-window volume.**

No 12-month fuel curve to model. This is the whole reason flat-7% Hermes was worth doing — it buys a transparent, defensible annualization.

### Core principle
**One consistent 2026 cost basis, applied identically to do-nothing and tender.** Never compare a 2025 invoice on one side to a 2026 engine cost on the other. 2025 data is used only to (a) shape the seasonal volume curve and (b) derive the invoiced carriers' real Q4 peak premium.

### Step 1 — Base = 2026-Q1 book (NOT a 2025 replay)
Carrier mix flipped wholesale 2025→2026, so a 2025-population replay is invalid (carries GLS/Colis-Privé that's gone; misses DPD-PL/Maersk that's now in):

| Carrier | 2025-Q1 | 2026-Q1 | |
|---|---|---|---|
| GLS | 84,164 | 0 | **gone** |
| Colis Privé | 29,064 | 0 | **gone** |
| DPD Poland | 2,622 | 68,010 | +2,493% |
| Maersk | ~0 | 27,452 | **new at scale** |
| DHL | 323,165 | 270,517 | −16% |
| UPS | 139,252 | 144,314 | +4% |
| DB Schenker | 5,895 | 9,917 | +68% |
| Direct Link | 6,734 | 8,391 | +25% |

→ **Base = the 531,194 2026-Q1 parcels (current mix, the routing decision baked in).** 2025 = seasonal shape + peak premium only.

### Step 2 — Volume → full-year, per-country
Volume is **−10.5% YoY** (2025-Q1 590,857 → 2026-Q1 528,598) and **divergent by country** → scale **per-country**, not one global factor:
- Per country: `FY_2026 ≈ Q1_2026_actual × (FY_2025_country / Q1_2025_country)`.
- 2025 monthly share of FY: **Q1 20.7% · Q2 21.2% · Q3 17.9% · Q4 40.2%** (Dec 21.5%). Global: ÷0.207 ≈ **~2.56M FY parcels**.
- Movers (own ratio, not blanket): DE −14%, FR −15% (drive the decline); CH +42%; DK −31%; FI −31%.
- ⚠ **Assumption:** 2026 Q2–Q4 track 2025's *shape* at 2026-Q1's *level*. If the YoY decline accelerates, ~2.56M is a mild over-estimate (volume sensitivity band).

### Step 3 — Cost = peak-free base + peak (by carrier class)
| Carrier class | Carriers | Annual base | + Peak |
|---|---|---|---|
| **Engine** | DHL Paket, Hermes, Maersk-EU, DPD-PL-current | Q1 **peak-free** unit cost × annual volume | engine peak rate × peak-window volume — DHL €0.19 (Nov–Dec) + €0.50 PiP (Nov24–Dec7); Hermes/Maersk €0.25 (Oct–Dec); **DPD none** |
| **Invoiced, has 2025 history** | UPS, DB Schenker, Direct Link | Q1 unit cost × **GRI** × annual volume | **Q4 peak premium derived from the 2025 matrix** `real_total_eur` (their real billed Q4 uplift) × peak-window volume |
| **Invoiced, NO 2025 base** | **Maersk-FR** | Q1 actuals × annual volume | **€0.25/parcel assumed** (Oct–Dec) — no 2025 invoices to inherit from |

The invoiced-carrier peak premium (UPS etc.) is the one clever bit: their Q1 invoices are peak-free, but their *2025* invoices carry real peak — so we measure the premium from 2025 and apply it, grounded in their actuals, not assumed.

### Step 4 — Routing fixed; both sides; fuel as a rate band
- **Routing FIXED** — re-price the Q1 rules across full-year volume; **no peak re-routing** (operational reality).
- **Both sides identical** → `saving = FY_baseline − FY_portfolio`. Peak fires on both sides, so it largely cancels in the *saving* — the directional result is robust.
- **Fuel = a RATE sensitivity** (vary the flat rates, e.g. Hermes ±2pp, Maersk ±2pp) → present the saving as a **band**. (Not a monthly-index sweep — fuel is flat now.)

### Step 5 — Q4 product-mix: NOT adjusted (LOCKED 2026-06-10, qualitative caveat only)
**Decision: do NOT compute a Q4 product-mix adjustment** — too much complexity for the last leg. Q1 unit costs apply to Q4 volume. **Caveat to state:** Q4 likely carries bulkier gift products (calendars/posters) than Q1, so annual cost on *both* sides may be modestly understated; since it hits both sides it largely cancels in the saving, and it is **not quantified**. Honest, stated, not modelled.

### Step 6 — Peak direction (note both ways)
Migrating Q4 volume *off* high-peak UPS *onto* lower-peak tender carriers may push the annual % saving **above** 9.32%, not below — if UPS's peak is steeper than the tender carriers'. Report the per-carrier peak exposure so the direction is visible.

### The centerpiece: the Q1 → annual bridge
The report's defensibility hinges on a **waterfall** that turns the trusted Q1 number into the annual one, each step named + sourced:

```
Q1 saving        €275,484  (9.32%)  [the audited, reconciled anchor]
× volume scale   →  ~€1.33M         (×~4.82 to full-year volume, per-country)
± peak           →  ?               (engine rates + 2025-derived invoiced premium; differential)
± fuel band      →  ?               (flat-rate sensitivity)
= ANNUAL saving  €X.XM  (~9% ± band) on ~€14M annual spend
```

### Report structure — match (and extend) the Q1 routing report
Build parallel to `routing_2026q1/`, reuse its HTML shell / dark theme.

| Q1 routing report | Annual report |
|---|---|
| Headline today/routed/saving €+% | Same, full-year, **as a band** |
| Per-carrier routing (parcels+cost) | Same, annual, **+ peak contribution per carrier** |
| Service + size-tier splits | Same |
| `saving_split` (DBS / lowconf_dest) | Same, annual |
| Caveats (FR-floor, carrier-only) | Same **+ annualization caveats** (Maersk-FR assumed peak, Hermes-7%, fixed routing, Q4-mix-not-modelled, volume-decline) |
| Reconciles, ties end-to-end | Same discipline |
| — | **+ the Q1→annual bridge** (legibility) |
| — | **+ monthly volume+cost curve** (Q4 spike visible) |
| — | **+ per-carrier peak-exposure exhibit** |

---

## PART B — Running assumptions ledger
Every modelling assumption in force, for the end-of-project assumptions summary. **C** = contract/offer-grounded · **F** = flagged assumption (defensible, document it) · **P** = placeholder (needs a real value).

| # | Assumption | Value | Basis | Status | Revisit trigger |
|---|---|---|---|---|---|
| Fuel-1 | DHL fuel | DE energy 1.25% (+€0.19 toll/CO₂); Intl Z4/5/6 5%, Z1/2/3 0% | DE 1.25% **carrier-confirmed round-2** (full 01/25–04/26 schedule, flat); engine matches | **C** | — |
| Fuel-2 | Hermes fuel | **flat 7% all months** | principal decision (was 0/0/7 by month) | **F / PENDING** — above offer's ~0% Q1 ladder; conservative. **NOT yet applied** — the oversize rebuild (HEAD 6833671) did *not* include it; needs a dedicated Hermes-fuel rebuild | **apply + rebuild all 3**; revisit if Hermes publishes real index |
| Fuel-3 | Maersk-EU fuel | **6.6%** point estimate (+2.4% Iran as sensitivity band, not in point) | principal-set; carrier reply gave band **4–6%** + blended formula | **F** — *above* the stated band; derivation doc `FUEL_SUMMARY.md` **referenced but missing** | chase Maersk monthly schedule; reconcile 6.6% vs 4–6% |
| Fuel-4 | Maersk-ROW fuel | 24.75% (FedEx Intl FSC × 50%, current snapshot) | analyst snapshot | **P** | pull FedEx-PL Q1 monthly (no carrier round-trip) |
| Fuel-5 | DPD-PL-current fuel | 5% (≤31.5 kg) / 11% (>31.5 kg) | contract | **C** | — |
| Surch-1 | DHL bulky/Sperrgut | €20 DE / €21 Intl on any side over the 120×60×60 envelope (`d_max>120 ∨ d_mid>60 ∨ d_min>60`) | **carrier-confirmed round-2**: 95×65×5 flat canvas → *"yes, bulky, one side 65>60"* (+ `509E-Infoblatt Sperrgut`) | **C** — engine correct; **NOT** the maersk/hermes girth class (DHL genuinely per-dimension) | — |
| Surch-2 | DHL thin-flat Sperrgut waiver | not modelled — price **full** Bulky today | DHL negotiating a waiver for ORWO <1 cm calendars, possibly thin canvases generally (`REVIEW_CONCLUSIONS.md:20`) | **F — upside-only** | if the waiver lands, the €2.31M Q1 / €11.62M FY Bulky line drops materially; revisit on Stefan's decision |
| Peak-1 | DHL peak | €0.19/parcel Nov–Dec + €0.50 peak-in-peak Nov 24–Dec 7 | contract | **C** | — |
| Peak-2 | Hermes peak | €0.25/parcel Oct–Dec | offer (slide 9) | **C** | — |
| Peak-3 | Maersk-EU peak | **€0.25/parcel Oct–Dec** (peer-anchored to Hermes) | **principal decision: keep €0.25, note it** | **P** — real schedule promised in email, never delivered | replace if Maersk sends the 2025 schedule |
| Peak-4 | Maersk-FR peak (annualization) | **€0.25/parcel Oct–Dec** (same peer-anchor) | no 2025 base to inherit | **P** | same as Peak-3 |
| Peak-5 | DPD-PL-current peak | **none** | **principal-confirmed DPD has no peak** | **C** — correct, *not* a gap | — |
| Peak-6 | Maersk-ROW demand | €0 | FedEx schedule Q1-only; full-year window no magnitude given | **F** (deferred) | if a ROW magnitude is published |
| Cost-1 | UPS | 2025 actuals × **1.05 GRI** | incumbent, no engine | **F** — GRI 5% vs own research note **5.9%** | confirm 2026 UPS GRI |
| Cost-2 | DB Schenker | 2025 invoiced × GRI | freight, no engine | **C** | — |
| Cost-3 | Direct Link | 2025 invoiced × GRI | orphan incumbent (€60,968 / 2% of book, unmapped) | **F** — carry-forward at actuals | confirm it stays / its 2026 treatment |
| Cost-4 | DPD-PL-current discount | ~9% off list | fitted (absent from offer xlsx) | **F** | confirm contractual discount |
| Vol-1 | Annualization volume | 2026-Q1 × per-country 2025 seasonal ratio; ~2.56M FY (Q4 40.2%) | 2025 shape, 2026-Q1 level + mix | **F** | re-check if YoY decline accelerates |
| Scope-1 | Tender population | PCS-PL site, invoiced-only, 17 EU countries | cost-matrix build | **C** | GB excluded by design |
| DQ-1 | Oversize→freight leak | ~3,448 parcels rerouted to freight | **FIXED** — HEAD 6833671, maersk-3.1.0/hermes-2.1.0 | **resolved** — cost the headline ~€100k (€377k→€277k); confirms the audit leak was real | — |

### Headline (for reference)
**Post-rebuild (HEAD 052d3c4):** **€275,484 / 9.32%** Q1 saving on 531,194 parcels / €2,955,020. Journey: €377,471/12.77% (original) → €276,951/9.37% (oversize fix, −€100k) → €275,484/9.32% (Hermes flat-7%, −€1.5k). `saving_split`: **DB Schenker 60.9%**, **`lowconf_dest` 87.4%**. Q1 = low season, **zero peak**. Annual = the separate re-weight this note specifies.
*Note: `routing_2026q1/routing_table_final.parquet` is a stale orphan (not read by the reports — they read `routing_stats.json` fresh); don't analyse off it.*

---

## Open carrier items to chase (for the assumptions summary's "pending" section)
1. **Maersk EU fuel** — monthly schedule + scope confirmation + the 6.6%-vs-4–6%-band reconciliation (+ write the missing `FUEL_SUMMARY.md`).
2. **Maersk EU/FR peak** — the real 2025 schedule promised by email but never attached.
3. **Maersk ROW fuel** — FedEx-PL Q1 monthly values (analyst-pullable, no round-trip).
4. **UPS GRI** — 5% vs 5.9%.
5. **DPD-PL-current** — confirm the ~9% discount is contractual. *(No-peak now principal-confirmed.)*
6. **DHL thin-flat Sperrgut waiver** — ORWO <1 cm calendars (possibly thin canvases generally); pending Stefan. Upside-only: if it lands, the €2.31M Q1 Bulky drops. Default = price full Bulky.

## Standing audit items (from the red-team, still open)
- **A0 — RESOLVED (2026-06-10):** MAERSKUK is a separate deal, **out of EU-tender scope**; the FR-only baseline is correct (matches `open_questions/maersk.md`). No action.
- **A1–A5** — saving leans on unvalidatable Hermes/Maersk-EU engines (face value); the scenario selector (`mandatory_saving`) has no per-parcel do-nothing floor. €377k is conservative on *peak* but exposed on *fuel + engine validity*.

## Build checklist (4th report — annual_2026/)
- [x] Oversize rebuild (HEAD 6833671).
- [x] Hermes flat-7% + all 3 Q1 reports rebuilt (HEAD 052d3c4); headline €275,484/9.32%.
- [ ] Per-country full-year volume = 2026-Q1 × (FY2025/Q1-2025); split each cell's volume into peak-window (per carrier: DHL Nov–Dec + PiP Nov24–Dec7; Hermes/Maersk Oct–Dec) vs non-peak, from the 2025 monthly shape.
- [ ] Derive the invoiced carriers' Q4 peak premium (€/parcel) from the 2025 matrix `real_total_eur` (UPS/DBS/Direct-Link); Maersk-FR = €0.25 assumed.
- [ ] Cost both sides = **peak-free base × annual volume + peak rate × peak-window volume** (engines from constants; invoiced from the derived premium; invoiced base × GRI). Fixed routing, re-priced, **no re-route**.
- [ ] `annual_saving = FY_baseline − FY_portfolio`; fuel **rate**-sensitivity band (not a monthly sweep). **Q4 mix NOT adjusted** — qualitative caveat only.
- [ ] Build the **Q1→annual bridge** waterfall.
- [ ] Render parallel to `routing_2026q1/` (reuse shell): headline-as-band, per-carrier + peak contribution, monthly volume/cost curve, `saving_split`, peak-exposure exhibit, full caveats.
- [ ] Append the assumptions table (Part B); reconcile + tie end-to-end.

# EU Tender 2026 — annualization method + running assumptions log

**Date:** 2026-06-10 · **Author:** Jebrim · **Status:** design locked with Niklavs. Oversize-engine rebuild **landed** (HEAD 6833671, maersk-3.1.0/hermes-2.1.0). Remaining before the 4th report: **(1) Hermes flat-7% fuel + rebuild all 3** (the only outstanding engine change — DHL bulky confirmed correct round-2, no change), then **(2) build the annualization report**.
**Companion:** the red-team audit → `2026-06-09-eu-tender-2026-red-team-audit.md` (tier-(a) items A0–A5 still stand; this note is the forward-build spec + the assumptions ledger).
**Purpose:** one source for (1) how the full-year-2026 annualization report is built, and (2) every modelling assumption in force — so the build owner and the end-of-project assumptions summary both read from here.

---

## PART A — Annualization method (the 4th report)

### Goal
Full-year 2026 cost for **both** the do-nothing baseline and the chosen 6-carrier tender portfolio → the **annual saving**, presented as a **band** (fuel sweep), not a point. The Q1 headline (**€276,951 / 9.37%** post-rebuild, on 531,194 parcels / €2,955,020) is the low-season anchor; the annual figure is a separate re-weight, **never a ×4**.

### Core principle
Replay a full-year parcel population through **one consistent 2026 cost basis**. **Never** compare a 2025 invoiced cost on one side to a 2026 engine cost on the other — same basis per carrier on *both* the baseline and the portfolio. The 2025 invoice is only ever used as the ×GRI 2026-cost proxy for a no-engine carrier, applied identically to both sides.

### Step 1 — Base population = 2026-Q1 actuals (NOT a 2025 replay)
The carrier mix flipped wholesale 2025→2026, so a 2025-population replay is invalid (it carries GLS/Colis-Privé volume that's gone and misses the DPD-PL/Maersk volume that's now in):

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

→ **Base population = the 531,194 2026-Q1 parcels (current mix).** 2025 is used for the seasonal *shape only*, never as the population.

### Step 2 — Project Q1 → full-year volume (per-country, 2025 seasonal shape)
Volume is **down ~10.5% YoY** (2025-Q1 590,857 → 2026-Q1 528,598) and **divergent by country**, so scale **per-country**, not by one global factor:

- For each country: `FY_2026 ≈ Q1_2026_actual × (FY_2025_country / Q1_2025_country)`.
- 2025 monthly share of FY (the projection key): **Q1 20.7% · Q2 21.2% · Q3 17.9% · Q4 40.2%** (Dec alone 21.5%).
- Global sanity: 528,598 ÷ 0.207 ≈ **~2.56M FY parcels** (vs ~2.86M if 2025 were reused — ~12% too high).
- **Assign Q2–Q4 ship-months** to the projected parcels so engine peak fires in Oct–Dec.
- Material per-country movers (apply their own ratio, don't blanket): DE −14%, FR −15% (drive the decline); CH +42%; DK −31%; FI −31%.
- ⚠ **Assumption:** 2026 Q2–Q4 track 2025's *shape* at 2026-Q1's *level*. If the ~10% YoY decline accelerates, ~2.56M is a mild over-estimate.

### Step 3 — Price on the consistent 2026 basis, by carrier class
| Carrier class | Carriers | Pricing | Peak source |
|---|---|---|---|
| **Engine** | DHL Paket, Maersk-EU, Hermes, DPD-PL-current | 2026 engine over the full-year population | fires natively by ship-month |
| **No-engine, has 2025 history** | UPS, DB Schenker, Direct Link | 2025 **monthly** invoice × 2026 GRI | inherited from real 2025 Oct–Dec invoices |
| **No-engine, NO 2025 base** | **Maersk-FR** (new at scale 2026) | 2026-Q1 actuals replayed across projected volume | **assumed €0.25/parcel** Oct–Dec (same peer-anchor as Maersk-EU — no 2025 invoices to inherit from) |

Maersk-FR is the special case the mix-flip created: it has no 2025 invoiced base to annualize from, so it can't inherit peak from history like UPS/DBS — apply the €0.25 assumption for consistency with the EU lane.

### Step 4 — Routing, fuel, both sides
- **Routing: FIXED.** Take the Q1-decided routing rules and **re-price** them across the full-year population. **No peak-driven re-routing** (we don't operate with monthly carrier-switching agility; the model shouldn't pretend to).
- **Forward fuel:** Q2–Q4 fuel indices don't exist yet → run a **low/mid/high fuel sweep**, present the annual saving as a **band**.
- **Both sides identical:** do-nothing baseline and tender portfolio both priced on the above. **Saving = FY_baseline − FY_portfolio.**

### Step 5 — Peak direction (model both ways)
Migrating Q4 volume *off* high-peak UPS *onto* lower-peak tender carriers may make the annual % saving come out **above** 12.8%, not below — peak fires on both sides, but if UPS's peak is steeper, the tender gains in Q4. The genuine downside is the **Q4 volume/mix shift** (heavier/bulkier gift parcels could change who wins). Model both directions; don't assume annualization only erodes.

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
**Post-rebuild (HEAD 6833671):** **€276,951 / 9.37%** Q1 saving on 531,194 parcels / €2,955,020 — down from €377,471 / 12.77% pre-oversize-fix (the fix correctly reroutes ~3,448 oversized parcels to DB Schenker freight, ≈ −€100k). New `saving_split`: **DB Schenker rerouting = 60.9%** of the saving, **`lowconf_dest` = 87.4%**. Q1 = low season, **zero peak**. Annual = the separate re-weight this note specifies.
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
- **A0** — Maersk scope: live mart shows MAERSKUK (32k) > MAERSKFR (28k); confirm UK is out of tender scope.
- **A1–A5** — saving leans on unvalidatable Hermes/Maersk-EU engines (face value); the scenario selector (`mandatory_saving`) has no per-parcel do-nothing floor. €377k is conservative on *peak* but exposed on *fuel + engine validity*.

## Build checklist (4th report, when the rebuild lands)
- [x] Oversize rebuild landed (HEAD 6833671, maersk-3.1.0/hermes-2.1.0); headline now €276,951/9.37%.
- [ ] Apply **Hermes flat-7% fuel** + rebuild all 3 (the only outstanding engine change).
- [ ] Build full-year population (2026-Q1 base × per-country 2025 seasonal weights; Q2–Q4 ship-months for peak).
- [ ] Price both sides on the Step-3 basis (engines native; UPS/DBS/Direct-Link at 2025-invoice×GRI; Maersk-FR at Q1-actuals + €0.25 peak).
- [ ] Fixed routing, re-priced; fuel low/mid/high sweep.
- [ ] Report annual saving as a band; show the Q4 peak-direction effect both ways.
- [ ] Append the final assumptions table (Part B) to the report.

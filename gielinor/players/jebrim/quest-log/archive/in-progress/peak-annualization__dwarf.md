# Dwarf dig — Peak/demand standing across the 6-carrier portfolio + Q1→annual reliability

**Brief:** Read-only analytical dig in bi-analytics (`NFE/projects/2_EU_tender_2026/2_analysis`, committed HEAD 39c4595). Where do PEAK/DEMAND surcharges stand across the chosen 6-carrier portfolio, and how reliably can the Q1 €377,471 / 12.8% saving be annualized?

**Portfolio (6):** DHL Paket, Maersk (FR actuals + EU engine), Hermes, DPD-PL-current, UPS (actuals×1.05), DB Schenker (freight). Only DHL Paket / Maersk / Hermes / DPD-PL-current have rate engines under `carriers/`; UPS and DB Schenker have **no engine dir** (actuals-based / freight).

---

## 1. Per-carrier peak/demand modeling

| Carrier | Peak modeled? | Module + constant (file:line) | Verdict |
|---|---|---|---|
| **DHL Paket** | **YES — wired** | `carriers/dhl_paket/surcharges/peak.py` + `peak_in_peak.py`; constants `dhl_paket/constants.py:108` `PEAK_PER_PARCEL_EUR=0.19` (Nov 1–Dec 31), `:119` `PEAK_IN_PEAK_PER_PARCEL_EUR=0.50` (Nov 24–Dec 7, **CONFIRMED** Round-2). Both in `surcharges/__init__.py` `ALL`. | Correct: €0 in Q1 because off-season; schedule fires Q4. |
| **Hermes** | **YES — wired** | `carriers/hermes/surcharges/peak.py`; `hermes/constants.py:96` `PEAK_EUR=0.25` (Oct 1–Dec 31, slide-9 confirmed). In `ALL`. | Correct: €0 Q1, fires Oct–Dec. |
| **Maersk (EU)** | **YES — wired, but FLAGGED placeholder** | `carriers/maersk/surcharges/peak.py` (fires on `service=="eu_hd"`, Oct–Dec); `maersk/constants.py:102` `PEAK_EUR=0.25` **peer-anchored to Hermes** (Maersk's own 2025 EU schedule is a deferred attachment, Q3 PARTIAL). In `ALL`. The module docstring is the audit's "deferred" note — but the value IS wired into the full-year matrix (≈€250k/yr). | Wired but provisional; replace when Maersk supplies the real schedule ([[S120_3760e65b_eu-tender-full-year-build|S120]] REVISIT). |
| **Maersk (ROW / FedEx Economy)** | **NO — documented deferral** | `maersk/constants.py:126` `ROW_DEMAND_EUR_PER_KG=0.0` — FedEx demand schedule known for Q1 only (€0.40/kg→suspend→€0.70/kg) but full-year Oct27–Jan18 window unwired. ROW = AU-only ≈26.2k ships = 0.9% of Maersk-eligible → bounded/immaterial. | Honest, bounded deferral ([[S120_3760e65b_eu-tender-full-year-build|S120]], principal-confirmed). |
| **DPD-PL-current** | **NO peak module at all** | `carriers/dpd_pl_current/surcharges/` has NO peak.py; `ALL` = FlatServices, ExceedTech, NonSortable, NonStandard, ZoneFee, Customs. | **Gap** — but it's the *incumbent/current* contract engine; full-year cost_peak = €0 (see §4). Whether DPD PL's current contract carries a peak charge is unmodeled. |
| **UPS** (actuals×1.05) | n/a — no engine | Peak captured *implicitly* in the actuals it bids (real invoiced peak is in the cost, ×1.05 GRI uplift on top). | Q1 actuals carry whatever peak UPS actually billed in Q1 (near-zero — off-season). Q4 peak not separately projectable from a Q1-only actuals bid. |
| **DB Schenker** (freight) | n/a — no engine | Freight basis, no parcel peak schedule modeled. | Not a parcel-peak exposure. |

**Audit claims verified against code:** Hermes Oct–Dec €0.25 ✓ (`hermes/constants.py:96`). Maersk EU peak €0.25 peer-anchored ✓ + ROW demand unwired ✓ (`maersk/constants.py:102,126`). DHL/Hermes/Maersk carry peak schedules ✓; DPD-PL-current does NOT (extends the audit — the only portfolio engine with no peak module). FedEx not in portfolio (confirmed: `carriers/fedex/` exists but fedex is not one of the 6).

---

## 2. Q1 is peak-free — confirmed

`data/cost_matrix_2026q1/*.parquet` (Jan/Feb/Mar 2026), summed across the 4 portfolio engine carriers:

```
carrier         cost_peak  cost_peak_in_peak  cost_demand  surcharge_peak_flags
dhl_paket       0.0        0.0                0.0          0
dpd_pl_current  0.0        0.0                0.0          0
hermes          0.0        0.0                0.0          0
maersk          0.0        0.0                0.0          0
```

All zero. (Whole-matrix note: `cost_demand=€77,719` shows up only on **dhl_express** — NOT in the portfolio — its demand surcharge overlaps Jan 1–Feb 16; irrelevant to the 6.) `real_peak_eur` is an **actuals** column (`sql/population_2026q1.sql:45` = `peak_demand_charges_eur`); Q1 actuals (`data/actuals_2026q1.parquet`) total **€1,764 real peak across 189,917 parcels** — i.e. the incumbents themselves paid ~zero peak in Q1. **Q1 is genuinely off-season on both the engine side and the actuals side.**

---

## 3. The annualization method — full-year matrix EXISTS and exercises peak

- `cost_matrix.py` builds a **full-year 2025** matrix: `data/cost_matrix/cost_matrix_2025-01..12.parquet` (12 monthly partitions, ~25.9M rows, off `data/population.parquet` = 2,875,235 full-year-2025 priced shipments). Chunked by month to avoid OOM ([[S120_3760e65b_eu-tender-full-year-build|S120]]).
- **Annualisation basis = "Option 1" — replay 2025 actuals on 2026 rate cards. EXECUTED 2026-05-28 ([[S120_3760e65b_eu-tender-full-year-build|S120]])** (`docs/NEXT.md:22`, `docs/DECISIONS.md`, `FULL_YEAR_SCOPING_NOTE.md`).
- It is explicitly **NOT a ×4** and **NOT raw — a seasonal re-weight**: decision_report.html:152–154 — *"Annualise later… Q1 is the low season — it does not exercise Q4 volume, peak surcharges, or the product-mix spike — so the annual figure is a separate re-weight (parked), not a ×4 of Q1."*
- The full-year matrix DOES fire peak (see §4). So the project has *two* layers: the **Q1 €377k operable saving** (low-season unit-cost basis) and a **separately-built full-year layer** that carries peak — they are deliberately kept distinct, and the headline saving quoted to management is the **Q1** number, with annualisation flagged as parked.

---

## 4. Sizing the annualization risk (full-year 2025 matrix)

**Peak fires in the full-year matrix** (`data/cost_matrix/*.parquet`, summed per portfolio engine carrier):

```
carrier         cost_peak   cost_peak_in_peak   peak as % of FY engine cost
dhl_paket       180,320     143,171             1.30%   (€323,491/yr total peak)
hermes          278,196     0                   1.70%
maersk          250,431     0 (EU placeholder)  1.11%
dpd_pl_current  0           0                   0.00%   (no module — gap)
```

**Volume profile (the reason ×4 is wrong):** Q1 2025 = 595,979 ships = **20.7%** of the year; Q4 = 1,152,681 = **40.1%** (December alone 616,740 ≈ 31% of the year). **Q1 × 4 understates annual volume by ~17%.** Annualisation must re-weight to the Q4-heavy demand cycle, not multiply.

**Q4-vs-Q1 unit-cost lift (full-year engine, eligible rows):**
- Hermes: Q1 €5.78 → Q4 €6.02 = **+4.0%/parcel**
- DHL Paket: −0.4%; Maersk: −0.4% (Q4 product-mix shifts lighter, offsetting the per-parcel peak add at the gross level — peak adds absolute cost but the Q4 mix dilutes per-parcel).

**Erosion read.** Gross peak is ~1.1–1.7% of each carrier's full-year cost. But the erosion to the *saving* is **differential**, not gross: in Q4 the **baseline incumbents also pay peak**, so peak only erodes the 12.8% to the extent the new-offer carriers' Q4 peak exceeds what they replace. The net peak drag on the headline % is therefore **small — order ~1–2 points** of margin — *if* baseline and new offer both carry peak symmetrically. The larger, unquantified levers are **Q4 volume×product-mix** (the 40% quarter never seen in Q1) and **forward fuel** (see below). A plausible honest-annualisation band: the 12.8% could move by **roughly ±2–4 points** on peak + Q4-mix alone before fuel.

**Biggest unmodeled peak exposure among the 6:** **DPD-PL-current** (zero peak module — if its current contract bills a Q4 peak, the full-year cost is understated and the saving overstated). After that, **Maersk EU** (the €0.25 is a peer-anchored placeholder, not the real schedule) and **Maersk-ROW demand** (unwired, but bounded to 0.9% of volume).

---

## 5. Forward fuel + Q4 product-mix — KNOWN GAPS, not projectable from the repo

- **Forward fuel:** explicitly DEFERRED. `docs/NEXT.md:46` — the low/mid/high fuel sweep (re-price each engine's fuel mechanism ×3 across the 26M-row matrix; present the headline as a *range*) is "the main outstanding full-year refinement," held for a focused session. The full-year report ships on a **single mid/current fuel point**. **Cannot be projected from committed repo state** — it is a parked computation, not a failure.
- **Q4 product-mix spike** (heavier/bulkier Q4 parcels): partially in the full-year matrix via actual 2025 Q4 dims, but its interaction with peak + bulky surcharges is inside the parked full-year layer, not the Q1 headline.
- **Seasonal layers still to wire** (`docs/NEXT.md:47`): DHL Paket Peak/PiP, Hermes Q4 peak, Maersk-ROW demand — i.e. the full-year build is real but not yet the polished annualisation deliverable.

---

## VERDICT

**How annualizable is the Q1 €377k?** It is a **clean, conservative low-season floor — NOT a number to multiply by 4.** Q1 is genuinely peak-free (verified both engine-side cost_peak=0 and actuals-side €1,764 real peak), so the €377k carries *zero* peak/demand. Annualising honestly requires (a) re-weighting Q1→full-year volume (Q1 is only 20.7%; Q4 is 40.1% — ×4 understates volume ~17%), (b) layering Q4 peak/demand (~1.1–1.7% of cost gross; smaller net of the baseline's own peak), (c) the Q4 product-mix spike, and (d) forward fuel as a range. None of (a)–(d) is baked into the €377k.

**Is the "separate re-weight, not ×4, pending" framing honest and present?** **YES — consistently and prominently:**
- decision_report.html:152–154 ("Annualise later… separate re-weight (parked), not a ×4 of Q1").
- management_briefing/eu_tender_2026_briefing.html:246, :252, :341, :364 — speaker notes ("this is one quarter… it is NOT simply four times this. We're not annualising today") + next-step ("produce the full-year budget figure with the seasonal re-weight") + appendix ("Full-year = a separate seasonal re-weight, not Q1 × 4").
- docs/NEXT.md, docs/ASSUMPTIONS.md:85,149,159–160 document every peak/demand/fuel deferral with revisit triggers.

The framing is not buried — it is on the management slide, in the speaker script, and in the decision report's own caveats. This is an honest, well-flagged deliverable.

**Single biggest annualization unknown:** **forward fuel** (explicitly deferred to a parked low/mid/high sweep — the headline is on one fuel point, and fuel moves all carriers' Q4 cost together; `docs/NEXT.md:46`). Runner-up structural unknown: **DPD-PL-current's unmodeled peak** (only portfolio engine with no peak schedule) and the **Maersk EU peak placeholder** (peer-anchored €0.25, real schedule still a deferred attachment).

---

### Files cited
- `carriers/{dhl_paket,hermes,maersk,dpd_pl_current}/surcharges/__init__.py`, `.../peak.py`, `.../peak_in_peak.py`, `.../constants.py` (lines per §1)
- `data/cost_matrix_2026q1/*.parquet` (Q1 peak=0), `data/actuals_2026q1.parquet` (real_peak €1,764), `data/cost_matrix/*.parquet` (full-year peak fires)
- `cost_matrix.py` (full-year build), `decision_report/decision_report.html:152–154,183`, `management_briefing/eu_tender_2026_briefing.html:246,252,341,364`, `docs/NEXT.md:22,46,47`, `docs/ASSUMPTIONS.md:85,149,159–160,177–199`

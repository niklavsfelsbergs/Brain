# Hermes routed slice — carrier-substitution delta (UPS-offer revisit gate)

**Drafted 2026-06-09 (Jebrim, EU tender routing).** Figures from `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/routing_2026q1/` — `routing_assignment.parquet` (per-parcel `family` assignment) + the 2026-Q1 cost matrix (`cost_matrix_2026q1.py`). Basis = Q1 2026 actuals; engine bid = `cost_total_eur` (cheapest eligible service per carrier); incumbent = real invoice `today_eur` (OML>€400 netted, LPS full). Links: [[eu_tender_2026]], [[S166_f82b01df_routing-service-split-build|S166]] routing service-split, [[S132_32ff1025_shipping-savings-routing-optimization]] (mirage discipline).

## The slice

The routing assigns **62,299 parcels to Hermes** at **€340,330** (Q1). All of it is *new* migration to Hermes (no hermes→hermes stay) — Hermes won every cell on its engine bid. Incumbent mix of the slice: **UPS 54,107** · DB Schenker 4,746 · DPD PL 3,353 · DHL 86 · residual 7.

Dominated by **long DE wrapped/flat formats** — `WICKELVERPACKUNG 80x60 / 100x75`, `STANZVERPACKUNG 120x80`, `ORWO_80x60`, `Plattenverpackung` — length+girth ~220–310 cm but light (~2.4–4.3 kg). Destination ~88% DE, rest AT/ES + a thin tail.

## What each alternative carrier would cost this slice (Q1)

| alt carrier | basis | parcels priced | their cost | Hermes cost (same) | delta |
|---|---|---|---|---|---|
| **UPS** | **real Q1 invoice** (it actually shipped these) | 54,107 | €302,773 (€5.60/pc) | €255,387 (€4.72/pc) | **+€47,386 (+18.6%, +€0.88/pc)** |
| DHL Paket | engine bid | 61,009 | €1,429,491 (€23.43/pc) | €324,170 (€5.31/pc) | +€1,105,321 (+341%, +€18.12/pc) |
| Maersk | engine bid | 61,884 | €1,506,315 (€24.34/pc) | €327,900 (€5.30/pc) | +€1,178,415 (+359%, +€19.04/pc) |

DHL can't carry 1,290 of the parcels at all; Maersk can't carry 415. UPS comparison covers only the 54,107 it actually shipped — **no UPS rate engine exists** in the matrix to price the other ~8,200 (DB Schenker/DPD incumbents Hermes also absorbs).

## The load-bearing finding

**DHL and Maersk are ~4× more expensive on this slice purely because they apply a ~€20 bulky/Sperrgut surcharge to the long DE formats** (DHL DE = €3.23 base + €20.00 `cost_bulky_de`; Maersk DE ≈ €26.25 flat). **Hermes carries the same parcel flat (~€4.43 median) with no equivalent penalty** — that is the *entire* reason it wins the slice. **UPS does NOT surcharge these formats** — its real DE rate was €5.35/pc, competitive. So against the carrier that actually shipped them, Hermes' edge is **thin: ~€47k/quarter, ~€0.88/parcel.**

→ The €1.1–1.2M DHL/Maersk gaps are "those two surcharge these formats into the ground," not "Hermes is irreplaceable." UPS is the honest benchmark, and Hermes only modestly beats it.

## Revisit trigger (the decision gate) — **principal-set 2026-06-09**

**When the UPS Round-1 offer lands, re-evaluate whether Hermes is needed at all.** Hermes earns its portfolio seat almost entirely on this one slice; if UPS's *offered* (post-tender) rate neutralizes the slice, Hermes' case collapses.

Re-run when the offer arrives:
- Re-price the 62,299 (or live equivalent) under the **UPS offer** engine (Phase-2 calculator, S163 — `1_offers/picanova/UPS/calculation/`), compare to Hermes.
- If UPS offered ≤ Hermes' ~€4.72/pc — or close enough that the ~€47k/quarter (~€190k/yr indicative) gap is outweighed by carrier-count reduction (≤6 cap), service quality, or avoiding onboarding a new carrier — **drop Hermes and keep this volume on UPS.**
- Factor the ~8,200 non-UPS parcels (DB Schenker/DPD incumbents Hermes absorbs) into whether UPS can take the *whole* slice.

**Annualisation caveat:** all figures are Q1; the tender decision basis re-weights to full-year (peak/Q4 mix/forward fuel — see keepsake EU-tender pin + `FULL_YEAR_SCOPING_NOTE.md`). Treat ~4× Q1 as indicative for annual, not committed.

---

## Mirror finding — UPS is the load-bearing carrier (NOT droppable)

Same analysis run on the **45,654 parcels the routing keeps on UPS** (UPS = incumbent-only, no offer engine yet; assigned because real invoice `today_eur` was cheapest). Question: if we stopped working with UPS, what do those parcels cost on the remaining 5?

| | parcels | UPS cost (today) | reroute to remaining 5 | saving lost |
|---|---|---|---|---|
| UPS-routed slice | 45,654 | €412,557 (€9.04/pc) | €701,821 (€15.37/pc) | **+€289,263 (+70%)** |

**Dropping UPS surrenders €289k/quarter = 70.3% of the entire €411k routing saving** — vs only €73k (17.8%) for dropping Hermes. UPS carries almost the whole optimization.

**No clean substitute — it's lane-structural.** Concentrated where UPS is uniquely cheap and the EU-6 alternatives aren't:

| dest | parcels | extra cost if UPS dropped |
|---|---|---|
| **FR** | 16,470 | **+€129k** |
| AU | 3,196 | +€54k |
| DE | 15,013 | +€39k |
| CH | 3,146 | +€31k |
| NL | 1,934 | +€23k |

- **France is the killer (+€129k)** — UPS is structurally cheap on FR; the only FR alternative is the Maersk-FR incumbent and the engines reprice well above UPS. Same FR-dependency seen in the DB Schenker must-freight set + the FR-extend decision.
- AU / CH / overseas / heavy-international — UPS cross-border beats DHL/Maersk/Hermes by a wide margin (~€20/pc Maersk vs €9 UPS).
- Volume scatters (19,430→Hermes, 9,472→DPD PL, 9,216→DHL, 7,342→Maersk) each at a big premium; no single carrier absorbs it cleanly.

**The two findings are mirror images:** Hermes is droppable (its slice mostly reverts to UPS at near-parity, €73k); UPS is not (holds FR/overseas/heavy lanes the EU-6 can't match, €289k). **The live question isn't "can we drop UPS" — it's "how hard do we negotiate the UPS renewal," because ~70% of the saving leans on it.** A *better* UPS offer raises, not lowers, the cost of walking away.

(Same basis: per-parcel cheapest engine bid = a floor, slightly optimistic vs cell-constrained routing; UPS at real Q1 invoice OML-netted. Filename is Hermes-anchored but this note now covers both droppability findings.)

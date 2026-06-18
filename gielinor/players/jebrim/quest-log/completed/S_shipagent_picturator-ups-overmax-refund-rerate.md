# Picturator UPS — over-max refund re-rate (sibling to estimate-gap / quota-maturity)

**Spawned by:** Jebrim (principal), shipping-agent emulation
**Tier:** gold-contract (`shipping_mart` only; no CLAUDE.local.md → gold perimeter absolute)
**Scope:** Picturator (`source_system='Picturator'`), UPS (`shipping_provider_group='UPS'`), order-month, matured = invoiced Jan–May 2026
**Siblings:** `S_shipagent_picturator-june-estimate-gap-decompose.md`, `S_shipagent_picturator-june-quota-maturity.md`

## Ask
Re-rate UPS actuals removing the over-max surcharge family (OML + peak/demand-OML, net of in-place reversals), keep LPS. Does the refunded-actual close the gap to the June mart estimate (~€6.72)? Quantify the strip; tie back to June quota.

## Status trace
- Charge-code map verified live: oversize sub-types live in `fact_shipment_invoice_lines.charge_description_english` (mart collapses to one `oversize_overweight` bucket per rule 15). Over-max family = "Over Maximum Size" (SOV), "Over Maximum Length", "Demand Surcharge - Over Maximum" (demand-OML), + WorldEase variants.
- Cost-summary exists ONLY for invoiced parcels (238,196 inv / 4,189 expected / 263 null) → it IS the matured set. Demand-OML/SLP sit in `oversize_overweight` bucket, NOT `peak_demand_charges` (that bucket only €1.9k).
- Matured UPS-Picturator: 238,196 parcels, €2,078,092 → **€8.72/parcel**. Family split reconciles to bucket €263,222 exactly: LPS €126,729 / over-max €126,634 / demand-LPS €8,741 / add-handling €1,114.
- Over-max family net €126,634 = gross €193,847 − reversals €67,213 (~35% already clawed in-place). Strip = **€0.532/parcel**.
- After strip: €8.19/parcel. June estimate confirmed live = **€6.72/parcel** (18,816 expected June parcels). Residual gap **€1.47/parcel (~22%)** AFTER refund.
- Dimension legitimacy (S124): over-max-charged parcels max length+girth 328.7cm, NONE >400cm (UPS over-max threshold), 145/199 even <300cm (under large-package threshold). Surcharge lands on non-qualifying parcels → supports refund/dispute basis.
- Quota tie-back: June implied-mature 17.31% (full UPS) → **17.04%** (UPS net OML refund). Strip moves it only **−0.28pp**.

## Verdict
Stripping over-max does NOT close the gap. Refunded-actual €8.19 vs estimate €6.72 → residual **€1.47/parcel (~22%) shortfall remains**. Over-max is only ~29% of the total estimate gap (€0.53 of €1.85 mature actual − but only €0.53 of the €2.00 gap to estimate). The estimate is structurally low on UPS even with ALL disputed over-max refunded — the bulk of the under-estimate is base rate + LPS + fuel, not over-max. The "defect" is NOT mainly un-refunded over-max.

## Checks
- Family split sums to cost-summary oversize bucket (€263,222) to the cent.
- Gross/net reversal discipline: strip = remaining NET (€126,634), not gross (€193,847) — actuals already net ~35% clawback.
- Quota numerator recomputed live both ways; revenue denominator clean (€3.96M, no anomaly).
- Dimension cross-check confirms over-max mis-application (refund assumption defensible).

## Deliverable
Chat-only findings + SQL returned to principal. No chart requested.

---

## Follow-up (2026-06-18): realistic-net multiplier — over-max fully refunded + 30% LPS on un-refunded months

**Ask:** multiplier on top of the UPS estimate to average out to total cost WITHOUT over-max, assuming 30% LPS refund on months not yet refunded. Build target net cost/parcel → express as multiplier vs both estimate bases.

**Trace:**
- Confirmed matured set live: 238,196 parcels / €2,078,092 / €8.7243 pp, order-month (`shop_order_created_date`) Jan–May 2026, invoiced. Components: base 5.5237, fuel 1.1248, linehaul 0.6493, residential 0.2177, oversize-bucket 1.1050, other 0.1035. Reconciles to cent.
- Family split reconciled to oversize bucket €263,222: over-max net €126,634 (= gross €193,847 − reversals €67,213, ~35% in-place) — **identical to prior pass**; LPS family net €135,470; add-handling €1,118.
- **LPS by order-month (gross/net/reversal):** Jan net 36,824/gross 41,654/rev −4,831 (refunded); Feb 16,826/20,990/−4,164 (refunded); Mar 14,229/24,918/−10,689 (refunded ~43%); Apr 38,390/44,382/−5,992 (refunded); **May 29,202/29,202/0 reversals → ONLY un-refunded month.**
- 30% assumption applies to May only: −0.30 × €29,202.40 = **−€8,760.72**. Jan–Apr left at net (no double-refund).
- **Target = €2,078,091.89 − 126,634.00 (over-max) − 8,760.72 (May LPS 30%) = €1,942,697.17 → €8.1559/parcel.** Adjusted-LPS = (135,470−8,760.72)/238,196 = €0.5320 pp.
- **Multipliers:** vs June est €6.72 → **1.2137**; vs Jan–May est €8.03 → **1.0157**.
- Cross-apply: June-mult on Jan–May est = €9.75 (19% over-lift); Jan–May-mult on June est = €6.83 (under-lift). Neither single multiplier is clean across both bases.

**Recommendation:** calibrate on the stable Jan–May estimate → **×1.0157** (target ≈ Jan–May est, +1.6%). The June ×1.2137 is an artifact of June's €1.30 denominator drop — applying it broadly over-corrects already-correct months. Best fix: repair the June estimate drop, don't bolt a multiplier on a moving denominator.

**Checks:** matured headline + family split reconcile to cost-summary bucket to the cent; over-max gross/net matches prior pass exactly; LPS month classification driven by reversal-line presence (not value heuristic); target ÷ actual = 0.9348 (strip is 6.5% of actual). Quota: target is 93.5% of actual cost → tracks the prior June implied-mature frame (17.31% → ~16.2% at target).

**Deliverable:** SQL at `shipping-agent/workbench/analysis/20260618-ups-lps-refund-multiplier/sql/20260618-01_ups-lps-refund-multiplier.sql`. Chat summary + multipliers returned.

---

## Follow-up (2026-06-18): SCM Overview quota chart — UPS family, actual vs refund-adjusted

**Ask:** reproduce SCM Overview Final quota for the UPS family, overlay a refund-adjusted quota. Two series per order-month, chart + monthly table + SQL. Scope deliberately WIDER than prior passes: UPS family (`shipping_provider_group='UPS'`, not Picturator-only), Order Source = PCS+PicaAPI+Picturator, Jan 2025 → Jun 2026.

**Scope confirmed / tie-out:**
- `source_system IN ('PCS','PicaAPI','Picturator')` IS the SCM "Order Source" filter. `shipping_provider_group='UPS'` reproduces the dashboard UPS line.
- Tie-out HIT to the cent: **May 2026 actual 22.24% (dash ≈22.2%), Jun 2026 actual 15.71% (dash ≈15.7%)**. No scope fix needed.

**OFF-CONTRACT flag (maintainer profile):** `fact_shipment_invoice_lines` carries NO UPS main-source charge detail right now — only `dhl` + `ups_orwo` (for recent months). The gold join to our UPS scope returns ~48 lines / 14 shipments. So the over-max/LPS family split + reversal lines were read from **`enterprise_silver.ups_invoices`** (full-access profile), mapped to the gold scope by `trackingnumber`. This is the gold→silver departure; figures reconciled back to the gold cost-summary oversize bucket per month (residual diff = additional-handling, left untouched). **Rulebook gap surfaced:** `fact_shipment_invoice_lines` is structurally incomplete for the main UPS invoice source — a gold-only colleague CANNOT do the family split / reversal classification this brief needs. Worth a coverage-audit note.

**Family codes (silver `chargedescriptioncode`):** over-max family = OVR (Über Maximalgröße), OML (Über Maximallänge), WRC (Über Maximalgewicht), **SOV (Nachfragezuschlag-Über Max. = demand-over-max)**. LPS family = LPS (Zuschlag für große Pakete), SLP (Nachfragezuschlag-Großes Paket). First family pass MISSED SOV (€22.3k in May 2026 alone) — caught via reconciliation gap vs the gold bucket; added it → reconciliation closed.

**Refund logic applied:**
- Over-max: strip remaining NET every month (actuals already net in-place reversals). Older months net ≈0 (already fully reversed); strip concentrates Nov 2025→May 2026.
- LPS 30% on un-refunded months only (zero reversal lines): **un-refunded = May 2026 + Jun 2026** (Jun tiny/immature). Jan 2025→Apr 2026 all carry LPS reversals → left at net, no double-refund.

**Headline numbers (actual → adjusted):**
- May 2026: quota 22.24% → 19.84% (−2.40pp), avg €9.00 → €8.02. Biggest mover (un-refunded both families).
- Apr 2026: 22.38% → 21.20% (−1.18pp), €9.22 → €8.74.
- Jan 2026: 21.62% → 20.28% (−1.34pp). Feb 21.38% → 20.32%.
- Jun 2026: 15.71% → 15.70% (−0.01pp) — only 5.9% invoiced, refund near-zero, coverage-immature.
- Older months (Feb–Aug 2025): no adjustment (over-max fully reversed, LPS refunded).

**Checks:** tie-out to SCM dashboard hit both anchor months; family split reconciled to gold cost-summary oversize bucket per order-month (older months diff <€800; recent-month gap = additional-handling, correctly left alone); over-max gross/net reversal discipline (strip remaining net, not gross); LPS month classification driven by reversal-line presence not value heuristic; chart labels render clean (€ + → no mojibake).

**Deliverable:**
- Chart: `shipping-agent/workbench/analysis/20260618-ups-quota-refund-adjusted/outputs/20260618-063705--ups-quota-actual-vs-refund-adjusted.html`
- SQL: `…/20260618-ups-quota-refund-adjusted/sql/20260618-01_ups-quota-actual-vs-refund-adjusted.sql`
- CSV: `…/20260618-ups-quota-refund-adjusted/data/20260618-01_ups-quota-monthly.csv`
- Chart script: `…/20260618-ups-quota-refund-adjusted/notebooks/build_quota_chart.py`

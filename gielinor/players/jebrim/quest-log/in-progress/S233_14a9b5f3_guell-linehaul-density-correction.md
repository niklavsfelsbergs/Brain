# S233 — Güll line-haul density: grounded against the mart, marginal collapses

**Player:** Jebrim · **sid8:** 14a9b5f3 · **2026-06-12**
**Thread:** continuation of [[S230_b94d4675_eu-tender-no-hermes-with-gull-report|S230]] — the density/line-haul estimation the [[S230_b94d4675_eu-tender-no-hermes-with-gull-report|S230]] resume named as the next step.

## The ask

Niklavs (eu tender): the Güll engine assumes **150 parcels/pallet** for line-haul allocation but "thats completely random." Check what the data mart actually shows for parcels per loading unit.

## What was done

Two shipping-agent pulls off the gold `shipping_mart`:

- **[[S231_shipagent_guell-pallet-fill-substitutes|S231]]** — the mart carries a **loading-unit** (pallet-grain) grouping, ~96% populated on Szczecin (Güll's origin). Q1-2026 Szczecin loading units average **~52 parcels** (median 33, n=11,739 — robust). Per-parcel weight/volume on the AT/CH lanes pulled: weight cap reached ~176 (AT) / ~223 (CH) parcels; geometric volume ceiling ~80 (AT) / ~101 (CH). 150 sits at the p90–p95 tail and above the AT volume ceiling — volume-bound, not weight-bound.
- **[[S232_shipagent_guell-loading-unit-by-destination|S232]]** — single-vs-mixed destination split. CH-only units pack denser (~70), AT-only sparse (~20, partials artifact — AT isn't dedicated today). Both thin (249 / 139 units). Confirmed: neither lane's single-country pallets cluster near 150.

**Finding:** 150 is ~2–3× the observed packing. The robust number is the **inbound** Szczecin pallet (~52); the inbound sprinter leg (€955 ÷ 8 pallets ÷ density) is the dominant term and where 150 did the most damage.

## The engine correction (guell-2.0.0, uncommitted)

`carriers/guell/constants.py`: split the flat `PARCELS_PER_PALLET = 150` into **`PARCELS_PER_PALLET_INBOUND = 52` / `_AT = 75` / `_CH = 75`** (a single density across the mixed inbound sprinter and dedicated outbound pallets was never lane-appropriate). Per-parcel line-haul: inbound €0.80→€2.30, outbound AT €0.16→€0.33, CH €0.27→€0.53. Updated derived constants, the three surcharge docstrings, `tests/fixtures.py` (the three `_INBOUND/_LH_AT/_LH_CH` constants — all expectations auto-derive). **19/19 tests pass.**

Also fixed `build_stats_no_hermes_with_gull.py`, which **hardcoded `150`** into the JSON — now imports the real split constants so it can't drift again.

## The result — Güll collapses

Regenerated cost matrix → stats → report. Güll's routed volume recomputed live (not held fixed):

- Routed volume **~87,000 → 308 parcels/yr** (CH only); the per-cell routing sheds Güll once it's dearer than DHL/DPD/UPS/Maersk.
- **Net marginal +€163,097 → +€520/yr.** The €163k was almost entirely the density artifact.
- 5-carrier floor (€976,024) unchanged — only Güll's constants moved; reconciliation closes at Δ€0.

Conclusion is robust to the soft outbound numbers: the inbound term (robust, n=11,739) alone collapses it.

## Report reframed (HTML regenerated)

`final_report_no_hermes_with_gull/report_no_hermes_with_gull.html` — reframed from "ADD Güll, +€163k" to **"Güll EVALUATED — not competitive at grounded density."** Summary, KPI, tier table, card role, Güll panel, density callout, risks, decisions-requested all rewritten. The one open lever surfaced: **inbound-sprinter consolidation** (does Güll share the €955 truck with other customers? → drops our per-parcel share). The old "PAPER vs defensible €60–120k" framing removed (it was a pre-grounding guess; €520 is the grounded answer).

## Decisions / locked calls

- Densities: inbound **52** (observed, robust), outbound **75/lane** (geometric-informed; AT-only obs unreliable due to partial-pallet artifact). The "~52/~75" values Niklavs endorsed via the multiple-choice.
- Güll: **do not add on current economics.** Re-evaluate only if the inbound sprinter economics change (consolidation lever).
- bi-analytics changes left **uncommitted** (separate repo, their go).

## Sibling flag (not acted on)

**Austrian Post** carries the identical unvalidated `LINE_HAUL_PARCELS_PER_PALLET = 150.0` — Güll's 150 was *borrowed from "AP precedent."* Same mart finding (~52) applies; AP's own note calls density "the largest single open lever (~€20–82k Q1)." Not touched (different carrier, out of scope) — flagged for whoever works AP next. [[feedback_fix_the_class_across_sibling_consumers]] / [[feedback_revalidate_borrowed_constants]].

## Pending external actions

- **bi-analytics commit** — pending principal (their go, separate repo). The guell engine + report changes are uncommitted in the working tree.
- **Logistics-manager conversation** — Niklavs owns: the inbound-sprinter fill + consolidation question (Picanova-only vs shared truck), and weight-vs-volume binding. This is the one lever that could revive Güll.

# Shipping-agent pull — DB Schenker / PCS PL / TCG: box vs product (basket contents)

**Spawned by:** Jebrim (principal) · **Agent:** shipping-agent (emulated) · **Date:** 2026-05-28
**Tier:** upstream / off the gold contract (product dims not in the mart — see below)

## The ask
Follow-on to the box-level freight-fit run. Prior run found 1,760 of 1,780 freight parcels bust 120cm on **box** dims. New hypothesis: some are oversize only because the *box* is bigger than the *product* needs. Compare shipped box dims vs the physical size of the product(s) inside the basket; isolate parcels on freight only because of packaging.

## Scope (locked, confirmed in data)
- Carrier `DB SCHENKER`; origin `production_site = 'PCS PL'`; vertical `source_system IN ('Picturator','PicaAPI')`.
- Period May 2026 MTD (2026-05-01 .. 2026-05-28). Anchor reproduced exactly: **1,780 shipments, 9,728 items, 1,760 box-over-120 (98.9%)**, 0 missing box dims.

## Feasibility finding (headline-adjacent)
Product physical dimensions are **not stored anywhere reachable** — `dw.dim_products` carries category/subcategory/shipping_format but **no cm**. The only product size signal is **encoded in the SKU**: 3-letter prefix + two 3-digit groups = printed panel width x height in cm (e.g. `CVS0800601F2` = canvas 80x60). 99.6% of items (9,690/9,728) parse. Third axis (depth) assumed: 8cm canvas/framed/metal, 5cm flat prints (matches observed box heights ~7-9cm). **Off the gold contract** — SKU-parse + depth assumption, not a curated field.

## Method
- Product min footprint per parcel: single-item = product bounding box; multi-item = max-of-each-axis across items (nesting lower bound) PLUS a total-volume gate (sum item w*h*d*qty <= 432,000 cm3 = 120x60x60 parcel envelope) to split out high-quantity baskets that need the big box for *count*, not packaging.
- Parcel-fit (UPS): product <= 120cm every dim AND length+girth (long + 2*(mid+depth)) <= 325cm.

## Result (reconciles to 1,780)
- **Genuinely oversize** (product itself > 120cm): **718** (40.8%)
- **Packaging-driven** (small product, fits parcel by dim AND volume): **926** (52.6%) <- the number wanted
- **Oversize by quantity/volume** (many items need the big box): **103** (5.9%)
- **Box already within parcel range:** 20 · **Unclassifiable** (size not in SKU): 13
- 718+926+103+13 = 1,760 box-over-120; +20 = 1,780. Tie holds.

Packaging waste concentrates in **canvas** (768 of pre-volume-gate 1,029, ~75%; avg longest-box-vs-product gap ~53cm). Non-canvas flat prints (aluminium/acrylic/framed) have larger gaps (~90cm) — flat art in long freight cartons. Zero parcels fail the girth test, so the 120cm dim limit is the binding constraint.

## Checks
- Anchor reproduced (1,780 / 9,728 / 1,760).
- SKU-parse sanity-checked vs box on 20 single-item rows: box ~3-5cm > product on each printed axis -> parse reliable; large canvases (150-180cm) are genuinely big.
- Caught & corrected a heuristic flaw: max-of-each-axis understated high-count multi-item baskets (280 small canvases "fit" one canvas's box). Added the total-volume gate -> moved 103 from packaging-driven to quantity-driven. Corrected number 926 (was 1,029).
- All four classes reconcile to 1,780.

## Deliverables (outside brain)
- SQL: `shipping-agent/workbench/investigations/db-schenker-pcs-pl-box-vs-product/sql/20260528-01_box-vs-product-classification.sql`
- Data: `.../data/20260528-01_classification-summary.csv`, `.../data/20260528-02_packaging-driven-by-category.csv`
- Chart: `.../outputs/20260528-101408--packaging-driven-oversize-freight-by-product-type-poland-site-db-schenker-may-2026.html`

## Open / for principal
- Product dims live only in the SKU + a depth assumption -> off-contract. If this number gets used for a carrier-swap saving, gate it on the real UPS rate card + a per-canvas depth check, and re-run the standard savings falsification gate. The 926 is a *physical-fit* candidate count, not a sized saving.
- By-category CSV sums to 1,029 (pre-volume-gate); corrected total is 926. Noted in chart description.

---

## Follow-on run (2026-05-28) — full ranked basket-signature list of the 926

**Ask:** see ALL 926 packaging-driven baskets, grouped by basket signature (product composition of the parcel) and ranked by parcel count desc -- the list of baskets to consider switching off freight.

**Method:** reused the -01 classification verbatim (SKU parse + depth assumption + volume gate). Reproduced 926 exactly first. Pulled item-level rows for the 926 (window-function form -- LISTAGG and deep re-join CTEs were rejected by the read-only MCP path, so signatures are built in Python). Signature = sorted, duplicate-collapsed product composition, e.g. `1x canvas 120x80cm`, `5x canvas 75x50cm`, `1x canvas 120x90cm + 1x canvas 80x60cm`. Category labels confirmed against `dw.dim_products` (Wall Deco subcats) so no raw SKU codes leak.

**Result:**
- **699 distinct basket signatures** across the 926 parcels. Per-signature counts sum to exactly **926** (verified, assert in script).
- Extremely fragmented: **619 of 699 (89%) are singletons** (one parcel each); only 80 signatures have >=2 parcels.
- Concentration low: top 5 = 8.2%, top 10 = 12.2%, top 20 = 18.1% of 926. No dominant basket.
- Biggest single basket: **`1x canvas 120x80cm` = 36 parcels** (one ~120cm canvas alone in a ~135cm carton). Next: `1x aluminium print 120x90cm` = 13. Canvas dominates the head of the list.
- Every signature's product longest dim <= 120cm (confirms all are genuine parcel candidates).

**Checks:** 926 anchor reproduced before grouping; per-signature counts sum to 926; max product longest dim = 120; CSV = 699 rows, cumulative reaches 100%.

**Deliverables (outside brain):**
- SQL: `.../sql/20260528-03_packaging-driven-basket-signatures.sql`
- Script: `.../notebooks/build_basket_signatures.py`
- CSV (all 699): `.../data/20260528-03_packaging-driven-basket-signatures.csv`

**Open:** the long tail means there's no "switch off these N baskets" shortcut -- the win is structural (right-size the canvas/flat-art cartons), not basket-by-basket. The single biggest lever is the 36 lone-120cm-canvas parcels + the canvas head generally. Still off-contract (SKU dims), so any saving needs the rate-card + depth gate noted above.

# Mart pull: CUSTOM_OVERSIZED 2026 shipment count by carrier

**Context:** Continuation of EU tender DB Schenker reroute work. Same gold mart (`shipping_mart`).
**Player:** Jebrim. **Tier:** gold-contract (`fact_shipments` only).

## Ask
Count CUSTOM_OVERSIZED shipments in 2026 by carrier. Match `LOWER(TRIM(packagetype)) = 'custom_oversized'`
(packagetype, not packagetype_group). Pick the best-covered date column for the 2026 scope; state basis + coverage.

## Turn log
- Profiled date coverage on the oversized slice (73,357 rows total):
  - received_by_carrier_date: 64,817 (88.4%) — ship/dispatch basis
  - shop_order_created_date: 73,357 (100%) — order basis
  - order_produced_date: 73,350 (~100%) — produced basis
  - delivered_by_carrier_date: 61,690 (84.1%)
  - NOTE: unlike the prior PCS-only oversized pull (received_by_carrier_date null), on the
    full carrier population received_by_carrier_date IS well-covered. The null was PCS-specific.
- Scoped on received_by_carrier_date (ship basis — closest to a real shipment year for lane work).
- 2026 ship-date total = 13,509. Order-basis 2026 = 13,550 (diff 41, immaterial).
- Coverage caveat: 8,540 of 73,357 (11.6%) have NULL received_by_carrier_date → excluded by ship-year filter.
  Of those, 1,151 have a 2026 order date, so order-basis would add ~1,151 to 2026.

## Result (2026, received_by_carrier_date / ship basis)
| Carrier        | 2026 count |
|----------------|-----------:|
| UPS            | 6,949 |
| DB Schenker    | 5,912 |
| DPD UK         | 524 |
| Yodel          | 89 |
| DHL            | 33 |
| DPD Poland     | 2 |
| **Total**      | **13,509** |

## Checks
- Carrier breakdown sums to 13,509 = year cross-tab 2026-received total. Reconciles exactly; no null-carrier rows in scope.
- Cross-tab confirmed ship-vs-order basis divergence is small for 2026 (13,509 vs 13,550).

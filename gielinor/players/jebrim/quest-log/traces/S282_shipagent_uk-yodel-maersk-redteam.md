# Trace — shipping-agent red-team: UK Yodel/Maersk negotiation validation

Date: 2026-06-19 | Player: Jebrim | Tier: gold-contract (all five queries on-contract; fact_truck_charges lives in shipping_mart, not silver)

## Ask
Independently re-derive every committed figure in the UK Yodel/Maersk negotiation analysis from the live gold mart; falsify each. Scope: shipping_mart.fact_shipments, destination_country_code='GB', shop_order_created_date in Q1 2026 (Jan-Mar), cost_source='invoice', source_system IN ('Picturator','PicaAPI'). Cost basis: real_shipping_cost_eur / 1.1515 -> GBP. Truck baked into _eur (= cost_summary.truck_charges_eur).

## Turn-by-turn
- Loaded how_to.md + CLAUDE.local.md (full-access tcg_nfe). Confirmed cost_summary has truck_charges_eur + all buckets.
- fact_shipments has NO carrier/carrier_name; carrier handle = shipping_provider_group. fact_truck_charges IS gold (shipping_mart).
- Q1 totals: PASS. 98,911 all / 98,274 dims (committed 98,909/98,272, +2). total_eur 588,306 (committed 588,297). truck_eur 210,707 (committed 210,703). extruck 377,599. Buckets all within euros of committed.
- Basis proof: real_shipping_cost_eur EXACTLY = sum of all buckets incl truck (spot-check 5 rows, to 4dp). Truck baked in CONFIRMED.
- Mixed-currency corruption: SUM(_local)=268,519 vs SUM(_eur)/1.1515=510,904 -> ~1.9x divergence. Per-carrier eur/local ratio varies (DPD 1.86, Maersk 2.34, UPS local~=0/null). _local UNUSABLE as single-currency total. CONFIRMED.
- Q2 split: PASS. Full-book mainland 94,091 (94,089), NI/BT 1,560, OOA 3,209, CI 51 - all match. Dims mainland 93,482 (93,480), dims offshore 4,792 exact. INT-vs-BIGINT: max digit-run=5 chars, 0 runs>=10; INT count = BIGINT count = 3,209 identical. Overflow risk does NOT materialize on this book; BIGINT defensive but immaterial.
- Q3 KEY SETTLEMENT: mainland ex-truck parcel actual = GBP 288,061 vs committed 288,058 -> PASS to GBP 3. "Existing GBP 288,058" IS the RAW INVOICED ACTUAL, not a reprice. Mainland incl-truck 463,949; mainland truck 175,888 (committed 175,884). Carrier mix mainland: DPD UK 45,567 / MAERSK 31,457 / YODEL 12,198 / UPS 4,258.
- Q4 engine mirror: PASS. Small 27,331 / Medium 20,014 / Large 43,698 / OOG 2,439 (committed 27,331/20,013/43,697/2,439). Base total 272,504 (committed 272,498, +6). OOG 2,050@15 + 389@50 = 50,200 exact. Parcel total = base*1.10 + OOG = 349,955 (committed 349,948, +7). Mainland has 0 OOA + 0 BT by construction -> no remote line. CONFIRMED.
- Q5 TRUCK - divergence found. Physical Q1 'UK DHL Freight' loads = 60 (committed "~47.5"). 60 x EUR 3,700 = EUR 222,000 = GBP 192,792 raw, allocated to 93,367 parcels. Committed 47.5 = GBP 175,884 / 3,700 = back-derived from MAINLAND-ALLOCATED truck spend, not physical count. Gap (192,792 raw vs 175,888 mainland) = offshore+no-dims truck share (~GBP 16,904 ~= 4.6 trucks). Current rate CONFIRMED: EUR 3,700 flat Jan-Mar, dropped to EUR 3,620 from April (May/Jun flat 3,620). So 3,700 is STALE; go-forward stay-rate should be 3,620.
- BASIS FLAG: cost_per_truck_eur stores 3,700 as a EUR value (3,700/1.1515 = GBP 3,213). Committed analysis treats GBP 3,700 as the per-truck rate. Either contract is genuinely EUR 3,700 (committed currency mislabel) or rate is GBP 3,700 stored unconverted in the _eur column. Real ambiguity - needs principal/source confirmation.

## Headline
Q1-Q4 PASS (all within rounding). Q5: current rate 3,620 not 3,700 CONFIRMED; "47.5 trucks" is an allocation artifact not a physical count (physical = 60); per-truck-rate currency basis ambiguous (EUR vs GBP 3,700).

## Deliverable
chat-only (read-only validation; no files written outside this trace per brief).

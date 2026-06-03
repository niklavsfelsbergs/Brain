# Shipping-agent: MerchOne blank-destination upstream source trace

**Spawned by:** Jebrim (principal), Niklavs-authorized off-gold reach.
**Tier:** upstream (off the gold contract) — maintainer profile `CLAUDE.local.md` present, connection user `tcg_nfe`, schemas `enterprise_bronze`/`enterprise_silver` in scope.
**Question:** 867 MerchOne packages (24 Apr 2026 onward) have blank destination_country + whole ship-to block in gold. Is the ship-to (a) genuinely missing in the picaapi source, or (b) present upstream and dropped in the pipeline into gold? Then compare vs poc_landing copy of picaapi.

## Status (turn-by-turn)
- Read how_to.md in full + CLAUDE.local.md (maintainer overlay) + sources.md + mart-contract.md. Join key gold->source = (trackingnumber, shop_ordernumber); shipment_id = STRTOL(LEFT(MD5(COALESCE(trackingnumber,'')||'|'||shop_ordernumber),15),16)::BIGINT. MerchOne source = enterprise_bronze.picaapi_*.
- Gold reconcile: 867 distinct PicaAPI blank-dest shipments, 24 Apr-1 Jun 2026; entire ship-to block NULL (0 cc/zip/region/addr). 849 real-tracking, 18 synthetic. Matches prior finding exactly.
- Join proven on GOOD rows: gold trackingnumber -> picaapi_shipments.tracking_number -> picaapi_orders (id), increment_id == shop_ordernumber 300/300; ship address + country ISO present 300/300. Address filter = addressable_type ILIKE '%OrderModel%' AND type='shipping'.
- Bronze trace of 849 blanks via that filter: 849/849 matched order, 0 ship address, 0 country -> APPEARED missing. BUT direct addressable_id join (no type filter) returned address rows.
- ROOT REFINED: bronze DOES hold shipping-address rows for these orders but DEGRADED -- addressable_type=NULL (so the OrderModel filter drops them), postcode/city/street ALL blank (0/684), only country_id + firstname populated. Billing rows intact w/ postcodes. country_id resolves to valid ISO 684/684.
- poc_landing has full picaapi copy incl picaapi_addresses (14.5M rows vs bronze 9.6M). Same 849 joined on increment_id: 849/849 matched, 827/827 distinct orders carry COMPLETE shipping addr (real postcode/city/street), 849/849 country ISO. Sample recovered: US/DE real addresses, addr created_at = 24 Apr (= regression start).
- bronze dp_updated_at current (2026-06-02) -- not stale; row-level/field-level gap, not a frozen feed.

## CONCLUSION
(a) NOT missing at origin: poc_landing carries the complete ship-to. (b) Bronze (the gold-feeding copy) received a DEGRADED address: country_id+name only, addressable_type NULL, address detail blank. (c) Two losses stack: source->bronze feed degraded the record; gold build then drops it because its address join keys on addressable_type (NULL here) -- so even the country_id bronze had never reaches gold. Data lost at the source->bronze feed (primary), compounded by a gold-build join that can't pick up a partial/untyped address row. (d) Owner: bronze picaapi ingestion (the picaapi_addresses feed into enterprise_bronze) -- why does it write addressable_type NULL + blank detail when poc has the full row. Secondary: gold build address-join hardening (fall back to country_id when addressable_type NULL).

## Example query (verified-runnable, 2026-06-02)
- Built + ran live a single side-by-side contrast query for example order PPO00194188 (order_id 4726122): UNION ALL of poc_landing vs enterprise_bronze picaapi_addresses, join addressable_id=picaapi_orders.id AND type='shipping', source-labeled. Returned 2 rows -- poc full (40 FAIRVIEW AVE / GROUND LEVEL / 07304-2606 / JERSEY CITY / addressable_type=...OrderModel / country 840), bronze degraded (street/postcode/city/addressable_type all NULL, only country_id 840). Schemas confirmed via get_object_details; bronze side joins addressable_id directly (no addressable_type filter, since it's NULL). Handed the exact SQL + result rows back to Jebrim for the writeup.

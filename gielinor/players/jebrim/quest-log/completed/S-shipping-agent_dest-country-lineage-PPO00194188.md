# Shipping-agent pull — where destination_country is lost (order PPO00194188 / order_id 4726122)

**Role:** shipping-agent (emulation) · **Player in scope:** Jebrim · **Date:** 2026-06-02 · **Tier:** UPSTREAM (off-gold, maintainer profile `tcg_nfe` authorized)

## Ask
Contradiction: bronze `picaapi_addresses` still has `country_id=840` (US) for address 14185594 (only lost street/zip/city + `addressable_type` which is NULL in bronze), yet gold `shipping_mart` shows the package with BLANK destination_country. Where between bronze and gold is the country lost, and why?

## Hop-by-hop (order_id 4726122 / address 14185594)
- bronze.picaapi_addresses: country_id 840 PRESENT, type='shipping' PRESENT, addressable_type=NULL, all detail (city/postcode/firstname/region) NULL.
- silver.picaapi_addresses: country_id 840 PRESENT, type='shipping'. (table has NO addressable_type column at all.)
- silver.order_addresses (assembly gold reads): ship_country_id 840 PRESENT, is_present=NULL, ship_city/zip NULL.
- gold.fact_shipments: destination_country NULL, AND zip/region/forename/surname/address all NULL. order/source IDs present (shipment found).

## Finding — the leading hypothesis is REFUTED
Country_id 840 is NOT lost bronze→silver. It survives all the way into silver `order_addresses`. The drop is at the **silver→gold hop**.
- Mechanism (CONFIRMED by cross-tab over ~1.96M PicaAPI rows): gold populates destination_country iff silver `order_addresses.is_present IS NOT NULL`. is_present=True → 100% present (1,951,898); is_present=False → 100% present (8,110); **is_present=NULL → 0% present (703 rows, all NULL in gold)** despite ship_country_id being present. PPO00194188 is in the is_present=NULL bucket.
- Root cause chain (PAPER on the transform code, CONFIRMED on the table states): bronze addressable_type=NULL → silver order_addresses cannot resolve the address as "present" (is_present=NULL) → gold's address-assembly step gates ALL address fields (country included) on a resolved/present address, so it carries nothing.
- Country lookup is NOT a factor: id 840 resolves cleanly to US in picaapi_countries; the row is simply absent before resolution.

## Confirmed vs PAPER
- CONFIRMED (queried each table for this key + the 1.96M cross-tab): the hop is silver→gold; the discriminator is order_addresses.is_present NULL.
- PAPER (bi-etl code outside perimeter): that the gold step literally JOINs/filters on is_present / a resolved-address flag. Observed behavior is a perfect 0%/100% split, but the exact predicate is inferred.

## Fix implication
Fixing bronze's addressable_type alone is NECESSARY but likely NOT SUFFICIENT for a one-shot backfill: re-tagging would let silver set is_present and let the country flow on the next full rebuild. But the silver→gold step also drops the country for is_present=NULL even though ship_country_id is sitting right there — so hardening gold to carry country_id whenever order_addresses has it (independent of is_present) would recover all 703 rows immediately without waiting on a bronze re-ingest.

## Deliverable
- Chat-only (findings to principal). No chart requested.

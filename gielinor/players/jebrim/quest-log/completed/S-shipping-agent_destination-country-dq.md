# Shipping-agent pull — missing destination_country DQ investigation

**Spawned by:** Jebrim (principal) · **Date:** 2026-06-02
**Agent:** shipping-agent (in-session emulation) · **Tier:** gold-contract (`shipping_mart.*`, read-only via Redshift MCP)
**Ask:** Niklavs reports missing `destination_country` for some shipments. Determine whether the missingness is a specific cut or spread evenly; characterize it.

## Turn-by-turn
- Loaded how_to.md §0 + reference/{mart-contract,tables}.md. CLAUDE.local.md present (grants upstream) but stayed on gold — this is a gold DQ question.
- Contract grounding: `destination_country` (63 distinct) + sibling `destination_country_code` (60 distinct) both on fact_shipments. §4: ORWO destination_country now fully populated (0% blank). "Missing" per contract = NULL (checked '' / whitespace too).
- Baseline: 867 missing / 18,205,453 rows = **0.0048%**. All true NULL — zero empty-string, zero whitespace.
- Sibling cross-tab: in ALL 867 cases destination_country_code is ALSO missing → **not a derivation gap**, geography genuinely absent.
- Dimensional breakdown: 100% of nulls on **source_system = PicaAPI (MerchOne)**; 0 on every other source. Carriers/sites spread (ONTRAC/USPS/PCS CMH highest rates) but all roll up under MerchOne.
- Time: zero missing before April 2026. Apr 2026 = 1.17% of MerchOne (750), May = 0.13% (100), early Jun = 0.66% (17). Recent regression, largely subsided. Sharp start **2026-04-24**.
- Affected rows fully complete otherwise: 89% invoiced, 97% have ship date, revenue present, real tracking — NOT undispatched/cancelled/label-only. Entire ship-to block empty (no country, code, zip, region, address). 45 MerchOne shops, US/cross-border lean (Lyto US Store top at 205).

## Headline result
Missingness is **sharply concentrated, not spread evenly**: a recent regression on **MerchOne** only, beginning **2026-04-24**. 867 rows = 0.0048% mart-wide. Not a derivation gap — full ship-to address is absent upstream on otherwise-complete, real-money shipments. Tapering since April peak.

## Caveats
- `destination_country` is nullable (no NOT NULL guarantee); no documented upstream reason in known-dq.md — this is a new, undocumented regression.
- Sibling-field hypothesis tested and rejected: country_code does not survive when country is null.
- Cause attribution (why the MerchOne ship-to block dropped from 2026-04-24) is a guess — would need the upstream MerchOne feed (enterprise_bronze.picaapi_*, off the gold contract) to confirm. Flagged as follow-up, not chased per brief scope.

## Open / needs principal
- Rulebook gap: no entry in `reference/known-dq.md` for this MerchOne destination_country regression. Maintainer (principal) may want to add a dated stamp.

Deliverable: chat-only (findings summary returned to principal). No chart warranted.

---

## Follow-up pull — pinpoint the first-bad table in lineage (2026-06-02, upstream)

**Tier:** UPSTREAM / off-gold — maintainer profile (`tcg_nfe`, `CLAUDE.local.md` grants `enterprise_*`, `poc_landing`). Flagged off-contract.
**Ask:** name the SINGLE first table in lineage where the MerchOne ship-to address goes missing/degraded; contrast with the last-good table upstream; re-confirm the poc_landing good-copy table.

### Turn-by-turn
- Re-confirmed gold population: 867 pkgs / 845 distinct orders, blank destination_country, source PicaAPI, from 2026-04-24. Matches prior trace.
- Mapped the address lineage: 3 layers carry `picaapi_addresses` — `poc_landing` (rawest landing, 29 cols incl. full address) → `enterprise_bronze` (14 cols, still has city/postcode/street/country/type/addressable_type) → `enterprise_silver` (only 6 cols — street/zip/city columns DON'T EXIST). Silver assembly table = `enterprise_silver.order_addresses` (ship_street/city/zipcode/country_id + is_present flag) — what gold joins.
- Order shipping address keyed: `picaapi_addresses.addressable_id = picaapi_orders.id`, `addressable_type='...OrderModel'`, `type='shipping'`; order# = `picaapi_orders.increment_id`.
- silver.order_addresses for the 845 keys: 788 rows, all 788 blank ship_zip/street/city, 683 blank bill_zip too → silver degraded.
- bronze.picaapi_addresses for the 845 keys: 684 shipping rows, ALL 684 blank zip/street/city, country_id intact (0 blank), ALL 684 addressable_type=NULL (missing type tag). Exact 684/684 from prior trace. → bronze ALREADY degraded.
- poc_landing.picaapi_addresses for the 845 keys: 845 rows, ZERO blank zip/street/city/country, ZERO null addressable_type. created_at 2026-04-24 → 2026-06-01 (matches regression start). → poc GOOD.
- Row-level ground-truth (PPO00194188, order_id 4726122): poc = postcode 07304-2606 / JERSEY CITY / 40 FAIRVIEW AVE / country 840, addressable_type=OrderModel. bronze = same order_id, postcode/city/street all NULL, addressable_type NULL, but country_id 840 + name (Johnnie Rivera) retained.
- Row drop too: all 845 orders reach bronze.picaapi_orders (header survives), but only 684 have a shipping-addr row (degraded); 161 have NO shipping-addr row. 684+161=845, reconciles.

### Headline
- **Last-good table:** `poc_landing.picaapi_addresses` — full ship-to (street/zip/city/country) + type tag intact, all 845 orders, 0 degraded.
- **First-bad table:** `enterprise_bronze.picaapi_addresses` — the bronze ingest of the MerchOne address feed is where it breaks: 684 rows degraded (street/zip/city NULL, addressable_type NULL), 161 rows dropped entirely. The raw landing (poc_landing) is COMPLETE; degradation happens at the poc_landing→enterprise_bronze hop, NOT at the raw landing and NOT at silver (silver inherits the broken bronze + structurally drops the address columns).
- **Backfill source (confirmed):** `poc_landing.picaapi_addresses`, joined `addressable_id = poc_landing.picaapi_orders.id`, `type='shipping'`, order# = `picaapi_orders.increment_id`. 845/845 complete.

### Checks
- Boundary unambiguous: poc 0/845 degraded vs bronze 684/684 degraded on the SAME order_ids. Row-level value contrast confirmed.
- Counts reconcile: 684 degraded + 161 dropped = 845 = gold distinct orders.
- poc created_at window (24 Apr–1 Jun) matches the regression start exactly.

### Open / needs principal
- The defect is in the **poc_landing → enterprise_bronze ingest of picaapi_addresses** (`bi-etl` enterprise_bronze DAG for the MerchOne address feed) — likely an address-type filter/join that drops rows whose `addressable_type` is null and nulls the detail. Fix or backfill belongs there; gold rebuild follows.
- Off-gold figures — do not reconcile against a gold number; raw vocabulary used deliberately.

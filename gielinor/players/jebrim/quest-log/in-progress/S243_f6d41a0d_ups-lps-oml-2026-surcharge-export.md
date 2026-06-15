# UPS LPS/OML 2026 surcharged-shipment export (shipping-agent sub-agent trace)

Player: Jebrim. Spawned as the shipping-mart sub-agent for a data export. Continues the S199 UPS OML/LPS surcharge-predictor investigation (reused its probe joins).

## Ask
2026 UPS surcharged shipments (LPS + OML family), one row per surcharged shipment, to parquet.
Columns: trackingnumber, pcs_ordernumber, order_date, our_dims (detailkeyeddim),
ups_invoice_dims (packagedimensions), packagetype, surcharge_amount (net, refund-in-place aware).

## Tier / scope
UPSTREAM — off the gold contract. tcg_nfe maintainer overlay (CLAUDE.local.md grants enterprise_silver / enterprise_bronze).
silver = enterprise_silver.ups_invoices (charge lines, net, transactiondate=date)
bronze = enterprise_bronze.csv_ups_zip_invoicedata (packagedimensions + detailkeyeddim; ~3-mo zip retention)
gold   = shipping_mart.fact_shipments (pcs ordernumber, shop order date, packagetype).
Read-only throughout.

## Charge codes included
LPS, OVR, OML, SLP (demand LPS), SOV (demand over-max). Excluded residential/AHS demand: PSC/PSR/SAH.

## Window
Calendar 2026 by silver transactiondate, literal bounds '2026-01-01' .. '2027-01-01' (no DATEADD/CURRENT_DATE).

## Status (turn-by-turn)
- Verified bronze dims-coverage window LIVE: invoice dates 2026-03-11 .. 2026-06-10 (wider than S199's 06-03 view). Jan/Feb dims NULL by design.
- Silver family landscape 2026: LPS/OVR/OML/SOV span full year; SLP only Jan 2-21 (demand surcharge expired). 1,701 distinct surcharged trackings.
- Grain: 440/1,701 trackings carry >1 code -> aggregated to one row per tracking. Net = SUM(netamounteur); gross/reversed split carried + LISTAGG code list.
- Gold join integrity: 10 trackings multi-match to fact -> deduped via ROW_NUMBER (latest order) so row_count == distinct_trackings == 1701, no fan-out. 8 unmatched to gold kept (LEFT JOIN, gold cols NULL), not dropped.
- Reconciliation: net 307,697.80 = gross 418,978.90 + reversed -111,281.10; ties to per-code sum (LPS 144,657.80 + SOV 72,200 + OVR 58,394.70 + OML 17,468.50 + SLP 14,976.80).
- ups_invoice_dims populated 666 / 1701; by month Jan 0, Feb 1, Mar 203, Apr 209, May 214, Jun 39.
- our_dims (detailkeyeddim) populated only 663 — SAME bronze-retention field, so Jan/Feb also NULL there (flagged: brief expected our_dims fully populated; the keyed-dims source is retention-limited too).

## Deliverable (v1 — bronze-only our_dims)
Parquet: shipping-agent/scratchpad/20260615-01_ups-lps-oml-surcharged-2026.parquet (1,701 rows). [PRESERVED]
SQL: shipping-agent/scratchpad/sql/20260615-01_ups-lps-oml-surcharged-2026-export.sql
Export script: shipping-agent/scratchpad/20260615-01_export_ups_lps_oml_2026.py

## v2 revision (2026-06-15) — our_dims backfilled from GOLD for full-year coverage
Principal chose "backfill from gold." Done: gold fact_shipments length/width/height_cm (passthrough-verified S199)
joined on trackingnumber, deduped to one fact row per tracking (latest order, same as before), formatted "LxWxH cm".
- New parquet: shipping-agent/scratchpad/20260615-01_ups-lps-oml-surcharged-2026-v2.parquet (1,701 rows).
- SQL + export script updated in place (v1 parquet kept; v2 = new filename, no clobber).
- Coverage: our_dims_gold = 1,691 / 1,701. Gold matches 1,693 trackings; 2 carry non-physical sentinel dims
  (<=0.1 cm — impossible on oversize parcels) so their formatted string is left NULL (raw numerics still carried).
  8 trackings unmatched to gold (expected). Jan 386/389, Feb 244/245 now filled (were 0 / 1 from bronze).
- Bronze keyed string KEPT as our_dims_bronze (663 populated, retention-limited) — no data loss. ups_invoice_dims
  unchanged at 666. Both retention-limited fields untouched.
- Invariants re-verified independently off the parquet: rows 1,701; net total EUR 307,697.80; no fan-out
  (distinct trackings == row count == 1,701).
- New columns: our_dims_gold, our_length_cm, our_width_cm, our_height_cm, has_our_dims_gold. Renamed prior
  our_dims -> our_dims_bronze for clarity (gold is now the primary declared-dims column).

## v3 revision (2026-06-15, sid8 f6d41a0d) — drop bronze col + component-split UPS dims
Principal: "remove that column [our_dims_bronze] and add a split for ups invoice dims by component like gold."
Done as a post-hoc polars transform on the v2 parquet (pure dataframe op, no DB re-query):
- DROPPED our_dims_bronze (gold supersedes it; principal confirmed gold is the upgrade earlier this session).
- ADDED ups_length_cm / ups_width_cm / ups_height_cm parsed from ups_invoice_dims ("L x W x H", whitespace-padded,
  descending), placed right after ups_invoice_dims — mirrors the gold our_length/width/height_cm split.
- New files: shipping-agent/scratchpad/20260615-01_ups-lps-oml-surcharged-2026-v3.parquet + .csv (1,701 rows, 24 cols).
  v1/v2 preserved (no clobber).
- Invariants re-verified off the parquet: rows 1,701; net EUR 307,697.80; ups dims 666 (component split = 666, zero
  parse failures); our_dims_gold 1,691. Both axes now per-component comparable (our_length_cm vs ups_length_cm etc.).
- CSV deliverable written (principal asked for CSV).

## Pending external actions
No pending external actions. (Export shipped to principal as parquet + CSV in the shipping-agent repo; nothing sent externally.)

## Open / for principal
- **Export script/SQL still produce the v2 shape** (bronze col present, no UPS component split). The v3 transform was
  applied post-hoc on the file. Offered to fold drop+split into the generator so a re-run reproduces v3 directly;
  principal cued "wrap up" instead of answering → carried as the open dep. Files: scratchpad/sql/...-export.sql +
  scratchpad/20260615-01_export_ups_lps_oml_2026.py.
- 2 surcharged rows carry sentinel gold dims (<=0.1 cm) instead of real declared dims — left NULL in the string,
  not faked. Worth a glance if exact dims on those 2 trackings matter; otherwise expected DQ on a tiny slice.
- The bronze keyed string (now dropped from v3) and gold can be cross-checked in v2 where both exist:
  gold is the precise PCS-declared value, bronze is UPS's rounded keyed echo (e.g. gold 120.5x90.5x5 vs bronze
  "121.0x 91.0x 5.0"). Passthrough holds; gold is the more precise source.

## Cascade
Cascade: none — data export, no canonical docs / per-carrier status tables affected.

## Main-brain changes
- Quest-log trace (this file): S243_f6d41a0d_ups-lps-oml-2026-surcharge-export.md
- inventory/ups-lps-oml-2026-export-resume__f6d41a0d.md (resume state)
- examine/drafts/2026-06-15-verify-each-fields-source-table-before-promising-coverage.md (harvest, Q5 correction)
- Export artifacts live OUTSIDE the brain (shipping-agent repo scratchpad) — not part of this commit.

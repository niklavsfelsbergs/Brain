# S366 (sid8 422d59ed) — ORWO FKBRING/CIRRO: identify + mark excluded

**Player:** Jebrim. **Date:** 2026-06-25. **Status:** complete (shipped + committed).
**Arc:** continues the ORWO Tender 2026 (parent [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain]]; corrects handover resume `orwo-tender-resume__cb17c25e`).

## Ask
Investigate ORWO shipments on carriers **FKBRING** and **CIRRO** — what are they, are they tied to a specific `keyaccountid`? Redshift first, PTS only if needed.

## What was found
Gold `shipping_mart.fact_shipments` profiling + raw `enterprise_bronze.orwo_pts_parcelfinish` (`carrierid` × `senderkeyaccountid`, parcel grain):

| Carrier (extkey) | Carrier | Key account (`senderkeyaccountid`) | Dest | Parcels |
|---|---|---|---|---|
| FKBRING + FKBRINGPARCEL | Bring (Posten Norge) | **fotoknudsen** | Norway | ~82.5k |
| CIRRO | cross-border consolidator | **onskefoto** (Önskefoto) | Sweden | ~73.7k |

Each carrier is a **dedicated single-key-account Nordic brand lane**. Tiny residue (~380 parcels) under `senderkeyaccountid='ORWO'`, null country — unmapped/internal.

The gold mart has no `keyaccountid`; it lives in raw ORWO/PTS tables. `orwo_pts_parcelfinish` is the one table carrying both `carrierid` and `senderkeyaccountid` at parcel grain — answered fully from Redshift, no PTS connection needed.

## Decision (principal)
**TCG does not pay the shipping for these key accounts — they are already excluded from the tender.** Their 0% invoice coverage in the mart is *correct* (no TCG invoice because TCG isn't billed), not an uninvoiced-cost gap to model. This **corrects** the earlier framing that lumped FKBRING (78.8k) + CIRRO (69.8k) into the ~600k "uninvoiced layer to price." The TCG-paid layer still needing a basis is everything else — POST_DVF/Deutsche Post the real one.

## Pending external actions
None pending.

## Writes
- NFE `projects/7_ORWO_tender_2026/_scope.md` — 2026-06-25 EXCLUSION block. **Committed** bi-analytics-main `e662fca` (not pushed).
- Brain resume `orwo-tender-resume__cb17c25e.md` — correction banner so next ORWO session drops them from the uninvoiced-layer table.
- Bank draft `bank/drafts/notes/projects/2026-06-25-orwo-keyaccount-carrier-exclusion.md`.

## Cascade.
None — ORWO-tender-local scope correction; no SCM/mart/EU-tender artifact affected.

## Main-brain changes.
Quest-log entry + resume correction + one bank draft (this brain repo). NFE doc change committed in bi-analytics-main.

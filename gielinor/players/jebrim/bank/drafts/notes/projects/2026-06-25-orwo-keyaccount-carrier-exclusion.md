# ORWO: FKBRING/CIRRO are key-account lanes TCG doesn't pay for (tender-excluded)

**Source:** [[S366_422d59ed_orwo-fkbring-cirro-exclusion|S366]] (sid8 422d59ed), 2026-06-25. Live Redshift, READ-ONLY.

## Claim
In the ORWO/Wolfen book, two of the 0%-invoice-coverage carriers are **excluded from the tender by ownership**, not gaps to price:

- **FKBRING / FKBRINGPARCEL** = Bring (Posten Norge) → key account **`fotoknudsen`** → Norway (~82.5k parcels).
- **CIRRO** = cross-border consolidator → key account **`onskefoto`** (Önskefoto) → Sweden (~73.7k parcels).

TCG does not pay the shipping for these key accounts (the brand carries its own carrier cost), so there is no TCG invoice — the mart's 0% invoice coverage is correct, not missing data.

## How to verify
`enterprise_bronze.orwo_pts_parcelfinish` is the only raw table carrying both `carrierid` and `senderkeyaccountid` at parcel grain (`keyaccountid` is absent from the gold mart). Group `carrierid × senderkeyaccountid × recipientcountrycode`.

## Generalizable lesson
A carrier with **0% invoice coverage** is not automatically an *uninvoiced-cost gap to model*. First check **ownership**: a dedicated single-key-account lane may be one TCG isn't billed for at all (excluded-by-scope), distinct from a TCG-paid lane whose invoices just haven't been loaded (POST_DVF/Deutsche Post — the real gap). Verify against the key-account field before treating absence-of-invoice as a pricing problem.

## Links
Corrects [[orwo-tender-resume__cb17c25e]] uninvoiced-layer framing. NFE anchor `projects/7_ORWO_tender_2026/_scope.md` (2026-06-25 EXCLUSION block). Parent quest [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain]].

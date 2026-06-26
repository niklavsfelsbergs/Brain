# A proposed pipeline fix off surface provenance is a hypothesis until grain-validated vs ground truth

Draft (2026-06-19, [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]]). Q5 correction-harvest.

**The moment.** I spec'd a one-line bi-etl change — fill ORWO `weight_kg` from `parcelfinish.weight` via `COALESCE` — off a clean-looking provenance picture (parcelfinish has weight ~100%, the mart uses the sparse `usedpackaging.weightg`). Before stating it as the fix I verified against ground truth: the two sources disagreed **~5x** (0.6 vs 3.4 kg), and the carrier invoice gave a **third** value (9 kg). All three were *different grains* — per-order packaging vs per-tracking parcel vs carrier-billed — because ORWO is consolidated (~4.8 shipment_ids/tracking). The COALESCE was invalid (it would stamp a parcel weight onto order rows and ~5x over-count on SUM).

**Not isolated this session.** Two earlier confident claims were also overturned by tracing one level deeper: "dims are all in Redshift, just unwired" (FALSE for the DHL2 stream — a real capture gap) and the "fz/FOTOWELT key breaks the join" theory (red herring — the mart uses a different, numeric key). And a "9–11 kg invoice vs 3.4 kg parcelfinish" alarm dissolved once I stopped averaging at the wrong grain.

**Why it matters.** For "can we recover X / fix the mart" questions, the surface (schema, column names, a single average) is not enough to specify a change or assert recoverability — each surface read this session looked solid and was wrong at depth.

**How to apply.** Before speccing a source swap or claiming recoverability: (1) trace the *actual* pipeline wiring (read the DAG), not the column names; (2) compare candidate sources at **row grain** against a ground truth (the carrier invoice), never on averages alone; (3) treat any disagreeing totals as a grain/consolidation artifact first ([[disagreeing-totals-suspect-grain-mismatch]]); (4) only then write the fix. The verification was cheap and caught every error — do it *before* the recommendation, not after.

Related: [[2026-06-19-orwo-mart-weight-grain-and-consolidation]], the existing grain/measurement reflexes (verify-the-measurement-measures-the-thing, re-validate-borrowed-constants).

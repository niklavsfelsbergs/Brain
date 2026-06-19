# ORWO Tender 2026 - scope & cost basis

Draft (2026-06-19, [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]]). Candidate seed for a new **`orwo-tender`** domain (sibling of [[eu-tender]]). Anchor: NFE `projects/7_ORWO_tender_2026/`.

**What it is.** Extend the carrier tender to **ORWO** (Picturator produced at Wolfen) - the entity explicitly OUT of scope in the Picanova EU tender (project 2). Standalone home `NFE/projects/7_ORWO_tender_2026/`. Focus ORWO; **sendmoments parked** (ships under the ORWO DHL account, may be invoice+offer only, not in PTS).

**Why it's a different shape than the Picanova tender.** ORWO ships **bulk-mail manifests / consolidated parcels** (many order-grain shipment_ids per physical tracking, ~4.79 for UPS) and has poor package-dim coverage. So the Picanova `(carrier,service,country,weight,dim,packagetype)->cost` engine does NOT transfer.

**The reframe (load-bearing).** Across all 5 current carriers (UPS, DHL, Austrian Post, Guell, GLS), **base transport rates are weight x zone(country) x service - dims are NOT needed for the base rate.** So ORWO is repriceable on **weight alone**. Dims only feed oversize-surcharge modeling (a tail; partly readable off invoice surcharge lines + UPS billedweight / DHL vol_wgt).

**Method = reprice at TRACKING (parcel) grain**, not the per-order shipment_id grain: one row per physical parcel, weight = invoice `billedweight` where invoiced (carrier truth) else `parcelfinish.weight` (rounded to the carrier's weight band), against the weight-tier cards. DHL2 Paket on weight alone (no dims, fine - weight-tier priced + 94% invoiced).

**Cost-coverage mosaic.** `invoiced OR has-weight` ~93% of ORWO volume. DHL ~94% invoiced; UPS ~54%; POST ~0.6% invoiced but 97% weight + now a rate card -> modelable.

**Status.** Contracts reviewed -> `contracts_review/` (per-carrier + `_index`). Coverage + invoice + weight/dims grain -> `coverage_and_invoice_profile.md`. Next: build the tracking-grain repricing base (UPS+DHL first).

**Related:** [[eu-tender]] (Picanova sibling; shared re-rating trust-gate method), [[carrier-contracts]] (the ORWO rate cards), [[shipping-mart]] (the weight-grain/consolidation finding), [[2026-06-19-orwo-mart-weight-grain-and-consolidation]], [[2026-06-19-orwo-carrier-contracts-2026]], [[S266_e455d12d_orwo-box-grain-quota-estimator]].

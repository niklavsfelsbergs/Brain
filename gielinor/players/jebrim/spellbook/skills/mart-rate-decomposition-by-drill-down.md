# Mart NULL classification by drill-down

> **Status.** Draft. Pending alching. Authored 2026-05-21 in S019 (Jebrim) as harvest from [[S014_2026-05-21_shipping-data-mart-ttyd-howto|S014]] (Shipping Data Mart TTYD how-to) §9 work.

## When to use

When auditing a column with a non-trivial NULL rate at the aggregate level on a multi-source mart (`fact_*` tables fed by multiple `source_system`s, refreshed across time, partitioned by carrier or other dim group).

The naïve move — single SELECT, single NULL rate — produces a number that blends multiple regimes and lands as a misleading "anomaly" or "DQ issue" when in reality several distinct phenomena are stacked under the aggregate. The skill below is the drill discipline that decomposes the aggregate before classifying.

## The skill — drill-then-classify

For any column with non-trivial aggregate NULL rate:

1. **Decompose by `source_system`.** Group by source, recompute NULL rate per group. If the rate splits, the aggregate was hiding ≥2 regimes — treat each source as its own column going forward.
2. **Decompose by time (within each source).** Bucket by month (or whatever period fits the data refresh cycle). Look for date boundaries where the NULL rate steps. A step = a regime change (ingestion went live, source got rewired, pipeline broke). Treat pre/post as distinct slices.
3. **Decompose by dim group (carrier, production site, country, …).** Within a single source × stable-time window, group by the obvious dim. If a sub-population dominates the NULL rate, you have a per-variant gap, not a column-wide problem.
4. **Decompose to leaf (extkey, sku, leaf identifier).** Last layer. The leaves are where actual ingestion / source-availability decisions live.

**Stop when** (a) the residual NULL rate within the slice is uniform (regime is stable) or (b) the slice is too small to subdivide (<500 rows/month is a good practical floor; one-off appearances are noise).

**Only then bucket-classify each leaf** into one of five:

1. **Will fill.** Defined-intended, not yet populated. Backfill expected.
2. **Deprecated.** Was populated, no longer is.
3. **Bugged.** Should be populated, isn't, root cause unknown.
4. **Empty by design.** Source doesn't carry it. Not a defect.
5. **Undefined / do not use.** Column exists in DDL with no agreed semantics yet.

The classification is per-leaf, not per-column. A single column can carry leaves in multiple buckets simultaneously (e.g., `fact_shipments.received_by_carrier_ts` is bucket-4 for PCS / Rewallution / ORWO, bucket-1 for PicaAPI pre-2025-11 → bucket-clean post, bucket-3 for the specific PICT extkey variants identified).

## The discipline lift

The drill protocol replaces "what bucket does this column live in?" with "what slice am I looking at, and is it small/uniform enough to bucket yet?" The disprove instinct — "if I think I see a pattern at level N, look at level N+1 to try to break it" — is now structural, not a separate maxim to remember.

## Originating observation

[[S014_2026-05-21_shipping-data-mart-ttyd-howto|S014]] §9 work, 2026-05-21. Three sequential probes proved each previous framing wrong:

- **Probe 1** (source × month): showed PCS / Rewallution were silently 100% NULL alongside ORWO (T11 only flagged ORWO), PicaAPI ~78% NULL was a regime-change average (carrier-ts ingestion landed 2025-11), Picturator ~34% NULL was a real degradation starting 2025-09.
- **Probe 2** (source × month × dim group): showed the "PICT degraded Sep 2025" framing was wrong — only DHL and UPS groups degraded, plus a dim-coverage gap and DPD UK delivered-events not wired. All other carriers stayed clean.
- **Probe 3** (extkey): showed "DHL + UPS broke" was wrong — workhorse extkeys (DHLPKT, UPS04STD, etc.) stayed clean throughout; specific new extkey variants (bare DHL, bare UPS, DHLWPINT, DHL54PREMIUM, DHLWPKT, UPSWWE) were never wired for carrier-event ingestion.

Each level overturned the previous classification. The final §9 lands at the right granularity — extkey-level, ETL-actionable — only because the drill continued past the first plausible answer.

## Anti-pattern this skill replaces

Publishing the aggregate as classification ("PICT is 34% NULL — possibly bugged") without decomposition. The bucket assignment looks right at the aggregate level but is wrong at every leaf inside it. Wrong-at-leaf classifications then bake into reference docs and propagate (T11's NULL classification missed PCS + Rewallution because we never split by source before assigning ORWO to bucket 4).

## Related

- §9 of `bi-analytics-main/NFE/projects/3_shipping_data_mart_TTYD/how_to.md` for the classification this skill produced.
- publish-aggregates-only-after-disprove-pass (Jebrim examine draft) — the meta-rule about always running one disprove-pass before publishing.

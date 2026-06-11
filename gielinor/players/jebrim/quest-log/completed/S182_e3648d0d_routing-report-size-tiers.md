# S182 · Routing report — size-class tiers (small / standard / large / oversize)

**Player:** Jebrim · **sid8:** e3648d0d · **2026-06-09**
**Repo touched:** `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/routing_2026q1/` (external — principal-gated, uncommitted)

## What this was

Niklavs asked how oversize/standard is defined in the "What each carrier takes" section of the EU-tender routing report, then evolved it into a richer size taxonomy. Grew the binary `standard|oversize` into **four tiers**, plus UI fixes to the carrier cards.

## The taxonomy (landed)

Classifier in `carrier_envelopes.py` (`sz` expression), most-restrictive first:

- **oversize** — HYBRID: a special-handling packagetype family (`zugeschnittene` / `custom_oversized` / `pallet` / `gel` / `gel versandtasche`, case-normalised) **AND** (physically large `d_max>120 | d_mid>60 | d_min>60`, OR unmeasured `d_max null/<=0`). ~14,729 (2.8%).
- **small** — DHL Kleinpaket box: `≤1 kg AND 35.3×25×8 cm` (sorted sides). ~92,063 (17.3%). Numbers from the live `dhl_paket` engine `constants.py`, not memory.
- **standard** — within DHL standard cuboid `120/60/60`. ~314,191 (59.2%).
- **large** — exceeds 120/60/60 but parcel-servable (was the old "oversize"). ~110,211 (20.7%).

Masses validated against the Q1 actuals population (531,194 parcels).

## Key decisions (with Niklavs)

1. **Oversize is a packagetype thing, not a dimension thing.** Standard packagetypes never touch DB Schenker; the whole DBS book is the special families. The families total 14,827, of which 8,951 (~60%) ride DB Schenker today, the rest ship parcel ("often go DB Schenker" = literally true).
2. **No deeper signal than packagetype available.** Carrier-billed `real_oversize_eur` is a dead end (0.2% of book, mostly disagrees — it measures which carrier billed a surcharge, not physical oversize). Product grain isn't in the shipment-level mart. Decided: packagetype is the best signal; left flat (no gel/pallet/custom sub-split) per Niklavs.
3. **Hybrid refinement (the 24-on-DHL-Paket catch).** Niklavs spotted 24 "oversize" parcels routed to DHL Paket DE and flagged DQ. Investigation: NOT measurement DQ — they're physically tiny (≤22.5 cm, <1 kg) items carrying a `CUSTOM_OVERSIZED`/`GEL` packagetype label. The packagetype gate is a product-class flag, not a size guarantee. Fix = the hybrid AND-physically-large rule above; reclassified 98 packagetype-oversize parcels to small/standard. Real measurement DQ (zero dims) was only 5 parcels.

## UI fixes to the cards

- Per-rule one-line render (`.szr` nowrap span) — was wrapping mid-rule.
- Card width 330→380px min + tighter card-table padding — Parcels column was squished.
- Class order forced to small → standard → large → oversize (`SZ_ORDER`), was alphabetical.
- Light-gray per-class parcel count in parens (`.szn`), summed across each region's destinations (reconciles to the region total).

## Files changed (bi-analytics-main, UNCOMMITTED — principal-gated)

- `routing_2026q1/build_final.py` — `packagetype` now flows into `routing_assignment.parquet`.
- `routing_2026q1/carrier_envelopes.py` — 4-tier hybrid `sz` classifier + per-rule counts + `SZ_ORDER`.
- `routing_2026q1/routing_report.py` — `.cls-small/.cls-large/.szr/.szn` styling, legend prose, card width.
- regenerated: `routing_assignment.parquet`, `envelopes.json`, `routing_report.html`, `routing_stats.json`.

## Pending external actions

None pending. (The bi-analytics-main commit is gated on Niklavs's go — see resume `open_dep`.)

## Cascade / Main-brain changes

None to brain content this session — all substantive work was in the external `bi-analytics-main` repo. Brain close artifacts only: this quest-log entry, the inventory resume, one examine draft.

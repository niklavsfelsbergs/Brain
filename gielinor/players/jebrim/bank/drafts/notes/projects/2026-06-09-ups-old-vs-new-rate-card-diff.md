# UPS — current contract vs 2026 tender offer (rate-card diff)

**Drafted:** 2026-06-09 ([[S168_1a9eb9d9_ups-old-vs-new-rate-card-diff|S168]]). **Status:** finding, stable. **Promote at:** next Jebrim alching.
**Anchor (full artifact + repro):** `bi-analytics-main/NFE/projects/2_EU_tender_2026/1_offers/picanova/UPS/comparison/`
(`compare_rate_cards.py` + `findings.md` + `data/diff_{standard,zone,de_zones}.parquet`).
Part of the EU-tender UPS thread ([[eu_tender_2026]]); done while UPS Round-1 replies pend.

## What this is
A base-**net-rate** diff of the **current UPS contract** Picanova ships under
(`Documents/Shipping/1. EU/1. PICANOVA/UPS/Picanova UPS Rate Card 2026.xlsm`) vs the **2026 tender
offer** (`…/UPS/offer/Netto-Tarife Picanova_2026_Vertrag Q6744021DE-01_NEU.xlsm`). Both cards are
2026-priced and share an **identical workbook layout** (same sheets + row/col offsets — verified),
so the diff is the **negotiated change**, clean of GRI drift. The offer extraction (`extract_rates.py`)
offsets were re-validated against the old card before reuse.

## Findings (verified)
- **Standard Single, light parcels (≤2 kg) = ~+5% across nearly every EU lane** (DE 2.69→2.82,
  FR 4.60→4.83, AT 4.77→5.01, IT 4.45→4.67, BE/NL 4.15→4.36, CH 11.44→12.01). This is the
  decision-relevant view — our volume is light, Standard is the workhorse. **The new offer is a
  modest uplift on the core product**, not a better deal at the card level.
- **Two carve-outs on Standard light:** **Poland −15%** (4.11→3.50, genuine cut, *same zone*),
  **Denmark + GB flat** (0%).
- **Standard heavy bands (>20 kg) reshape unevenly** (PL +24%, CH −41%, a cluster CZ/Baltics/BG/RO/HU/
  HR/SK/SI/GR/PT only +1.6%) — secondary; small tail for us. The uplift is **weight-dependent**, so a
  flat mean-across-bands is the wrong instrument; split light vs heavy.
- **Express / Express Saver ≈ 97% identical** (1277/1320 bands unchanged). Premium air was **not**
  renegotiated. The 43 changed bands are the rarely-hit 9999 kg over-max band (−75%, ~0 volume for us)
  + domestic-saver heavy bands (+12–79%) + a few far-zone light bands.
- **Structure:** zones **unchanged** (0 reassignments, keyed iso2+PLZ); **Expedited is NEW** as an
  export product (a fresh lever the S163 engine already prices); **WW Economy absent** (confirmed with
  carrier — overseas tail stays on current contract via the engine `WW-ECO-stays` rule).

## Method caveats (load-bearing)
- **Fuel / peak / LPS NOT compared** — provisional pending UPS Q1/Q4/Q6; diffing placeholders = noise.
  Fuel basis alone (flat 35% card vs ~20% real) swamps a 5% base move, so the card delta is *not* the
  whole cost story. → keepsake EU-tender risk #1 (provisional-fuel collapse).
- **Two measurement artifacts caught** (cf. [[2026-06-01-verify-the-thing-dont-trust-the-wiring]] /
  verify-diffs-both-ways): (1) the mean-across-bands *inverted* the 1 kg picture → real weight-dependent
  signal, not a bug, but the flat mean is the wrong summary; (2) a DE_ZONES diff exploded to 1648 rows
  with a false "PL Zone 31→3" — a many-to-many join fan-out; properly keyed on (iso2, von_plz, bis_plz)
  it's **zero** zone changes. Don't report a zone move off the un-keyed join.

## Next step
**Volume-weight it:** price 2026-Q1 actuals through the old card, diff vs the new-card replay already
built. Because fuel/peak/LPS are *identical* params both sides, the **delta is clean of the
placeholders** — a defensible *relative* €/yr number even though neither absolute is quotable. Converts
"~5% on the card" into "€X/yr more on our actual mix."

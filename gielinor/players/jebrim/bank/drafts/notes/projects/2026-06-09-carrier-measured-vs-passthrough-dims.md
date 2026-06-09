# Carrier invoice dims: independent MEASUREMENT vs declared PASSTHROUGH

**As-of:** 2026-06-09 (S173). **Source:** topic 45 (`bi-analytics-main/NFE/shipping_topics/45_invoice_vs_mart_dimension_accuracy/`). Companion to the S167 coverage map [[2026-06-09-carrier-invoice-dimension-coverage]] — *this note corrects it* (see below).

## The distinction this note adds
The S167 map answered "which carriers carry dim data." This answers the harder question: **is that data an independent carrier MEASUREMENT, or just a reprint of the dimensions WE declared** (which we already hold in `shipping_mart`)? Mart dims (`length/width/height/volume/length_plus_girth_cm`) are **PCS-owned = our declared dims** (`shipping-agent/reference/known-dq.md:43`). A passthrough has zero audit value.

**Discriminator method:** join the carrier's raw invoice line to `fact_shipments`, unit-align, compute the **exact-equality rate** vs our declared dim. ≥~98% exact = passthrough; meaningful deltas = real measurement. **Watch the dual-field trap** — a carrier can expose BOTH a declared-passthrough field AND a measured field on the same invoice (check every dim column, not the first).

## Verdict (tested S173)
| Carrier | Verdict | Measured field | Note |
|---|---|---|---|
| OnTrac | REAL | `billed_*_in` | most faithful (~85% within ±2cm); also round-trips declared `length_in` separately |
| FedEx | REAL | L/W/H | genuine but noisy (±15–20cm large formats) |
| Asendia USA | REAL | L/W/H | independent but loose (MAE ~11cm) |
| Yodel | REAL | `actual_*` (mm) | **only 6.9% populated**, bursty (strong Oct 2025–Mar 2026); `declared_*` empty |
| USPS | REAL — subset | `ca_assessed_*` | ~13.8k assessed only; `manifest_*` is verbatim ours |
| UPS | REAL — subset | `packagedimensions` | freight/oversize lines only (~0.8% of volume) |
| Maersk | **PASSTHROUGH** | — | reprints declared L/W/H 100% verbatim |
| DB Schenker | INCONCLUSIVE | `cbm` (volume) | volume scalar only, no axis to discriminate |
| Direct Link | INCONCLUSIVE | `volume` | scalar, unit undetermined |
| DHL (DE/US/ORWO) | NO SIGNAL | — | no usable dim data on the invoice |

Dual-field trap caught on: OnTrac, USPS, UPS, Yodel.

## Correction to the S167 coverage map (pending principal greenlight)
`2026-06-09-carrier-invoice-dimension-coverage.md` files Maersk under Tier-1 "real measured dimensions" and DB Schenker + Direct Link as well-populated measured. **Wrong:** Maersk is a passthrough; DB Schenker + Direct Link are volume-only scalars with no independent-measurement value; Yodel is not "full coverage" (6.9%). Demote on greenlight.

## PCS PL consequence
At `production_site = 'PCS PL'`: DHL (~45%) no signal, UPS (~22%) oversize-subset only, **Yodel (~8%) the only at-scale independent measurement** — and only on its 6.9% dim-populated subset. So independent dim audit covers a small minority of PCS-PL volume; the bulk (DHL especially) is unaudited.

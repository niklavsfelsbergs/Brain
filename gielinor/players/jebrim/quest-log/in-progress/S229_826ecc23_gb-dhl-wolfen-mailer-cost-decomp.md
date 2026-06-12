# [[S227_6f393689_scm-breakdown-cost-basis-fix|S227]] — GB+DHL Wolfen flat-mailer cost decomposition (shipping-agent emulation)

**Player in scope:** Jebrim
**Spawned by:** Niklavs, scoped mart pull for NFE shipping_topics/47 (loss-making-lane follow-up)
**Tier:** gold-contract (`shipping_mart.*`, four facts). Maintainer overlay present but not needed.
**Window:** shop_order_created_date 2025-05-01 .. 2026-04-30. Scope: TCG (source_system IN Picturator,PicaAPI).
**Cohort:** destination GB + carrier DHL + packagetypes {Großbrief/Maxibrief, Versandtasche A3 Kalender, Versandtaschen B4}.

## Turn log
- Origin confirm: cohort is production_site='Wolfen' on **Picturator** source (NOT the ORWO identity-only source) — so these Wolfen parcels carry full packagetype/dims. Wolfen share: Großbrief 1199/1231=97.4%, A3 100%, B4 100%. Small non-Wolfen tail = 32 PCS-PL Großbrief rows (€589). Origin = Wolfen, confirmed.
- Bucket decomp on invoiced subset (cost_source='invoice'): cost is ~97-98% **base_rate** for Großbrief + B4; A3 has base ~82% + oversize ~16.5%.
- Sperrgut answer: NO oversize on Großbrief (0/969) or B4 (0/325). A3 only: 43/207 ships carry "Surcharge Bulky goods International" = €903 total (€4.36/ship). Base dominates everywhere.
- Raw charge desc: base line = **"DHL Parcel International (GK) Premium"** ~€21.50/line, invoice_source dhl_orwo. These flats are billed as **international premium PARCELS**, not letters — that's the expense. Fuel (Maut/CO2) + peak negligible.
- Dims: Großbrief 32x24x2 / lpg 85cm; B4 35x25x2 / lpg 89cm (flat, no oversize). A3 48x33x1 / lpg 116cm — long flats, oversize physically justified where it fires.
- % invoiced: Großbrief 68.6%, B4 89.3%, A3 94.9% — bucket decomp run on invoiced subset only (real, not modeled).

## Headline
"Why so expensive" = expensive DHL international-parcel base rate (~€21.50/ship), NOT sperrgut. Only the A3 calendar mailer carries a (justified) bulky-goods surcharge, and even there base dominates. Großbrief/B4 = pure base, zero oversize.

## Deliverable
Raw bucket tables + SQL + plain-language answer returned to Niklavs in chat for folding into NFE findings.md. No charts requested.

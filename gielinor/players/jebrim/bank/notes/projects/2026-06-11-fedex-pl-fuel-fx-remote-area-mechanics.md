# FedEx Poland fuel/FX/remote-area mechanics (EU tender fedex engine inputs)

As of: 2026-05-27

- FedEx PL runs THREE independent fuel-surcharge indices (VASS schedule, eff. 5 Jan 2026): International (kerosene jet fuel - applies to IE/International Economy), Regional (EU automotive gas oil / diesel - applies to RE/Regional Economy + REF), Domestic (separate, not in scope). RE and IE are therefore on DIFFERENT fuel indices - one fuel number cannot serve both.
- Cadence: Regional updates weekly (Monday-effective, posted the Friday before, EC DG Transport & Energy gas-oil prices); International moves in periodic step changes with named effective dates (e.g. 6 Apr 2026, 11 May 2026).
- EUR/PLN: Q1 2026 actuals ~ Jan 4.2114, Feb 4.2186, Mar 4.2725; Q1 avg ~4.234. The engine's 4.30 placeholder was HIGH by ~1.5% (understates EUR cost when dividing PLN by it) - provisional at research time, replaced in later engine work.
- Extended Area Service (OPA/ODA remote-area), international, eff. 5 Jan 2026, ex-VAT: Tier A PLN 15/shipment flat; Tier B PLN 2.60/kg min PLN 105; Tier C PLN 3.35/kg min PLN 135. Postcode-list driven; the list exists (linked from the live schedule) but was not pulled.
- Address Correction: International PLN 43.70/shipment; Domestic PLN 12/shipment.
- Adjacent VASS items (same doc): AHS Intl - Dimension PLN 150/pkg, Packaging PLN 120/pkg, Weight >25kg PLN 180/pkg (highest single applies); Oversize PLN 220/pkg; Third Party Billing 2.5%.
- Source doc gotcha: the FedEx PL VASS schedule lives at carrier_responses_to_open_questions/Maersk/new-offer-rates-vassuis-en-pl.pdf - filed under Maersk but it IS the FedEx PL schedule.
- Gotcha: all FedEx-published surcharge web pages were access-gated to fetchers at research time; exact monthly fuel % was a carrier ask then (later closed by the 2026-06-03 fuel-history research).

Source research: [[2026-05-27-fedex-fuel-fx-remotearea]] - full sources and detail there.

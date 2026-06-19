# Trace: dwarf_orwo-ups-contracts

Task: ORWO UPS contract review (current + old), write ups.md
Date: 2026-06-19

## Turn-by-turn log

1. Read spawning-dwarves.md — confirmed write boundary and no sub-spawn rule.
2. Attempted to open 0R6D66 and World Ease xlsx files via openpyxl — SUCCESS. Also tried 0R6D51.xlsm — FAILED: file is an XML digital-signature wrapper (20 KB, starts `<signatures>`), not a real spreadsheet. Probably a UPS signing artifact or placeholder.
3. Dumped 0R6D66 sheet `01_UPS TM Economy DDP - Versand`: worldwide rate matrix, 35 zones (CA zones 1-5, AR, BR, CL, CN, CO, AU x4, HK, IN, ID, IL, JP, KR, MY, MX, NZ, NO, SA, SG, ZA, CH, TW, TH, TR, AE, US, GB x2). Weight breaks 0.5–30 kg (per-shp), then per-kg for >30 kg. Contract ID Q5041622DE, customer "WW Economy Picanova", service "UPS TM Economy DDP", from DE, start 13 Jul 2024, end 30 Mai 2054.
4. Dumped World Ease Expedited sheet `WW Expedited + Worldease`: US/Canada only (Zone 4), 1–80 kg per-shp rates, with derived columns for residential surcharge +0.40, fuel +20.96%, US Processing Fee 1.18 (50% discounted). Service labelled "Worldwide Expedited - ORWO US Project".
5. Read current UPS ORWO Contract PDF (Q6842839DE-02, signed 01 Sep 2025, effective 03 Sep 2025 – 31 Dec 2025 then indefinite). Addendum A: account TEM10548391 = PICANOVA GMBH. Addendum B: domestic Standard Zone 1 rates, export transborder zones 3/4/5/31/41, export worldwide zones 6/704, country-level rates for AT/BE/EE/FI/FR/IE/IT/LU/NL/PL/ES/SE/CH. Addendum C: fuel surcharge 35% off tariff for all service types; residential 0.40/shp; AHC 100% off; address correction 100% off; extended area 100% off; label charges 100% off.
6. Read old xlsm (Q6842839DE-01): Cover = PICANOVA GMBH, Q6842839DE-01. DE E-Standard Single sheet: same zone structure (DOM Zone 1, TB Zones 3/3+4/4/4+5/31/41/5, WW Zones 6/704). Rate values appear identical to current contract (same net rates for domestic: Z1 1-3kg=2.69, 3-5=3.26 etc.).
7. Read old Zuschlaege sheet: all accessorials 100% off (AHC, address correction, EAD, EAP), custom thresholds preserved (10cm/50cm AHC triggers, 25cm LPS, 19cm overmax size).
8. Read Shipping Profile PDF: baseline was 4,400 pkgs/month average 0.5 kg/pkg at gross 308,737 EUR/month. Split: domestic 500 pkg, transborder import 1,400 pkg, transborder export 400 pkg, WW export 400 pkg, domestic return 100 pkg, unknown 1,600 pkg. Confirmed 0.5 kg average weight.
9. Noted: current contract PDF (Q6842839DE-02) and old contract PDF ([completed] FU1_Final offer ENG_Q6842839DE-02 signed) appear to be the SAME document (Q6842839DE-02, 01 Sep 2025, same addenda). Old "-01" version has xlsm rate card.
10. ORWO 0R6D51 and 0R6D66 are different UPS account numbers — both have current 2026 rate cards. 0R6D66 = WW Economy rate card under contract Q5041622DE (separate from the Q6842839DE contract). 0R6D51 = signature file only, no data.
11. Wrote ups.md to projects/7_ORWO_tender_2026/contracts_review/.

## Blockers / gaps

- 0R6D51 rate card unreadable: file is a digital-signature XML stub, not a spreadsheet. No rate data recoverable from it.
- Old Q6842839DE-01 xlsm (Netto-Tarife) rate values appear identical to Q6842839DE-02, suggesting -02 is a renewal/extension of -01 with same net rates.
- Account number mismatch: Q5041622DE / 0R6D66 = "WW Economy Picanova" (separate contract), but Q6842839DE = ORWO's contract using PICANOVA account TEM10548391. Need clarification on which account is used for which ORWO shipments.
- Fuel surcharge: current % confirmed as 20.96% (WW Expedited sheet, 18.02.2026). For Standard service the 35%-off-tariff discount means net fuel % depends on published rate — not fixed in the contract.

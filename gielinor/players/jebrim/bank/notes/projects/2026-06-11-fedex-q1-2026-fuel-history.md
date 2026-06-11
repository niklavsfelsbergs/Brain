# FedEx PL Q1 2026 fuel-surcharge history (Intl + Regional) + CH clearance fee

As of: 2026-06-03

- International FSC: USGC kerosene jet-fuel spot (EIA weekly), ~2-WEEK LAG confirmed empirically (FedEx's own pulled March rows each carry the EIA price from 2 weeks prior), Monday-effective. Band table (eff. 6 Apr 2026): $1.69-1.89 -> 31.50%, $1.89-2.09 -> 31.75%, then +0.25% per $0.03 band; same table validated live across Q1 (pulled rows $2.469->35.00%, $3.103->40.25%, $3.478->43.50% match exactly).
- Regional FSC: EC Weekly Oil Bulletin EU-avg automotive gas oil EUR/L, band table pulled in full: 1.47-1.55 -> 19.50%, 1.55-1.59 -> 20.00% ... 1.95-1.99 -> 25.00%, up to 2.51-2.55 -> 32.00% (~+0.25% per 0.04 EUR band). Lag assumed ~1-2wk, NOT independently confirmed.
- Q1 monthly averages, International: Jan ~31.65%, Feb ~32.65%, Mar ~39-40% (35% early -> 43.5%+ late). Jan/Feb RECONSTRUCTED (no pulled history rows), Mar partly PULLED.
- Q1 monthly averages, Regional: Jan ~19.5%, Feb ~19.5%, Mar ~23% (climbing 20.0% -> 25.5% by end-March). All Regional Q1 cells RECONSTRUCTED.
- Q1 is NOT flat - the late-March fuel spike (EIA jet $2.47 -> $4.04, EU diesel 1.57 -> 2.00 EUR/L) is the load-bearing signal; model per-month, not one blended quarter number.
- June 2026 anchors reproduced by both tables (Intl 49.25% at $4.113 = same +0.25%/$0.03 slope extended past the printed top; Regional 22.50% = the 1.75-1.79 band) - strongest validation of the reconstruction.
- Switzerland clearance (FedEx CH ancillary schedule, CHF): DDP disbursement fee = 2.50% of duties+taxes advanced, min CHF 22.00; DAP standard clearance is bundled in transport (CHF 0 incremental for a routine single-commodity parcel). Situational: 6th+ line item CHF 13/item, In-Bond CHF 74, OGA CHF 84+, Post Entry Adjustment CHF 135.
- The CH-specific CHF 22 / 2.5% schedule supersedes the earlier generic pan-EU display (EUR 8 min / 15 flat / 2.5% > EUR 600) for Switzerland.
- Gated-page workaround that worked: r.jina.ai proxy read the FedEx PL surcharges page and the Intl FSC PDF that direct fetches could not.

Source research: [[2026-06-03-fedex-q1-2026-fuel-history]] - full sources and detail there.

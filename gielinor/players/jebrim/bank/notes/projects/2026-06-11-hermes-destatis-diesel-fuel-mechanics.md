# Hermes fuel surcharge - Destatis diesel index mechanics

As of: 2026-05-27

- Hermes's fuel ladder prices off the Destatis producer-price index "Dieselkraftstoff Abgabe an Grossverbraucher" (large-consumer diesel), EVAS 61241, base 2021=100. NOT the Grosshandel (wholesale) series, NOT the consumer Verbraucherpreisindex.
- The index IS the price relative: monthly index = Grossverbraucher price EUR/100L / 108.66 x 100 (108.66 = the 2021 annual-average price = index 100). Self-validates on the confirmed Jan-2026 anchor: 133.08/108.66x100 = 122.5.
- Reply ladder (the correct one): 0.00% for index <= 122.7, then +0.50% per ~2.578-pt band; formula % ~ ceil((I - 122.7) / 2.578) x 0.5%. Endpoints confirmed: 0% <= 122.7 and 14% at 192.4-194.8. Linear-band rule assumed uniform across all 28 bands (confirm exact printed edges before pricing).
- TRAP - two-ladder reconciliation: Hermes's OFFER ladder (0% up to 155.3, "Mar 2026 = 154.9 -> 0%") is the SAME ladder on the retired 2015=100 base (~1.26x scale). Destatis rebased 2015->2021 with the Jan-2024 reporting month; the 2015 series has no live feed. Replay only on the 2021=100 reply ladder.
- The stale offer "154.9" and the live Mar index 158.5 are numerically close but on DIFFERENT scales - do not read the proximity as agreement.
- Q1 2026 values (firmed): Jan 122.5 -> 0.00%; Feb 122.7 -> 0.00% (exactly on the inclusive 0% threshold - knife-edge, get Hermes's Feb print in writing); Mar 158.5 -> ~7.0% (band ~156.4-158.9; range 6.5-7.0%).
- Mar prices: Grossverbraucher 172.25 EUR/100L (LasiPortal), index 158.5 corroborated by the BGL Grossverbraucher series.
- Republication-feed traps: LasiPortal/BGL/ZUFALL publish the PRICE, not the index (several mislabel it "Preisindex"); ZUFALL labels by billing month, LasiPortal by 15th-of-month survey (one-month offset); press-release "Kraftstoffe" MoM is petrol+diesel combined and understated the Mar diesel spike (first pass got Mar ~151/~11% wrong on it).
- Hermes's EUR/L figures (base 2021 = 1.165 EUR/L) are Hermes-internal; only the index is Destatis-anchored and auditable. Track the index, not Hermes's EUR/L.

Source research: [[2026-05-27-hermes-destatis-diesel-index]] - full sources and detail there.

# ORWO carrier contracts 2026

Draft (2026-06-19, [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]]). For [[carrier-contracts]]. Source: `NFE/docs/shipping_contracts/.../ORWO` (current `1. EU/2. ORWO/`, old `0. OLD/EU/ORWO/`); full per-carrier write-ups in NFE `projects/7_ORWO_tender_2026/contracts_review/`. Legal entity: Orwo Photolab GmbH / ORWO Net GmbH (Bitterfeld-Wolfen).

**Current 2026 cards on file:**
- **UPS** - accounts Q6842839DE-02 (TEM10548391, primary) + Q5041622DE/0R6D66 (WW Economy). Services: Domestic Standard (DE), TB Standard (EU), WW Std/Economy DDP/Expedited. Base = weight x zone. Dims needed only for WW Economy DDP / Expedited (max(actual,volumetric)) + LPS(>25cm)/Overmax(>19cm) surcharges. Fuel = 35% off a floating index (not reconstructable from contract). `0R6D51` was a dead signature stub.
- **DHL** - cust 5311934365 / contract 40440743. Products: Paket domestic (3-tier weight break), Kleinpaket (flat <=1kg), Paket International, **Warenpost International**, Express (sep acct DE102981753), Freight. Weight-keyed.
- **Austrian Post** - AT domestic only. Two weight bands (<=2kg/<=30kg). Base weight-only. **Factsheet missing** from file set (volumetric divisor + rural surcharge). T&C letter is 2024/2025-rate; 2026 signed terms not on file.
- **Guell (CH)** - weight-break model (2/10/30kg x Priority/Economy), CHF. **No density/pallet pricing** (unlike the Picanova Guell). Sperrgut (oversize) needs dims, small exposure. **Prices locked to 31.12.2025** - 2026 card not on file.

**POST gap RESOLVED:** the mart "POST" carrier (~EUR82k/mo, was 99% estimated) = **DHL Warenpost International = Deutsche Post AG** (settlement code 66, billing numbers 5311934365 66xx, invoiced by Deutsche Post under the ORWO DHL account). Rate = base + per-100g x zone(1-6) x service. The 99%-estimate was a missing-rate-card problem, now closed.

**Old/historical:** GLS (real DE+EU offer, dims-friendly/no volumetric, but **lapsed 2025-12-31 + unsigned** - needs a fresh 2026 quote); nShift (integration platform, signed, in force; configured carriers Maersk/Deutsche Post/DHL DE/UPS/GLS DE); Fuji Return (returns table, carrier unnamed); DHL Express/Freight (old offers/admin).

**Dimension coverage caveat for repricing:** ORWO base rates are weight-keyed so dims aren't needed for base. Mart dims/weight are mis-grained/capture-gapped for ORWO -> see [[2026-06-19-orwo-mart-weight-grain-and-consolidation]]; reprice at tracking grain off invoice billedweight / parcelfinish weight.

**Related:** [[carrier-contracts]], [[2026-06-19-orwo-tender-scope-and-cost-basis]], [[2026-05-28-ups-orwo-fif-data-quirks]].

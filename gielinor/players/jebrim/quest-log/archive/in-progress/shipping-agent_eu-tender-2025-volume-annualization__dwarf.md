# Shipping-agent pull — EU-tender 2025 volume annualization proxy

**Spawned by:** Jebrim, EU-tender annualization prep
**Question:** Can 2025 volumes be used directly as the 2026 full-year volume proxy, or must they be scaled? Volume/count analysis in the exact tender cost-matrix scope.
**Tier:** gold-contract (`shipping_mart.fact_shipments` only, count + light carrier split)

## Scope (locked)
- `production_site = 'PCS PL'` (Stettin) only
- `cost_source = 'invoice'` only
- Period on `shop_order_created_date` (period-truth column), NOT shipped
- Country set: continental EU/EFTA allowlist (GB + overseas excluded) — fell out of the data, not hardcoded:
  DE,FR,NL,IT,AT,ES,CH,SE,BE,DK,PL,LU,IE,FI,PT,NO,CZ,GR,SK,RO,HU,CY,LV,MT,HR,EE,BG,SI,LT

## Reconciliation vs 531,194 target
- 2026-Q1 scoped total = **528,598** (within 0.5% of 531,194 anchor). Per-country anchors reconcile within ~0.6%:
  DE 344,044 (vs 342,127), FR 50,091 (49,990), NL 34,977 (34,919), IT 26,151 (26,091), AT 24,787 (24,695).
  My counts run ~0.5% HIGHER per-country; the ~2,600 total residual is the opposite sign → snapshot/definition drift,
  not a wrong country list. GB (94,002 in scope) is decisively OUT (would blow past target). PASS.

## Turn-by-turn
- Confirmed PCS PL exists (629,511 invoiced all-countries 2026-Q1) → country filter needed to reach tender pop.
- Tested EU/EFTA continental sets → all land 528,200–528,600; excl-GB-only = 535,389. 531,194 sits between → continental set is the read, residual is drift.
- Pulled 2026-Q1 / 2025-Q1 / 2025-FY by country + carrier + month on locked scope.

## Headline results
- **YoY 2025-Q1 → 2026-Q1: 590,857 → 528,598 = −10.5%** (volume DECLINE).
- 2025 monthly profile: Q1 = 20.7% of FY, Q4 ≈ 40.5%, Dec = 614,969 = **21.5% of the FY alone** (peak). Matches expectation.
- **Carrier mix flipped wholesale**: 2025-Q1 GLS (84k) + COLIS PRIVE (29k) + ~0 DPD-PL → 2026-Q1 DPD POLAND (68k) + MAERSK (27k), GLS & COLIS PRIVE GONE. DHL & UPS roughly stable.
- Verdict: 2025 CANNOT be used directly — needs scaling. Country-level divergence material (CH +42%, DK −31%, FI −31%).

## Deliverable
chat-only (tables + SQL returned to Jebrim).

# S187 — SCM €3.3M (7 countries) vs EU-tender €2.96M (18 countries) reconciliation

**Spawned as:** shipping-agent mart specialist (emulation). Principal: Jebrim.
**Ask:** reconcile two same-labeled "Q1 shipping spend" totals over gold `shipping_mart`; attribute the gap driver-by-driver. Population/basis mismatch, not dropped data.
**Tier:** gold-contract throughout (all columns named live on the four gold facts). CLAUDE.local present but no upstream needed — stayed on gold.
**Period:** Q1 2026 = `shop_order_created_date` in [2026-01-01, 2026-04-01).
**Cost basis caveat carried in all numbers:** freight only (tax/customs excluded by design); invoiced = `real_shipping_cost_eur`, final = COALESCE(real,expected,avg).

## Turn log
- Grounded how_to.md (full first page) + mart-contract + query-patterns + CLAUDE.local before SQL.
- T1 reproduce tender baseline: 532,255 parcels / €3,102,212 gross real. All rows cost_source='invoice', real==total exact. vs brief ≈531,194/≈€3,030,998 → +2.3% drift, attributed to invoice backfill since deck built (contract warns invoiced cost rises over time). UPS OML net-out reconciles: 69 parcels / €75,324 oversize (brief −€75,978). Net ≈ €3.03M live.
- T2 relaxation ladder, 7 SCM countries (DE,FR,AT,NL,IT,ES,CH):
  - L0 tender-exact/7c: 506,422 / €2,802,700
  - L1 drop PCS PL (all sites): 671,361 / €3,237,914 (+€435,214 = Wolfen photo-lab site, invoiced)
  - L2 final basis + drop invoiced-only: 784,760 / €3,612,915 (+€375,001 expected-basis tail; 89.6% invoiced)
  - L3 drop dim/packagetype gates: 1,250,372 / €4,071,165 (+€458,250 dim-null parcels; 90.2% invoiced)
  - **L1 is the single step that closes the gap to ~€3.3M.** Origin filter (PCS PL) is driver #1.
- T3 SCM scope probe: production_site x source_system crosswalk confirms the two are crossing axes — Wolfen *site* produces 103,781 Picturator(B2C) parcels too, ORWO vertical = 619,779 parcels/€711k in 7c (incl untracked/expected tail). All-vertical no-dim-gate scopes overshoot (€3.67M–€4.07M); €3.3M ≈ L1. SCM does NOT filter to PCS PL — shows all sites, default COALESCE(final,expected) basis picks up non-invoiced tail.

## Headline
SCM's ~€3.3M for 7 countries is LARGER than the tender's €2.96M for 18 countries because the tender restricts to one production origin (PCS PL print site) and to invoiced-only freight, while SCM shows ALL production sites (sweeping in the Wolfen photo-lab parcels). Removing just the origin filter (L1) adds €435k and lands at €3.24M.

## Deliverable: chat-only (reconciliation table returned to principal). No files outside quest-log.
## Open: 2.3% live-vs-deck drift on the baseline is invoice backfill, not a method error — flag if deck needs a refresh stamp.

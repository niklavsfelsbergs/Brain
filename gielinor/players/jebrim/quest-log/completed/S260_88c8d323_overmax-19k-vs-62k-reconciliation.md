# S260 — Over-max surcharge: €62K vs €19K reconciliation (May 2026 TCG)

**Spawned as:** shipping-agent (mart specialist), scoped pull for Jebrim.
**Asked:** A logistics manager was told "May 2026 has €62K in over-max surcharges"; the Invoice Details report shows €19K for the same thing. Find the source of the discrepancy against the live gold shipping_mart.
**Scope:** TCG shops (Picturator + PicaAPI), May 2026 order-month (`shop_order_created_date`), UPS over-max parcels. Gold contract — `shipping_mart.*` only.
**Cost basis:** invoiced-only (the whole 47-parcel population is 100% invoiced).

## Turn-by-turn
- Loaded how_to.md + mart-contract.md in full. No CLAUDE.local.md → gold-only perimeter absolute.
- Found the literal over-max labels in invoice lines: UPS "Demand Surcharge - Over Maximum", "Over Maximum Size", "Over Maximum Length", "Large Package Surcharge" — all collapse into the single `oversize_overweight` bucket (rule 15). OnTrac "Over Maximum Limits Surcharge" is a separate US tail (45 parcels, €422) — not this population.
- Population locked: **47 parcels, all UPS** — matches prior pull exactly.
- Bucket split (total_eur = €61,732): oversize bucket €50,567 / fuel €10,002 / base rate €1,069 / other €47 / residential €9. Bucket invariant holds: 11 buckets sum to €61,731.94 == total_eur.
- Over-max surcharge isolated: "Demand Surcharge - Over Maximum" = **€22.3K** (47 parcels, exactly 1 line each, ~€475/parcel — consistent with rule 15's >€400 inference). Plus dimensional Size/Length €23.5K + Large Package €4.8K fill the rest of the oversize bucket.
- **€19K reconciled to invoice-lag:** cumulative over-max Demand Surcharge by invoice_date hit **€18,525 by week of June 1**, then climbed to €22,325 by mid-June as lagging UPS invoices landed. €19K = the over-max surcharge at an early-June report snapshot.

## Headline result
- **€61.7K = total landed cost** of the 47 over-max parcels (base + fuel + ALL surcharges). NOT the over-max surcharge.
- **€19K = the over-max surcharge line-item itself**, captured at an early-June Invoice Details pull (€18.5K). Now €22.3K with full invoice coverage.
- Root cause: €62K summed the TOTAL cost column over the parcels that *carry* an over-max surcharge; €19K is the over-max charge line alone. Different things, same parcels.

## Caveats
- The €19K→€22.3K drift is UPS invoice lag (15 of 47 parcels' over-max lines invoiced in June). The current full over-max surcharge is €22.3K, not €19K.
- "Over-max surcharge" is ambiguous: the canonical UPS "Demand Surcharge - Over Maximum" = €22.3K; the whole over-max dimensional family (Demand + Size + Length) = €45.8K; the entire oversize bucket = €50.6K. Confirm which definition the manager's source used.

## Deliverable
- Chat-only reconciliation table returned to principal. No chart (single small table).

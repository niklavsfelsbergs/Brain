# DPD UK "2day" avg cost drop May->June 2026 — driver diagnosis (shipping-agent emulation)

**Player:** Jebrim | **Tier:** gold-contract (shipping_mart only; no CLAUDE.local.md) | **Session:** d1f7d4b7
**Ask:** Why did DPD UK "2day" avg cost/shipment drop ~GBP20 (May) -> ~GBP10 (June)? Test (a) destination mix, (b) rate change, (c) cost-basis artifact.

## Turn log
- Scoped slice: carrier `DPD UK`, service `DPDUK2DN` (= "2day"; `DPDUKNDN` is next-day, excluded). GBP-invoiced, FX flat (~0.865), so EUR vs GBP not the story.
- Volume stable-ish: May 1,584 shipped (98.7% invoiced) vs June 826 shipped but only 60% invoiced (326 on "expected"/estimated). The "GBP20->GBP10" headline = all-shipments final-cost avg (EUR19.2->10.7); invoiced-only GBP avg = GBP14.89->9.93.
- Bucket split (rule 4, first decomposition): base_rate is the mover (GBP11.73->7.96/ship); fuel falls via lower fuel-incidence share; oversize/peak/other negligible. No new/disappearing bucket.
- Weight + dims FLAT (1.63->1.65kg, 151->150cm girth) — not a lighter-parcel mix.
- Zone split: base rate is bimodal — mainland <GBP4 vs a flat GBP19 remote/island surcharge zone (BT/IV/PA/PH/KW/HS/ZE/IM/GY/JE).
- **Like-for-like per-shipment GBP by zone is FLAT both months**: mainland GBP3.14->3.09, remote GBP20.39->20.58. No rate change.
- **True shipped mix barely moved** (remote 68%->63% of all shipments). But INVOICED mix collapsed: remote invoiced 99% (May) -> 37% (June). The expensive remote invoices haven't landed (DPD lag + June partial to the 17th).

## Verdict
**(c) cost-basis / coverage artifact — partial-month invoice lag.** Not (b) rate (zone rates flat), not (a) real mix (true shipped mix stable). The cheap mainland invoices arrive fast; the expensive GBP19 remote-zone invoices lag, skewing June's invoiced average cheap. Reconstructing June at May's coverage -> ~GBP14.1/ship, ~back to May. Drop is an artifact, expected to revert as June invoices arrive.

## Deliverable
- Chart: shipping-agent/workbench/analysis/20260617-dpd-uk-2day-cost-drop/outputs/20260617-112421--dpd-uk-2day-coverage-by-zone.html
- SQL + data colocated in same analysis item.

## Checks done
- Bucket split reconciles to total; zone-weighted blend reproduces both monthly invoiced averages (May 14.89, June 9.93).
- FX confirmed flat; currency confirmed GBP; zero/null-cost rows checked (none material).

---

## RECONCILIATION vs Power BI "Shipping Invoices Report" (principal pushback, session d1f7d4b7 cont.)
Principal challenged the order-month framing with a PBI screenshot (Service=2DAY, Date Type="Invoice Date", May £23,440/1,130/£20.74 -> June £13,196/1,348/£9.79). The order-month pull (June 826 shipped/496 inv) disagreed ~3x with PBI's June 1,348. Pinned the grain mismatch.

**A. Lens matched = invoice_date month** (carrier billing period). Reproduces PBI to the penny on avg:
| period | PBI cnt/avg | invoice_date cnt/avg |
|---|---|---|
| 2025-12 | 1,070/£26.32 | 1,024/£20.07 (avg outlier - PBI Dec scopes wider; immaterial to May/June) |
| 2026-04 | 484/£21.51 | 475/£21.18 |
| 2026-05 | 1,130/£20.74 | 1,108/£20.56 |
| 2026-06 | 1,348/£9.79 | 1,293/£9.72 |
Counts ~3-5% under PBI (PBI parcel-count slightly wider service map); avgs match to pennies. shipment_date lens also tracks but invoice_date is the one that produces a populated June column under an "Invoice Date" toggle (the 5/30 pin in the screenshot is stale; live max invoice_date = 6/14). The order-month framing was a DIFFERENT population (spine ship/order date, all shipments incl. uninvoiced) - not wrong, just not this report's lens.

**B/C/D. Drop SURVIVES on the report's own lens, and it is mix-lag (a), reverts. NOT a real remote drop (b).**
- Per-postcode avg FLAT May vs June: BT £25.00->£24.77, IV £24.43->£24.54, KW £24.22->£22.88, PA £10.57->£9.58. No rate change.
- avg tracks remote-share lockstep every month (0% remote->£6.95; 100%->~£20; 38%->£9.72) => pure destination mix, not rate.
- DECIDER: order-date (mix-complete) June remote-share = **62.7%** (normal: Dec 65.4, May 67.6). Invoice-period June remote-share = **37.8%** (depressed). The cheap mainland parcels bill fast and fill June's billing bucket; the expensive Highlands/Islands/NI remote invoices for June activity haven't landed -> they arrive July+ and pull June's avg back toward ~£15-16. Same lag conclusion as the order-month pull, now proven on the report's own lens.
- May's invoiced set is 100% remote postcodes (BT/PA/IV/PH/KW/HS/IM/ZE) - the mainland May parcels just hadn't billed by month-end either; they'd have landed in later periods.

**Earlier "reverts to ~£15" conclusion HOLDS on this lens.** The drop is a billing-period fill artifact, not a real cheapening of 2-day shipping.

## Reconciliation deliverable
- Chart: shipping-agent/workbench/analysis/20260617-dpd-uk-2day-cost-drop/outputs/20260617-122720--dpd-uk-2day-order-vs-invoice-remote-share.html
- SQL: .../sql/20260617-02_pbi-lens-reconcile.sql ; data CSVs 02/03/04 colocated.

## Close (S257, sid8 d1f7d4b7)
Question fully answered across two passes (initial mart cut + PBI-lens reconciliation). Verdict held: the £20→£10 is an invoice-period fill artifact (cheap mainland bills first; expensive remote lags), NOT a rate change and NOT a real mix shift — reverts to ~£15-16 as June remote invoices land. Principal accepted; confirmed the plain-language "yes, the bucket is more mainland right now, that's why" framing.
- **open_dep: none.** Only optional follow-up = re-pull June billing-period remote-share in early-mid July to empirically confirm the revert (37.8%→~63%). Non-blocking; offered as a reminder.
- Harvest: 1 examine draft (name-the-lens-when-relaying-a-subagent-verdict) + 1 cross-conv memory. The first pass's order-month lens != the principal's invoice-period report = the correction that produced the draft.
- Deliverables (charts/SQL/data) live in the shipping-agent repo workbench, outside the brain. Brain artifact = this trace.
- Graduated → completed/ (analysis shipped, no open dep).

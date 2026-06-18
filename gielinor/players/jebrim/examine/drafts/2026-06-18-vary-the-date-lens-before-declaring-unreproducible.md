# Vary the date lens before declaring a figure unreproducible

**Draft.** Source: S260 (88c8d323), 2026-06-18 — over-max 62k reconciliation.

This session I tried to reproduce a sub-agent's €61,732 / 47-parcel over-max cost figure, got €56,445 / 43 parcels on my own pull, and **declared the €62K "unreproducible — an artifact, discard it."** That was wrong. The principal asked "maybe 62k is by shop order created date?" — I re-anchored the exact same cohort on `shop_order_created_date` (order-month) instead of `transactiondate` (ship date) and it reproduced to the cent: €61,731.94. The 4 "extra" parcels were May-ordered but shipped/billed outside May.

**The lesson.** When a derived cost/quota figure won't reproduce, the **date anchor** (order-month vs ship/received vs invoice date) is the first thing to vary — *before* concluding the number is broken. The shipping mart alone carries `shop_order_created_date` / `received_by_carrier_date` / `delivered_by_carrier_date`, and the invoice layer adds `invoice_date` / `transactiondate` (≈ `shipment_date`) — a cohort's count and total move materially across them. Declaring "unreproducible" after testing **one** lens is a premature absence-assertion (sibling of never-assert-absence + name-the-lens-when-relaying-a-verdict). A figure you can't reproduce may be *your reproduction* that's mis-lensed, not the original.

**How to apply.** Before writing "this number is wrong / an artifact / can't be reproduced": enumerate the candidate date anchors and re-run across them. Only after the figure fails every plausible lens is "unreproducible" a defensible claim. Order-month is the SCM/quota-standard lens — try it first for cost/quota figures. Links: [[2026-06-12-which-variant-anchor-to-most-recent-active]].

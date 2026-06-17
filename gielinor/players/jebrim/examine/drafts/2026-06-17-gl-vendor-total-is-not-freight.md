# A GL vendor total is not freight — verify the basis before comparing carrier spend across QB and the mart

**Observation ([[S258_67ba98fb_qb-bi-invoice-reconciliation|S258]], sid8 67ba98fb, topic 48).** Reconciling QuickBooks carrier invoices against the BI shipping mart, I presented QB's gross per-vendor totals (e.g. Asendia ~$1.18M for 2026 Jan–May) as "booked cost" — comparable to LucaNet/BI freight. They are not: the LucaNet/BI Asendia *freight* figure is ~$445k. The gross vendor total overstated freight by ~2.6×.

**Why it's wrong.** A vendor-level GL sum bundles two things a shipping figure excludes:
1. **Payment-type mixing** — `Bill` (the cost booking) + standalone `Check` (direct-pay) can double-count, and `Bill Pmt -Check` settles AP rather than adding cost. Summing transaction rows blind to type inflates the number.
2. **Expense-category mixing** — `-SPLIT-` bills post freight *and* non-freight (duties/VAT/customs/adjustments) the carrier fronts and rebills. A shipping mart correctly carries only the freight lines. (Confirmed at the invoice level: the $103.7k Asendia QB-only tail was 21 `-SPLIT-` bills, and even matched invoices ran QB ≥ BI by 1–3.5% — the surcharge/duty residue.)

**How to apply.** Before comparing carrier spend across the GL and a shipping figure, pin the basis: sum **Bills only** (exclude Checks/Bill-Pmts) and isolate the **freight expense account** (e.g. `4730 Asendia`, `4731 OnTrac`), stripping `-SPLIT-` non-freight — *then* compare. A raw `SUM(vendor amount)` is gross vendor spend, not freight cost. Invoice-*number* matching is unaffected (presence ≠ amount); this trap is specific to amount/cost comparison.

Sibling of [[size-artifact-on-booked-basis]] / decompose-before-attributing-a-cost-gap / populated-column-is-not-a-measurement: the label on a total ("Asendia spend") doesn't certify what it measures. Caught and corrected in-session, but only after presenting the inflated table once.

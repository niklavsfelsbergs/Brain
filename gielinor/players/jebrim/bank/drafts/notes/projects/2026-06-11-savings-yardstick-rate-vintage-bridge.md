# Savings yardstick must share the decision's rate vintage — the three-number bridge

**Example (the founding catch).** EU tender round-2 Q08: the routing moved 21,946 DE Poster40
parcels DHL→DPD and the report booked it as a **loss** (−€568 Q1). Both were right: DHL raised
its flat rate €3.13→€3.32 (+6.1%) in late Feb, the decision compared DPD against the
March-anchored (post-increase) keep cost and correctly won, while the savings column compared
against full-Q1 actuals — ⅔ of which were at the dead pre-increase rate. Forward-correct move,
retrospective minus sign.

**The rule.** When any carrier's rates move inside the baseline window, a single
actuals-baseline can't serve both jobs. Report a **three-number bridge**, one meaning per delta:
(1) what we paid (actuals, finance-reconcilable) → (2) what doing nothing costs at current/2026
rates → (3) what the plan costs. Plan savings = (2)−(3) only, per flow and headline; the
(1)→(2) delta is the carriers' rate moves, labeled as such. Corollaries: stay rows (`ups→ups`,
`dhl→dhl`) book phantom penalties under an actuals yardstick; savings *against* a carrier that
raised rates are understated; and a latest-month anchor with a thin-cell fallback to the full
window quietly mixes vintages (pro-incumbent bias on marginal cells).

**Status.** q09 build session implements this in the tender report (handed off 2026-06-11).

## Anchor

[[S196_5733cb1d_eu-tender-result-investigation|S196]] T28–T33 (q08 findings §Q08b/§Q08c, the
"why does it pop up if it's a loss" exchange); rate increase verified same-weight-bucket in
`result_investigation/q08_dhl_paket_to_dpd_pl.py`.

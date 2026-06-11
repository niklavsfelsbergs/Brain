# [[S209_89e4a123_carrier-overview-v2-rederive|S209]] D5 — dhl_express hand re-derive (carrier_overview_v2)

**Dwarf for Jebrim.** Rewrite sections/dhl_express.md to reconcile prose to the regenerated deterministic card after UPS entered as 10th offer + engine drift. NARRATE-NOT-REDERIVE ([[S180_4766eb11_dpd-current-report-refresh|S180]]).

## What I did
- Read ground-truth card `_data/hands/dhl_express_card.md`, current `sections/dhl_express.md`, PLAN §5.
- Card authoritative: coverage 956,968 / 33% book; **0 wins**, **0 within-10%**, **46 off-pace**. Native envelope demand 52.2% / oversize 14.4% / remote 6.8% / nonconv 0.0%.
- Rewrote `sections/dhl_express.md` in place, same structure.

## Key reconciliations (old prose → card)
- One-line: "almost never the cost winner" → "never the cost winner (0 of 46 eligible segments)".
- Where it wins: "exactly 1 segment, CH Bulky 1–2 kg €18.26" → **0 wins, 0 within-10%**. The CH Bulky win is gone — **UPS took it** (10th offer). vs-today HOLLOW line dropped (no win left to test).
- Where it competes/loses: old "3 per-parcel-cheapest-but-mean-loser segments" + "42 off-pace" → card has no competitive entries, only off-pace. Collapsed to **off-pace on all 46**, +70% to +350%, with 6 card-exact examples (Iberia Bulky 2–5kg €30.94 +351.6% vs maersk, etc.).
- Why (mechanic): appended "UPS took CH Bulky → no cost segment left". Engine-mechanics prose preserved.
- Analyst take: rewrote to 0 wins / 0 within-10% / 46 off-pace; UPS took the lone slice; premium-not-cost framing kept; new-carrier risk kept.
- Cost-structure: PRESERVED — engine-fire counts (137,840× oversize, 65,432× remote, 499,553× demand, 17× nonconv) are fire counts not envelope %; card does not contradict. Coverage 956,968/33% matches.

## Contradiction resolved
- Old prose's "1 win + 3 competes" framing fully removed; the per-parcel-cheapest-but-mean-loser segments (not in the new card structure) dropped rather than carried forward.

Status: DONE. Out of scope held — only sections/dhl_express.md touched.

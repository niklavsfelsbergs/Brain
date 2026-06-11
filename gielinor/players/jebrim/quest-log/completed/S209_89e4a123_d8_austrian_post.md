# [[S209_89e4a123_carrier-overview-v2-rederive|S209]] D8 — austrian_post hand reconcile (carrier_overview_v2 re-derive)

Dwarf for Jebrim. NARRATE-NOT-REDERIVE: reconcile sections/austrian_post.md prose to _data/hands/austrian_post_card.md.

## Card ground truth read
- Coverage: 184,612 / 6% of book (unchanged from section).
- WINS: 0. Within-10%: 0. Off-pace: 9. (unchanged headline)
- Native envelope: line_haul 100%, maut_at 75.5%, diesel_ch/customs_ch 24.5%, sperrgut_at 8.6%.

## Discrepancy found (section vs card)
- **AT · Standard ≤1 kg** (51% lane, 2.5% book): card = €5.44, **+48.6% vs dpd_pl_current=3.66**. OLD section said "+29.4% vs guell 4.20" — WRONG comparator (was guell, is dpd_pl_current) AND wrong % (29.4→48.6). This is the one real correction; on its single biggest AT lane the winner is now dpd_pl_current, not guell.
- All other 8 off-pace lanes: card numbers match section verbatim (guell comparators hold).

## Consequence for framing
- Still 0 wins — firm-fallback framing kept.
- Nuance: it's no longer "guell beats it on every lane." On AT Standard ≤1 kg, dpd_pl_current is the winner. Güll still wins the rest of AT + all CH. Adjusted "dominated by guell" prose to acknowledge dpd_pl_current on the largest AT lane while keeping guell as the dominant blocker and the held one.

## Done
- Rewrote sections/austrian_post.md in place. Cost-structure engine prose preserved (no number contradicted by card).
- Edits: One-line, Where-it-wins, off-pace AT≤1kg line + lead-in, Why-mechanic AT-Standard line, The-lever (split held-guell vs firm-dpd), Analyst-take (dominated-by-guell→8/9 + dpd ninth).
- Coverage 184,612/6%, native envelope, and 8 guell off-pace lanes all matched card verbatim — unchanged.

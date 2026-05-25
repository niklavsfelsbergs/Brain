# Resume — shipping-agent board-numbers learnings (S063)

**Status:** in-progress (core deliverable shipped + committed; verification open)

**Where we are:** 8 board-numbers learnings harvested and implemented as 6 edits to the shipping-agent `how_to.md` (committed `bab905e`), captured in the Jebrim quality-assessment bank note (committed `941432f`). A naive embodying-agent re-test confirmed 6/8 rules fire; the original response's 3 worst failures are fixed.

**Next concrete step:** On the next *real interactive* use of the shipping agent, spot-check the two rules a single-shot probe couldn't exercise:
1. **rule 12** — does it lead with the numbered `1. TCG / 2. Both / 3. ORWO` selection *and wait*, on an unscoped "we"?
2. **rules 20/27** — does the "note this in memory?" offer fire on a durable finding or at a close cue?
If both fire → close this quest. If not → tighten the rule text (don't re-guess from the contaminated probe — get the clean live signal first).

**Files to read first:**
- `Documents/GitHub/shipping-agent/how_to.md` — rules 12, 16, 35, 4, 2, 20/27 (the edits)
- `bank/notes/projects/shipping-agent-quality-assessment-2026-05-24.md` — the 8 learnings + impl mapping (the 2026-05-25 section)
- `quest-log/in-progress/S063_5b1ac700_shipping-agent-board-numbers-learnings.md` — this session's narrative

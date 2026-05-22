# Translation tables are read bidirectionally — ambiguity propagates

**Date:** 2026-05-22
**Player:** Jebrim
**Anchor:** S033 shop-vs-vertical fix conversation. The shipping-agent's `how_to.md` translation table listed `source_system` against multiple external handles ("production line" and "shop platform"). When Niklāvs asked for a shop-grain breakdown, the agent freehand-mapped "shop" to `source_system` and returned a by-vertical breakdown instead — the wrong grain. Folded into commit `9e63dd5`.

## The observation

The translation table lists **internal-name → external-handle** mappings as a one-way reference (when the user uses external handle X, prefer internal name Y). But the agent uses the table **bidirectionally** in practice:

- Forward read: user says "vertical" → agent picks `source_system`. (Intended direction.)
- Backward read: user says any external handle that appears in the listed mappings → agent picks the internal name those mappings front. (Unintended consequence.)

When a single internal name carries **multiple external aliases** in the table (e.g., `source_system` ↔ "production line" AND `source_system` ↔ "shop platform"), the agent will resolve ANY of those external phrases to that internal name — even if one of them is wrong for the user's actual question. The forward mapping is fine; the backward mapping is what fires the bug.

In S033, "shop" (substring match on "shop platform") got resolved to `source_system` because that's where the table front-listed it. The user meant `vertical` (the actual shop-grain column). The agent had no signal that "shop" was ambiguous because the table was structured as one entry per internal name with comma-separated aliases.

## The lesson

When authoring a translation table:

1. **Don't front-list multiple meanings of one internal name.** If one column legitimately answers two different user phrasings, list it under each phrase as a separate row — even if it duplicates the internal name. The agent reads rows, not aliases.
2. **Audit for back-collisions.** Before adding a row "X ↔ A, B, C," check whether any of A, B, C could legitimately mean a different column. If yes, that column needs its own row above, so the alias-priority is unambiguous.
3. **In doubt, ask which grain.** When the user's external phrase matches multiple table rows, the cheap repair is "do you mean the X grain or the Y grain?" before answering. The expensive failure is freehand-mapping and giving the wrong-grain answer with confidence.

## Why this is examine-worthy

It's a meta-pattern about how the agent reads its own reference docs, not a one-off shop bug. Any reference doc that maps internal → external is at risk of the same bidirectional-read trap. The shipping-agent docs are the first instance; the brain's own translation surfaces (e.g., player addresses, dwarf trigger phrases) could carry the same risk.

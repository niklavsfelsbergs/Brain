# Structural restructure: mechanism over shape

> **Status:** draft, anchor [[S024_2026-05-21_shipping-agent-rulebook-revamp|S024]] T14 (2026-05-22). Surface at next alching.

## The rule

When restructuring an information architecture (folder layouts, doc systems, codebases), **lead with the mechanisms that prevent decay, not the visible shape.** The shape is the easy part. Without the mechanisms, any restructure reaccretes into the monolith it replaced.

## The mechanisms that matter (the load-bearing list)

1. **Routing rule.** A one-page table answering *"where does new content land?"* When new gotchas surface, they need a defined home. Without this, content drifts to the path of least resistance — usually one big file.
2. **Size budgets.** Per-file caps. Make creep visible before it's a problem.
3. **Live vs stable separation.** Dated observations (that rot) live in different files from durable knowledge (that doesn't). Mixing them means stable sections get re-edited every time volatile sections do.
4. **Stamps on live entries.** `last-verified: YYYY-MM-DD` + a re-verify probe pointer per dated fact. Otherwise a reader six months in can't tell what's still true.
5. **Audience tags per file.** AI / both / human. So readers stop guessing and writers stop conflating.
6. **Harvest discipline.** Where do mid-work observations land? If there's no answer, they vanish — or they accrete into the wrong file.

## How to apply

1. **Ask what's causing the bloat first.** Why did the current shape grow? Usually one of: no routing rule, no size budgets, no harvest mechanism. The answer determines which mechanisms the restructure needs to install.
2. **Decide which mechanisms apply for this context.** Not all six fit every restructure. For example: if the agent doesn't self-modify, routing rules + harvest live in maintainer sessions, not in the agent's docs. The constraint shapes which mechanisms are load-bearing.
3. **Propose the mechanisms before the shape.** "Live vs stable will be separated. Stamps go on live entries. Each file declares its audience." *Then* propose where files live.
4. **Map the new shape against the mechanisms.** Each file should be classifiable: always-loaded vs on-cue, live vs stable, AI vs analyst vs human. Files that don't classify cleanly are usually doing too many things.
5. **Verify the split doesn't break invariants.** For code: smoke-test (does the import still resolve? does the path anchor still work?). For docs: cross-references updated, audience tags applied, stamps where applicable.

## What this looked like in [[S024_2026-05-21_shipping-agent-rulebook-revamp|S024]]

First pass (mine): mechanical split by content shape — rules / knowledge / skills. The user pushed: *"we're on a good path. But can we do better?"*

Second pass: five mechanisms surfaced. User vetted them; routing rule + size budgets dropped because the shipping-agent doesn't self-modify (those would live in maintainer sessions). Four mechanisms kept: live-vs-stable, always-loaded-vs-on-cue (the actual splitting axis), audience tags, stamps.

The split that landed was substantively similar to the first proposal in folder shape, but the *files now classify cleanly* — every file has a status (LIVE / STABLE), an audience tag, and (where applicable) a `last-verified` stamp + re-verify probe. The mechanisms make the split self-enforcing during future maintenance.

## When to skip this

Skip mechanism-first for cosmetic moves (rename a file, fix a path). The discipline is for **structural** restructures — splits, merges, layer introductions, taxonomy changes. The cost of doing it wrong is months of re-rotting; the cost of slowing down for 10 minutes to think about mechanisms is cheap.

## Anchor

[[S024_2026-05-21_shipping-agent-rulebook-revamp|S024]] T14 (2026-05-22). how_to.md split from 793 → 313 lines. First proposal was mechanical; user push forced the mechanism-first reading. The deeper insight — *"the file structure is the visible part; the mechanism is what keeps it from rotting"* — surfaced only after the second pass.

## Related

- [[layer-routing]] (gielinor `meta/`) — the brain's own routing rule, the inspiration for this.
- The brain's keepsake / bank / spellbook split — the pattern the shipping-agent split mirrors.

# Build order is not presentation order — a deliverable inherits the framing of the sequence it was built in

**Observed:** 2026-06-25, [[S367_ae7565da_orwo-methodology-walkthrough|S367]] (ae7565da) — building the ORWO methodology walkthrough HTML for Niklavs to present.

## What happened

The ORWO tender was built **UPS-first** (Phase-1 was a UPS vertical slice; the whole `production_site='Wolfen'` population correction was *discovered* through UPS). When I wrote the explainer doc, that build history leaked into the framing in **three separate places**, and Niklavs caught each one:

1. §1 population table listed only the UPS book (~126k, AT-first) — omitting that the whole book is ~90% **DHL DE-domestic**. ("why does section 1 focus so much on UPS?")
2. §2 cost-bucket table used entirely UPS invoice vocabulary as if it were the universal cost basis.
3. §5 lane table hid the cross-border tails as "mixed" and labelled FR "UPS competitive" instead of naming the carrier it moves to.

Each was the same root cause: **I narrated the analysis in the order it was constructed, not in the order a reader needs it.** The reader needs the *whole population* first (DHL-dominant), then the slice where the action is (UPS cross-border). The builder's path (UPS-first) is irrelevant to them.

## Why it matters

A from-scratch explainer is not a changelog. The sequence you *discovered* things in — which carrier you validated first, which correction came when — is an artifact of the work, not a feature of the answer. Presenting it that way silently centers whatever you happened to start with, and a sharp reader reads that as "they think UPS is the main story" when UPS is 10% of the book.

## How to apply

When turning an analysis into a deliverable (doc, deck, report): **re-derive the structure from the reader's question, not from the git history.** Before writing, ask "what's the actual shape of the thing?" (here: DHL domestic core + UPS cross-border slice) and lead with that. Then do a deliberate **bias read-through** — scan for any section that leads with the entity/sub-problem you happened to build first where it should lead with the whole. The build is path-dependent; the presentation must not be.

Related: [[2026-06-22-name-the-incumbent-a-switch-exits]] (same arc — naming only the winners hid the UPS exit); the MEMORY entry *restructure-narrative-when-finding-moves-the-decision-line* (rebuild the primary cut, don't bolt on).

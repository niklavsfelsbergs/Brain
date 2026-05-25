# S063 — Shipping-agent board-numbers learnings → rulebook

**Born:** 2026-05-25 (sid 5b1ac700). Jebrim, activated mid-session via "Hey Jebrim" after a dev-brain entry ("Lets develop gielinor") that did no writes and posted no OPEN.

## What this was

Principal handed over a shipping-agent response to a board-prep prompt (five slide-ready Q2 figures for a Thursday logistics review) and asked for the problems / learnings. Became: critique → harvest 8 learnings → implement them as rulebook edits in the shipping-agent repo → naive re-test → commit.

## What happened

- Critiqued the response against the live `how_to.md` rulebook. Strong judgment held (blocked the misleading "costs coming down" narrative via mix-shift decomposition, refused to fabricate a return rate + handed off to the real owner, named the on-time coverage gap). New failure class: coherence *across* a set of numbers, which the rulebook governed per-figure but not as a set.
- Principal confirmed all findings; refined **L1** (scope → explicit 3-option selection: 1. TCG / 2. Both / 3. ORWO) and added **L8** (silent "5 days = on-time" assumption — should state no SLA is set and offer the threshold as a fork).
- Second finding surfaced from the principal's `memory/` question: the shipping-agent's `memory/` layer is **dormant** — bare except its spec, while ~40 flat scratchpad files accrete; the promotion handshake never fires.
- Harvested the consolidated 8 learnings into the Jebrim bank note `bank/notes/projects/shipping-agent-quality-assessment-2026-05-24.md` (2026-05-25 section). Committed brain `941432f`.
- Implemented 6 edits to `how_to.md` (single source of truth — all entry files just `@import` it): rule 12 (numbered scope selector), rule 16 (assumed-SLA fork), rule 4 (uniform integrity stance), new rule 35 (multi-number set pre-flight), rule 2/table (status-code leak), rules 20/27 (memory-promotion trigger), + §0 rule-count fix. Committed shipping-agent `bab905e`.
- Re-tested by spawning a **naive** general-purpose agent to embody the shipping agent on the exact board prompt — kept blind to the 8 changes, to avoid marking my own homework. 6 of 8 rules fired cleanly; the original's three worst failures (silent scope pick + self-contradiction, buried punchline, unexplained identical per-parcel/per-order costs) all fixed.

## Decisions

- The rulebook is shared core (maintainer-edited); editing `how_to.md` directly is a maintainer act, authorized by the principal this session. The Jebrim-side durable capture is the bank note.
- New rule 35 numbered after 34 (not renumbered) with an explicit "every-mode" scope line — renumbering would break the doc's many `rule N` cross-references.
- Did **not** re-guess L1's rule text on the contaminated probe: my test brief told the embodying agent to "proceed without a reply," which suppressed rule 12's present-and-wait behavior. Flagged for a clean live check instead (instrument, don't re-guess).

## Pending external actions

None pending. Two commits landed mid-session: shipping-agent `bab905e`, brain `941432f`. The S063 close commit covers this entry + resume file + harvest draft.

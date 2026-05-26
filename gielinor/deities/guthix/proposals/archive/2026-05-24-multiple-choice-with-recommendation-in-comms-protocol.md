# Proposal: wire the multiple-choice-with-recommendation rule into the comms protocol

**Drafted:** 2026-05-24 (B-006 bankstanding, guthix-a99ae9c2)
**LANDED:** 2026-05-24 (B-006) — subsection added to `meta/communication-protocol.md` on principal authorization, same pass.

## 1. Observation

This round confirmed [[D-025_offer-multiple-choice-with-recommendation]] — the rule that at a genuine branch point the agent offers options as an explicit multiple-choice question *and* names which it recommends and why. The lorebook now records the **decision**, but `meta/communication-protocol.md` — the in-force rulebook read every session — does not carry the **rule**. D-025's own text flags this: *"If promoted, the natural home is a one-line addition to `meta/communication-protocol.md` (which is user-only; raise as a principal edit or a godly proposal during bankstanding, same pattern as [[D-024_scope-git-commits-with-pathspecs-parallel-sessions]]'s follow-up)."*

The behavior is real — this very B-006 pass was conducted in exactly this shape (three `AskUserQuestion` batches, recommended option first, reasoning in the description). But until the protocol file names it, the rule binds by habit and memory, not by the rulebook. Lorebook is the *why-record*; meta is the *instruction*.

## 2. Proposed change

Add a subsection to `gielinor/meta/communication-protocol.md` (suggested placement: after the *Guthix routing* section, before *Intent narration*). Proposed text:

```
## Offer choices as multiple-choice with a recommendation

At a genuine branch point — more than one reasonable way forward — present the
options as an explicit multiple-choice question (via `AskUserQuestion`) rather
than a paragraph of trade-offs, and **always name which option is recommended
and why**. Put the recommended option first, suffix its label "(Recommended)",
and carry the reasoning in its description.

Lower the threshold for offering structured choices — but never offer them
neutrally. A bare menu offloads a decision the agent should hold a view on; the
recommendation is what keeps the agent accountable for that view while leaving
the call to the principal.

Calibration: still skip the question when there's an obvious default or the
answer wouldn't change what the agent does next (the compression rule above
still applies). The recommendation requirement is the guard against using the
tool to dodge having an opinion.

See [[D-025_offer-multiple-choice-with-recommendation]] for the founding decision.
```

## 3. Reasoning

- **Rules that bind live in meta, not lorebook.** A decision recorded only in the lorebook is history; the agent reads `meta/*.md` every session as in-force instruction. Without this edit, the rule depends on the memory entry and habit — exactly the gap that left Guthix routing dormant pre-S038 (operator adoption near zero because the option wasn't reachable through the rulebook).
- **The behavior is already validated.** B-006 ran in this shape end-to-end and it worked well. The edit codifies a proven pattern, not an untested aspiration.
- **Cost to land:** one small edit to a user-only file. No migration, no backfill.

## 4. Scope of impact

- Touches `gielinor/meta/communication-protocol.md` only.
- Applies to **every actor and mode** (players, Guthix, Braindead, unscoped) — consistent with D-025.
- No data migration. No hook change. No other layer affected.

## 5. Alternatives considered

- **Leave it in the lorebook only.** Rejected — that's the gap this proposal fixes; a decision that never reaches the rulebook doesn't bind behavior.
- **Add it to `CLAUDE.md` instead.** Rejected — the communication protocol is the correct home; `CLAUDE.md` already imports it and points there for the full rule.
- **Enforce via a hook.** Rejected — this is a judgment rule ("genuine branch point"), not a mechanically detectable condition. A hook would either misfire or be inert.

## 6. Risk if landed wrong

Low. The main failure mode is over-application — offering multiple-choice for trivial choices with an obvious default. Mitigated by the explicit calibration paragraph (the compression rule still governs) and the "answer wouldn't change what the agent does next" test carried from D-025. If it ever over-fires, the cost is a few unnecessary questions, correctable by tightening the calibration line.

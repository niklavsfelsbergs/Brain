# The grounding-precondition is captured but not firing — it needs a trigger, not another note

**Decision (proposed, B-008 2026-05-26).** Stop treating recurrences of the grounding-precondition miss as new drafts to capture. The lesson is already captured at every level; the gap is that nothing makes it *fire* at the moment it's needed. Pursue a **mechanism** (a trigger), and treat further captures of the same miss as evidence for the mechanism, not as fresh knowledge.

**Observation (the recurrence).** The grounding-precondition — *read the active context and correctly identify the referent before producing substantive output* — is confirmed globally (`examine/confirmed/2026-05-25-grounding-precondition-before-substantive-output.md`, "G1"), promoted at B-007 from two independent player instances, and additionally lives in memory (`feedback_anchor_referent_before_analyzing`, `feedback_check_own_memory_before_working_repo`). Despite all that, the same miss reproduced three more times:

- **S066 (Zezima).** Analyzed a property as "new" before recognising it as S056 apartment #1.
- **S076 (Jebrim).** Grepped only the working repo for "the message I prepared"; it was in his own `bank/notes/`.
- **S095 (Zezima).** Opened the uploaded folio cold and re-derived the whole analysis before recognising it as Gate 2 of the S066 deep-dive.

Zezima's S095 draft named the signal precisely: *"the lesson sitting in memory did not prevent the slip… the failure isn't capture, it's that nothing makes 'check my own notes first' actually fire when a session opens with a continuation cue + an artifact."*

**Why this is the right call.** This is the brain's own *instrument-don't-reguess* / *verify-enforcement-fires* ethos applied to itself: a documented rule that demonstrably doesn't fire is not fixed by documenting it harder. The brain's enforcement surface is **hooks** (`.claude/hooks/`), and its session-entry surface is the **respawn ritual** — those are where a trigger belongs. A fourth confirmed note would be the clutter version of the same mistake.

**What changes in how the agent operates.** On any session/turn opening with a *continuation cue* (`once again`, `again,`, `back to`, `some more`, `afterall`, `the X I prepared/made/built earlier`) or an uploaded artifact in a player's namespace: the first move is to search the active player's `bank/notes/`, `research/`, and `quest-log/` for the subject, map the artifact to where prior work left off, and confirm referent identity — *before* analyzing. "This is new" is a hypothesis to disprove, not a default. The mechanism (below) makes this fire rather than relying on recall.

**Mechanism — drafted as a godly proposal this round.** `deities/guthix/proposals/2026-05-26-grounding-precondition-trigger-hook.md` — a `UserPromptSubmit` hook that detects the cue/artifact and injects a "check your own bank/notes/research first" reminder. The respawn ritual's first-message step is the alternative/complementary surface. Principal lands the proposal (or edits the surface).

**Anchors.** G1 (`examine/confirmed/2026-05-25-grounding-precondition-before-substantive-output.md`); Zezima `examine/confirmed/2026-05-26-read-doc-cold-recurrence.md` (S095); Jebrim `examine/confirmed/2026-05-26-check-own-bank-for-prepared-content.md` (S076); Zezima `2026-05-25-anchor-referenced-subject-before-assuming-its-new.md` (S066). Memory: `feedback_anchor_referent_before_analyzing`, `feedback_check_own_memory_before_working_repo`.

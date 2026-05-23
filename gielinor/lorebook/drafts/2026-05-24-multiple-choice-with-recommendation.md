# Offer choices as multiple-choice with a recommendation and why

**Type:** operating rule (communication). Drafted 2026-05-24 (dev-brain session, sid 89f41770). **Status: draft — awaiting principal promotion.**

**What changed.** When a response reaches a genuine branch point — more than one reasonable way forward — present the options as an explicit **multiple-choice question** rather than prose, and **always name which option I recommend and why**. Lower the threshold for offering structured choices, but never offer them neutrally: each set comes with an opinionated default.

**Why.** Niklavs decides faster from a small labelled option set than from a paragraph of trade-offs, and he wants my judgment *in* the choice, not withheld. A bare menu offloads a decision I should have an opinion on; a recommendation-with-reasoning keeps me accountable for a view while leaving him the call. Pairing the two — structure *and* opinion — is the shape he asked for.

**What triggered it.** Direct user feedback, this session, verbatim: *"I want you to more often give me multiple choice questions but also say which one you recommend and why."* Given alongside the rebuild-from-concepts lesson ([[I-003]] in the dev brain) as a working-preference he wanted recorded.

**Mechanism.** The `AskUserQuestion` tool already supports this — put the recommended option first, suffix its label with "(Recommended)", and carry the *why* in its description. Calibration note: the tool's own guidance says reserve it for decisions where the answer changes what I do next, not for choices with an obvious default. Niklavs' feedback lowers that threshold — offer choices *more* readily — but the recommendation requirement is the guard against using it to dodge having a view.

**What it affects.** No `meta/` file edited yet — this draft proposes the behavior. If promoted, the natural home is a one-line addition to `meta/communication-protocol.md` (which is user-only; raise as a principal edit or a godly proposal during bankstanding, same pattern as [[D-024]]'s follow-up). Applies to every actor and mode (players, Guthix, Braindead, unscoped).

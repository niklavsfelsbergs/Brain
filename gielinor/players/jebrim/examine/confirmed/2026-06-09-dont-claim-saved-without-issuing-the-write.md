# Don't claim "saved to X" without actually issuing the write

**Observation (S195, sid8 1a966d4a).** I told Niklavs "Saved to `research/2026-06-09-pre-departure-prep-checklist.md`" after presenting the prep checklist in chat — but I never called the Write tool for it. Caught it at close-session (step 2 / the pre-commit status scan): the file was MISSING. Three other artifacts that session *were* genuinely written; this one I narrated as saved while only having produced the prose.

**The failure.** Treating "I composed the content in my response" as equivalent to "I persisted it." The save-claim rode along with the chat output instead of being gated on an actual tool call. A reader trusts "saved to X" as a completed action; here it was false, and it left a dangling `[[wikilink]]` from the business-sketch doc.

**Rule.** A completion claim about an artifact ("saved", "wrote", "created X at path") must be backed by the actual tool call *in the same turn*, not by having produced the content in prose. Same family as verify-the-thing / check-real-exit-not-trailing-echo: the artifact existing is the ground truth, the narration is not. When producing multiple artifacts in one session, each "saved" deserves its own Write — and at close, the pre-commit `git status` scan is the backstop that catches the ones that slipped (it did here).

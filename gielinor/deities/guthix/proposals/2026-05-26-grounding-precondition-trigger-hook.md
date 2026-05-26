# Godly proposal — a UserPromptSubmit hook that makes the grounding-precondition fire

**Drafted:** 2026-05-26 (bankstanding B-008). **Status:** active draft for principal review.

## 1. Observation

The grounding-precondition (read active context + confirm referent identity before substantive output) is confirmed globally (`examine/confirmed/.../grounding-precondition...`, "G1"), graduated at B-007 from two independent player instances, and stored in memory (`feedback_anchor_referent_before_analyzing`, `feedback_check_own_memory_before_working_repo`). It still failed three more times since:

- **S066 (Zezima)** — analyzed a flat as "new" that was S056 apartment #1.
- **S076 (Jebrim)** — grepped only the working repo for "the message I prepared"; it was in his own `bank/notes/`.
- **S095 (Zezima)** — re-derived the folio analysis cold before recognising it as Gate 2 of the S066 deep-dive.

Every miss opened with a **continuation cue** (*"once again," "again," "the X I prepared"*) and/or an **uploaded artifact**, and in every case the already-captured lesson did not fire. Capture is saturated; triggering is the gap. (See `lorebook/drafts/2026-05-26-grounding-precondition-needs-a-trigger-not-another-note.md`.)

## 2. Proposed change

Add a `UserPromptSubmit` hook — `.claude/hooks/grounding-cue-reminder.py` — wired in `.claude/settings.json`. On each submitted prompt:

- **Match continuation-cue patterns** (case-insensitive, word-boundaried): `once again`, `again[, ]`, `\bback to\b`, `some more`, `after\s?all`, and prepared-content forms `the .{0,30}\b(prepared|made|wrote|built|created|drafted)\b.{0,20}\b(earlier|before|last time|already)\b`.
- **Best-effort artifact detection** — if the harness exposes attached-file info on the UserPromptSubmit payload, also fire when an artifact is attached. (Flagged uncertain — see §6; the cue match is the load-bearing path.)
- **On match, inject `additionalContext`** (non-blocking) along the lines of:
  > *Grounding cue detected ("{matched}"). Before analyzing: search the active player's `bank/notes/`, `research/`, and `quest-log/` for this subject; map any uploaded artifact to where prior work left off; confirm the referent's identity. Treat "this is new" as a hypothesis to disprove. (G1; recurred S066/S076/S095.)*
- **Scope:** fire only in gielinor player/consultation modes (skip dev-brain — Braindead's construction work has different cue semantics). Cheap, stateless, no model call.

## 3. Reasoning

The brain's enforcement surface is hooks; its other six guarantees are hook-enforced precisely because documentation alone doesn't hold. This is the same lesson turned on a behavioral precondition: a rule that demonstrably doesn't fire (3 reproductions despite global-confirm + memory) wants a mechanism, not a fourth note. `UserPromptSubmit` `additionalContext` is the lightest possible intervention — it nudges at exactly the moment the miss happens (prompt submission with a cue), costs nothing, and blocks nothing.

## 4. Scope of impact

- **New file:** `.claude/hooks/grounding-cue-reminder.py`. **Edit:** `.claude/settings.json` (register the UserPromptSubmit hook).
- **Actors affected:** all gielinor players + consultation (Guthix). Not dev-brain.
- **No migration/backfill.** Additive; G1 and the memory entries stay as the substance the reminder points to.

## 5. Alternatives considered

- **A respawn-ritual first-message step** (scan the opening message for cues, do a self-bank check before accepting input). Complementary, but only covers session *start* — S076's miss was mid-session. The hook covers every turn. Could land both; the hook is the higher-coverage primary.
- **A fourth confirmed note / a sharper rule in `communication-protocol.md`.** Rejected — this is the failure mode itself (documenting harder a rule that doesn't fire).
- **A blocking hook** (refuse the turn until a bank search is logged). Rejected — too heavy, false-positives would be infuriating, and the miss isn't dangerous enough to justify blocking.

## 6. Risk if landed wrong

- **False positives** — genuinely-new asks containing "again"/"more" trigger the reminder. Mitigation: the injection is short, advisory, non-blocking; an unneeded reminder costs one or two lines of context, not a wrong action. Tune patterns if noisy.
- **Artifact detection may be infeasible** — if `UserPromptSubmit` doesn't expose attachment metadata, that half silently no-ops; the cue-match path still delivers most of the value. Verify against Claude Code's actual UserPromptSubmit payload before relying on it (don't assume the field exists — the brain's own *verify-enforcement-fires* lesson).
- **Over-trust** — the reminder could become wallpaper the agent stops reading. Mitigation: keep it terse and only on real matches, so it stays signal.

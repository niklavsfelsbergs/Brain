# D-034 — Close-ritual enforcement (three layers, honest ceiling)

**Date:** 2026-05-28 · **Session:** [[S115_a9fe4749_khaan-failure-receipts-and-hygiene|S115]] · **Actor:** Braindead (dev-brain)

## Context

[[S115_a9fe4749_khaan-failure-receipts-and-hygiene|S115]] closed, then the principal challenged "are you 100% wrapped?" — and three close-session steps had been silently skipped (the `wrapped_up` marker, the load-bearing quest-log `Cascade.`/`Main-brain changes.` lines, and a `git status` discrepancy). Caught only by manually walking the ritual against the filesystem. The principal then asked: **how do we make the close ritual never-skippable — when a conversation is ending, it should be mandatory?**

## The constraint that shapes the answer

**A hook runs a script, not the model.** The close ritual's valuable half — naming the quest, writing the quest-log narrative, harvesting learnings, composing a real commit — needs the model in the loop. Claude Code's `SessionEnd` hook fires when the process is already exiting and, per the docs, runs **async / no-wait** (a hard window-close can kill it before it finishes; file writes *may* land, git *probably* won't). So: *"force the full ritual via a hook" is not achievable.* What is achievable: **make skipping loud and hard while the model is still in the loop, and guarantee a durability/visibility floor when it isn't.**

Also confirmed (Claude Code hooks docs, [[S115_a9fe4749_khaan-failure-receipts-and-hygiene|S115]] via claude-code-guide): `UserPromptSubmit` injects context via `hookSpecificOutput.additionalContext` (30s timeout); `Stop` fires every turn, so it cannot signal end-of-conversation.

## Decision — three layers

1. **Close-completeness gate (in-session, the direct fix).** `developer-braindead/verification/close_check.py --sid8 <sid8>` re-derives the dev close-session steps from ground truth (quest-log + Cascade/Main-brain lines, respawn references the session, CLOSING posted, active-mode unscoped, core artifacts committed) and emits a locked `CLOSE RITUAL INCOMPLETE` banner + the gaps on any FAIL. Bound as **mandatory step 9** of `developer-braindead/spellbook/session-close.md` — run after the commit, before declaring wrapped. Turns "I think I closed" into "the checklist passed." This is the mechanized antidote to the [[S115_a9fe4749_khaan-failure-receipts-and-hygiene|S115]] miss; it reuses the Khaan item-5 verification harness and item-2 banner pattern.
2. **End-cue reminder (in-session nudge).** `gielinor/.claude/hooks/close-cue-reminder.py` (`UserPromptSubmit`) — on a winding-down cue ("lets close", "wrap up", "hand this over to the next session", …) it injects a non-blocking reminder to run the close ritual + its gate before stopping. The **exit-side symmetry** of `require-open-on-entry.py` ([[D-033_positive_enforcement_gate_open_on_entry|D-033]], the entry gate). Fires for every actor (the dev close is exactly what broke). Registered in root `settings.json` next to `grounding-cue-reminder.py` (root-only — reminders should fire once, not double-inject).
3. **SessionEnd safety-net (best-effort floor).** `gielinor/.claude/hooks/session-end-safety-net.py` (`SessionEnd`) — if the session posted an OPEN but no CLOSING, append an auto-CLOSING **stub** to the relevant comms channel so siblings + the next respawn know to reconcile. **Deliberately does NOT commit** — an unattended commit in this shared-index, parallel-session repo is the hazard that once swept a sibling's staged file (dev S118). Skips `reason=='clear'/'resume'` (not true ends). Registered in root `settings.json` SessionEnd.

## The honest ceiling

- Layers 1+2 make skipping **loud and hard on a graceful end** (model in the loop).
- Layer 3 gives a **best-effort visibility floor** on a graceful `/exit`/logout — but **cannot be relied on** for a hard window-close (async/no-wait). It is a net, not a guarantee, and its header says so.
- The **cognitive** half of the ritual can *never* be hook-forced once the window is closed; the durable guarantee there is the in-session per-turn quest-log + OPEN, recovered by the **next respawn's reconciliation** (which already exists). Layer 3 just makes that recovery louder.

So the guarantee is: **"verified-complete on a deliberate close (1), reminded if you start to drift (2), and visibly flagged for reconciliation if you vanish (3)"** — not "the model is forced to think at exit," which is impossible.

## Scope / follow-ons

- `close_check.py` is scoped to the **dev-brain** close ritual (the one [[S115_a9fe4749_khaan-failure-receipts-and-hygiene|S115]] botched). The **gielinor** `close-session.md` (player close) is a parallel future extension — same shape, different steps.
- Verified empirically this session: `close_check` reports the realistic mix mid-session and would go all-PASS at a clean close; `close-cue-reminder` fires on cues / silent on negatives incl. the meta-question "how can we ensure the close ritual is never skipped"; `session-end-safety-net` appends the stub on an unmatched OPEN (temp-comms e2e), skips `clear`, and no-ops when a CLOSING exists.

## Related

[[D-033_positive_enforcement_gate_open_on_entry|D-033]] (the entry gate this mirrors at exit), [[S115_a9fe4749_khaan-failure-receipts-and-hygiene|S115]] (the Khaan items 2/5 primitives reused), `developer-braindead/spellbook/session-close.md` (the ritual now gated), `gielinor/spellbook/failure-banners.md` (the banner doctrine).

# close-session — session-end procedure

The procedure the agent runs before the principal closes the conversation. Codifies wrap-up so the next session lands clean.

The quest-log entry is the source of truth for what's open; close-session is what makes sure the entry actually reflects reality before the substrate is left to disk.

## When this fires

Triggered by the principal at the end of a session — typical cues:

- "lets close the session" / "let's close"
- "close the session"
- "wrap up" / "let's wrap"

Strict matching is *not* required for action cues (unlike player address). A close-cue near the end of a session is taken as the trigger. If unclear, ask.

The ritual covers **all players** with non-empty `quest-log/in-progress/`, not just the currently active one. Mid-session player switches may have left a previous player's state mid-flight — close-session catches that.

## SNNN — session ID

Each session that runs close-session gets a sequential ID: `S001`, `S002`, etc. Sequence is **global across all players**.

**Determine SNNN at close-time:**

1. Glob across `players/*/quest-log/` (in-progress + completed) and `players/*/quest-log/archive/` for files matching `^S\d{3}_`.
2. Take the max numeric. Next SNNN = max + 1. First-ever close = `S001`.

**Apply SNNN:**

- A quest file that has **never been closed before** gets its SNNN prepended now (this is its birth-session ID). Filename: `S{NNN}_{YYYY-MM-DD}_{slug}.md`.
- A quest file already carrying an SNNN keeps it. The SNNN identifies birth, not last touch.
- Files moved to `completed/` keep their birth-SNNN prefix.

## Steps

For **each player** with a non-empty `quest-log/in-progress/`, run steps 1-6 in that player's namespace. Then run global steps 7-10.

### 0. Spawn-decision — principal-self or gnome?

Before walking the steps, evaluate the gnome spawn heuristic for session-close (per `spellbook/skills/gnomes.md`):

- **> 15 turns** in the active session, OR
- **≥ 2 players touched** in the session, OR
- **> 5 pending drafts** to triage at close-time.

If any fires, spawn a **gnome** with the session-close brief:

- Ritual: `session-close`.
- Players in scope: all players with non-empty `quest-log/in-progress/`.
- Inputs: which threshold(s) fired (turn count, players touched, drafts pending).

The gnome runs steps 1–9 and returns the structured report (per `spellbook/skills/gnomes.md`). The principal reviews the report and approves any proposals before the session actually ends.

If no threshold fires (light session — typically **< 10 turns AND read-only**), run steps 1–9 personally. Light closes stay with the principal so the procedure doesn't drift.

Skip the special-case unscoped step 10 if a gnome ran the close — the gnome handles inbox writes via its own step coverage. If principal-self ran, step 10 below applies.

### 1. Reconcile pending actions

Every external action logged as `pending` in the quest-log entry must be marked `completed` or `failed` before close. If unclear what actually happened, ask the principal before marking. Never close with a dangling `pending` — that's the crash-recovery signal and will fire reconciliation on next session start unnecessarily.

If there are no pending actions, write an explicit "No pending external actions." line so the state is unambiguous.

### 2. Persist chat-only drafts

Anything that was drafted in conversation this session but isn't yet on disk:

- **If the principal approved it** → write it to its intended location.
- **If still awaiting approval** → embed the full draft inside the quest-log entry under a `## Pending drafts` section so it survives the restart. The reconciliation prompt on next session will surface it.

This closes the "chat-only state is volatile" gap. Drafts that exist only in conversation are lost on session close otherwise.

### 3. Write resume state to `inventory/<quest-slug>-resume.md`

**Per `gielinor/meta/layer-routing.md`, resume state lives in inventory, not in the quest log.** For each in-progress quest this player owns, write (or overwrite) `players/<active>/inventory/<quest-slug>-resume.md` with the next-session prompt:

- **Status:** explicit (`in-progress` or `done`).
- **Where we are:** one sentence on current state.
- **Next concrete step:** one paragraph the next session can act on. If the next step is blocked on the principal, phrase it as a question, not as an action.
- **Files / paths to read first:** bulleted, ordered by load priority.
- **Pending drafts:** populated by step 2 if any.

These sections are what `respawn.md`'s reconciliation prompt reads to surface the next move. The respawn ritual reads `inventory/*-resume.md` as the resume foreground; without this file, the next respawn has nothing to surface beyond the turn log.

**Compact the quest log itself.** Strip any resume-state sections that historically lived at the top of the quest-log file (`Status`, `Where we are`, `Next concrete step`, `Files to read first`) — they belong in inventory now. The quest log keeps narrative + decisions + turn-by-turn log + Pending drafts (if any). Per-turn history is reference; the inventory file is foreground.

**Migration note (sessions opened before 2026-05-21).** Existing in-progress quest files may carry the resume sections at the top. On the first close-session pass after 2026-05-21, lift those sections into a new `inventory/<quest-slug>-resume.md` file, then trim them from the quest log. One-time per quest.

### 4. Decide: continue or complete the **quest** (not the session)

The trigger for moving to `completed/` is **quest close**, not session close. Session close is the moment this ritual runs; quest close is whether the deliverable is shipped or the thread has reached its resting point.

- **Continue (default for multi-session quests)** → leave the file in `quest-log/in-progress/`. Apply SNNN prefix per the SNNN rule above if not already present. Inventory resume file (step 3) stays.
- **Complete** → move the file to `quest-log/completed/`. Apply SNNN prefix in the move if not already present. **Also move the corresponding `inventory/<quest-slug>-resume.md` to `inventory/archive/<quest-slug>-resume.md`** (or just remove if the quest is fully closed and the resume info is no longer needed — the quest-log entry in `completed/` is the durable record).

A quest is done when its "Next concrete step" is "none — quest closed." Multi-session quests stay in `in-progress/` across many closes; the existence of an inventory resume file is the cheap signal that more work is queued.

### 5. Inventory hygiene

The player's `inventory/` is volatile by design — but as of 2026-05-21 it's also the **primary resume surface**. The hygiene rule splits accordingly:

- **`<quest-slug>-resume.md` files for in-flight quests** — must remain populated and current. These are what respawn reads. Do not flush; step 3 just wrote/updated them.
- **Resume files for closed quests** — moved to `inventory/archive/` (or removed) in step 4 above.
- **Other inventory items (free-form working memory)** — if stale (work landed or was abandoned), flush them. If actively carried across sessions and not quest-specific, consider promoting to `bank/drafts/notes/` instead.

Soft check: if `quest-log/in-progress/` has files but `inventory/` has no `*-resume.md` files for them, that's a step-3 failure — surface the gap and fix before continuing.

### 6. Observation harvest

After the entry is tightened (step 3), skim what happened this session and convert anything durable into draft form. This is **Pump 2** — the per-close population pump that keeps identity layers and bank growing. See [[D-012]] (dev brain) for the rationale.

**Skim surface.**

- Fresh turns added to in-progress quest-log entries this session.
- The resume sections (**Where we are**, **Next concrete step**) of all in-progress quests touched this session.

The agent judges per-item stability — "is this observation likely to still be true next session, or is it still shifting?" Stable findings become drafts; shifting content stays in the turn log.

**The four harvest questions.**

1. *"Did any work crystallize into a reusable concept this session?"* → write to `players/<active>/bank/drafts/notes/<topic>/<slug>.md`.
2. *"Did I notice something about myself or how I operate?"* → write to `players/<active>/examine/drafts/<YYYY-MM-DD>-<slug>.md`. Global (`gielinor/examine/drafts/`) only if the observation is clearly cross-player and the principal cues it.
3. *"Did I notice something about Niklavs through this work?"* → write to `players/<active>/niksis8_character/drafts/<YYYY-MM-DD>-<slug>.md`. Global routing handled by bankstanding, not here.
4. *"Did anything earn a pin?"* → write to `players/<active>/keepsake/proposals/<YYYY-MM-DD>-<slug>.md`. Almost always no.

**Discipline.**

- **Cap 1–5 drafts per session.** Bias to less. Empty-set is a valid and common answer. A session where nothing earned its way produces zero drafts; this is healthy.
- **Observation-backed only.** Drafts must cite the specific turn or moment that produced them, per `gielinor/meta/drafts-mechanics.md`. Aspirational drafts ("I should be more careful about X" with no anchor) fail the discipline.
- **Player-scope first.** Per [[D-012]] (D2=B), drafts land in the active player's namespace by default. Cross-player promotion is bankstanding's job.

**Unscoped sessions.** If the session was unscoped (no player ever activated), harvest writes to `gielinor/examine/drafts/`, `gielinor/niksis8/drafts/`, `gielinor/lorebook/drafts/`, and `gielinor/keepsake/proposals/` directly. Bank-note candidates have no global home — write them to `players/inbox/<YYYY-MM-DD>-<slug>.md` for bankstanding to triage.

**Skill graduation is NOT done here.** That's a Pump 3 (alching/bankstanding) job. Close-session harvest captures observations; alching converts patterns into named skills.

### 7. Surface drafts across global + per-player layers

If this session created any `examine/drafts/`, `niksis8/drafts/`, `niksis8_character/drafts/`, `lorebook/drafts/`, `keepsake/proposals/`, or `bank/drafts/notes/` entries (including this session's harvest output from step 6), **surface them now** — one line per draft, grouped by layer. The principal triages on the spot or defers to `/drafts`.

This is an additional surface event beyond what `meta/drafts-mechanics.md` already specs (`/drafts`, bankstanding, blocking action). Close-session is now a fourth.

### 8. Commit

Always commit at session close (unless the working tree is genuinely clean — in which case skip and note it).

**Pre-commit soft-block.** Before staging, run one more check: for each player with files in `quest-log/in-progress/`, confirm a matching `inventory/<quest-slug>-resume.md` exists and is non-empty. If any quest is missing its resume file, **do not auto-commit** — surface the gap, ask the principal whether to (a) write the missing resume file before commit, (b) commit anyway and flag it as deliberate, or (c) abandon the quest into `quest-log/archive/in-progress/`. This is the inventory-empty enforcement clause; it's a proposal-not-a-block (principal can override).

- **Stage scoped.** Prefer `git add gielinor/players/<name>/quest-log/ ...specific paths` over `git add -A`. Verify with `git status` before committing.
- **Subject:** `S{NNN}: <one-line summary>`. Under 70 chars.
- **Body:** short paragraphs grouped by area of change. Past tense. Why over what.
- **Trailer:** `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` (or current model identity).
- **Never `--no-verify` or `--no-gpg-sign`.** If a hook fails, fix and create a new commit — do not amend the rejected one.
- **Never push.** Push is a separate, explicit principal action.

The principal has authorised the close-session commit by making it part of this ritual. The standing rule "always ask before committing" (`~/.claude/CLAUDE.md`) is **overridden inside this step**. It still applies outside.

If the tree is clean — read-only session, audit, discussion — skip the commit silently and note "no commit; tree clean" in the close.

### 9. State the close

One or two sentences back to the principal. Include:

- The SNNN.
- Which players had quest-log entries touched.
- The commit hash (or "no commit; tree clean").

Then wait. The principal closes the conversation.

### 10. Special case: unscoped session

If the session was unscoped (no player ever activated), there is no per-player quest-log to close. The agent writes a single entry to `players/inbox/S{NNN}_{YYYY-MM-DD}_unscoped.md` capturing what happened. Same SNNN rule. Bankstanding triages the inbox later.

## Related

- `respawn.md` — the receiving side. The reconciliation prompt fires on next session start.
- `meta/death-and-spawn.md` — for the recovery model that close-session feeds into.
- `meta/drafts-mechanics.md` — close-session is now a fourth draft-surfacing event.
- `developer-braindead/spellbook/session-close.md` — the dev-brain twin (single-track, rolling `respawn.md` instead of per-player quest-log entries).

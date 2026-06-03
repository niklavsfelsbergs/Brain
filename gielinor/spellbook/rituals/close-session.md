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

- A quest file that has **never been closed before** gets its SNNN prepended now (this is its birth-session ID). Filename: `S{NNN}_{sid8}_{slug}.md` per [[D-024_scope-git-commits-with-pathspecs-parallel-sessions]] (dev brain) — the `sid8` (first 8 chars of `CLAUDE_CODE_SESSION_ID`) disambiguates parallel-session SNNN-allocation races. Two sessions racing to S044 both succeed with different sid8 suffixes; SNNN drifts from unique-key to approximate-temporal-ordering, which is acceptable.
- A quest file already carrying an SNNN keeps it. The SNNN identifies birth, not last touch. **Legacy filenames** (`S{NNN}_{YYYY-MM-DD}_{slug}.md` from before [[D-024_scope-git-commits-with-pathspecs-parallel-sessions]]) keep their existing shape — no renaming pass.
- Files moved to `completed/` keep their birth-SNNN prefix.

## Steps

For **each player** with a non-empty `quest-log/in-progress/`, run steps 1-6 in that player's namespace. Then run global steps 7-12.

**Read `meta/write-rules.md` before the harvest pump (steps 2 / 6 / 7).** It left the eager `@import` chain (§X Stage B), and close-session is one of its re-triggers — the harvest writes only to `drafts/` and `proposals/` (no `confirmed/` promotions, no `keepsake/current.md` pins), which is exactly the discipline the write-reach table fixes.

**First, before any step (switchboard, S141).** As the *first* action of the close, write `closing` to `.claude/intent/<sid8>.mode` at the brain root (`<sid8>` = first 8 chars of `CLAUDE_CODE_SESSION_ID`). This flips the session's switchboard row to `WRAPPING UP` for the duration of the wrap — the mid-wrap phase, distinct from the `WRAPPED UP` that the final *Switchboard marker* step sets once everything's done. If the close pauses for a graduation veto or commit nod, the row reads `YOUR MOVE · wrapping up`. Switchboard concern only, not architecturally enforced; if skipped, the row just stays `BUSY` until the final marker.

### 0. Spawn-decision — principal-self or gnome?

Before walking the steps, evaluate the gnome spawn heuristic for session-close (per `spellbook/skills/spawning-gnomes.md`):

- **> 15 turns** in the active session, OR
- **≥ 2 players touched** in the session, OR
- **> 5 pending drafts** to triage at close-time.

If any fires, spawn a **gnome** with the session-close brief:

- Ritual: `session-close`.
- Players in scope: all players with non-empty `quest-log/in-progress/`.
- Inputs: which threshold(s) fired (turn count, players touched, drafts pending).

The gnome runs steps 1–11 and returns the structured report (per `spellbook/skills/spawning-gnomes.md`). The principal reviews the report and approves any proposals before the session actually ends.

If no threshold fires (light session — typically **< 10 turns AND read-only**), run steps 1–11 personally. Light closes stay with the principal so the procedure doesn't drift.

Skip the special-case unscoped step 12 if a gnome ran the close — the gnome handles inbox writes via its own step coverage. If principal-self ran, step 12 below applies.

### 1. Reconcile pending actions

Every external action logged as `pending` in the quest-log entry must be marked `completed` or `failed` before close. If unclear what actually happened, ask the principal before marking. Never close with a dangling `pending` — that's the crash-recovery signal and will fire reconciliation on next session start unnecessarily.

If there are no pending actions, write an explicit "No pending external actions." line so the state is unambiguous.

### 2. Persist chat-only drafts

Anything that was drafted in conversation this session but isn't yet on disk:

- **If the principal approved it** → write it to its intended location.
- **If still awaiting approval** → embed the full draft inside the quest-log entry under a `## Pending drafts` section so it survives the restart. The reconciliation prompt on next session will surface it.

This closes the "chat-only state is volatile" gap. Drafts that exist only in conversation are lost on session close otherwise.

### 3. Write resume state to `inventory/<quest-slug>-resume__<sid8>.md`

**Per `gielinor/meta/layer-routing.md`, resume state lives in inventory, not in the quest log.** For each in-progress quest this player owns, write (or overwrite) `players/<active>/inventory/<quest-slug>-resume__<sid8>.md` (where `<sid8>` is the first 8 chars of `CLAUDE_CODE_SESSION_ID`, per [[D-024_scope-git-commits-with-pathspecs-parallel-sessions]] dev brain) with the next-session prompt:

- **Status:** explicit (`in-progress` or `done`).
- **Where we are:** one sentence on current state.
- **Next concrete step:** one paragraph the next session can act on. If the next step is blocked on the principal, phrase it as a question, not as an action.
- **Files / paths to read first:** bulleted, ordered by load priority.
- **Pending drafts:** populated by step 2 if any.

**Freshness header (top of file).** Open the resume file with a machine-readable header so the next respawn can judge whether the state still fits the task it's resuming (Khaan item 6, dev brain S118; see `inventory/_about.md` for the full convention):

```
---
quest: SNNN_<slug>      # the quest-log entry this resume serves (or topic slug if multi-session)
sid8: <sid8>            # first 8 chars of CLAUDE_CODE_SESSION_ID — this session
ts: YYYY-MM-DD HH:MM    # now (last-write time)
open_dep: none          # or a one-line name of what blocks closing (player-declared; feeds D-029 graduation)
---
```

No cryptographic hash — the quest/sid8/ts fields **are** the identity check (a `sha256(prompt)` stamp would false-trip every turn, the brittleness that held Khaan item G). **Set `open_dep` from what the session actually leaves open:** `none` if the deliverable shipped with nothing pending, else a one-line name of the blocker (an awaiting-sign-off, an external dependency, a follow-up another actor owns). This is the field step 4's graduation scan reads — declaring it here is the player's cheap half of the clerk-not-nanny split (§R.2, dev brain 2026-05-30). **Migration:** an existing headerless resume gets the header on its next close — this step overwrites resume files each pass — mirroring the [[D-024_scope-git-commits-with-pathspecs-parallel-sessions]] sid8-suffix migration.

These sections are what `respawn.md`'s reconciliation prompt reads to surface the next move. The respawn ritual reads inventory files for the active player as the resume foreground; without this file, the next respawn has nothing to surface beyond the turn log.

**Compact the quest log itself.** Strip any resume-state sections that historically lived at the top of the quest-log file (`Status`, `Where we are`, `Next concrete step`, `Files to read first`) — they belong in inventory now. The quest log keeps narrative + decisions + turn-by-turn log + Pending drafts (if any). Per-turn history is reference; the inventory file is foreground.

**Migration note (sessions opened before 2026-05-21).** Existing in-progress quest files may carry the resume sections at the top. On the first close-session pass after 2026-05-21, lift those sections into a new `inventory/<quest-slug>-resume__<sid8>.md` file, then trim them from the quest log. One-time per quest.

**Migration note (sessions opened before [[D-024_scope-git-commits-with-pathspecs-parallel-sessions]], 2026-05-22).** Pre-existing `inventory/<quest-slug>-resume.md` files (no sid8 suffix) stay readable — respawn step 6.i treats them as own-session state. On the next close-session for that quest, write the suffixed shape `<quest-slug>-resume__<sid8>.md`; the unsuffixed predecessor can be moved to `inventory/archive/` once the suffixed version is the live resume surface.

### 4. Decide: continue or complete the **quest** (not the session)

The trigger for moving to `completed/` is **quest close**, not session close. Session close is the moment this ritual runs; quest close is whether the deliverable is shipped or the thread has reached its resting point.

- **Continue (default for multi-session quests)** → leave the file in `quest-log/in-progress/`. Apply SNNN prefix per the SNNN rule above if not already present. Inventory resume file (step 3) stays.
- **Complete** → move the file to `quest-log/completed/`. Apply SNNN prefix in the move if not already present. **Also move the corresponding `inventory/<quest-slug>-resume.md` to `inventory/archive/<quest-slug>-resume.md`** (or just remove if the quest is fully closed and the resume info is no longer needed — the quest-log entry in `completed/` is the durable record).

A quest is done when its "Next concrete step" is "none — quest closed." Multi-session quests stay in `in-progress/` across many closes; the existence of an inventory resume file is the cheap signal that more work is queued.

**Agent-initiative scan for stale-done quests.** Before defaulting to "continue," the agent scans **every** in-flight quest the active player owns (not just the ones touched this session) for done-but-not-moved signal:

- "Pending external actions" line reads *"None pending."* (or equivalent).
- Last few turns / last decision line read as shipping, completing, delivering — not as handing-off or carrying-forward.
- Inventory resume file (if present) status reads `done` or describes a clean ship.
- No fresh activity since a prior session, AND this session didn't reopen it.

For each quest that fires this signal, **classify it by ambiguity** ([[D-029_auto-graduate-unambiguous-complete-ready-quests]]). **Read the resume file's `open_dep` header field first** (the player's declaration, `inventory/_about.md`); fall back to inferring from the quest body only when the field is absent (legacy resumes):

- **Unambiguous** — the CLOSING / resume records the deliverable **shipped + committed** *and* `open_dep: none` (legacy: no open dependency inferable from the body). → **Graduate it in this close without a separate y/n.** Execute the complete-flow above, then report the moves as one vetoable batch: *"Graduated S114/S115/S117 → completed/ (shipped+committed, no open dep). Veto any to carry forward."* An un-vetoed move stands; a veto reverses it (`git mv` back).
- **Ambiguous** — `open_dep` names a blocker, or (legacy) a stated open dependency, a "done but pending principal/external action," or any uncertainty about whether it's truly closed. → Propose for explicit approval as a batch with a one-line reason each; the principal approves per-line (`1y 2y 3n`) or in bulk (`all y`). Do **not** auto-move. Per approval: execute the complete-flow above.

**Why this exists.** Born 2026-05-22 (S038 brain-underutilization fix). Before this scan, the principal had to remember to cue "this quest is done" per-quest, which they didn't — Jebrim accumulated 5 stale-done quests over 18 in-progress entries before bulk cleanup. The agent has full read of each quest body and the resume file; it can propose the moves the principal would have eventually cued.

**Boundary.** Auto-graduation is limited to the **unambiguous shipped+committed+no-open-dep** case and is always reported as a vetoable batch — never silent. Anything with a stated open dependency or any ambiguity stays propose-and-confirm. The agent never auto-*completes the underlying work*; it only moves a quest the CLOSING already declared finished, and the no-deletes guarantee makes any wrong move a `git mv` away from reversal. ([[D-029_auto-graduate-unambiguous-complete-ready-quests]] split the prior "propose only, approval every time" gate, which D-026 left in place and which rapid same-terminal iteration kept skipping — letting `in-progress/` reach 15 twice then 22 at B-010.)

**Default is move, not defer ([[D-026_graduate-complete-ready-quests-in-session]]).** A quest that reads complete-ready is graduated in *this* close — the one that finishes it — not punted with "propose →completed/ next session." The cross-session deferral is exactly what let Jebrim's `in-progress/` reach 15 twice (B-004, B-007): the proposal kept getting written into the CLOSING instead of resolved. Surface complete-ready quests for approval *now*; absent a positive reason to carry one forward (genuine ambiguity, or a named open dependency), move it. "Leaving open: propose →completed/ next session" is no longer an acceptable CLOSING line — either it's open with a stated reason, or it graduates this session. Note the failure mode this guards (per the same round's probe-design lesson): the stale-done scan above already *existed* and still didn't fire reliably — the lever is making "move" the default action, not adding more words. [[D-029_auto-graduate-unambiguous-complete-ready-quests]] (B-010) finished the job D-026 started: making the move the default *wording* wasn't enough while the per-quest approval gate remained — so the unambiguous case now auto-graduates with after-the-fact veto, and only the ambiguous case waits on a y/n.

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
5. *"Did the principal correct me, push back on a judgment, or did something I did this session prove wrong / get reverted / surface a non-obvious failure mode?"* → the **highest-signal** learnings. Capture the specific moment as a self-observation in `players/<active>/examine/drafts/<YYYY-MM-DD>-<slug>.md` (or `gielinor/examine/drafts/` if clearly cross-player). If the lesson generalizes beyond this player and this task — a working-style or judgment lesson — **also** write it to the cross-conversation memory at `~/.claude/projects/.../memory/` per that system's protocol (one fact per file; update `MEMORY.md`). **This question is exempt from the empty-set bias below: if a correction, reverted change, or caught misjudgment happened this session, it MUST produce a captured learning.** Born 2026-05-24 — the principal directed that wrap-ups always harvest learnings from scenarios like the [[S083]] (dev brain) regression he caught.

**Discipline.**

- **Cap 1–5 drafts per session.** Bias to less. Empty-set is a valid and common answer for questions 1–4. A session where nothing crystallized produces zero of those; this is healthy. **Question 5 (corrections/reverts/caught misjudgments) is the exception** — if one happened, it must produce a learning regardless of the cap.
- **Observation-backed only.** Drafts must cite the specific turn or moment that produced them, per `gielinor/meta/drafts-mechanics.md`. Aspirational drafts ("I should be more careful about X" with no anchor) fail the discipline.
- **Player-scope first.** Per [[D-012]] (D2=B), drafts land in the active player's namespace by default. Cross-player promotion is bankstanding's job.

**Unscoped sessions.** If the session was unscoped (no player ever activated), harvest writes to `gielinor/examine/drafts/`, `gielinor/niksis8/drafts/`, `gielinor/lorebook/drafts/`, and `gielinor/keepsake/proposals/` directly. Bank-note candidates have no global home — write them to `players/inbox/<YYYY-MM-DD>-<slug>.md` for bankstanding to triage.

**Skill graduation is NOT done here.** That's a Pump 3 (alching/bankstanding) job. Close-session harvest captures observations; alching converts patterns into named skills.

### 7. Surface drafts across global + per-player layers

If this session created any `examine/drafts/`, `niksis8/drafts/`, `niksis8_character/drafts/`, `lorebook/drafts/`, `keepsake/proposals/`, or `bank/drafts/notes/` entries (including this session's harvest output from step 6), **surface them now** — one line per draft, grouped by layer. The principal triages on the spot or defers to `/drafts`.

This is an additional surface event beyond what `meta/drafts-mechanics.md` already specs (`/drafts`, bankstanding, blocking action). Close-session is now a fourth.

### 8. Post `CLOSING` to `gielinor/comms/active.md`

Per [[D-024_scope-git-commits-with-pathspecs-parallel-sessions]] (dev brain) and `comms/_about.md`. For each player who posted an `OPEN` (or `UPDATE`) earlier this session and has not yet posted a `CLOSING`, append now — one entry per actor identity that opened. Skip for Guthix consultation sessions that didn't open (consultation default is chat-only, no comms post). Header:

```
[YYYY-MM-DD HH:MM] <actor>-<sid8> CLOSING
```

Body:

- `Completed:` — what shipped this session, in one or two lines.
- `Leaving open:` — the carried-forward items (typically what step 3's inventory resume files describe in more detail).

If the session opened multiple actors (mid-session player switch, mini-respawn), each one that has an unmatched `OPEN` gets its own `CLOSING`. The dev-brain twin runs the same step against its own `developer-braindead/comms/active.md`.

If the session never posted an `OPEN` (trivially scoped — one-off read, no writes), skip this step. Don't post bare `CLOSING` entries with no matching open.

### 9. Commit

Always commit at session close (unless the working tree is genuinely clean — in which case skip and note it).

**Pre-commit soft-block.** Before staging, run two checks:

1. **Missing inventory resume files.** For each player with files in `quest-log/in-progress/`, confirm a matching `inventory/<quest-slug>-resume__<sid8>.md` (or legacy `inventory/<quest-slug>-resume.md` for pre-[[D-024_scope-git-commits-with-pathspecs-parallel-sessions]] quests) exists and is non-empty. If any quest is missing its resume file, **do not auto-commit** — surface the gap, ask the principal whether to (a) write the missing resume file before commit, (b) commit anyway and flag it as deliberate, or (c) abandon the quest into `quest-log/archive/in-progress/`. This is the inventory-empty enforcement clause; it's a proposal-not-a-block (principal can override).
2. **Orphan untracked quest-log files.** Run `git status --short gielinor/players/*/quest-log/ developer-braindead/quest-log/` and grep for lines starting with `??`. Untracked quest-log files are usually quest narratives written in prior sessions that close-session's `git add` missed — their content is already authoritative on disk but not versioned. **Surface these as part of this commit's scope** unless the principal explicitly excludes one. Born 2026-05-22 (S038) after a `git status` audit revealed `S031_*` and `S034_g2_*` had lived untracked for sessions.

- **Stage scoped.** Prefer `git add gielinor/players/<name>/quest-log/ ...specific paths` over `git add -A`. Verify with `git status` before committing.
- **Subject:** `S{NNN}: <one-line summary>`. Under 70 chars.
- **Body:** short paragraphs grouped by area of change. Past tense. Why over what.
- **Trailer:** `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` (or current model identity).
- **Never `--no-verify` or `--no-gpg-sign`.** If a hook fails, fix and create a new commit — do not amend the rejected one.
- **Never push.** Push is a separate, explicit principal action.

This close commit is pre-authorized — see the brain-wide **Commit policy** (`CLAUDE.md` → *Commit policy*, the canonical statement). The principal authorised it by making it part of this ritual, so **don't ask before committing here**; the standing "always ask before committing" rule applies everywhere outside this step.

If the tree is clean — read-only session, audit, discussion — skip the commit silently and note "no commit; tree clean" in the close.

### 10. Run the close-completeness gate

Before declaring the session wrapped, run:

```
python developer-braindead/verification/close_check.py --ritual player --sid8 <sid8>
```

(`<sid8>` = first 8 chars of `CLAUDE_CODE_SESSION_ID`.) It re-derives the load-bearing player-close steps from **ground truth**, keyed by sid8 across `players/*/`:

- **CLOSING posted** — `gielinor/comms/active.md` carries a `<actor>-<sid8> CLOSING` for any actor that posted an `OPEN` this session (step 8; skipped if no `OPEN`).
- **quest-log present** — a `players/*/quest-log/{in-progress,completed}/*<sid8>*.md` exists, or a `players/inbox/*<sid8>*.md` for an unscoped session (step 2 / step 12).
- **inventory resume present** — every player with an in-progress quest for this sid8 has a matching `inventory/*-resume__<sid8>.md` (step 3, the step-9 inventory-empty enforcement clause mechanized).
- **resume freshness header** — every resume file for this sid8 carries the `quest`/`sid8`/`ts` header (step 3; Khaan item 6, S118). Bounded to the current sid8 so legacy headerless resumes never false-trip.
- **core artifacts committed** — those quest + resume files are git-clean and not orphan-untracked (step 9).

**On any FAIL it prints the locked `CLOSE RITUAL INCOMPLETE` banner + the specific gaps — fix them, re-commit if needed, and re-run until it exits 0. Do NOT declare the session wrapped or write the `wrapped_up` marker on a FAIL.** This is the mechanized guard against a premature done-claim — the gielinor-player half of [[D-034_close_ritual_enforcement|D-034]], parallel to the dev-brain close's own step 9 (the dev twin, `developer-braindead/spellbook/session-close.md`). It turns "I think I closed" into "the checklist passed." The check is **per-player and multi-player** (a session that switched players is verified for each), has no `respawn.md` arm (gielinor resume state lives in inventory), and does not check the dev-brain `active-mode.txt` marker. Added 2026-05-29 (S117); the resume-freshness-header arm added the same day (S118, Khaan item 6).

If the close ran via a **gnome**, the gnome runs this gate as part of steps 1–11 and surfaces a FAIL in its report; the principal does not declare the session wrapped until it passes.

### 11. State the close

One or two sentences back to the principal. Include:

- The SNNN.
- Which players had quest-log entries touched.
- The commit hash (or "no commit; tree clean").

Then wait. The principal closes the conversation.

**Switchboard marker (visualizer concern).** As the **final action** — after the commit and the close statement, whether the close ran principal-self or via a gnome — overwrite `.claude/intent/<sid8>.mode` at the brain root (`<sid8>` = first 8 chars of `CLAUDE_CODE_SESSION_ID`) with `wrapped_up` (replacing the `closing` marker the *First, before any step* note wrote). This flips the session's switchboard row from `WRAPPING UP` (mid-wrap) to `WRAPPED UP` — "done, terminal still open" — distinct from `ENDED` (process gone). `status-sidecar.py` reads the marker on this turn's `Stop` event and holds the `wrapped_up` state until the process actually ends. If the principal sends a fresh prompt instead of closing the conversation, the marker auto-clears and the session resumes as `working`. Not architecturally enforced — a missing marker just leaves the row reading `WAITING`/`IDLE` as before.

### 12. Special case: unscoped session

If the session was unscoped (no player ever activated), there is no per-player quest-log to close. The agent writes a single entry to `players/inbox/S{NNN}_{sid8}_unscoped.md` capturing what happened. Same SNNN rule. Bankstanding triages the inbox later. Skip step 8 — wisp sessions don't post to comms.

## Related

- `respawn.md` — the receiving side. The reconciliation prompt fires on next session start.
- `meta/death-and-spawn.md` — for the recovery model that close-session feeds into.
- `meta/drafts-mechanics.md` — close-session is now a fourth draft-surfacing event.
- `developer-braindead/spellbook/session-close.md` — the dev-brain twin (single-track, rolling `respawn.md` instead of per-player quest-log entries).

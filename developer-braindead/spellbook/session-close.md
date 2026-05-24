# session-close — session-end procedure

**Invoked.** At the end of every dev session, before the user closes the conversation.

**Produces.** A landed quest-log entry, an updated `respawn.md`, any required `bank/` updates, **and a git commit** capturing every change the session made.

## Steps

1. **Name the quest.** Pick a short, *understandable* descriptive name for what this session was about. Not evocative — clear. Filename pattern: `SNNN_descriptive_underscore_name.md`. Examples: `S001_dev_brain_architecture`, `S002_dev_brain_runescape_restructure`.
2. **Write the quest-log entry** at `quest-log/{filename}.md`. Format per `entry-formats.md`:
   - H1: `# SNNN — YYYY-MM-DD — Quest name`
   - 3–5 bullets describing what happened. Wiki-link to every artifact created or changed.
   - End with two lines: **Cascade.** (what dev-brain files landed) and **Main-brain changes.** (what crossed into `vault/`, or `none`).
3. **Update `respawn.md`.** Overwrite in place. New `Last updated` line. Refresh "where we are," "what's open," "next concrete step." History lives in quest-log, not here.
4. **Update `bank/plan.md` if status changed.** Mark items `[x]` if completed; add new items if surfaced.
5. **Harvest learnings + audit memory pointers.** Two durability tasks at every close:
   - **Learnings (always scan).** Skim the session for the highest-signal moments — *where the principal corrected me or pushed back, where something I shipped proved wrong or got reverted, or where a non-obvious failure mode / insight surfaced.* Distill each into a carried lesson in `bank/build-lessons.md` (the `From [[SNNN]]: **…**` format), citing the specific moment that produced it (observation-backed, not aspirational). If the lesson generalizes beyond this repo — a working-style or judgment lesson, not a cockpit-specific detail — **also** write it to the cross-conversation memory at `~/.claude/projects/.../memory/` per that system's protocol (one fact per file, update `MEMORY.md`). A routine build session may yield nothing — but **a session that contained a correction, a reverted change, or a misjudgment the principal caught MUST produce a captured learning.** This is not optional and not subject to "bias to less." (This step exists because [[S083]] shipped a regression — a heuristic with a known-but-unverified false-trip — that the principal caught in his *live* environment, then asked "did you learn from this?" That class of scenario is precisely what must be harvested, every time.)
   - **Pointers.** If dev-brain structure changed (new files, renames, layer changes), update `~/.claude/projects/.../memory/` so the cross-conversation memory still points correctly. Risk tracked in [[R-002]].
6. **Post the `CLOSING` entry to `comms/active.md`.** Per [[D-019]] — every dev-brain session that posted an `OPEN` must post a matching `CLOSING` before commit, so the next session's sibling-detection can correctly recognize this one as done. Format:

   ```
   [YYYY-MM-DD HH:MM] braindead-<sid8> CLOSING
     Completed: <quest name and short summary>
     Leaving open: <items in respawn.md that are still pending, or 'none'>
   ```

   Append-only. If the session ran without posting an `OPEN` (rare — read-only sessions that didn't trigger one), still post a `CLOSING` so the channel reads cleanly. If the working tree is clean *and* no `OPEN` was posted, skip silently.
7. **Clear the visualizer marker.** Overwrite `brain/.claude/active-mode.txt` with `unscoped` (or leave empty). The hook emits `despawn-braindead` on the transition — Braindead packs up and leaves the workshop. Skip silently if the file is already empty / not `dev-brain`.
8. **Commit the session.** Always. This is the durability checkpoint — every session ends with a git commit that captures everything the session changed.

   - Stage the session's changes. Prefer scoped adds (`git add gielinor/ developer-braindead/ <specific-files>`) over `git add -A`, which can sweep in unintended artifacts. Verify with `git status` before committing.
   - Commit with a structured message:
     - **Subject:** `SNNN: <one-line summary>` (same `SNNN` as the quest entry). Keep under ~70 chars.
     - **Body:** a few short paragraphs grouped by area of change, mirroring the quest-log's bullets. Past tense, "why" over "what."
     - **Trailer:** `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` (or current model identity).
   - **Do not push.** Push is a separate, explicit user action. The session ends with a local commit only; the remote moves on the user's word.
   - **Do not skip hooks** (`--no-verify`, `--no-gpg-sign`). If a hook fails, fix the underlying issue and create a new commit — never amend the commit the hook rejected.
   - **If the working tree is clean** (a read-only session — discussion, audit, no file changes), skip the commit silently and note "no commit; tree clean" in the close.
   - **The principal has already authorized end-of-session commits** by making this part of the ritual. Don't ask before committing here; the ritual is the authorization. (The user's standing rule "always ask before committing" still applies *outside* this step.)
9. **State the close back to the user** in 1–2 sentences. Include the commit hash (or "no commit; tree clean"). Get a nod.
10. **Flag the switchboard: `WRAPPED UP`.** As the final action — after the commit and the close statement — write `wrapped_up` to `.claude/intent/<sid8>.mode` at the brain root (`<sid8>` = first 8 chars of `CLAUDE_CODE_SESSION_ID`). This flips Braindead's switchboard row from `CLOSING` (mid-wrap) to `WRAPPED UP` — "done, terminal still open" — distinct from `ENDED` (process gone). `status-sidecar.py` reads it on this turn's `Stop` and holds the state until the process ends; a fresh prompt auto-clears it and resumes. Independent of step 7's `active-mode.txt` clear — that despawns the sprite; this sets the row state. Switchboard concern only, not architecturally enforced.

## Notes

- Quest naming is the step most likely to be skipped. Don't. The name is what makes the session findable months later.
- The "what crossed into main brain" check is load-bearing for [[D-001]] / [[R-001]]. Even `none` must be stated explicitly.
- If the session was unusually long or branchy, consider splitting into multiple SNNN entries. Rare; default to one.
- The commit is the **last writing step** for a reason: every other artifact (quest log, respawn, plan, memory) needs to be on disk before the commit captures them. If a later thought surfaces, write a *new* commit — don't amend.

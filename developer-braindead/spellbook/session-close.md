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
5. **Audit Claude memory pointers.** If dev-brain structure changed (new files, renames, layer changes), update `~/.claude/projects/.../memory/` so the cross-conversation memory still points correctly. Risk tracked in [[R-002]].
6. **Clear the visualizer marker.** Overwrite `brain/.claude/active-mode.txt` with `unscoped` (or leave empty). The hook emits `despawn-braindead` on the transition — Braindead packs up and leaves the workshop. Skip silently if the file is already empty / not `dev-brain`.
7. **Commit the session.** Always. This is the durability checkpoint — every session ends with a git commit that captures everything the session changed.

   - Stage the session's changes. Prefer scoped adds (`git add gielinor/ developer-braindead/ <specific-files>`) over `git add -A`, which can sweep in unintended artifacts. Verify with `git status` before committing.
   - Commit with a structured message:
     - **Subject:** `SNNN: <one-line summary>` (same `SNNN` as the quest entry). Keep under ~70 chars.
     - **Body:** a few short paragraphs grouped by area of change, mirroring the quest-log's bullets. Past tense, "why" over "what."
     - **Trailer:** `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` (or current model identity).
   - **Do not push.** Push is a separate, explicit user action. The session ends with a local commit only; the remote moves on the user's word.
   - **Do not skip hooks** (`--no-verify`, `--no-gpg-sign`). If a hook fails, fix the underlying issue and create a new commit — never amend the commit the hook rejected.
   - **If the working tree is clean** (a read-only session — discussion, audit, no file changes), skip the commit silently and note "no commit; tree clean" in the close.
   - **The principal has already authorized end-of-session commits** by making this part of the ritual. Don't ask before committing here; the ritual is the authorization. (The user's standing rule "always ask before committing" still applies *outside* this step.)
8. **State the close back to the user** in 1–2 sentences. Include the commit hash (or "no commit; tree clean"). Get a nod.

## Notes

- Quest naming is the step most likely to be skipped. Don't. The name is what makes the session findable months later.
- The "what crossed into main brain" check is load-bearing for [[D-001]] / [[R-001]]. Even `none` must be stated explicitly.
- If the session was unusually long or branchy, consider splitting into multiple SNNN entries. Rare; default to one.
- The commit is the **last writing step** for a reason: every other artifact (quest log, respawn, plan, memory) needs to be on disk before the commit captures them. If a later thought surfaces, write a *new* commit — don't amend.

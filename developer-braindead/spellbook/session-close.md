# session-close — session-end procedure

**Invoked.** At the end of every dev session, before the user closes the conversation.

**Produces.** A landed quest-log entry, an updated `respawn.md`, and any required `bank/` updates.

## Steps

1. **Name the quest.** Pick a short, *understandable* descriptive name for what this session was about. Not evocative — clear. Filename pattern: `SNNN_descriptive_underscore_name.md`. Examples: `S001_dev_brain_architecture`, `S002_dev_brain_runescape_restructure`.
2. **Write the quest-log entry** at `quest-log/{filename}.md`. Format per `entry-formats.md`:
   - H1: `# SNNN — YYYY-MM-DD — Quest name`
   - 3–5 bullets describing what happened. Wiki-link to every artifact created or changed.
   - End with two lines: **Cascade.** (what dev-brain files landed) and **Main-brain changes.** (what crossed into `vault/`, or `none`).
3. **Update `respawn.md`.** Overwrite in place. New `Last updated` line. Refresh "where we are," "what's open," "next concrete step." History lives in quest-log, not here.
4. **Update `bank/plan.md` if status changed.** Mark items `[x]` if completed; add new items if surfaced.
5. **Audit Claude memory pointers.** If dev-brain structure changed (new files, renames, layer changes), update `~/.claude/projects/.../memory/` so the cross-conversation memory still points correctly. Risk tracked in [[R-002]].
6. **State the close back to the user** in 1–2 sentences. Get a nod.

## Notes

- Quest naming is the step most likely to be skipped. Don't. The name is what makes the session findable months later.
- The "what crossed into main brain" check is load-bearing for [[D-001]] / [[R-001]]. Even `none` must be stated explicitly.
- If the session was unusually long or branchy, consider splitting into multiple SNNN entries. Rare; default to one.

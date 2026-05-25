# S091 — 2026-05-25 — Remove leftover Windows-toast notifier

- Entered dev-brain mid-conversation via "lets develop gielinor". Principal: a leftover dev that pings Windows when a claude session finishes is now redundant with the cockpit's notifications — find it and remove it. Posted [[S091]] `OPEN`; one live sibling (braindead-327b1216, cockpit chat-UI **discussion-only**) — no file overlap.
- **Located it in the GLOBAL `~/.claude/`, outside the brain repo** (not in any in-repo hook): `~/.claude/settings.json` carried a `Notification`-event hook firing `~/.claude/hooks/notify.ps1` — a `System.Windows.Forms` `NotifyIcon` balloon ("Claude Code needs your attention"). Confirmed it's the only toast mechanism; there is **no** Stop/SessionEnd notifier. The `Notification` event fires on attention/idle — functionally the "I'm done, look at me" ping the principal meant.
- **Killed it:** stripped the whole `hooks` block from `~/.claude/settings.json` (re-validated — JSON parses, no `hooks` key remains; this is the functional kill, applies to *every* project) and moved `notify.ps1` → `~/.claude/hooks/archive/notify.ps1` (reversible).
- **Disposition constraint:** `block-deletes.py` is command-pattern based, *not* path-scoped — it intercepts any shell `rm`/`Remove-Item` I issue even for an out-of-repo file, and the guard isn't bypassable. So the script was *moved* to archive, not deleted; principal picked move-to-archive over hard-deleting it himself via `!`. The archived copy can be `!`-deleted anytime.
- **Flagged:** the cockpit only watches brain sessions, so claude runs in *other* repos no longer toast — offered a lightweight global Stop-hook if that turns out to bite.

**Cascade.** New `quest-log/S091_remove_leftover_windows_toast_notifier.md`; `comms/active.md` (OPEN + CLOSING); `respawn.md` Last-updated refresh. No dev-brain structural change, no `bank/`/`plan.md` change, no build-lesson (routine session, no correction).

**Main-brain changes.** none (the only edits were to the principal's global `~/.claude/`, outside both brains).

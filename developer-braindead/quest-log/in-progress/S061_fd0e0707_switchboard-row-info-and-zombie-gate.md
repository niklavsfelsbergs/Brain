# S061 — switchboard row info + zombie gate

**Session:** braindead-fd0e0707 · 2026-05-23 · dev-brain (entered via "lets develop gielinor")

## Ask

Principal: switchboard is buggy — shows already-closed sessions, some wedge on
`Pending...`, and rows don't carry enough info. Wants each row to hold:
1. a (renameable) name — already exists,
2. the session's opening message (for tracking),
3. a current action summarized to ~80 chars, constantly updating.

## Diagnosis (confirmed against the live manifest)

Dumped `state-switchboard.json`: four sessions wedged at 3h+ (`9eb9cd94` WORKING,
`4365c34d`/`4685b18c`/`85d0e427` waiting) + one live-but-unnarrated (`9d5c5d89`).
Three root causes, all in `status-sidecar.py`:

1. **Zombies.** `_write_manifest` only excluded `state == "ended"`. A terminal
   closed hard / crashed never fires `SessionEnd`, so its status file freezes at
   working/waiting and squats until the 24h `STALE_SEC` sweep. The 1h
   `LIVE_SESSION_SEC` liveness constant existed but wasn't applied to manifest
   inclusion.
2. **Stuck WORKING / Pending.** Reader decays only `waiting → idle`, never
   `working` (S043 killed working-decay because a real 17-min turn looks
   identical on the wire). `Pending...` = actor unresolved; for dead rows the
   intent files were GC'd so the actor was lost forever.
3. **Thin rows.** Only the `subtitle` line, which flip-flops intent/action and
   freezes mid-turn (manifest action refreshes only at sidecar-fire cadence).

## Decision

Principal chose the **1h uniform liveness gate** (via AskUserQuestion) — any
session silent >1h drops regardless of state. Simplest, reuses the existing
constant, clears all four zombies.

## Changes

**`status-sidecar.py` (uncontested — committed solo):**
- `_write_manifest`: drop rows on **two** liveness signals — (a) the session's
  own `claude.exe` is gone (`_session_process_dead` → `_pid_alive`, ground truth,
  drops within one poll), or (b) silent > `LIVE_SESSION_SEC` (1h backstop for
  PID recycling). New `_pid_alive` (OpenProcess + GetExitCodeProcess, **fail-open**
  on any inconclusive probe — never false-drops a live session) +
  `_session_process_dead` (picks the `claude.exe` chain entry, falls back to
  `claude_pid`).
- `main()`: capture `first_prompt` once from the first `UserPromptSubmit`
  `payload["prompt"]` (collapse whitespace, ≤140 chars), carried forward, never
  overwritten. New `FIRST_PROMPT_MAX` const; field added to the record (rides
  into the manifest automatically).

**`switchboard/activity.js` (uncontested — commit solo):**
- New `recordAction(sid8, text, ts)` + `latestAction(sid8)` store — lets the row
  action line tick at the chat panel's 2s poll cadence instead of the slower
  sidecar cadence.

**Contested client files (additive, NOT committed — handed off in comms):**
- `chat.js`: 1 line — feed `recordAction` from each `action` ndjson record.
- `switchboard.js`: render `.sb-firstprompt` (opening message, row 2) + change
  `.sb-intent` into the live action line (`latestAction || latest_action ||
  subtitle`, capped 80 chars).
- `styles.css`: grid → 4 rows; new `.sb-firstprompt` rule; `.sb-intent` → row 3;
  `.sb-spark` → row 4.

## Verified

- `py_compile` + `node --check` (activity/chat/switchboard) green; CSS braces 318/318.
- Drove a synthetic `UserPromptSubmit` through the hook: manifest **10 → 3 rows**
  (4 zombies dropped, the legit idle session retained, cleanly-ended sessions
  excluded as before); my own row captured
  `first_prompt="lets develop gielinor. The switchbar is buggy"`.
- **Live debug with the principal:** blank board on their first refresh = JS
  module cache mismatch (new `switchboard.js` importing `latestAction` from a
  cached old `activity.js` → link error blanks the board); full `Ctrl+Shift+R`
  fixed it. The Jebrim row showed as `Pending...` partly because they typed
  *"Hey Jeb**i**m"* (typo → no address match → unscoped). A `Pending IDLE` row
  lingered at 16m: confirmed via PowerShell its whole PID chain incl `claude.exe`
  was dead — it was a true zombie inside the 1h window. That motivated the
  **process-liveness** signal.
- Process-liveness verified: `_pid_alive` correct on a live PID (True), the dead
  `claude.exe` 18404 (False), a bogus PID (False); `_session_process_dead` True
  on the zombie record; a hook fire then dropped `9d5c5d89` from the manifest
  immediately while the 4 live sessions stayed.

## Commits

- `24c32df` — zombie time-gate + `first_prompt` capture (`status-sidecar.py`) +
  `recordAction`/`latestAction` store (`activity.js`).
- `cc234ed` — process-liveness drop (`status-sidecar.py`).
- Contested client render (`switchboard.js`/`styles.css`/`chat.js`) **uncommitted**,
  riding in the shared tree — hunks handed off in `comms/active.md` CLOSING.

## Open

- **Browser eyeball** — the 3-line row layout + live action ticking are
  client-only; can't self-verify the render. Hard-refresh (styles.css `?v` not
  bumped — index.html is contested; left to the coordinated client commit).
- Pre-S061 sessions parked on a Stop never re-fire `UserPromptSubmit`, so they
  show no opening message (empty line hidden). New sessions get it from turn 1.
- Awaiting-crew rows now show the last tool action on the action line rather
  than the "awaiting crew — D1 D2" subtitle; the AWAITING CREW chip still carries
  the state. Acceptable per "action line = action"; refine if it reads worse live.
- Commit held pending principal call (always-ask boundary). Contested client
  hunks ride uncommitted in the shared tree per D-024.

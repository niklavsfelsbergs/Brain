# S141 — 2026-06-01 — Cockpit board: auto-title subheader, two-phase wrap states, bg-wait shows BUSY

Dev-brain via "lets develop gielinor", mid-conversation. OPEN → 2 UPDATEs → CLOSING via `comms_append`. No live Braindead siblings ([[S140_cfcc35f4_cockpit-sb-app-icon|S140]] cfcc35f4 CLOSED 12:25). Three small, independent cockpit board fixes Niklavs raised in sequence — all in the board/hook data path, all RUNTIME-UNVERIFIED till a cockpit relaunch ("I will test later").

## 1. Row subheader → Claude Code's auto-title (the VSCode session name)

Niklavs asked where the "Set up Guthix bankstand"-style names in VSCode come from, and wanted *that* text as the board row **subheader** (which held the first prompt). Found it: it's Claude Code's `{"type":"ai-title","aiTitle":"…"}` record, written + re-summarised into each session `.jsonl` (one session had 73 of them); VSCode shows the latest. The cockpit already read it for the transcript view but never on the board.

- `status-sidecar.py` — new `_latest_ai_title()` tail-reads the transcript for the latest ai-title and writes `ai_title` into the per-session state (carry-prev on a read miss; cap 80). Mirrors `_latest_action_for`.
- `cockpit/backend.py` — passes `ai_title` through the board model.
- `cockpit/web/board.js` — subheader renders `s.ai_title || s.first_prompt` (Niklavs' chosen fallback: auto-title once it exists, first prompt until then). Name/label + `.doing` untouched.
- Proven on live transcripts: `cfcc35f4`→"Create custom app icon for Gielinor cockpit", **this session**→"Configure default session names in Gielinor", `None`→"".

## 2. Two-phase close: WRAPPING UP → WRAPPED UP

A wrapped-up session showed `WRAPPING UP` forever; Niklavs wanted it to flip to `WRAPPED UP` when done. Turned out **both close rituals already documented** this two-phase (`CLOSING` mid-wrap → `WRAPPED UP`) but it was never wired and `board.js` mislabeled `done` as "WRAPPING UP". Niklavs picked the full two-phase (multiple-choice — signed off the ritual edits).

- Tag approach mirroring alching/bankstanding promotion (no new base state): new `closing` `.mode` marker written at the **start** of close-session, overwritten by `wrapped_up` at the **end**.
- `status-sidecar.py` — `MODE_VALUES` += `closing`; mode block tags `closing` (base state stays); resume-clear on UserPromptSubmit extended to `closing`.
- `cockpit/backend.py` — `MAIN_RANK` `closing:2` (the documented WRAPPING UP slot, above busy); detect + main-derivation (`closing` before alching) + demote-to-sub under a ball-state.
- `cockpit/web/board.js` — `MAIN_LABEL` `done`→"WRAPPED UP", + `closing`→"WRAPPING UP"; `SUB_LABEL` += `closing`. `cockpit/web/styles.css` — `.flavor-closing`.
- Rituals (user-only, Niklavs-signed-off): `gielinor/spellbook/rituals/close-session.md` + `developer-braindead/spellbook/session-close.md` write `closing` first; `gielinor/meta/communication-protocol.md` marker doc updated.
- Nuance recorded: a single-turn close jumps straight to WRAPPED UP; WRAPPING UP surfaces whenever the close crosses a turn boundary (the usual case, given the ask-before-commit / graduation-veto pauses).

## 3. Background-shell / monitor wait shows BUSY, not YOUR MOVE

Niklavs: a session waiting on a background shell to return shows `YOUR MOVE`; should stay `BUSY`. Root cause: a `run_in_background` Bash ends the turn (`Stop → your_move`) to wait for the detached process; the harness re-invokes on completion. The shell/monitor analogue of the existing `your_move + crew → busy` fix.

- `status-sidecar.py` — new `_current_turn_launched_bg()`: walks the transcript tail backward, **turn-scoped** (stops at the current turn's start = a prompt or a `<task-notification>` re-invoke), True iff this turn produced a genuine `Command running in background with ID:` tool_result. At Stop, `your_move` + that → `busy` + `monitoring` tag.
- `cockpit/backend.py` — a `monitoring` row never escalates to `stalled` (intentional quiet wait ≠ frozen heartbeat).
- **Misjudgment, self-caught (build-lesson):** my first cut was a naive regex over the whole transcript blob. It self-polluted — it matched the launch string that my **own grep** had printed into this session's transcript (this session falsely returned True) — and windowed out real launches in long files. Caught empirically, rewrote turn-scoped + `startswith`-on-genuine-tool_result. The fixed version's 5-case harness includes the grep-echo case → correctly not triggered.

## Verification

`py_compile` ×2 + `node --check` clean. `pytest cockpit/test_backend.py` **11/11** (added closing cases to `test_main_status_taxonomy` + a monitoring-no-stall case to `test_busy_stays_busy_when_quiet`). Two synthetic harnesses green: 6-case wrap-lifecycle chip derivation, 5-case bg-task turn detection. `_latest_ai_title` + `_current_turn_launched_bg` proven on real/synthetic fixtures. All three RUNTIME-UNVERIFIED until a cockpit relaunch + a real close / bg wait — Niklavs will test later.

Committed in one session commit (the three features share `status-sidecar.py`/`backend.py`/`board.js`, so clean per-feature pathspec splits weren't feasible without interactive hunk staging). Dogfooded the new two-phase close on this very session (step-0 `closing` marker → `wrapped_up` final).

**Cascade.** `developer-braindead/.claude/hooks/status-sidecar.py` (`_latest_ai_title`, `_current_turn_launched_bg` + `_is_turn_start`/`_is_bg_launch`, `closing` mode handling, bg-wait→busy override), `cockpit/backend.py` (ai_title passthrough, closing main/rank/sub, monitoring stall-suppress), `cockpit/web/board.js` (ai-title subheader, MAIN/SUB labels), `cockpit/web/styles.css` (`.flavor-closing`), `cockpit/test_backend.py` (+closing + monitoring cases), `developer-braindead/spellbook/session-close.md` (step-0 closing marker), `bank/build-lessons.md` (detector self-pollution lesson), this quest-log, respawn, comms CLOSING.

**Main-brain changes.** `gielinor/spellbook/rituals/close-session.md` (write `closing` at start), `gielinor/meta/communication-protocol.md` (mode-marker doc += `closing`) — both the two-phase-close wiring, Niklavs-signed-off via the multiple-choice pick.

# S077 — cockpit swarm verification (S073–S076) + scroll desync fix

**Session:** braindead-e0f2af5d. Dev-brain via "lets develop gielinor".
**Mode:** Braindead, principal-driven verification pass. No live siblings at open (S073/S074/S075/S076 + token-audit all CLOSING'd, HEAD 4fd70ad).

## Why

The S073–S076 swarm all committed in a ~30-min window and none had been eyeballed in the packaged WebView2 window. Principal chose to clear the verification debt before the next build. We relaunch, walk the checklist, fix what doesn't hold.

## Fix landed — terminal scroll desync (completes S073)

S073 un-scaled the terminal's ancestry and fixed the *idle scroll lock*. But a second, subtler symptom remained: **open a session → content renders at the bottom (prompt visible) but the scrollbar thumb sits at the TOP, and a wheel-down jumps the screen to the top.**

**Root cause — scrollbar/buffer desync, not "stuck at top."** `scrollToBottom()` moves xterm's displayed line (`ydisp`) so the screen render shows the newest output, but the native `.xterm-viewport` element's `scrollTop` was left at 0 because at sync time its `scrollHeight` wasn't laid out yet (re-parent + `fit()` reflow lands after). Thumb at 0, `ydisp` at bottom → they disagree. A wheel-down off `scrollTop=0` maps back to a line near the top → the "jump up."

The first attempt this session (a fixed→bounded pin loop that hammered `scrollToBottom()` harder) could not fix it — it only moved `ydisp`, which was already correct. Principal's precise symptom report ("content at bottom, scrollbar at top, scroll-down jumps up") reframed it as a native-scrollbar desync.

**Fix (`cockpit/web/term.js`, `<Term>` mount effect):** a bounded pin-every-frame loop (~0.8s / 48 frames, re-fitting through the first 6 frames, bails the instant `_follow` flips false on wheel-up) that drives **both** sides each frame — `scrollToBottom()` for the render AND `vp.scrollTop = vp.scrollHeight` on the native viewport element so the thumb agrees with `ydisp`. Same pin-every-frame philosophy the console history view (`console.js`) already uses. Also corrected a stale comment in the same component still describing the pre-S073 `transform` counter-scale.

`node --check` green. **Confirmed live by principal** (scrollbar lands at bottom, no jump). Committed solo (`62d5128`).

## Feature landed — board-side rename (double-click a row)

Principal hit the `/rename` limitation: it rides `UserPromptSubmit`, so you can't rename a session while it's mid-turn (the input is busy) — you wait for a turn boundary. This is VSCode-only; the cockpit's own terminals intercept `/rename` client-side in `term.js` and already work mid-work.

Fix (principal chose disk-backed over localStorage, for one source of truth): renaming is now a **board operation**, decoupled from the prompt pipeline. `backend.py` gains `POST /api/rename {sid8, name}` that read-modify-writes the *same* `state-names.json` the rename hook uses (identical sanitize: single-line, printable, 40-cap; empty clears). `board.js` — double-click a row name → inline `<input>`; Enter/blur commits, Esc cancels (commit fires once, via blur; clicks inside don't select the row). `main.js` `renameSession` POSTs + optimistically patches the local model so the label shows instantly. `styles.css` `.rename-input`. Works on a busy session, including a VSCode row.

Gates: `py_compile` + `node --check` + CSS braces all green.

## Fix landed — `/rename` no longer strands a session at WORKING

Principal spotted a row reading WORKING with nothing happening. Root cause: `/rename` fires `UserPromptSubmit` → **both** `rename-intercept` (renames, exits 2 to block) **and** `status-sidecar` (stamps `working`) run; but the blocked prompt runs no turn, so no `Stop` ever fires to clear it. Renaming a session stranded it at WORKING until its next real prompt. (S074's idle-decay only rescues `waiting_for_user`→`idle`, never a stuck `working`.)

Fix (`status-sidecar.py`): detect a `/rename` prompt — the same two shapes `rename-intercept` matches (the `<cockpit-rename>` sentinel + raw `/rename …`) — and **no-op** on it, leaving the session state untouched. Added `import re` + `_RENAME_SENTINEL`/`_RENAME_RAW` + `_is_rename_prompt`, with an early `sys.exit(0)` in `main()` for a rename `UserPromptSubmit`. Also stops a `/rename` from being captured as the session's `first_prompt` (the S076 latent edge). Hooks hot-reload → effective on next fire, no relaunch needed. Detector unit-tested 9/9.

## Verification status

- **S073 scroll** — DONE (idle lock from S073 + this desync fix; principal-confirmed).
- **S074 idle decay** — untested (passive 5-min timer).
- **S075 say-feed** — untested.
- **S076 VSCode parity (display half)** — PARTLY DONE: `/rename` write-half confirmed live in a VSCode session (state-names.json populated, row relabelled "SCROLL"/"Guthix"). Click-vscode-row→open-in-VSCode still untested.
- **S072 leftovers** — Shift+Enter newline + topbar density @372px untested.
- **board-side rename** — built, pending principal relaunch + eyeball.
- **`/rename` strand fix** — built + unit-tested, pending live confirm (rename an idle session → stays idle).

## New finds this session (not in the S073–S076 checklist)

1. **Manifest lists only the firing session at times.** `state-switchboard.json` showed only the guthix session while `~/.claude/status/` had two live (guthix + this one). Likely a manifest-rebuild/live-window quirk (a long working turn fires no hooks, so its status goes stale and may drop) — possibly self-heals on next event. Same family as S039/S042 manifest stability. NOT fixed; flagged.
2. **No decay for a stuck `working`.** S074 decays `waiting_for_user`→`idle` only. A session whose `Stop` is ever missed shows WORKING forever. The `/rename` strand was the main cause and is now fixed at the source; a staleness decay would be belt-and-suspenders but risks false-decaying a genuinely long turn (no heartbeat during a turn — sidecar doesn't fire on ordinary tool calls). Deferred.

## Open

Continue the verification pass: S076 click-to-open, then S075 / S074 / S072 leftovers. Decide whether finds #1/#2 above warrant a follow-up session.

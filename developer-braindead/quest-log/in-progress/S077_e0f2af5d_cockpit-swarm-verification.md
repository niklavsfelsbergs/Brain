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

`node --check` green. **Confirmed live by principal** (scrollbar lands at bottom, no jump). Committed solo.

## Verification status

- **S073 scroll** — DONE (idle lock from S073 + this desync fix; principal-confirmed).
- **S074 idle decay** — untested (passive 5-min timer).
- **S075 say-feed** — untested.
- **S076 VSCode parity (display half)** — IN PROGRESS (vscode-row renders /rename name + click opens VSCode).
- **S072 leftovers** — Shift+Enter newline + topbar density @372px untested.

## Open

Continue the verification pass: S076 next, then S075 / S074 / S072 leftovers.

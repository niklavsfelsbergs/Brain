# S073 — terminal scroll bug, root fix (un-scale the terminal's ancestry)

**Session:** d82c4fbc · dev-brain via "lets develop gielinor" · 2026-05-24
**Principal cue:** "make it perfect so I can peacefully continue working on my agents. lets solve the things 1 by 1." First problem: opening an idle, text-heavy session → (1) scroll-up locked, (2) scroll-down jumps to the very top, (3) then normal until re-navigated.

## Diagnosis (the part the prior 3 attempts missed)

The scroll bug is NOT in the `_follow`/`_write`/scrollToBottom machinery ([[S070_2f4981ed_cockpit-terminal-crash-and-scroll-fix|S070]]/[[S072_dbd41cc0_cockpit-fluid-ui|S072]] worked there). Tell: an **idle** session emits no output, so nothing in our code re-pins the viewport — the lock has to be in xterm's *own* wheel handling. Root cause: xterm sat under a **scaled ancestry** — `.app-grid{zoom:1.35}` + the [[S069_c3f2e3f3_terminal-scale-fix-and-brain-presentation|S069]] counter `.term-host{transform:scale(1/1.35)}`. Net *visual* 1.0, but `transform` is per-level and asymmetric (it scales getBoundingClientRect + wheel deltas but NOT offsetWidth/clientHeight), so xterm's mouse→cell and wheel→line math drift. This is the SAME fragility [[S069_c3f2e3f3_terminal-scale-fix-and-brain-presentation|S069]] proved with selection; the counter-transform fixed selection but left scroll broken. "Scroll-down jumps to top" = corrupted wheel-delta→line mapping snapping viewportY to 0; "then normal" = first real scroll forces a viewport re-sync.

Crucial nuance: `transform` does NOT change the *effective zoom* — under the old setup the terminal's effective zoom was still 1.35, with an asymmetric visual transform on top. That's why net-1.0-by-transform never gave clean coords.

## Fix (principal chose the architectural option over a 4th band-aid)

`cockpit/web/styles.css` ONLY. Give the terminal a **genuinely zero-scaling ancestry**:
- `.app-grid` — dropped `zoom`; now plain `width:100vw; height:100vh` flex.
- Moved `zoom: var(--zoom)` onto the elements that should scale but hold no xterm: `.board-col, .feed-col, .rail, .modal`; `.term-col > .console-head` and peek `.console` (inverse-width `calc(100%/var(--zoom))` so a zoomed box still fits its unscaled column — no overflow, headers stay equal height).
- `.term-frame`/`.term-host` — dropped the `transform` + `*--zoom` width/height. Plain `width/height:100%` + padding. Terminal ancestry (app-grid → console-col → term-col → term-frame → term-host) now has **no zoom and no transform anywhere** → xterm gets a clean 1:1 coordinate system.
- Terminal still tracks the zoom knob via FONT scaling (`term.js termFontFor × --zoom`), untouched. No term.js / main.js change (resizer geometry is identical: board still renders at board-w × zoom).

## Status
- CSS brace balance 200/200; term.js `node --check` clean; no residual transform/zoom on the term subtree.
- **Pending principal relaunch + eyeball.** Verify: (a) the actual fix — open idle text-heavy session, scroll-up works instantly, no jump-to-top; (b) the one risk — per-item `zoom` in the unzoomed flex row (board/feed/rail). Modern Chromium folds zoom into flex used-size so columns should size correctly, but confirm no gap/overlap between pillars and that the 3 header bars (topbar / console-head / feed-head) line up.
- **Committed at close** (principal cued "wrap up"; dev session-close ritual authorizes the end-of-session commit). UNVERIFIED — if the eyeball finds an issue, fix with a NEW commit, never amend. Committed SOLO with explicit pathspecs amid a live swarm (siblings [[S074_cockpit_switchboard_status_fixes|S074]]/[[S075_d27b2fe0_agent-prose-into-feed|S075]] on backend.py/board.js/main.js/feed.js/status-sidecar.py — left untouched; styles.css carried only my scroll hunks).

## Open / not this session
- [[S072_dbd41cc0_cockpit-fluid-ui|S072]] leftovers: Shift+Enter→\n live-confirm; topbar control density at 372px board width.
- If per-item flex-zoom misbehaves in this WebView2 build, fallback is the fixed-overlay-outside-.app-grid pattern (the [[S071_e11aff01_neuron-overlay-design|S071]] neuron-overlay dodge) — bigger (JS rect-tracking) but bulletproof.

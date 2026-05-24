# S072 — cockpit fluid UI: scroll-to-zoom + resizable pillars

> Renumbered from S071 (claimed by the parallel neuron-overlay session e11aff01).

**Session:** dbd41cc0 · dev-brain via "Lets develop gielinor" · 2026-05-24
**State:** committed; **principal relaunch + eyeball pending** (pywebview can't be observed headlessly).

## Ask
Principal wants the cockpit more fluid: (1) scroll-to-zoom that scales the whole UI *and* the text (laptop-friendly), (2) the three pillars resizable sideways, (3) professional-UI suggestions.

Decisions taken (AskUserQuestion): zoom gesture = **Ctrl/Cmd+scroll**; extras = **all four** (topbar zoom+%, focus mode, keyboard shortcuts, per-panel collapse).

## What landed (all under `cockpit/web/`, no backend/hook changes)

**1. Scroll-to-zoom (`--zoom` made a live knob).**
- `main.js`: zoom React state, persisted `cockpit-zoom`. Ctrl/Cmd+wheel and Ctrl+`=`/`-`/`0` adjust it (window listeners, **capture phase + stopPropagation** so xterm never scrolls / never gets `^B`/`^J`, and WebView2 page-zoom is suppressed). Clamp 0.6–2.2, step 0.1, default 1.35.
- `term.js`: the terminal counter-scales to net 1.0 (xterm needs true px), so `zoom` alone does NOT grow terminal text. Fixed: `fontSize = round(BASE_FONT(13) × --zoom)`; new exports `applyTermZoom()` (rescale font + refit, rAF-coalesced) and `fitTerms()`. Wheel handler now ignores Ctrl/Cmd (was the `_follow` scroll-lock signal). xterm 5.x → `term.options.fontSize` (vendored build has no `setOption`; fallback kept anyway).

**2. Resizable pillars.**
- `styles.css`: `.board-col`/`.feed-col` widths → `var(--board-w)`/`var(--feed-w)` (defaults 372/340 in `:root`), `transition: width .14s` (disabled mid-drag via `body.resizing`).
- `main.js`: `<Resizer side="board|feed">` — draggable gutter, computes layout width from `clientX` relative to `.app-grid` rect **divided by --zoom** (grid is sized to fill the viewport, so rect & clientX share viewport-px space). Widths live in CSS vars + localStorage (no React state mid-drag). Double-click a gutter = reset to default. Min/max 220/760. Refits terminals on drag end.

**3. Extras.**
- Topbar zoom controls + % readout live in a new **board status bar** (`.board-foot`, VS-Code-style) — `[−] 135% [+]` + focus toggle `⤢`.
- **Focus mode**: collapses both side panels for a full-width console. Ctrl+`\` or the `⤢` button.
- **Keyboard**: Ctrl+`=`/`-`/`0` zoom; Ctrl+B board; Ctrl+J feed; Ctrl+`\` focus.
- **Per-panel collapse**: `‹` in the board topbar, `›` in the feed header; collapsed pillars become a thin **rail** (left rail also carries a `+`-new) — click the rail or its chevron to reopen.

**4. Shift+Enter → newline (`term.js`).** Principal asked if the zoom work broke Shift+Enter in the terminal. It didn't (the key handler only fires on Ctrl/Cmd). Root cause: plain xterm sends bare `\r` for both Enter and Shift+Enter, so Shift+Enter just submits. Added an explicit intercept in `attachCustomKeyEventHandler` — Shift+Enter sends a literal `\n` (Ink/claude TUI treats `\r`=submit, `\n`=insert-newline). Strictly safe; plain Enter untouched. **Sequence is a best-bet — needs a live confirm; fallbacks are `\x1b[13;2u` (kitty) or the `\`+Enter trick.**

## Baseline + sibling carry
- Built on top of the uncommitted **S070** scroll-lock fix + feed-state board merge already in the tree (principal-confirmed working). Folded into this commit (term.js/console.js/main.js), credited.
- **Carried live sibling [[2f4981ed]]'s handoff**: it built a new `waiting_for_answers` board state ("Waiting for answers…", splitting AskUserQuestion/ExitPlanMode out of the overloaded `waiting_for_user`). It committed the clean logic side (`status-sidecar.py` + `backend.py`) and **ceded the render hunks to this session's files** — `board.js` STATE_LABEL entry + `styles.css` `--answers`/`.state-waiting_for_answers` hot-pink chip. Those hunks ride in my `board.js`/`styles.css` commit (D-024 / S057 pattern). Did NOT touch their Python.

## Parked
- A proper **test environment** for iterating on the cockpit without disrupting work sessions. Investigated and surfaced the low-friction path (no-store assets + `app.py`'s port-reuse → dogfood from a second browser-tab client at `127.0.0.1:8770`, work stays in the window). Principal parked it for now — capture for a future session.

## Open / to verify on relaunch
- Relaunch cockpit, eyeball: Ctrl+scroll zoom (chrome + terminal text both scale), drag gutters, double-click reset, collapse rails, focus mode, persistence across a close/reopen.
- **Ctrl+J caveat**: in the embedded terminal, `^J` is a newline — the global feed shortcut intercepts it. Flagged to principal; easy to rebind if it bites.
- Topbar control density at default board width (372px) — the row may feel tight; board is now resizable so widen if so.
- Nothing committed yet (principal cue required).

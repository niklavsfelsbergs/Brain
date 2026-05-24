# S070 — cockpit terminal: crash fix + scroll-to-bottom robustness

**Session:** 2f4981ed · dev-brain (entered via "lets develop gielinor") · 2026-05-24
**Actor:** Braindead

## What was reported

Principal: "There was just a change made to the cockpit and it completely broke. I closed it, 3 sessions which were active disappeared and now i cant send messages there." Then, after the first fix landed: "what's still not resolved is the issue that the terminal chats open scrolled to the top … it only happens when the agent is done thinking."

## Fix 1 — the crash (`cockpit/web/term.js`)

**Root cause.** A sibling (the S069-ceded `term.js` owner) added WebView2 paste support and called `this.term.attachCustomKeyHandler(...)` — a method that does not exist in the vendored xterm (the real API is `attachCustomKeyEventHandler`; confirmed 3 occurrences in `vendor/xterm.js`, zero of the wrong name). The `undefined(...)` call threw a `TypeError` in the `TermConn` constructor at line 88 — **before** `this.term.onData(...)` (line 110) wired the keystroke→PTY path.

Consequences, all explained by the one throw:
- terminal renders (`open()` at line 76 succeeds) but no keystroke reaches the PTY → **can't send messages**;
- the throw bubbles out of the constructor, so every `resumeTerm()` on reopen failed → **the 3 owned sessions "disappeared"** from the board.

The principal never saw it because the paste handler rode **uncommitted** on top of committed S069 — it was added after S069 closed.

**Fix.** One-word rename: `attachCustomKeyHandler` → `attachCustomKeyEventHandler`. The handler signature `(e: KeyboardEvent) => boolean` already matched the correct API. Owned-session ids persist in `localStorage` (`cockpit-owned-terms`) and are only dropped on explicit release/close, so a failed resume did not lose them — reopen resumes from disk.

## Fix 2 — terminal opens scrolled to the top (`cockpit/web/term.js`, `Term()` effect)

**Root cause.** On open/row-switch the effect re-parents the xterm node (resets viewport to top of scrollback) and `fit()` reflows the rows. The prior code scrolled synchronously + once at 60ms, which races the reflow's layout commit. For a **streaming** session the next PTY write re-pins to bottom (invisible), but for an **idle** session (agent done, no more output) nothing corrects it → stuck at top. Hence "only when the agent is done thinking."

**Fix.** `fit()`, then `scrollToBottom()` across the next two animation frames (after xterm commits the new dims), plus one re-run at 120ms as a belt-and-suspenders for WebView2's slower transform/relayout under `.term-host`. rAF handles cancelled in cleanup.

## Committed

`git` SOLO with explicit pathspecs (D-024): `cockpit/web/term.js` + `cockpit/backend.py` (the `/api/clipboard` bridge the paste handler depends on — coherent unit; also lands the S069-ceded markup `fontSize:18` + `.term-frame`/`.term-host` div that pairs with the already-committed `styles.css`).

**Left uncommitted (separate sibling WIP, not mine):** `cockpit/web/main.js` (feed-state board merge), `cockpit/web/console.js` (read-only console scroll tweak), `cockpit/_probe_ask.py` (S065 cruft), and the gielinor/ + visualizer-mirror files.

## Open / next

- Principal to confirm both fixes live (relaunch → send a message; open an idle terminal → lands at bottom).
- The scroll fix targets the **embedded PTY terminal**. If the complaint was the **read-only Console peek** (`console.js`), that's a separate surface a sibling is already touching — revisit.
- Cockpit polish backlog (S066/S068) still stands.

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

The principal never saw it because the paste handler rode **uncommitted** on top of committed [[S069_c3f2e3f3_terminal-scale-fix-and-brain-presentation|S069]] — it was added after [[S069_c3f2e3f3_terminal-scale-fix-and-brain-presentation|S069]] closed.

**Fix.** One-word rename: `attachCustomKeyHandler` → `attachCustomKeyEventHandler`. The handler signature `(e: KeyboardEvent) => boolean` already matched the correct API. Owned-session ids persist in `localStorage` (`cockpit-owned-terms`) and are only dropped on explicit release/close, so a failed resume did not lose them — reopen resumes from disk.

## Fix 2 — terminal scrolls to the top when the agent finishes (`cockpit/web/term.js`)

**First attempt (insufficient — kept as the on-open path).** Guessed it was an on-open re-parent/`fit()` race and made the open-time `scrollToBottom()` fire across two rAFs + a 120ms re-run. Principal: "still happened." That ruled out the on-open theory.

**Real root cause (researched — xterm.js [#5620](https://github.com/xtermjs/xterm.js/issues/5620), github/copilot-cli [#1805](https://github.com/github/copilot-cli/issues/1805)).** Claude's TUI (and other AI CLIs) render by **clear-screen-then-full-rewrite**. When a turn completes and the whole screen is rewritten with a long response, that burst fires rapid scroll/clear events that xterm.js **misreads as a user scroll-up** — it sets its internal "scrolled away" state, stops following output, and locks the viewport at the top. This happens *during the completion rewrite*, not on open, which is why a one-shot open-time `scrollToBottom()` can't touch it. "Only when the agent is done thinking" = the long completion rewrite is what trips it.

**Fix (the documented pattern, scoped to `TermConn`).** (1) **Batch** PTY output into one `term.write` per animation frame (`_write`/`_wq`/`_wraf`), so xterm sees one coherent frame instead of the burst's half-states. (2) Carry a sticky **`_follow`** flag that **only a real wheel-up clears** (and a wheel-down that reaches the bottom restores) — the TUI's synthetic scroll churn never touches it. (3) In the batched write's **render callback**, `scrollToBottom()` if `_follow`, re-pinning after the rewrite renders. Reset `_follow = true` on open/row-switch; cancel the pending write-rAF in `close()` so a queued flush can't write into a disposed terminal. The on-open double-rAF scroll (first attempt) stays for the idle-switch case where no further output arrives to trigger the flush re-pin.

## Committed

`a072ce5` SOLO with explicit pathspecs ([[D-024_parallel_player_coordination|D-024]]): `cockpit/web/term.js` + quest-log + comms. The fix lands on top of the sibling's **`9fe6f2b`** ("cockpit: fix paste in WebView2 terminal via server-side clipboard bridge"), which had committed both `backend.py` (the `/api/clipboard` bridge) **and** the broken `term.js` paste handler — that commit is what took the cockpit down. By the time I staged, `backend.py` was already clean (sibling-committed), so my commit carried only the corrected `term.js` (rename + scroll fix + the S069-ceded markup `fontSize:18` / `.term-frame`/`.term-host` div, which pairs with `styles.css` from [[S069_c3f2e3f3_terminal-scale-fix-and-brain-presentation|S069]]'s `c3f2e3f3`).

**Left uncommitted (separate sibling WIP, not mine):** `cockpit/web/main.js` (feed-state board merge), `cockpit/web/console.js` (read-only console scroll tweak), `cockpit/_probe_ask.py` ([[S065_bfa95764_cockpit-askuserquestion-hang-fix|S065]] cruft), and the gielinor/ + visualizer-mirror files.

## Resolution

Both fixes confirmed and committed. Principal turned the laptop off overnight, so the 3 sessions' processes were dead on relaunch — but the cockpit's owned-id list (localStorage, persistent WebView2 profile per [[S066_7f5db8c5_cockpit-sweep|S066]]) + claude's on-disk transcripts meant `claude --resume` brought all 3 back once the crash no longer threw. Principal confirmed: **"yeah they're back"** (crash fix) and **"I think we're good"** (scroll fix — soft confirm after live use). Launched the cockpit for the principal via `wscript Switchboard.vbs` (the `!` prefix only works at the Claude Code prompt, not raw PowerShell — clarified).

Commits: **a072ce5** (crash rename + first scroll attempt), **c0f15d5** (research + verify-TODO docs), and the close commit (scroll v2 `term.js` + this quest-log + respawn + comms).

## Open / next

- Soft-confirm caveat: if scroll-lock recurs under heavier load, next lever is buffering Claude's synchronized-output frames (`ESC[?2026h/l`) and flushing atomically — copilot-cli #1805 "Layer 3".
- Scroll fix targets the **embedded PTY terminal**; the **read-only Console peek** (`console.js`) is a sibling's surface — revisit if its scroll misbehaves.
- Cockpit polish backlog ([[S066_7f5db8c5_cockpit-sweep|S066]]/[[S068_89f41770_reflection_cockpit_parking_and_lessons|S068]]) still stands: board-merge confirm, place→close→reopen persistence cycle, `/rename` best-effort, offline-vendor Preact.

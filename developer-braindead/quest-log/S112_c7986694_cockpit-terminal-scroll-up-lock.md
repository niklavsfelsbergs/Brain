# S112 — cockpit terminal: scroll-up locks, can't scroll down (idle)

**Status:** OPEN — root cause CONFIRMED from the wheel trace; fix shipped to working tree (GUI-unverified, probe kept armed for the verifying relaunch). NOT closed.
**sid:** c7986694. Dev-brain via "lets develop gielinor", mid-conversation; OPEN posted to comms; no live Braindead siblings.

## The report

Long conversation, open the cockpit terminal → at bottom, fine. Scroll **up** → the view jumps to a position, **locks**, and then **can't scroll down** (up still works). End state: only the top of Claude's last message visible; the rest of the message + the in-terminal prompt + the compose bar are below the fold and unreachable. **Pressing a key resets it** (types into the prompt, xterm's `scrollOnUserInput` pins to bottom). **Idle only** (turn finished) — does NOT happen mid-response.

## Diagnosis so far (NOT yet confirmed by a stuck-state trace)

This is the recurring prompt-below-fold/scroll family ([[S083_d71c4ab3_cockpit-full-audit|S083]] / [[S093_f3239bdc_transcript-readability-and-term-fit|S093]] / [[S095_f9310a45_cockpit-transcript-full-width-speech-bubble|S095]]) but a NEW symptom: scroll-UP-locks, not cut-off-at-open. Per the [[S095_f9310a45_cockpit-transcript-full-width-speech-bubble|S095]] build-lesson (instrument the PREMISE, the over-fit guard was exonerated by the disk trace) I did NOT touch the fit knob.

**Smoking gun, already in `switchboard/term-fit-diag.log` (open-frame samples, 16:51:52):**
`rows=49 overfit=-16.0px baseY=43 vp.scrollTop=0 vp.scrollHeight=784 vp.clientHeight=784`
- `overfit=-16px` → over-fit guard innocent (16px slack), consistent with [[S095_f9310a45_cockpit-transcript-full-width-speech-bubble|S095]].
- `baseY=43` → xterm buffer HAS 43 rows of scrollback, but `vp.scrollHeight == vp.clientHeight == 784` → the native `.xterm-viewport` element thinks it has **zero scrollable overflow**. Healthy samples show `scrollHeight=19488` vs `clientHeight=784`.
- **Idle-only** rules out `_write` output churn and RO/zoom-driven `fitNow` during the stuck state → sole actor is xterm's **native viewport scroll-area sync** (scrollHeight stale vs buffer).

**Open question the trace must answer:** why does *down* lock while *up* works? (Hypothesis: at the locked position the native viewport scrollHeight is still collapsed so the native down-scroll has no range; up works because xterm's wheel→`scrollLines` moves `ydisp` into scrollback. Confirm from the wheelUp/wheelDn samples.)

## Instrument armed (transient — STRIP when fixed)

`cockpit/web/term.js`, two probes added this session (node --check clean):
1. **wheel handler** — throttled (120ms) forced `_diag("wheelUp"/"wheelDn")` on rAF after each scroll → captures POST-scroll geometry to `term-fit-diag.log`.
2. **over-fit guard (`fitNow`)** — `_diag("overfit-shrink")` only when the loop actually resizes → shows if a `term.resize()` fires during the stuck state (would re-sync/collapse the viewport).

Log boundary marker written at line 3379: `===== ISSUE#3 SCROLL REPRO ... =====`. Fresh repro samples land after it. Backend `/api/termdiag` route + `TERM_FIT_DIAG_PATH` still wired (never stripped since [[S095_f9310a45_cockpit-transcript-full-width-speech-bubble|S095]]).

## VERDICT (from the wheel trace, 2026-05-27 — probe was loaded, captured the lock)

Decisive sample (cid=t8): `wheelUp viewportY=114 baseY=191 scrollHeight=3056 clientHeight=1136` → then `wheelDn` drives ydisp only to 120 and **locks**, `follow` flips **true** at viewportY=120 while baseY=191 (71 rows short). Native max scrollTop = 3056−1136 = 1920 (= ydisp 120); `_isAtBottom` saw `scrollHeight−clientHeight−scrollTop = 0 ≤ slack` → false-positive → follow on.

**Root cause:** the native `.xterm-viewport` `scrollHeight` **lags the real buffer** (`baseY`) by ~one viewport — output arriving while off-bottom (and a fresh open, per the `baseY=43 scrollHeight==clientHeight` open sample) doesn't resync the scroll area. So (1) wheel-down caps at the stale native floor, short of the true bottom, and (2) `_isAtBottom`'s native-scrollbar branch then false-positives and re-engages `_follow`, stranding the user. Keystroke → xterm `scrollOnUserInput` → real `scrollToBottom` → resets. (NB: the captured trace had baseY GROWING, i.e. active output, not strictly idle — but the open-frame staleness shows the same lag with an idle short buffer; same mechanism, two faces.)

## FIX (shipped to working tree `cockpit/web/term.js`, node --check clean, GUI-UNVERIFIED)

- **(A) `_isAtBottom` buffer-authoritative** — return `viewportY >= baseY`; native-scrollbar branch only as a throw-fallback. Kills the false-positive that locked `_follow` on. Supersedes the S081 H2 "EITHER" rule (over-fit index wobble is moot now (B) keeps scrollHeight honest).
- **(B) `_syncViewport()` = `term.refresh(0, rows-1)`** (→ onRender → viewport syncScrollArea) called in `_pinBottom` (before pin) and in `_write`'s callback **always** (even off-follow) so scrollHeight tracks buffer growth and wheel-down can reach the true bottom.

## Verify on next relaunch (probe STILL ARMED — strip after)

1. Relaunch cockpit; open a long-convo terminal; scroll up, then scroll **down** — must reach the true bottom (prompt + compose bar fully visible), no lock.
2. In `term-fit-diag.log`: a `wheelDn` at the bottom should now show `viewportY≈baseY` (not stuck short) and `scrollHeight ≈ (baseY+rows)*cellH` (not `baseY*cellH`).
3. Regression check: scroll up to read history — must NOT yank back down (follow stays false until you wheel to the real bottom); a completed turn still auto-pins.
4. If clean: strip both probes (wheel diag + overfit-shrink) and decide whether to finally remove the whole `/api/termdiag` sink (live since S095). This likely closes the recurring scroll-desync family (S083/S093/S095) at its ROOT — the scrollHeight lag — rather than another fit-knob tweak.

## Second issue this session — numbered lists all render "1." (FIXED, logic-verified)

Principal screenshot: an ordered list in the transcript rendered every item as `1.`. Root cause in `cockpit/web/md.js`: a blank line called `flushList()`, closing the `<ol>`. A **loose** list (items separated by blank lines — exactly the screenshot) became N single-item `<ol>`s, each restarting at 1.

**Fix (shipped to working tree, not committed):** defer the list-flush across a single blank — a `pendingBlank` flag; a following same-type item continues the one list, any other block closes it. `cockpit/web/md.js` (3 edits) + `styles.css` `.transcript-view .b-text li` margin 0.15em→0.45em so the merged loose list still breathes (the screenshot's spacing came *from* the bug — per-item `<ol>` bottom margins).

**Verified:** 8/8 inline node unit tests (loose ol→one `<ol>`/5 `<li>`; tight ol; list-closes-before-`<p>`; prose splits into two `<ol>`; loose ul; ol→ul type switch). Shared renderer → also fixes feed/board bubbles. Visual (CSS spacing) RUNTIME-UNVERIFIED until relaunch.

## Not done

Live verification (GUI relaunch) — both the scroll fix and the list fix are RUNTIME-UNVERIFIED. Probes kept armed until the principal confirms.

**Cascade.** `cockpit/web/term.js` (scroll fix: `_isAtBottom` buffer-authoritative + `_syncViewport` on write/pin; wheel + over-fit probes), `cockpit/web/md.js` (loose-list flush deferral), `cockpit/web/styles.css` (`.transcript-view .b-text li` margin 0.15→0.45em), `developer-braindead/quest-log/S112_c7986694_*`, `developer-braindead/respawn.md` (Last-updated prepend), `developer-braindead/bank/build-lessons.md` (+1 lesson), `developer-braindead/comms/active.md` (OPEN + CLOSING).
**Main-brain changes.** none (all changes are cockpit + dev-brain; no writes into `gielinor/`).

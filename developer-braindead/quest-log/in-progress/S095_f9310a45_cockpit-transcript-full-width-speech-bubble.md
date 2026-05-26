# S095 — cockpit transcript: full-width + agent speech bubble (+ c0143b9f WIP synthesis)

**Session:** braindead-f9310a45 · 2026-05-26 · dev-brain via "lets develop gielinor" (mid-conversation pivot). OPEN posted. No live Braindead siblings.

**Status:** built + JS parses; **EYES-ONLY relaunch verification pending** (no GUI to eyeball from here).

## The ask

Principal dislikes the transcript mode (showed a live screenshot). Two fixes + a research request:

1. **Stretch the whole box** — the transcript text filled only the left ~60% of the panel, right ~40% empty dark space.
2. **Agent's text in a speech bubble.**
3. Research online for how to set up a great chat interface.

## Research (informs the design)

Searched current (2025–26) chat-UI / LLM-interface best practice. The decisive finding: modern LLM chat UIs (ChatGPT, Claude) **deliberately don't put the assistant in a tight bubble** — assistant responses go **wide** because they hold rich content (code, tables, tool calls), while the **user** message stays a compact aligned bubble. Users actively want *more* assistant width (browser extensions exist purely to widen Claude.ai's margins). So the principal's two asks aren't in tension — they point straight at the standard pattern: **kill the measure cap, give the agent a wide left-aligned speech bubble, keep the user's compact right bubble.** (Sources captured in the closing summary; thefrontkit / multitaskai / intuitionlabs / medium-bootcamp.)

## Decisions (principal, via multiple-choice)

- **Abandoned WIP → ADOPT + build on top.** `braindead-c0143b9f` (2026-05-25 22:18, never CLOSING'd) left clean uncommitted readability WIP in the tree on the exact three files (the de-chromed tool rows, icon-only hover-reveal copy buttons, dimmed composer in reading mode — its S093-follow fixes #1–#5). Principal approved folding it in as baseline and committing it synthesized with this session's work. Nothing of theirs lost.
- **Bubble style → wide left bubble + tail.** Agent text in a tinted rounded bubble, left-aligned, ~full-box width with a thin right gutter; squared top-left corner = tail toward the CLAUDE label above (mirrors the user bubble's squared bottom-right). User keeps the compact right bubble.

## What landed

All scoped to `.transcript-view` (the board / feed / VS Code peek console keep their own rendering).

- **`cockpit/web/transcript.js`** — `Turn()` now wraps the assistant turn's blocks (prose + tool rows + thinking) in a single `<div class="asst-bubble">`. The speaker header (`CLAUDE` + copy-turn button) stays above the bubble. User turn unchanged (already a right-aligned `.bubble`).
- **`cockpit/web/styles.css`** —
  - 66ch prose cap (`.b-text > p/ul/ol/blockquote/h1–h3`) changed `max-width: 66ch` → `none`. Prose now fills the bubble; the panel is already bounded by the side pillars so full-bleed reads fine.
  - New `.transcript-view .asst-bubble`: fill `#241d12` (subtle warm lift off the `#1c1813` reading bg), `1px` border `color-mix(line 50%)`, `border-radius: 4px 14px 14px 14px` (squared top-left tail), `padding 12px 16px`, `margin-right: clamp(16px, 5%, 64px)` (the thin right gutter that keeps it on "the agent's side"). First/last-child margin resets; tool rows nudged `margin-left: 2px` so support material sits subordinate inside the bubble.
- **`cockpit/web/board.js`** — build tag `b89.4` → **`b90.1`** (fresh-code confirmation after relaunch).
- **Adopted from c0143b9f (uncommitted, now part of this synthesis):** `transcript.js` CopyBtn icon-only/hover-reveal + `showText` for copy-all; `main.js` `.term-col` gains `reading` class when transcript view active; `styles.css` tool-row de-chrome, copy-btn reveal-on-hover, `.tv-bar` zoom + bigger controls (#4), composer dim-in-reading (#5).

`node --check` green on transcript.js / main.js / board.js. No `?v=` cache-buster on styles.css (plain `<link>`), so a relaunch loads fresh CSS. No hooks, no backend logic, no gielinor writes.

## EYES-ONLY relaunch checklist (board reads `b90.1` when fresh)

1. Open a driven session, flip to **transcript** view.
2. **Agent text fills the box** — prose runs nearly the full panel width (thin right gutter only), no big empty right band.
3. **Agent text is in a speech bubble** — a tinted rounded container, left-aligned, with the squared top-left corner reading as a tail up to the `CLAUDE` label; tool rows + code nest inside it as one utterance.
4. **User stays a compact right bubble** (unchanged).
5. Adopted c0143b9f WIP still good: tool rows are low-chrome left-rule rows (not bright boxes); copy buttons hidden until row-hover; composer dims while reading and wakes on focus.
6. Selection/copy still works (drag-select holds through the 2s poll); A−/A+ + strip-line-#s still function.

## Follow-on (same session): two more cockpit issues — terminal/compose surface

Principal raised two more (separate from the transcript work above; scope expanded to `cockpit/web/term.js`).

**(1) Compose-bar Enter doesn't send — FIXED.** Typing in the fixed compose bar (TermComposer) + Enter put the text into claude's in-terminal prompt but didn't submit. Root cause: `submitComposed` sent `text + "\r"` (single-line) or `paste(t)` + *immediate* `\r` (multi-line) — the CR arrived inside claude Code's fast-input/paste-coalesce window, so it was folded into the paste and landed as a literal newline in the input box instead of submitting. The seed first-message send already documented the same symptom ("the line is sitting in the prompt and the user just presses Enter"). Fix in `term.js`: unified to bracketed-paste the text (`term.paste`, DECSET 2004) then send the submitting `\r` as a **separate, delayed** keystroke (`COMPOSE_SUBMIT_DELAY_MS = 110`, new module const) so claude sees a clean Enter. `node --check` green.

**(2) Terminal bottom cut off at open — INSTRUMENTED (disk-logger wired), not guess-fixed.** "Open a session → scroll can't reach the very bottom; claude's prompt/textbox only reachable by starting to type." This is the recurring prompt-below-fold bug, "fixed" in S083 (over-fit guard) and S093 (fit-while-hidden) and now regressed. Per the instrument-don't-reguess lesson, I did **not** tweak the fit/pin knob a third time blind — the bug is ambiguous between **H1 over-fit** (`rows*cell > frame.clientHeight` → bottom row below the clip; `overfit > 0`) and **H2 scroll-desync** (`_pinBottom` drives ydisp but native `.xterm-viewport` scrollTop sticks; `overfit ≈ 0` but `viewportY`/`scrollTop` disagree); the fix is opposite for each. Candidate non-knob hypothesis to check against the numbers: a *resumed* session's history replay can finish AFTER the `PIN_FRAMES=48` (~0.8s) pin window ends, leaving the view stuck not-at-bottom — would show as H2 with a late content grow.

Principal chose the **no-DevTools disk-logger** route (over the DevTools-paste route). Wired (transient, strip-when-fixed, mirrors S094 `term-size-diag.log`):
- `term.js._diag(why, force)` — now computes the geometry always, console output still gated on `window.__TERMDIAG`, but it ALSO POSTs each line to `/api/termdiag`. New `force` param bypasses the 250ms throttle for the decisive open-frame samples (`open f1/f8/f40`) so none are dropped (at 250ms throttle f8 used to be skipped). Open-pin call site passes `force=true`.
- `backend.py` — new `api_termdiag` handler + `TERM_FIT_DIAG_PATH = switchboard/term-fit-diag.log` + route `POST /api/termdiag` (registered, marked transient). Best-effort append, swallows IO errors. Pairs with ptybridge's server-side `term-size-diag.log`.
- `node --check` term.js + `py_compile` backend.py green. Board `b90.1 → b90.2`.

**Capture procedure (principal):** relaunch (board reads `b90.2`), open/select a session so the cut-off reproduces, then tell me — I read `switchboard/term-fit-diag.log`. The `open f1/f8/f40` lines + the server-side `term-size-diag.log` setwinsize lines together give H1 vs H2, and I fix from the numbers. **Then strip the logger** (term.js POST + backend route).

**(3) "Restarted, ALL sessions lost their name" — INVESTIGATED, instrumented, NOT our regression.** Principal reported every session showing the bare `chat` label after a restart.
- **Not introduced by this session.** The rename code path is grep-verified untouched: my `term.js` diff is only `submitComposed` + `_diag`; `ptybridge.py` + `names.js` unmodified vs HEAD; my `backend.py` edit only added the `/api/termdiag` route. `chat` is just the default label for a PTY session placed without a player address (`main.js:375` `actor: t.label || "chat"`, `main.js:452`).
- **Ground truth gathered:** port is fixed `8770` and currently serving (PID 976) → not a localStorage-origin/port wipe. `switchboard/state-names.json` is INTACT with 5 real names (`scroll`, `cockpit fixes`, `Guthix`, `DF`, `Top brerar`) — but keyed on OLD sid8s (`d82c4fbc`…) that don't match the current board sessions. `state-instances.json` shows the named sessions are no longer live. So the names orphaned on a **sid8 mismatch** — the recurring S092/S093-R4 rename-persistence bug. S093-R4 left the `/clear`-then-restart path explicitly unverified and *assumed* `--resume` keeps the id.
- **Why I can't pin it statically:** the decisive data is the runtime announce/rotate/carry sequence + the client localStorage, neither visible from disk now. Both name stores (disk `_carry_disk_name`; localStorage via term.js re-announce) HAVE carry logic — so the question is whether rotation is even *detected* on resume, or the carry silently no-ops.
- **Instrument (not guess #3):** re-enabled the S093-R4 rename-diag trace in `ptybridge.py` — logs `announce` (with `resuming`/`anchor_sid8`), `rotate` (prev/cur/anchor), and the `_carry_disk_name` result token (`wrote`/`no-label`/`new-exists`/…) to `switchboard/rename-diag.log`. Transient, strip-after. `py_compile` green.

## Follow-on (same session): transcript readability pass

Principal showed a live Jebrim transcript (now full-width per the first change) — "not easy to read." Critique: (1) **measure too long** — removing the 66ch cap overshot to ~120+ char lines (my own change); (2) inline-code **chips speckle** the prose (a dozen per paragraph); (3) body text small/dim for its size; (4) weak hierarchy. Core tension surfaced: *"stretch the box"* vs *"readable measure."* Principal picked (via multiple-choice, recommended) **bigger text + capped measure** — the resolution that fills the box via font size, not line length (how Claude/ChatGPT/long-form readers do it).

Landed (`styles.css`, scoped to `.transcript-view`):
- `.t-asst` reading font **16px → 18px**, line-height **1.62 → 1.7**.
- `.asst-bubble` — dropped the near-full-width `margin-right` gutter; now `max-width: min(100%, 78ch)`. At 18px that measure fills most of the panel (so it doesn't look empty like the first screenshot) while keeping lines trackable. Code/tool rows nest inside, capped to the bubble. Fill `#241d12 → #262014`, border `--line 50% → 58%`, padding `12/16 → 14/18` (more visible bubble + room for the bigger text).
- Inline code **de-speckled** — dropped the chip background/padding/radius entirely; monospace + dimmer `--ink-dim` now mark code inline without drawing a box on every span.

Board `b90.3 → b90.4`. CSS loads fresh on relaunch (plain `<link>`, no cache-buster). Body-ink brighten + extra code-block spacing held back as cheap follow-ups if the font bump isn't enough.

## Follow-on (same session): name-loss ROOT CAUSE (from the trace) + spacing

**Name loss — diagnosed from `rename-diag.log` + principal clarification ("manual rename works; an AUTO name like jebrim turns to chat").** The instrument was decisive: the newest restart logged two `announce` events, both `resuming:true` with `sid8 == anchor_sid8` and **zero `rotate` events** → `--resume` KEEPS the id (S093-R4's premise holds; the carry was never the problem). So manual renames (keyed on the stable sid8 in `state-names.json`/localStorage) survive — confirmed by "active rename works." The real bug: **the AUTO-label doesn't travel across resume.** A session placed as "Jebrim" carries that label only on the client `TermConn` (`main.js` doPlace `c.label = actor.label`); `resumeTerm(uuid)` constructs with an empty label, and a just-resumed idle session has no hook actor-attribution yet (no status/intent file), so the board's `actor: t.label || "chat"` (`main.js:375`) falls to **"chat"**.
- **Fix (`term.js`, S095):** new auto-label store `cockpit-term-labels` ({uuid: label}, localStorage) — DISTINCT from the manual-rename store. Saved when a labeled term announces (`saveTermLabel(f.sessionId, this.label)`); restored in the constructor on resume (`this.label = loadTermLabel(resumeId)`). So a resumed "Jebrim" keeps its name; a manual rename still wins on the board (`nameFor(sid8)` is checked first). Forward-looking — sessions placed before the fix have no stored label (one manual rename fixes those). `node --check` green. Board `b90.4 → b90.5`.
- NOT a regression from this session (the rename path was untouched; this is a pre-existing gap the trace exposed).

**Transcript line-spacing — over-corrected, fixed.** Principal showed image #5 (mine, airy) vs image #6 (target, tight) — "spacing between lines... should look more like the second image." My readability pass had bumped line-height to 1.7 (too loose). Reverted lower than even the original: `.t-asst` line-height **1.7 → 1.45** (matches image #6 density). Font stays 18px (the earlier bigger-text choice, which serves the measure). CSS-only.

## Follow-on UI dials (same session, `styles.css`, board → b90.8)

Quick principal-driven iterations on the transcript look:
- **Line spacing** dialed twice: 1.7 → 1.45 → **1.38** (line-height); paragraph gap `0.7em → 1em` (lists matched) — tight lines, clearer paragraph breaks (image-#6 target).
- **User bubble matches the agent** — `.transcript-view .t-user .bubble` now mirrors `.asst-bubble` (fill `#262014`, border `--line 58%`, padding `14/18`, `min(100%,78ch)`, 18px/1.38), right-aligned with a squared **top-right** tail (mirror of the agent's top-left). `.transcript-view .bubble` font 15.5px → 18px/1.38.
- **Divider only before YOU turns** — replaced the per-turn hairline (`.tv-turns > * + *`) with: small `14px` gap between all turns + the border/`24px` divider only on `> * + .t-user`. So a question + its answer(s) read as one block; the hairline marks each new exchange.

CSS-only, loads fresh on relaunch. Board `b90.5 → b90.8`.

## Issue #2 RESOLVED — from the trace (the instrument paid off)

Principal: "the textbox getting stuck issue just popped up in one session." Read `switchboard/term-fit-diag.log` (589 samples). Decisive:
- **H1 over-fit RULED OUT.** Every healthy sample: `frameH=816 rows=49 cellH=16 → overfit=-16px` (a row of *slack*, not over-fit) and `scrollHeight-scrollTop-clientHeight=0` (at bottom), `follow=true`. Never a `follow=false`, never a not-at-bottom sample.
- **The 12 bad samples are all `open f1/f8/f40` with `frameH=0`** (cid t2/t4/t6) → overfit reads 800 as an artifact of frameH=0. `frameH=0` = the `<Term>` wrapper was `display:none` (transcript view active) when the row was selected. So the open pin loop ran entirely against a 0-height box: `fitNow()` bails (S093 zero-box guard) and `_pinBottom()` no-ops. The terminal mounts **unfit/unpinned**.
- Recovery in the trace is always a later `keydown frameH=816` — i.e. it only un-sticks when you TYPE. Matches the symptom exactly.

**Root cause:** selecting a session *while the transcript view is up* mounts the terminal hidden; its multi-frame open-pin loop bails on the 0-box. Flipping back to terminal then triggers only a SINGLE RO-driven fit+pin (term.js RO does `fitNow()` + `_pinBottom()` in one rAF), which races the display:none→visible relayout — one frame lands before `scrollHeight` settles, so the pin misses and the prompt sits below the fold until a keystroke forces a cursor-scroll.

**Fix (S095):**
- `term.js` new `reshow()` — a multi-frame fit+pin burst (40 frames, fit first 6 visible frames, pin every visible frame, skips frames while still hidden, ends on wheel-up). Mirrors the open pin loop. Cancelled in `close()`.
- `main.js` effect on `[termView, sel]` — calls `sel.reshow()` when the view flips back to `terminal` for a live term. So a session opened-from-transcript fits + pins to bottom on show, instead of waiting for a keystroke.
- `node --check` green (term.js + main.js). Board `b90.8 → b90.9`.
- The over-fit guard / pin loop were NOT touched (the trace proved they're not the culprit — instrument-don't-reguess held: the bug was elsewhere, the hidden-mount path).

**Next:** verify on relaunch (open a session *from transcript view*, flip to terminal → prompt at bottom, no typing needed). Once confirmed, **strip both transient loggers** (term.js `/api/termdiag` POST + backend route + the `force` diag; ptybridge rename-diag) and commit.

## Open / next

- **Issue #2 (term-fit) + #3 (rename-orphan): ONE instrumented relaunch (board `b90.3`) captures both.** Relaunch → open/select a session so the bottom-clip reproduces and the names show `chat`. Then I read `switchboard/term-fit-diag.log` (H1 vs H2) **and** `switchboard/rename-diag.log` (did `--resume` rotate? did the carry fire?). Fix both from the numbers, then strip both loggers (term.js `/api/termdiag` POST + backend route; ptybridge rename-diag calls).
- Eyes-only verify above (relaunch needed). Compose-Enter (#1): type in the bar → Enter sends + clears; Shift+Enter still newlines; multi-line still sends as one block.
- **Commit pending principal OK** (global rule: ask before committing). Scope when approved: `cockpit/web/{transcript.js,styles.css,main.js,board.js}` + this quest-log + comms entry + respawn. NOT unrelated working-tree M files.
- Aesthetic dials if the bubble reads too subtle/too strong: bump fill toward `--panel` (#2a2114) or border opacity; widen/narrow the `margin-right` gutter.
- Strategic next step unchanged — §C shipping-mart pilot ([[D-027_inward_outward_build_imbalance]]).

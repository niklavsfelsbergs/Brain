# [[S081_p1_terminal-prompt-below-fold|S081]] p1 — terminal prompt sits below the fold after a turn

**Role:** dwarf (penguin-style sub-agent slot p1), dev-brain, spawned by principal.
**Status:** fix landed in working tree, NOT committed. Awaiting live relaunch verification.

## The bug
After a claude response finishes, the live `>` prompt input line is not visible at the
bottom of the embedded xterm, even when scrolled fully down. Bottom visible row is
mid-response body text; native scrollbar thumb sits near-but-not-quite at the bottom.
Only typing (forcing a cursor scroll) reveals the prompt. Secondary: stale/dead text
sometimes lingers at the very bottom. One root, two faces.

## Hypothesis concluded: H1 (over-fit / clipped prompt)
The fit addon (`vendor/addon-fit.js`) computes `rows = floor((hostHeight - padding) / cellHeight)`
by reading `.term-host`'s `getComputedStyle().height`. In this WebView2/Chromium build the
height it measures comes back a hair taller than the box that actually PAINTS inside
`.term-frame { overflow:hidden }`. Cause: the sibling `.console-head` carries `zoom: var(--zoom)`
(1.35) on a `min-height:50px` box → it consumes a **non-integer 50×1.35 = 67.5px** of the flex
column, and the `flex:1` terminal div's reported-vs-painted height can disagree by up to ~a row.
Result: xterm believes it has one more row than physically fits; `scrollTop = scrollHeight` still
leaves the last row (the prompt) clipped below `.term-frame`'s edge. `floor` can't catch this —
the error is in the *measured height*, not the division.

Why H1 over H2 (_follow desync): the screenshot signature is decisive — thumb *just shy* of
bottom + prompt clipped is "xterm has more rows than fit," not "scrollToBottom can't reach the
end." The _follow/viewport-sync path was already hardened twice ([[S077_e0f2af5d_cockpit-swarm-verification|S077]] open path, [[S078_959a4c34_switchbar-two-axis-states|S078]] streaming
path); the rows×cellHeight-vs-frame-clientHeight path had never been guarded.

## The change (all in `cockpit/web/term.js`, nothing committed)
1. **Over-fit guard in `fitNow()`** (root fix). After `this.fit.fit()`, re-measure against the
   ACTUAL painted `.term-frame` clientHeight and, while `rows*cellHeight > frameClientHeight - 16px`
   padding, `this.term.resize(cols, rows-1)` (bounded to 4 iterations). Shrinks the over-count
   so the prompt row lands inside the clip.
2. **New helper `_cellHeight()`** — rendered row height from `term._core._renderService.dimensions.css.cell.height`
   (fallback: `viewport.scrollHeight / buffer.length`). Used by the guard, `_isAtBottom`, and diag.
3. **`_isAtBottom()` hardened** (belt-and-suspenders for H2). Now returns true if EITHER the buffer
   index says so (`viewportY >= baseY`) OR the native `.xterm-viewport` is scrolled within one cell
   of its end. So a wheel-down to the true bottom always re-engages `_follow` even if buffer math is
   momentarily off after a mid-stream resize.

LEFT ALONE per brief: the Shift+Enter handler (`"\\\r"`) at ~L136.

## Diagnostic added (TEMPORARY, clearly marked `[term-diag]`, easy to remove)
- New method `_diag(why)` — throttled ~1 log / 250ms. Logs: `.term-frame` clientHeight, xterm
  rows & cols, cellHeight, `rows*cellHeight`, **overfit delta in px**, `_follow`, `viewportY` vs
  `baseY`, and native `vp.scrollTop / scrollHeight / clientHeight`.
- Wired at two call sites (both tagged for removal): top of the keydown handler
  (`attachCustomKeyEventHandler`), and inside the `<Term/>` open pin loop at frames 1/8/40.
- Remove `_diag()` + both call sites once confirmed fixed.

`node --check cockpit/web/term.js` passes. styles.css untouched.

## What the live relaunch should check
1. Open/resume a terminal, let a turn finish — the `>` prompt should be visible at the bottom with
   NO typing needed.
2. Open DevTools console, filter `[term-diag]`. Read **overfit**:
   - If pre-fix logs showed `overfit` ~ +1 cell (≈ +18–24px) and post-fix shows `overfit <= 0`,
     H1 confirmed and the guard is doing its job.
   - If `overfit <= 0` even before the guard yet the prompt is still hidden, H1 is wrong — pivot to
     H2: watch `follow` and `viewportY` vs `baseY` after a finished turn (a stuck `follow=false`
     or `viewportY` never reaching `baseY` would be the tell), and lean on the `_isAtBottom` change.
3. Confirm no row-count thrash (guard should settle in ≤1-2 resizes; if `rows` oscillates, the
   `-16` padding constant or cellHeight source needs a look).
4. Once green, strip the `[term-diag]` block and its two call sites; commit.

## If H1 fix is insufficient
The brief's alternative for H1 is making `.console-head` a fixed/explicit height instead of
`zoom`-scaling its box (removing the non-integer source entirely). That's a styles.css change and
more invasive (touches the three-header-alignment block at EOF), so the JS-side guard was chosen
first as minimal + reversible. Fall back to it if the guard proves flaky.

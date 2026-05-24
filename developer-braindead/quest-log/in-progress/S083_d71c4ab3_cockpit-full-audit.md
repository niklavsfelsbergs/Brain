# S083 — cockpit full audit (autonomous, principal out)

**Session:** d71c4ab3 · Braindead · dev-brain via "lets develop gielinor".
**Brief:** Principal going out; left me to audit the system in laps until the cockpit is *properly usable*. Research / subspawns / whatever needed. Broad delegation read as commit authority for this session (explicit pathspecs per D-024).

**Hard constraint (stated up front to the principal):** I cannot do the GUI eyeball (pywebview window is the principal's relaunch). So the strategy: maximize correctness on the *provable* layers — status pipeline (Python), scroll/PTY math (JS) — via deep review, real tests, and a headless backend exercise; leave a tight relaunch checklist for the eyes-only last mile.

## Method
- 3 parallel recon dwarves (read-only): D1 status pipeline (status-sidecar.py + emit-event.py + backend.py), D2 frontend (board/main/feed/console/fleet/names/styles), D3 terminal/PTY/scroll (term.js + ptybridge.py + app.py + addon-fit).
- Cross-checked every CRITICAL/MAJOR finding against my own read of backend.py, status-sidecar.py, term.js before acting.

## What the recon found, and what I did about each

### Terminal prompt-below-fold (the 5-session blocker) — FIXED on the logic side
- D3 hypothesized the uncommitted S081 over-fit guard might be inert/harmful. I worked the geometry myself: the fit addon measures `container` (= `.term-host` content box = frameInner − 16px padding) and the guard measures `.term-frame.clientHeight − 16` — **both resolve to the same budget**, so the guard fires *only* on a genuine ≤1px rounding over-count and shrinks to the true clip box. The guard is **correct and fail-safe** (worst case a ~1-row dead strip, never a clipped prompt). Kept it.
- The **real uncovered vector** (D3 finding 3b): `applyTermZoom` and `fitTerms` change the row count but never re-pin → prompt left below the fold after a zoom or panel resize. Fixed: extracted `_pinBottom()` (drives `scrollToBottom` AND the native `.xterm-viewport` thumb together) and call it from ALL four geometry-change sites (ResizeObserver, `_write` batcher, open pin-loop, applyTermZoom, fitTerms).
- Hardened `_cellHeight()` fallback (was dividing by the 8000-line scrollback; now visible `viewportHeight/rows`).
- Gated `_diag` behind `window.__TERMDIAG` (opt-in, silent default) — kept as the relaunch-diagnostic instead of console spam or deletion.
- Shift+Enter→`\n` (Ctrl+J) carried from S081c — best current guess, unverifiable headless.
- Commit **e04c679** (term.js + board.js, incl. a.kind crash-guard + build tag b81.3→**b83.1**).

### Status pipeline — the "stalled/idle CRITICAL" was a false alarm; real bugs fixed
- D1 flagged `stalled`/`idle` as orphaned tokens (backend ranks/labels/styles them, nothing produces them). Verified in backend.py: this is **deliberate** — `build_session_model` lines 250-251 say S080's stale-greying *supersedes* the D-029 `your_move→idle`/`busy→stalled` decay. Not a usability bug; dead scaffolding. Left the scaffolding (re-wiring stays a one-liner) but fixed the **lying `STALL_AFTER_SEC` comment** that claimed active stall-detection.
- **E4 (real crash bug):** `_pending_subagents` did an unguarded `.items()` on `byToolUseId` → a corrupt role file would 500 `/api/sessions` and blank the board. Fixed with isinstance guards at every level (mirrors the sidecar). Commit **f5222d1**.
- **Verified the S080 manifest/PID gate is correct and I did NOT touch it** — it's load-bearing, just-stabilized, and a change is untestable headless; the blank-board bug is already fixed. (B1 "parked-zombie lingers ~55min" is a deliberate S080 trade-off; the real root is the never-refreshed `claude_pid_chain` at status-sidecar.py:1595 — re-walking it when the cached claude.exe pid is positively dead would make `_session_process_dead` reliable and let the needs_you/your_move exemption be safely removed. Left as a documented future fix — too risky to land blind on the just-stabilized gate.)

### Cleanup
- Removed the dead `--closing` CSS var (S074 remnant, provably unreferenced). Commit **f8d54c0**.
- **Left** the peek `.console` `calc(100%/zoom)` width (latent twin of the S079 grainy-box): can't verify headless, S078 author judged it "scales whole". Flagged for eyeball.

### Regression gate (new, lasting)
- `cockpit/test_backend.py` — 26 standalone assertions pinning the session-model contract (stale-greying, attention tally, all 7 legacy aliases, heartbeat, ranking, E4 robustness, graceful degradation). Commit **dc6b0ca**. Writing it caught two real contract dependencies now pinned: the heartbeat filter needs emit-event's COMPACT json, and sid8 must equal session_id[:8].

## Verification done (no GUI)
- `node --check` green on all web modules; `py_compile` green on backend + sidecar.
- `cockpit/test_backend.py` → **26/26**.
- Headless aiohttp integration smoke (`make_app` + TestClient): server boots, `/api/sessions` `/api/feed` `/api/clipboard` `/` `/history` `/api/rename` `/api/open-vscode` all behave (200s/400s correct, no-store headers, `/pty` present, dead `/chat` absent). **12/12 real assertions** (the lone "miss" was my wrong assumption — the catch-all static route serves `GET /api/rename` as index, by design).

## Deliberately NOT done (and why)
- **ptybridge UTF-8 split (D3 5b):** real but rare/cosmetic (boundary mojibake on box-drawing/emoji); pywinpty's decode behavior is uncertain and the PTY data path is high blast-radius + untestable headless. Documented, not touched.
- **console.js dead drivable-composer branch (D2):** provably dead, but removal touches the peek view I can't eyeball; maintainability-only. Deferred.
- **Double `/api/feed` poller, index-list-keys, non-atomic name writes (F3):** minor perf/cosmetic, multi-file churn for low value. Deferred.

## RELAUNCH CHECKLIST (eyes-only — for the principal)
Relaunch the cockpit (running window holds stale code). The board `<h1>` should read **SWITCHBOARD b83.1** — confirms my code loaded.
1. **Terminal prompt (the big one):** open/resume a terminal, let a turn finish — the `>` prompt should be visible at the bottom with NO typing. Then zoom (Ctrl+scroll / Ctrl ±) and collapse/expand a panel — prompt should stay at the bottom after each (the S083 re-pin). If it STILL clips: open DevTools, run `window.__TERMDIAG = 1`, reproduce, read `[term-diag]` — `overfit > 0` ⇒ H1 (guard isn't catching it); `follow=false` or `viewportY < baseY` ⇒ H2.
2. **Shift+Enter:** in a terminal, Shift+Enter should insert a newline, not submit. (5th attempt — `\n`/Ctrl+J. If it still submits, the byte path is a dead end; tell me.)
3. **Board accuracy:** rows don't vanish; a quiet session greys with an age but keeps its real chip; "N need you" only counts live needs_you/your_move.
4. **Header/peek (flagged):** the peek `.console` (click a non-cockpit row) — does its right edge under-fill at zoom≠1 (grainy strip)? If yes, it's the same fix as S079 (`width:100%`); I left it untouched, can patch on your word.

## Laps
- L1: ground truth + 3 recon dwarves + own read of core files.
- L2: status-pipeline reconciliation + backend E4 guard + STALL honesty comment (committed, verified).
- L3: terminal usability (re-pin/cellHeight/diag) + board crash-guard/build-tag (committed).
- L4: dead `--closing` var (committed) + backend regression test 26/26 (committed) + aiohttp integration smoke.
- Stop point: reached the verifiable ceiling; remaining work is visual-only or blind-risky. Consolidated rather than churn unverifiable code.

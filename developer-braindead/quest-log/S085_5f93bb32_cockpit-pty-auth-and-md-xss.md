# S085 — Codex security findings: cockpit /pty RCE + md.js XSS, and the brain-root hook-enforcement gap

**Session:** braindead-5f93bb32. Entered mid-conversation via "lets develop gielinor".
**Status:** code landed + verified at all headless-testable layers; UNCOMMITTED (awaiting principal); one eyes-only relaunch check outstanding.

## What prompted it

Principal pasted 6 Codex findings on the cockpit and asked for my read. Triaged each against live code (see comms OPEN). Verdicts:

- **#1 (Critical) — /pty unauthenticated WS + arbitrary `launch`.** REAL. `ptybridge.pty_handler` had no Origin/token check, and `elif launch: proc.write(launch + "\r")` wrote any `launch` query value straight into a PowerShell PTY → drive-by RCE from any visited webpage while the cockpit runs.
- **#2 (High) — md.js link XSS.** REAL. `esc()` neutralizes `<>&` but not `"`; link regex URL class `[^)\s]+` allowed `"` (attribute breakout) and `javascript:`/`data:` schemes. Sink: `console.js` renders transcript text via `dangerouslySetInnerHTML` (5 sites).
- **#3 — editing retired switchboard/.** Correct workflow note (cockpit/ is the live tree per [[S064_78824901_switchboard-cockpit-rebuild|S064]]/[[D-028_switchboard_cockpit_rebuild|D-028]]), no code bug. Codex itself half-tripped: it flags `switchboard/terminal.js` while its real findings all point at `cockpit/`.
- **#4 — port 8770 trusted on TCP-connect.** REAL, low impact. Deferred.
- **#5 — rename localStorage-first masks disk.** REAL (`board.js:39` `nameFor || s.name`; terminal `/rename`→`names.js` localStorage only). Cosmetic. Deferred.
- **#6 — sel.id vs session_id.** ALREADY FIXED by [[S084_454e276c_cockpit-switchbar-selection-and-nav|S084]] (`main.js:465` `sel.id.slice(0,8)`→`selectedSid8`, `board.js:145` `s.sid8===selectedSid8`). Codex snapshot predates 22:55 2026-05-24.

Principal chose (AskUserQuestion): **fix #1 + #2 now**; leave #4/#5 parked (more inward polish — [[D-027_inward_outward_build_imbalance|D-027]] says §C is the real next step), #3 no-op, #6 done.

## What landed (5 files + tests)

**#1 — /pty lockdown:**
- `backend.py` — `make_app()` mints `app["cockpit_token"] = secrets.token_urlsafe(18)` per process; `static_handler` bakes `<script>window.__CT=...</script>` into any `.html` serve (before `</head>`). A cross-origin page can't READ our same-origin HTML body, so it can't learn the token.
- `ptybridge.py` — two gates before the WS upgrade: token compare **fail-closed** (`request.query.get("token") != request.app.get("cockpit_token")` → 403) + Origin check (foreign browser origin → 403; null/absent passes, token still gates). **Removed** the `elif launch:` arbitrary-command branch (only `launch=claude` / `resume=<uuid>` honored now). Clamped cols (20–500) / rows (5–200) at connect AND in the resize handler.
- `term.js` — `_connect()` appends `&token=${encodeURIComponent(window.__CT)}` to the `/pty` URL.

**#2 — md.js link sanitizer:**
- `md.js` — new `safeUrl()` drops any explicit scheme that isn't http(s)/mailto (relative/anchor pass); link replacer escapes `"`→`&quot;` in the href and renders text-only for an unsafe URL.

**Build tag:** `board.js` b84.1 → **b85.1** (relaunch confirms fresh code).

**Tests:** `test_backend.py` +`test_pty_auth` (async via aiohttp TestClient): token minted, HTML injection present, /pty 403 without token / with wrong token / with foreign Origin, not-403 with valid token. **38 passed, 0 failed** (was 31). md.js proved with a node vector check: `javascript:`/`data:` → no anchor; https/mailto/relative → anchor; `"` in url → escaped, no breakout.

## Gates run

- `py_compile` backend.py + ptybridge.py — OK
- `node --check` term.js, md.js, board.js — OK
- `python test_backend.py` — 38/38
- node md.js vector check — 6/6

## UNVERIFIED (eyes-only, needs relaunch)

- **The terminal still connects** after the token gate — i.e. `window.__CT` injection + `term.js` sending it works end-to-end in WebView2. Server side + client read are tested; the live WS round-trip is not. **If a placed session's terminal shows `[session ended]` / 403 immediately, the token plumbing is the suspect.** Board must read `SWITCHBOARD b85.1` on fresh code.
- Place a new session (Ctrl+Shift+\` or + new) → claude TUI comes up as before.

## Batch 2 — brain enforcement architecture (Codex findings #1, #3)

Second Codex batch (system-level, not cockpit). Triage verdicts:

- **#1 (Critical) — boundary hooks not enforced at brain root. CONFIRMED + the real one.** `brain/.claude/settings.json` wired only observability hooks; all six boundary hooks were wired solely in `gielinor/.claude/settings.json` via `${CLAUDE_PROJECT_DIR}/.claude/hooks/block-*.py` — at brain root that resolves to `brain/.claude/hooks/` (which lacks them). **Proven empirically: `rm` of a temp file at brain root SUCCEEDED — block-deletes did not fire.** And the cockpit launches every session with `cwd=brain root` (`ptybridge.py:96`), so the dominant path had zero boundary enforcement. The "six guarantees… cannot bypass" were prompt discipline in the default mode.
- **#2 (High) — `bypassPermissions` at root.** Confirmed (`settings.json:7`). Deliberate; only dangerous in combination with #1 (no gates + no prompts = no net).
- **#3 (High→I rate Medium) — penguin `BRAIN_ROOT` scope bug. CONFIRMED.** `penguin-write-boundary.py:42` had one extra `.parent` (repo root) vs dwarf/gnome (gielinor/), pulling dev-brain paths into the in-brain test.
- **#4 ritual-heavy / #5 overbuilt-inward / #6 manual coordination** — agreed; judgment calls. Through-line across #1/#4/#6: the system favors documented discipline over enforced mechanism. #5 = [[D-027_inward_outward_build_imbalance|D-027]], §C is the fix.

Principal chose (AskUserQuestion): **fix #1 + #3 now.**

### What landed (batch 2)

- `.claude/settings.json` — registered all six boundary hooks in the **root** settings with **absolute paths** to `gielinor/.claude/hooks/*.py` (matching the existing absolute-path convention for observability hooks), under three new PreToolUse matchers: `Edit|Write|NotebookEdit|MultiEdit` (block-confirmed-writes + dwarf/gnome/penguin boundaries), `Bash|PowerShell` (block-deletes), `Agent|Task` (block-sub-spawn). Added `_comment_boundary_hooks` documenting why. **Left the gielinor wiring in place** — redundant-but-harmless (blocking hooks are idempotent) defense-in-depth in case the loader behaves differently per launch dir.
- `gielinor/.claude/hooks/penguin-write-boundary.py:42` — dropped the extra `.parent` so `BRAIN_ROOT` = gielinor/, matching dwarf/gnome.

### Verified

- **LIVE:** after the settings edit, block-deletes fired and blocked a Bash `rm` in this very session — Claude Code hot-reloaded the settings. The same `rm` that succeeded pre-edit is now gated. (Live side effect: this session can no longer run delete-pattern Bash commands — the intended discipline.)
- Both `settings.json` files parse (a corrupt one would silently kill all hooks).
- Hook simulation harness (OS temp, 13 cases, all PASS): block-deletes rm→2 / git mv→0; confirmed→2 / notes→0; penguin research→0, bank→2, examine→2, dev-brain→0 (abstains), principal→0; block-sub-spawn dwarf→2, penguin→2, principal→0.

### Honest caveat on #3

The fix makes penguin **consistent** with dwarf/gnome (abstain on out-of-gielinor paths) — it does NOT *block* penguin→dev-brain writes; those remain allowed by the same "abstain outside gielinor" design all three role hooks share. What was fixed is the anomaly where penguin alone applied gielinor allow/block rules repo-wide. Hard-blocking role-agents from dev-brain entirely would be a broader change across all three hooks (flagged, not done).

### UNVERIFIED (batch 2)

- Behavior in a **gielinor-launched** session (both root + gielinor settings would wire the hooks → double-fire; expected harmless but not observed). Confirm no double-block oddity next gielinor session.
- That the hot-reload also applies the role boundaries to a freshly-spawned sub-agent (only the principal-side block-deletes was observed live this session).

## Deferred / not done

- #4 (port identity check) — folds nearly free into the token work if ever wanted; not done.
- #5 (rename single-source: terminal `/rename` should POST `/api/rename`, board read disk-first, retire `names.js` localStorage) — real cleanup, low urgency.
- The strategic next step is unchanged: **§C shipping-mart freshness pilot** ([[D-027_inward_outward_build_imbalance|D-027]] / plan.md §C) — the load-bearing outward build after a long run of inward cockpit work.

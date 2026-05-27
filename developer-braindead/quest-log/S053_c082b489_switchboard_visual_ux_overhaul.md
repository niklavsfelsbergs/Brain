# S053 — 2026-05-23 — switchboard visual/UX overhaul

Principal opened in dev-brain ("iterate on the switchboard more"), picked **visual/UX polish**, then asked for "10 suggestions to make it cleaner and COOLER" and said "do it ALL." A single branchy session: a 10-item polish pass, a source-side action-text fix, a follow-up sizing/rename round, and the AskUserQuestion waiting-state fix. All client-side under `switchboard/` plus two hook touches; **no `gielinor/` writes**.

- **Source-side action humanizer** ([[emit-event.py]] `_humanize_tool_call`). The brain runs git as `cd <repo>\n<cmd>`, so the `cd` prefix defeated every git phrasing and the abspath ate the 60-char budget (`git com`). Added `_strip_cd_prefix` (newline/`&&`/`;`-separated), `_shorten_paths` (brain-rooted → repo-relative; other GitHub repos → repo + tail; handles `C:/`, `/c/`, `~/`), and `_extract_commit_subject` (`-m` + heredoc). Verified: `cd <repo>\ngit commit -F - <<'EOF'\nS053: …` → `Committing: S053: …`.

- **Chat panel rewrite** ([[chat.js]], [[state.js]]): per-minute **time-rail** (drops per-line `[HH:MM:SS]`), **speaker-run collapsing** (name once, continuations under a per-actor tinted rule), **action verb-glyphs** (`⌕✎✚❯⎇☆`, color-coded, path-stripped, dimmed monospace), **commit drop-banners** (gold shimmer; COMMITS tab now filters on a `data-commit` flag, cross-actor), **live search** (`/` focus, Esc clear), **two-way actor-flash** (switchboard hover → that session's chat lines). `state.js` gained `formatMinute`, `shortenPaths`, `humanizeAction`. New shared [[activity.js]] ring-buffer feeds the sparkline (decoupled — panels never import each other).

- **Switchboard panel** ([[switchboard.js]]): per-row **activity sparkline** (state-colored), **WAITING hero** row (pulsing glow + "click to jump"), **roster legend** filling the dead space below the rows (color key + "N sessions tracked · M needs you"), and **session rename** — double-click a row name → inline edit → `localStorage` keyed by `sid8` (server is GET-only, so no file write); re-render pauses mid-edit.

- **Theme** ([[styles.css]]): parchment grain (feTurbulence data-URI, `background-blend-mode: multiply`), inner-shadow vignette + gold corner rivets on both panels, and a **CRT/scanline toggle** (`?crt=1` or the `▦` header button).

- **Follow-up sizing round** (principal request): chat body **14→20px** with sub-elements scaled (time-rail, comms body, tabs, search, jump-pip); **COMMS header matched to the SWITCHBOARD header** (52px / 34px title / 12px dot, search+tabs bumped and centered). CRT toggle moved into the switchboard header (was overlapping the legend caption).

- **AskUserQuestion waiting-state fix** ([[status-sidecar.py]], [[settings.json]]): a session parked on `AskUserQuestion`/`ExitPlanMode` read WORKING because no `Stop` fires mid-turn. Registered the sidecar on `PreToolUse`/`PostToolUse` **matched only** to those two tools → `PreToolUse` flips `waiting_for_user`, `PostToolUse` flips back to `working`. ~0–2 extra fires/session; fire-budget exception documented inline in `settings.json`.

- **Green-line artifact**: investigated, no code cause — only `#2e7a2e` in CSS is the 350ms row-click flash, and the reported line crossed the inter-panel gap where no element lives. Confirmed gone in the principal's second screenshot. Concluded transient (browser/selection).

- **Verification**: `node --check` clean on all six modules; hook regexes unit-tested against the real `state.js` exports and the screenshot strings; `py_compile` clean on both hooks; `settings.json` valid. Live-confirmed by principal across two screenshots (glyphs, time-rail, runs, sparklines, legend, sizing, header match).

**Cascade.** `switchboard/`: new `activity.js`; rewrote `chat.js`, `switchboard.js`, `state.js`, `styles.css`; edited `index.html`, `app.js`, `_about.md`. Hooks: `developer-braindead/.claude/hooks/emit-event.py`, `status-sidecar.py`. Config: `brain/.claude/settings.json` (prompt-tool matchers), `brain/.claude/active-mode.txt`, intent file. Comms: `developer-braindead/comms/active.md` (OPEN + CLOSING).

**Main-brain changes.** none. (`switchboard/` and `brain/.claude/` are brain-root infrastructure; nothing crossed into `gielinor/`.)

# S064 — switchboard full rebuild: standalone fleet cockpit

**Session:** braindead-78824901 (instance 2). Dev-brain via "lets develop gielinor".
**Status:** OPEN — all 5 phases built; cockpit functionally complete + packaged (app icon). Principal live-eyeball of Phases 3–5 + **the swap** pending.

## What the principal asked

Opened with the strategic question: redefine + rebuild the switchboard from scratch? It "keeps bugging," eats time meant for building agents, but "makes everything so much better if it works."

## The arc

1. **Diagnosed the disease, not the bugs.** ~18 of the last ~25 dev sessions touched the switchboard. Root cause = no fixed definition → three uncoordinated products in one trenchcoat (monitor / feed / driver) with three drifting data paths. Matches [[D-027_inward_outward_build_imbalance]]'s inward/outward imbalance.
2. **Refused to run ahead.** Principal called it out — I was reasoning about the *existing* structure, not their *end goal*. Pivoted to elicitation (watchtower-vs-cockpit strawman).
3. **Definition (principal's words):** a **standalone fleet cockpit** — *the* place to run ~10 parallel sessions from; see every state at once, watch the work flow, drive any in-app, place/release the fleet. VS Code → engine room. The name was literally right; we'd built the wallboard, never the operator's console.
4. **Foundation locked** (decisions ratified one at a time): hooks PRESERVED as contracts; stack = Python + `pywebview` single process + Preact/htm frontend; clean-modern aesthetic; all §1–§5 product defaults (bypassPermissions, place=actor+brain+prompt, place/re-task/release, VS Code rows = read-only peek, nested subagents, both brains one board, lifecycle feed w/ actions-off default, pulse+sound attention, window state, console rendering carryover).
5. **Coordination:** found a live sibling **braindead-3d2dc4b1 (S063)** on the incremental-patch path (cache-bust, rename COMMS). Surfaced it; principal chose **greenfield + keep old board live**. Flagged the sibling off the doomed polish in comms.
6. **Spec on disk:** [[D-028_switchboard_cockpit_rebuild]] captures definition + foundation + the one-model-three-views discipline + preserved-contract schemas + the 5 build phases + locked decisions.

## Phase 1 — built this session (greenfield `cockpit/`)

- `backend.py` — assembles the **one session model** from `../switchboard/state-switchboard.json` + the `state-{dwarves,gnomes,penguins}.json` role files (subagent nesting); serves `/api/sessions` + static, all `Cache-Control: no-store`. Distinct port **8770** (no collision with the live board on 8765).
- `app.py` — pywebview shell: backend in a daemon thread + native window, one process (server-dying disease structurally impossible).
- `web/index.html` + `main.js` + `styles.css` — Preact/htm fleet board, clean-modern dark theme, state-colored rows, attention pulse, subagent nesting, 2s poll.
- `requirements.txt`, `run.bat`, `_about.md`.
- **Verified:** venv built (aiohttp 3.13.5 + pywebview); `build_session_model()` reads the live state correctly (2 sessions, right states/hosts/ages/doing); HTTP layer green (`/api/sessions` 200 + no-store, `/` html, `main.js` text/javascript).

## Phase 2 — built this session (session console + driver)

- `backend.py` grew the driver, lifted near-verbatim from the proven `switchboard/server.py` (S060) minus the unused `/pty`: `/chat` WS (headless `claude` stream-json; input + `{type:interrupt}`→control_request; `?resume=<uuid>`), `/history?session=<uuid|sid8>` (`.jsonl`→visual turns via `parse_transcript`), all `no-store`.
- Frontend split into clean modules: `board.js` (fleet board, click-to-select), `console.js` (the session console — drives cockpit-owned sessions, read-only peek for VS Code ones; renders streamed text / thinking / tool cards / cost dividers via a preview-then-commit model), `md.js` (small markdown), `main.js` (two-column shell + owned-session tracking in localStorage).
- **Drivable vs peek:** the frontend tracks session ids it launched (`cockpit-owned` localStorage) — those resume+drive; everything else (incl. VS Code rows) is read-only `/history` peek, per the locked decision.
- **Verified (backend):** py_compile clean; `/api/sessions` 200; `/history?session=78824901` resolved sid8→full uuid, title parsed, 16 visual turns from the live `.jsonl`; `/chat` WS handshake minted + announced a fresh session; all new JS/CSS served 200 w/ right content-types. **Live render + an actual driven turn = principal eyeball** (handshake-only here to avoid spending a real turn).

## Phase 3 — built this session (fleet command + persistent connections)

- **`fleet.js` — the connection manager (the backbone).** Persistent per-session `SessionConn`s live here, *not* in the console — so a placed/owned session keeps its `/chat` process alive when you switch to another row (a fleet, not one-at-a-time). Each conn owns its WS + model + listeners; the console subscribes. Owned ids persist in `localStorage` → a reload resumes them from disk.
- **`console.js` refactored to a pure subscriber view** — no WS ownership; renders `conn.model`, sends via `conn.sendInput`/`conn.interrupt`. Switching away no longer kills the session.
- **Place** (`main.js` PlaceModal): actor picker (Jebrim/Zezima/Guthix/unscoped/Braindead) → cockpit composes the address (`Hey Jebrim, …`; Braindead → `Lets develop gielinor. …`), live preview of the composed first message, places a session that auto-sends the seed on connect. The actor implies the brain, so no separate brain picker.
- **Re-task** = click an owned idle/wrapped row → `openOwned` resumes from disk + you type. **Release** = button in the console head → `release()` closes the WS → backend terminates the process + drops it from owned.
- **Verified:** all modules serve 200/no-store; `node --check` green on fleet/console/board/main/md. Live flow (modal → place → persistence-across-switch → release) is the principal's eyeball.

## Phase 4 — built this session (activity feed)

- **`/api/feed`** (backend): merges `chat.ndjson` (lifecycle stream — `picked_up`/`intent`/`needs_you`/`done` + raw `action`s) with best-effort-parsed comms mirrors (`state-comms-*.md` headers + first body line, coarse ts), filters tsless, sorts, returns last 300.
- **`feed.js`** (third column): polls `/api/feed`, renders per-kind styled items (PICKED UP→`NIKLAVS`, PROGRESS, NEEDS YOU amber, DONE, COMMS, actions dim/mono), **actions toggle off by default**, click an item → `onJump(sid8)` selects/peeks that session, sticky-bottom autoscroll.
- Layout now three columns: board | console | feed.
- **Verified:** py_compile + `node --check` green; `/api/feed` returned 266 merged items (comms 50 / action 159 / intent 17 / done 10 / needs_you 5 / picked_up 25), lifecycle reads correctly across braindead+jebrim. Live render = principal eyeball.

## Phase 5 — built this session (package + polish)

- **App icon (the "click an icon" deliverable):** `Switchboard.vbs` (windowless `pythonw app.py`, relocatable), `make-icon.py` (PIL → `icon.ico`: dark panel + 4 status dots), `make-shortcut.ps1` (Desktop + Start-menu `.lnk` → wscript+vbs, custom icon). Ran both — shortcuts created + verified.
- **`app.py` polish:** reuses the port if a server's already up (no double-bind / no server-dying), `on_top` from `config.json`.
- **Frontend polish:** WebAudio beep when a session newly enters WAITING + 🔔 toggle; ▦ feed-collapse toggle; tighter tool cards; toggles persist in localStorage.
- **Verified:** py_compile + `node --check` green; `icon.ico` written (17 KB); shortcuts created.

## The swap — DONE (S064, principal said "do the swap")

The cockpit is now THE board. Executed:

1. **Archived the old client** (14 files) → `switchboard/archive/` via `git mv` (never deleted): `index.html`, the ES modules (`chat/switchboard/terminal/state/activity/settings/focus/app.js`), `styles.css`, `server.py`, `start-switchboard.vbs`, old `_about.md`/`_README.md`. Kept in `switchboard/`: `path-map.json` (hook reads it) + all runtime state files (gitignored — the cockpit + hooks use them).
2. **Replaced `switchboard/_about.md`** with a pointer: the dir is now hook-state-only; the UI is `cockpit/`.
3. **Retired the old server:** removed the "Switchboard Server" **Startup shortcut** (pointed at the now-archived `start-switchboard.vbs`) + stopped the running `:8765` process. The cockpit is **on-demand** via its Desktop/Start-menu icon (not auto-start — offered as an option if the principal wants it up at logon).
4. **Hooks untouched** — they still write `switchboard/state-*`; the cockpit reads them at `../switchboard/`. Nothing migrated.

Reversible: archived files recoverable via git; re-add the Startup shortcut + relaunch to restore the old board.

## Open / deferred

- **Principal eyeball** of the full cockpit (Phases 3–5) via the icon.
- Deferred polish (post-swap): vendor Preact/htm offline (drop CDN); window-geometry persistence (pywebview API fragile); PyInstaller single-file `.exe`; richer subagent nesting (confirm `byToolUseId` shape in `emit-event.py`).
- A stray dev backend (8770) may be running in the background — harmless; kill if tidying.

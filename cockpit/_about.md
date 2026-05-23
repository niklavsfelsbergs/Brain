# cockpit/ — the Switchboard rebuild (greenfield)

> The from-scratch rebuild of the switchboard as a **standalone fleet cockpit**.
> Full rationale + spec in [[D-028]]. Built greenfield so the old `switchboard/`
> stays live until this reaches parity; old client archived at the swap.

## What it is

A standalone window the principal runs a fleet of parallel Claude sessions
from — *the* console, not a dashboard beside VS Code. One Python process
(`pywebview`) hosts a native window + the backend + the claude driver, so it
launches and dies as one — no separate server to go stale.

Three surfaces over **one session model** (the anti-accretion discipline):

- **Fleet board** (left) — every live session + nested subagents, state at a
  glance, click to open. State colors: working / waiting-on-you (amber pulse) /
  awaiting-crew / alching / wrapped-up / ended.
- **Session console** (center) — drive a cockpit-launched session in-app
  (prompt / stream / Stop / release); VS Code sessions are read-only peek.
- **Activity feed** (right) — lifecycle checkpoints + comms across the fleet;
  raw actions off by default; click an item to jump to its session.

## How to run

**As an app (the normal way).** Double-click the **Switchboard** icon on the
Desktop / Start Menu. It launches windowless via `Switchboard.vbs` → `pythonw
app.py`. One-time, after a fresh clone or move:

```
py -m venv cockpit\.venv
cockpit\.venv\Scripts\python.exe -m pip install -r cockpit\requirements.txt
cockpit\.venv\Scripts\python.exe -m pip install pillow   # icon gen only
cockpit\.venv\Scripts\python.exe cockpit\make-icon.py
powershell -ExecutionPolicy Bypass -File cockpit\make-shortcut.ps1
```

`config.json` (optional) — `{"on_top": true}` keeps the window above others.

**Backend-only (browser / dev / smoke test)** — distinct port 8770, never
collides with the old board on 8765:

```
cockpit\.venv\Scripts\python.exe cockpit\backend.py   # → http://127.0.0.1:8770/
```

## Stack

- **Backend:** Python + `aiohttp` (`backend.py`). Reads the hook state files in
  `../switchboard/` (preserved contracts — hooks untouched). Endpoints:
  `/api/sessions` (the model), `/api/feed` (merged lifecycle + comms), `/chat`
  (headless-claude WS driver), `/history` (`.jsonl` → visual turns). Assets
  `Cache-Control: no-store` → no stale-JS tax.
- **Frontend:** Preact + `htm` via an ESM import map (`web/`). No build step.
  (Preact loads from esm.sh — needs internet at load; vendoring locally is the
  one deferred polish item.)
- **Shell:** `pywebview` (`app.py`) — native window; reuses the port if a server
  is already up, else starts its own.

## Files

- `backend.py` — model assembly + feed + `/chat` driver + `/history` + static.
- `app.py` — pywebview shell (backend thread + native window, one process).
- `web/index.html` — shell + import map. `main.js` — app: board + console + feed,
  place modal, sound/feed toggles. `board.js` — fleet board. `console.js` —
  session console (subscriber view). `fleet.js` — persistent connection manager
  (sessions keep running when you switch away). `feed.js` — activity feed.
  `md.js` — small markdown. `styles.css` — clean-modern theme.
- `Switchboard.vbs` — windowless launcher. `make-icon.py` — generates `icon.ico`.
  `make-shortcut.ps1` — creates the Desktop/Start-menu shortcuts.
- `requirements.txt`, `run.bat`, `config.json` (optional).

## Build status (D-028 phases)

All five built (S064): 1 board · 2 console+driver · 3 fleet command
(place/re-task/release + persistent connections) · 4 activity feed · 5 package
+ polish (icon/shortcut, sound, toggles, density). **Swap done** — the old
`switchboard/` client is archived (`switchboard/archive/`), the old auto-start
server is retired; the cockpit is the board, launched on-demand via its icon.
Hooks unchanged — they still write `../switchboard/state-*`, which this reads.

## Preserved contracts (don't rewrite the hooks)

Reads `../switchboard/state-switchboard.json` (manifest), the
`state-{dwarves,gnomes,penguins}.json` role files (subagent nesting),
`chat.ndjson` (lifecycle stream), and `state-comms-*.md` (comms). Drives via the
S060 stream-json protocol. State vocabulary is hook-derived; the cockpit only
reads it. Full schema in [[D-028]] § Preserved contracts.

## Deferred (post-swap polish)

- Vendor Preact/htm locally (offline; drop the CDN dependency).
- Window-geometry persistence (pywebview API is version-fragile).
- Single-file `.exe` via PyInstaller (the shortcut already delivers the icon).
- Richer subagent nesting (confirm `byToolUseId` shape in `emit-event.py`).

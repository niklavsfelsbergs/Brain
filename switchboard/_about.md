# switchboard/ — hook state directory (client retired S064)

> The switchboard **UI moved to `cockpit/`** in the S064 rebuild ([[D-028]]).
> This directory is no longer a web app — it is now just the **runtime state
> the hooks write**, which the cockpit (and any future reader) consumes.

## What lives here now

- **Hook-written state (gitignored, runtime):** `state-switchboard.json` (the
  per-session manifest), `state-{actors,instances,dwarves,gnomes,penguins}.json`,
  `state.ndjson`, `chat.ndjson` (the lifecycle/action stream), and
  `state-comms-{gielinor,braindead}.md` (comms mirrors). The hooks
  (`.claude/hooks/status-sidecar.py`, `emit-event.py`) write these; **don't move
  or rename them** — the cockpit reads them at `../switchboard/`.
- **`path-map.json`** — still read by `emit-event.py`'s path classifier. Keep.
- **`archive/`** — the retired client (S052–S063): `index.html`, the ES modules
  (`chat.js`, `switchboard.js`, `terminal.js`, `state.js`, `activity.js`,
  `settings.js`, `focus.js`, `app.js`), `styles.css`, `server.py`,
  `start-switchboard.vbs`, the old `_about.md`/`_README.md`. Kept per
  archive-discipline (never deleted); the cockpit replaces all of it.
- **`.venv/`** — the old server's venv; unused now (the cockpit has its own).

## The current UI

See **`cockpit/`** — a standalone pywebview fleet cockpit. Launch via the
**Switchboard** desktop/Start-menu icon. It reads this directory's state files;
the hooks remain the single source of truth for both.

# S074 — cockpit no-open diagnostic → handed to dev-brain

**Status:** RESOLVED in dev-brain (Braindead, `S094`, sid `64acd968`). This session pivoted to dev-brain via "lets develop gielinor" to fix it properly — the cockpit/switchboard is construction infrastructure, not my (Jebrim's) data-work domain. Flagged the mode mismatch up front; principal chose the flip. Fix: cleared stacked `cockpit/.venv` python processes (incl. leftover diagnostic `backend.py` probes) + freed `:8770` → clean launch paints; principal confirmed "works." Full record in dev-brain `quest-log/S094_*`.

## What I did (diagnostic only — no writes to cockpit)
- **Symptom:** "switchboard won't open — the terminal opens, the cockpit window itself does not."
- Nothing listening on `:8770`; no python/pythonw process alive → cockpit not running / silently failed at launch.
- Launcher is `pythonw` (windowless) → swallows any startup exception, so a crash is invisible. Diagnostic = relaunch with the visible `python.exe`.
- Python side (`app.py`/`backend.py`) unchanged since S093 (principal-verified "works"); only `cockpit/web/` has uncommitted WIP (frontend → can't block the *window* from opening).
- `cockpit/.webview/EBWebView` modified 09:14 today → the window machinery started then stalled. **Leading suspect: stale WebView2 profile-lock or a hung `webview.start()`.**

## Next (now Braindead's, in dev-brain)
1. Visible-launch trace: `cockpit\.venv\Scripts\python.exe cockpit\app.py`.
2. If it hangs at `webview.start()`: move `cockpit/.webview` aside (archive — never delete) and relaunch.

Continuation: dev-brain quest-log + `developer-braindead/comms/active.md` (`braindead-64acd968 OPEN`).

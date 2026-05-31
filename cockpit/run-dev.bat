@echo off
REM ── Cockpit DEV / preview backend ───────────────────────────────────────────
REM Isolated from the live cockpit (port 8770). Read-only: NO PTY driving, NO
REM rename writes — so the live fleet can never be mutated from here. It reads the
REM SAME switchboard/state-*.json files, so the board / feed / brain map mirror
REM the live cockpit. Restart it freely (Ctrl+C, re-run) to pick up backend.py
REM changes; refresh the browser (F5) to pick up web/ changes. The live cockpit on
REM 8770 keeps driving your agents untouched.
REM
REM Usage:  run-dev.bat [port]      (port default 8771)
setlocal
set "PORT=%~1"
if "%PORT%"=="" set "PORT=8771"
echo Starting DEV backend on %PORT% (read-only). Browser will open; F5 once it finishes starting.
start "" "http://127.0.0.1:%PORT%/"
"%~dp0.venv\Scripts\python.exe" "%~dp0backend.py" --port %PORT% --dev

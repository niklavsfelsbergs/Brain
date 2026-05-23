@echo off
rem Launch the Switchboard cockpit. pythonw = no console window (app-like).
cd /d "%~dp0"
.venv\Scripts\pythonw.exe app.py

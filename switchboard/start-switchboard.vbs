' start-switchboard.vbs — launch the switchboard server detached and hidden.
'
' Runs server.py via the venv's pythonw.exe (no console window), decoupled from
' any Claude Code session — so the board stays whole across terminal closes,
' which was the root cause of the "server keeps dying / half-broken app" problem
' (S062). Self-locating: resolves paths relative to THIS script's folder
' (switchboard/), so it's not tied to a hardcoded checkout path.
'
' Install: a shortcut to this file lives in the Windows Startup folder, so it
' auto-runs at logon. Idempotent enough — if :8765 is already taken, the second
' server exits on the bind failure and does no harm.
'
' Manual use: just double-click this file to (re)start the server.

Set fso = CreateObject("Scripting.FileSystemObject")
here = fso.GetParentFolderName(WScript.ScriptFullName)
pyw  = here & "\.venv\Scripts\pythonw.exe"
srv  = here & "\server.py"

Set sh = CreateObject("WScript.Shell")
' 0 = hidden window, False = don't wait for it to exit.
sh.Run """" & pyw & """ """ & srv & """", 0, False

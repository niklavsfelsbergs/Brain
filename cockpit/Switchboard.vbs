' Windowless launcher for the Switchboard cockpit. Runs the pywebview app via
' pythonw (no console window). Relocatable — resolves its own folder.
Set fso = CreateObject("Scripting.FileSystemObject")
here = fso.GetParentFolderName(WScript.ScriptFullName)
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = here
sh.Run """" & here & "\.venv\Scripts\pythonw.exe"" """ & here & "\app.py""", 0, False

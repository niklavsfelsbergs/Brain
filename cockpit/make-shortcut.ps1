# Create "Switchboard" shortcuts (Desktop + Start Menu) that launch the cockpit
# windowlessly via Switchboard.vbs, with the custom icon. Re-run after moving.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$ws = New-Object -ComObject WScript.Shell
$icon = Join-Path $here "icon.ico"
$vbs  = Join-Path $here "Switchboard.vbs"

function New-SBShortcut($path) {
  $lnk = $ws.CreateShortcut($path)
  $lnk.TargetPath = "wscript.exe"
  $lnk.Arguments = '"' + $vbs + '"'
  $lnk.WorkingDirectory = $here
  if (Test-Path $icon) { $lnk.IconLocation = $icon }
  $lnk.Description = "Switchboard cockpit"
  $lnk.Save()
  Write-Output ("shortcut -> " + $path)
}

New-SBShortcut (Join-Path ([Environment]::GetFolderPath("Desktop")) "Switchboard.lnk")
New-SBShortcut (Join-Path ([Environment]::GetFolderPath("Programs")) "Switchboard.lnk")

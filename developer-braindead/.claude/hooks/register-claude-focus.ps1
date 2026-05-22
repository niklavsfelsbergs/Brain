# One-shot setup script that registers the `claude-focus://` URL scheme in
# HKCU so browser clicks on switchboard rows can fire focus-window.ps1.
#
# Run once: pwsh -ExecutionPolicy Bypass -File register-claude-focus.ps1
# Re-run if focus-window.ps1 moves; the command line is baked at register time.
#
# HKCU (not HKLM) — no admin needed, scope is the current user. To uninstall:
#   Remove-Item -Path 'HKCU:\Software\Classes\claude-focus' -Recurse
#
# After running, the first browser click on a sb-row may prompt "Allow this
# site to open claude-focus links?" — accept once with "Always allow" and
# subsequent clicks go through silently.

$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$focusScript = Join-Path $here 'focus-window.ps1'
if (-not (Test-Path $focusScript)) {
    Write-Error "focus-window.ps1 not found next to this script (expected: $focusScript)"
    exit 1
}

$psExe = Join-Path $PSHOME 'powershell.exe'
$command = '"{0}" -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "{1}" "%1"' -f $psExe, $focusScript

$root = 'HKCU:\Software\Classes\claude-focus'
if (-not (Test-Path $root)) {
    New-Item -Path $root -Force | Out-Null
}
Set-ItemProperty -Path $root -Name '(default)' -Value 'URL:Claude Focus Protocol'
Set-ItemProperty -Path $root -Name 'URL Protocol' -Value ''

$shellOpenCommand = "$root\shell\open\command"
if (-not (Test-Path $shellOpenCommand)) {
    New-Item -Path $shellOpenCommand -Force | Out-Null
}
Set-ItemProperty -Path $shellOpenCommand -Name '(default)' -Value $command

Write-Host ""
Write-Host "Registered claude-focus:// URL scheme." -ForegroundColor Green
Write-Host "  Handler: $psExe"
Write-Host "  Script:  $focusScript"
Write-Host ""
Write-Host "Test by entering this in a browser address bar (replace with a live sid8):"
Write-Host "  claude-focus://393ef3bd" -ForegroundColor Cyan
Write-Host ""
Write-Host "Logs land in: $env:USERPROFILE\.claude\status\focus.log" -ForegroundColor DarkGray

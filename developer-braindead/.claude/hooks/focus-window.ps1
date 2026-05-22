# Terminal switchboard window-focus helper (D-020 Phase 3).
#
# Invoked by Windows via the `claude-focus://` URL scheme. The visualizer
# sidebar sets `window.location.href = "claude-focus://<sid8>"` on row click;
# Windows hands the URL to this script via the protocol handler registered by
# register-claude-focus.ps1.
#
# What it does:
#   1. Parse the sid8 out of the URL argument.
#   2. Read ~/.claude/status/<sid8>.json for the recorded claude_pid.
#   3. Walk the process tree up from claude_pid until it finds a Code.exe
#      process with a non-zero MainWindowHandle -- that's the owning VS Code
#      workspace window.
#   4. Restore-if-minimized, then bring it to the foreground.
#
# Failure modes are all swallowed to the log file (~/.claude/status/focus.log);
# the protocol handler runs windowless so users never see a crash dialog.
#
# Argument shape: the protocol handler passes the full URL as %1, e.g.
#   "claude-focus://393ef3bd"  or
#   "claude-focus://393ef3bd/" (some browsers append a trailing slash).

param([string]$Url)

$logPath = Join-Path $env:USERPROFILE ".claude\status\focus.log"
function Write-Log([string]$msg) {
    try {
        $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
        Add-Content -Path $logPath -Value $line -Encoding utf8 -ErrorAction SilentlyContinue
    } catch {}
}

try {
    Write-Log "invoked with url=$Url"

    if (-not $Url) {
        Write-Log "no url argument; exiting"
        exit 0
    }

    # Strip the scheme and any trailing slash. Accept both "claude-focus://X"
    # and "claude-focus:X" defensively.
    $sid8 = $Url -replace '^claude-focus:(//)?', '' -replace '/$', ''
    $sid8 = $sid8.Trim()
    if ($sid8 -notmatch '^[0-9a-fA-F]{8}$') {
        Write-Log "invalid sid8 in url: '$sid8'"
        exit 0
    }

    $statusFile = Join-Path $env:USERPROFILE ".claude\status\$sid8.json"
    if (-not (Test-Path $statusFile)) {
        Write-Log "status file not found: $statusFile"
        exit 0
    }

    $status = Get-Content $statusFile -Raw -Encoding utf8 | ConvertFrom-Json
    $chain = $status.claude_pid_chain
    if (-not $chain -or $chain.Count -eq 0) {
        Write-Log "no claude_pid_chain in status file for $sid8 (sidecar may be on the old format -- send a message in that session to refresh)"
        exit 0
    }
    Write-Log "sid8=$sid8 host=$($status.host) chain_depth=$($chain.Count)"

    # The sidecar captured the chain at hook fire time so dead intermediate
    # processes still appear with names. Iterate it now and pick the first
    # live Code.exe with a non-zero MainWindowHandle.
    Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class Win32Focus {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
}
"@ -ErrorAction SilentlyContinue

    $target = $null

    # Phase 3 disambiguator: prefer the HWND the sidecar captured on the last
    # UserPromptSubmit. Sibling VS Code windows share one Code.exe pid
    # (Electron: `File > New Window` adds an HWND, not a pid), so the chain
    # walk converges on a shared ancestor and Get-Process.MainWindowHandle
    # picks arbitrarily among the windows. The stored HWND was foreground
    # when the user last submitted from this terminal -- unambiguously right.
    $storedHwnd = 0
    if ($status.PSObject.Properties.Name -contains 'claude_hwnd') {
        try { $storedHwnd = [int64]$status.claude_hwnd } catch { $storedHwnd = 0 }
    }
    if ($storedHwnd -ne 0) {
        $h = [IntPtr]$storedHwnd
        if ([Win32Focus]::IsWindow($h)) {
            $u = 0
            [void][Win32Focus]::GetWindowThreadProcessId($h, [ref]$u)
            $p = $null
            if ($u -ne 0) { $p = Get-Process -Id $u -ErrorAction SilentlyContinue }
            $title = ''
            $pname = 'Code'
            if ($p) { $title = $p.MainWindowTitle; $pname = $p.ProcessName }
            Write-Log ("using stored hwnd={0} pid={1} title='{2}'" -f $storedHwnd, $u, $title)
            $target = [pscustomobject]@{
                Id = $u
                MainWindowHandle = $h
                MainWindowTitle = $title
                ProcessName = $pname
            }
        } else {
            Write-Log ("stored hwnd={0} is no longer a window; falling back to chain walk" -f $storedHwnd)
        }
    } else {
        Write-Log "no claude_hwnd in status file (old format or pre-UserPromptSubmit); using chain walk"
    }

    if (-not $target) {
        for ($i = 0; $i -lt $chain.Count; $i++) {
            $node = $chain[$i]
            $cpid = [int]$node.pid
            $cname = [string]$node.name
            $p = Get-Process -Id $cpid -ErrorAction SilentlyContinue
            if ($p) {
                Write-Log ("  chain[{0}] pid={1} name={2} live hwnd={3}" -f $i, $cpid, $p.ProcessName, $p.MainWindowHandle)
                if ($p.ProcessName -eq 'Code' -and $p.MainWindowHandle -ne 0) {
                    $target = $p
                    break
                }
            } else {
                Write-Log ("  chain[{0}] pid={1} name={2} (dead)" -f $i, $cpid, $cname)
            }
        }
    }

    if (-not $target) {
        # Fallback: if there's exactly one VS Code window open on the machine
        # right now, focus that. Catches the case where the chain walk misses
        # but the user clearly meant the only VS Code instance.
        $candidates = @(Get-Process -Name Code -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 })
        if ($candidates.Count -eq 1) {
            $target = $candidates[0]
            Write-Log "chain walk found no target; falling back to sole Code.exe window pid=$($target.Id)"
        } else {
            Write-Log "no Code.exe window found in chain; $($candidates.Count) live Code windows, can't disambiguate; giving up"
            exit 0
        }
    }

    $hwnd = $target.MainWindowHandle
    Write-Log "target hwnd=$hwnd pid=$($target.Id) title='$($target.MainWindowTitle)'"

    # SW_RESTORE = 9. If minimized, restore first.
    if ([Win32Focus]::IsIconic($hwnd)) {
        [void][Win32Focus]::ShowWindow($hwnd, 9)
    }

    # Windows since 2000 restricts SetForegroundWindow unless the calling
    # process is already foreground or recently active. The protocol-handler
    # process is fresh -- workaround is to attach this thread's input to the
    # foreground window's thread, then SetForegroundWindow. Detach after.
    $fgHwnd = [Win32Focus]::GetForegroundWindow()

    $fgThread = 0
    $tgtThread = 0
    if ($fgHwnd -ne [IntPtr]::Zero) {
        $u = 0
        $fgThread = [Win32Focus]::GetWindowThreadProcessId($fgHwnd, [ref]$u)
    }
    $u = 0
    $tgtThread = [Win32Focus]::GetWindowThreadProcessId($hwnd, [ref]$u)
    $myThread = [Win32Focus]::GetCurrentThreadId()

    $attached1 = $false; $attached2 = $false
    try {
        if ($fgThread -ne 0 -and $fgThread -ne $myThread) {
            $attached1 = [Win32Focus]::AttachThreadInput($myThread, $fgThread, $true)
        }
        if ($tgtThread -ne 0 -and $tgtThread -ne $myThread -and $tgtThread -ne $fgThread) {
            $attached2 = [Win32Focus]::AttachThreadInput($myThread, $tgtThread, $true)
        }
        [void][Win32Focus]::BringWindowToTop($hwnd)
        $ok = [Win32Focus]::SetForegroundWindow($hwnd)
        Write-Log "SetForegroundWindow returned $ok (attached fg=$attached1 tgt=$attached2)"
    } finally {
        if ($attached1) { [void][Win32Focus]::AttachThreadInput($myThread, $fgThread, $false) }
        if ($attached2) { [void][Win32Focus]::AttachThreadInput($myThread, $tgtThread, $false) }
    }
}
catch {
    Write-Log "unhandled error: $($_.Exception.Message)"
}

exit 0

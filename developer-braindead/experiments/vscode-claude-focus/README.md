# claude-focus

A tiny VS Code extension that focuses the terminal pane belonging to a Claude Code session when its switchboard row is clicked.

Companion to `developer-braindead/.claude/hooks/status-sidecar.py` and the switchboard sidebar in `developer-braindead/experiments/visualizer/index.html`. Solves the case the OS-level `claude-focus://` handler can't: multiple Claude sessions running as terminal panes inside **one** VS Code window. Window-level focus is a no-op there; this extension reaches into VS Code's terminal list and focuses the pane.

## Install (symlink — recommended)

Requires Windows Developer Mode enabled (Settings → Privacy & security → For developers → Developer Mode), or run PowerShell as admin.

```powershell
$src = "$env:USERPROFILE\Documents\GitHub\brain\developer-braindead\experiments\vscode-claude-focus"
$dst = "$env:USERPROFILE\.vscode\extensions\niksis8.claude-focus-0.0.1"
New-Item -ItemType SymbolicLink -Path $dst -Target $src
```

Then reload the VS Code window: `Ctrl+Shift+P` → **Developer: Reload Window**.

## Install (copy — fallback)

If symlinking is blocked:

```powershell
$src = "$env:USERPROFILE\Documents\GitHub\brain\developer-braindead\experiments\vscode-claude-focus"
$dst = "$env:USERPROFILE\.vscode\extensions\niksis8.claude-focus-0.0.1"
Copy-Item -Recurse -Path $src -Destination $dst
```

Re-copy after edits, then reload the window.

## Verify

Paste this into any browser URL bar (replace with a live sid8 from the switchboard):

```
vscode://niksis8.claude-focus/focus?sid8=393ef3bd
```

The matching terminal pane should activate. If the status bar reads *"no terminal in this window matches"*, the URI landed in a different VS Code window — VS Code routes `vscode://` URIs to one instance at a time, not necessarily the one owning the target terminal.

## How it works

1. `vscode://niksis8.claude-focus/focus?sid8=<sid8>` fires from the switchboard click handler.
2. VS Code routes the URI to this extension's `handleUri`.
3. Extension reads `~/.claude/status/<sid8>.json` for `claude_pid_chain` (captured by the sidecar at hook fire time — every PID from `claude.exe` up to the workspace `Code.exe`).
4. Iterates `vscode.window.terminals`; the first whose `await terminal.processId` is in the chain wins.
5. `terminal.show(false)` brings the pane forward and focuses it.

The chain is the matching surface (not a single shell PID) because the hook may have fired from any descendant — bash inside powershell inside claude inside the VS Code terminal — and VS Code's `terminal.processId` returns the shell it directly spawned (usually powershell). Matching against the whole chain absorbs that asymmetry.

## Limitations

- **Wrong-window misses.** With multiple VS Code windows open, the URI is delivered to one window's extension instance. If the target terminal lives in a different window, the extension surfaces a status-bar message but can't reach across. The OS-level `claude-focus://` handler in `developer-braindead/.claude/hooks/focus-window.ps1` is the right tool for cross-window focusing; this extension is for in-window.
- **Stale chain.** If `~/.claude/status/<sid8>.json` was last written before the sidecar's status-sidecar.py was updated (or sessions predate the chain capture), `claude_pid_chain` will be empty. Send any message in the target session to refresh.
- **No automatic install/uninstall.** Symlink or copy by hand; remove the folder under `~/.vscode/extensions/` to uninstall.

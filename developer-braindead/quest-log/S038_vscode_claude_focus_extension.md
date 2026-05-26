# S038 — 2026-05-22 — vscode-claude-focus extension (in-pane click-to-focus)

**Status.** Done end-to-end. Extension installed, switchboard click reaches the matching terminal pane, verified live.

## What happened

- **Diagnosis of [[S037_terminal_switchboard_phase_3_click_to_focus]]'s click-to-focus blocker.** Principal reported switchboard clicks weren't navigating. Read `~/.claude/status/focus.log` — every click logged `SetForegroundWindow returned True` against **the same HWND** (`66726`, PID `18664`) regardless of which `sid8` was clicked. `Get-Process Code` confirmed: exactly one VS Code top-level window on the machine, multiple Claude sessions running as terminal panes inside it. The chain walk works correctly; it just lands on the shared workspace ancestor because the principal works in a one-window-many-panes setup, not the multiple-windows setup S037 assumed.

- **Decision: ship a VS Code extension** (option 2 of three offered). The OS-level `claude-focus://` handler is fundamentally window-scoped — VS Code terminal panes have no OS-level HWND. Only an extension running inside the VS Code process can reach the terminal list and `show()` a specific pane. Option 1 (open each session in its own window) and option 3 (set distinct terminal tab names + manual navigation) declined.

- **`niksis8.claude-focus` extension built.** Three files at `developer-braindead/experiments/vscode-claude-focus/`:
  - `package.json` — minimal manifest, publisher `niksis8`, name `claude-focus`, `activationEvents: ["onUri"]`, no contributes.
  - `extension.js` — registers a `UriHandler`. On `vscode://niksis8.claude-focus/focus?sid8=<sid8>`: validates the sid8 (8 hex), reads `~/.claude/status/<sid8>.json`, builds a Set from `claude_pid_chain` PIDs, iterates `vscode.window.terminals`, awaits each `terminal.processId`, calls `t.show(false)` (focus-takes-pane) on the first match. Status-bar message on success and on each failure mode (invalid sid8, missing status file, no chain, no terminal match).
  - `README.md` — install via symlink (`New-Item -ItemType SymbolicLink` in PS, requires Developer Mode) or copy fallback, plus manual verification step (paste URI in browser).

- **Switchboard click handler rewired.** `developer-braindead/experiments/visualizer/index.html` row click now navigates to `vscode://niksis8.claude-focus/focus?sid8=<sid8>` instead of `claude-focus://<sid8>`. Shift-click → copy-sid8 preserved. Tooltip updated from *"focus VS Code window"* to *"focus terminal pane."* The OS-level `claude-focus://` URL scheme + `focus-window.ps1` + `register-claude-focus.ps1` are left in place — still the right tool for cross-VS-Code-window focusing, just not the common case.

- **Install + verify.** Principal symlinked the source into `~/.vscode/extensions/niksis8.claude-focus-0.0.1/` and reloaded the window. Switchboard row click now activates the correct terminal pane in the same window. Confirmed working live.

## Observations to carry

- **"It works in the log" ≠ "the user saw it work" — second confirmation.** S037 closed on a successful self-test (`SetForegroundWindow returned True`) without ever asking *which window setup the user actually has*. The test plan checked the mechanism in isolation, not against the deployment shape. Reinforces S037's own carried lesson — *build the visible-effect test setup into the test plan, not after.* Twice in two sessions. Worth a [[lorebook]] draft: **a focus/navigation feature must be tested against the user's actual window topology, not the design's assumed topology.**

- **OS-level URL schemes hit a ceiling at the window boundary.** VS Code terminal panes are application-internal, not OS objects — no HWND, no `SetForegroundWindow` path. A protocol handler is the right tool for cross-application or cross-window focus; an in-application extension is the only tool for in-window focus. The two layers compose: switchboard click could in principle fire *both* URLs, with the extension winning when present and the OS handler as a multi-window fallback. Not built yet (current setup is single-window); revisit if the principal ever runs ≥2 VS Code windows in parallel.

- **`claude_pid_chain` is the right matching surface, not a single PID.** VS Code's `terminal.processId` returns the shell PID (powershell on this machine, at chain depth 3). The hook fires from deeper in the tree (bash inside the shell inside claude). Matching against the *whole* chain absorbs the depth asymmetry — works regardless of which descendant fired the sidecar. The pattern from S037 (capture-the-chain-at-fire-time) pays off again for a totally different reason: there it was *dead intermediate processes*, here it's *which PID `terminal.processId` happens to expose*. Single-pid matching would have failed silently.

- **VS Code extension as a sidecar surface.** Until S038 the brain's only Windows-side custom surfaces were PowerShell scripts in `developer-braindead/.claude/hooks/`. The extension is the first piece of *editor-internal* code. Tiny — ~70 lines of JS, three files — but it crosses a build boundary. If a second feature ever wants editor-internal access (e.g., "show the active player's quest-log entry in a webview when the visualizer's COMMS panel mentions a session"), the precedent and install pattern are now set.

## Files touched

- `developer-braindead/experiments/vscode-claude-focus/package.json` — **new**.
- `developer-braindead/experiments/vscode-claude-focus/extension.js` — **new**.
- `developer-braindead/experiments/vscode-claude-focus/README.md` — **new**.
- `developer-braindead/experiments/visualizer/index.html` — switchboard row click handler swapped to `vscode://` URL; tooltip updated.
- `~/.vscode/extensions/niksis8.claude-focus-0.0.1/` — installed (symlink to the source). Machine state, not under version control.

## What's still pending

- **S037 quest-log entry moves to top-level eventually.** Currently at `quest-log/in-progress/S037_*.md`. Its mechanism works as designed (verified in S037's own self-test, log shows `True`) — it's just not load-bearing for the principal's actual setup. Leave under in-progress until either a multi-VS-Code-window scenario validates it or the principal calls it done. Not S038's housekeeping to do.
- **Cross-window fallback.** If the principal ever opens a second VS Code window, the switchboard click should chain `vscode://` then `claude-focus://`. Skipped — current setup is single-window. Revisit when needed.
- **D-020 doc update.** S037 also left this open. The decision doc now needs (a) the process-tree-walk subsection from S037, *and* (b) the extension-as-in-window-focus addendum from S038. One pass covers both. Carried.
- **Lorebook drafts.** Three carried lessons want a draft: Windows PS5.1 ASCII discipline (S037), hook-fire-rate-as-budget (S032), and the new *"test against the user's actual topology"* lesson from this session. All three are *Windows-substrate-has-gotchas* in different flavors — could be one combined draft.

## Cascade

`developer-braindead/experiments/vscode-claude-focus/{package.json, extension.js, README.md}` (new), `developer-braindead/experiments/visualizer/index.html` (click handler + tooltip), `developer-braindead/quest-log/S038_*.md` (this entry), `developer-braindead/respawn.md` (refreshed).

## Main-brain changes

None.

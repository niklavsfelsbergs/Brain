# S037 — 2026-05-22 — Terminal switchboard Phase 3 (click-to-focus)

**Status.** In progress. Mechanism shipped and self-tested; live visual confirmation against a second VS Code window still pending.

## What landed this session

- **Sidecar registration re-enabled at lower frequency.** [[D-020_terminal_switchboard]] Step 1 decision: `UserPromptSubmit` + `Stop` + `SessionEnd` only (3 fires/turn, well below `emit-event.py`'s baseline). `_comment_status_sidecar` in `brain/.claude/settings.json` rewritten to document the new shape. PreToolUse / PostToolUse intentionally not registered — per-tool-call granularity wasn't load-bearing for the switchboard UX.

- **`claude_pid_chain` capture (Phase 3 prep).** `developer-braindead/.claude/hooks/status-sidecar.py` gained a `_ppid_chain()` helper using `CreateToolhelp32Snapshot` via ctypes — walks the process tree from `os.getppid()` up to a depth of 20, returns `[{pid, name}, ...]`. Cached per session on first fire; the snapshot is the most expensive thing the sidecar does. Record now carries both `claude_pid` (chain[0].pid for compat) and `claude_pid_chain`.

  Why the chain instead of a single PID: Claude Code spawns hooks via a short-lived shell wrapper (observed on this machine: two bash.exe layers above the Python hook). That wrapper exits seconds after the hook completes, so by the time the user clicks a switchboard row, `os.getppid()` points at a dead process. The chain captures every ancestor while they're still alive — focus-window.ps1 picks the first surviving Code.exe.

- **`focus-window.ps1` (new, ~150 lines).** Protocol handler for `claude-focus://<sid8>`. Reads the status file, iterates `claude_pid_chain`, calls `Get-Process` on each PID, picks the first live Code.exe with `MainWindowHandle != 0`. Restore-if-minimized, then `SetForegroundWindow` with the `AttachThreadInput` workaround (Windows since-2000 restriction). Fallback: if the chain walk yields nothing AND there's exactly one VS Code window alive, focus that. All errors swallowed to `~/.claude/status/focus.log`. **Pure ASCII source** — em-dashes had to be stripped after Windows PowerShell 5.1 mis-decoded UTF-8 bytes as cp1252 and broke the parse.

- **`register-claude-focus.ps1` (new).** One-shot HKCU registry write to register the URL scheme. Handler command line baked at register time — re-run if `focus-window.ps1` moves. Idempotent. Run once this session; registered successfully.

- **Visualizer sidebar click handler rewired.** `experiments/visualizer/index.html` row `click` listener now does `window.location.href = 'claude-focus://' + sid8`. **Shift-click** falls back to copy-sid8-to-clipboard (preserves the Phase-2 affordance for cases where the protocol handler isn't registered). Tooltip updated.

- **Sidecar `_detect_actor` refactor (parallel session).** Mid-session a parallel Braindead in another window changed `_detect_actor` from a hand-rolled candidate list to a glob over `*-<sid8>.txt` — drops the drift hazard with `emit-event.py`'s actor enumeration when new players land. Picked up the change on a re-read; aligned the chain edits around it. Also a new `_sweep_tmps()` for orphan `.tmp.<pid>` files, plus intent carry-forward that gates on matching actor (was pinning stale lines across actor transitions). All three improvements are sound and orthogonal to Phase 3 work.

## Self-test results

Focus script run manually against three sessions in the log (`~/.claude/status/focus.log`):

- **d7a364e5** (parallel Braindead, fresh-format) — chain depth 7, found Code.exe at depth 5, `SetForegroundWindow returned True`.
- **393ef3bd** (this session) — chain depth 7, found same Code.exe at depth 5 (single VS Code window on the machine, so all sessions land on the same hwnd right now), `SetForegroundWindow returned True (attached fg=True tgt=False)`.
- **e22e57d6** — old-format status file, no chain; script logged the diagnostic and exited cleanly.

The chain shape that landed for both new-format sessions: `bash.exe → bash.exe → claude.exe → powershell.exe → Code.exe → Code.exe (workspace, hwnd populated) → <unknown root>`. Two leading bash.exe layers — Claude Code's hook spawn path on this machine is `bash -c bash -c python` rather than the cmd.exe I'd guessed in the design doc. Notable but not load-bearing; the chain doesn't care which shell.

## What's still pending

- **Live visual confirmation against a second VS Code window.** The mechanism works in isolation (log shows `SetForegroundWindow returned True`), but with only one VS Code window open on the machine, "navigation" is a no-op visually — the target window is already foreground. Open a second VS Code window with its own `claude` session, send any prompt to populate its chain, then click that row from this visualizer. Expected: this window stays, that window comes forward.

- **The PowerShell-process flash.** Every protocol-handler invocation flashes a conhost briefly even with `-WindowStyle Hidden`. Polish item; suppression would require switching the handler from `powershell.exe` to either `wscript.exe` or a compiled launcher. Low priority.

- **Old-format sessions need a refresh.** Any session whose last hook fired before the sidecar edit has only `claude_pid`, no chain. Either send any message in those sessions (re-fires sidecar with new code) or just spawn fresh ones for the multi-window test.

- **D-020 doc update.** The decision doc still describes the original 5-event registration design and the original single-PID Phase 3 plan. Both have moved. Update the §"Hook wiring" and §"Phase build order" sections, plus add a §"Process tree walk" subsection capturing the chain rationale.

- **Lorebook draft on hook-fire-rate-as-budget.** Carried from [[S032_terminal_switchboard_phases_1_and_2]]; the option-1 decision provides the lesson but the draft hasn't been written.

## Files touched

- `brain/.claude/settings.json` — registered status-sidecar.py for UserPromptSubmit + Stop (kept SessionEnd); rewrote `_comment_status_sidecar`.
- `developer-braindead/.claude/hooks/status-sidecar.py` — `_ppid_chain()` added; record gains `claude_pid` + `claude_pid_chain`.
- `developer-braindead/.claude/hooks/focus-window.ps1` — **new**.
- `developer-braindead/.claude/hooks/register-claude-focus.ps1` — **new**. Run once.
- `developer-braindead/experiments/visualizer/index.html` — switchboard row click handler.
- `HKCU\Software\Classes\claude-focus` — URL scheme registered (machine state, not a file).
- `~/.claude/status/focus.log` — log file path established; safe to delete to reset.

## Observations to carry

- **Windows PowerShell 5.1 reads .ps1 files as cp1252 unless a UTF-8 BOM is present.** A single em-dash in a `Write-Log` string broke the parse — the three UTF-8 bytes were read as three cp1252 characters, swallowing the closing quote. **Discipline: pure ASCII for .ps1 scripts, or write with BOM.** Worth a lorebook draft (paired with the existing hook-frequency budget draft — both are "Windows substrate has gotchas the design doc didn't enumerate" lessons).

- **The chain-walk-at-fire-time pattern is the right shape for "I need an ancestor PID later" on Windows.** Parent PIDs are unstable: wrappers exit fast, PIDs get recycled, and `Get-Process -Id <dead>` returns nothing. Capturing the chain while everyone is alive sidesteps all of it. Same pattern could apply to other instrumentation that needs to retain process-tree facts across time.

- **"It works in the log" ≠ "the user saw it work."** First user feedback was "still just opens a terminal" — the mechanism was correct end-to-end, but with one VS Code window the visible effect was zero. Build the visible-effect test setup *into the test plan*, not after.

- **The conhost flash is the protocol handler's tax.** Not the script's bug. Plan for it explicitly when designing browser-triggered local actions.

## Next session — START HERE

1. Open a second VS Code window with a fresh `claude` session. Send any prompt to populate its chain.
2. From this window's visualizer (`http://localhost:8765/?live=1`), click that other session's row. Confirm the other window jumps forward and this one recedes.
3. If it works: update D-020 + write the hook-fire-rate / ASCII-PS lorebook draft + close out S037.
4. If it doesn't work: check `~/.claude/status/focus.log` for which Code.exe HWND it targeted; the chain capture might need disambiguation logic when multiple Code.exe siblings are alive.

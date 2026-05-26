# S032 — 2026-05-22 — Terminal switchboard (D-020 Phases 1 + 2)

A new instrumentation layer for parallel-session operation. Principal addressed Guthix to brainstorm "how do I know which of my five Claude Code terminals is waiting for me right now" — the question that the visualizer answers spatially but not temporally. Design surfaced as a three-phase switchboard; session pivoted into dev-brain and shipped Phases 1 + 2 end-to-end. A terminal-rendering incident mid-session forced a partial rollback of Phase 1's wiring; the code stayed on disk, only the high-frequency registrations were paused pending diagnosis.

## What shipped

- **[[D-020_terminal_switchboard]]** — full design captured: state machine (`working` / `waiting_for_user` / `idle` / `ended`), reader-derives-idle rationale, user-global file path at `~/.claude/status/<sid8>.json`, sidecar hook decoupled from `emit-event.py` for failure isolation, three-phase build order (sidecar → sidebar → click-to-focus), VS Code substrate constraints flagged, scope deferrals (sub-agent entries, click-to-focus, cross-machine).

- **Phase 1 — status sidecar.** `developer-braindead/.claude/hooks/status-sidecar.py` (new). Maps the four turn-bracketing events to states, writes atomic per-session JSON to `~/.claude/status/<sid8>.json`, includes a 24h sweeper that moves stale files to `~/.claude/status/archive/`. Actor detection by intent-file lookup; host detection from env (`vscode` via `TERM_PROGRAM` / `VSCODE_PID`, `windows-terminal` via `WT_SESSION`). All errors swallowed to stderr; never breaks a tool call. Validated live across 6 concurrent sessions — all three states caught in the wild on first run, including a real `waiting_for_user` Jebrim parked on a question for the principal.

- **Phase 2 — visualizer sidebar.** `developer-braindead/experiments/visualizer/index.html` gained a `<aside class="switchboard">` as a third flex child of `.world`, right of COMMS. ~280px wide, OSRS-themed (shared CSS pattern with `.logbox`). Polls a new `state-switchboard.json` snapshot every 2s and re-renders ages every 1s without re-fetching. Per-row: state dot, `Actor·N sid8`, age, italicized two-line-clamped intent. Sort order: waiting-for-user first (pulsing yellow), then working (green), then idle (gray), then ended (dimmed). Click copies sid8 to clipboard (Phase-3 hook point). `?sid8=<value>` URL param highlights "this" session with a gold outline.

- **Manifest mirror.** Status sidecar now also writes `developer-braindead/experiments/visualizer/state-switchboard.json` — a snapshot of every live status file. Architectural call: browser sandboxing precludes reaching `~/.claude/status/` directly; the mirror to the served viz dir is the minimum-disruption bridge (no custom server, no symlink). Hook derives the viz path from its own `Path(__file__).parent.parent.parent`, not the session's `CLAUDE_PROJECT_DIR`, so the brain-local viz dir is always the right target regardless of which repo the session was opened in.

- **Settings wired then partially rolled back.** `brain/.claude/settings.json` initially registered the sidecar for `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `SessionEnd`. Mid-session diagnosis of a stuck terminal-rendering state ruled hook frequency out as the root cause but left the four high-frequency registrations *paused* defensively until the actual cause is found — only `SessionEnd` remains live. A `_comment_status_sidecar` field documents the pause inline.

- **Comms entries.** `OPEN` at session start (declaring D-020 scope and steering clear of `index.html`), `UPDATE` mid-session when the principal redirected to Phase 2, `→ @braindead-f39b5b3f` ping before touching `index.html`. `CLOSING` lands at this step. The status sidecar caught a real-time signal that one of the "stale-intent" siblings I flagged at respawn (ab5ad0df) was actually alive — surfacing the limitation of intent-file-mtime as a liveness check.

## The terminal-rendering incident

Mid-session the principal noticed Claude Code's chat output rendering with character substitutions in the VS Code integrated terminal — lowercase Latin letters becoming DEC Special Graphics glyphs (`m` → `┘`, `r` → `┤`). Pattern matches a stuck terminal **character-set escape sequence** (`ESC ( 0` without a matching `ESC ( B` reset).

Diagnosis attempts:
1. **First hypothesis: hook fire frequency.** Manual invocation of both `status-sidecar.py` and `emit-event.py` confirmed neither writes anything to stdout/stderr in normal operation. But the new sidecar fired 2N+3 times per turn (vs `emit-event.py`'s ~N times), and high-frequency Python subprocess spawns on Windows + VS Code's terminal are a known interaction. Disabled the four high-frequency registrations; killed two leftover `http.server 8765` processes for hygiene.
2. **The disable didn't fix the corruption** — which was expected if the stuck state was character-set-escape-based (terminal state persists regardless of process activity), but it also means hook frequency wasn't the cause.
3. **Best diagnosis offered:** something emitted `ESC ( 0` into the terminal stream and never emitted the reset. Best guess at source: a Claude Code TUI rendering edge case, not anything written to disk. Fix is a fresh terminal — close the corrupted tab, open new.

Outcome: status sidecar retains only its `SessionEnd` registration; the per-turn / per-tool-call registrations are paused pending diagnosis. The sidebar pane still renders because *other* sessions' hooks were running before the registration change and their files persist. The principal will handover to a fresh agent in a clean terminal to continue.

## Why this came together now

The principal's question came framed as "I have N terminals open, how do I know which one wants me" — exactly the question that emerges once D-017's parallel-instances + D-019's parallel-Braindead pattern goes from "thing that ships" to "default operating mode." The visualizer answers "where in the brain is each actor," not "is this actor currently waiting on me." Different question, different surface — the sidebar belongs next to COMMS, not on the canvas.

The decoupled hook script (vs. extending `emit-event.py`) was the right call given the terminal incident — the visualizer pipeline kept working through the diagnosis cycle because the two scripts have no shared state. The architectural value paid off the same day it was chosen.

The user-global file path (vs. project-local) was correct in spirit but premature in execution: the hook is only *registered* in `brain/.claude/settings.json`, so only brain sessions write status files. To get true cross-repo visibility, the hook needs to move to `~/.claude/settings.json` (user-level). The status file path was designed for that future; only the registration needs to migrate. Punted as out of scope for first cut, but flagged in D-020.

## Observations to carry

- **High-frequency hooks on Windows + VS Code integrated terminal are a hazard, even when silent.** Disabling didn't fix the active corruption, so hook frequency wasn't the cause of *this* incident, but the asymmetry — `emit-event.py` fires ~N times per turn and has been stable for weeks; `status-sidecar.py` at 2N+3 fires per turn was added without a frequency budget check — is the kind of thing worth a lorebook draft. *Treat hook-fire rate as a constrained resource on Windows; budget against the existing baseline before adding another script.*

- **Decoupled hook scripts paid off in real-time.** When the registration of one hook needed to be partially rolled back, the other's behavior was untouched and the visualizer kept running through the diagnosis. The "shared file, separate processes" pattern is strictly better than "one script does everything" for failure isolation. Same logic suggests Phase 3's window-focus helper, when it lands, should also be a separate script.

- **Status sidecar is a strictly stronger sibling-liveness signal than intent-file mtime.** At respawn I flagged `ab5ad0df` as a potential `ABANDONED` candidate because their intent file was 9 minutes stale; the sidecar showed them very-much-alive (their last hook fire was 5 seconds ago, intent had been updated since I read it). The comms ritual's sibling-detection check (D-019 §3) could swap from `intent-file mtime <5min` to `status-sidecar state ≠ ended AND last_event_ts <5min` once the sidecar stabilizes — strictly stronger.

- **"Cross-repo" is a registration question, not a file-path question.** Putting status files at `~/.claude/status/` was correct, but only sessions whose hook *fires* can populate the dir, and the hook only fires for sessions whose settings.json includes it. The visibility scope is the *intersection* of "where the file lives" and "where the hook runs" — and the latter is the binding constraint. Worth keeping in mind when designing user-level instrumentation.

- **`Guthix mode` and dev-brain mode aren't isolated.** The principal started this session by invoking Guthix outside of bankstanding ("you are the god, you can do anything"). Guthix offered the design; the principal then pivoted into dev-brain to build it. Worth pattern-noting: design conversations with Guthix can naturally bridge into dev-brain construction sessions, with the design memory carried in chat rather than a bankstanding `proposals/` entry. Not a problem, just a transition pattern worth recognizing.

## Cascade

Dev-brain files landed:
- `bank/decisions/D-020_terminal_switchboard.md` (new).
- `.claude/hooks/status-sidecar.py` (new).
- `experiments/visualizer/index.html` (switchboard pane: CSS + aside markup + IIFE poller).
- `experiments/visualizer/state-switchboard.json` (generated, not source — but lives in the served tree).
- `quest-log/S032_terminal_switchboard_phases_1_and_2.md` (this file).
- `respawn.md` (overwritten at close).
- `comms/active.md` (OPEN + UPDATE + → @ ping + CLOSING).

## Main-brain changes

- `brain/.claude/settings.json` — registered the sidecar, then partially paused its registrations. The settings file lives at brain root (not gielinor proper); change is dev-brain-instrumentation-scoped, not a cognitive-layer touch.

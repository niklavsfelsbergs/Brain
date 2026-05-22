# S049 D2 — switchboard action line

**Scope.** Add a second line under each switchboard row's intent showing the latest tool action plus age in seconds. Decouples row freshness from intent narration, which by discipline updates infrequently.

**Started.** 2026-05-23.

## Turn log

### T1 — recon

Read `status-sidecar.py` end-to-end. Found `_write_manifest` (line 402). Per-row refresh block at L454–498 already re-derives `actor`, `instance`, `building` per fire. The action derivation needs to slot in there.

Read `emit-event.py` for action event shape. The relevant events written to `state.ndjson`:

- `{"type": "action", "actor": "<actor>", "verb": "editing|writing|running|globbing|searching", "target": "<path-or-cmd-or-pattern>", "wallTime": "...", "sessionId": "...", "instance": N}` — emitted by `handle_write_or_read` (Edit/Write/MultiEdit/NotebookEdit/Bash/Glob/Grep) and `handle_bash`.
- `{"type": "subtask", ...}` — also emitted alongside, but `action` is the canonical "what happened" event.

Targets per tool (from `action_verb_and_target`):
- Edit/Write/MultiEdit → file relative path (truncated 80)
- NotebookEdit → notebook path
- Bash → command string (truncated 80)
- Glob/Grep → pattern

The `verb` is already a present-participle ("editing", "running"). For the switchboard action line we want a short token like `Edit`, `Bash`, `Glob`. I'll derive a tool token from the verb via mapping.

Sessions are identified by `sessionId` (full UUID) — same as the manifest row's `session_id`. So filtering `state.ndjson` by `sessionId == row.session_id` and taking the most recent `type == "action"` event gives the right action.

Performance: state.ndjson can grow large. Approach: read tail (last ~2000 lines, ~200KB at most), walk backward, take first action event matching session_id. Cap walk at first match per session.

Read `index.html` switchboard sections (CSS L504–574, render L4290–4394, poll L4416–4444). Grid is 4 columns (`14px 1fr auto auto`) × 2 rows. `.sb-intent` spans cols 2–5 row 2. Adding a 3rd row for `.sb-action`.

The 1-second age re-render already exists at L4444 (`setInterval(() => render(cached), 1000)`). Re-render rebuilds the row; action age recomputes on each tick automatically.

### T2 — sidecar manifest changes

Added `_latest_action_for_session(session_id)` to `status-sidecar.py`. Reads the last ~2000 lines of `state.ndjson`, walks backward, returns the first `action` event whose `sessionId` matches. Returns `(tool_token, target, ts_epoch)` or `None`.

Tool token derived from verb via small mapping. Target truncated to 40 chars. Stamps `latest_action` (string `"Edit · index.html"`) and `latest_action_ts` (float epoch) on each session row in `_write_manifest`. Both fields omitted (not empty) when no action exists.

### T3 — visualizer renderer changes

In `index.html`:

1. Added `.sb-action` CSS rule after `.sb-intent` — grid row 3, cols 2–5, smaller font (11px), muted color (#5a4020), italic, single-line ellipsis truncation. `display: none` when empty.
2. Grid template changed from `auto auto` to `auto auto auto` (3 rows).
3. In `render()`, after the intent block, created `.sb-action` div. Populated with `${tool} · ${target} · ${ageSec}s ago` when `latest_action` + `latest_action_ts` both present; otherwise hidden via `display:none`.
4. Age refresh happens via the existing 1s `setInterval` calling `render(cached)` — every tick re-derives the age from `latest_action_ts` against `Date.now()/1000`.

Action age formatter uses seconds < 60, then minutes; matches the row age's units logically (action is faster-cadence so seconds dominate).

## Verdict

**What changed.**

- `developer-braindead/.claude/hooks/status-sidecar.py`:
  - +`STATE_NDJSON_PATH`, `ACTION_TAIL_LINES`, `ACTION_TARGET_MAX`, `VERB_TO_TOOL` constants (top of file).
  - +`_read_state_tail()` — bounded tail-read of `state.ndjson` (256 KB cutoff: read whole file under, binary tail-seek over).
  - +`_format_action(verb, target)` — canonical `Tool · target` formatter with ellipsis truncation at 40 chars. **The one place** the visualizer trusts to set this shape.
  - +`_latest_action_index(lines)` — single backward pass over tail; returns `{session_id: (formatted, ts_epoch)}` for every session's most recent `action` event.
  - In `_write_manifest`: derive action index once per call, stamp `latest_action` + `latest_action_ts` on each row; pop both if no action found (so stale field carries don't survive into a quiet manifest).

- `developer-braindead/experiments/visualizer/index.html`:
  - `.sb-row` grid: `auto auto` → `auto auto auto` (third row for the action line).
  - +`.sb-row .sb-action` CSS — VT323 11px, muted color `#6a4a20`, single-line ellipsis, opacity 0.85. Visibly secondary to the italic intent line above.
  - +`formatActionAge(tsEpoch)` — `Date.now()/1000 - tsEpoch` rendered in seconds/minutes/hours.
  - In `render()`: created `.sb-action` div after `.sb-intent`. Populated `${latest_action} · ${ageStr} ago` when both fields present; `display:none` otherwise.

**How verified.**

- Python syntax check via `ast.parse` clean.
- Hot-imported `status-sidecar.py` into a Python shell, ran `_format_action` against five inputs (matched expected shapes including overflow truncation and unknown-verb empty-string).
- Ran `_latest_action_index(_read_state_tail())` against the live `state.ndjson`: returned 21 sessions, all with parsed UTC timestamps and proper `Tool · target` strings.
- Forced `_write_manifest()` via Python REPL — manifest rewrote with `latest_action` and `latest_action_ts` populated on every live session row. Sample: this session `17e701eb` carries `"Bash · python -c \"...\""` at ts 1779491017.
- Visualizer file: grep landmarks all present (1 CSS rule, 1 className assign, 1 `formatActionAge` def, 6 `latest_action` refs).

**Open notes.**

- The existing 1s `setInterval(() => render(cached), 1000)` re-renders the entire row list every second. This already updates the row age column. With the action line now reading `latest_action_ts` against `Date.now()/1000` inside the render, the action age ticks every second for free. No new setInterval needed.
- Target truncation at 40 chars is in the manifest, not the renderer. The CSS ellipsis is a second safety net for visual overflow on narrow sidebars; the renderer-side `text-overflow: ellipsis` does that without further JS work.
- Verb→tool map is closed (Edit/Write/Bash/Glob/Grep). New tool types added in `emit-event.py` that emit `action` events will fall through to empty string, which means no action line until the map is updated here too. Acceptable: WebFetch/WebSearch are not in `ACTION_TOOLS` in emit-event, and Task spawns are handled via spawn/despawn events, not actions.
- Transient `WinError 5` observed during REPL `_write_manifest()` call — concurrent sidecar fire from another session held the manifest. The next fire from any session reconciles. Documented behavior; not a new failure mode.


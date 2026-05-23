# brain/switchboard/ — the observability surface

> Promoted from `developer-braindead/experiments/visualizer/` in S052 (2026-05-23).
> The map was killed; switchboard + chat are the load-bearing surfaces.
> Lives at brain root because it observes both brains (gielinor sessions and
> dev-brain Braindead sessions).

## What it is

Two panels side by side:

- **Switchboard (left, 280px wide).** One row per live Claude Code session,
  polled from `state-switchboard.json`. Per-row: actor name, instance, state
  chip (WORKING/WAITING/CLOSING/IDLE/ENDED), age, and a ≤100-char subtitle of
  what it is actually doing. Click to focus the session's VS Code window;
  shift-click copies the sid8.
- **Chat (right, fills remaining width).** Append-only event stream rendering
  three sources: (a) gielinor + dev-brain `comms/active.md` mirrors for
  inter-session coordination, (b) `chat.ndjson` for human-language tool-call
  summaries emitted by the hooks, (c) intent-narration changes (also via
  `chat.ndjson`, kind=`intent`). Speaker tab filters, jump-to-latest pip,
  per-tab unread badges.

## How to run

Live mode (the one that matters):

1. `cd brain/switchboard`
2. `python -m http.server 8765`
3. Open `http://localhost:8765/?live=1`
4. Append `&sid8=<your-sid8>` to highlight "this" session with a gold outline.

Without `?live=1` the page renders an inert shell — no fetches, no polling.
Useful for inspecting layout without a running hook.

Replay mode is gone with the map.

## Files

- `index.html` — shell + layout, mounts the two panels. No inline JS or CSS.
- `styles.css` — every rule, in one place.
- `app.js` — entry; reads URL params, kicks off both panels.
- `state.js` — shared derivation helpers (`deriveSessionState`, `sbAgeSec`,
  `SB_IDLE_AFTER_SEC`, `SB_CLOSING_RX`, `formatWall`).
- `switchboard.js` — left panel: polls `state-switchboard.json`, sorts, renders
  rows, handles row clicks via `focus.js`.
- `chat.js` — right panel: polls comms mirrors + `chat.ndjson`, renders entries
  through a unified `appendLogEntry`. Owns scroll-lock, jump-to-latest, tab
  filter, and unread badges.
- `focus.js` — `dispatchFocus(sid8)` (VS Code `claude-focus://` URI) +
  `copySid8(sid8)`.
- `path-map.json` — still load-bearing for `emit-event.py` (hook side classifies
  paths into buildings even though the map is dead — the classification
  contributes to the `chat.ndjson` action text). Don't touch from here.
- `_README.md` — legacy map-era README. Kept as historical context; the
  load-bearing spec is this file.

## Data sources (live mode)

All written by hooks; the switchboard is a passive renderer.

- `state-switchboard.json` — per-session manifest; polled every 2 s.
  status-sidecar.py writes one record per `sid8`, including a `subtitle` field
  (≤100 chars, human-language). The switchboard row uses that as its
  second-row text.
- `state-comms-gielinor.md`, `state-comms-braindead.md` — mirrors of the two
  brains' `comms/active.md` files; polled every 3 s. Headers parsed
  (`[ts] actor-sid8 KIND`); bodies collapsed by default, click header to
  expand.
- `chat.ndjson` — append-only stream of human-language tool-call summaries
  and intent narration; polled every 2 s. Each line is a JSON object with at
  minimum `{ ts, kind, actor, text }`. Recognized kinds: `action`, `intent`,
  `commit`, `narrate`, `system`; unknown kinds render as plain chat lines.
  Render history is capped at 500 entries — older entries drop off the top.

## URL params

- `?live=1` — enable polling. Anything truthy also accepted (`?live`).
- `?sid8=<id>` — highlight the row for this session (gold outline + "(this)"
  label).

## Related decisions

- D-009 — visualizer initial design (pre-S052; map era).
- D-020 — terminal switchboard.
- D-024 — parallel player coordination + comms shape (the `state-comms-*.md`
  mirrors are this).
- D-025 — visualizer character lifecycle audit findings.
- S052 quest log — the rebuild.

## What it's NOT

- Not a cognitive layer. It writes nothing into either brain; it only renders
  state that hooks already wrote.
- Not in either brain's namespace. It's brain-root infrastructure.
- Not part of the visualizer family anymore. The map is dead; the
  SVG-and-sprite era was a long detour, well-archived in git history.

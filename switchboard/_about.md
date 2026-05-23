# switchboard/ — the observability surface

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

Two servers, pick by whether you want the embedded terminal:

**A. Observability only** (no terminal, zero deps):

1. `cd switchboard` (from repo root)
2. `python -m http.server 8765`
3. Open `http://localhost:8765/?live=1`

**B. Observability + embedded agent chat** (S060 — talk to `claude` in-app via
the ▶_ toggle):

1. One-time: `python -m venv switchboard/.venv` then
   `switchboard/.venv/Scripts/python.exe -m pip install pywinpty aiohttp`
2. `switchboard/.venv/Scripts/python.exe switchboard/server.py`
3. Open `http://localhost:8765/?live=1`, click ▶_ in the switchboard header.

`server.py` serves the same static files **plus** the WebSocket bridges. Both
servers bind `127.0.0.1:8765` — run one or the other, not both. The static
surface stays GET-only in both; only the `/chat` and `/pty` sockets accept input.

Append `&sid8=<your-sid8>` to highlight "this" session with a gold outline.
Without `?live=1` the page renders an inert shell — no fetches, no polling.
Replay mode is gone with the map.

## Embedded agent chat (S060)

The ▶_ button toggles a third panel — **not a terminal**, a chat UI. A left rail
holds **one pill per conversation** (`+` new, `×` end); each pill is a live
`claude` rendered as a conversation: user bubbles, streamed assistant text,
tool-call cards, an input box. The terminal look is gone because we don't run
claude's TUI — we drive it **headless** over the stream-json protocol and render
the structured events ourselves.

**How.** `server.py`'s `/chat` socket spawns `claude -p --input-format
stream-json --output-format stream-json --include-partial-messages --verbose
--permission-mode bypassPermissions --session-id <uuid>` (clean pipes, not a
PTY) at the **brain root** — so `brain/.claude/settings.json` is picked up and
each conversation lands on the switchboard board like any other session.
Streaming-input mode keeps one process alive for the whole multi-turn chat.
`terminal.js` parses the events: `stream_event`/`text_delta` → live text;
`assistant` → authoritative content + tool cards; `user`/`tool_result` → fills
a card; `result` → turn-end divider (cost · duration).

**Click-to-navigate.** The server mints the session UUID (`--session-id`) and
announces the `sid8` to the browser, so each pill knows its sid8 — a click on
the matching switchboard row jumps to that conversation. Wiring: `terminal.js`
registers a resolver with `focus.js`; the row's `dispatchFocus(sid8)` tries it
before falling back to the VS Code `claude-focus://` URI. Panels stay decoupled
(switchboard.js never imports terminal.js).

- Only hosts sessions **the switchboard launches** (the headless process is the
  switchboard's child). Existing VS Code sessions still use row → window focus.
- No CDN dependency — the renderer is plain DOM + a small markdown helper.
- Runs with `bypassPermissions` (matches the operator's existing setup) so tools
  execute without interactive approval. Localhost-only socket.
- Wire protocol: server→client JSON frames — `{t:session}` once, then
  `{t:event,ev}` (raw claude stream-json events), `{t:stderr,d}`, `{t:exit,code}`;
  client→server `{type:input,text}`.
- `/pty` (xterm + ConPTY raw terminal, slices 1–2) remains in `server.py` as a
  latent raw-shell option; the client no longer wires it.
- Next: session persistence across page reload; thinking-block display; the
  observer→interactor `D-NNN`.

## Files

- `server.py` — static file server (GET-only) + `/chat` (headless claude,
  stream-json) and `/pty` (raw PTY) WebSocket bridges (S060). Run from
  `switchboard/.venv`. Spawns at brain root.
- `terminal.js` — embedded agent-chat panel: rail of conversations, stream-json
  event rendering (bubbles / tool cards / input), sid8 click-to-navigate.
  Imported by `app.js`. (Filename kept; it drives the "TERMINAL" panel.)
- `index.html` — shell + layout, mounts the two panels. No inline JS or CSS.
- `styles.css` — every rule, in one place.
- `app.js` — entry; reads URL params, kicks off both panels.
- `state.js` — shared derivation/format helpers (`deriveSessionState`,
  `sbAgeSec`, `SB_IDLE_AFTER_SEC`, `SB_CLOSING_RX`, `formatWall`,
  `formatMinute`, `shortenPaths`, `humanizeAction` — the last maps a humanized
  action line to a verb glyph + color class + cleaned body + isCommit flag).
- `switchboard.js` — left panel: polls `state-switchboard.json`, sorts, renders
  rows (state chip, subtitle, per-row activity sparkline, WAITING hero),
  handles row clicks via `focus.js`, dispatches `sb-hover` for the chat
  actor-flash, builds the roster legend. Double-click a row name to rename the
  session — labels persist in browser localStorage (`sb-session-names`, keyed by
  sid8; the server is GET-only, so renames can't write a file). Re-render pauses
  while a rename input is open.
- `chat.js` — right panel: polls comms mirrors + `chat.ndjson`, renders entries
  through a unified `appendLogEntry`. Owns scroll-lock, jump-to-latest, tab
  filter, unread badges, the per-minute time-rail, speaker-run collapsing,
  action verb-glyphs, commit drop-banners, live search, and the two-way
  actor-flash (responds to the switchboard's `sb-hover` event).
- `focus.js` — `dispatchFocus(sid8)` (VS Code `claude-focus://` URI) +
  `copySid8(sid8)`.
- `activity.js` — shared per-session event-cadence ring buffer. `chat.js`
  records each `chat.ndjson` event into it; `switchboard.js` reads
  `activityBuckets(sid8)` back to draw each row's sparkline. Decoupled — the
  two panels never import each other, only this module.
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
- `?crt=1` — enable the CRT/scanline overlay on load (also toggleable at
  runtime via the ▦ CRT button, bottom-left).

## Action-text quality (source-side)

The chat panel's action lines are only as clean as `chat.ndjson`.
`emit-event.py:_humanize_tool_call` strips a leading `cd <repo>` from Bash
commands before classifying (the brain runs most git work as `cd <repo>\n<cmd>`,
which otherwise defeats every git phrasing and eats the display budget),
shortens repo-root paths, and pulls a commit subject out of `-m`/heredoc forms.
`state.js:humanizeAction` re-applies the same cleanup client-side as a fallback
(and to clean historical lines), then adds the verb glyph + color.

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

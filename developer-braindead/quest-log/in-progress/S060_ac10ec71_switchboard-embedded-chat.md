# S060 — switchboard embedded agent chat

**Session** ac10ec71 · 2026-05-23 · Braindead (dev-brain mode)

> Renumbered S058 → **S060** at close — siblings shipped S058 (in-voice
> narration, `4af5279`) and S059 (ALCHING/WRAPPED-UP states) during this session.

## Ask

Principal (entering dev-brain): *"Would it be possible to prompt you through a
terminal inside the switchboard app instead of vscode?"*

## What happened

1. **Feasibility framing.** Answered: yes, but it's an observer→interactor
   crossing, and it only works cleanly for sessions the switchboard **launches
   itself** — an existing VS Code session lives in a PTY VS Code owns, and there
   is no PTY-attach on Windows (those keep the D-020 Phase 3 click-to-focus).
   Surfaced the direction fork → principal chose **host new sessions in-app**.
2. **Stack fork.** Probed the box: Node v25.9 / npm 11 / Python 3.13, no
   pywinpty. Recommended **Python (pywinpty + aiohttp)** over Node — matches the
   all-Python hook tooling and dodges a node-pty native compile against the
   bleeding-edge Node 25 ABI. Principal picked Python.
3. **Built slice 1:**
   - `switchboard/.venv` + `pip install pywinpty aiohttp` (cp313 wheels, no MSVC).
     pywinpty 3.0.3, aiohttp 3.13.5.
   - `server.py` — aiohttp static (GET-only, traversal-guarded) + `/pty`
     WebSocket↔PTY bridge. Spawns `powershell.exe -NoLogo` at **brain root**
     (cwd → settings.json picked up → session lands on the board), auto-types
     the `?launch=` command. Reader thread → asyncio.Queue → ws; client sends
     JSON `{type:input|resize}`.
   - `terminal.js` — lazy xterm.js (CDN, on first open, try/catch so a CDN
     failure can't break the other panels), FitAddon, WS wiring. Imported by
     `app.js`.
   - `index.html` — ▶_ toggle in switchboard header + third `.terminalbox`
     panel (hidden until `.open`). `app.js` calls `initTerminal()`.
   - `styles.css` — `.terminalbox` chrome matched to `.logbox`; cache-buster
     `?v=9` → `?v=10`.
   - `.gitignore` — `switchboard/.venv/` + `_smoketest.py`.
   - `_about.md` — run instructions (two-server choice) + terminal section + file
     list.
4. **Verified headless.** `_smoketest.py`: static serve OK (index.html +
   terminal.js with `text/javascript` MIME), PTY round-trip OK (`echo` marker
   returned 2× — echoed input + output), resize accepted. Stopped the test
   server (freed :8765 for the principal).

## Slice 2 — multi-terminal + click-to-navigate

Principal after slice 1 went live: *"works! I need to be able to operate
multiple ones and also navigate to them by clicking on the switchbar."*

- **Session id is now minted server-side.** `claude` supports `--session-id
  <uuid>` (confirmed via `claude --help`). `server.py` generates a uuid per
  `/pty` connection, launches `claude --session-id <uuid>`, and **announces**
  `{t:session, sessionId, sid8}` to the browser as frame #1. Wire protocol moved
  to JSON both ways (server→client `{t:session}` then `{t:out,d}`).
- **Multi-terminal** (`terminal.js` rewrite): tab strip, `+` spawns, `×` ends.
  Each tab = own xterm + own WS + own PTY. Panes overlay absolutely; only the
  active one is shown (so FitAddon measures full size). Tab dot encodes WS state.
- **Click-to-navigate:** `focus.js` gained `registerInAppFocus(fn)`;
  `dispatchFocus(sid8)` tries the in-app resolver before the VS Code URI.
  `terminal.js` registers `focusBySid8` → opens panel + activates the matching
  tab. switchboard.js untouched (still only imports focus.js → panels stay
  decoupled). Match works because `--session-id` ⇒ `CLAUDE_CODE_SESSION_ID` ⇒
  the sidecar keys the row by the same sid8.
- index.html header → tabs + `+`; styles.css → `.term-tabs/.term-tab/.term-
  stack/.term-pane`; cache-buster `?v=10` → `?v=11`.

## Slice 2.5 — UX iterations (principal-driven)

- Pills moved from a horizontal header strip to a **vertical rail** on the left
  of the panel (xterm to the right). `+ new` to the header right.
- Reskinned the xterm to a warm-dark OSRS palette (aged-wood bg, parchment ink,
  gold cursor, full ANSI retuned), beveled pills, themed scrollbar.
- Font 17 → 22px.

## Slice 3 — "make it not look like a terminal" → headless chat UI

Principal: *"is it possible to make it not look like a terminal?"* → chose the
full chat-UI rebuild. **Key reframe:** the terminal look is claude's own TUI, not
our chrome — so the fix is to stop running the TUI and drive claude **headless**.

- **Probed the real stream-json schema** (ran one headless turn) before coding
  the parser: `system/init`, `stream_event`(message_start / content_block_start
  / content_block_delta{text_delta,input_json_delta} / message_stop), authoritative
  `assistant`, `user`/`tool_result`, `result`(cost,duration). `claude` resolves
  to a native `.exe` (`~/.local/bin/claude.EXE`) → spawn directly, clean pipes,
  no shell/PTY.
- **Server `/chat`** (`server.py`): `asyncio.create_subprocess_exec` of `claude
  -p --input-format stream-json --output-format stream-json
  --include-partial-messages --verbose --permission-mode bypassPermissions
  --session-id <uuid>` at brain root. Pumps stdout lines → `{t:event,ev}`, stderr
  → `{t:stderr}`, exit → `{t:exit}`; client `{type:input,text}` → writes a
  stream-json user message to stdin. Streaming-input keeps the process alive for
  a multi-turn conversation. `/pty` kept as a latent raw-terminal option.
- **Client** (`terminal.js` rewritten, **xterm/CDN removed**): per-conversation
  chat DOM — user/assistant bubbles, live `text_delta` streaming, tool-call cards
  (name + summarized input + result, error-tinted), turn-end divider (cost·time),
  thinking pulse, small built-in markdown (code fences/inline/bold/links). Rail +
  sid8 click-to-navigate carried over unchanged.
- **Skin** (`styles.css`): chat mirrors the COMMS panel — parchment message area,
  dark RuneScape-font ink, gold user bubble / parchment assistant card, dark code
  blocks, gold Send button, parchment input. `?v=13` → `?v=14`.

## Verified

- Slice 1: PTY bridge round-trip + static serving, headless. ✅
- Slice 2 (headless): static; `session` frame with valid 8-char sid8; **two
  connections get distinct sids**; PTY round-trip over JSON framing. ✅
- Slice 3 (headless): static; `/chat` session announcement; a real headless turn
  streamed `text_delta` and returned `result` = `'hello there friend'`. ✅
  Client-side rendering (bubbles/tool-cards/markdown) is browser-only — unverified
  until the principal hard-refreshes.

## Open / next

- **Live browser verify (principal-side):** run `server.py` from the venv, open
  `?live=1`, click ▶_ — confirm (a) xterm renders + CDN loads, (b) `claude`
  auto-launches in the PTY, (c) **a new switchboard row appears** for that
  session (the payoff: terminal next to its own row), (d) ⟳ relaunches.
- **D-NNN** — record the observer→interactor crossing once the slice is
  live-confirmed. The switchboard was deliberately "writes nothing"; `/pty`
  changes that (localhost-only shell-spawning ws).
- **Follow-ons:** session persistence across page reload; thinking-block
  display; mid-turn cancel/stop; richer markdown; collapse long tool results;
  consider `acceptEdits` vs `bypassPermissions` toggle in the UI.

**Quest status: OPEN** — slices 1–3 shipped + headless-verified; client-side
render (chat bubbles / tool cards / markdown) is browser-only, awaiting principal
eyeball. Will iterate. Stays in `in-progress/`.

**Cascade.** `switchboard/` (new `server.py`, `terminal.js`; modified
`index.html`, `styles.css`, `app.js`, `focus.js`, `_about.md`), `.gitignore`,
this quest-log entry, `developer-braindead/respawn.md`.

**Main-brain changes.** none — `switchboard/` is brain-root infra, not
`gielinor/`. No writes crossed into the main brain.

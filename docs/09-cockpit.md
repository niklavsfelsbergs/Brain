# 09 — The cockpit: how you drive the brain

Everything above describes the brain *at rest* — its layers, rules, and rituals. This page
is about **operating** it: the cockpit is the console you run the fleet of sessions from.
It is one section by design — a code-level cockpit manual lives in
[`cockpit/_about.md`](../cockpit/_about.md); this is how it *enables working with the
brain*.

## What it is

The cockpit ([`cockpit/`](../cockpit/)) is a standalone **desktop window** — a single
Python process (`pywebview` + an `aiohttp` backend + the claude driver, all in
[`app.py`](../cockpit/app.py)) that launches and dies as one unit. It is the from-scratch
rebuild of the earlier `switchboard/` map+client ([D-028]); launch it from the
Desktop/Start-menu icon ([`Switchboard.vbs`](../cockpit/Switchboard.vbs)).

It is, deliberately, **not** a dashboard bolted next to VS Code and **not** a headless
agent runner. It is the place you watch and steer multiple live Claude Code sessions —
players, Guthix, Braindead, their sub-agents — at once.

## The three surfaces, over one session model

The anti-accretion discipline: all three views project from a *single* normalised session
model ([`build_session_model()`](../cockpit/backend.py)), not three independent data paths.

- **Fleet board** (left) — every live session plus nested sub-agents, state at a glance,
  click to open. State colours track the [D-029] two-axis vocabulary: `needs_you` /
  `your_move` (the two "ball in your court" states that drive the attention count and
  pings), `busy`, `idle`, `done`, `ended` — with flavour (alching / crew / wrapped-up)
  riding as tags. ([`web/board.js`](../cockpit/web/board.js))
- **Session console** (centre) — drive a cockpit-launched session live over the terminal
  (prompt / stream / Stop / release), with a **fixed compose-bar** below the PTY so you can
  scroll history while typing, and a **terminal ⇄ transcript toggle**: the transcript
  renders the same session's `/history` as clean, selectable DOM (markdown + collapsible
  tool cards and per-turn / per-tool-output / copy-all buttons) so copied text isn't sheared
  by the xterm grid — the PTY stays the engine underneath, the transcript is a read/copy
  skin. VS Code-hosted sessions appear as a read-only peek.
  ([`web/console.js`](../cockpit/web/console.js), [`web/term.js`](../cockpit/web/term.js),
  [`web/transcript.js`](../cockpit/web/transcript.js), [`web/fleet.js`](../cockpit/web/fleet.js))
- **Activity feed** (right) — lifecycle checkpoints and comms across the fleet; raw actions
  off by default; click an item to jump to its session. ([`web/feed.js`](../cockpit/web/feed.js))

## How it connects to the brain

The cockpit is strictly a **reader** of the hook contracts — the
[observability hooks](08-enforcement-and-hooks.md) are untouched by the rebuild and still
write into [`switchboard/`](../switchboard/). The backend reads:

- `state-switchboard.json` — the session manifest (the model's backbone).
- `state-{dwarves,gnomes,penguins}.json` — to nest pending sub-agents under their parent.
- `state.ndjson` — tail-read for a fresh action heartbeat (the manifest's frozen action
  timestamp goes stale during ordinary-tool turns).
- `chat.ndjson` — lifecycle stream for the feed.
- `state-comms-{gielinor,braindead}.md` — comms mirrors, parsed into feed items.
- `state-names.json` — disk-backed board renames (shared with the `/rename` hook).

So the loop closes: hooks emit state as sessions work → the cockpit renders it → you click a
row → you're driving that session. The cockpit decays/greys stale rows itself but does not
invent state; the *vocabulary* is hook-derived. (Two reader-side rules worth knowing: a
quiet `your_move` past 5 min drops out of the attention tally; and there is a deliberate
refusal to re-add a timeout-based busy→idle decay — it false-tripped genuine long
analytical turns, so cancellation is detected from the actual Esc keystroke, never inferred
from silence.)

## How it drives a session — and why over a real PTY

The live drive path is [`ptybridge.py`](../cockpit/ptybridge.py) (the `/pty` WebSocket). It
spawns a **real PowerShell PTY** (`winpty`) with `cwd` = brain root and runs `claude
--session-id <uuid>` *interactively* inside it, piped to the xterm.js terminal in the
window. One WebSocket ⇄ one PTY ⇄ one claude session. Because cwd is the brain root, the
session picks up [`.claude/settings.json`](../.claude/settings.json) and lands on the fleet
board like any other. The bridge strips leaked VS Code env vars and stamps
`CLAUDE_COCKPIT=1` so the hook attributes the session to host "cockpit." The `/pty`
endpoint is RCE-sensitive, so it's gated by a per-process token plus an Origin check
(hardened in [S085]).

**Why a real interactive terminal rather than headless?** This is the load-bearing design
reason and worth stating plainly:

> As of **2026-06-15**, Anthropic moved headless `claude -p`, the Agent SDK, and GitHub
> Actions onto a metered API-credit pool — those no longer count toward the Claude
> subscription. *Interactive* Claude Code in a terminal stays on the subscription. So the
> cockpit deliberately abandoned its original headless `/chat` driver and pivoted to driving
> a genuine interactive terminal session.

The PTY route also gets two things headless never could: **Esc cancels a turn** natively,
and **`AskUserQuestion` / `ExitPlanMode` / permission prompts work** because there is a real
TTY (headless auto-dismissed them with an unanswerable error).

## Stack, in one line

Backend: Python + `aiohttp`, assets served `Cache-Control: no-store`. Frontend: Preact +
`htm` via an ESM import map — no build step; xterm and a fit-addon vendored under
`web/vendor/`. Shell: `pywebview`. A relaunch is needed to pick up backend/JS changes (the
running window holds stale code).

---

Next: **[10 — The dev brain](10-dev-brain.md)** — where this very documentation was built.

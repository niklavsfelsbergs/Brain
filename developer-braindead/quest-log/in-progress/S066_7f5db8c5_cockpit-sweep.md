# S066 — cockpit sweep (first review since the S064 rebuild)

**Session:** braindead-7f5db8c5. **Mode:** dev-brain. **Surface:** read-only
sweep — no cockpit files touched (two siblings live-editing: [[S065]]
bfa95764 + f1df4fa5).

## The ask

Principal, in dev-brain: *"The terminal is buggy. I cant cancel with esc, i
couldnt answer when questions came up. Likely more stuff that doesnt work. Do an
investigation on whats put together, there hasnt been a sweep done."*

The "terminal" is the **cockpit session console** (`cockpit/web/console.js`
driven by the `/chat` handler in `cockpit/backend.py`) — not the archived
`switchboard/archive/terminal.js` the principal had open in the IDE. [[S064]]
built the whole cockpit in one pass; most surfaces were browser-verified on the
dev server and never exercised in the icon-launched window. This is that sweep.

## Findings (prioritised, with code refs)

| # | Severity | Finding | Where | Status |
|---|---|---|---|---|
| 1 | **P0** | **Esc doesn't cancel.** The composer `onKeyDown` binds only `Enter`. No `Escape` handler exists. Interrupt *does* work via the **Stop** button (`conn.interrupt()` → backend `control_request`), but Esc is unwired. | `cockpit/web/console.js` (composer `<textarea onKeyDown>`, ~L130) | **OPEN** — not covered by S065. One-liner: `if (e.key==="Escape" && model.busy) conn.interrupt()`. |
| 2 | **P0** | **Can't answer in-session questions.** Headless `claude -p` **auto-dismisses** `AskUserQuestion`/`ExitPlanMode` (injects its own `tool_result {is_error:true}` "Answer questions?") the instant they're called — no stream-json client can intercept or supply the answer. Console rendered the inert tool card; session then wedges at `busy`. | `cockpit/backend.py` `chat_handler`; `console.js` tool-card render | **FIXED in [[S065]]** (bfa95764): `--disallowedTools "AskUserQuestion ExitPlanMode"` → agent falls back to **prose** questions, answerable in the composer. (Corrects my initial theory — a tool_result round-trip UI would NOT have worked; the CLI dismisses first.) |
| 3 | P1 | **A wedged turn has no recovery but Stop.** When a session sits at `busy` with no `result` frame (the #2 signature, and any future hang), the composer shows only **Stop** — can't type a follow-up. S065's prose fix removes the main trigger, but the wedge state itself has no UI affordance. | `console.js` (`model.busy` gates Send↔Stop) | OPEN (mostly mitigated by S065). |
| 4 | P1 | **`--permission-mode bypassPermissions` is un-gated and has no toggle.** Every cockpit-driven session auto-approves all permission prompts. The brain's *architectural* hooks (no-confirmed-writes, no-deletes, dwarf/gnome boundaries) still fire — they're PreToolUse `exit(2)`, independent of permission mode — so the six guarantees hold. But there's zero human gate on Bash/Edit in a cockpit session, and no `bypassPermissions`↔`acceptEdits` UI toggle (deferred since old S060). | `cockpit/backend.py` `chat_handler` args (~L179) | OPEN — **decision needed**, not obviously a bug. |
| 5 | P2 | **No reconnect on WebSocket drop.** `ws.onclose` sets status "disconnected" and stops; backend `finally` calls `proc.terminate()`. A backend restart or network blip ends the session with no recovery UI. (Switching *rows* is fine — the conn stays alive in `fleet.js`, by design.) | `cockpit/web/fleet.js` (`SessionConn.connect` onclose) | OPEN. |
| 6 | P2 | **No "working" indicator during silent tool runs.** The streaming preview only shows on text/thinking delta. During a long Bash with no output, nothing moves but the Stop button — hard to tell "thinking" from "wedged". | `cockpit/web/console.js` (`Preview` gated on `preview.text`/`thinking`) | OPEN — polish. |
| 7 | P2 | **Feed drops/clusters comms.** `api_feed` filters any item whose `ts` won't parse; comms timestamps are coarse (date-only → all collapse to 00:00 ordering). Lifecycle kinds (`picked_up`/`intent`/`needs_you`/`done`) ARE wired correctly to the hook contract — feed isn't broken, just comms ordering. | `cockpit/backend.py` `api_feed` / `_comms_ts` | OPEN — minor. |
| 8 | P2 | **Offline blank-window risk (known/deferred).** `web/index.html` loads Preact/htm from esm.sh — no internet at launch = silent blank render, no error. | `cockpit/web/index.html` import map | OPEN — already logged as [[S064]] Step 0 item 2 (vendor locally). |

## What's solid (the floor)

So future sessions don't re-audit the good parts: the one-process model (no
server-dying disease), `Cache-Control: no-store` on all assets (kills the
stale-JS tax that haunted the old board through S063), the fleet-board read
model, `/history` transcript replay, persistent connections across row-switches,
and the place/release flow all look correctly built. Hook contracts untouched
and intact. The bones are good — what was missing is the **interactive-response
layer**, exactly the half headless-driving forces you to own.

## Recommended next actions

1. **Bug #1 (Esc)** — trivial, isolated to `console.js`, low collision. Land it.
2. **Bug #4 (bypass/toggle)** — surface to principal as a decision: is fully
   un-gated the intended posture for a fleet console, or do we want an
   acceptEdits toggle?
3. **#3/#5/#6** — robustness pass once #1 + S065 land.

## Coordination note (D-024)

Three parallel cockpit sessions at sweep time: this one (read-only sweep),
bfa95764 ([[S065]] — question fix, landed on disk), f1df4fa5 (hit the same #2
wall). Clean split: siblings build, I review. SNNN bumped 64→66 (S065 = the
question-fix session). No cockpit files touched by this session.

## S066 cont. — the B pivot (build)

Principal, after the sweep + a pricing-research detour: Anthropic's **2026-06-15
billing change** moves `claude -p` / Agent SDK / GitHub Actions off the Claude
subscription onto a metered API-rate credit pool (no rollover); *interactive*
terminal claude stays on the subscription. The cockpit's `/chat` driver is
headless `claude -p` — exactly the repriced path. Principal chose **Option B:
replace the headless driver with a real embedded interactive terminal.**

Why B is the right call beyond cost: a real TTY fixes **both** reported bugs for
free — Esc cancels natively, and AskUserQuestion/ExitPlanMode/permission prompts
work natively (no headless auto-dismiss, so [[S065]]'s `--disallowedTools`
workaround becomes unnecessary). And it sidesteps sweep finding #4 (the headless
path hardcoded `bypassPermissions`; the PTY runs plain interactive claude, same
as a normal terminal).

**Built (additive — kept `/chat` as fallback so nothing of the siblings' breaks):**
- `cockpit/ptybridge.py` (new) — PTY bridge lifted from the archived
  `switchboard/server.py` /pty handler. One WS ⇄ one PowerShell PTY running
  `claude --session-id <uuid>` interactively at brain root. Own module to stay
  off backend.py's merge surface.
- `cockpit/backend.py` — **2-line additive edit** in `make_app` only (import +
  `/pty` route). Did NOT touch `chat_handler` (bfa95764's S065 surface).
- `cockpit/web/term.js` (new) — xterm.js view; `TermConn` keeps the terminal +
  WS alive across row-switches (mirrors fleet.js); `termForSid8` so a board-row
  click returns to the live terminal. Inline styles — no `styles.css` touch.
- `cockpit/web/index.html` — vendored xterm `<link>`/`<script>` (UMD globals).
- `cockpit/web/main.js` — surgical: place → `openTerm`, console-col branches on
  `sel.kind === "term"`, release control. fleet.js untouched.
- Deps: `pywinpty` installed in `cockpit/.venv` (+ requirements.txt pending);
  xterm 5.5.0 + addon-fit vendored to `web/vendor/` (offline).

**Verified (backend, by me):** `py_compile` + `node --check` green. Scratch-port
smoke test: PTY spawns, session frame minted, `echo` input→output roundtrip OK.
Real-claude test: `launch=claude` → interactive claude TUI streamed in the PTY
(markers `Claude` / mode banner / `>` prompt seen); closing the WS cleans up.

**NOT yet verified (browser-only → needs principal):** xterm render in the
packaged window; the place→seed auto-type (3s heuristic delay in `term.js
_seedSoon` — if the TUI isn't ready the line waits in the prompt for Enter);
fit/resize sizing. **Relaunch trap:** a backend is already serving :8770 with the
OLD code, and `app.py` *reuses* a live backend — so the cockpit must be fully
**closed and reopened** to load `/pty`. Caveat: the two sibling sessions appear
to run inside the current cockpit process, so a restart may interrupt them — do
it at a clean moment.

## Leaving open

- **Try B live:** close + reopen the cockpit, place a session, confirm the
  terminal renders and is drivable; check the seed auto-type + Esc + answering a
  question in-terminal.
- requirements.txt: add `pywinpty`.
- Refinements: seed-timing (detect TUI-ready vs fixed delay); a release/“×” is
  wired but terminal persistence across reload (resume a PTY claude via
  `--resume`) is not; once B is trusted, retire `/chat` + S065's workaround.
- Original sweep bugs #1 (Esc) and #2 (questions) are **resolved by B** in the
  terminal path; #3/#5–#8 (headless-path robustness/polish) only matter if `/chat`
  is kept.

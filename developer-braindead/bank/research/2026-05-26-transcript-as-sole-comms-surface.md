# Transcript view as the sole comms surface — feasibility

**Date:** 2026-05-26 · **Session:** [[S099_acf8fc80_obsidian_quest_link_migration|S099]] (braindead-be7867be) · **Status:** research-only, parked behind §C (principal call)

## The question

Can the cockpit **transcript view** become the *only* surface you talk to a session through — read **and** drive it, never touching the xterm terminal? The principal's framing: "we would have to stream the whole terminal content."

## Verdict (one line)

**Normal back-and-forth (read + type): yes, a clean build. *Completely* eliminating the terminal: no** — the blocker is a specific interactive 20%, and "stream the whole terminal content" doesn't solve it, it just rebuilds xterm in DOM.

## Current architecture (grounded in the code, 2026-05-26)

- **Transcript = read-only render of the on-disk `.jsonl`.** `transcript.js` fetches `/history?session=<sid8>&full=1` every 2s (`backend.py:parse_transcript`) and draws structured turns (text / thinking / tool blocks) as clean DOM. No input path exists in it today. Born [[S091]]/[[S092]] for *clean copyable output* (xterm's fixed grid mangles copies); readability passes [[S093]]/[[S095]].
- **The PTY is the engine.** `/pty` (ptybridge) runs the real interactive `claude`; xterm just displays it. This is the **subscription** path — the whole reason the cockpit drives a real terminal instead of headless ([[D-028_switchboard_cockpit_rebuild]]).
- **A DOM→PTY input channel already exists.** [[S095]]'s compose-bar sends typed text into the PTY via bracketed-paste + a separate delayed CR (`COMPOSE_SUBMIT_DELAY_MS=110`). So "type in DOM, send to the live session" is already solved for plain text.

## The 80 / 20 split

**The easy 80% (buildable now):**
- *Output*: already structured and clean; the transcript shows the conversation better than the terminal. 2s poll → true streaming (SSE / tail the jsonl) is a straightforward upgrade — the file is appended live.
- *Input*: lift a compose box into the transcript, reusing the [[S095_f9310a45_cockpit-transcript-full-width-speech-bubble|S095]] bracketed-paste→PTY mechanism. Covers read-the-reply / type-the-next-prompt.

**The hard 20% — interactive TUI moments:** permission prompts (allow/deny), plan-mode approval (`ExitPlanMode`), `AskUserQuestion` menus, slash-command autocomplete, the `@`-file picker, Esc-to-interrupt.
- These are **never in the `.jsonl`** — the transcript only receives *committed* turns. A transcript-only view goes blind exactly when a decision is needed: you'd hit an AskUserQuestion menu and the panel would sit idle while the terminal silently waits for arrow-keys.
- This is the same limit flagged at [[S086]]: "interactive TUI bits still need a click into the terminal."

## Why "stream the whole terminal content" doesn't fix it

Streaming the raw ANSI byte stream and re-rendering it = **rebuilding xterm in DOM, worse**. You lose the clean-text win that made the transcript worth having and gain nothing. The literal ask is technically possible and not worth doing.

## The real ceiling — billing

The clean, structured, *interactive-event-aware* path exists: the headless `stream-json` SDK route ([[S060]] built exactly this — a chat UI with bubbles/streamed text/tool cards/input). **But headless meters/bills; the interactive PTY keeps us on subscription.** So the structured I/O lives on the path we can't use, and the subscription path is ANSI-only. *That tension is the ceiling, not the rendering.* (See cross-conv memory: headless billing constraint, 2026-06-15.)

## Three ways to handle the 20%

1. **Hybrid auto-flip — recommended.** Transcript is the default surface (streaming + compose box). On an interactive prompt, auto-surface the terminal for that moment, then flip back. We **already detect** these states — the sidecar (`status-sidecar.py`) classifies `waiting_for_user` on `AskUserQuestion`/`ExitPlanMode` for the board. Reuse that signal. You live in the transcript ~80% of the time; xterm appears only when a decision genuinely needs it. Cheapest robust path, no new brittle surface.
2. **Re-render prompts as DOM controls.** Parse the PTY stream for menus, draw native buttons that send keystrokes back. Powerful but **brittle** — every Claude Code TUI change can break the parser. Load-bearing UI on an unstable surface.
3. **Full ANSI→DOM streaming.** The literal "stream everything" reading. Reimplements a terminal, worse. Rejected.

## Recommended design (if/when this is built)

Hybrid (option 1), scoped to `cockpit/*`:
- `transcript.js`: replace the 2s `/history` poll with streaming; add a compose box wired to the existing bracketed-paste→PTY channel.
- `main.js`: on the sidecar's `waiting_for_user` (already computed), auto-flip the visible surface transcript→terminal, and flip back when it clears.
- No hook changes (preserved contracts); no headless path (subscription preserved).
- Explicitly **don't** chase terminal-free elimination — the interactive prompts stay the terminal's job.

## Decision

**Research-only this session.** Not built — the parked load-bearing gap is the outward §C shipping-mart pilot ([[D-027_inward_outward_build_imbalance]]), not more inward cockpit polish. This note is the design-on-the-shelf; the hybrid is the path to pull off it when cockpit work next earns priority. Roadmap home: a line under the cockpit/UX items in `bank/plan.md`.

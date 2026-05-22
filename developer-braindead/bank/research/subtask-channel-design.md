# Subtask channel — making the visualizer feel alive under sustained work

> **Why this file exists.** S027 closed the visualizer audit. Sitting under the still-open "make the world alive" goal from [[Q-008]] is a more pointed complaint from the principal at end of S027: *the sprite gets stuck on one intent for 10 minutes while doing a billion things underneath.* This file sketches the fix — a third communication channel between **intent** (agent-authored, slow, scope-level) and **action** (hook-authored, fast, raw tool calls) — and prepares the next session to pick it up cleanly.
>
> **Status.** Design only. No code. Pick up next session.

---

## The problem

Today the visualizer has two channels feeding the COMMS panel and the sprite bubble:

| Channel | Author | Cadence | Content shape |
|---|---|---|---|
| **Intent** | Agent (Claude), writes `.claude/intent/<actor>-<sid8>.txt` | Slow — only on scope changes per [[gielinor/meta/communication-protocol.md]] | Why / what scope ("Auditing visualizer", "Wrapping up S027") |
| **Action** | Hook (`emit-event.py` PreToolUse) | Fast — every tool call | Raw file/command ("Bash: git status", "Edit: index.html") |

Both work as designed. Both feed COMMS. But two failure modes:

1. **The bubble (above the sprite) shows only intent.** Action events go to COMMS but not the bubble. When the agent doesn't update intent for a stretch, the bubble freezes — even though the agent is hammering tool calls underneath. This is the principal's "stuck on one thing for 10 minutes" complaint.
2. **The action stream is too raw to read at a glance.** `Bash: git status` works; `Bash: cd "C:/Users/.../Documents/GitHub/brain" && git status` is the same content but reads as noise. The audit's I12 (deferred) called this out as "action target prettification." Until that lands, action-stream as a "what's happening now" surface is half-baked.

So the visible aliveness budget today is bounded by how often the agent remembers to update intent narration. That's the bottleneck.

## The fix — a third channel between intent and action

Introduce **subtask** as a new channel:

| Channel | Author | Cadence | Content shape |
|---|---|---|---|
| **Intent** (unchanged) | Agent | Slow | Why / scope |
| **Subtask** (new) | Hook (synthesis layer over PreToolUse) | Medium — debounced per N seconds | Current micro-step in natural language ("reading meta/modes.md", "running git status", "searching for `instanceKey`") |
| **Action** (unchanged) | Hook (raw PreToolUse) | Fast | File/command literal |

The subtask line is **hook-authored, natural-language, debounced**. The agent never writes to it. The hook builds it from the same PreToolUse payload that drives action events, but runs it through a small synthesis layer.

### The three speeds, no overlap

- **Intent** says *why* — slow, deliberate, scope-bounded. "Wrapping up S027."
- **Subtask** says *current step* — fast enough to feel alive, natural enough to read at a glance. "writing the close commit."
- **Action** says *exact call* — exhaustive, the audit trail. "Bash: git commit -m ..."

The audit's I12 prettification work is the foundation for subtask — they share the synthesis layer.

## Rendering

Two options for surfacing subtask:

**Option A: secondary line in the existing bubble.** Bubble becomes two-line by default: intent on top (bold, primary), subtask underneath (muted, italic, smaller font). Already a 2-line bubble exists (wrap from long intents) — extending it to "intent + subtask" is a natural shape. The bubble grows from a fixed-text label into a mini status panel.

**Option B: separate sub-bubble.** A second, smaller, faded bubble below the sprite shows subtask. Intent bubble stays clean. More DOM, but clear visual hierarchy.

Recommend **Option A**. Less DOM, cleaner aesthetic, and the bubble already wraps to two lines — the wrap mechanism rebadges as "line 1 = intent, line 2 = subtask" instead of "lines 1+2 = wrapped intent."

Edge case: when intent is two lines and subtask wants to land, do we drop subtask, drop intent line 2, or grow to three lines? Recommend: cap at two lines total, prefer intent. If intent is short enough to fit on one line, subtask gets line 2. If intent fills both lines, no subtask shows. (Intent wins because it's the scope; if you wrote a verbose intent, you've already told us what's happening.)

## Synthesis layer — turning tool calls into natural language

The hook's PreToolUse handler today emits an `action` event with raw text. The new layer sits before that emit and produces a *second* event of type `subtask` (or extends the existing intent event surface). Rough verb mapping:

| Tool | Args | Subtask phrase |
|---|---|---|
| `Read` | path | "reading {basename(path)}" |
| `Edit` | path | "editing {basename(path)}" |
| `Write` | path | "writing {basename(path)}" |
| `Bash` | cmd | verb-extracted (see below) |
| `Glob` | pattern | "searching for {pattern}" |
| `Grep` | pattern | "searching for `{pattern}`" |
| `Task` | description | "spawning dwarf — {description}" |
| `WebFetch` | url | "fetching {hostname(url)}" |
| `WebSearch` | query | "searching: {query}" |

`Bash` is the hard case — argument is freeform. Pattern-match the first verb token:

| Match | Subtask phrase |
|---|---|
| `git status\|diff\|log` | "checking git {verb}" |
| `git add\|commit\|push` | "{verb}ing changes" |
| `ls\|cd\|pwd\|mkdir` | "navigating files" |
| `python\|node\|rg\|jq` | "running {tool}" |
| `cat\|head\|tail` | "reading output" |
| fallback | "running shell command" |

The list lives in the hook as a small dict. Easy to extend. Crucially: when the verb isn't matched, fall back to a generic phrase rather than dumping raw command text — that's the I12 win.

## Debouncing

Without debounce a turn that fires 12 fast tool calls becomes a strobe. Strategy:

- **Min update interval per actor: 500ms.** If the previous subtask was set <500ms ago, skip the write.
- **Aggregation window: 1.5s.** Within this window, identical verbs collapse — three `Read` calls in 1s become "reading 3 files" rather than three flashes of the latest basename.
- **Reset on new tool call after silence.** First call after a >2s gap always lands; the bubble shouldn't have a stale "reading X" while the agent is now writing.

These are starting numbers, tune in S028+.

## Long-operation heartbeat (deferred but related)

The same gap also opens during long-running Bash commands or dwarf waits (a 30s Explore dwarf returns nothing until despawn). The subtask channel doesn't directly solve this — a pulse-while-waiting is a separate mechanism. Note it as a follow-on: a `setInterval`-driven "still working ({elapsed}s)" overlay when there's a pending tool call and no other channel activity.

## What changes where

- **Hook** (`developer-braindead/.claude/hooks/emit-event.py`):
  - New synthesis function `subtask_for(tool, args) -> str` with the verb tables above.
  - New event type `subtask` emitted on PreToolUse alongside (or instead of) action — TBD how to layer.
  - Debounce state per actor (in-memory dict, reset on session boundary).
- **Visualizer** (`developer-braindead/experiments/visualizer/index.html`):
  - New `subtask` event handler in `applyEvent`'s switch.
  - `renderIntent` extended to accept a secondary subtask line; bubble layout adjusts to "primary line + dimmed line".
  - State map `actorSubtask[actorKey]` parallel to `intents[actorKey]`; cleared on move when the *intent* clears (per existing player vs sub-agent rules).
- **No main-brain change.** This is dev-brain infrastructure; `gielinor/meta/communication-protocol.md` stays as-is — the protocol's "agent voice" rules unchanged. Subtask is hook voice, not agent voice.

## Open questions

1. **Subtask for sub-agents.** Dwarves and gnomes have task-label bubbles set on spawn. Does subtask layer on top of those too? Recommend: yes for dwarves (a 30s recon dwarf benefits even more from subtask), but the task label stays as the *primary* line and subtask fills the secondary. For player sprites, intent stays primary.
2. **Subtask in replay mode.** EVENTS array is hand-authored; no PreToolUse to drive subtask. Either (a) leave subtask absent in replay — fine, replay is the demo, not the working aliveness target; or (b) bake some subtask events into EVENTS for the demo arc. Recommend (a).
3. **Per-session subtask file?** Probably not — subtask is event-driven, not file-driven. The event carries the subtask text directly. No `.claude/subtask/...` sidecar.
4. **What about the COMMS panel?** Do subtask events also append to COMMS, or only update the bubble? Recommend: yes-append, with a new line class `.log-entry.subtask`. Adds chat aliveness directly. Tab routing: shares the speaker's tab (so Jebrim subtask events go to JEBRIM tab + ALL).
5. **Replay-mode demo of the channel.** Once shipped, the audit primer / S028 close should include a short EVENTS-array demo sequence showing intent + subtask + action together. Worth its own follow-up.

## Recommended next-session start order

1. **Sketch the hook synthesis dict** in `emit-event.py` (verb tables for Read/Edit/Write/Bash/Glob/Grep/Task/WebFetch/WebSearch). Keep it data, not logic — easy to extend.
2. **Wire `subtask` as a new event type** alongside action. Emit both per PreToolUse.
3. **Add `subtask` to the visualizer's dispatch.** Update `actorSubtask[actorKey]` state; trigger a re-render of the bubble.
4. **Extend `renderIntent`** to render a primary line + dimmed secondary line. Choose Option A layout.
5. **Add debounce** (500ms min update, 1.5s aggregation, 2s reset gap).
6. **Live test in a real working session.** Watch a Jebrim session do 10 minutes of work and confirm the bubble updates ~every few seconds without becoming a strobe.
7. **Tune the debounce numbers** based on observation. Adjust verb table for any common patterns that fall through to "running shell command" too often.

Stretch (defer to S029+ if S028 doesn't reach it):

- Long-operation heartbeat (the "still working" pulse for slow Bash + dwarf waits).
- Replay-mode demo events.
- Color tinting on the subtask line (faint hue from the speaker's `--<actor>-text` var? or neutral muted gray?).

## Related

- [[gielinor/meta/communication-protocol.md]] — the agent-authored intent contract. Unchanged by this work.
- [[Q-008]] — visualizer aliveness picks. This work is the most-targeted aliveness fix to date.
- [[visualizer-audit-S026-prep]] — I12 (action target prettification) is the foundation for the synthesis layer.
- [[D-014]] — narrate/action events + COMMS chat panel; subtask is a natural extension of the channel taxonomy.
- [[D-018]] — per-session substrate isolation. Subtask state in the hook is per-actor not per-session; should still work cleanly under parallel sessions, but worth double-checking during the live test.

# D-010 — 2026-05-21 — Visualizer intent narration via agent-written sidecar

**Context.** [[S010_visualizer_live_mode_v0]] shipped live-mode v0; characters walk and dwarves spawn but the viewer can't tell *what* an actor is actually doing. Niklavs asked for a small glimpse of intent above each player (e.g. "Wrapping up [[S002_dev_brain_runescape_restructure|S002]]"). Two readings of "what they're doing" exist: derived from the last file touched, or self-narrated by the agent. Path-derived would have been ~30 minutes of work; we picked the truthful version instead.

**Decision.** Ship intent narration as **per-actor plaintext sidecars the agent writes after stating its Plan**, the existing PostToolUse hook converting writes into `intent` events, and the renderer hanging a speech bubble over the actor.

Four knobs (settled in chat with Niklavs):

- **Rendering:** speech bubble (rounded rect + tail), not a flat label. Reads as a thought, not a status bar.
- **Persistence:** intent expires **on building change**. Walking somewhere new clears the bubble; the agent re-narrates if the new intent still applies. Avoids stale labels and avoids flicker timers.
- **Dwarves narrate too:** but they don't write files. The hook attaches the `Task` call's `description` field to the `spawn-dwarf` event; the bubble lives for the dwarf's lifetime. Dwarves don't have visibility into their own dwarf-id, so requiring them to write a sidecar would either need new wiring (env var passthrough, tool_use_id leak) or risk collisions. Spawn-time description is the principal's narration of the dwarf and is good enough for v0.
- **Strictness:** soft. Protocol guidance in `meta/communication-protocol.md` — same enforcement model as Understanding/Plan today. Skipping a turn doesn't break anything; the file is a hint, not a contract.

**Alternatives considered.**

- **Path-derived intent** (verb extracted from the file the hook saw). Cheaper, reactive, lies — shows last *touched* file, not current goal. Promising as a fallback for sessions without narration but rejected as the primary mechanism.
- **Single JSON file holding all actors' intents.** Simpler to enumerate; harder to update atomically when dwarves narrate concurrently. Per-actor files won.
- **Mid-task dwarf narration via a description-slug sidecar.** Considered, deferred. Would need the hook to track `description → dwarf-id` mapping and read updates. v0 keeps dwarf intent fixed to the spawn description.
- **Hook validation that intent was written each turn.** Brittle; many turns don't merit narration (a single `Read`, a clarifying question). The soft model is honest — the absence of a bubble means the agent didn't bother narrating, not that the system broke.
- **Stop-hook reading a sidecar at turn-end instead of write-hook on the file directly.** Adds a hook surface for marginal benefit. Existing PostToolUse on `Write|Edit` already fires for the sidecar; we just branch in handler.

**Consequences.**

- Path: `brain/.claude/intent/<actor>.txt`. Plaintext, single line, ≤60 chars (truncated in hook).
- Active-actor naming: `<player>.txt` (player session) or `wisp.txt` (unscoped / dev-brain). Determined by mode the agent is already aware of from CLAUDE.md routing — no new state required.
- Hook (`developer-braindead/.claude/hooks/emit-event.py`) gets a branch in `handle_write_or_read`: when the touched path contains `/.claude/intent/`, the hook reads the file and emits a single `intent` event (no building move, no `log` line, no actor-state mutation). Other writes flow through normally.
- Hook attaches `intent: description[:60]` to every `spawn-dwarf` event.
- Renderer (`experiments/visualizer/index.html`) gains a `#speech-bubbles` SVG layer above building labels, plus `setIntent` / `clearIntent` / `renderIntent` helpers. `applyEvent` cases:
  - `intent` → set bubble for `ev.actor`.
  - `move` → clear bubble for `ev.actor` (per the on-building-change expiry knob).
  - `spawn-dwarf` → if `ev.intent`, set bubble for `ev.id` after spawn.
  - `despawn-dwarf` / `despawn-wisp` → clear bubble.
  - `resetWorld` clears all bubbles.
- New `intent` event type in the NDJSON vocabulary: `{type: "intent", actor, text, wallTime, source: "hook"}`. Schema-compatible with bootstrap-from-tail — late-joining viewers see the most recent intent for each actor at boot.
- Intent files are gitignored (`.claude/intent/*.txt`); transient runtime state, same status as `state.ndjson`. The directory itself is kept via `.gitkeep`.
- Protocol addition lives in `gielinor/meta/communication-protocol.md` — a new section between "Internal rituals stay silent" and "Why this rule exists."

**Open follow-ups (deferred).**

- **Mid-task dwarf re-narration.** If dwarves doing long work want to update their bubble, we need a description-slug → dwarf-id mapping in the hook plus a sidecar path dwarves can write to. Wait for a session where this actually matters.
- **Idle indicator interplay.** [[D-009_visualizer_live_mode_v0|D-009]] deferred an idle-fade on actors with no recent events. Speech bubbles should probably fade with the actor when idle. Re-check when idle indicator lands.
- **Stale-intent eviction on death-as-crash.** Today's design: a stale intent file from a crashed session re-emits on next session start (because the file still exists). Close-session ritual could clear the directory; reconciliation prompt is also a candidate place. Defer until it actually misleads.
- **Per-building intent restoration.** Current design clears on move; if the agent's intent legitimately spans buildings ("Bankstanding for Zezima — pass across all layers"), the user sees flicker. Defer; revisit if observed.

**Session ref.** [[S011_visualizer_intent_narration]] (in progress).

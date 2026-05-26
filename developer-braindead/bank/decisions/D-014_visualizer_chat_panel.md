# D-014 — 2026-05-21 — Visualizer chat panel with longer intents, narration channel, and action events

**Context.** [[D-010_visualizer_intent_narration]] gave each actor a speech bubble fed by `.claude/intent/<actor>.txt`, but the bubble is the *only* surface for "what the agent is doing." Bubbles clear on building change and are capped at ~60 chars; mid-session the map can look static even when work is happening, and there's no log of what just happened. Niklavs asked for a RuneScape-style chatbox below the map — each actor narrating their work line by line, with history kept — so he can stay in the loop without staring at the sprite.

**Decision.** Add a chat panel below the map fed by three streams:

1. **Intent (extended).** Same `intent/<actor>.txt` contract as [[D-010_visualizer_intent_narration]], but the cap rises from ~60 to **~100 chars**, with bubbles allowed to wrap to two lines (text centered). Bubble and chat read the *same* string — no second sidecar.
2. **Narration (new authored channel).** A global system-voice channel for broader-scope commentary the actor doesn't speak in their own voice — *"Bankstanding phase 0 begins"*, *"Session S016 opens"*. Single global sidecar `.claude/narration.txt`, overwrite semantics (the file holds the most recent narration line, the chat keeps history). Cap ~200 chars.
3. **Action (new mechanical event).** A new `action` event emitted by the hook on selected tool calls — Edit, Write, Bash, Grep, Glob. Read is **skipped** by default (too noisy; sprite moves already show building shifts). Schema: `{type: "action", actor, verb, target, wallTime, source: "hook"}`.

System lines for `move` / `spawn-dwarf` / `despawn-dwarf` also surface in chat in muted/italic style — they were already in the event stream, the chat just renders them too.

**Discipline rule (codified in protocol).** Intent describes *why/what scope* ("Drafting S016 entry"); actions show *which file/command* ("editing .../S016.md"). They complement; they do not mirror. Keeps the chat from becoming two-line redundant pairs.

**Alternatives considered.**

- **Two-line sidecar (short bubble + longer chat).** Considered and rejected. Cleaner separation but doubles the agent's per-turn writes and the renderer's parsing. With the bubble cap at 100 and two-line wrap allowed, one string serves both surfaces.
- **Narration as a renderer derivation (mechanical only — option (a) from chat).** Auto-derive narration lines from `move`/`spawn`/`despawn` events only, no new contract. Cheaper but thinner — no way to announce *"Bankstanding phase 0 begins"* or *"Session S016 opens"*. We took the authored channel.
- **Bundle narration into intent files with a `*` prefix.** Considered. Conflates first-person speech and third-person narration in one file — wrong mental model. Two channels keep the agent's discipline cleaner.
- **Append-only narration log file.** Considered. File would grow unbounded; chat panel + `state.ndjson` already keep durable history. Overwrite matches the existing intent pattern.
- **Narrating Reads.** Floods the chat (most turns are Read-heavy). Sprite movement already shows building shifts. Skip by default; revisit if reads become invisible in a meaningful way.
- **Rolling reads up into a debounced "Jebrim: reading 4 files" line.** Tempting but adds hook complexity for marginal benefit. Defer.
- **New `narrate` sidecar per actor (`narration/<actor>.txt`).** Wrong shape — narration is system voice, not actor voice. Single global file matches the semantics.

**Consequences.**

*Hook side (`developer-braindead/.claude/hooks/emit-event.py`):*

- Existing `intent` branch in `handle_write_or_read`: bump truncation from 60 → 100 chars.
- New branch: writes touching `/.claude/narration.txt` read the file and emit a `narrate` event `{type: "narrate", text, wallTime, source: "hook"}`. No actor binding. Truncated to 200 chars.
- New PreToolUse handler emits `action` events for Edit/Write/Bash/Grep/Glob:
  - Edit/Write → `verb: "editing"` (or "writing" for new files), `target: <path>` (path made relative to brain root if inside it; otherwise basename).
  - Bash → `verb: "running"`, `target: <command truncated to 80c>`.
  - Grep → `verb: "searching"`, `target: <pattern truncated to 60c>`.
  - Glob → `verb: "globbing"`, `target: <pattern>`.
  - Read → **not emitted**.
- Action events skip the `move` path — they emit a chat-only event, not a building change. (Edit on a file inside a known building still emits `move` via the existing path map.)
- Actor attribution reuses S015's `agent_id` → dwarf-id binding. Dwarves emit `action` events under `actor:Dn`.

*Renderer side (`experiments/visualizer/index.html`):*

- New `#chat-panel` div below the map. Fixed height (e.g. ~200px), scrollable, auto-scroll to bottom, lock-on-scroll-up.
- New `applyEvent` cases:
  - `intent` → push `<Actor>: <text>` line, actor-name colored to sprite (existing per-actor color map).
  - `action` → push `<Actor>: <verb> <target>` line, same color treatment.
  - `narrate` → push `* <text>` line, muted/italic style.
  - `move` → push `* <Actor> walks to <building>` muted/italic. (Already an event; chat just renders it.)
  - `spawn-dwarf` → push `* <Dn> spawned by <parent> — <description>` muted/italic.
  - `despawn-dwarf` → push `* <Dn> returns to <parent>` muted/italic.
  - `resetWorld` → clear chat history.
- DOM cap: keep last 200 lines (older lines pruned). State.ndjson remains the durable record; chat is a window.
- Bootstrap-from-tail (existing late-joiner replay): read the last N events from `state.ndjson` and replay into the chat panel so a fresh page load lands populated.

*Bubble rendering:*

- Bubble layer (existing `#speech-bubbles`) updated to wrap text to two lines when it overflows. Text-anchor stays middle (centered). Rounded-rect width grows to fit longest line; height accommodates wrapped lines. Tail still anchored to actor sprite.

*Protocol addition (`gielinor/meta/communication-protocol.md`):*

- Extend the "Intent narration (visualizer sidecar)" section to:
  - Note the cap is now ~100 chars / two-line bubble (was 60).
  - Add the new "Narration channel" subsection — when and how to write `.claude/narration.txt` (system-voice broader context, not actor speech). Examples: session opens, bankstanding phase transitions, mode switches.
  - Add the discipline rule: intent = why/scope, actions = which file/command. Keep the two from mirroring each other in chat.
- Drift fix: the current doc says "Unscoped or dev-brain session → `wisp.txt`". The convention in use is `braindead.txt` for dev-brain mode. Update to match.

*Gitignore:*

- `.claude/narration.txt` is transient runtime state — gitignored, same status as `intent/*.txt` and `state.ndjson`.

**Open follow-ups (deferred).**

- **Read narration / rollup.** If Read-heavy turns ever feel invisible in the chat, revisit the debounced-rollup idea. Phase 0: just skip.
- **Action target prettification.** Paths shown verbatim today; could shorten common prefixes (`players/jebrim/quest-log/in-progress/` → `…/in-progress/`). Wait until chat is in use and we see what reads badly.
- **Chat scroll-lock UX.** "User scrolled up → don't auto-scroll" is straightforward but worth confirming the lock-release UX (button to jump to bottom, or auto-release on scroll-back-to-bottom). Pick once it's running.
- **Actor color taxonomy.** Sprite colors today are ad-hoc; chat surfaces them more prominently. May warrant a tightened palette. Defer until visually checked.
- **Bubble two-line layout edge cases.** Single-word overruns, very narrow buildings, and dwarf bubbles that slide during move — all need a look once wrapping ships. Treat as visual polish, not blockers.
- **Replacing per-actor intent file with a chat-broadcast tool.** Future-question — if the agent ever calls a dedicated "say" tool instead of writing a sidecar, both bubble and chat would feed from the same call. Defer; the sidecar pattern is working.

**Session ref.** [[S016]] (in progress).

**Status.** Drafted in chat with Niklavs 2026-05-21. Awaiting implementation across hook + renderer + protocol.

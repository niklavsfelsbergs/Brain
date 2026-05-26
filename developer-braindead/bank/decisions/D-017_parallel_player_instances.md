# D-017 — 2026-05-22 — Parallel player instances: per-session sprites with tint differentiation

**Context.** Niklavs sometimes runs two sessions of the same player in parallel — typically two Jebrim sessions, one continuing a long quest and one branching off something side-channel. Today the visualizer renders one sprite per player ID, so both sessions' events route to the same sprite: intent bubbles overwrite each other, action streams interleave in COMMS without disambiguation, move events fight for the sprite's position, and the focal label can't represent "Jebrim is in *two* buildings doing *two* things."

The parallel-session pattern has surfaced as an attribution-correctness problem before — [[S014_visualizer_polish_and_aesthetics_pass]] (player swap mid-session), [[S022_visualizer_audit_fixes]] (Bash attribution flipped under parallel Jebrim work), [[S023_visualizer_ticker_and_cross_session_attribution]] (recency walk needed session-filtering), [[S024_visualizer_aliveness_pass_1_3]] (intent silence after move under sustained tool use). Each fix has been a band-aid at the attribution layer. This decision makes the sessions visible as separate entities in the visualizer instead.

**Decision.** When the hook observes a second `sessionId` for an existing actor name, the visualizer spawns a second sprite for that actor. Each instance is independent: its own intent file, own building tracker, own bubble, own COMMS prefix, own sprite. Both stay rendered as long as either is alive.

### Naming + identification

- **Instance IDs** are `<actor>-<n>` where `n` is per-actor spawn order: `jebrim-1`, `jebrim-2`. First instance keeps the original short label (`Jebrim`); subsequent instances are labeled `Jebrim·2`, `Jebrim·3`. Borrows the dwarf-numbering precedent.
- **Sprite differentiation** is **tint**, not badge. Same sprite art, hue-shifted: instance 1 uses the canonical palette, instance 2 a slightly desaturated/warmer variant, instance 3 a third variant. Cycle through 3 variants like dwarves do. Tint values picked per-player so the secondary Jebrim still reads as a wizard, not a different character.

### Both instances are active

Active-player state is per-instance. The focal label can hover over both Jebrims simultaneously, each with its own building name. COMMS user prefixes carry the instance number: `Jebrim·2: editing nfe/rollups.sql`. The legend gains entries lazily — only when a second instance exists does `Jebrim·2` appear in the legend block.

This breaks the current invariant "one focal label per player." Visualizer code needs to handle a `Set<activeInstance>` instead of a `Map<player, activeInstance>`.

### Despawn trigger

An instance despawns when **either**:

1. **The session goes idle for 5 minutes** — load-bearing signal. A background tick in the visualizer (the existing live-mode poll is fine) checks each instance's `lastEventAt`. If 5 minutes pass with no events for that `sessionId`, the instance fades out.
2. **Claude Code's `SessionEnd` hook fires for the instance's `session_id`** — bonus signal. Despawns immediately on clean exits (`prompt_input_exit`, `clear`, `resume`, `logout`, `other` matchers) without waiting for the idle timer.

`SessionEnd` is explicitly documented as best-effort: it cannot block and has no guarantee on forced kills (Ctrl+C, SIGKILL, terminal closed mid-task, crash). So the idle timer is the actual contract; `SessionEnd` just makes graceful exits feel snappier. The 5-minute threshold also matches the Anthropic prompt cache TTL — a session that hasn't fired tool calls in 5 minutes has almost certainly stalled or finished. Cheap to extend later if false-despawns happen.

`SessionEnd` requires adding a new top-level entry to `.claude/settings.json` (`"SessionEnd": [{ "hooks": [...] }]`), with the hook emitting a `despawn-instance` event into `state.ndjson` keyed by `session_id`. The matcher field tells us whether the despawn was clean (log it) or anomalous (worth surfacing).

### File and state schema changes

- **Intent files** become per-session: `.claude/intent/<actor>-<short-session-id>.txt` where short-session-id is the first 8 chars of `_SESSION_ID`. The hook's intent-write handler parses the suffix to route to the right instance. Sessions that don't write to a session-suffixed file (e.g., older sessions, or unscoped writes) fall back to `<actor>.txt` and target instance 1.
- **Narration file** stays single (`.claude/narration.txt`) — narration is system voice, not actor voice.
- **`state-actors.json`** keyed by `(actor, sessionId)`. Legacy reads (keyed by actor alone) treated as instance-1.
- **Move events** carry `instance` alongside `actor`. Hook stamps it from `_SESSION_ID`.
- **All emitted events** carry `instance` (or implicitly default to 1 if absent). Visualizer routes by `(actor, instance)`.

### What stays the same

- **Sub-agents** (dwarves, gnomes) are spawned by a *specific* instance. The hook records the parent instance on spawn; the dwarf's events route through that instance's parent for cross-player references. Sub-agents don't get their own duplicate-instance treatment — each dwarf is already unique.
- **Wisp and Braindead** are conceptually single-actor (system voice / construction crew). Treating them as instance-1 only is fine for now; revisit if two dev-brain sessions ever run in parallel.
- **Player invocation by address in `gielinor/CLAUDE.md`** is not affected. The address sets the player; the session ID is parallel-instance scaffolding the agent doesn't think about.

### Out of scope for the first cut

- **Cross-instance dwarf delegation.** If `jebrim-1` asks `zezima-2` to do something, the visualizer should attribute correctly, but the cross-instance dwarf wiring is harder than within-instance. First cut: dwarves attribute to their spawning instance; cross-instance is reported via the existing principal-records-delegation convention.
- **Color-tint accessibility.** Tint variants must remain distinguishable for the common color blindness types. Use a tool to check the chosen palette before shipping.
- **Sprite collision.** Two Jebrims in the same building stack on the same `STAND[building]` coords. First cut: small jitter offset per instance number (instance 1 at canonical, instance 2 at +12px, etc.).

## What "shipped" looks like

- Hook (`emit-event.py`) stamps `instance` on every event derived from `_SESSION_ID`. Per-session intent file convention with fallback.
- Visualizer (`index.html`) handles a `Map<(actor, instance), spriteEl>`. Spawn on first event for a new `(actor, instance)`, despawn on 5-minute idle or explicit session-end. Tint per instance number. COMMS prefix carries instance.
- State files keyed by `(actor, sessionId)`. Legacy single-actor keys treated as instance-1.
- `meta/modes.md` (main brain) — no change. Instance is a visualizer/hook concern, not a cognitive-mode concern.

## Open questions

- **Persistence across visualizer refresh.** When the principal hard-refreshes the visualizer, instance state replays from `state.ndjson`. State-actors.json being session-keyed means the visualizer can reconstruct which instances were alive at refresh time. Should work, but worth a live test.
- **Same-session re-launch.** If `_SESSION_ID` ever changes mid-session (it shouldn't), the visualizer would treat it as a new instance. Defensive: hook caches the first-seen session ID and refuses to re-key.
- **Ghost sprite on crash.** A session that crashes (SIGKILL, terminal closed) leaves an instance rendered for up to 5 minutes before the idle timer despawns it. Acceptable — visualizer ghost sprite ≠ data corruption, and 5 minutes is the documented prompt-cache TTL boundary.

## Related

- [[S014_visualizer_polish_and_aesthetics_pass]], [[S022_visualizer_audit_fixes]], [[S023_visualizer_ticker_and_cross_session_attribution]], [[S024_visualizer_aliveness_pass_1_3]] — parallel-session attribution incidents.
- [[D-014_visualizer_chat_panel]] visualizer chat panel — provides the COMMS surface this decision modifies.
- [[D-016_gnomes_subagent]] gnomes — precedent for system-namespace sub-agents with their own numbering.
- `Q-008` — visualizer aliveness, current parking lot for visual-layer work.

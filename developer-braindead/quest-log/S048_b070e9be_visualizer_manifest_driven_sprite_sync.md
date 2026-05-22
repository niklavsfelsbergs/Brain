# S048 — 2026-05-23 — Visualizer manifest-driven sprite sync

Principal opened with "why are my sprites stuck even when sessions are dead?" — the switchboard sidebar correctly tracked liveness via the sidecar, but sprites lingered, bubbles persisted from closed sessions, and Jebrim/Zezima stood inert at fixed positions regardless of whether their actor had a live session. Three patch attempts (switchboard-driven GC, spawn-from-manifest, `relayoutBubbles` snapping) each narrowed the symptom but the next bug looked like the last one: derived state, maintained by an event stream the visualizer could only see in-flight, was structurally divergent from the sidecar's per-session truth.

Pivoted to architectural inversion. The switchboard manifest (written by [[status-sidecar.py]] on every hook fire) becomes the single source of truth for *who's on the map, where they are, and what they're saying*. The event stream stays only for narrative log and replay mode. Three concrete changes:

- **[[status-sidecar.py]]** — new `_detect_building(actor, session_id)` reads `state-actors.json` per session and stamps `building` into each manifest record. Backwards-compat: missing field falls through to the visualizer's default-spawn building.
- **[[experiments/visualizer/index.html]]** — new `syncSpritesFromManifest()` runs on every 2s switchboard poll. Single function does spawn/move/intent/despawn/orphan-intent cleanup in five passes; replaces the earlier patchwork of `spawnMissingSprites` + `syncStaticPlayerVisibility` + `gcDeadSprites` + ad-hoc `relayoutBubbles` calls. Hoisted `deriveState` / `ageSec` / `CLOSING_RX` from the sidebar IIFE to module scope so both views classify state identically.
- **Sprite state encoding** — extended the inversion: sprite state class (`state-working` / `state-waiting_for_user` / `state-closing` / `state-idle` / `state-ended`) applied per poll, with CSS drop-shadow rings + pulse animations matching the switchboard's row colors. Glance at sprite ≡ glance at sb-row chip.

Earlier in the session also landed (kept from the patch arc, all still load-bearing): wander wrapper for ambient motion when stationary (`.wander` SVG child group, JS picks random ±18px offsets every 4–12s, suppressed during `.walking`), sprite click-to-focus via `vscode://niksis8.claude-focus` (same URI the switchboard row uses; sub-agents route to parent via `parentSid8` stamped at spawn in [[emit-event.py]]), and switchboard-row hover → sprite gold-ring pulse (the reverse interlink).

The inversion's mental-model upshot: *if it's on the map, it's in the switchboard, and vice versa*. Stale intents only happen if the intent file itself goes stale. Empty bubbles can't exist — an empty `record.intent` clears the bubble on the next 2s tick. Ghost sprites can't exist — `state-actors.json` and the sidecar's 1h GC both have to forget a session before it leaves the map.

**Carry-forward bugs surfaced but not fully resolved:**
- Static jebrim/zezima HTML sprites can be hidden + their building set, but their HTML coordinates persist for the visualizer's lifetime (moveActor updates their position, but a fresh page-load resets to the HTML's hardcoded coords). Not a regression — pre-existing.
- The 5-min `INSTANCE_IDLE_MS` sweep is now belt-and-suspenders; manifest-driven sync is the primary GC. Kept the sweep for replay mode.
- `setIntent` now no-ops when text is unchanged (avoid 2s churn); subtle perf win, possibly user-visible if intents flickered.

**Cascade.**
- new: `developer-braindead/quest-log/S048_b070e9be_visualizer_manifest_driven_sprite_sync.md`.
- modified: `developer-braindead/.claude/hooks/emit-event.py` (parentSid8 on spawn events), `developer-braindead/.claude/hooks/status-sidecar.py` (`_detect_building`, manifest building stamp), `developer-braindead/experiments/visualizer/index.html` (manifest-driven sync, wander, click-to-focus, sprite state CSS, hoisted deriveState).
- updated: `developer-braindead/respawn.md`.

**Main-brain changes.** none.

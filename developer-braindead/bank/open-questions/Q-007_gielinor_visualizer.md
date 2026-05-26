# Q-007 — Gielinor real-time visualizer

**Status.** `working` — replay v0 shipped in [[S008_iso_visualizer_v0]] as iso 2D SVG (see [[D-008_iso_replay_v0_over_three_js]]); live-mode decision landed in [[D-009_visualizer_live_mode_v0]] (hooks + NDJSON + polling, scoped to v0). Remaining open thread is execution of [[D-009_visualizer_live_mode_v0|D-009]] steps 4–6 (read-side hook coverage, dwarves, bootstrap-from-tail) and whether the watchdog fallback for non-Claude writes is worth building.

**The question.** Should we build a real-time visualization of the brain operating — a top-down Gielinor map with buildings for each brain layer, players as character sprites, dwarves as smaller sprites — animated live as the agent reads, writes, spawns, and synthesizes?

## Why this is open

The aesthetic is aligned with the project — RuneScape-themed naming was deliberate. The agent has plenty of telemetry: file events, mtimes, git history, and hooks that can intercept tool calls. Cost is bounded — weekend-scale for v0.

The case *against* building now: the brain hasn't been used in real anger yet. Jebrim has [[S001_dev_brain_architecture|S001]] + [[S002_dev_brain_runescape_restructure|S002]] (mid-flight), Zezima has 0. A visualizer built before the dwarves have actually spawned is decorating an empty city.

The case *for* building now: watching dwarves spawn in real time would surface friction in the new `spawning-dwarves` skill faster than reading quest logs after the fact. The visualizer might *accelerate* observation by making activity legible.

## Proposed architecture (light, real-time)

Three parts:

1. **Watcher.** Python `watchdog` monitoring the brain folder. Every file event maps to a layer → a building → an "intent." Writes a tiny `state.json` on every event.

2. **Hooks.** `.claude/hooks/` already exists for architectural guarantees. Add `PreToolUse` / `PostToolUse` hooks intercepting `Read` / `Edit` / `Write` / `Glob` / `Grep` on paths under `gielinor/`. Emit events into the same `state.json` stream. **Without this, only writes show up — reads are where the interesting motion is.**

3. **Renderer.** Single HTML page. Absolutely-positioned character `<div>`s with CSS transitions on `top`/`left`. Polls `state.json` every 500ms. When a character's target building changes, the CSS transition handles the "walking" animation for free. No game engine needed. Buildings as static SVG/PNG or unicode glyphs in a v0.

## What it visualizes

- **Players** — Jebrim and Zezima as character sprites. Position = building of their last activity. Motion = CSS transition between buildings as activity shifts.
- **Dwarves** — small pins clustered around their parent player when their sibling file exists in `quest-log/in-progress/`. Despawn on `completed/` move.
- **Buildings** — Bank, Lorebook Library, Examine Hall of Mirrors, Spellbook Tower, Keepsake Vault, Meta Town Hall, Quest Hall (in-progress), Inn (completed), Inbox Square (unscoped captures).
- **Optional log panel** — chat-feed-style text below the map, derived from `git log` + recent file events. "[[S007_bankstanding_phase_0_alching|S007]] closed (commit 19a4497): bankstanding gained Phase 0."

## Effort

- Watcher script: ~1 hour.
- Hooks for read-events: ~1 hour + testing.
- HTML renderer with CSS-transition pins: half-day with simple shapes, two days with pixel art.
- Sound, particles, animated walking: open-ended joy work.

V0 with reads + writes + dwarves moving: probably a weekend if pixel art is skipped.

## Gotchas

- **Read-vs-write blind spot.** `watchdog` only catches writes. Hooks fix this; the watcher alone is insufficient.
- **Idle map.** Between turns, the agent is idle. The visualization will be still most of the time. Either fine (status portrait, not entertainment) or worth a "thinking" indicator.
- **Dwarves and `run_in_background`.** When the new `spawning-dwarves` skill spawns dwarves in background, the visualizer should show them active even when the principal isn't blocked. `state.json` needs to track dwarf liveness via task state, not just file presence.
- **Replay vs live.** Building a replay-from-git-log mode first (cheaper, no hooks needed) gives a demo case to validate the visual design before investing in real-time. Worth doing this as a stepping stone.

## What "answered" would look like

Either:

- A `D-NNN` decision to build, with explicit scope (v0 replay-only? v0 live? what layer of visual fidelity?).
- A `D-NNN` decision to defer indefinitely, with the trigger that would unblock it ("build after first real bankstanding").
- A `D-NNN` decision to ship a replay-from-git-log v0 first, with explicit go/no-go on real-time after the v0 lands.

## Handoff notes for the next agent

This is **deferred design exploration**, not committed work. Trigger condition for building: real dwarf wave runs in Jebrim [[S002_dev_brain_runescape_restructure|S002]] *and* first bankstanding produces real motion to render. Until then, don't start coding — the visualization will be more entertaining if you have actual activity to show.

If the next session decides to build, start with the **replay-from-git-log v0**. It's cheaper (no hooks, no watcher) and validates the visual design before committing to live infrastructure. Real-time is a follow-up once the replay version proves the aesthetic.

Related: [[S006_handoff_precondition_and_dwarf_spawning]] (dwarf-spawning skill — provides the dwarves to render), [[S007_bankstanding_phase_0_alching]] (bankstanding Phase 0 — provides the alching motion to render).

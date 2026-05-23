# D-025 — visualizer character audit (S042 findings)

**Status.** Decision: ratify the audit findings as the canonical bug list; fix order #3 → #6 → #1 → #5 → #2 with the first two landed in S042 commit `cd402d6`; remaining items carried forward with exact code refs so any session can resume in ~10 minutes.

**Date.** 2026-05-22.
**Session.** S042 (third dev-brain SNNN today after S040 ideas-folder + S041 D-024).
**Trigger.** Principal: *"Fix the map once and for all. Sprites and speech bubbles keep getting stuck or things not appearing. Full audit on character behavior and bugs."*

## Why an audit

Visualizer carries 26+ open carryforwards across S027 → S039. Symptoms ("stuck sprites", "missing bubbles") are user-visible but the cause map is fragmented across quest-logs. Audit consolidates the cause map into one ranked list so future fix work can prioritize by user-visible severity rather than session-chronological accident.

## Audit shape (the reusable pattern)

Three parallel recon dwarves (read-only general-purpose agents), each scoped to a non-overlapping surface:

- **D1** — character lifecycle in `index.html`: spawn, walk, intent/bubble, despawn paths per actor class
- **D2** — hook→viz event flow: emit-event.py + status-sidecar.py event emission, state file writes, polling consumer in `index.html`
- **D3** — carryforward verification + state file health: walk respawn.md's open list, verify each against current tree; head-tail state.ndjson; cross-check state-actors.json / state-instances.json / state-switchboard.json against live status files in `~/.claude/status/`

Each dwarf returned a self-contained markdown report with `file_path:line_number` on every claim, ranked findings, and a "top suspect" list. Principal synthesized into one tier-ranked list (Tier-1 load-bearing, Tier-2 confirmed live, Tier-3 latent, Tier-4 housekeeping). Each tier mapped to a fix proposal with sign-off before execution.

**Pattern is reusable** for any cross-cutting subsystem audit where the surface spans 2-3 files: three dwarves, three non-overlapping scopes, principal synthesis, tier-ranked triage, principal sign-off, fix loop. Recon under 5 minutes wall-clock; synthesis under 10 minutes.

## The bug list (ranked by user-visible severity)

### Tier 1 — load-bearing (smoking guns for the principal's complaint)

**#1. Suffix-strip is local to `ensureActorExists`; every other call site uses un-stripped key.** When `ev.actor = "braindead-<sid8>"`, the spawn path correctly strips to bare `braindead`, but `case 'move'` / `'intent'` / `'action'` / `'subtask'` in `applyEvent` build `actorKey = instanceKey(ev.actor, ev.instance)` from the un-stripped name. State writes (`currentBuilding[actorKey]`, `setIntent(actorKey, …)`, `actorPositions[actorKey]`) land on phantom keys the sprite-render path doesn't know. Sprite stays put; bubble silently never renders. Live evidence: `state.ndjson:5` carries `"actor":"braindead-ed610cbe"` as a real event in the current stream.
- **Code refs.** `index.html` `ensureActorExists` body (strip lives here); `applyEvent` cases `move` / `intent` / `action` / `subtask` (line numbers shifting under f9da453a's migration — find by `instanceKey(ev.actor`).
- **Fix shape.** Hoist constant `SID8_SUFFIX_ACTORS` to module scope; extract helper `stripSid8Suffix(actor)`; apply `ev.actor = stripSid8Suffix(ev.actor)` at the top of `applyEvent` (before the `instanceLastEventAt` stamp that ALSO uses un-stripped). Same call also replaces the inline strip inside `ensureActorExists`. ~20 lines total.

**#2. Sprite anchor calibration broke under PNG-scale migration.** `SPRITE_HEAD_Y = -8` (used for thought-trail anchor) and `GATHER_SLOTS.bubbleY = -48 … -101` were tuned for pre-migration inline-SVG sprites (head at ~y=-13). After f9da453a's PNG swap with `transform="scale(2.4)"` on players + braindead, visible head sits at y≈-55; wisp/guthix at `scale(1.7)` puts head at y≈-22; Guthix has additional `ACTOR_Y_OFFSET=-67` so his head is at y≈-90. Trail starts mid-torso (players) or 80px below the floating sprite (Guthix). Bubble pointer base sits below the head for scaled players.
- **Code refs.** `index.html` — `SPRITE_HEAD_Y` declaration; `GATHER_SLOTS` table; `ACTOR_Y_OFFSET` for guthix.
- **Fix shape.** Per-actor head-Y table keyed off `(scale, y-offset)`. Or compute head-Y from sprite bbox at render time. **Deferred to f9da453a** — sprite anchor is inseparable from sprite art work they're doing.

### Tier 2 — confirmed live in the running state files

**#3. Switchboard manifest renders all parallel Braindeads as `instance:1`** despite `state-instances.json` correctly assigning 1/2/3/4. Cause: `_write_manifest` only refreshes `actor`+`intent` per row at write time; `instance` was stamped once at this session's own sidecar fire and never re-derived. Collapses S023/D-017 parallel-instance UX into ambiguous "Braindead·1" — sidebar can't tell sessions apart, click-to-focus can't disambiguate.
- **Status.** ✅ Landed in S042 commit `cd402d6`. Refactored `_detect_instance` to return `Optional[int]` (None when uncertain), then both the existing call site at line ~736 and the new per-row manifest refresh fall through to prev value instead of regressing real N→1.

**#4. `actor: unknown` on UserPromptSubmit-first-turn.** UserPromptSubmit fires before the agent writes intent for the turn. The cascading resolver (S039) eventually corrects via write-time refresh from another session, but if no other session fires sidecar in the meantime, it sticks until this session's `Stop`. Self-corrects fast on multi-session machines.
- **Status.** Deferred — bites only on truly-single-session machines. Mitigation: principal's typical use is 3-5 parallel sessions, so write-time refresh from sibling fires resolves it within seconds.

### Tier 2 (continued) — confirmed but lower-severity

**#5. Idle GC sweeps players + base actors but NOT dwarves/gnomes/penguins.** `despawnIdleInstances` walks `instanceNodes` (player instance ≥2) and the three base actors. **A sub-agent whose `despawn-*` event was lost stays forever**, keeping its `intents[]` entry, which can dominate cluster relayout indefinitely. State.ndjson append-race could lose a `despawn-dwarf` line under concurrent writes.
- **Code refs.** `index.html` `despawnIdleInstances` body.
- **Fix shape.** Extend the function to also walk `dwarfNodes` / `gnomeNodes` / `penguinNodes`. Same 5min idle threshold. Cleanup via `despawnDwarf(id)` / `despawnGnome(id)` / `despawnPenguin(id)` + `clearIntent(id, false)`. ~25 lines.

**#6. `state-instances.json` byId never gets cleaned on session crash.** Was: only `handle_session_end` cleared byId. Crashes left entries forever; `next` drifts upward; slot reclaim operates against polluted byId; symptom = "Braindead-17 with four live sessions."
- **Status.** ✅ Landed in S042 commit `cd402d6`. New `_gc_state_instances(live_full)` paralleling `_gc_state_actors`, wired into the `UserPromptSubmit`-only GC pass.

### Tier 3 — medium / latent (real but require specific conditions)

- **#7. `spawn-braindead` short-circuits on stale `_mode=dev-brain`** (handle_active_mode_write:625-634). Crashed prior dev-brain session leaves marker; new dev-brain session's mark-write is no-op; spawn-braindead never fires; sprite only appears via `ensureActorExists` self-heal on first move event. Bubble missing until then. **Fix:** also check whether the stale marker's session is in `live_full` before short-circuiting.
- **#8. Background Task may never despawn until 5min idle + can misattribute activity.** `handle_task_post:1415-1418` returns early for background entries. LIFO binding from `pendingAgentBind` may attach activity to wrong dwarf when multiple spawns pending; the other dwarf despawns at 5min while still running. **Fix:** match by `tool_use_id` rather than LIFO, OR explicit dwarf-id stamping in the spawn event.
- **#9. `spawnDwarf` / `spawnGnome` throw on unknown `ev.at`** (no `STAND[ev.at]` presence check). Malformed spawn event aborts mid-function with `currentBuilding` already set; subsequent moves find no DOM node. Penguin path has the safe iceberg fallback; gnome and dwarf don't. **Fix:** fallback to `inbox-square` (workshop for gnomes?) like penguin's iceberg.
- **#10. `spawnGuthix` silently no-ops on unknown `ev.at`** (`if (!b) return;`). No console trace; subsequent `setIntent('guthix')` early-returns. **Fix:** fallback to `lorebook-library` + console.warn.
- **#11. `setIntent` silently early-returns when `actorPositions[actor]` missing.** Sub-agent failure mode — if `spawn-dwarf` event lost from state.ndjson but later `intent` event for that dwarf lands, bubble silently no-ops with no console warning. **Fix:** console.warn + try ensureActorExists rather than silent-return.
- **#12. state.ndjson concurrent-append interleave.** 3,706+ lines / 771KB+; appending from N parallel sessions is not atomic. Visualizer silently skips bad JSON lines. **Fix:** either rotation (append to per-day file, manifest concatenates) OR file-lock around append. Defer until visibly breaks.
- **#13. Lane-layout has no viewBox-edge clamp + no upper-bound on bubble Y.** Clusters at map edges may clip; inter-cluster Y push has no floor. **Fix:** clamp at write time.
- **#14. `actorBaseName` doesn't recognize sid8 suffix.** Bubble outline accent color falls to default brown for any `actor-sid8` actor. Subsumed by #1's fix (once `ev.actor` is stripped upstream, this stops mattering).

### Tier 4 — housekeeping (cruft)

- Two garbled-path files at brain root from PowerShell escape pathology. Archive only, don't delete.
- Dead procedural-building helpers (`isoBuilding`, `wallTexture`, `roofTexture`, `swWallPoly`, `seWallPoly`) — uncalled after S039 sprite migration. Sweep next bankstanding.
- 5 zombie empty `bySession` entries in `state-dwarves.json`. Not GC'd by `_gc_state_actors`. Possible #6-style extension to also clean state-dwarves.
- Stale carry-forward in `respawn.md:133` about dead day-night code — already deleted in S033, retire the line.

## What S042 landed

- **#3** manifest per-row instance refresh — `status-sidecar.py` (commit `cd402d6`)
- **#6** state-instances.json crash cleanup — `status-sidecar.py` (commit `cd402d6`)

Together these restore parallel-Braindead sidebar disambiguation (Braindead·1 / ·2 / ·3 / ·4 visible) and stop drift of the `next` allocation high-water.

## What's carried forward to next session

In priority order, with exact code refs:

1. **#1 suffix-strip propagation** (`index.html` `applyEvent`). Highest user-visible impact. ~20 lines.
2. **#5 idle GC for sub-agents** (`index.html` `despawnIdleInstances`). Defensive; stops "dwarves stick forever" on lost despawn events. ~25 lines.
3. **#2 sprite anchor recalibration** — owned by f9da453a per @-mention in comms. If they decline, comes back here last.
4. **#7-#14** triaged opportunistically when adjacent code is touched.

## Lessons

- **"Proceed in parallel" works for non-overlapping commits, not interactive concurrent editing.** Three Edit-tool attempts back-to-back failed because f9da453a was rewriting sprite definitions between my Read and Edit. Line numbers shifted +13 then more. Edit tool requires file stability between read-anchor and write — that doesn't hold under live concurrent writes. Worth folding into [[D-024]] as a constraint: "logically separable" doesn't help if the toolchain can't apply changes against a moving file.
- **Audit-then-fix shape generalizes.** Three dwarves on non-overlapping scopes → principal synthesis → tier-ranked triage → fix loop with sign-off. Same shape used for S027 visualizer audit, S033 visualizer audit, this S042 audit. Worth promoting the *shape* to a [[gielinor/spellbook]] skill — "cross-cutting subsystem audit." Penguins do the same for outward-facing research; this is the inward-facing equivalent.
- **The respawn carry-forward list ages fast.** D3's verification pass found at least 3 carry-forwards already-fixed but still listed (S031 dead day-night code, S033's `despawnPlayerInstance` bubble-fade, S033's `ensureActorExists` strip — partially fixed). Carry-forward debt accumulates on its own clock; a respawn-section "verify still-pending" pass every N sessions would help.
- **Frame ≠ root cause** (echoing [[S038]]'s lesson). "Stuck sprites" sounds like a visual bug; the load-bearing cause is event-key-pollution in pure JS state-mapping (#1). The symptom is visual; the bug is invisible.

## Related

- [[D-024]] — parallel player coordination (drafted same day, S041). This session lived the problem D-024 is about.
- [[D-019]] — parallel Braindead instances + comms channel (the substrate that lets parallel sessions coordinate at all).
- [[D-020]] — terminal switchboard (the system whose `instance:1` collapse #3 fixes).
- [[D-017]] — parallel player instances (parent of D-019/D-020).
- [[S033]] — prior visualizer audit (12 fixes shipped, same shape).
- [[S027]] — earlier visualizer audit (11 fixes shipped).
- `gielinor/spellbook/rituals/` — candidate home for the audit-then-fix skill if promoted.

## S052 amendment — 2026-05-23

The map was killed in [[S052]] / [[D-026]] — the visualizer collapsed to switchboard + chat and moved to `brain/switchboard/`. The Tier-3/Tier-4 carry-forwards above that targeted map code (sprite anchor recalibration #2, idle GC for sub-agent sprites #5, lane-layout viewBox-edge clamp #13, animal scatter housekeeping, dead procedural-building helpers) are **obsolete** — the surface they referenced no longer exists. State-file paths in §D3 above now live at `brain/switchboard/state-*.json`. The event-routing and resolver concerns (#1 suffix-strip, #3 manifest instance refresh, #4 actor-unknown, #6 byId crash cleanup, #11 setIntent silent-return) live on through `status-sidecar.py` / `emit-event.py` and remain relevant for the chat panel + switchboard rows.

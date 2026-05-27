# S049 — map fixes: wander + switchboard action line + intent refresh

**Session.** S049 / sid8 17e701eb (Braindead instance 2).
**Started.** 2026-05-23. Opened as Jebrim, flipped to dev-brain immediately after partial respawn — principal cued "lets develop gielinor. We need to work on the map." Mini-respawn skipped quest-log hand-off (no Jebrim quest existed this session).

## Frame

[[S048_b070e9be_visualizer_manifest_driven_sprite_sync|S048]] inverted the visualizer to manifest-driven and *thought* it had landed wander + sprite state-classes. Live observation post-S048: sprites are still standing still, switchboard rows show stale intent from earlier in session and never refresh. Principal asked to clarify map intent first, then dwarf the fix.

## Intent doc (the contract the dwarves work against)

**Single source of truth:** switchboard manifest. Map renders it.

**Three legibility layers:**
- **Intent** — agent-written `.claude/intent/<actor>-<sid8>.txt`, low cadence, "why/what scope" — bubble + sb-row line 1.
- **Action** — hook-emitted on each tool call, high cadence, "which file/which tool" — sb-row line 2 + COMMS.
- **Liveness** — manifest state + ambient wander, per-poll, "actor is alive" — state-class glow + visible drift.

**Invariants:** (1) sprite ↔ manifest record. (2) sprite at `record.building`, building change → walk. (3) state-class matches `record.state`. (4) working sprites visibly drift. (5) sb-row shows intent + latest-action-with-age. (6) static jebrim/zezima hidden when no live session. (7) sub-agents inherit parentSid8.

**Out of scope:** state.ndjson-driven sprite presence; demanding agent narrate intent every turn.

## Diagnosis (pre-spawn)

- **Bug A (sprites don't wander).** `tickWanderForActor` at `index.html:2637` uses `setAttribute('transform', ...)` on the SVG transform **attribute**; CSS `.wander { transition: transform 1200ms }` only transitions the CSS transform **property**. Result: instant jumps every 4–12s, no visible drift.
- **Bug B (no action line).** `.sb-row` has `.sb-intent` only; manifest has no `latest_action`. Row freezes when intent doesn't change.
- **Bug C (intent stales).** Largely the discipline reality (agent doesn't re-write intent each turn). Bug B's action line gives the row freshness from a high-frequency source; C dissolves once B lands. D3 verifies the manifest's intent-refresh path works as designed.

## Dwarves (spawned 2026-05-23, parallel, background)

- **D1 — wander animation fix.** `experiments/visualizer/index.html` ~3 lines (CSS-property swap for the .wander inner transform).
- **D2 — switchboard action line.** `status-sidecar.py` (manifest `latest_action`/`latest_action_ts`) + `index.html` (sb-row second line, age-tick).
- **D3 — intent refresh verification.** Read-only smoke test of manifest's `_detect_intent` / `_write_manifest` path against live session.

Sibling quest-log files at:
- `quest-log/in-progress/S049_17e701eb_d1_wander.md`
- `quest-log/in-progress/S049_17e701eb_d2_switchboard-action.md`
- `quest-log/in-progress/S049_17e701eb_d3_intent-refresh.md`

## Per-turn log

- T1 (2026-05-23). Spawned D1/D2/D3. Returning control to principal.
- T2 (2026-05-23). All three dwarves back. Synthesis: D1 wander animation, D2 manifest+sb-action line, D3 verdict "plumbing fine, cadence was the symptom." All landed in main (verified via grep).
- T3 (2026-05-23). Principal observed sprites still move too little when working. Decided on state-aware wander (single-actor option, no new spawn). Edited `index.html` directly — replaced flat WANDER_MAX_PX / WANDER_MIN/MAX_INTERVAL_MS constants with `WANDER_STATE_TABLE`: working ±35px every 1.2–3.5s, waiting ±18px every 4–12s, closing ±10px every 6–14s, idle/ended frozen. Added `wanderParamsFor(g)` helper, modified `tickWanderForActor` + `maybeTickWander` + `moveActor`. `setSpriteState` now clears the wander timer on state change so transitions feel responsive.

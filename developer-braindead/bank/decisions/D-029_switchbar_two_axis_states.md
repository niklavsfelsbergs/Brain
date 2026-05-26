# D-029 — 2026-05-24 — Switchbar status vocabulary: two-axis split (state + tags)

**Context.** The fleet board's status enum ([[D-020_terminal_switchboard]] / [[D-028_switchboard_cockpit_rebuild]]) was one field doing two jobs. It carried both *ball-holder* states (`working`, `waiting_for_user`, `waiting_for_answers`, `waiting_for_subagents`, `idle`) and *activity-flavor* states (`alching`, `wrapped_up`) in a single `state` field. The symptom: a precedence ladder in `status-sidecar.py` main() — "alching only replaces a *plain* working turn", "wrapped_up *holds across* working/waiting" — which exists solely because two orthogonal axes were crammed into one slot. Three live seams traced back to it ([[S077_e0f2af5d_cockpit-swarm-verification|S077]] parked finds + this audit):

1. **Stuck `WORKING` is indistinguishable from a long real turn.** The sidecar fires only on `UserPromptSubmit`, `Stop`, `SessionEnd`, and Pre/Post for two tight matchers — *not* ordinary tool calls. So `last_event_ts` is frozen for a whole working turn, and the only decay we had was `waiting_for_user → idle`. A crashed-mid-turn session reads WORKING until the liveness gate drops the whole row (process-dead, or 1h stale).
2. **`ENDED` was dead config** — in `STATE_LABEL`/`STATE_RANK` but filtered out of the manifest, so it never rendered.
3. **Manifest staleness** when one session is mid-long-turn ([[S077_e0f2af5d_cockpit-swarm-verification|S077]] find #1) — same root as #1.

Decided in dev-brain [[S078_959a4c34_switchbar-two-axis-states|S078]] with the principal driving the reframe.

## Decision

Split the one enum into **two axes**:

- **Base state** (the chip — answers *"what do I do about this one?"*): `busy`, `needs_you`, `your_move`, `stalled`, `idle`, `done`. (`ended` stays an internal token but is filtered off the board.)
- **Flavor tags** (ride on the chip, never replace it): `alching`, `crew` (with subagent IDs), `wrapped`. Independent of the base state — a session is `busy + [alching]` or `done + [wrapped]`. This kills the precedence ladder: tags annotate, they don't compete.

### Base-state set

| Chip | Token | Trigger | Derived where | Attention |
|---|---|---|---|---|
| **BUSY** | `busy` | prompt submitted; tool running; foreground spawn out; actor unresolved | sidecar (absorbs old `working` + `waiting_for_subagents`) | no |
| **NEEDS YOU** | `needs_you` | `AskUserQuestion`/`ExitPlanMode` mid-call; never decays | sidecar Pre-override | yes — **hot ping** |
| **YOUR MOVE** | `your_move` | `Stop` (turn ended, parked) | sidecar | yes — **soft ping** |
| **STALLED** | `stalled` | `busy` AND no action heartbeat for `STALL_AFTER_SEC` (300s) | **backend**, on read | yes — count only |
| **IDLE** | `idle` | `your_move` quiet > `IDLE_AFTER_SEC` (300s) | backend (unchanged) | no |
| **DONE** | `done` | `.mode` = `wrapped_up`; terminal lingering | sidecar | no |

Hard `ended` (SessionEnd / process-dead) stays filtered off the board — a closed terminal shouldn't linger. DONE is only the graceful-wrap-terminal-open case.

### Resolved knobs (principal)

1. **`STALL_AFTER_SEC = 300`** (5 min). Generous enough that normal turns (tools fire every few seconds) never trip it; a marathon single tool call self-corrects the moment it returns and bumps the heartbeat.
2. **Two distinct pings**, not bell-on-one: `needs_you` gets an urgent (hot) sound, `your_move` a gentle (soft) one. Both ring on a *new* entry into the state. `stalled` is silent (visual + high rank only).
3. **Backend re-reads `state.ndjson` per poll** for the action heartbeat, rather than trusting the manifest's frozen `latest_action_ts`. One capped tail-read per poll builds a `{sid8: last_action_ts}` map. This is what makes STALLED honest and closes seams #1 + #3 — it decouples "actually progressing" from "did the sidecar fire."

## Implementation seam

- **Sidecar** emits the new base-state tokens + a `tags` list on the record; the `.mode`/crew overrides set **tags**, not `state` (only `wrapped_up → done` remains a state-setting marker, a genuine lifecycle end). The precedence ladder is removed.
- **Backend** (`build_session_model`) derives `stalled` and `idle` on read off the fresh heartbeat map; updates `STATE_RANK`/attention.
- **board.js** — new `STATE_LABEL`/`STATE_RANK`, renders `tags` as small chips.
- **main.js** — two ping functions, prev-set tracked per attention kind.

Contracts otherwise preserved per [[D-028_switchboard_cockpit_rebuild]] (the cockpit backend is now the sole consumer of the status manifest, so the token rename is a safe clean break).

## Rank (board order)

`needs_you (0) > your_move (1) > stalled (2) > busy (4) > idle (7) > done (8)` — STALLED surfaces near the top so a possible crash gets noticed.

## Consequences

- The ladder-shaped overrides in the sidecar disappear; flavor is additive.
- STALLED gives the operator a real "go check this" signal the board never had.
- `bankstanding` as a tag is deferred — it needs a `.mode` marker the rituals don't write yet. Noted, not built.
- Live UI needs a cockpit relaunch to verify (stale code in the running window); `node --check` + `py_compile` are the pre-commit gates.

## Related

- [[D-020_terminal_switchboard]] — terminal switchboard; origin of the status sidecar + state vocabulary.
- [[D-028_switchboard_cockpit_rebuild]] — cockpit rebuild; preserved-contract note and the original state list this supersedes.
- [[D-027_inward_outward_build_imbalance]] — inward/outward imbalance; this is observability polish, explicitly bounded so it doesn't extend the time-sink.
- [[S078_959a4c34_switchbar-two-axis-states|S078]] — quest-log entry capturing the build.

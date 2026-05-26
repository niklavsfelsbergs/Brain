# D-024 — 2026-05-22 — Parallel player coordination: shared comms + session-suffixed state

**Context.** [[D-017_parallel_player_instances]] gave parallel player instances per-session sprites and visualizer attribution. [[D-018_parallel_session_substrate_isolation]] session-keyed intent files and `state-actors.json`. [[D-019_parallel_braindead_and_comms_channel]] built a comms channel for parallel Braindead and explicitly punted parallel-player coordination ("future decision") and cross-brain coordination ("current architecture has no answer").

That future arrived. Niklavs routinely runs parallel player sessions — two Jebrims on different threads, or Jebrim + Zezima side-by-side. Visualizer is fine; the disk isn't:

1. **`inventory/<topic>.md` clobber.** Per-quest resume state, single-writer-assumed. Two Jebrim sessions writing the same topic overwrite silently.
2. **Quest-log `SNNN_*.md` allocation race.** SNNN picked by scanning existing files; two sessions starting near-simultaneously can both pick the same N.
3. **Cross-player wrong-terminal blindness.** The `communication-protocol.md` wrong-instance check is *content-based* (does this ask fit my domain?). It catches the principal mis-addressing one terminal but doesn't catch the agent being unaware a sibling exists.
4. **Cross-player global-surface collisions** — `players/inbox/`, global `examine/drafts/`, `niksis8/drafts/`, `lorebook/drafts/`. Date-prefix filenames; last-write wins.
5. **Liveness signal is intent-file mtime.** S032 flagged this as strictly weaker than [[D-020_terminal_switchboard]]'s status sidecar — a session can be alive with a 10-minute-old intent file mid-long-task.

The light-coordination posture D-017 took for parallel Jebrims ("principal disambiguates by eyeballing the visualizer") doesn't cover the disk hazards. This decision fixes the bulk of them with one new file + one suffix rule + a sidecar swap, parallel to D-019's shape.

## Decision

Four coordinated changes:

### 1. `gielinor/comms/active.md` — one file, all players + deities

Append-only log, same protocol as `developer-braindead/comms/active.md`. Single file covering Jebrim, Zezima, Guthix, future-roster — cross-player visibility from day one. Per-player files would fragment the wrong-terminal check at exactly the moment it pays off.

Entry kinds: `OPEN` (respawn), `UPDATE` (mid-session pivot), `→ @<actor>-<sid8>` (dialogue), `CLOSING` (session-close). Header format identical to D-019:

```
[YYYY-MM-DD HH:MM] <actor>-<sid8> <KIND>
```

Concurrent-write safety inherits from D-019: `open(..., 'a')` is atomic for small writes on Win+POSIX; line-level garbling tolerated, no lockfile.

### 2. Liveness via [[D-020_terminal_switchboard]] status sidecar

Sibling detection at respawn reads `~/.claude/status/*.json` for sessions matching:

```
state ≠ ended AND last_event_ts < 5min AND actor in {jebrim, zezima, ...}
```

Cross-reference with `gielinor/comms/active.md` — any session id in the sidecar manifest without a matching `CLOSING` entry is a confirmed-live sibling. Surface to principal before posting OPEN.

Strictly stronger than intent-file mtime (S032 carry-forward). Ship from the start; don't retrofit later.

### 3. Session-suffix only the state files

Two surfaces get `__<sid8>` suffix:

- **Inventory:** `inventory/<topic>__<sid8>.md` (e.g., `inventory/eu-tender-resume__a1b2c3d4.md`).
- **In-progress quest-log:** `quest-log/in-progress/SNNN_<sid8>_<slug>.md`.

Drafts (`bank/drafts/notes/`, `examine/drafts/`, `niksis8_character/drafts/`, `keepsake/proposals/`) stay plain. The comms `OPEN` announces topic territory; drafts are spontaneous enough that filename collision risk is low and disk clutter avoidance wins.

The SNNN race window survives — two sessions allocating SNNN+1 within seconds get different files (different sid8) but same N. Acceptable: SNNN drifts from unique-key to approximate-temporal-ordering. Same tolerance D-019 took for dev-brain.

### 4. Respawn rule for inventory recovery

Updated step in `gielinor/spellbook/rituals/respawn.md`:

> When loading inventory, prefer `<topic>__<own-sid8>.md` if present. Otherwise list all `<topic>__<sid8>.md` files; cross-reference each sid8 against the comms log and the sidecar manifest. Surface the candidates to the principal: clean-CLOSING sessions are recoverable, no-CLOSING-with-dead-sidecar sessions are crashed, live siblings shouldn't have their inventory touched.

Suffixing alone doesn't decide which file is canonical. The discipline line does.

## File and ritual changes

- `gielinor/comms/active.md` + `gielinor/comms/_about.md` scaffolded.
- `gielinor/spellbook/rituals/respawn.md` — sibling-detection + comms-read + OPEN-entry + inventory-recovery rule added.
- `gielinor/spellbook/rituals/close-session.md` — CLOSING-entry step added before commit.
- `gielinor/meta/layer-routing.md` — inventory and quest-log rows updated with suffix shape.
- No hook changes. No visualizer changes. Discipline + the existing sidecar.

## Out of scope for the first cut

- **Cross-brain coordination.** A Jebrim session and a Braindead session in parallel don't see each other — two comms files (`gielinor/comms/active.md` and `developer-braindead/comms/active.md`), no bridge. The fix is one root-level `comms/active.md` shared across both brains; defer to a future decision.
- **Draft filename collision prevention.** Two parallel Jebrims drafting the same source on the same day still overwrite. Comms OPEN gives advance warning but doesn't enforce. Tolerated.
- **SNNN allocation lock.** Race window survives. Lockfile possible but D-019 declined the same tradeoff and this decision matches.
- **Hook enforcement.** No `parallel-coordination.py` hook. Discipline rule lives in `respawn.md` and `close-session.md`.
- **Players posting to dev-brain comms or vice versa.** Each brain reads its own file.

## Open questions

- **Comms file growth.** Unbounded append. Inherits D-019's manual-rotation plan; can automate to `comms/archive/active-YYYY-MM-DD.md` later.
- **Three-fresh-sessions collision.** Three Jebrim respawns within seconds could all see "no siblings" before any posts OPEN. Principal sees three fresh OPENs and brokers. If routine, brief lockfile at respawn-step.
- **Cross-brain drift.** D-019 §Out-of-scope §4 noted Jebrim+Braindead might "collide on intent." This decision doesn't fix that. Track as a deferred branch; revisit when a real collision happens.
- **Guthix consultation entries in comms.** Consultation is chat-only by default ([[D-022_guthix_consultation_mode]]). Should Guthix post OPEN/CLOSING? First cut: yes, lightweight — one line each. Sidecar already tracks his sessions.

## Related

- [[D-017_parallel_player_instances]] — parallel player instances; this completes its disk-side gap.
- [[D-018_parallel_session_substrate_isolation]] — substrate isolation; per-sid8 intent files are the precedent for per-sid8 inventory + quest-log.
- [[D-019_parallel_braindead_and_comms_channel]] — parallel Braindead + comms; this is its player-side mirror.
- [[D-020_terminal_switchboard]] — status sidecar; liveness signal source.
- [[D-022_guthix_consultation_mode]] — Guthix consultation; in scope as a participant in the global comms file.
- `gielinor/meta/communication-protocol.md` §"Wrong-instance check" — content-based sibling check; this decision adds the file-system-based one.

## S052 amendment — 2026-05-23

`status-sidecar.py` still mirrors both `comms/active.md` files into the switchboard dir for browser fetch (the http.server roots there). Mirror filenames unchanged (`state-comms-braindead.md`, `state-comms-gielinor.md`); their destination moved from `developer-braindead/experiments/visualizer/` to `switchboard/` per [[D-026_switchboard_promotion]]. Sandbox shape and concurrent-append discipline above are unchanged.

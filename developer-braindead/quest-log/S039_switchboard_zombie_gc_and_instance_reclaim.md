# S039 — 2026-05-22 — switchboard zombie GC and instance-slot reclaim

**Status.** Done end-to-end. All five live sessions now resolve to their actors in the switchboard; instance numbers compacted from 1..N; future allocations reclaim freed slots.

## What happened

- **Diagnosed three compounded "sprites stuck / switchboard all UNKNOWN" symptoms.** Principal reported every session showing `actor=unknown` in the switchboard and zombie sprites lingering on the map. Tracing through `status-sidecar.py` and `state-actors.json` surfaced three independent root causes layered on top of each other: (1) `_detect_actor` returns `unknown` when zero or multiple intent files match `*-<sid8>.txt` — both modes fire in the wild (no narration yet vs leftover files from a mid-session player switch); (2) `state-actors.json.byId` accumulates entries from sessions that died without firing `SessionEnd`, plus top-level `wisp` / `guthix` scalars with no owner-marker concept; (3) `UserPromptSubmit` (the sidecar's most-frequent registration) fires *before* the agent writes intent for the turn, so `actor=unknown` lands in the status file at turn-start and sticks through the working state until `Stop` fires at the end.

- **One-time cleanup pass.** Archived 30 stale + junk intent files into `brain/.claude/intent/archive/` (per `archive-discipline.md` — never delete). Deduped session `0f7bf46f`'s pair (kept newer `braindead-`, archived older `jebrim-`). Wrote a proper `braindead-b427fb24.txt` for the current session. Rewrote `state-actors.json` removing zombie `byId` entries + orphan top-level scalars.

- **Cascading actor resolver.** Replaced `_detect_actor`'s `len != 1 → unknown` cliff with: (1) one intent file matches → use it; (2) multiple match → newest by `mtime` wins; (3) none match → fall back to `state-instances.json` `byId` reverse lookup (highest instance number wins when a session is registered under multiple actors). `emit-event.py` registers an instance on every attributed action, so any session that's done *any* work is reachable from this fallback — even when intent narration hasn't been written yet.

- **Manifest write-time actor refresh.** `_write_manifest` now re-detects actor for each session at write time against the intent dir + instance map. Canonical `<sid8>.json` is untouched (would race with the owning session's writes). Result: every sidecar fire from any session refreshes the *whole* sidebar; a session stuck in `actor=unknown` from its UserPromptSubmit resolves on the next other-session fire (5-30s in practice) rather than waiting until its own `Stop`.

- **Periodic zombie GC.** Added `_live_session_ids`, `_gc_state_actors`, `_gc_intent_files` to `status-sidecar.py`. Gated on `UserPromptSubmit` only (one fire per turn, lowest-frequency registration, post the current session's status refresh so the GC can't classify itself as dead). Liveness ground truth = `~/.claude/status/<sid8>.json` with `state ≠ ended` AND `last_event_ts` within 1h. Drops dead `byId` entries; drops `_mode_session_id` / `_guthix_session_id` when the owner is dead; drops the `guthix` top-level scalar when no owner marker exists (wisp left alone — markerless by design, doesn't accumulate); archives `*-<dead_sid>.txt` intent files (current session always exempt as a first-fire belt).

- **Mini-respawn intent archive step.** Added step 2 to `gielinor/spellbook/rituals/respawn.md` mini-respawn: outgoing actor's per-session intent file moves into `archive/` on player switch. Closes the same-turn ambiguity window the periodic GC would close anyway, but does it within the switch itself.

- **Instance slot reclaim.** Principal flagged that `braindead` had climbed to `·17` with only four live sessions. `resolve_instance` was allocating monotonically from `next`; `handle_session_end` was already deleting `byId` entries but the comment noted "Reusing low-numbered slots is a separate optimization." Now allocates the lowest free integer not in `by_id.values()` — slot freed by `handle_session_end` is reclaimed by the next new session. `next` kept as diagnostic high-water mark. One-time manual compaction of `state-instances.json` snapped current live sessions back to 1..N.

## Observations to carry

- **The "monotonic + reclaim opportunistic" comment was load-bearing.** `handle_session_end`'s `next stays where it was; reclaim is opportunistic` line documented a chosen non-optimization — and that choice produced exactly the visible regression the principal flagged ("braindead-17 with four live sessions"). A note that says "we chose not to do X" is a debt marker; "deferred for later" comments accumulate user-visible cost on their own clock. Pair with [[S029_parallel_braindead_and_comms_channel]]'s D-017 deferred-branches observation — there's a wider pattern of "deferred for later" tightening into "wait, why is X like that" questions weeks afterward. Worth a [[lorebook]] draft.

- **`UserPromptSubmit` fires *before* the agent works — actor detection can't anchor on it.** The S037 sidecar-registration shape (UserPromptSubmit + Stop + SessionEnd) is correct for hook-fire-budget, but UserPromptSubmit *literally cannot* know the actor for the current turn because the intent file gets written by the agent during the turn that the prompt initiates. The right architecture is: the status file records what it *can* know at fire time, and the manifest layer re-derives anything that can be sharper. Generalize: **for two-layer state where the inner layer is captured at irregular points and the outer layer is read on demand, refresh-on-read beats write-back.**

- **The cascading-fallback shape generalizes.** `intent file (explicit narration) → mtime tiebreaker → state-instances.json (implicit from work done)` is the same pattern that recurs whenever you have a "principal voluntarily writes X, but you can derive X from observed behavior anyway." Sidebar identity here, error messages elsewhere, default-route inference earlier. Name it if it shows up a third time.

- **PS 5.1's `Set-Content -Encoding utf8` writes a BOM and Python's `json.loads` tolerates it but reads of partial files via emit-event.py do not always.** Tripped during the one-time `state-instances.json` rewrite. The fix (`System.IO.File.WriteAllText` + `UTF8Encoding $False`) is the right shape for *all* PowerShell-touched JSON. Pair this with the S037 "ASCII for `.ps1` scripts" lesson — they're the same family of Windows-substrate gotchas, both worth one lorebook draft.

- **One-time cleanup ran with a stale live-set; the automated GC won't have that problem.** When I did the initial intent-dir sweep, I read the live set once and used it as a static list — two sessions (`996503de`, `4508bd10`) spawned between snapshot and sweep, and their intent files got archived on a list that didn't know about them. Self-heals (next intent narration restores) but worth noting: any one-shot cleanup needs to either run very fast (before new state appears) or read its ground truth at sweep-time, not at plan-time.

## Files touched

- `developer-braindead/.claude/hooks/status-sidecar.py` — `ACTORS_PATH` + `LIVE_SESSION_SEC` constants; new `_live_session_ids`, `_gc_state_actors`, `_gc_intent_files`, `_actor_from_instances`; `_detect_actor` rewritten as cascading resolver with `session_id_full` parameter; `_write_manifest` re-detects actor per session at write time; main() wires GC behind `UserPromptSubmit` and passes full session id to detector.
- `developer-braindead/.claude/hooks/emit-event.py` — `resolve_instance` now allocates lowest free integer in `by_id.values()` instead of monotonic `next`.
- `developer-braindead/experiments/visualizer/state-actors.json` — one-time cleanup of zombie `byId` + orphan top-level scalars.
- `developer-braindead/experiments/visualizer/state-instances.json` — one-time compaction (braindead 12/15/16/17 → 1/2/3; jebrim 12 → 1).
- `brain/.claude/intent/` — 30 files archived into `archive/`; current session's `braindead-b427fb24.txt` written.
- `gielinor/spellbook/rituals/respawn.md` — new step 2 in mini-respawn: archive outgoing actor's per-session intent file on player switch.

## What's still pending

- **Carried from prior sessions, unchanged by this one** — S031 lane bubbles untested, penguin live test, parallel-Braindead visual tuning, cross-repo sidecar rollout, S037 cross-window click-to-focus, Guthix live test (consultation + bankstanding), subtask debounce, replay demos, drafts triage, audit follow-ups, first live gnome spawn, Q-008.

- **Visual ghost period after compaction.** The visualizer may briefly show ghost sprites at the *old* high instance numbers for the four compacted sessions until the 5-min idle-despawn timer clears them. One-time visual cost.

- **Lorebook draft pair (Windows substrate gotchas).** S032 hook-fire-rate-as-budget + S037 ASCII-PS for `.ps1` + S039 BOM-free encoding for JSON written from PS = three Windows-substrate lessons that compose into one draft. Carried for next bankstanding.

- **Lorebook draft (deferred-branches debt).** S039's instance-monotonic + S029's D-017 deferred branches surfaces a pattern: "comments noting we chose not to do X" become user-visible bugs on their own timeline. Worth one draft.

**Cascade.** `quest-log/S039_switchboard_zombie_gc_and_instance_reclaim.md` (this entry); `respawn.md` refresh below.

**Main-brain changes.** `gielinor/spellbook/rituals/respawn.md` mini-respawn step 2 added (intent archive on switch). No other gielinor surfaces touched.

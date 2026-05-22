# S047 — visualizer: cluster-stack + helmet clearance

**Session.** braindead-a110d573 (this session). Opened as Jebrim, flipped to dev-brain mid-conversation via "lets develop gielinor" to implement a viz design.

**Surface touched.** `developer-braindead/experiments/visualizer/index.html` only.

## What landed

### 1. Principal + sub-agents cluster (proposal #3 from chat)

`relayoutBubbles()` rewritten. Replaces S029 X-proximity lane tiling with **parent-based grouping**:

- Sub-agents (`/^[DGP]\d+$/`) look up principal via `subAgentParentSid[id]` → parentSid8, then a fresh reverse-map of `baseActorToSid` + `actorInstanceToSid` resolves sid8 → principal actor key.
- Bubbles group by principal regardless of sprite-X proximity.
- Multi-member groups stack vertically: **principal at the bottom** (closest to sprite, keeps the thought-trail anchor), sub-agents above in **reverse spawn order** (newest at top).
- All members of a stack anchor to the principal sprite's X (either from the principal's bubble entry, or `actorPositions[principalKey]` when the principal has no current intent).
- Non-bottom members get a new `entry.layoutSuppressTrail = true` flag.
- `renderIntent()` honors `layoutSuppressTrail` — clears trail innerHTML + opacity 0 for non-bottom members. Only one trail per stack.
- Pass 4 collision-push acts on stack-bottoms only (singletons + the bottom of each multi-member group). New pass 4.5 rigidly re-flows the stack upward from the (possibly-pushed) bottom so siblings move as one unit.

### 2. Helmet clearance — all bubbles lifted by another -40 px

S039 lifted `GATHER_SLOTS.bubbleY` by -32 (v4 PNG actors taller); the residual gap still read as "bubble sitting on the helmet" per principal screenshot. Bumped all 10 slot bubbleY values by another -40 (`-80 → -120` center, `-110 → -150` back, etc.). No-slot fallback `-68 → -108` in both `renderIntent` and the cluster `baseYOff` default. Result: ~65 px clearance between sprite head and bubble bottom.

## Open — for next session (HIGH-PRIORITY carry)

### Parallel-Braindead spawn failure (S042 #1 carry-forward, recurs)

Same root as **D-025 #1 (suffix-strip propagation)** — fix landed in S042's `915ff92` for the spawn path itself but the spawn flow for *parallel-instance* Braindead still misses cases.

**Observed live this session:** 4 sessions in `state-switchboard.json` (Braindead a110d573 WAITING, Jebrim·3 WAITING, Pending… e3a19e31 IDLE, Braindead·3 b070e9be IDLE). Only 5 sprites in DOM (`actor-jebrim`, `actor-zezima`, `actor-jebrim-2`, `actor-jebrim-3`, `actor-braindead-3`). **My own Braindead a110d573 — the WAITING/active session — has no sprite.** "Pending…" likewise has no sprite (actor unresolved by status-sidecar's cascading resolver).

**Symptom on the map ("pulsating speech cloud" from the principal's S045 screenshot):**
- Hook receives this session's intent narration `Clustering principal + dwarves`, sets `intents['braindead']`.
- No `actor-braindead` DOM node exists for instance 1 (my session's `braindead` key, resolved by status-sidecar at the bare name).
- `reconcileFromManifest` Pass 4 (`index.html:2616`) — `if (!hasSpriteFor(actor)) clearIntent(actor, false)` — deletes the orphan.
- Next intent narration write recreates `intents['braindead']`; next manifest sync wipes it. Loop visible as pulsate.

This presented to the principal as three sub-issues but they're **one root cause**:
- "Pulsating speech cloud appearing and disappearing" — orphan clear loop.
- "1 has a speech bubble other doesn't" — the IDLE Braindead·3 has a sprite + stable bubble; my WAITING Braindead has no sprite so bubble can't stick.
- "4 chats only 2 on the map" — partially viewport crop (Jebrim·{1,2,3} stacked behind one Keepsake Vault sprite, possibly) **and** my Braindead + the Pending session having no sprite at all. Both phenomena present at once; my Braindead is the load-bearing failure.

**Investigation surface — start here:**

1. `applyEvent`'s `intent` event handler. The intent narration `Clustering principal + dwarves` arrives for actor `braindead` (instance 1). Trace: does `ensureActorExists('braindead', <inferred-building>, 1)` get called? If yes, why is there no DOM node afterward? If no, what's skipping the spawn?
2. The "Braindead arrives at the workshop" narration appearing top-left (the `.claude/narration.txt` global narration channel) suggests the hook *did* receive a spawn-shaped event, but the visualizer's spawn path silently failed. Possible: the manifest sync sees `braindead` as a live session BUT spawn keys off something else (e.g., a sub-agent state or a stale `braindead` entry from a prior session that already despawned).
3. `actorPositions` had **10 keys** at inspection time (`jebrim`, `zezima`, `wisp`, `braindead`, `braindead-2`, `braindead-3`, `braindead-4`, `braindead-5`, `jebrim-2`, `jebrim-3`) — instances 1, 2, 4, 5 of Braindead all tracked positions, but **only instance 3 has a current DOM node**. Confirms: stale position entries are accumulating across despawn-respawn cycles; that accumulation may be confusing the spawn idempotency check (something like "already have braindead position → skip ensureActorExists" → silent skip → no sprite).
4. Cross-check the `_detect_instance` allocator in `status-sidecar.py` — at the time of inspection my session resolved as `braindead` (bare, instance 1) while the older still-live session resolved as `braindead-3`. The non-monotonic instance allocation may collide with visualizer's per-instance spawn assumptions. (S039 added the lowest-free-integer allocator; that's the right behavior on the sidecar side, but the visualizer may not be tolerant of it.)

**Recommended path:**
- Step 1: Reproduce with two live Braindead sessions, devtools open. Inspect `actorPositions` + DOM `.actor` nodes at the moment of pulsate.
- Step 2: Set a logpoint in `ensureActorExists` for the `braindead` actor; verify whether it's called and whether it returns early.
- Step 3: Pair the visualizer-side fix with a sweep of stale `actorPositions` entries on despawn (the 10-key accumulation is a smell regardless).

This is D-025 #1 territory but specific to parallel-instance Braindead, not the single-instance case S042's `915ff92` fixed.

## Pending drafts

None this session. Both changes are mechanism; no observation-shaped harvest.

## Files

- `developer-braindead/experiments/visualizer/index.html` — two edits described above.

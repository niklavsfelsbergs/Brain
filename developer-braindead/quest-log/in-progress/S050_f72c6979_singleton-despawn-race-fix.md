# S050 — singleton despawn race fix (S047 carry, complement to S048's inversion)

**Session.** braindead-f72c6979 (this session). Opened in dev-brain mode via "lets develop gielinor", picking up S047's high-priority carry.

**Number.** Bumped 048→050. Mid-session discovered parallel sibling `braindead-b070e9be` had already taken S048 with "manifest-driven sprite sync inversion" (commit `c2b1fbf`) addressing the same carry from a different angle, and `braindead-17e701eb` had S049 OPEN with map fixes. The two changes are complementary: S048 made `syncSpritesFromManifest` the truth source for spawn/move/intent; S050 fixes the singleton despawn timeout race that the inversion didn't touch (the race lives inside `despawnBraindead`/`Wisp`/`Guthix` themselves, called by both the new sync Pass 3 and the existing `applyEvent` despawn-* cases).

**Surface touched.** `developer-braindead/experiments/visualizer/index.html` only.

## Root cause

The three singleton despawns (`despawnBraindead`, `despawnWisp`, `despawnGuthix`) scheduled a 500ms fade-out via `setTimeout` whose closure read the module-level node variable at fire time:

```js
setTimeout(() => { if (braindeadNode) braindeadNode.remove(); braindeadNode = null; }, 500);
```

The closure reads `braindeadNode` when the timeout fires, not when it was queued. Two scenarios where this clobbers a live sprite:

1. **Live race.** A fresh `spawnBraindead` within the 500ms fade window sets `braindeadNode = newg`. The pending timeout fires, removes `newg`, sets `braindeadNode = null`. Spawn lost.
2. **Bootstrap replay (the load-bearing scenario in S047's repro).** `state.ndjson` in this repo carried ~9 historical spawn-braindead + ~9 despawn-braindead pairs, ending on `a110d573`'s spawn at 22:04 with no matching despawn. `pollLive`'s first chunk replays all 18 events synchronously. Each despawn queues a 500ms timeout closing over `braindeadNode`. After the loop ends, `braindeadNode = g_22:04` (latest spawn). ~500ms later the first queued timeout fires, reads `braindeadNode` (now g_22:04), removes it, sets to null. Remaining queued timeouts fire but see `braindeadNode === null` → noop. Net: `braindeadActive=true` (set by 22:04 spawn-braindead), `braindeadNode=null` (clobbered).

`hasSpriteFor('braindead')` returns `braindeadActive && !!braindeadNode` → `true && false` → false. Pass 4 of `syncSpritesFromManifest` (orphan-intent clear) wipes the bubble every 2s poll. Pass 1 (`setIntent`) re-adds it from the manifest. **Pulsate.**

The carry's parallel-instance evidence (`braindead-3` IDLE had a sprite, bare `braindead` instance 1 did not) fits because `despawnPlayerInstance` already used the local-capture pattern — only the singletons missed it.

## Fix

Local-capture pattern applied to all three singletons, parallel to how `despawnPlayerInstance` already operates:

```js
function despawnBraindead(instant = false) {
  if (!braindeadNode) return;
  const g = braindeadNode;
  const finalize = () => {
    g.remove();
    if (braindeadNode === g) braindeadNode = null;
  };
  if (instant) {
    finalize();
  } else {
    g.classList.add('fade-out');
    setTimeout(finalize, 500);
  }
  delete actorPositions['braindead'];
  delete currentBuilding['braindead'];
  freeGatherSlot('braindead');
}
```

Two properties:
- **Local capture.** `g` is the node being despawned; the timeout closes over it. Fresh respawns within the fade window can't be clobbered.
- **Identity check before nulling.** `braindeadNode === g` only nulls if no fresh spawn has replaced the module reference.
- **Instant path** (new `instant` parameter, defaults to `false`). Threaded through applyEvent's `case 'despawn-braindead'`, `case 'despawn-wisp'`, `case 'despawn-guthix'` so bootstrap-replay despawns finalize synchronously — no queued timeouts during replay, no clobber possible even before the local-capture guard kicks in.

Same shape for `despawnWisp` and `despawnGuthix` (cross-referenced via comment to avoid restating).

Caller compatibility verified — `syncSpritesFromManifest` Pass 3 (lines 2569/2575/2581) and `despawnIdleInstances` (lines 4090/4099/4108) call with no arg → `instant=false` default → fade-out behavior unchanged. Only the three `applyEvent` case branches at lines 3909/3911/3913 pass `instant`.

## Files

- `developer-braindead/experiments/visualizer/index.html` — three despawn functions + three applyEvent cases.

## Open — for next session

### Parallel-instance fade-vs-respawn drop (same family, different shape)

`despawnPlayerInstance` correctly captures `g` locally and doesn't null any module variable — so it doesn't suffer the singleton clobber. But it deletes `instanceNodes[actorKey]` immediately while the old DOM node is still fading. `spawnPlayerInstance` then early-returns due to `document.getElementById('actor-' + actorKey)` finding the fading remnant. The respawn is silently dropped within the 500ms window. Next sync (2s later, beyond the fade) recovers.

Not the load-bearing case from S047's repro (the parallel `braindead-3` sprite was stable in the screenshot), but worth fixing pre-emptively for the same family. Either remove the fading remnant in `spawnPlayerInstance` (parallel to `spawnBraindead`'s eager `if (braindeadNode) braindeadNode.remove()`), or thread `instant` through `despawnPlayerInstance` and the `case 'despawn-instance'` branch.

### Verification still owed

Open visualizer at `?live=1` with two Braindead sessions live, devtools console open. Expected:
- `actor-braindead` DOM node present for the bare `braindead` instance (was missing in S047 repro).
- No pulsating speech cloud — bubble stays anchored to a present sprite.
- `Object.keys(intents)` and `[...document.querySelectorAll('svg.map .actor')].map(g => g.id)` should both contain `actor-braindead`.

If pulsate persists, breakpoint in `ensureActorExists` filtered to `actor === 'braindead'` and trace whether spawn is called or skipped. The fix addresses the bootstrap-replay clobber; if the live race surfaces differently the diagnosis will point at a different load.

## Pending drafts

None this session — pure mechanism fix, no observation harvest.

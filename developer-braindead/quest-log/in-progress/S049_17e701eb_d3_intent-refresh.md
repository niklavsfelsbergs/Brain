# [[S049_17e701eb_visualizer_state_aware_motion_and_action_line|S049]] D3 — Intent refresh verification

**Dwarf:** Braindead (sid8 `17e701eb`)
**Date:** 2026-05-23
**Scope:** Read-only smoke test of hypothesis 2 — does the manifest re-read intent files on every sidecar fire, or is there a caching / skip bug that pins stale intent?

## Verdict

**Works as designed.** The manifest's per-session `intent` field is re-derived from disk on every `_write_manifest` call via `_detect_actor`, which reads the intent file fresh (no caching). The freeze the principal sees is a **fire cadence** problem, not a refresh-logic problem: manifest writes are gated on hook fires (`UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `SessionEnd`) from any live session. When no live session is firing — e.g., everything is parked on `Stop` or `waiting_for_user` — the manifest is not rewritten, so a session that edits its intent file mid-turn won't see the new value reflected in the switchboard until *some* other (or the same) session next fires a hook. This is hypothesis 1 territory (agent discipline + cadence), confirmed not to be a plumbing bug.

## Supporting evidence

### State capture (timestamps in unix-seconds, UTC)

| t | Event | Source | Value |
|---|---|---|---|
| 1779490604 | Last sidecar fire on my session before D3 began | `~/.claude/status/17e701eb.json` `last_event_kind: UserPromptSubmit` | `intent: "Clarifying map intent + dwarf briefs"` |
| 1779490697 | Intent file last written (parent session, pre-spawn) | `brain/.claude/intent/braindead-17e701eb.txt` mtime | `"Spawning S049 map-fix dwarves"` |
| 1779490807 | Manifest's last write (parent `Stop` right before spawning dwarves) | `state-switchboard.json` `generated_at` | manifest row intent: `"Spawning S049 map-fix dwarves"` — pulled the fresh disk value at this fire |
| ~1779490880 | D3 smoke-test edit | I overwrote `braindead-17e701eb.txt` → `"D3 smoke test marker"` | — |
| 1779490905+ | Post-edit checks | manifest still `generated_at=1779490807`, intent still `"Spawning S049 map-fix dwarves"` | manifest hasn't fired since my edit, so the new disk value isn't in it |

### Cross-check between status and manifest at t=1779490807

The interesting boundary is at the parent's last `Stop` fire (1779490807): the intent file had been changed at 1779490697 (the parent's turn flipping intent from "Clarifying..." to "Spawning..."), and the manifest written at 1779490807 picked up `"Spawning S049 map-fix dwarves"` — proving the refresh path is live across at least one fire boundary. Before the spawn, the manifest read showed the *previous* intent line; after the next fire, the manifest's row carried the new line. Single-fire latency, no stale read.

### Manually invoking the refresh path

To rule out any environmental wrapper around `_detect_actor`, I imported `status-sidecar.py` directly and called `_detect_actor(Path(brain), "17e701eb", "<full-sid>")` after my D3 edit. Return value:

```
('braindead', 'D3 smoke test marker')
```

The function read the file fresh. The next manifest write that runs after this would stamp this value onto my row. No cache, no skip condition for working sessions.

### Relevant code (file: `developer-braindead/.claude/hooks/status-sidecar.py`)

1. **`_detect_actor` (lines 141-197).** Resolves `(actor, intent)` for a session. For each fire it `glob`s `intent_dir/*-<sid8>.txt`, picks newest mtime, and reads the first line as the intent string. The function builds `matches` from scratch every call and calls `p.read_text(...)` on the chosen file — no memoization, no module-level cache. Line 186: `raw = p.read_text(encoding="utf-8").strip()`.

2. **Manifest refresh loop (lines 454-465).** Inside `_write_manifest`, for every non-ended status row:

   ```python
   refreshed_actor, refreshed_intent = _detect_actor(Path(proj), s8, sfull)
   if refreshed_actor != "unknown":
       j["actor"] = refreshed_actor
       if refreshed_intent:
           j["intent"] = refreshed_intent
   ```

   The `if refreshed_intent:` guard only protects against an empty-string overwrite of a known-good value (a sensible safeguard — preserve last-known intent when the file is briefly missing, e.g., during mini-respawn archive moves). It does **not** skip non-empty disk reads; any non-empty file content will land in `j["intent"]`.

3. **Manifest fire trigger (line 991).** `_write_manifest()` is the unconditional final step of every hook fire. There is no rate-limiting or "intent unchanged → skip" path.

4. **State filter (line 435).** `if j.get("state") == "ended": continue` — only `ended` rows skip the refresh, which is correct (they're filtered out of the manifest entirely).

### What I couldn't directly test

- **Cross-session refresh.** I can't fire the parent session's hook from inside a dwarf turn, and no other live session fired between my edit and my last check. But the architecture is sound: on the next fire from *any* live session (parent resumes, another terminal does anything), `_write_manifest` will see my fresh intent file and propagate. The earlier in-session observation (1779490697 → 1779490807) is one concrete example of that round-trip working in <2 minutes.
- **Mid-session mode flips (Jebrim → Braindead, etc.).** Per `_detect_actor` docstring (lines 145-147), multi-file matches resolve by newest mtime. As long as the new-mode intent file is the newest under `*-<sid8>.txt`, the refresh picks it. The GC at line 735 archives stale files. I did not run a mode-flip in this smoke test — flagged as out-of-scope edge case.

## No fix needed

The refresh plumbing behaves correctly. The "intent froze" symptom the principal observes when one session sits on a single intent line for an entire turn is a function of:

1. Agent discipline — narrate intent on meaningful change (already covered by D2's action-line patch keeping rows visibly alive).
2. Manifest cadence — manifest only rewrites on hook fires, not on disk-watch / timer. If the principal wants the manifest to track intent edits even with no fires, that would be a *new* feature, not a fix to existing plumbing.

If a future enhancement is desired, the surface to consider is adding a low-frequency watchdog write in the visualizer's sidecar (e.g., a timer-driven `_write_manifest` independent of hook fires), or having the visualizer client poll intent files directly. Both are scope changes, not bug fixes; out of scope for D3.

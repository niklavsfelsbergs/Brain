# Visualizer audit — S021

> **Scope.** `developer-braindead/experiments/visualizer/index.html` (~2933 lines), `developer-braindead/.claude/hooks/emit-event.py` (630 lines), state files (`state.ndjson`, `state-actors.json`, `state-dwarves.json`, `path-map.json`; `state-gnomes.json` not yet created — emerges on first gnome spawn).
>
> **Method.** Read both target files end-to-end. Walked every `applyEvent` case and every hook code path. Cross-referenced path-map.json / SVG `BUILDINGS` / CSS palette / actor-helper functions for invariants. Reviewed README and inline docs.
>
> **Output discipline.** No fixes in this pass — findings only, sorted by severity (bug > consistency > improvement > docs). Each finding cites `file:line`. Principal triages.
>
> **Not yet validated in the wild.** This is the pre-work for the first live gnome spawn (Step 2 of respawn). One real end-to-end run will surface things a static read can't see; this note is the deliberate sweep that shapes what to watch for.

---

## A. Bugs (genuine defects or latent races)

### B1. FIFO `pendingAgentBind` misattributes sub-calls under concurrent / instant-return spawns

**Where:** `emit-event.py:548-577` (`attribute_to_subagent`), interacts with `:464-501` (`handle_task_pre`) and `:504-545` (`handle_task_post`).

**What:** The FIFO `pendingAgentBind` queue binds each spawn's `tool_use_id` to the first subsequent sub-call's `agent_id`. With two spawns in rapid succession where the first returns instantly (no sub-calls), the second spawn's first sub-call pops the *first* spawn's `tool_use_id` from FIFO. When the first spawn's PostToolUse arrives, the cleanup at `:516-518` (`for aid, tui in list(by_agent.items()): if tui == tool_use_id`) removes the binding, but the misattribution already happened. After cleanup, the second spawn's subsequent sub-calls find empty `byAgentId` and empty `pendingAgentBind` — they silently fall through to main-thread attribution.

**Effect:** Sub-agent work misattributed (visually wrong sprite in chat); subsequent sub-calls from the survivor silently land on the wrong actor. No error trail.

**Triggers:** any pattern where two Task calls fire close in time and one returns before making a sub-call. Today's usage is mostly sequential, but parallel sub-agent spawns (per `meta/communication-protocol.md` dwarf-spawn annotation) are explicitly supported.

### B2. Single malformed event halts the entire recency walk

**Where:** `emit-event.py:178-180`.

```python
wt = parse_wall(ev.get("wallTime", ""))
if wt is None or (now - wt).total_seconds() > RECENCY_SEC:
    break
```

`wt is None` (parse failure) and "past window" share the same exit. One corrupt event anywhere in the tail terminates the walk before older-but-valid events are reached.

**Effect:** dwarf/gnome `parent` field can fall back to "wisp" when a real parent exists. Visualizer attaches the sub-agent to the wrong actor / building.

**Fix shape:** parse failure → `continue`; window-past → `break`. (Recorded as a finding, not implementing per audit discipline.)

### B3. Dev-brain override missing in `infer_dwarf_parent`

**Where:** `emit-event.py:146-198` vs `:311-320` (`current_main_actor` has the override).

`current_main_actor` short-circuits to `"braindead"` when `read_active_mode() == DEV_BRAIN_MODE`. `infer_dwarf_parent` does not — it uses the recency walk unconditionally. If dev-brain mode is active but no intent has been written this session yet (e.g., spawn happens before the first intent file write), the walk picks up a player's stale intent from the *previous* gielinor session within the 10-min window. The spawn's `parent` field is then a player who isn't present.

**Effect:** in early-session dev-brain spawns, the sub-agent's `parent` and `at` come from a phantom player. Visualizer places the sub-agent at the wrong building.

### B4. Persisted `_mode` outlives the session — ghost despawn on next gielinor session

**Where:** `emit-event.py:211-253` (`handle_active_mode_write`); state at `state-actors.json:1` shows `"_mode": "dev-brain"` from a prior dev-brain session.

If a session ends without writing `unscoped` back to `active-mode.txt`, `state-actors.json._mode` stays `"dev-brain"`. The next gielinor session's first edit to `active-mode.txt` triggers a `despawn-braindead` event for an actor that was never spawned this session.

**Effect:** stray "Braindead packs up and leaves" line in COMMS (`:248-252`); harmless on sprite layer (`despawnBraindead` at `index.html:2396` no-ops if `braindeadNode` is null), but the chat log emits a misleading line.

### B5. Hard cliff at the 10-minute recency boundary

**Where:** `emit-event.py:153, 179`.

A spawn that fires at `T - 599s` since last intent uses that intent's actor as parent. At `T - 601s`, falls through to "wisp" (or whatever else). The cliff is binary; no soft decay. Not catastrophic, but explains a class of "why did this spawn attribute to wisp" surprises.

### B6. `attribute_to_subagent` silent fallthrough when binding cannot resolve

**Where:** `emit-event.py:567-573`.

When `agent_id` is present but `byAgentId` lookup misses *and* `pendingAgentBind` is empty (the failure mode B1 produces), the function returns `(None, None, None)` with no log. Caller (`handle_write_or_read`, `handle_bash`) attributes to main actor. The visualizer then shows the sub-agent's work under the main actor's sprite.

**Effect:** silent failure mode; would be invisible without instrumentation. Worth a `print(..., file=sys.stderr)` at the failure path so live-mode operators have a breadcrumb.

### B7. Despawn-on-crash leak — no recovery path

**Where:** `emit-event.py:464-501` (Pre) and `:504-545` (Post).

If a Task PreToolUse fires but PostToolUse never does (Claude Code crash, network error, parent kill), `byToolUseId` and `pendingAgentBind` accumulate. State files grow monotonically; live-mode dwarf/gnome sprites stay on screen indefinitely. No timeout, no GC, no startup-cleanup pass.

### B8. Non-atomic state-file writes

**Where:** `emit-event.py:87-91` (`save_json`), `:94-97` (`append`).

`Path.write_text(...)` overwrites in place. A crash mid-write truncates the file. `load_json` recovers via default fallback, but the persisted state is **lost**, not just unreachable. On Windows, partial writes can survive past the crashing process; POSIX append atomicity (<PIPE_BUF) doesn't apply on Windows either.

**Worst case:** mid-session crash zeroes `state-dwarves.json` → next post can't find the spawn → despawn is dropped → sprite leaks (overlaps with B7).

### B9. Event-loop interleave between `state-actors.json` and `state.ndjson`

**Where:** `emit-event.py:422-429` (write to `state-actors.json` then append to `state.ndjson`).

Two concurrent hook invocations (parallel tool calls in one batch — e.g., two Bash commands in one response) can race:
1. Hook A reads `state-actors.json`, computes new mapping.
2. Hook B reads same snapshot, computes a different mapping.
3. Hook A writes; Hook B writes (overwriting A).
4. Both append `move` events to `state.ndjson` — both events land, but persisted state reflects only B.

**Effect:** the renderer sees both moves and animates them; `state-actors.json` desynchronizes from the stream's reality. Self-heals on the next move for that actor.

### B10. `setIntent` drops the bubble silently when actor has no position

**Where:** `index.html:2497` (`if (!actorPositions[actor]) return;`).

`ensureActorExists` (called at `:2709`) only handles `braindead` and `wisp`; jebrim/zezima are seeded at module load (`:2162-2163`). But any *future* actor whose first event is `intent` (no preceding spawn or move) silently has the bubble dropped. With the current roster this is dormant; with a third player added, this latent.

### B11. `currentBuilding` not cleared for non-baked actors in `resetWorld`

**Where:** `index.html:2749-2787`.

`resetWorld` deletes from `dwarfNodes`, `gnomeNodes`, `actorPositions` for dynamic actors, and sets `currentBuilding['jebrim'/'zezima']` (`:2776-2777`), but leaves `currentBuilding[<dwarfId>]`, `currentBuilding[<gnomeId>]`, `currentBuilding['wisp']` un-cleared. A scrub-back retains stale building tracking for actors no longer present.

**Effect:** mostly cosmetic in current code paths; could surface if any code reads `currentBuilding` for despawned actors (it doesn't today, but adding such a read would inherit the staleness).

### B12. `currentEventWallTime` survives `resetWorld`

**Where:** `index.html:2643` (declaration) vs `:2749-2787` (resetWorld).

After scrub-back, `currentEventWallTime` retains the last-seen value until the next event with `wallTime` runs through `applyEvent`. The replay timeline (`formatTime(t)` vs `formatWall(...)`) checks `LIVE && currentEventWallTime` so this only affects live mode, where reset isn't usually triggered. Cosmetic.

### B13. `deriveSpeaker` bounded to D[1-3] / G[1-3] — drift from `speakerFor`

**Where:** `index.html:2625-2632` vs `:2617-2623`.

`deriveSpeaker`'s regex caps at 3:
```js
if (/\bD[1-3]\b|dwarves?|\bspawning D/i.test(msg)) return 'dwarves';
if (/\bG[1-3]\b|gnomes?|\bspawning G/i.test(msg)) return 'gnomes';
```

`speakerFor` is unbounded (`/^D\d+$/i`, `/^G\d+$/i`). When the agent counter rolls past 3 (already at `nextId: 8` in `state-dwarves.json:1`), a fourth+ dwarf's free-text message won't be recognized as dwarf-speech by `deriveSpeaker`. Falls through to `activePlayer` or "system".

**Effect:** D4+ / G4+ chat lines miscoloured in COMMS. Tab filter still works (driven by `data-speaker` attribute, which is set elsewhere).

### B14. Race between `state-actors.json` `_mode` save and event append

**Where:** `emit-event.py:224-252`.

```python
actors["_mode"] = new_mode
save_json(ACTORS_PATH, actors)
wall = now_iso()
# Transitioned INTO dev-brain ...
if new_mode == DEV_BRAIN_MODE and prev_mode != DEV_BRAIN_MODE:
    append({... "type": "spawn-braindead" ...})
```

If `save_json` succeeds but `append` fails (disk full mid-append; though both write to the same dir so unlikely-in-tandem), the persisted `_mode` says "dev-brain" with no corresponding spawn event in the stream. Next session-start won't re-emit spawn (`_mode == new_mode` short-circuit at `:222`).

**Effect:** Braindead never appears in the visualizer for the rest of the session. Edge case but not impossible.

### B15. Read events emit `move` with no `action` — sprite oscillation without breadcrumb

**Where:** `emit-event.py:55-58, 388-391` and `index.html:2675-2706`.

Reads emit a `move` event but no `action`. The sprite walks into the building; nothing appears in chat to explain why. If an agent does many quick reads across buildings (e.g., this very audit pass), the sprite ping-pongs with chat only carrying the "walks to X" narration. Working-as-designed per D-014 ("read events too noisy"), but worth surfacing as a UX item — *some* trace would help debug "why did the sprite move there?"

---

## B. Consistency (cross-file invariants that drift)

### C1. Color taxonomy unrationalized across CSS vars / chat / tabs / legend

**Where:** `index.html:11-71` (CSS vars), `:347-352` (chat user colors), `:423-429` (tab dots), `:440-446` (speaker bullets), `:827-831` (legend).

Each actor has *at least three different shades* across UI surfaces:

| Actor | Sprite (CSS var) | Chat user color | Tab dot | Legend swatch |
|---|---|---|---|---|
| Jebrim | `--jebrim-robe` `#2e4d75` | `#1f4b8a` (hard) | `#9bc4ff` | `var(--jebrim-robe)` |
| Zezima | `--zezima-robe` `#a85a2a` | `#a44a14` (hard) | `#ffb56b` | `var(--zezima-robe)` |
| Dwarves | `dwarf-1/2/3` (per-instance) | `#8a5a10` (hard) | `#ffd24a` | `#cf9a2c` (hard) |
| Gnomes | `--gnome-1/2/3` | `#5b3d6e` (hard) | `#c8a8e0` | `#8b6caf` (hard, matches `--gnome-2`) |
| Wisp | `--wisp` `#ffe49b` | `#8a7020` (hard) | `#fff4c8` | `var(--wisp-core)` |
| Braindead | `--braindead-robe` `#4c6478` | `#1a6660` (hard) | — | — |

Hardcoded hexes that drift from the CSS-var palette mean changing the canonical color in one place (e.g., bumping Jebrim's robe to a warmer blue) doesn't propagate. Either rationalize on CSS vars or accept the drift; what's there now is neither.

### C2. Braindead missing from COMMS tab, filter, dot, legend

**Where:** `index.html:858-866` (tabs HTML), `:432-438` (filter CSS), `:423-429` (dot CSS), `:827-831` (legend).

Tabs: `all`, `jebrim`, `zezima`, `dwarves`, `gnomes`, `wisp`, `commits`. No `braindead` tab. CSS filter rules don't have `data-filter="braindead"`. Dot color rule absent. Legend skips braindead.

Braindead has `data-speaker="braindead"` styling for chat lines (`:351, 444`) — i.e., is a first-class speaker — but isn't surfaced in the COMMS UI. Either by-design (dev-brain mode is an internal concern) or a gap.

### C3. `deriveSpeaker` regex bound mismatch with `speakerFor`

(See B13.)

### C4. Action-verb taxonomy collapsed into one CSS class

**Where:** `emit-event.py:290-308` (verbs: editing/writing/running/globbing/searching), `index.html:2716-2721` (always class `'action'`), `:354-356` (CSS).

All five action verbs share `.log-entry.action` color (`#0a0604`). The CSS `.log-entry.write` class (`:356`) is dead code — no codepath emits class `write` for action events. Either prune `.log-entry.write` or split the action class taxonomy (e.g., `action-edit`, `action-bash`) if the goal is per-verb tinting.

### C5. `path-map.json` building list ↔ SVG `BUILDINGS` ↔ `STAND` ↔ `BUILDING_DESC` ↔ `LABEL_Y_OFFSET`

**Where:** `path-map.json:4-15`, `index.html:886-897`, `:900-911`, `:1948-1959`, `:1924-1935`.

All five surfaces enumerate the same 10 buildings. ✓ No drift.

### C6. `state-gnomes.json` not yet on disk — expected, not a finding

`emit-event.py:28` declares the path; the file is created lazily on first gnome spawn via `save_json`. Today the path is unrealized; that's correct.

### C7. The dev-brain override applies only to default-actor case in `handle_write_or_read`

**Where:** `emit-event.py:420-421`.

```python
if actor == m.get("defaultActor", "wisp") and read_active_mode() == DEV_BRAIN_MODE:
    actor = "braindead"
```

The override fires only when path classification falls through to `defaultActor` (no explicit actor rule matched). If Braindead modifies a path that *does* match an actor rule (e.g., editing a Jebrim bank file from dev-brain mode), the work is attributed to Jebrim. Documented in `path-map.json:55` as intended ("the hook layers session-mode on top of these rules"), but the UX is confusing — a gielinor player who isn't even logged in spawns on the map.

This is a design choice rather than a bug; flagging because the first principal-cued dev-brain-modifies-Jebrim moment will surface it.

---

## C. Improvements (deferred work, latent backlog)

### I1. Rationalize color taxonomy on CSS vars (per C1)
Single source-of-truth color per actor; all UI surfaces derive from it.

### I2. Promote Braindead to COMMS first-class (per C2)
Add tab + filter + dot + legend row, parallel to Jebrim/Zezima.

### I3. Tighten `deriveSpeaker` regex (per B13/C3)
`\bD[1-3]\b` → `\bD\d+\b`; same for G.

### I4. Atomic state-file writes (per B8)
Temp-file + rename for `save_json`; consider POSIX-style `with locking` for `state.ndjson` appends (Windows file-lock semantics differ).

### I5. Despawn-on-crash recovery (per B7)
Either: hook-side startup pass that walks role-state files and emits despawn events for stale entries; renderer-side timeout that auto-clears a sub-agent sprite after N idle minutes.

### I6. Fix recency-walk parse-failure handling (per B2)
`continue` on `wt is None`; `break` only on `(now - wt).total_seconds() > RECENCY_SEC`.

### I7. Dev-brain override in `infer_dwarf_parent` (per B3)
Mirror `current_main_actor`'s short-circuit.

### I8. Surface attribution-failure trail (per B6)
`print(..., file=sys.stderr)` when `attribute_to_subagent` returns `(None, None, None)` despite having an `agent_id`.

### I9. Idle indicator (D-009 deferred)
Fade active actor's glow after N seconds of no events in live mode.

### I10. Watchdog for non-Claude writes (D-009 deferred)
Periodic disk scan to detect writes that bypassed the hook (IDE-direct edits, OS-level moves).

### I11. SSE upgrade (D-009 deferred)
Replace 500ms polling with server-sent events when justified.

### I12. Action target prettification (D-014 follow-up)
Bash commands show raw command text. Could pattern-match common verbs (mv, cp, git, python -m http.server) and prettify.

### I13. Chat scroll-lock UX (D-014 follow-up)
`logEl.scrollTop = logEl.scrollHeight` at `index.html:2591, 2605` defeats the user's read-history intent. Only auto-scroll when already at bottom.

### I14. Bubble two-line edge cases (D-014 follow-up)
`wrapBubbleText` (`:2515`) hard-slices single long tokens at 50 chars (`:2520`); multi-word edge cases unverified for cases like single-word over the limit followed by short trailing.

### I15. Per-building character (S009 aesthetic backlog)
Ambient particles per building (lanterns at Inn, gem-shine at Vault, papers fluttering at Inbox Square).

### I16. Gnome workshop building (D-016 deferred)
Revisit after a few live gnome spawns. If the gnome lacks a "home," consider adding.

### I17. Tighten gnome-write-boundary allowlist
Per respawn iteration menu: `/spellbook/drafts/` → `/spellbook/drafts/skills/`. Out-of-scope for *this* audit (lives in `gielinor/.claude/hooks/`), flagged for traceability.

### I18. Narration shakedown
End-to-end test: write to `.claude/narration.txt` at multiple session-boundary moments, verify each renders correctly and at the right position. Used briefly at S019/S020 open; not stress-tested.

---

## D. Documentation surface

### D1. README stale (`_README.md:29-34`)
"Steps still pending (per D-009)" lists Steps 3-6; Steps 4-6 have all shipped (read/glob/grep hooks, Task spawn pipeline, bootstrap-from-tail). README pre-dates D-014 (chat panel), S012 (Braindead), D-016 (gnomes), the narration channel, the active-mode marker, and the entire sub-agent attribution model.

### D2. No reference for event schema
`state.ndjson` carries ~14 event types: `session-start`, `log`, `move`, `intent`, `action`, `narrate`, `spawn-dwarf` / `despawn-dwarf`, `spawn-gnome` / `despawn-gnome`, `spawn-wisp` / `despawn-wisp`, `spawn-braindead` / `despawn-braindead`, `commit`. The shape of each is implicit in `applyEvent` (`index.html:2657-2747`) and the emit functions. Worth one short reference doc for the maintainer who arrives without context.

### D3. No reference for `path-map.json` precedence rules
Inline `_notes` (`path-map.json:50-56`) cover building-rule ordering and the dev-brain override, but not the actor-rule vs default-actor interaction or how the trailing-slash trick (`emit-event.py:106-107`) lets directory-shaped needles match.

### D4. `ROLE_CONFIG` shape undocumented
`emit-event.py:33-52` is the canonical structure; if a future role joins (rangers, gnomes-but-bigger, etc.), the maintainer learns by reading code. Worth a docstring above the constant explaining the key contract.

---

## Triage suggestions (for the principal)

**Most likely to bite next:** B1 (FIFO misattribution) — first time two sub-agents launch close in time, this surfaces. The current usage pattern is mostly sequential, but parallel dwarf spawns are explicitly endorsed in `meta/communication-protocol.md`.

**Most easily fixed:** B2 (parse-failure vs window-past) is a two-line change. B13 (deriveSpeaker bound) is regex tweak. C2 (Braindead COMMS gap) is mostly mechanical CSS/HTML.

**Most architectural:** B7 + B8 + I4 + I5 together — the state files lack atomicity and crash recovery. If gnome/dwarf usage scales up, this layer needs attention. The fix is well-known (temp-file + rename, startup GC pass) but adds complexity.

**Validation event:** The S020 cascade hasn't yet had a live gnome spawn. That run will exercise B1's preconditions (if two gnomes spawn close together), B3's dev-brain override gap (if the spawn happens before the first intent write), and the gnome render path end-to-end. Recommend pairing this audit with the deferred Step 2 — running the audit-and-validation together exposes more than either alone.

**Documentation debt:** D1 is the highest-leverage doc fix. The README is the entry point for a future maintainer; today it tells them about the world as it existed at S010-ish.

---

## Files referenced

- `developer-braindead/.claude/hooks/emit-event.py` (lines: 28, 33-52, 55-58, 87-97, 100-118, 146-198, 211-253, 256-278, 290-308, 311-320, 372-437, 440-453, 456-461, 464-501, 504-545, 548-577, 580-630)
- `developer-braindead/experiments/visualizer/index.html` (lines: 11-71, 347-352, 354-362, 423-446, 432-438, 827-831, 858-866, 886-897, 900-911, 1924-1935, 1948-1959, 2127-2163, 2497, 2515, 2611-2632, 2657-2747, 2749-2787)
- `developer-braindead/experiments/visualizer/path-map.json` (lines: 4-15, 17-40, 42-46, 47, 50-56)
- `developer-braindead/experiments/visualizer/_README.md` (lines: 29-34)
- `developer-braindead/experiments/visualizer/state-actors.json`
- `developer-braindead/experiments/visualizer/state-dwarves.json`

# D-019 — 2026-05-22 — Parallel Braindead instances + dev-to-dev comms channel

**Context.** [[D-017]] introduced parallel player instances (per-session sprites with tint differentiation, instance-1 reserved for the first session, despawn on 5-min idle). It explicitly deferred Braindead: *"Wisp and Braindead are conceptually single-actor (system voice / construction crew). Treating them as instance-1 only is fine for now; revisit if two dev-brain sessions ever run in parallel."*

That moment arrived. Niklavs wants to run multiple dev-brain sessions in parallel — different construction tasks (one on the visualizer, one on hook docs, one on a meta-rewrite) progressing independently. Two missing pieces:

1. **Visualization.** Today every dev-brain session writes events as `actor=braindead`, routing to a single sprite. Bubbles overwrite, COMMS interleaves without disambiguation, the workshop sprite can't represent two construction crews in flight.
2. **Coordination.** More important than the visual half: two Braindeads editing `gielinor/meta/modes.md` in the same window produce merge pain that no tint variant prevents. The collision surface is `gielinor/` writes — the dev brain itself has enough natural namespacing (per-session quest-log files) to be mostly safe, but main-brain writes are not.

The light-coordination posture D-017 takes for parallel Jebrims (principal disambiguates by eyeballing the visualizer) is insufficient for Braindead because Braindead's collision surface includes shared files in `gielinor/` that Jebrim doesn't touch.

**Decision.** Two coordinated changes ship together:

### 1. Extend D-017 instance routing to Braindead

Mechanical parallel to player-class instances:

- **Hook.** Introduce `INSTANCED_ACTORS = PLAYER_ACTORS | {"braindead"}` as the gate for `resolve_instance` and the `append()` instance-stamp. `wisp` and `guthix` stay excluded — wisp is system voice (only one), guthix is bankstanding-deity (always solo). Dwarves and gnomes remain unaffected (they're already uniquely numbered).
- **Visualizer.** `ensureActorExists('braindead', ...)` calls `spawnPlayerInstance('braindead', n, at)` for `n > 1`. The existing `spawnBraindead` covers instance 1 (the canonical workshop sprite). Tint variants reuse the existing `.parallel-instance.tint-2/3/4` CSS — Braindead's robe hue-shifts the same way Jebrim's does. Instance badge above head reads `2`, `3`, etc.
- **Despawn.** Same 5-min idle timer + SessionEnd hook coverage; identical to player despawn.
- **Naming.** Label `Braindead·2`. Instance-1 keeps the short label `Braindead`. COMMS prefix gains the dot-number when `instance > 1`.
- **Collision.** Two Braindeads at the workshop stack on `STAND['braindead-workshop']`. Use the existing per-instance jitter offset (D-017 §"Out of scope for the first cut"). Gather-slot scaffolding from S028 already handles bubble layout.

### 2. New dev-to-dev comms channel: `developer-braindead/comms/active.md`

A shared append-only file. Every Braindead session reads it at respawn and writes to it during the session. Two entry kinds:

- **Declaration entry.** Posted at respawn, after sibling detection. Names targets and what the session is steering clear of.
- **Dialogue entry.** Posted ad-hoc when one Braindead needs to ping a sibling — handoff request, conflict warning, "I'm done with X, you can pick it up." Uses `@braindead-<sid8>` for addressing.

Closing entries land at session-close before the commit.

#### File shape

```markdown
# active.md — dev-to-dev comms

> Append-only log. Each Braindead session reads at respawn, posts a declaration,
> dialogues as needed, posts a closing entry at session-close.
> See _about.md for the protocol.

---

[2026-05-22 14:32] braindead-5de1e12a OPEN
  Targets: experiments/visualizer/index.html — scale-up pass (respawn Step 1).
  Steering clear of: developer-braindead/.claude/hooks/, gielinor/meta/.
  Open to handoff: replay-demo arcs (Step 4), drafts triage (Step 6).

[2026-05-22 14:48] braindead-9c1f2a4b OPEN
  Targets: gielinor/meta/communication-protocol.md — intent-vs-action discipline rewrite.
  Steering clear of: experiments/, hooks/.
  Open to handoff: none yet.

[2026-05-22 15:03] braindead-9c1f2a4b → @braindead-5de1e12a
  Heads up — I'll need a small read of experiments/visualizer/index.html for
  context (no writes). Will not edit. OK?

[2026-05-22 15:04] braindead-5de1e12a → @braindead-9c1f2a4b
  Reads are fine. I'll @ you if I touch the meta tree.

[2026-05-22 15:47] braindead-5de1e12a CLOSING
  Completed: visualizer scale-up shipped (S029).
  Leaving open: Step 4 demos still untouched; comms channel itself untested under three-way parallel.
```

#### Entry format (parseable, human-readable)

Each entry is bounded by a blank line above. First line is the header:

```
[YYYY-MM-DD HH:MM] <braindead-id> <KIND>
```

Where `KIND` is one of:
- `OPEN` — declaration entry at respawn
- `→ @<target-id>` — dialogue addressed to a sibling
- `UPDATE` — declaration update mid-session (targets shifted)
- `CLOSING` — final entry at session-close

Body is free-form markdown, indented 2 spaces. Multi-line bodies are fine.

#### Detection mechanic (respawn-side)

Before posting the OPEN entry, a fresh Braindead:

1. Lists `brain/.claude/intent/braindead-*.txt` files with `mtime` within 5 minutes (matches D-017 despawn threshold). These are the live siblings.
2. Reads `developer-braindead/comms/active.md`. Last 20 entries are scanned for any session id appearing in step 1 but missing a `CLOSING` entry — that's a confirmed-live sibling.
3. Surfaces the result to the principal: *"Detected one live sibling: braindead-9c1f2a4b, working on gielinor/meta/communication-protocol.md. Open targets I'd grab next are …"* — and waits for direction before committing to a task.
4. Posts the OPEN entry once direction is given.

#### Read cadence (in-session)

- At respawn (mandatory).
- Before editing any file under `gielinor/` (the collision surface — main-brain writes are where parallel work goes wrong).
- When stuck or context-starved — sibling may have relevant in-flight reasoning.

Polling every turn is overkill. Three trigger points cover the actual risks.

#### Append discipline (concurrent-write safety)

Append-only newline-separated entries make concurrent writes survivable: Python's `open(..., 'a')` is atomic for small writes at the OS level on the platforms we care about (Windows + POSIX). Worst case: two entries interleave at the line level but no data is lost. The file is not a database; the protocol tolerates occasional minor garbling.

If garbling becomes routine, revisit with a file lock — but defer.

### Out of scope for the first cut

- **Comms entries from non-Braindead actors.** Players (Jebrim, Zezima) and Guthix have their own coordination patterns. The channel is dev-to-dev only.
- **Garbage collection.** The file grows unbounded. Manual rotation when it gets unwieldy. Could automate via a `comms/archive/active-YYYY-MM-DD.md` rotation later.
- **Visualizer surface for comms.** The channel is text-only; bubbles don't render its content. If dialogue becomes load-bearing, consider surfacing recent entries in COMMS tab. Defer until used.
- **Cross-brain coordination.** Jebrim and a Braindead session running in parallel don't collide on disk (different layers) but might collide on intent ("Niklavs has me here and Jebrim there — am I expected to read Jebrim's quest-log?"). The current architecture has no answer; leave for a future decision.

## What "shipped" looks like

- `developer-braindead/bank/decisions/D-019_*.md` (this file).
- `developer-braindead/comms/active.md` + `developer-braindead/comms/_about.md` scaffolded.
- `developer-braindead/spellbook/respawn-ritual.md` — sibling-detection + comms-read + OPEN-entry steps added.
- `developer-braindead/spellbook/session-close.md` — CLOSING-entry step added before commit.
- `developer-braindead/.claude/hooks/emit-event.py` — `INSTANCED_ACTORS` introduced; `resolve_instance` + `append` gate updated; verify suffix-strip and disk-fallback still work for braindead-N.
- `developer-braindead/experiments/visualizer/index.html` — `ensureActorExists('braindead', ...)` dispatches to `spawnPlayerInstance` for n>1; tint reuses parallel-instance CSS.
- `developer-braindead/quest-log/in-progress/S029_*.md` documents the build.

## Open questions

- **Stale-sibling detection.** What if a sibling's intent file is fresh (mtime < 5min) but the session has actually died and just hasn't tripped SessionEnd? The principal will see the false-positive at respawn and can override. Acceptable.
- **Multi-instance respawn collision.** Two Braindeads starting within seconds of each other could both see "no siblings" before either has posted its OPEN. First cut: tolerate — the principal sees two fresh OPENs in the file and can broker. If routine, add a brief lockfile during respawn-step-3.
- **Closing-entry skip.** A Braindead that crashes (SIGKILL, terminal closed) leaves no CLOSING. The next respawn sees the OPEN with no CLOSING and an intent-file mtime older than 5min — treat as `ABANDONED` automatically. Note in comms read.

## Related

- [[D-017]] — parent decision; this extends its scaffolding to Braindead and adds the comms layer it didn't include.
- [[D-018]] — parallel-session substrate isolation; the disk-fallback work that made per-session intent files load-bearing for Braindead.
- [[S028]] — shipped the suffix-strip fix that made `braindead-<sid8>.txt` route correctly; that fix is the substrate D-019 builds on.
- `gielinor/meta/modes.md` — no change. Instance is a hook/visualizer concern, not a cognitive-mode concern. Braindead is still one actor with one voice; instances are a parallelism mechanic.

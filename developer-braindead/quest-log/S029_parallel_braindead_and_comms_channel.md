# S029 — 2026-05-22 — Parallel Braindead instances + dev-to-dev comms channel

Multiple dev-brain sessions are now a supported pattern. Closed the [[D-017]] follow-up that explicitly deferred Braindead instance routing, and shipped a coordination channel so parallel construction crews can declare targets and dialogue before stepping on each other's work. Driven by the principal's observation that the dev brain has reached a state where building multiple things in parallel — a visualizer pass and a meta rewrite, for example — is the natural next mode of operation. The Jebrim multiplication scaffolding from D-017 became the substrate.

## What shipped

- **[[D-019]]** — full design captured: extending `INSTANCED_ACTORS` to braindead, dialogue-shaped comms channel at `developer-braindead/comms/active.md`, entry kinds (`OPEN`, `→ @target`, `UPDATE`, `CLOSING`, `ABANDONED`-synthesized-at-respawn), sibling-detection mechanic via intent-file mtime + active.md cross-reference, read cadence (respawn / before gielinor/ edits / when stuck), append-only concurrent-write safety, open questions (stale-sibling false positives, multi-instance respawn race, closing-entry skip on crash).

- **Comms channel scaffolded.** `developer-braindead/comms/_about.md` codifies the entry-kind table, read cadence, write discipline (append-only, blank-line-bounded entries, plain markdown), rotation guidance (manual to `comms/archive/` at ~500 entries), and the boundary against content that belongs elsewhere. `comms/active.md` opened with a SCAFFOLD seed entry; first live `OPEN` lands at the next dev-brain respawn under the new ritual.

- **Respawn ritual extended.** `developer-braindead/spellbook/respawn-ritual.md` step 6 detects live Braindead siblings (intent-file mtime < 5min, cross-referenced against `comms/active.md` OPEN entries lacking CLOSING). Step 7 requires the session plan to account for any detected siblings before the principal's nod. Step 8 posts the `OPEN` entry to the comms channel — post-nod, never pre-emptive. Notes section adds the discipline rule: surface detection but don't pre-empt the principal's judgment on whether the sibling is actually alive, and never post an `OPEN` for a rejected target.

- **Close-session ritual extended.** `developer-braindead/spellbook/session-close.md` step 6 posts the `CLOSING` entry to comms before the visualizer-marker clear and commit. Renumbered subsequent steps. Edge cases handled inline: read-only sessions without an `OPEN` skip the CLOSING; mismatched-but-still-running sessions get a CLOSING regardless.

- **Hook wired.** `developer-braindead/.claude/hooks/emit-event.py` introduced `INSTANCED_ACTORS = PLAYER_ACTORS | {"braindead"}` (line 44). Four gates flipped from `PLAYER_ACTORS` to `INSTANCED_ACTORS`: `set_actor_building` (line 205, per-session building tracking), `resolve_instance` (line 228, instance-number assignment), `append` instance-stamp (line 255, every braindead event gets its instance), and `handle_session_end` despawn-instance loop (line 947, sessions emit cleanup events on graceful exit). Suffix-strip + disk-fallback paths already covered braindead via `NON_PLAYER_SUFFIX_ACTORS` from S028 — no change needed. Syntax-checked clean.

- **Visualizer wired.** `developer-braindead/experiments/visualizer/index.html` extended `ensureActorExists` to route `actor === 'braindead' && instance > 1` to `spawnPlayerInstance` with `braindead-workshop` as the actor-aware fallback building. `spawnPlayerInstance` learned the same actor-aware default. Existing `actorDisplayName` (renders `Braindead·2` via `parseInstanceKey`) and `speakerFor` (routes braindead to BRAINDEAD tab regardless of instance) already handled the disambiguation downstream; the `despawn-instance` event case (line 3443) already correctly skipped instance 1 and faded out 2+ via `despawnPlayerInstance`.

- **Quest log convention noticed.** Dev-brain quest-log is flat (no `in-progress/` / `completed/` split) — this file is named at session close per the existing ritual rather than scaffolded mid-session. The mid-build task was deferred to this step; reframed at close-time.

## Why this shipped now

D-017 explicitly left a hook for Braindead: *"Treating them as instance-1 only is fine for now; revisit if two dev-brain sessions ever run in parallel."* The revisit moment arrived with the principal's framing — *"we are in a weird place, I want to be able for you to build multiple things in parallel in separate sessions."* The mechanical half (visualizer + hook) was a tight extension of D-017; the conceptual half (a coordination channel beyond passive sprite differentiation) was the addition. The dialogue posture (vs. declarations-only) was chosen because the collision surface — `gielinor/` writes — has real merge-pain risk that passive declarations don't resolve when two crews are touching adjacent surfaces.

S028's per-session intent-file mandate + suffix-strip fix were load-bearing prerequisites: without them, parallel braindead sessions couldn't have distinguishable intent files, and the sibling-detection mechanic would have had nothing reliable to scan.

## Observations to carry

- **D-017's deferred branches age fast.** Two and a half weeks after D-017 shipped, the deferred Braindead branch closed under principal pressure. Worth pattern-noting: D-NNN documents with "out of scope for first cut" sections accumulate latent work that becomes load-bearing on a slower clock than the section originally projected. Bankstanding could surface these via a "deferred branches > 30 days" check.

- **Coordination is asymmetric across actor classes.** Parallel Jebrims (per D-017) need no comms channel — Jebrim's collision surface is per-player layers, naturally namespaced. Parallel Braindeads need one because Braindead writes to `gielinor/` shared surfaces. The instance scaffolding is uniform; the coordination layer is not. Implication: each new instanced actor needs a separate decision about coordination.

- **Append-only files dodge concurrent-write design entirely.** The comms channel is two parallel writers (sometimes more) with no lock and no controller. Append-only + newline-bounded + atomic-at-OS-level-for-small-writes gets us to "good enough" without ceremony. The principle is wider than this one file.

- **"Seems ambitious" is a green light, not a hedge.** Read it as scope acknowledgment, ship the bigger variant. The smaller variant always still ships when the principal directs explicitly.

## Cascade

Dev-brain files landed:
- `bank/decisions/D-019_parallel_braindead_and_comms_channel.md` (new).
- `comms/_about.md`, `comms/active.md` (new layer).
- `spellbook/respawn-ritual.md` (sibling detection + OPEN step).
- `spellbook/session-close.md` (CLOSING step).
- `.claude/hooks/emit-event.py` (`INSTANCED_ACTORS`).
- `experiments/visualizer/index.html` (`ensureActorExists` + `spawnPlayerInstance` braindead routing).
- `quest-log/S029_*.md` (this file).
- `respawn.md` (overwritten at close).

## Main-brain changes

none.

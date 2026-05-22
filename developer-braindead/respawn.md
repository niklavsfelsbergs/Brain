# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-22 (end of [[S029]] — parallel Braindead instances + dev-to-dev comms channel).

## Where we are

[[S029]] closed the [[D-017]] deferred-Braindead branch and added a coordination layer so parallel dev sessions can declare targets and dialogue. Two coordinated shifts shipped end-to-end:

**1. Parallel Braindead instances.** D-017's machinery (per-session sprites, tint variants, instance numbering, 5-min idle-despawn) now extends to Braindead. Mechanical surface area:

- **Hook.** `INSTANCED_ACTORS = PLAYER_ACTORS | {"braindead"}` added. Four gates flipped from `PLAYER_ACTORS` to `INSTANCED_ACTORS`: `resolve_instance`, `append` instance-stamp, `set_actor_building`, `handle_session_end` despawn loop. Suffix-strip + disk-fallback already covered braindead via `NON_PLAYER_SUFFIX_ACTORS` from [[S028]] — untouched.
- **Visualizer.** `ensureActorExists` now routes `actor === 'braindead' && instance > 1` to `spawnPlayerInstance` with `braindead-workshop` as the actor-aware fallback building. `spawnPlayerInstance` learned the same default. `actorDisplayName` / `speakerFor` / `despawn-instance` case already handled the disambiguation downstream; no further wiring needed.
- **Visuals.** Braindead·2 will render as `<use href="#braindead">` inside a parallel-instance group with `.tint-2` hue-rotate filter, sharing the workshop STAND via the gather-slot scaffolding from S028. Instance badge "·2" above the head.

**2. Dev-to-dev comms channel.** [[D-019]] captured the design; `developer-braindead/comms/` is the new layer.

- **Entry kinds.** `OPEN` (declaration at respawn after sibling detection), `→ @target` (dialogue), `UPDATE` (target shift mid-session), `CLOSING` (session-close), `ABANDONED` (synthesized by next respawn when prior OPEN has no CLOSING and intent file is stale).
- **Sibling detection.** Respawn scans `.claude/intent/braindead-*.txt` for mtime < 5min, cross-references against the last ~20 `active.md` entries for OPENs lacking CLOSINGs. Surfaces detection to the principal; never pre-empts judgment about whether a sibling is alive.
- **Read cadence.** Mandatory at respawn; before any `gielinor/` edit (the collision surface); when stuck.
- **Append-only.** Atomic-at-line-level for small writes on Windows + POSIX. Tolerates minor interleaving; no lock needed unless garbling becomes routine.

**3. Ritual updates.**

- `spellbook/respawn-ritual.md` step 6 detects siblings; step 7 requires plan to account for them; step 8 posts the `OPEN` after the principal's nod.
- `spellbook/session-close.md` step 6 (new) posts the `CLOSING` before the visualizer-marker clear and commit.

## Next concrete step — START HERE

**Step 1 — Live test parallel Braindead.** The whole shipped surface is untested under two-Braindead conditions. Open a second Claude Code window at this repo, cue *"Lets develop gielinor"*, and watch:

- Sibling detection at respawn — should surface the existing braindead-5de1e12a session (or whichever is live) before plan formation.
- The new Braindead's `OPEN` entry lands in `comms/active.md` after the plan-nod.
- Visualizer spawns `Braindead·2` at the workshop with tint-2 hue-rotate. Instance badge "·2" above head.
- Both sessions write intent files; visualizer routes each to the correct sprite. COMMS panel shows `Braindead·2:` prefixes for the second session's chat lines.
- Editing a `gielinor/` file from either session triggers a re-read of `comms/active.md` (manual-discipline check, not enforced).
- When one session closes, the `CLOSING` entry lands; the other Braindead can see it on next read.
- Idle-despawn (5 min) fades out the abandoned instance if a session crashes.

Tune if needed: tint-2 hue-rotate angle (braindead robe's `--braindead-robe` blue might land in an awkward zone after 140° rotation; pick a different tint slot if so), instance-badge position relative to the bobbing sprite, gather-slot offset at the workshop when two crews stand there.

**Step 2 — Scale up the whole map** (carried from S028). Same brief: more room for the now-routine cluster of background dwarves + parents + bubbles. Touches `experiments/visualizer/index.html` only (TILE_W/H proportional bump, building footprints, STAND positions, viewport crop, gather-slot offsets).

**Step 3 — Live test Guthix end-to-end** (carried from S028). Replay-mode demos worked; live-mode demo of `Hey Guthix` + `let's bankstand` still pending.

**Step 4 — Subtask debounce decision** (carried from S028). After more observation, decide whether to ship slice 4. Default to no debounce if bubble stays alive without strobing.

**Step 5 — Replay-mode demo arcs** (carried from S028). Subtask + Guthix demos in EVENTS array. Now also: parallel-Braindead demo (two Braindeads at the workshop with comms-channel dialogue).

**Step 6 — Recover Jebrim session 58f8e88a** (carried from S028). Probably resolves itself on next respawn of that session.

**Step 7 — Drafts triage** (long-carried S018 → S027):

- `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md` — promote to `lorebook/decisions/D-NNN_*.md`.
- `gielinor/players/jebrim/keepsake/proposals/2026-05-21_eu-tender-2026.md`.
- `gielinor/players/jebrim/spellbook/drafts/skills/moving-target-decomposition.md` (Jebrim alching).
- `gielinor/players/jebrim/niksis8_character/drafts/` (S017-era + 2026-05-21-prefers-evidence-over-premature-infrastructure).

**Step 8 — Audit follow-up notes** (carried S027):

- `bank/decisions/`: *recon dwarves should cross-check audit findings against intervening commits before bundling.*
- B1 day/night cadence — 87s/day may be too fast.
- B9 hook D-018 read race — separate session at the hook level.

**Step 9 — First live gnome spawn** (carried S020+).

**Step 10 — Q-008 visualizer aliveness pick** (carried). S028 subtask + S029 parallel-instances subsume some of this; remaining urgency lower.

## Open at the start of next session

- **Live test parallel Braindead** — Step 1. First action.
- **Scale up the map** — Step 2.
- **Live test Guthix** — Step 3.
- **Subtask debounce decision** — Step 4.
- **Replay demos** — Step 5 (now includes parallel-Braindead).
- **Jebrim 58f8e88a recovery** — Step 6.
- **Drafts triage backlog** — Step 7.
- **Audit follow-up notes** — Step 8.
- **First live gnome spawn** — Step 9.
- **Q-008 pick** — Step 10.
- §C Pilot definition, §H.3 brain-zone taxonomy, §H.4 identity ↔ main-brain interaction — unchanged.

## Carried-over observations

From [[S029]] (new): **D-017's deferred branches age fast.** Two and a half weeks after D-017 shipped, the deferred Braindead branch closed under principal pressure. Pattern: D-NNN documents with "out of scope for first cut" sections accumulate latent work that becomes load-bearing on a clock the section didn't project. Bankstanding could surface these via a "deferred branches > 30 days" check.

From [[S029]] (new): **coordination is asymmetric across actor classes.** Parallel Jebrims (D-017) need no comms channel — Jebrim's collision surface is per-player layers, naturally namespaced. Parallel Braindeads need one because Braindead writes to `gielinor/` shared surfaces. Implication: each new instanced actor warrants a separate decision about coordination.

From [[S029]] (new): **append-only files dodge concurrent-write design entirely.** The comms channel has two-or-more parallel writers with no lock and no controller. Append-only + newline-bounded + atomic-for-small-writes gets to "good enough" without ceremony. Principle is wider than this one file.

From [[S029]] (new): **"seems ambitious" reads as a green light, not a hedge.** Ship the bigger variant; the smaller still ships under explicit narrower direction.

From [[S028]] (still relevant): **subtask exposes architecture/intuition mismatches that quieter channels papered over.** Worth a `bank/decisions/` note.

From [[S028]] (still relevant): **silent suffix-strip bugs hide until the surface gets busy.** Pattern: *infrastructure bugs are easier to spot once redundant signal is removed.*

From [[S028]] (still relevant): **the "bare intent file" fallback was never load-bearing — only confusing.** Removing the fallback was a strict simplification. Worth a `lorebook/drafts/` entry on *"defaults that exist only for absent inputs accumulate hidden coupling — prefer a hard surface."*

From [[S027]] (still relevant): **recon dwarves should cross-check audit findings against intervening commits before bundling.**

From [[S027]] (still relevant): **a multi-fix audit pass converts the audit doc from a primer into a verification checklist.**

From [[S023]] (still relevant): **shared global state at brain root is hostile to parallel Claude sessions.** S029's `INSTANCED_ACTORS` follows the same gating pattern. Cumulative incident pattern now spans S014, S022, S023, S027, S028, S029.

From [[S023]] (still relevant): **watching-it-run finds bugs the audit-and-validate phase missed.** Step 1's live test will confirm.

From [[S022]] (still relevant): **audit-then-validate finds different bugs than either alone.**

From [[S022]] (still relevant): **shared global state is hostile to parallel Claude sessions.**

From [[S021]] (still relevant): **the audit-then-validate pattern works for accreted infrastructure.**

From [[S021]] (still relevant): **cross-file invariants need an explicit list when ≥3 surfaces enumerate the same set.** S029 extended the suffix-strip prefix set and the instance-routing set in tandem — six surfaces now share the actor-class enumeration.

From [[S020]] (still relevant): **architectural guarantees need a live failure test, not just code review.** Step 1 carries the live-test load for parallel Braindead.

From [[S020]] (still relevant): **the claude-code-guide agent earned its spawn.**

From [[S019]] (still relevant): **a new role's blocklist is easier to get right than its allow-list.**

From [[S019]] (still relevant): **single source of truth for tunable numbers is worth one hop.**

From [[S018]] (still relevant): **the quest log is the gravitational center; other layers starve without explicit routing.**

From [[S018]] (still relevant): **bundle big structural decisions; resist piecemeal landing.** S029 followed this — D-019 landed end-to-end in a single session as a coordinated hook + visualizer + ritual + decision-doc bundle.

From [[S017]] (still relevant): **spec docs that prescribe DOM/structure without inventorying what already exists will ship suboptimal designs.**

From [[S017]] (still relevant): **heuristics that walk back through `state.ndjson` need to remember the stream is cross-session.**

From [[S017]] (still relevant): **emulating a specific UI's look means font and palette must change together.**

From [[S016]]: **"players communicate" in dev-brain mode probably means the visualizer, not the chat preamble.** S029 generalizes this: dev-brain *crews* now communicate explicitly via a file channel, in addition to the visualizer surfacing.

From [[S015]]: **shipping behind "the docs say X" is risky in this codebase because the docs are right but the integration is novel.**

From [[S015]] (separate): **delete discipline isn't enforced for dev-brain infrastructure.**

From [[S014]] (now eleven-incident pattern with S018, S020, S022, S023, S027, S028, S029): **the procedure was right; the procedure assumed a state that didn't exist.**

From [[S014]]: **the renderer needs to be self-healing because the hook stream is a lossy substrate.**

From [[S014]]: **tool renames upstream are silent regressions.**

From [[S013]]: **uncommitted work occupies the ID space.**

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss.**

From [[S009]]: **mental UI preview must include z-order and all collision targets.**

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]]: **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.**

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S029_parallel_braindead_and_comms_channel.md` — what just shipped.
3. `bank/decisions/D-019_parallel_braindead_and_comms_channel.md` — full design including open questions.
4. `comms/_about.md` + `comms/active.md` — the new coordination layer.
5. `spellbook/respawn-ritual.md` + `spellbook/session-close.md` — sibling detection + comms entry steps.
6. `experiments/visualizer/index.html` — `ensureActorExists` + `spawnPlayerInstance` braindead routing (search "D-019").
7. `.claude/hooks/emit-event.py` — `INSTANCED_ACTORS` (line 44) and the four gates that reference it.
8. `bank/decisions/D-017_parallel_player_instances.md` — parent decision; D-019 extends.
9. `bank/decisions/D-018_parallel_session_substrate_isolation.md` — the per-session intent-file mandate that made sibling detection possible.
10. `gielinor/meta/guthix.md` — the bankstanding deity from S028 (still relevant for cross-actor parallel work).
11. `bank/research/visualizer-audit-S026-prep.md` — historical; open questions still pending live verification.
12. `bank/open-questions/Q-008_visualizer_aliveness.md` — parked.
13. `gielinor/.claude/hooks/gnome-write-boundary.py` + `dwarf-write-boundary.py` + `block-sub-spawn.py` — still untested under live sub-agent activity.
14. `gielinor/spellbook/skills/spawning-gnomes.md` — gnome operating spec.
15. `bank/plan.md` — current mission state.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) remains asset-agnostic and untouched during S029. The Braindead instance-routing extension layered on the existing `ensureActorExists` / `spawnPlayerInstance` surface; the engine itself wasn't reshaped. Keep extending; don't rewrite.

New event types in S029: none — all events flow through existing channels (intent stamped with instance, despawn-instance reused, no new event names).

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then `http://localhost:8765/?live=1`. For parallel-Braindead testing, open two Claude Code windows at brain/ root.

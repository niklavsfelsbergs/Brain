# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S020]] — gnomes ratification + visualizer integration).

## Where we are

[[S020]] closed two deliverables in one session: ratification of the [[S019]] gnomes cascade and the deferred visualizer integration. The ratification pass surfaced one load-bearing finding — **all three sub-agent boundary hooks were silently inert**, gated on env vars (`CLAUDE_BRAIN_GNOME=1`, `CLAUDE_BRAIN_DWARF=1`) that Claude Code never propagates into sub-agent tool calls. Fix landed: each hook now parses stdin first and gates on `payload.get("agent_type") == "gnome"` (or `"dwarf"`, or both for the sub-spawn block). The canonical mechanism was confirmed via a claude-code-guide sub-agent: Claude Code populates `agent_id` + `agent_type` in the PreToolUse JSON payload, but env vars are *not* propagated.

This fix incidentally re-armed the pre-existing dwarf write boundary, which had the same gating bug since its founding hook landed. Architectural guarantees #3 (dwarf boundary), #4 (gnome boundary), #5 (no sub-spawn) in `gielinor/CLAUDE.md` are now actually live; before today they were paper-only. #1 (no confirmed writes) and #2 (no deletes) were unaffected.

The visualizer integration shipped end-to-end and mirrors the dwarf pipeline:

- `developer-braindead/.claude/hooks/emit-event.py` — new `ROLE_CONFIG` table keying dwarf/gnome roles. `handle_task_pre/post` parameterized by kind via `spawn_kind_from_tool_input`. `attribute_to_dwarf` → `attribute_to_subagent` dispatches on `payload.agent_type`. New `state-gnomes.json` parallel to `state-dwarves.json`.
- `developer-braindead/experiments/visualizer/index.html` — gnome sprite (tall pointy hat, slim earth-tone vest, beard tuft, scroll-in-hand; cool blue/lavender/teal palette distinct from dwarves' warm tones). `spawnGnome` / `despawnGnome`, `applyEvent` cases for `spawn-gnome` / `despawn-gnome`, `isGnomeActor` + `isSubAgentActor` helpers, `ensureActorExists` G-prefix skip, ticker stats, `resetWorld` cleanup. `speakerFor` / `actorDisplayName` / `deriveSpeaker` recognize G\d+ IDs. CSS for `data-speaker="gnomes"`, dedicated GNOMES tab in COMMS, legend row.
- Doc updates: [[D-016]] addendum recording the env → payload-field correction; `gielinor/meta/modes.md` line corrected to reference the payload mechanism.

The S020 cascade is on disk but **untested in the wild** — first live gnome spawn is the validation, and that spawn now validates both the boundary fix (does the hook actually fire?) and the visualizer wiring (does the gnome sprite show + chat + walk + despawn?). Combined-test candidate: a Jebrim alching gnome (Jebrim is overdue, never-alched + day-1+ + an in-flight S021 file). Single spawn exercises the boundary, the per-tool attribution, the alching procedure, and D-014 + S015 attribution at once.

## Next concrete step — START HERE

**Step 1 — first live gnome spawn.** Cue: principal sets up a fresh Jebrim session, recognizes the alching threshold breach at respawn, evaluates the spawn heuristic (>20 turns since last-alched OR never-alched + day-1+ — Jebrim qualifies on both), and spawns a gnome via `Task(subagent_type="gnome", description="Alch Jebrim's namespace — never alched, ~20+ in-flight turns since spawn", ...)`. Watch for:

- **Boundary fires.** If the gnome tries to write to `gielinor/meta/foo.md` (planted test write) or to a confirmed/ path, the hook blocks with the BLOCKED message naming the path and the path-mismatch. If the hook doesn't fire, the env→payload fix didn't take and something deeper is broken.
- **Visualizer.** Gnome sprite appears next to Jebrim with the task description as a persistent bubble (intent never expires on building change because `isSubAgentActor` now covers G-prefix). Move events as the gnome walks between buildings; action events on each Edit/Write. Despawn-gnome on Task return.
- **GNOMES tab.** Spawn log, action lines, walk lines all attribute to `speaker: "gnomes"` and render in the new tab with the lavender styling.
- **State file.** `state-gnomes.json` appears in `experiments/visualizer/` with the gnome's `byToolUseId` / `byAgentId` bindings during the run.

**Step 2 — drafts triage (carried from S018 → S019).** Several drafts still await ruling:

- `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md` — promote to `lorebook/decisions/D-NNN_*.md` to canonicalize the S018 audit's structural decisions.
- `gielinor/players/jebrim/keepsake/proposals/2026-05-21_eu-tender-2026.md` (still untouched).
- `gielinor/players/jebrim/spellbook/drafts/skills/moving-target-decomposition.md` — awaits Jebrim skills-promotion at first Jebrim alching (covered by Step 1 if the gnome runs).
- `gielinor/players/jebrim/niksis8_character/drafts/` (S017-era + `2026-05-21-prefers-evidence-over-premature-infrastructure.md`) — also covered by Step 1 if the gnome runs.

**Step 3 — D-014 browser verification (carried from S017).** Subsumed by Step 1's combined test if the principal opens the visualizer in live mode while the gnome runs.

**Step 4 — narration channel shakedown.** Still pending — try writing `.claude/narration.txt` at session boundaries / phase transitions and read in the visualizer. Used briefly at S019 open and again at S020 open.

Other live threads (carried, lower priority):

- **Untracked Jebrim files at S019 close** — `inventory/S015-ttyd-resume.md`, `niksis8_character/drafts/2026-05-21-prefers-evidence-over-premature-infrastructure.md`, `spellbook/drafts/skills/investigate-before-specialize.md`, `quest-log/in-progress/S015_*.md`, modifications to `keepsake/current.md` and `quest-log/completed/S014_*.md`, `keepsake/archive/proposals/`. Pickup at next Jebrim respawn via reconciliation prompt.
- **Soft-block tuning** (S018 close-session pre-commit) — three options offered; re-evaluate "abandon" after first fire.
- **Self-observation sweep tuning** (S018 alching step 3a) — cap 0–3; watch first alching pass output (Step 1).
- **Cross-player parity for future players.** Jebrim + Zezima aligned. No template system yet.
- **Possible `I-NNN` from S018** — quest-log-as-vacuum pattern. Candidate for next bankstanding.
- **Possible `lorebook/drafts/` from S020** — *architectural guarantees need a live failure test, not just code review.* Three boundary hooks shipped over multiple sessions all gated on a wrong predicate that "read right." Pattern worth canonicalizing at next bankstanding. Cite [[S020]].
- **Thread A from S013 — verify visualizer feature set end-to-end.** Mostly covered by Step 1 if it goes live with both attribution + boundary firing.
- **Thread B — observe the harvest pump.** No code; watch what the next sessions' harvests produce.

Iteration menu (deferred, no priority assigned):

- **D-014 follow-ups.** Action target prettification. Chat scroll-lock UX. Actor color taxonomy tightening. Bubble two-line edge cases.
- **Idle indicator / watchdog for non-Claude writes / smarter active-player inference / SSE upgrade.** D-009 deferred.
- **Aesthetic backlog from [[S009]].** Per-building character.
- **Tighten gnome hook allowlist** from `/spellbook/drafts/` to `/spellbook/drafts/skills/` for symmetry with D-016. Phantom risk today; tighten if any non-skills subfolder ever lands there.
- **Gnome workshop building.** Defer until the gnome has been used a few times and the visual gap is felt (per [[D-016]] *Things deferred*).

## Open at the start of next session

- **First live gnome spawn** — Step 1. Validates the whole S020 cascade in one shot.
- **Drafts triage** — Step 2. Largely subsumed if a Jebrim alching gnome runs in Step 1.
- **D-014 + S015 browser verification** — Step 3. Same combined-test candidate as Step 1.
- §C Pilot definition, §H.3 brain-zone taxonomy, §H.4 identity ↔ main-brain interaction — unchanged.

## Carried-over observations

From [[S020]] (new): **architectural guarantees need a live failure test, not just code review.** Three sub-agent boundary hooks (gnome, dwarf, sub-spawn) all gated on env vars Claude Code doesn't propagate. The dwarf hook went undetected for the longest — never tested in the wild because no dwarf ever attempted a prohibited write. Code review can't catch a wrong predicate when the predicate "reads right." Pattern worth a `gielinor/lorebook/drafts/` entry at next bankstanding.

From [[S020]] (new): **the claude-code-guide agent earned its spawn.** Direct domain question ("does Claude Code propagate env vars to sub-agents") with a concrete-needed-answer ("yes/no + canonical mechanism if not"). One-shot, returned the precise field names + payload shape needed for the fix. Confirms [[D-014]]'s dwarf-spawn heuristic: scoped, domain-specific lookups are exactly where sub-agent invocation pays off.

From [[S019]] (still relevant): **a new role's blocklist is easier to get right than its allow-list.** Gnome write-boundary uses both — allow-list for housekeeping surface, explicit blocklist for principal-only paths that might otherwise match. Blocklist precedence is load-bearing.

From [[S019]] (still relevant): **single source of truth for tunable numbers is worth one hop.** Spawn heuristic thresholds in `spawning-gnomes.md`; rituals reference but don't copy.

From [[S018]] (still relevant): **the quest log is the gravitational center; other layers starve without explicit routing.** Layer-routing.md + drafts-gates + inventory promotion fixed this. Candidate for an `I-NNN` next bankstanding.

From [[S018]] (still relevant): **bundle big structural decisions; resist piecemeal landing.** S019 + S020 both follow this — D-016 phases A–D in S019, full ratification + visualizer in S020 rather than splitting.

From [[S017]] (still relevant): **spec docs that prescribe DOM/structure without inventorying what already exists will ship suboptimal designs.**

From [[S017]] (still relevant): **heuristics that walk back through `state.ndjson` need to remember the stream is cross-session.**

From [[S017]] (still relevant): **emulating a specific UI's look means font and palette must change together.**

From [[S016]]: **"players communicate" in dev-brain mode probably means the visualizer, not the chat preamble.**

From [[S015]]: **shipping behind "the docs say X" is risky in this codebase because the docs are right but the integration is novel.** (S020 is a clean counter-example — claude-code-guide returned a docs-cited answer that *was* directly integratable.)

From [[S015]] (separate): **delete discipline isn't enforced for dev-brain infrastructure.**

From [[S014]] (now five-incident pattern with S018): **the procedure was right; the procedure assumed a state that didn't exist.** S020 adds a sixth instance — the hook code was right; the hook's *trigger predicate* assumed a state (env var propagation) that didn't exist.

From [[S014]]: **the renderer needs to be self-healing because the hook stream is a lossy substrate.**

From [[S014]]: **tool renames upstream are silent regressions.**

From [[S013]]: **uncommitted work occupies the ID space.**

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss.**

From [[S009]]: **mental UI preview must include z-order and all collision targets.**

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]]: **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.**

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S020_gnomes_ratification_and_visualizer.md` — most recent session.
3. `quest-log/S019_gnomes_subagent_implementation.md` — the founding session for the gnomes work.
4. `bank/decisions/D-016_gnomes_subagent.md` — founding decision + the S020 addendum on the env → payload fix.
5. `gielinor/.claude/hooks/gnome-write-boundary.py` + `dwarf-write-boundary.py` + `block-sub-spawn.py` — the patched enforcement. Read at least one to internalize the new gating pattern.
6. `gielinor/spellbook/skills/spawning-gnomes.md` — operating spec; single source of truth for heuristics.
7. `gielinor/.claude/agents/gnome.md` — agent config.
8. `gielinor/meta/modes.md` — principal/dwarf/gnome axis with the S020 corrections.
9. `gielinor/spellbook/rituals/close-session.md` + `alching.md` — step 0 spawn-decisions.
10. **For visualizer:** `developer-braindead/.claude/hooks/emit-event.py` (ROLE_CONFIG, attribute_to_subagent) and `experiments/visualizer/index.html` (spawnGnome, applyEvent cases).
11. `bank/decisions/D-014_visualizer_chat_panel.md`, `D-015_jebrim_layer_audit_outcomes.md` — prior decisions the gnome work builds on.
12. `bank/plan.md` — current mission state.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during aesthetic iteration**. State additions across S009–S020 are layered on top of the dispatch surface, not changes to it. Keep extending, don't rewrite.

D-014 added `narrate` and `action` events alongside `intent` / `move` / `spawn-dwarf` / `despawn-dwarf`. S020 added `spawn-gnome` / `despawn-gnome` to the same dispatch surface — additive, no engine rewrite. The renderer's sub-agent surface is now parameterized: `dwarfNodes` / `gnomeNodes`, `spawnDwarf` / `spawnGnome`, parallel state files, shared `isSubAgentActor` for cross-cutting checks.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.

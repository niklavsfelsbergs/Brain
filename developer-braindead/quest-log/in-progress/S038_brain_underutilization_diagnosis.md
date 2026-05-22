# S035 — brain underutilization diagnosis

**Started.** 2026-05-22 — chat opened with Jebrim, flipped to dev-brain mid-session.

## Context

Principal frame: "we are underutilizing a lot of things in the brain — discuss then improve." Jebrim's pre-flip diagnosis (see `gielinor/players/jebrim/quest-log/in-progress/OPEN_2026-05-22_brain-underutilization-frame.md`) named five symptoms collapsing to four roots:

- **A. Promotion gate stalled** (drafts → confirmed; skills graduation): identity layers empty, S034 alching parked 8/8.
- **B. Bank capture post-hoc, not turn-reflexive**: `bank/notes/` thinner than work justifies.
- **C. Close-session backlog**: 11 in-flight Jebrim inventories, some likely stale-done.
- **D. Guthix invisible**: cross-cutting questions go to whichever player is active, not consultation mode.

Thesis: the brain's **write paths** are exercised; **promote** and **consult** paths aren't. Drafts is write-only in practice.

Principal said "all" → do all four, starting with the recommended diagnosis-then-decide approach.

## Phase 1 — diagnosis (in flight)

Spawned 4 Explore dwarves in parallel:

- **D1 — drafts inventory.** Every draft/proposal across globals + Jebrim + Zezima + Guthix. Promotion-readiness assessment per draft. Patterns in what gets drafted vs what stalls.
- **D2 — in-progress quest audit.** Jebrim's 11 in-progress + their inventory resume files. Classify each (done-not-moved / paused / live / abandoned-candidate / ambiguous). Recommended disposition per file.
- **D3 — ritual vs evidence.** Compare close-session / alching / drafts-mechanics specs against git-log evidence of actual invocations. Where is the friction that causes skipping?
- **D4 — Guthix usage trace.** Count consultation + bankstanding invocations historically. Survey Guthix layer contents. Identify where consultation would have helped but principal asked a player instead.

Each dwarf returns a tight diagnostic report. No fix proposals — pure recon.

## Phase 2 — synthesis (dwarf reports received)

### D1 — Drafts inventory

- **13 active drafts, 0 confirmed promotions** across Jebrim/Zezima/Guthix/globals identity layers.
- **5+ ready-to-promote Jebrim drafts**, all 2026-05-22: 2 examine (`check-artifact-mtimes`, `git-add-scoping`), 3 spellbook skills (`scope-creep-detection`, `read-routing-manifest`, `elicitation-with-default`).
- **2 critical lorebook drafts pending**: PowerShell UTF-8 (silent corruption fix), folder-naming-correction (meta-drift cleanup) — both blocked on principal meta edits (user-only by design).
- **Bank notes silent**: Jebrim has 1 pre-dated entry + 0 drafts; Zezima 0/1; Guthix 0/1. Not a draft-gate problem — alching isn't pulling distillations from work.
- **Keepsake flow works** — 5 Jebrim pins archived correctly. Proof the draft→approve loop *can* run.
- Highest-leverage observation: **promotion bottleneck is tempo, not design**. The gate works; review just isn't happening on a cadence.

### D2 — In-progress quest audit (Jebrim, 19 files)

Classification:
- **5 DONE-NOT-MOVED** — S023 (coverage audit), S024 (rulebook revamp), S026 (parent), S034_g2 (alching gnome artifact), OPEN_shipping-agent-personal-folders. All shipped; never walked to `completed/`.
- **8 LIVE** — S002 + 3 dwarves, S015, S026 + 3 dwarves, S034 (active work, recent activity).
- **2 PAUSED** — S001 (explicit carry-forward), S032 (parked + queued audit).
- **1 ABANDONED-CANDIDATE** — OPEN_brain-underutilization-frame (this session's bridge file; archive after S035 closes).
- **2 AMBIGUOUS** — S030_g1 (gnome ritual artifact), S031 (live, but resume missing).
- **2 missing inventory resume files** — S031, S032. Close-session step 3 didn't fire cleanly for these.

Root cause: close-session step 4 ("move done quests to completed") is **discretionary, not enforced**. The principal hasn't cued "this quest is done" for the 5 stale-done; the agent doesn't walk them on its own initiative.

### D3 — Ritual vs evidence (THE LOAD-BEARING FINDING)

**Promotions to `confirmed/` HAVE happened.** S029 alching (2026-05-21) wrote 5 entries into `gielinor/players/jebrim/examine/confirmed/`. They exist on disk.

**But they don't appear in `current.md`.** Per `respawn.md` step 6.e: the agent reads `confirmed/current.md`, **not the full `confirmed/` folder**. `current.md` aggregation is user-only and **no ritual owns it**. So even when promotion happens, the promoted knowledge **doesn't load at respawn**.

Jebrim's frame ("promotion gate stalled") is true but incomplete. The deeper failure: **even successful promotion is invisible at respawn**. The brain is leaking confirmed knowledge before it reaches the active session.

Other D3 findings:
- Alching permits "park all" as a batch — and that's becoming the default. No anti-park clause.
- `/drafts` command is unimplemented (`drafts-mechanics.md`: "to be designed against real use").
- Close-session and alching are **well-specified procedures**. The friction is in principal-side curation, not in ritual vagueness.
- Confirmed-layer write path is hook-enforced user-only — correct architecture, but with no `current.md` aggregation ritual, the user-only gate has no exit.

### D4 — Guthix usage trace

- **1 bankstanding session ever** (B-001, 2026-05-22). **0 consultation traces** (G-NNN entries).
- **0 `Hey Guthix` invocations** in any quest-log across all players.
- **Ratio: 1 Guthix : 53 player sessions = 1.9%.**
- All Guthix layer surfaces empty: `bank/notes/`, `bank/drafts/`, `proposals/`, `keepsake/current.md`.
- This very session (S035) is the case in point — principal asked Jebrim a system-scope question when the consultation mode shipped *2026-05-22 specifically for this shape of question*.
- Diagnosis: "architecture correct, operator adoption zero." Not broken; not yet working.

### Synthesis — the actual leverage map

Jebrim's frame: capture works, promote/consult don't. **Correct.** But the deeper structure D3 found:

1. **Promoted knowledge doesn't load at respawn** (the `confirmed/` → `current.md` gap). This is a *bug*, not a tempo problem.
2. **DONE-NOT-MOVED quests stay open because no one cues "this is done"** — and the agent doesn't take initiative. 5 of 11 are mechanically clear-able.
3. **Drafts pile up because the review step is per-draft, manual, in chat** — no batched-triage mode.
4. **Guthix is invisible because the address isn't reachable through habit** — even the principal asking about brain underutilization didn't reach for `Hey Guthix`.

The five symptoms map to **two bugs (structural)** and **two habits (tempo)**.

## Proposed order

| Phase | Surface | What | Effort | Impact |
|---|---|---|---|---|
| **1a** | structural | Decide: respawn reads `confirmed/` folder, OR alching aggregates to `current.md`. Implement the choice. | small (1 ritual edit + 1-line change OR a new alching step) | promoted knowledge actually loads next session |
| **1b** | mechanical | Move 5 DONE-NOT-MOVED quests to `completed/`. Archive `OPEN_brain-underutilization-frame` post-S035. Add resume files for S031/S032 (or principal decides). | small (gnome work, 30 min) | queue halves; respawn quieter |
| **1c** | mechanical | Promote 5 ready Jebrim drafts (2 examine + 3 skills) via principal triage in chat. Aggregate S029's 5 confirmed entries into Jebrim's `current.md`. | medium (principal turn cost, ~10 min) | identity layer populates from zero to seven entries |
| **2a** | structural | `/drafts` lightweight command — batched y/n/skip per draft. Lowers per-draft review cost from "context load" to "glance + key." | medium (command spec + implementation) | promotion tempo can sustain weekly cadence |
| **2b** | structural | Close-session step 4 gains agent-initiative: scan in-progress for "no pending actions + last turn says ship/complete," propose moves to principal at session close. | small (ritual edit) | DONE-NOT-MOVED becomes self-clearing |
| **2c** | habit | Guthix discoverability heuristic — at session start, if first prompt looks system-scope (cross-cutting, not player-domain), agent suggests `Hey Guthix`. | small (one rule in `meta/communication-protocol.md`) | consultation gets invited rather than remembered |
| **2d** | (deferred) | Turn-reflexive bank capture (Jebrim's "B" root cause). Hardest to enforce, lowest urgency given the above. | large (cognitive discipline + maybe hook nudge) | bank grows during work, not as harvest |

**Recommendation:** Phase 1 in this session (1a + 1b + 1c). Phase 2 next session or two. Phase 2d deferred until 1+2 are proven.

## Pending action

`completed` — 4 dwarves returned, Phase 1 shipped end-to-end.

## Phase 1 — shipped

Principal approved `go all` + chose option (i) for 1a. Executed:

- **1a** — `gielinor/spellbook/rituals/respawn.md` edited at steps 4, 5, 6.e, 6.f. Each now reads every `.md` in `confirmed/` instead of just `current.md`. All 12 previously-invisible Jebrim confirmed entries (+ any future promotions) load on next respawn.
- **1b-1** — `git mv` 8 stale-done quests to `gielinor/players/jebrim/quest-log/completed/`: S023, S024, S026 (parent + d1/d2/d3 dwarves), S030_g1 gnome, OPEN_shipping-agent-personal-folders. Jebrim's in-progress went from 18 → 10 entries.
- **1b-2** — Resume files written for S031 + S032. Each notes the close-session-step-3 gap as the reason for post-hoc creation.
- **1c-1** — 3 drafts promoted (D1 over-counted; on-disk reality was 3 not 5): `check-artifact-mtimes-doc-not-source-of-truth.md` and `git-add-scoping-with-parallel-sessions.md` → `examine/confirmed/`; `elicitation-with-default-surfaced.md` → `spellbook/skills/`. Identity layer 12 → 14 entries, all loading next respawn.
- **1c-2** — Skipped. After 1a, the folder gets read either way; `current.md` aggregation is now optional executive-summary territory.

## Surprises during execution

- **Naming collision.** This dev-brain entry was originally `S035_*` — collided with Jebrim's already-completed S035 (reprompting-skill). Renamed to S038. Cross-cutting S-NNN is the convention; ground-truth Jebrim's completed/ before naming a dev-brain quest next time.
- **D1 was outdated.** Reported 5+ ready drafts; on-disk reality was 3. Skills graduation IS working; identity-layer promotion was the broken half.
- **Untracked existing files surfaced.** `git status` shows pre-existing `S031_*` and `S034_g2_*` in-progress quest-log files as `??` (never git-added). Quest-log narrative survives in working tree but isn't versioned. Worth surfacing in Phase 2 — close-session step 8 evidently misses files that close-session itself didn't write.

## Phase 2 — shipped (a + b + c + d)

Principal picked **(b)** for `/drafts` scope ("active player + globals; exclude Guthix"), then **(a)** for the option cascade ("ship 2b + 2c + 2d in same session").

**2a — `/drafts` command + drafts-triage ritual.**

- `.claude/commands/drafts.md` (new) — slash command Claude Code reads when user types `/drafts`. Tight prompt; defers behavior to the ritual.
- `gielinor/spellbook/rituals/drafts-triage.md` (new, ~140 lines) — full procedure: scope-by-mode (player + globals, excludes Guthix and other players); recommendation rubric (y/n/edit); verdict-execution table mapping each layer to its promotion path; discipline notes. Parallels `alching.md` shape but narrower — single-axis hygiene tool, doesn't update `last-alched.md`.
- `gielinor/meta/drafts-mechanics.md` edited — replaced "to be designed against real use" stub with pointer to the ritual; also fixed the line about respawn reading `current.md` (stale after Phase 1a).

**2b — close-session step 4 agent-initiative scan.**

Added a paragraph to `gielinor/spellbook/rituals/close-session.md` step 4: agent scans **every** in-flight quest (not just session-touched ones) for done-but-not-moved signal — "Pending external actions: None pending," last turn reads as shipping, inventory resume status says done. Proposes batch list to principal for per-line approval (`1y 2y 3n`). Boundary clearly stated: propose only, never auto-complete. This is the Phase 1 cleanup mechanism formalized.

**2c — close-session step 8 orphan-quest-log catch.**

Added a second pre-commit check to step 8: `git status --short` on quest-log paths, grep `??`, surface as part of commit scope. Anchored to today's S031/S034_g2 discovery. Now close-session won't leave untracked quest narratives drifting across sessions.

**2d — Guthix routing heuristic in communication-protocol.md.**

New section before "Intent narration": when an incoming message reads system-scope rather than player-domain, agent surfaces one line suggesting flip to Guthix consultation. Trigger patterns explicit ("what do I have on X across the brain," "we are underutilizing X" — exactly this session's opening prompt to Jebrim), don't-fire-on cases explicit, scope explicit (player + unscoped modes only). The heuristic surfaces the option without forcing the switch. Same shape as the existing wrong-instance check.

## What remains (deferred)

- **Turn-reflexive bank capture** (Jebrim's "B" root cause). Hardest, lowest urgency. Reach for it once the new `/drafts` + close-session-step-4 mechanisms have run for a few sessions and the promote/consult tempo is verifiably back.

## Session disposition

Phase 1 committed at `150e238`. Phase 2 ready to commit — scope: 2 new files (`.claude/commands/drafts.md`, `spellbook/rituals/drafts-triage.md`), 3 edits (`meta/drafts-mechanics.md`, `spellbook/rituals/close-session.md`, `meta/communication-protocol.md`), plus this S038 update.

Next: commit + close session.

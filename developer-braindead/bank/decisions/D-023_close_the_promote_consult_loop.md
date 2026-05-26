# D-023 — 2026-05-22 — Close the promote/consult loop

**Context.** S038 opened with the principal's frame: *"we are underutilizing a lot of things in the brain."* Jebrim's pre-flip diagnosis named five symptoms (drafts piling up, identity layers empty, 11-deep in-progress quest backlog, Guthix barely visited, bank capture post-hoc). A four-dwarf recon (D1 drafts inventory; D2 in-progress audit; D3 ritual-vs-evidence; D4 Guthix usage trace) sharpened the picture.

The load-bearing finding came from D3: **promoted knowledge wasn't loading at respawn.** 12 confirmed Jebrim entries existed on disk under `examine/confirmed/`. Respawn step 6.e read only `current.md`, which was empty. The promotion gate had been running (sporadically); the load surface was the bug. Even when promotion succeeded, the entry was invisible next session.

The frame collapsed: the brain's **write paths were exercised**; the **promote** and **consult** paths weren't. Drafts were write-only in practice. Cross-cutting questions went to whichever player was active instead of Guthix. Stale-done quests stayed in `in-progress/` until someone manually cued completion. The brain wasn't slow to promote — it was leaking confirmed knowledge before it reached the active session, and reaching for the wrong actor for system-scope questions.

**Decision.** Close the loop with a mix of structural fixes (bugs) and habit-shaping aids (heuristics/proposals). Structural first because they don't drift; habits get layered on top once the bug is fixed.

## The fixes

### Structural (Phase 1)

**1. Respawn reads every `.md` in `confirmed/`, not just `current.md`.** Steps 4, 5, 6.e, 6.f in `gielinor/spellbook/rituals/respawn.md`. `current.md` becomes optional — an executive summary alongside atomic entries, not the load surface. **Generalizable design pattern: when a discipline rule requires manual aggregation that nobody runs, the right fix is usually to remove the aggregation requirement, not to add a ritual that does it.** The aggregation step rotted because no ritual owned it; removing the step removes the rot.

**2. Cleanup pass.** 5 stale-done Jebrim quests (S023, S024, S026 + 3 dwarves, S030_g1 gnome, OPEN_shipping-agent-personal-folders) walked to `completed/`. Two missing inventory resume files (S031, S032) generated post-hoc. Two orphan in-progress quest-log files (S031, S034_g2) that had lived untracked for sessions caught up. 3 ready drafts promoted (2 examine + 1 skill). Jebrim's `in-progress/` 18 → 10; identity layer 0 → 14 loading entries.

### Habit-shaping (Phase 2)

**3. `/drafts` slash command + drafts-triage ritual.** New `.claude/commands/drafts.md` + `gielinor/spellbook/rituals/drafts-triage.md`. Lightweight cut of alching step 1 — invocable any time, no full ritual required. Scope: active player + globals; excludes Guthix (bankstanding territory) and other players (their own alching). Verdict format: agent surfaces with y/n/edit recommendations, principal triages in batch (`1y 2y 3n`), generic affirmation resolves to "approve every `y`" per the elicitation-with-default skill. Promotion via `git mv` (Bash bypasses the `block-confirmed-writes` hook — the hook lists Edit/Write/MultiEdit/NotebookEdit, not Bash; this is the sanctioned promotion path).

**4. Close-session step 4 agent-initiative scan for stale-done quests.** Agent walks every in-flight quest at close (not just session-touched ones), looks for "Pending external actions: None pending" + last turn shipping language + inventory resume done status. Proposes batch list; principal approves per-line. Boundary explicit: propose only, never auto-complete.

**5. Close-session step 8 orphan-quest-log catch.** Added a second pre-commit check: `git status --short` on quest-log paths, grep `??`-prefix, surface untracked quest narratives as part of commit scope. Born of today's S031/S034_g2 discovery.

**6. Guthix routing heuristic in `meta/communication-protocol.md`.** New section before "Intent narration": when an incoming message reads system-scope rather than player-domain, agent surfaces one line suggesting flip to Guthix consultation. Trigger patterns and don't-fire-on cases explicit; scope limited to player + unscoped modes. Same shape as the existing wrong-instance check. **The heuristic was born of this conversation mis-routing itself** — the principal asked Jebrim *"we are underutilizing a lot of things in the brain"*, which is exactly the system-scope question Guthix's consultation mode exists for. Pre-S038 Guthix invocation ratio: 1.9% (1 bankstanding ever, 0 consultations, 0 `Hey Guthix` invocations in any quest-log). Architecture correct, operator adoption zero.

## Alternatives considered

- **Aggregate `confirmed/` entries into `current.md` as part of alching** (1a option ii). Rejected — adds an alching step that widens the agent's write surface (currently `confirmed/` is hook-blocked; adding an exception during alching is fragile), and keeps the manual aggregation problem rather than removing it. Read-folder (option i) is the simpler fix.
- **Auto-complete stale-done quests at session close.** Rejected — the agent has full read of each quest but the principal still owns the "this is done" call. Auto-completion risks moving a quest the principal had intended to extend. Propose-only with per-line approval matches the existing close-session discipline ("propose, never destroy").
- **`/drafts` as a thin wrapper over alching step 1.** Rejected — alching is a full per-player tending ritual (skill graduation, bank staleness, current.md budget, last-alched update). Drafts-triage is single-axis. Sharing the command makes both rituals less precise. Better to have two narrow tools than one wide one.
- **Add a `last-drafts-triaged.md` cadence marker.** Rejected as premature — `/drafts` is meant to be invocable any time, including multiple times per day. A cadence file would imply a recommended interval; the absence of pending drafts is already the right signal that the gate is empty.
- **Force Guthix on system-scope questions automatically.** Rejected — the agent doesn't switch actors on its own initiative; the principal owns the address. Heuristic surfaces the option in one line and waits.

## What this changed on disk

**Phase 1 (commit `150e238`):**

- `gielinor/spellbook/rituals/respawn.md` — steps 4, 5, 6.e, 6.f rewritten to read folder instead of single file.
- `gielinor/players/jebrim/quest-log/` — 8 files moved from `in-progress/` to `completed/`.
- `gielinor/players/jebrim/examine/drafts/` and `spellbook/drafts/skills/` — 3 drafts promoted (2 examine + 1 skill).
- `gielinor/players/jebrim/inventory/` — 2 new resume files (S031, S032).
- `gielinor/players/jebrim/quest-log/in-progress/` — 1 new OPEN frame (the Jebrim-side hand-off of the underutilization frame before dev-brain flip; archived at S038 close).
- `developer-braindead/quest-log/in-progress/` — `S038_brain_underutilization_diagnosis.md` (this session's run-log).
- 2 orphan untracked quest-log files (`S031_*`, `S034_g2_*`) staged for the first time.

**Phase 2 (commit `607eeb4`):**

- `.claude/commands/drafts.md` (new) — slash command.
- `gielinor/spellbook/rituals/drafts-triage.md` (new) — ritual procedure.
- `gielinor/meta/drafts-mechanics.md` — `/drafts` stub replaced with pointer; respawn-reads-current.md line corrected.
- `gielinor/spellbook/rituals/close-session.md` — step 4 agent-initiative scan added; step 8 second pre-commit check added.
- `gielinor/meta/communication-protocol.md` — new Guthix routing section before "Intent narration."

## Open questions

- **Will the Guthix routing heuristic actually fire?** It depends on the agent's read of "system-scope vs player-domain" being calibrated. First-run data needed; tune trigger patterns after observing real misses. The heuristic is silent on false-positives (suggesting Guthix when the question really is player-scoped) — those just cost a one-line surface the principal dismisses.
- **Will close-session step 4's batch surface scale?** If a player accumulates 20+ stale-done candidates between session closes, the batch will be heavy to triage. Watch the first few cycles; might need to cap per-pass or pre-filter by signal strength.
- **Will `/drafts` get used?** The implementation is sound but adoption is the same question Guthix faced. The slash command exists; principal habit matters more than spec. Worth a check at next bankstanding — count `/drafts` invocations in commit history.
- **Turn-reflexive bank capture (Jebrim's "B" root cause, deferred).** Hardest of the original five symptoms; not addressed in this decision. Reach for it once the new mechanisms have run for a few sessions and the promote/consult tempo is verifiably back. If `/drafts` stays empty and identity layers stay tight, the consult/promote loop is working and bank capture is the next leverage point.

## Meta-observations from this session

- **Recon dwarves report stale snapshots.** D1 said 5+ ready drafts; on-disk reality was 3. D2 referenced an `S034_g2` quest that existed but was untracked. The brain moves between sessions; dwarf recon ages between task start and report time. Going forward: ground-truth dwarf counts before acting on them.
- **The brain's own underutilization was the test fixture for diagnosing the brain's own underutilization.** This conversation reached for Jebrim instead of Guthix for a system-scope question. The Guthix routing heuristic shipped in 2d is born of literally this session mis-routing itself. Reflexive proof that the heuristic is needed.
- **Cascade approvals when proposing many small writes.** Initial over-gating ("approve per-file") was corrected on principal cue ("thats too blocking"). The right shape for many small writes: ask once for the cascade ("go all"), reserve per-item approval for identity-shaping decisions. Per the elicitation-with-default skill we promoted this same session.

## Related

- [[D-017_parallel_player_instances]] parallel player instances — the substrate this work assumes.
- [[D-022_guthix_consultation_mode]] Guthix consultation mode — defines the actor whose adoption this decision aims to surface.
- `gielinor/spellbook/rituals/drafts-triage.md` — the ritual `/drafts` runs.
- `gielinor/spellbook/skills/2026-05-22-elicitation-with-default-surfaced.md` — promoted this session; informs the `/drafts` verdict-collection shape.
- `gielinor/players/jebrim/quest-log/in-progress/OPEN_2026-05-22_brain-underutilization-frame.md` — the Jebrim-side hand-off frame (archived at S038 close).
- `developer-braindead/quest-log/S038_brain_underutilization_diagnosis.md` — the session's full run-log (walks to `completed/` at S038 close).

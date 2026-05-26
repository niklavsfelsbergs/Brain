# D-018 — 2026-05-22 — Parallel-session substrate isolation: per-session sidecars + discipline rules

**Context.** Five sessions in a row have surfaced parallel-session interference at the filesystem layer:

- [[S014_visualizer_polish_and_aesthetics_pass]] — `state-actors.json` race during a mid-session player swap.
- [[S022_visualizer_audit_fixes]] — Bash attribution leak on the shared `state.ndjson` recency walk.
- [[S023_visualizer_ticker_and_cross_session_attribution]] — dev-brain override flag (`active-mode.txt`) racy across sessions.
- [[S024_visualizer_aliveness_pass_1_3]] — intent bubble silence after move (different bug; same shared-state family).
- [[S025_parallel_player_instances]] — git index race; Jebrim's broad `git add` swept up D-017's staged changes into his commit.

Each got a local band-aid. The band-aids stack but don't address the underlying structural issue.

**The mismatch.** The brain is implicitly designed as a single-writer filesystem. The cognitive model — "one agent, one body, one brain" — assumes a coherent writer across every layer (`bank/`, `drafts/`, `keepsake/current.md`, state files, the git working tree). Claude Code's process model permits **N sessions on the same working directory concurrently**. The implementation has multi-writer access to a single-writer-designed substrate. Every shared mutable file is a latent race.

[[D-017_parallel_player_instances]] addressed *attribution* — the visualizer now renders parallel sessions as distinct tinted sprites. It did not address *isolation* — two Jebrims still share `state-actors.json`, still share `keepsake/current.md`, still share the git index. Labels made the symptoms legible; they didn't change the substrate.

## Decision

Adopt **per-session sidecars where data is naturally session-local; principal-arbitrated discipline where data is shared by design**. Reject worktree-per-session and CRDT-style state as too heavy for current usage. Document the workflow rules so the discipline holds when memory of the incidents fades.

### Taxonomy of shared mutable state

Three categories, three different treatments.

#### Category A — session-local data (sidecar per session)

Data that semantically belongs to one session. Should be physically per-session on disk; no shared file to race on.

| Surface | Current state | Treatment |
|---|---|---|
| `state.ndjson` | shared append-only log, session-stamped events (S023) | already correct — append is interleave-safe per B9 (S021 audit); session-stamped events let readers filter |
| `intent/<actor>.txt` | shared per-actor file | partially fixed in D-017 — per-session variant `<actor>-<sid8>.txt` exists; bare-file fallback remains for backwards compat. **Action: deprecate bare-file path once the cutover lands.** |
| `narration.txt` | shared, last-write-wins | acceptable as-is — narration is "system voice," and the most recent line is what should display. No fix needed. |
| `active-mode.txt` | shared, last-write-wins | already partially fixed in S023 (`_mode_session_id` recorded in `state-actors.json`, dev-brain override gated on it). **Action: extend the session-gating pattern to any future similar markers.** |
| `state-actors.json` | shared map `actor → building` | racy on concurrent moves of different actors. **Action: re-key as `(actor, sessionId) → building` for player-class actors**, matching the D-017 instance registry pattern. |
| `state-instances.json` | shared registry of `(actor, session_id) → instance` | already session-keyed by construction. Counter increment IS a race but acceptable — at worst two sessions assign the same instance number; the visualizer collision (same sprite key) self-heals when the next event lands and re-resolves. Add a lock if it becomes a real problem. |
| `state-dwarves.json`, `state-gnomes.json` | shared sub-agent registries | sub-agents are session-local by nature; should be session-keyed. **Action: re-key by `(sessionId, id)` to prevent collisions between two parallel sessions both spawning D1, D2, etc.** |

#### Category B — shared brain content (principal-arbitrated)

Data that semantically belongs to "the brain" — multi-session by design. Sidecaring would break the single-source-of-truth invariant. Stays single-writer, conflicts arbitrated by the principal at merge points.

| Surface | Current state | Treatment |
|---|---|---|
| `keepsake/current.md` (global + per-player) | user-only writes | already correct. Principal owns the pin set; agents propose. |
| `meta/*.md` | user-only writes | already correct. |
| `examine/confirmed/`, `niksis8/confirmed/`, `niksis8_character/confirmed/` | user-only writes | already correct — hook-enforced (no writes to `confirmed/`). |
| `lorebook/decisions/` | user-only writes | already correct. Drafts are agent-writable; canonicalization is principal-only. |
| `spellbook/rituals/` | user-only writes | already correct. |
| `bank/notes/` per-player | agent-drafted in `bank/drafts/notes/`, alching-promoted | drafts are unique-slug per file → no race. Promotion is principal-arbitrated. **Action: at alching, if two sessions drafted same-topic notes, principal merges or rejects one explicitly.** |
| `quest-log/in-progress/` per-player | each session writes its own file (date + slug naming) | already correct. Two parallel Jebrims write to two separately-named files. Inventory resumes name the active quest. |
| `inventory/` per-player | volatile working state | racy but acceptable — inventory is "what's carried now"; the latest writer's mental state is the right answer. Document the cost: a session that returns after another session has been carrying different inventory will read stale state and may resume incorrectly. **Action: per-session inventory files for resume-state**, named `<quest-slug>-<sid8>.md`, with a no-suffix fallback for single-session work. |

#### Category C — git working tree + index

The most disruptive race, because it can rewrite history. Cannot be sidecared without per-session worktrees.

| Surface | Current state | Treatment |
|---|---|---|
| git index | shared, no locking | **Discipline rule: never `git add -A` / `git add .` while parallel sessions may be active. Always commit with explicit paths.** Already in global `CLAUDE.md` for sensitive-file reasons; this is the second reason. |
| working tree | shared filesystem | follows from index discipline + Category A/B treatment per-file |
| branch state | shared HEAD | acceptable risk — commits sequence linearly; two concurrent commits would race the HEAD update but git itself handles that atomically. |

### Discipline rules (committed)

These extend / clarify rules already in the global `CLAUDE.md`:

1. **No `git add -A` or `git add .` in any agent context.** Always commit with explicit paths. Already user-rule for sensitive-file safety; D-018 adds parallel-session safety as a second reason.
2. **No staging files outside the agent's own session scope.** A Jebrim session does not stage `developer-braindead/` files. A dev-brain session does not stage `gielinor/players/<other-player>/` files. The principal arbitrates cross-scope commits manually.
2a. **Use `git commit -- <paths>` form** when other sessions may have staged files in the shared index. `git add <my paths>` followed by plain `git commit` will *still* capture everything currently staged. Confirmed live during the very commit that landed this decision — three of Jebrim's pre-staged file renames came along for the ride. The pathspec on `commit` is the only form that truly scopes the commit.
3. **Intent files use per-session naming when parallel sessions of the same player are likely.** `<actor>-<sid8>.txt` over `<actor>.txt`. Single-session work can continue using the bare file until the migration is complete.
4. **State file schemas use `(actor, sessionId)` keying** for any state that's per-actor and per-session. Migration in: `state-actors.json`, `state-dwarves.json`, `state-gnomes.json`, future similar.

### Out of scope

- **Worktree-per-session.** Each session opens in its own git worktree on its own branch, merges to `main` at session close. Would eliminate the Category C race entirely but adds operational overhead per session — branch creation, merge, conflict resolution. Defer until parallel sessions become routine enough that the manual workflow burden is justified.
- **CRDT-style append-only state.** All shared mutable files become event logs; current state derived by reduction. Would eliminate every Category A race but requires a substantial visualizer + hook rewrite. Defer.
- **File-locking via fcntl / Windows FileLock.** Possible but fiddly; complicates the hook's error-swallow contract. Acceptable if a specific race proves persistent; not pre-emptively.

### Success criteria

This decision is "working" when:

- Bug surface from parallel-session shared-state races stays flat for 3+ sessions of mixed work.
- A new shared mutable file added to the brain triggers the question "Category A/B/C?" before being merged.
- The S014–S025 pattern stops appearing in respawn.md's carried-observations list.

This decision is "failing" when:

- A sixth incident appears with the same shape as S014–S025 — at which point worktree-per-session moves from out-of-scope to recommended.

## Related

- [[D-017_parallel_player_instances]] — parallel player instances at the visualizer layer (attribution).
- [[S014_visualizer_polish_and_aesthetics_pass]], [[S022_visualizer_audit_fixes]], [[S023_visualizer_ticker_and_cross_session_attribution]], [[S024_visualizer_aliveness_pass_1_3]], [[S025_parallel_player_instances]] — the five-incident pattern that motivated this.
- Global `CLAUDE.md` user-rules — existing "no `git add -A`" warning; D-018 broadens its rationale.
- `gielinor/meta/write-rules.md` — the per-layer write discipline; D-018 layers concurrency considerations atop it.

## Open questions

- **Migration plan for state file re-keying.** `state-actors.json` re-key is a schema change — visualizer's bootstrap reader needs to handle both old (`actor: building`) and new (`actor:sid: building`) shapes. Cost: one half-day session.
- **Bare intent-file deprecation.** The fallback path in D-017's `_intent_file_candidates` keeps backwards compat indefinitely. Drop it once the principal confirms all sessions are writing per-session files; until then, two parallel sessions writing to bare `<actor>.txt` will clobber each other on disk (the hook stream still gets both events via session-stamping at append time, so the visualizer is fine — the on-disk file is the casualty).
- **Cross-session principal arbitration UX.** When alching surfaces "two sessions drafted same-topic notes," what's the principal's interface? Today it's manual reading of both. A diff-style surface could help.

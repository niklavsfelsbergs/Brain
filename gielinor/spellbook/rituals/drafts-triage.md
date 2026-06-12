# drafts-triage — lightweight promotion ritual

The procedure the agent runs when the principal invokes `/drafts`. A standalone partial version of alching's step 1 — surface pending drafts, propose verdicts, execute on approval. Lower friction than full alching, scoped only to the promotion gate.

Born 2026-05-22 (S038, brain-underutilization fix). The need surfaced when 12+ confirmed entries existed on disk but `respawn.md` was reading only `current.md`, and 5+ drafts had been sitting promotion-ready for days with no review pass. Alching covers the gate but is too heavy to invoke just for promotion. `/drafts` is the lightweight cut.

**Failure handling.** On any step failure (a verdict `git mv` fails, a layer won't read), emit this ritual's locked banner from `spellbook/failure-banners.md` verbatim and **halt** — never report the triage as clean when some verdicts landed and some didn't.

## Scope

**In scope:**

- Active player's drafts (if a player is active):
  - `players/<active>/examine/drafts/`
  - `players/<active>/niksis8_character/drafts/`
  - `players/<active>/bank/drafts/notes/`
  - `players/<active>/spellbook/drafts/skills/`
  - `players/<active>/keepsake/proposals/`
- Global identity drafts:
  - `examine/drafts/`
  - `niksis8/drafts/`
  - `keepsake/proposals/`
  - `lorebook/drafts/`

**Out of scope:**

- Guthix's deity layers (`deities/guthix/...`). Promoting from those is bankstanding's job — Guthix's promotions cross-cut the system and need ritual context.
- Other players' content. That player runs their own alching when they want to triage.
- In-flight quest content, inventory, or any non-draft surface.

**Mode-by-mode reach:**

- **Player session** — active player's layers + globals.
- **Dev-brain (Braindead) session** — globals only. Braindead isn't a player; he tends construction, not identity.
- **Consultation (Guthix) session** — runs against globals only. Guthix's own layers stay reserved for bankstanding.
- **Unscoped** — globals only.

## When it runs

- **On principal cue** — the `/drafts` slash command.
- **Recommended** if respawn flags pending drafts but full alching is too heavy for the moment.

The agent never auto-runs drafts-triage.

## The procedure

**Before the survey, read `meta/write-rules.md`** — it left the eager `@import` chain (§X Stage B), and this ritual is one of its re-triggers. It carries the per-layer draft→approve discipline and which layers are user-only (keepsake `current.md`, lorebook) vs. agent-promotable — the exact knowledge the execute step (§4) depends on.

**Switchboard marker.** Flag the session so the board renders a `drafts` flavor chip instead of a bare `BUSY` (mirrors alching's marker; see `meta/communication-protocol.md` → *Mode marker sidecar*): **on entry**, write `drafts` to `.claude/intent/<sid8>.mode` at the brain root (`<sid8>` = first 8 chars of `CLAUDE_CODE_SESSION_ID`); **on exit/report** (step 5, or if no drafts in scope), overwrite with an empty line to clear it. Switchboard-only — a missing marker just means no chip. When drafts-triage is delegated to a gnome, the principal's row reads `AWAITING CREW` and no `drafts` marker is written.

### 1. Survey

List every draft across in-scope layers. Group by layer (player layers first if a player is active, then globals). Number consecutively across all groups so the principal can address by number in a flat list.

Per draft, capture:

- Path (relative to brain root).
- One-line claim summary (the rule the draft proposes, in the draft author's voice).
- Anchor (date or session reference visible in the draft body).
- Agent recommendation: **y** (promote) / **n** (reject) / **edit** (needs revision before approval).
- One-line reason for the recommendation.

Recommendation rubric:

- **y** — observation-backed, concrete anchor (date/session/file path), clear rule, no contradiction with existing confirmed entries. Caveats like "single occurrence" are author conservatism, not blockers.
- **n** — speculative without anchor, duplicates an existing confirmed entry, or matches a pattern previously rejected in the same layer's `rejected/`.
- **edit** — solid observation but wording unclear, anchor incomplete, or rule scope ambiguous. Name specifically what to fix.

### 2. Surface to principal

Format per draft:

```
**Draft 1 / N — <layer> — <slug>**
[1-line claim]
Anchor: [where]
My take: [y/n/edit]. [why]
```

All drafts at once, numbered globally. Principal triages in batch.

If no drafts exist in scope, report cleanly: *"No pending drafts in scope. Done."* Do not invent drafts.

### 3. Collect verdicts

Principal replies in one of two shapes:

- **Batch on one line:** `1y 2y 3n 4: edit "use 'rule' not 'guideline'"`.
- **Per-line:** one verdict per draft, possibly across multiple lines.

Both forms accepted. Generic affirmation (`yes`, `go`, `all y`, `sure`) resolves to "approve every `y` recommendation; carry forward agent's `n` and `edit` calls" — per the elicitation-with-default-surfaced skill. If the principal wants different verdicts than the agent's recommendations, they have to call them out explicitly.

If the principal challenges a recommendation ("why y on #3?"), the agent answers and waits for the revised verdict. Do not execute until verdicts are settled.

### 4. Execute

For each verdict, execute as follows:

| Verdict | Layer | Action |
|---|---|---|
| **y** | `examine/drafts/` | `git mv` to sibling `examine/confirmed/` |
| **y** | `niksis8_character/drafts/` or `niksis8/drafts/` | `git mv` to sibling `confirmed/` |
| **y** | `bank/drafts/notes/` | `git mv` to `bank/notes/` preserving sub-path |
| **y** | `spellbook/drafts/skills/` | `git mv` to `spellbook/skills/` |
| **y** | `keepsake/proposals/` | **User-only.** Surface proposed pin text + target `keepsake/current.md` section; principal hand-edits. |
| **y** | `lorebook/drafts/` | **User-only.** Surface; principal canonicalizes as `lorebook/confirmed/D-NNN_<slug>.md`. In the same pass, add the decision's entry to `lorebook/_index.md` (distilled rule + cue patterns if it has a topic-cue moment, else its `carried-by:` line) — an unindexed decision is invisible to the `[LOR]` cue arm; `hygiene-check.py` flags the drift. |
| **n** | any | `git mv` to sibling `rejected/` preserving sub-path. Optionally append a one-line rejection note (use Edit before mv). |
| **edit** | any | Revise per principal direction; surface revised text for re-confirmation; on second-pass `y`, treat as y. |

**Why `git mv` via Bash and not `Edit`/`Write`:** the architectural hook `block-confirmed-writes.py` fires on PreToolUse for Edit/Write/MultiEdit/NotebookEdit — any path containing `confirmed/` is blocked. Bash is not in the hook's tool list, so `git mv` is the unblocked promotion path. This is sanctioned, not a workaround.

Per move, report briefly (one line per action). Batch-execute when possible (single Bash with chained `git mv`).

### 5. Report

Final summary:

- Counts by layer and verdict (e.g., *"examine: 2 promoted, 0 rejected; skills: 1 promoted; lorebook: 1 surfaced for principal write."*).
- Any drafts that couldn't be auto-moved (user-only layers — keepsake, lorebook).
- Brief cadence note: *"Next /drafts when drafts > 5 (or you feel like it)."*

No quest-log entry written by default — `/drafts` is a sub-minute hygiene tool, not a session event. If the triage produces a surprising pattern (3+ rejected drafts of similar shape, or a contradiction between a new draft and an existing confirmed entry), the agent surfaces it for next bankstanding rather than acting on it.

## What drafts-triage does not do

- Does **not** update `last-alched.md`. Alching is a deeper tending pass; this is a single-axis hygiene tool.
- Does **not** promote `bank/notes/` staleness (that's alching step 2's second half).
- Does **not** graduate skills from completed quests (alching step 6).
- Does **not** write to `confirmed/` via `Edit`/`Write` — `git mv` only.
- Does **not** touch Guthix's layers. Cross to bankstanding for those.
- Does **not** auto-surface drafts on session start. The principal invokes it.
- Does **not** read drafts in `archive/` or `rejected/`. Those are settled.

## Discipline

- **Propose, don't destroy.** Same rule as alching/bankstanding.
- **Preserve paths into archive/rejected.** A draft at `bank/drafts/notes/x/y.md` rejects to `bank/rejected/notes/x/y.md`. Never flatten.
- **Honor user-only layers.** Keepsake pins and lorebook decisions still go through principal-side writes; the agent surfaces and waits.
- **Anchor recommendations in observation, not vibes.** "ready-to-promote" must point at concrete anchor language in the draft. If the agent can't quote the anchor, the recommendation is `edit`, not `y`.
- **Stay narrow.** If something cross-cutting surfaces (skill that crosses players, identity observation that's actually system-level), note it for next bankstanding and move on.

## Related

- `alching.md` — the deeper per-player ritual that includes drafts-triage as step 1. Use alching when also tending bank staleness, current.md budgets, and skill graduation.
- `bankstanding.md` — the system-level counterpart. Touches Guthix layers and global identity at full ritual depth.
- `drafts-mechanics.md` — the founding drafts discipline. This ritual operationalizes the `/drafts` command stub from that file.
- `spellbook/skills/2026-05-22-elicitation-with-default-surfaced.md` — the elicitation pattern the verdict-collection uses (default surfaced, generic affirmation resolves to it).

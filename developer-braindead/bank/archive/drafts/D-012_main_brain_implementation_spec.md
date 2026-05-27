# D-012 implementation spec — main-brain edits queued

**Status.** Spec written 2026-05-21 in dev brain. **Applied in [[S013_close_session_harvest_pump|S013]]** this session — see `developer-braindead/respawn.md` post-S013 for the application record.

**Companion.** [[D-012_close_session_harvest_pump]] for the design rationale. This file is just the concrete diffs.

**Order matters.** Apply edits 1–6 in sequence. Edits 5–6 (scaffolds + lorebook draft) can land in the same commit as edit 1 (write-rules flip) or follow it; the harvest pump (edits 2–3) is functionally inert until at least edit 1 + per-player scaffolds (edit 5) exist.

---

## Edit 1 — `gielinor/meta/write-rules.md`

**Goal.** Flip `bank/` row from auto-write to drafts-gated. Soften the principle line accordingly. Note the discipline-only enforcement in the "What's enforced vs guided" section.

### 1a. The table row

Replace:

```markdown
| `bank/` (per-player) | yes, freely | when overturning existing knowledge | — |
```

With:

```markdown
| `bank/` (per-player) | drafts only (`bank/drafts/notes/`) | all promotions to `bank/notes/` | — |
```

### 1b. The principle line

Replace:

```markdown
Anything that defines who the agent thinks I am, who the agent (or a player) thinks it is, or what has been decided about the system requires my sign-off.

Knowledge and observations accumulate freely. Identity and core decisions are gated.
```

With:

```markdown
Anything that defines who the agent thinks I am, who the agent (or a player) thinks it is, or what has been decided about the system requires my sign-off. Knowledge accumulates via drafts that I review during alching.

Observations enter the brain freely as drafts. Promotion to canonical knowledge — identity, character, decisions, and per-player bank — is gated.
```

### 1c. The "What's enforced vs guided" section

Under **CLAUDE.md guides (discipline):**, add a bullet:

```markdown
- The bank drafts gate. `bank/notes/` is not hook-enforced; the agent has to write only to `bank/drafts/notes/` on its own and let alching promote. Pattern parallel to identity-layer drafts but without the hook. Reopen if discipline slips.
```

---

## Edit 2 — `gielinor/spellbook/rituals/close-session.md`

**Goal.** Insert observation-harvest as a new step in the per-player loop (between current 5 and 6). Renumber subsequent steps. Extend the existing "Surface drafts" step to enumerate `bank/drafts/notes/`.

### 2a. Per-player loop intro

Replace:

```markdown
For **each player** with a non-empty `quest-log/in-progress/`, run steps 1-5 in that player's namespace. Then run global steps 6-9.
```

With:

```markdown
For **each player** with a non-empty `quest-log/in-progress/`, run steps 1-6 in that player's namespace. Then run global steps 7-10.
```

### 2b. New step 6 — Observation harvest

Insert between current "### 5. Inventory hygiene" and "### 6. Surface drafts...":

```markdown
### 6. Observation harvest

After the entry is tightened (step 3), skim what happened this session and convert anything durable into draft form. This is **Pump 2** — the per-close population pump that keeps identity layers and bank growing. See [[D-012]] (dev brain) for the rationale.

**Skim surface.**

- Fresh turns added to in-progress quest-log entries this session.
- The resume sections (**Where we are**, **Next concrete step**) of all in-progress quests touched this session.

The agent judges per-item stability — "is this observation likely to still be true next session, or is it still shifting?" Stable findings become drafts; shifting content stays in the turn log.

**The four harvest questions.**

1. *"Did any work crystallize into a reusable concept this session?"* → write to `players/<active>/bank/drafts/notes/<topic>/<slug>.md`.
2. *"Did I notice something about myself or how I operate?"* → write to `players/<active>/examine/drafts/<YYYY-MM-DD>-<slug>.md`. Global (`gielinor/examine/drafts/`) only if the observation is clearly cross-player and the principal cues it.
3. *"Did I notice something about Niklavs through this work?"* → write to `players/<active>/niksis8_character/drafts/<YYYY-MM-DD>-<slug>.md`. Global routing handled by bankstanding, not here.
4. *"Did anything earn a pin?"* → write to `players/<active>/keepsake/proposals/<YYYY-MM-DD>-<slug>.md`. Almost always no.

**Discipline.**

- **Cap 1–5 drafts per session.** Bias to less. Empty-set is a valid and common answer. A session where nothing earned its way produces zero drafts; this is healthy.
- **Observation-backed only.** Drafts must cite the specific turn or moment that produced them, per `gielinor/meta/drafts-mechanics.md`. Aspirational drafts ("I should be more careful about X" with no anchor) fail the discipline.
- **Player-scope first.** Per [[D-012]] (D2=B), drafts land in the active player's namespace by default. Cross-player promotion is bankstanding's job.

**Unscoped sessions.** If the session was unscoped (no player ever activated), harvest writes to `gielinor/examine/drafts/`, `gielinor/niksis8/drafts/`, `gielinor/lorebook/drafts/`, and `gielinor/keepsake/proposals/` directly. Bank-note candidates have no global home — write them to `players/inbox/<YYYY-MM-DD>-<slug>.md` for bankstanding to triage.

**Skill graduation is NOT done here.** That's a Pump 3 (alching/bankstanding) job. Close-session harvest captures observations; alching converts patterns into named skills.
```

### 2c. Renumber existing step 6 → step 7

Change heading "### 6. Surface drafts across global + per-player layers" to "### 7. Surface drafts across global + per-player layers".

Inside that step, replace the draft-folder enumeration:

```markdown
If this session created any `examine/drafts/`, `niksis8/drafts/`, `niksis8_character/drafts/`, `lorebook/drafts/`, or `keepsake/proposals/` entries, **surface them now** — one line per draft, grouped by layer.
```

With:

```markdown
If this session created any `examine/drafts/`, `niksis8/drafts/`, `niksis8_character/drafts/`, `lorebook/drafts/`, `keepsake/proposals/`, or `bank/drafts/notes/` entries (including this session's harvest output from step 6), **surface them now** — one line per draft, grouped by layer.
```

### 2d. Renumber existing steps 7–9 → 8–10

- "### 7. Commit" → "### 8. Commit"
- "### 8. State the close" → "### 9. State the close"
- "### 9. Special case: unscoped session" → "### 10. Special case: unscoped session"

No content changes inside those steps beyond the number in the heading.

---

## Edit 3 — `gielinor/spellbook/rituals/alching.md`

**Goal.** Extend step 2 to triage `bank/drafts/notes/` before reviewing `bank/notes/` for staleness. Add a new step (between current 5 and 6) for skill graduation.

### 3a. Step 2 extension

Replace:

```markdown
### 2. Review the active player's `bank/` for staleness

Walk the player's `bank/notes/`. Look for entries that are no longer relevant — superseded by newer notes, about work that's done and won't come back, contradicted by current state. Propose moves to `bank/archive/notes/<same path>`.
```

With:

```markdown
### 2. Promote bank drafts, then review `bank/notes/` for staleness

**First, triage `bank/drafts/notes/`.** This holds harvest candidates from session closes (see [[D-012]] in dev brain) and any direct drafts the agent or principal landed mid-session. Per draft:

- **Promote** → move to `bank/notes/<same path>` (preserve folder structure).
- **Reject** → move to `bank/rejected/notes/<same path>`. Kept, not deleted.
- **Edit and promote** → the principal rewrites, then moves.

A draft that contradicts an existing `bank/notes/` entry triggers the "overturning existing knowledge" path: the contradiction surfaces, and either (a) the new draft wins and the old note archives, or (b) the new draft is rejected.

**Then, review `bank/notes/` for staleness.** Walk the player's existing notes. Look for entries that are no longer relevant — superseded by newer notes, about work that's done and won't come back, contradicted by current state. Propose moves to `bank/archive/notes/<same path>`.
```

### 3b. New step — Skill graduation

Insert between current "### 5. Review patterns in the player's `rejected/` folders" and "### 6. Update `last-alched.md`":

```markdown
### 6. Skill graduation — walk confirmed layers for named-pattern candidates

Per [[D-012]] (dev brain), Pump 3 extends to skill-graduation. Walk these layers looking for patterns that have repeated and earned a name:

- `players/<active>/examine/confirmed/` — patterns in how this character operates that have stabilized.
- `players/<active>/niksis8_character/confirmed/` — patterns in how Niklavs interacts with this character that have stabilized.
- `players/<active>/quest-log/completed/` — repeated procedures across multiple completed quests.

**Threshold.** A pattern earns a skill draft when it has repeated **≥2 times** and the agent can name it concisely. One-off patterns are not skill candidates — they may be examine drafts instead.

**Output.** Draft to `players/<active>/spellbook/skills/drafts/<slug>.md`. Skill drafts follow the same observation-rule as identity drafts: cite the specific repetitions that justified naming the pattern.

**Cap.** 0–2 skill candidates per alching pass. Skills are rare; this step is for genuine pattern-recognition, not for manufacturing skill drafts.
```

### 3c. Renumber existing step 6 → step 7

"### 6. Update `last-alched.md`" → "### 7. Update `last-alched.md`". No content change.

### 3d. Reach table update

In the "Ritual write-reach" table inside `gielinor/meta/write-rules.md` (separate file but related), the **Alching** row already says "only the active player's layers" — no change needed there; the new step 6 stays within scope.

In `gielinor/meta/modes.md`, the **Alching mode** section already enumerates `bank/`, `quest-log/`, `inventory/`, `examine/`, `niksis8_character/`, `keepsake/`. Add `spellbook/skills/` to that enumeration:

Replace:

```markdown
- Writes: proposes writes only to the active player's layers (`bank/`, `quest-log/`, `inventory/`, `examine/`, `niksis8_character/`, `keepsake/`), subject to draft-approval rules.
```

With:

```markdown
- Writes: proposes writes only to the active player's layers (`bank/`, `quest-log/`, `inventory/`, `examine/`, `niksis8_character/`, `keepsake/`, `spellbook/skills/`), subject to draft-approval rules.
```

---

## Edit 4 — per-player `bank/_about.md` updates

For each player (Jebrim today; same edit for Zezima when she has one; same template for future players).

**File:** `gielinor/players/jebrim/bank/_about.md`

### 4a. Structure section

Replace:

```markdown
## Structure

\`\`\`
bank/
  _about.md
  notes/                # the active knowledge graph
    <free subfolders by domain — reports/, queries/, pipelines/, etc.>
  archive/              # mirrors notes/
\`\`\`
```

With:

```markdown
## Structure

\`\`\`
bank/
  _about.md
  drafts/notes/         # harvest candidates + chat-initiated drafts; promoted by alching
  notes/                # the active knowledge graph (post-promotion)
    <free subfolders by domain — reports/, queries/, pipelines/, etc.>
  rejected/notes/       # drafts the principal turned down (kept; patterns matter)
  archive/              # mirrors notes/ — superseded entries
\`\`\`
```

### 4b. Write rules section

Replace:

```markdown
## Write rules

Auto-write. Jebrim writes to `bank/notes/` freely as he works. Overturning existing knowledge requires a draft in `gielinor/lorebook/drafts/`. See `gielinor/meta/write-rules.md`.
```

With:

```markdown
## Write rules

Drafts-gated as of [[D-012]] (dev brain) / 2026-05-21. Jebrim writes to `bank/drafts/notes/`; alching promotes to `bank/notes/` or rejects to `bank/rejected/notes/`. Overturning existing knowledge surfaces as a contradiction during alching review. See `gielinor/meta/write-rules.md`.
```

### 4c. Discipline section

Replace:

```markdown
- When you find a note that's contradicted by what you just learned, don't silently update — surface the contradiction as a lorebook draft if it's load-bearing, or just archive the old note if it's stale.
```

With:

```markdown
- When you find a note that's contradicted by what you just learned, write the new understanding as a fresh draft in `bank/drafts/notes/`. Alching surfaces the contradiction with the existing `bank/notes/` entry, and the principal decides whether to archive the old note or reject the draft.
```

---

## Edit 5 — per-player scaffolds (`.gitkeep` files)

For each player with a `bank/` folder:

```
gielinor/players/<name>/bank/drafts/notes/.gitkeep
gielinor/players/<name>/bank/rejected/notes/.gitkeep
gielinor/players/<name>/spellbook/skills/drafts/.gitkeep
```

Players to scaffold today: **Jebrim**. (Zezima if her bank exists; check before scaffolding.)

If `spellbook/skills/` doesn't yet exist for a player, the `drafts/.gitkeep` scaffolds the whole subtree.

---

## Edit 6 — `gielinor/lorebook/drafts/2026-05-21-harvest-pump-installation.md`

Create the file with this content:

```markdown
# 2026-05-21 — Observation harvest pump installed at close-session

## What changed

`gielinor/spellbook/rituals/close-session.md` gained a new step (step 6) that runs an observation harvest before commit. Four questions, agent-judged stability, cap 1–5 drafts, bias to less, empty-set valid. Drafts land in the appropriate per-layer `drafts/` or `proposals/` folder.

`gielinor/meta/write-rules.md` flipped the `bank/` layer from auto-write to drafts-gated. All bank-notes — harvest-derived or chat-initiated — now route through `bank/drafts/notes/` → alching promotes to `bank/notes/`. Uniform with identity-layer drafts pattern.

`gielinor/spellbook/rituals/alching.md` step 2 extended to triage `bank/drafts/notes/` before reviewing `bank/notes/` for staleness. A new step 6 added for skill graduation — walking confirmed identity layers + completed quest logs for patterns that have repeated and earned a name.

## Why

The first Jebrim alching pass (2026-05-21) executed correctly and surfaced near-empty rooms across every layer except quest-log. The procedure was right; the procedure assumed a draft pile that didn't exist.

Diagnosis: three population pumps run the brain. Pump 1 (per-turn quest-log) works. Pump 3 (per-ritual integrative: alching + bankstanding) was structurally fine but assumed Pump 2 had populated draft folders. Pump 2 (per-close harvest) didn't exist — close-session reconciled, tightened, surfaced existing drafts, committed, but never *created* drafts from session observation. Without Pump 2, the alching/bankstanding rituals found empty rooms regardless of how often they ran.

Pump 2 is the keystone. Installing it lets the rituals downstream actually do work.

## What triggered it

Concrete moment: 2026-05-21, Jebrim alching pass. Step 1 (identity drafts) found 0 in each of three folders. Step 3 (quest-log compression) found `completed/` empty. Step 5 (rejected patterns) found `rejected/` empty. The pass terminated cleanly but produced nothing. Surfaced to Niklavs as "the procedure assumed a state that didn't exist."

Niklavs cued the deeper question: "How could we actually make sure that all repos are growing organically?" The discussion produced the three-pumps frame, identified Pump 2 as the gap, and resolved into [[D-012]].

## What was affected

- `gielinor/meta/write-rules.md` (bank row flip + principle softening + enforcement note)
- `gielinor/spellbook/rituals/close-session.md` (new step 6, renumbering)
- `gielinor/spellbook/rituals/alching.md` (step 2 extension, new step 6 for skill graduation)
- `gielinor/meta/modes.md` (alching mode scope adds `spellbook/skills/`)
- Per-player `bank/_about.md` files (drafts-gate description)
- Per-player scaffolds (`bank/drafts/notes/`, `bank/rejected/notes/`, `spellbook/skills/drafts/`)

## Supersedes / superseded by

— (this is the lorebook's first entry of substance).

## Anchor

[[D-012]] in dev brain — full design rationale and alternatives considered. Decision packet: D1=A (in close-session), D2=B (player-scope first), D3=richer skim, Path 2 (one-tier bank gated), skill-graduation yes, cross-player drift deferred, cap 1–5 with bias to less.
```

(Filename: `2026-05-21-harvest-pump-installation.md` per lorebook convention — date = approval date, slug = the change.)

---

## Verification checklist for the main-brain session

After applying edits 1–6:

- [ ] `gielinor/meta/write-rules.md` shows bank as drafts-gated.
- [ ] `gielinor/spellbook/rituals/close-session.md` has 10 steps (was 9).
- [ ] `gielinor/spellbook/rituals/alching.md` has 7 steps (was 6).
- [ ] `gielinor/meta/modes.md` alching mode lists `spellbook/skills/`.
- [ ] `gielinor/players/jebrim/bank/drafts/notes/.gitkeep` exists.
- [ ] `gielinor/players/jebrim/bank/rejected/notes/.gitkeep` exists.
- [ ] `gielinor/players/jebrim/spellbook/skills/drafts/.gitkeep` exists.
- [ ] `gielinor/players/jebrim/bank/_about.md` reflects the new write rules.
- [ ] `gielinor/lorebook/drafts/2026-05-21-harvest-pump-installation.md` exists.
- [ ] Close-session is then exercised on this session — first harvest pump run is the meta-event. The harvest may itself draft an `examine/drafts/` entry observing that the procedure now produces drafts where it didn't before.

## Open questions (defer until applying)

- Should the close-session commit message format include a "Harvest: N drafts" line? Cosmetic; decide at first application.
- Should `bank/drafts/notes/` follow the same subfolder structure as `bank/notes/` (e.g., `drafts/notes/projects/<slug>.md` mirroring `notes/projects/<slug>.md`)? Suggest yes — keeps promotion a same-path move.
- Should the lorebook draft filename use today's date (when the change was decided in dev brain) or the date the main-brain session applies it? Convention in `lorebook/_about.md` says "Date is when the change was approved." The principal approved the design today; main-brain application is just execution. Keep `2026-05-21`.

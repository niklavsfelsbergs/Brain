# D-012 — 2026-05-21 — Close-session observation harvest pump + bank gate

**Context.** Jebrim's first alching pass (2026-05-21, this session) executed correctly and surfaced near-empty surface — empty `drafts/`, empty `keepsake/proposals/`, empty `completed/`, empty `rejected/`. Procedure was right; the procedure assumed a draft pile that didn't exist. Diagnosis: three population pumps run the brain. Pump 1 (per-turn quest-log) works. Pump 3 (per-ritual integrative: alching + bankstanding) works structurally but assumes Pump 2 has run. Pump 2 (per-close harvest) doesn't exist — close-session today reconciles pending actions, persists chat drafts, tightens resume sections, surfaces drafts, commits. It never asks "what did I learn?" So observations generated mid-session die in turn-log narrative or never get captured at all. Pump 2 is the keystone — without it, identity layers and bank both stay empty regardless of how often the principal runs alch.

A secondary problem surfaced once Pump 2's shape was discussed: `bank/` has been "auto-write, freely" per `write-rules.md` while the actual player practice (S001's working agreement) was "draft to chat → principal approves → write." The two patterns were in tension; the harvest pump forced the question.

**Decision.** Install **observation harvest** as a new step in `gielinor/spellbook/rituals/close-session.md`, before commit. Four-question prompt the agent runs against itself per session close. Drafts go to existing per-layer `drafts/` (or `proposals/` for keepsake) folders. Empty-set is a valid and expected common answer. Cap 1–5 drafts per close, agent judgment, bias to less-is-more.

Simultaneously, **flip `bank/` to a drafts-gated layer**. All bank-notes — harvested or chat-initiated — now route through `bank/drafts/notes/` → alch promotes to `bank/notes/<same path>` → or rejects to `bank/rejected/notes/<same path>`. One-tier bank, uniform with identity-layer pattern. Closes the loophole where bank-notes could land without principal review, at the cost of one alch cycle of latency for any new note.

Knobs settled in chat with Niklavs:

- **Pump 2 location.** Step inside `close-session.md`, not a separate `harvest.md` ritual. (D1=A.) One ritual to remember; harvest is structurally part of closing.
- **Layer routing.** Always draft player-scope first; bankstanding promotes to global when a cross-player pattern emerges. (D2=B.) Avoids premature globalization; bankstanding already has the cross-player view.
- **Harvest scope.** **Richer** skim — fresh turns added this session + resume sections of active in-progress quests. Agent judges per-item stability. (D3=richer.) Cheaper "resume-sections-only" defeats the pump; the harvest's job is converting fresh observation to durable draft, and the freshest material lives in the latest turns, not yet folded into resume sections.
- **Bank gate.** Path 2 — one-tier, drafts-gated. All bank-notes route through `bank/drafts/notes/`. The pre-existing chat-first pattern continues to discuss in chat, but the write lands in `drafts/` rather than `bank/notes/` directly.
- **Skill graduation.** In scope; extends Pump 3, not Pump 2. Alching step walks each player's `examine/confirmed/`, `niksis8_character/confirmed/`, and `quest-log/completed/` for patterns that have earned a name and repeated. Drafts to per-player `spellbook/skills/drafts/`. Detailed shape lives in the alching ritual edit, not this decision.
- **Cross-player niksis8 drift.** Deferred. Wait for Zezima activity to expose what actual contradictions look like.
- **Cap.** 1–5 drafts per harvest. Bias to less. The agent must be willing to write zero on a session where nothing earned its way.

**The four harvest questions** (canonical phrasing for the ritual edit):

1. *"Did any work crystallize into a reusable concept this session?"* → `players/<active>/bank/drafts/notes/<topic>/<slug>.md` if player-scoped. (Unscoped sessions: `players/inbox/` per bankstanding's existing triage path.)
2. *"Did I notice something about myself or how I operate?"* → `players/<active>/examine/drafts/<date>-<slug>.md`. Global only if observation is clearly cross-player and the principal cues it; otherwise player-scope per D2=B.
3. *"Did I notice something about Niklavs through this work?"* → `players/<active>/niksis8_character/drafts/<date>-<slug>.md`.
4. *"Did anything earn a pin?"* → `players/<active>/keepsake/proposals/<date>-<slug>.md`. Almost always no.

The discipline guard against drift: drafts must be **observation-backed** (per `gielinor/meta/drafts-mechanics.md`). The harvest question is not "what *could* I draft?" — it's "what did I actually observe that's worth preserving?" Empty answers stay empty.

**Alternatives considered.**

- **Separate `harvest.md` ritual that close-session calls.** Cleaner file separation, no real benefit. Rejected — one ritual per closing event keeps the trigger surface small.
- **Two-tier bank (loose `bank/notes/` + drafts-gated `bank/drafts/notes/` for harvest only).** My initial lean. The principal preferred Path 2 — full uniform gate while still calibrating what good bank-notes look like. Two-tier defers a decision; one-tier forces the calibration to happen and gives the principal a single review surface.
- **Quest-close as the only bank-note trigger.** Rejected by D3. Too many quests stay open across many sessions; we'd miss stable findings indefinitely. Session-close skim for stable items + full quest-close pass is the right split.
- **Auto-harvest cap (always 3 drafts).** Rejected. Agent judgment with bias-to-less is the discipline guard. A forced cap manufactures drafts and pollutes the rejection signal.
- **Hook-enforced bank/drafts/ gate** (like the `confirmed/` write block). Rejected for now — bank is content, not identity. Discipline-level enforcement is sufficient. Reopen if the discipline slips.
- **Harvest reads only resume sections of in-progress quests.** Rejected (D3). Resume sections are curated foreground, not raw observation stream. The freshest material — the thing the harvest exists for — sits in the latest turns.

**Consequences (main-brain edits queued; not applied from this brain).**

- `gielinor/meta/write-rules.md`: `bank/` row changes from `Auto-write: yes, freely` to `Drafts only — promotion via alching`. The "when overturning existing knowledge" exception folds into the new flow (the contradiction surfaces during alching review of `bank/drafts/notes/` against existing `bank/notes/`).
- `gielinor/spellbook/rituals/close-session.md`: new **Harvest** step before the commit step. Procedure: skim fresh turns + active-quest resume sections → ask the four harvest questions → for each yes, write to the appropriate drafts/proposals folder → cap at 5 → empty-set is valid → log one-line summary in the close output ("Harvest: N drafts across M layers" or "Harvest: empty").
- `gielinor/spellbook/rituals/alching.md`: step 2 extends — first walk `bank/drafts/notes/` to promote or reject pending entries, then review confirmed `bank/notes/` for staleness. New step (numbered between current step 5 and step 6) on **skill graduation**: walk this player's `examine/confirmed/`, `niksis8_character/confirmed/`, and `quest-log/completed/` for named-pattern candidates; draft to `players/<active>/spellbook/skills/drafts/` if a pattern has repeated and earned a name.
- Each player layer gains: `bank/drafts/notes/.gitkeep`, `bank/rejected/notes/.gitkeep`. Optional: `spellbook/skills/drafts/.gitkeep` if not already there.
- Each player's `bank/_about.md` updates to describe the new drafts gate (or a parallel doc updates if conventions live elsewhere).
- The harvest pump installing itself is a meta-observation; companion `lorebook/drafts/` entry on the gielinor side worth filing when the ritual edits land. The lorebook entry would record *why* the harvest pump exists — the first alch surfaced its absence.

**Open follow-ups (deferred).**

- **Skill-graduation procedure detail.** Yes-go signal from principal; detailed shape lives in the alching ritual edit, not D-012. Likely shape: walk confirmed identity layers + completed quest log for patterns that have repeated ≥2 times and earned a name; draft to per-player `spellbook/skills/drafts/`.
- **Cross-player niksis8 reconciliation.** Bankstanding-side problem; wait for Zezima activity to expose what the actual contradictions look like.
- **Bank-draft naming convention.** D-NNN-style stable IDs? Date prefix? Topic-slug folder structure? Settle at first harvest, not in this decision.
- **"Fresh turns" threshold.** Definitive operationalization (last close timestamp? last `## Turn log` entry? trailing N turns?) decided at first implementation.
- **Multiple active in-progress quests.** Jebrim currently has S001 (paused) + S002 (active) + S012 (this session, design). Harvest skims which? Likely "the ones touched this session" by `mtime`. Defer until it bites.
- **Stale-intent eviction at close.** Adjacent concern from D-010 — close-session could clear `.claude/intent/*.txt`. Decide alongside the close-session edits if convenient.

**Session ref.** [[S013]] (in progress, dev-brain side; named at close per `_about.md` convention). The gielinor-side activity this session (Jebrim alching + the design discussion that produced D-012) lives under gielinor's own counter, which is at S012 this session. The two brains keep independent SNNN counters per the brain-root rule.

**Related.**

- Pump definition + frame: chat content this session.
- Pattern this extends: `gielinor/meta/drafts-mechanics.md` (observation-rule, surface discipline), `gielinor/meta/write-rules.md` (layer table).
- Adjacent rituals: `gielinor/spellbook/rituals/close-session.md`, `alching.md`, `bankstanding.md`.
- Meta-observation: the first alch finding the empty room is itself the observation that justified the pump. Pattern-of-incident similar to S010's live-vs-replay miss ([[I-002]] cluster) — *the procedure was right; the procedure assumed a state that didn't exist.*

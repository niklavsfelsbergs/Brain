# D-015 — 2026-05-21 — Jebrim layer-utilization audit outcomes (layer routing + resume via inventory + skills drafts-gate)

**Context.** [[S017_d014_chat_panel_implementation]] closed with Niklavs queuing a specific handover topic: "Jebrim has done a lot of work but his `inventory/` is empty. For each apparently-underused layer, the question is binary: do we not need it, or are we just not utilizing it?" The brain has many layers per player + global, and some weren't getting used proportional to the work flowing through them. [[S018_jebrim_layer_utilization_audit]] opened in dev-brain mode (Braindead) to execute the audit.

The audit scope narrowed at [[S018_jebrim_layer_utilization_audit|S018]] T1 (via principal scoping questions): Jebrim only, main brain only, streaming findings. The reframe Niklavs supplied: "Question is if we are utilizing everything we developed or misusing something we have developed."

**Decision.** Bundle of five structural changes plus two keepsake proposals plus one file move, executed in five phases against principal ratification gates:

1. **Phase A — keepsake proposals (additive).** EU Tender 2026 and Shipping Data Mart TTYD proposed as Jebrim keepsake pins. Both qualify on the spec (load-bearing, deadlines, cross-session continuity); neither was pinned. Files in `gielinor/players/jebrim/keepsake/proposals/`. Principal pins or doesn't — user-only per write-rules.
2. **Phase B — meta + per-player `_about.md` updates.** New `gielinor/meta/layer-routing.md`. `write-rules.md` updated (skills row drafts-gated). Per-player `_about.md` updated for both Jebrim and Zezima (parity included in scope at T2): quest-log adopts quest-vs-session split, inventory promoted to primary resume surface, bank disclaims methodology, spellbook gets drafts/skills/.
3. **Phase C — file move.** `bank/drafts/notes/workflow/moving-target-work-decomposition.md` → `spellbook/drafts/skills/moving-target-decomposition.md`. Git rename. Content unchanged — the file already read as a skill description; the layer was wrong.
4. **Phase D — ritual edits.** `close-session.md` step 3 rewritten to write inventory resume files (not quest-log resume sections); step 4 reframed for quest-vs-session; step 5 hygiene split; step 8 pre-commit soft-block added. `respawn.md` steps 6.h (read inventory) and 6.i (alching threshold) added; reconciliation prompt rewritten to read from inventory; step 9 surfaces alching recommendation. `alching.md` thresholds updated to {never-alched + day-1+, >5 drafts, >20 turns, >7 days}; step 3 scoped to `completed/` only; new step 3a self-observation sweep through `in-progress/` turns since last-alched; step 6 path fixed to `spellbook/drafts/skills/`.
5. **Phase E — lorebook draft + this D-015.** `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md` for the gielinor self-improvement log; this dev-brain entry for construction history.

**Alternatives considered.**

- **Q1 — quest vs session: two-tier sessions + quests.** Considered. More honest but doubles bookkeeping (one file per session AND one file per quest). The re-trigger approach (1 file per quest, moves on quest close) achieves quest-vs-session honesty with no new files. Re-evaluate if quests start crossing too many sessions for narrative coherence in one file.
- **Q2 — inventory enforcement: discipline-only via about.md / hook-enforced / ritual-enforced.** Principal chose all three of (a) rituals carry it, (b) `meta/layer-routing.md` write, (c) close-session soft-block. Hook enforcement was the only option not taken — too brittle for "is inventory empty for this quest" check (false-positive prone). Soft-block in close-session is the cheapest place to catch the gap without blocking.
- **Q3 — collapse `bank/workflow/` into `spellbook/skills/`: keep both / collapse with lorebook-gate / collapse with per-player drafts-gate.** Principal chose collapse with per-player drafts-gate. Keeping both leaves the "is this a workflow note or a skill" ambiguity unresolved; the lorebook-gate is heavyweight for per-player methodology and creates a chokepoint at bankstanding. The drafts-gate parallels bank exactly — same mental model, alching promotes both.
- **Q4 — self-observation sweep placement: alching / close-session / both.** Principal accepted alching by implication (no pushback when proposed). Close-session would over-capture noise (per-session is too frequent); alching is the periodic deeper review where mid-session noise has settled. The sweep walks `in-progress/` turns since last-alched, not `completed/` — self-observations don't require quest-close because they're about the player, not about the work.
- **Q5 — alching thresholds: looser (never-or-time-only) / shipped numbers / tighter.** Principal chose shipped numbers. Looser misses the early-life pile-up case (Jebrim hitting day 2 with no alching is invisible without a draft-count trigger); tighter would nag too much given the early-phase brain is sparse and a >3-day quiet window is normal.
- **Pin both keepsake proposals immediately at Phase A close.** Considered. Held back — write-rules `keepsake/current.md` is user-only, and "approve" of the *proposal-write* is not the same as "pin." Principal pins on their own schedule.
- **Migrate [[S014_visualizer_polish_and_aesthetics_pass|S014]]'s existing resume sections in this session.** Considered. Held back — the migration note in close-session.md step 3 says "one-time per quest" on next close-session pass; [[S014_visualizer_polish_and_aesthetics_pass|S014]]'s migration happens organically when [[S014_visualizer_polish_and_aesthetics_pass|S014]] next closes a session. Doing it ad-hoc here would land outside any ritual and bypass the new soft-block check anyway.
- **Run cross-player parity for Zezima in a separate next-session item.** Considered (initially recommended). Principal chose to include parity in this session ("do it now while structure is fresh"). Right call — parity work is mechanical and the cost of doing it later is having Zezima's `_about.md` files quote stale rules for an unknown window.

**Consequences.**

*Files added.* `gielinor/meta/layer-routing.md` (new meta doc); `gielinor/players/jebrim/keepsake/proposals/2026-05-21_eu-tender-2026.md`; `gielinor/players/jebrim/keepsake/proposals/2026-05-21_shipping-data-mart-ttyd.md`; `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md`; this file.

*Files modified.* `gielinor/CLAUDE.md` (one `@import` added); `gielinor/meta/write-rules.md` (skills row + discipline note + cross-ref); both players' `quest-log/_about.md`, `inventory/_about.md`, `bank/_about.md`, `spellbook/_about.md`; all three global rituals (`close-session.md`, `respawn.md`, `alching.md`).

*Files moved.* `gielinor/players/jebrim/bank/drafts/notes/workflow/moving-target-work-decomposition.md` → `gielinor/players/jebrim/spellbook/drafts/skills/moving-target-decomposition.md` (git rename).

*Spec changes that propagate to all players.* The quest-vs-session split, the inventory-as-resume-surface promotion, the skills drafts-gate, and the alching-threshold updates apply to every player going forward. Jebrim and Zezima are aligned in this session; any future player must follow the new spec at scaffold time. Player-scaffold templates (if/when they exist as canonical text — they don't yet) inherit from these `_about.md` files.

*Rituals to watch.* Next close-session pass that touches an in-flight quest will exercise the new step 3 (write resume to inventory) and step 8 (soft-block check). Next respawn that finds a player with in-flight quests will exercise the new 6.h (inventory read) and 6.i (alching threshold). First alching after this commit will exercise step 3a (self-observation sweep) — bias the cap to less while we see what the sweep actually surfaces.

*Things explicitly deferred.*

- **[[S014_visualizer_polish_and_aesthetics_pass|S014]]'s migration of resume sections.** Happens on next close-session pass per the migration note. One-time.
- **Self-observation sweep tuning.** Cap is 0–3; bias to less; watch whether the sweep surfaces useful drafts or chaff.
- **Soft-block tuning.** Three options offered (write resume / commit anyway / abandon). "Abandon" may be too aggressive for a missing-file case — re-evaluate after first fire.
- **Cross-player propagation of `_about.md` patches to future players.** No template system yet; future-player scaffolding is principal work.
- **Possible `I-NNN` observation about the quest-log-as-vacuum pattern.** [[S018_jebrim_layer_utilization_audit|S018]] surfaced the pattern but the I-NNN log entry wasn't drafted in this session. Candidate for next bankstanding.

## Supersedes / superseded by

- Supersedes parts of [[D-012_close_session_harvest_pump]] — specifically, the skill-graduation routing and skill-drafts location. [[D-012_close_session_harvest_pump|D-012]] said skill drafts go to `spellbook/skills/drafts/<slug>.md` with promotion via lorebook drafts. D-015 corrects to `spellbook/drafts/skills/<slug>.md` with alching promotion (per-player, parallel to bank). The Pump 2 / Pump 3 / Pump 1 framing from [[D-012_close_session_harvest_pump|D-012]] is unchanged and stands.
- Extends [[D-012_close_session_harvest_pump]] otherwise: same harvest-pump architecture, this entry adds the resume-surface layer to the picture (inventory holds the surface; close-session writes; respawn reads).

## Anchor

- [[S018_jebrim_layer_utilization_audit]] in dev brain — the audit session, full turn log + the eight findings.
- `gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md` — the gielinor-side self-improvement log entry (principal approves to make canonical).
- `gielinor/meta/layer-routing.md` — the canonical routing table the audit produced.
- [[D-012_close_session_harvest_pump]] — the harvest-pump architecture this decision extends.

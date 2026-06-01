# Wire a harvest path: harness auto-memory → global examine/ (feeder → canonical)

> **REJECTED 2026-06-01 (B-015).** Premise false. The observation below — "global examine never written to, graduation never fires" — came from unverified Glob results; direct `ls` shows 3 prior entries and active graduation, with cross-player synthesis live at N=2. The path this proposes (graduate durable lessons to global examine) already exists and works as bankstanding step 3. Withdrawn before landing; kept per archive discipline because the failure (building on a false glob) is itself a recorded lesson — see `examine/drafts/2026-06-01-glob-results-are-claims-not-ground-truth.md`. *(Note added by Guthix at principal direction; the proposal body below is preserved unedited as the original draft.)*

## 1. Observation

Surfaced during B-015 (scoped bankstanding flipped from a Jebrim consultation, 2026-06-01; see [[G-001_2026-06-01_examine-emptiness-and-store-drift|G-001]] and `deities/guthix/bank/drafts/notes/2026-06-01-global-examine-empty-and-self-knowledge-store-drift.md`).

Cross-read, verified by direct glob:

- **Global `examine/` has never been written to.** 0 confirmed, 0 drafts, since brain birth (2026-05-20) — until this pass drafted its first entry (`examine/drafts/2026-06-01-verify-the-thing-dont-trust-the-wiring.md`).
- **The harness auto-memory (`MEMORY.md` + `memory/*.md`) is the warm store** — ~50 entries, actively appended during real work, auto-loaded into every session via system-reminder regardless of mode or actor.
- The two hold the **same kind of content** (operating lessons, user-facts) and have **drifted unsynced**. The architected layer stayed cold because it sits behind a graduation ritual that never fired; the auto-memory won on zero friction.

The cost is concrete: the "verify the thing, don't trust the wiring" principle accumulated **six instances across both stores** and was relearned per-domain for weeks because the general form had no canonical home and no path to reach one.

## 2. Proposed change

Treat the two stores as a **feeder → canonical pair**, structurally identical to the existing `research/ → bank/` pattern. Neither store is retired. Add the missing path between them.

**(a) Amend `spellbook/rituals/bankstanding.md`** — insert a new step (suggest **3b**, immediately after cross-player synthesis, since both are graduation-to-global steps):

> ### 3b. Harvest the harness auto-memory
>
> Walk `MEMORY.md` and `memory/*.md`. For each entry, decide whether it has crossed from *warm operating lesson* to *durable self-model* — recurs across domains/sessions, or names a principle broader than the incident that produced it. Propose graduations by `metadata.type`:
> - `feedback` (how the agent should work) → global `examine/drafts/`; if it's an operating *decision*, `lorebook/drafts/` instead.
> - `user` (who Niklavs is, universally) → global `niksis8/drafts/`.
> - `project` / `reference` → **stay in auto-memory** (volatile / pointer-shaped; not canonical-eligible). Route to a player's `bank/` only if clearly domain knowledge.
>
> Graduation **does not delete** the auto-memory entry — the warm copy keeps its frictionless-recall value. The `examine/`/`niksis8/` confirmed entry becomes the **canonical, citable** form; the auto-memory pointer is reconciled to reference it, not to diverge from it.

**(b) Update `meta/layer-routing.md`** — add a row: *"Operating lesson that has proven durable across domains (already warm in auto-memory) → harvest to global `examine/drafts/` during bankstanding step 3b."* And a one-line note in `meta/write-rules.md` naming the auto-memory as the warm feeder for the global identity layers.

## 3. Reasoning

- **Uses each store for its strength.** Auto-memory is frictionless and always-loaded — right for hot capture during work. Global `examine/` is gated, archived, and Obsidian-linked — right for the curated canonical self-model read at respawn. The problem was never two stores; it was no bridge.
- **Gives graduation the source it lacked.** Finding 1 (graduation never fires) has a root cause: there was nothing feeding it. Cross-player synthesis (step 3) only fires with ≥2 players carrying confirmed examine — and the corpus is lopsided to one player (Jebrim 36, Zezima 0). The auto-memory is the *actual* reservoir of cross-cutting lessons; harvesting it is what makes step 3's dormancy-at-N=1 not fatal.
- **Cost to land:** one ritual step, two doc rows. No new infrastructure, no hook, no migration of existing data (harvest runs forward from next bankstanding).

## 4. Scope of impact

- **Surfaces touched:** `spellbook/rituals/bankstanding.md` (new step), `meta/layer-routing.md` + `meta/write-rules.md` (routing notes). No hook changes. No code changes.
- **Actors:** Guthix (runs the harvest in bankstanding). No per-player actor affected.
- **Backfill:** optional one-time harvest of the current ~50 auto-memory entries at the next full bankstanding; not required for the path to work going forward.

## 5. Alternatives considered

- **Consolidate onto auto-memory, retire global `examine/`** — rejected by principal steer (B-015). Loses the draft-gate/archive discipline and Obsidian graph, and couples the self-model to the harness (migration risk per `bank/drafts/notes/2026-05-24-substrate-portability-claude-bound-vs-portable.md`).
- **Consolidate onto `examine/`, demote auto-memory to a thin index** — rejected: fights the frictionless tool that's actually working; would drift back to cold within weeks.
- **Do nothing, rely on cross-player synthesis (step 3)** — rejected: structurally dormant at N=1, and the corpus is lopsided, so it would stay dormant indefinitely.

## 6. Risk if landed wrong

- **Divergence between the two copies.** If a lesson is graduated to `examine/confirmed/` and the auto-memory copy is later edited independently, they contradict. Mitigation: graduation reconciles the auto-memory entry to *point at* the canonical form; the harvest re-checks for divergence each pass. This is the main thing to get right — it's the same seam the `research/→bank/` pattern manages, and it's manageable, but it's not free.
- **Over-harvesting.** Promoting volatile `project`/`reference` entries that don't belong canonical bloats `examine/`. Mitigation: the type-routing rubric in 3b explicitly keeps those warm-only.
- **Low blast radius overall:** forward-only, propose-then-approve gated, no destructive move. Worst case if abandoned: we're back to today's state (cold global layer), having lost nothing.

## Links

- Triggering observation: `deities/guthix/bank/drafts/notes/2026-06-01-global-examine-empty-and-self-knowledge-store-drift.md`
- Consultation trace: [[G-001_2026-06-01_examine-emptiness-and-store-drift|G-001]]
- First tenant of the cold layer (graduated this pass): `examine/drafts/2026-06-01-verify-the-thing-dont-trust-the-wiring.md`
- Inbox candidate that started it: `players/inbox/2026-06-01_examine-graduation-verify-the-thing-family.md`

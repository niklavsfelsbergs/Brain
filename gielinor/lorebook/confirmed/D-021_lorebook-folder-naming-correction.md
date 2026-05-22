# 2026-05-22 — Lorebook folder naming: `decisions/` references corrected to `confirmed/`

## What changed

Two meta docs were referencing a `lorebook/decisions/` folder that does not exist and never has. The actual structure (per `lorebook/_about.md` and the one existing canonical entry `lorebook/confirmed/D-017_user-only-with-explicit-permission.md`) is `lorebook/confirmed/`. Filename convention in use is `D-NNN_<slug>.md`, not the `YYYY-MM-DD-<slug>.md` shape that `_about.md` also documents.

**Proposed corrections (principal-only edits, since `meta/` is user-only):**

- `gielinor/meta/drafts-mechanics.md` — the line *"For `lorebook/decisions/` the equivalent is `lorebook/drafts/` → `lorebook/decisions/D-NNN_<slug>.md`."* → replace `decisions/` with `confirmed/`.
- `gielinor/meta/layer-routing.md` — the routing-table row *"Decision about how the agent operates going forward → `lorebook/drafts/` → principal approves to `lorebook/decisions/D-NNN_*.md`"* → replace `lorebook/decisions/` with `lorebook/confirmed/`.

**Filename-convention ambiguity (separate question, raised but not resolved here):** `lorebook/_about.md` describes confirmed-entry filenames as `YYYY-MM-DD-<slug>.md`, while the one existing entry uses `D-NNN_<slug>.md`. The latter is in-force; `_about.md` may want a follow-up patch to match practice (also user-only). Out of scope for this entry — flagging.

## Why

Stale docs that mis-name a load-bearing folder will mis-route the next agent that consults them. Bankstanding 2026-05-22 surfaced the inconsistency when computing where to land the three lorebook drafts pending from 2026-05-20/21. The practice (`confirmed/` + D-NNN) is what's actually in use across two ritual files and the one canonical entry; the meta-docs are the outlier.

No behavioral change implied — this is documentation aligning to existing practice, not a rule change. Logged in the lorebook anyway per principal preference (bankstanding 2026-05-22), since the lorebook is the chronological record of *all* such corrections, behavioral or not.

## What triggered it

Concrete moment: bankstanding 2026-05-22, step 2 (global identity drafts review). Surfacing the three pending `lorebook/drafts/` entries to the principal required computing where they would land on approval. Reading `meta/drafts-mechanics.md` said `lorebook/decisions/D-NNN_<slug>.md`. Reading the actual `lorebook/` showed no `decisions/` folder — only `confirmed/`, containing `D-017_user-only-with-explicit-permission.md`. Principal confirmed: docs are stale; correct them.

## What was affected

- `gielinor/meta/drafts-mechanics.md` (proposed edit; user-only).
- `gielinor/meta/layer-routing.md` (proposed edit; user-only).

## Supersedes / superseded by

— (correction of stale meta docs; not superseding any prior lorebook entry).

## Anchor

Bankstanding session 2026-05-22 chat transcript. The lorebook backlog at that moment: `2026-05-20-close-session-ritual-adoption.md`, `2026-05-21-harvest-pump-installation.md`, `2026-05-21-layer-routing-and-resume-via-inventory.md` — all referenced `lorebook/decisions/` indirectly via the meta docs at draft time; on promotion they will land in `lorebook/confirmed/` per actual practice.

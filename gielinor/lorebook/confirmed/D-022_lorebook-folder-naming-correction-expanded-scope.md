# 2026-05-22 — Lorebook folder naming: remaining `decisions/` references in `meta/`

## What changed

Follow-up to [[2026-05-22-lorebook-folder-naming-correction]] (D-021 once promoted). That entry corrected 2 of the stale `lorebook/decisions/` references in `meta/`. Bankstanding B-001 surveyed the rest of `meta/` and found **5 additional references** that still need correcting to `lorebook/confirmed/`.

**Proposed corrections (principal-only edits, since `meta/` is user-only):**

- `gielinor/meta/drafts-mechanics.md` line 3 — *"and by extension for `lorebook/decisions/` and `keepsake/` pins"* → `lorebook/confirmed/`.
- `gielinor/meta/drafts-mechanics.md` line 55 — *"`lorebook/decisions/` for the founding choice to gate identity behind drafts."* → `lorebook/confirmed/`.
- `gielinor/meta/death-and-spawn.md` line 53 — *"`lorebook/decisions/` for the choice to make confirmed/ durable…"* → `lorebook/confirmed/`.
- `gielinor/meta/modes.md` line 108 — *"Write to `lorebook/decisions/` — gnomes draft; principal canonicalizes."* → `lorebook/confirmed/`.
- `gielinor/meta/write-rules.md` lines 51 and 80 — gnome-boundary line and Related cross-ref. Both → `lorebook/confirmed/`.
- `gielinor/meta/_about.md` lines 5 and 7 — two occurrences in the "Two lifetimes" framing. Both → `lorebook/confirmed/`.

That is 9 distinct line edits across 6 files (counting the two occurrences in `_about.md` separately, and the two in `write-rules.md` separately).

## Why

The original D-021 draft caught the routing-relevant references (`drafts-mechanics.md` line 16, `layer-routing.md` line 21) — the ones the agent reads when computing where a draft lands on approval. The remaining 7 occurrences are in Related cross-references, gnome-boundary lists, and the meta `_about.md` framing. They are not load-bearing in the same way, but they are stale in the same way, and the next agent that reads them will be confused.

Bankstanding's job is exactly to surface this kind of slow drift. B-001 caught it because the global identity-drafts review forced a `grep` for the routing target.

## What triggered it

Concrete moment: bankstanding B-001, 2026-05-22, Phase 2. Surfacing `2026-05-22-lorebook-folder-naming-correction.md` to the principal, I grepped `meta/` for `lorebook/decisions` to confirm the draft's scope. Found 7 hits across 6 files, draft proposed correcting 2. Principal greenlit the follow-up.

## What was affected

- `gielinor/meta/drafts-mechanics.md` (2 additional edits proposed; user-only).
- `gielinor/meta/death-and-spawn.md` (1 edit proposed; user-only).
- `gielinor/meta/modes.md` (1 edit proposed; user-only).
- `gielinor/meta/write-rules.md` (2 edits proposed; user-only).
- `gielinor/meta/_about.md` (2 edits proposed; user-only).

## Supersedes / superseded by

Extends [[2026-05-22-lorebook-folder-naming-correction]] (D-021). Not a supersede — additive. Same correction, expanded scope.

## Anchor

Bankstanding B-001 chat transcript, 2026-05-22. Grep result: `gielinor/meta/drafts-mechanics.md:3, 55`, `gielinor/meta/death-and-spawn.md:53`, `gielinor/meta/modes.md:108`, `gielinor/meta/write-rules.md:51, 80`, `gielinor/meta/_about.md:5, 7`. Plus the original two (`drafts-mechanics.md:16`, `layer-routing.md:21`) already covered in D-021. Total = 9 occurrences across 6 files.

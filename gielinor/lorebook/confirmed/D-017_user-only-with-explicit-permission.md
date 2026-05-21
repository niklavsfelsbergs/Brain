# 2026-05-21 — "User-only" is default-no, not architectural-no

## What changed

`gielinor/meta/write-rules.md` gained a section clarifying that the "User-only" column in the write-rules table is a **default**, not an architectural prohibition. When the principal explicitly authorizes a write to `keepsake/current.md`, `meta/*.md`, or `spellbook/rituals/*.md`, the agent makes the write directly.

The five architectural guarantees in `gielinor/CLAUDE.md` (hook-enforced lines) remain non-overridable.

## Why

Without the carve-out, the principal had to manually paste the EU Tender 2026 pin text into `keepsake/current.md` because `current.md` was documented as "user-only" full stop. The friction is real and recurring: keepsake pins, mid-session rulebook clarifications, and ritual edits all involve the principal authorizing changes that the agent could execute in one step.

The architectural lines exist to prevent the agent from drifting identity or destroying state without sign-off. They are not the same shape as "this layer is user-controlled by default." Conflating them forces unnecessary copy-paste loops.

## What triggered it

S021 alching, 2026-05-21. After approving the EU Tender 2026 keepsake pin, the principal was told "pending user action: append the pin text to `current.md`." Principal: *"hmm, no, you are allowed to write there with my permission."*

The rule was applied immediately to the pin append, then surfaced as a rulebook clarification request.

## Boundary

The check is *explicit*, not inferred:

- "Yes, write it" / "go ahead, apply the fix" / "do it" in response to a specific proposal → counts.
- Ambient cooperation, agreement on the substance, or "sounds good" to general discussion → does not count.

Hook-enforced lines (no writes to `confirmed/`, no deletes, dwarf/gnome boundaries, no sub-spawn) remain architectural regardless of permission.

## What was affected

- `gielinor/meta/write-rules.md` — new section "User-only with explicit permission" added.
- This draft.

No changes to per-layer `_about.md` notes or per-file inline "user-only" markers — those reference the canonical rule; cross-reference suffices.

## Related

- [[D-012]] (dev brain) — the close-session harvest pump that established the broader "agent operates within bounded reach" pattern this clarification fits into.

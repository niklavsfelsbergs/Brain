# B-019 — bankstanding (2026-06-12): lesson-funnel reconcile

**Cue:** `hey guthix bankstand`. Single clean pass; most phases empty, work concentrated in Phase 8. Continuation of [[B-018_2026-06-11_lesson-funnel-reconcile|B-018]].

## Phases

- **Phase 0 (alch changed players):** Jebrim has changes since last-alched **but** carries in-progress quests *and* a large uncommitted promotion pile in the working tree (06-09 git-mv wave + [[S235_fcf8efd5_g1_alching|S235]] draft→confirmed moves: ~69 `D`, ~24 `??`). Skip-and-flag per the ritual — recommended a dedicated Jebrim alch + commit pass in a player session. Bankstanding can't write per-player anyway.
- **Phase 1 (inbox):** empty (archive only). No triage.
- **Phase 2 (global drafts):** `examine/`, `niksis8/`, `lorebook/`, `keepsake/proposals/` all empty. Nothing to review.
- **Phase 3 (cross-player synthesis):** dormant (N=1, only Jebrim operational).
- **Phase 4 (global budgets):** examine ~530 tok / 3k · niksis8 ~50 / 3k · keepsake ~440 / 2k — all under. No rotations.
- **Phase 5 (rejected patterns):** all global `rejected/` empty.
- **Phase 7 (lorebook):** no behavioral change. No entry.
- **Phase 8 (lesson-funnel reconcile):** the work. See below.

## Phase 8 — moves executed (principal-approved "all")

Detector (`developer-braindead/verification/lesson-store-check.py`) flagged: MEMORY.md over the 20k soft working cap, 5 index lines >200 chars, 34 examine↔MEMORY duplicates (2 unlinked).

- **A — cross-linked the 2 unlinked duplicates** (keep-both, stop divergence per [[B-015_2026-06-01_scoped-examine-graduation-and-store-drift|B-015]]):
  - `memory/feedback_qualifier_names_a_variant.md` → `[[2026-06-11-qualifier-names-a-variant-anchor-to-it]]`
  - `memory/feedback_verify_live_checkout_before_editing.md` → `[[2026-06-12-verify-which-checkout-is-live-before-editing]]`
- **B — trimmed 5 over-length MEMORY.md index lines** to the one-line rule (lines 2, 108, 109, 110, 111; two passes to clear the 200-char threshold the detector measures by Python `len`).

- **C — retired 2 graduated lessons** (principal-approved): moved `feedback_address_principal_as_you.md` + `feedback_grounding_before_advice.md` to `memory/archive/` and dropped their index lines. Both had graduated to always-on `keepsake/current.md` reflexes (Register "Address Niklavs as 'you'" + "Complete the cheap grounding precondition first"), so the warm copy was redundant. Bijection stays clean (109 topic ↔ 109 index).

**Post-state:** LINES ok; INTEGRITY ok (109/109 bijection); DRIFT 0 without cross-link (32 kept-both dupes all linked). MEMORY.md 20901 → 20311 B — **311 B over the soft working cap** still, ~4 KB under the 24.4 KB hard truncation cap. Principal scoped retirement to the 2 clearly-graduated lines; deeper retirement not pursued.

## Left for next pass

- **MEMORY.md soft-cap overage (311 B)** — clears only via further retirement (supersession judgment per line) or natural graduation. Defer to next pass; hard cap has ~4 KB headroom.
- **Jebrim uncommitted promotion pile** — commit-discipline drift across sessions; out of bankstanding lane ([[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]] sibling-sweep guard). Wants a dedicated cleanup pass.

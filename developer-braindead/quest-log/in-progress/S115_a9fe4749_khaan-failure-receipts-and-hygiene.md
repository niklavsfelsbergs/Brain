# S115 — Khaan items 2 (locked failure receipts) + 12 (engineering hygiene)

**Session:** braindead-a9fe4749 · 2026-05-28 · dev-brain via "lets develop gielinor" (mid-conversation).
**Hand-off continued:** [[S114_277d9053_khaan-audit-and-open-gate|S114]]'s ★ NEXT — Khaan-catalogue items 2 + 12 together (recommended-sequence step 1), then item 5. This session did 2 + 12; item 5 teed up, not built.

## What was asked

"Lets continue with the ideas from Khaan implementation." Grounded against the catalogue (`bank/research/2026-05-28-khaan-learnings-implementation.html`) + plan §P. Item 2 = one byte-locked failure banner per ritual, emitted verbatim + halt on any step failure, no silent fallback. Item 12 = codify atomic-write / ship-dormant / minimal-surface in `build-lessons.md`.

## Decision — ritual binding (principal, multiple-choice)

Item 2's banner doctrine needs a home + a binding into the rituals. The three agent-performed rituals (respawn, alching, drafts-triage) live in `spellbook/rituals/`, which is **user-only**. Offered three options; principal chose **"Bind into rituals"** — explicit permission for the user-only edits (the write-rules *user-only with explicit permission* path). Rationale: a doctrine file nothing points to rots (the [[S038_brain_underutilization_diagnosis|S038]] "load surfaces must match write surfaces" lesson).

## Built

1. **`gielinor/spellbook/failure-banners.md`** (NEW) — canonical registry: one byte-locked banner per ritual (respawn / alching / drafts-triage / born-link lint) + the no-silent-fallback doctrine (emit verbatim → state the failure → halt → surface; never substitute a stale/partial artifact). Notes a halt is stop-and-surface, not a lock (no anti-lockout needed — distinct from the `require-open-on-entry.py` gate, which fails open).
2. **`developer-braindead/bank/research/born-link-lint.py`** — added `BANNER` constant (the registry's born-link entry, mirrored) + emit verbatim on the block path *and* the migrate-failure path. The one banner wired into real code (enforcement, not just doctrine).
3. **3 ritual files** — one uniform **Failure handling** pointer line into `respawn.md` / `alching.md` / `drafts-triage.md`, each naming its failure modes + pointing at `spellbook/failure-banners.md`. (User-only edits, principal-approved.)
4. **`build-lessons.md`** — item 12: the three build-hygiene invariants (atomic-write all state JSON / never on a symlink; ship-dormant; minimal surface) + a substrate corollary booked from this session (see below).

## Verified (verify-enforcement-fires)

- `py_compile born-link-lint.py` OK.
- Smoke: ran `born-link-lint.py --check` on a throwaway file with `[[broken.md]]` + `[[../escape]]` → banner emitted verbatim, both links listed, **exit 1**.
- Golden (preview of item 5): asserted the `.py` `BANNER` constant == the registry's born-link code-block **byte-for-byte → MATCH**.

## Substrate catch (booked to build-lessons)

First banner used `☠` + em-dash; the Windows console codepage mangled it to `☠`/`�` on fire — defeating a *recognizable* receipt. Switched all four banners to **ASCII** (`--`, no emoji); all-caps carries the loudness. Also ASCII'd the adjacent pre-existing `COMMIT BLOCKED —` detail line (zero behavioral risk, same stderr block). Pairs with the [[S037_terminal_switchboard_phase_3_click_to_focus|S037]] ASCII-for-`.ps1` lesson. Agent-emitted markdown banners still render unicode fine — the rule is only for output crossing a Windows-console / Python-subprocess boundary.

## State / next

- plan.md §P.2 → done; §P.3 (item 5, golden-file verification harness) is NEXT — it would formalize the byte-match check done ad hoc here into `verification/check.py` per ritual.
- **Not yet committed** — awaiting principal go (ask-before-committing). Close artifacts (respawn prepend, comms CLOSING) pending at session close.
- Pending from [[S114_277d9053_khaan-audit-and-open-gate|S114]], unchanged: `meta/write-rules.md` "enforced by hook" line via godly proposal at next bankstanding.

## Targets touched (for the scoped commit)

`gielinor/spellbook/failure-banners.md` (new), `gielinor/spellbook/rituals/{respawn,alching,drafts-triage}.md`, `developer-braindead/bank/research/born-link-lint.py`, `developer-braindead/bank/build-lessons.md`, `developer-braindead/bank/plan.md`, this quest-log, `respawn.md` (prepend at close), `comms/active.md`.

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

**2+12 committed** at `8748c87` (scoped pathspec; the born-link pre-commit hook auto-wrapped + re-staged this quest-log on the way through — live confirmation the enforcement still fires).

## Then — item 5 (golden-file verification harness)

Principal chose "commit 2+12, then build item 5." Home decision (multiple-choice): **dev-brain `verification/`** — Braindead owns construction-verification, one harness spanning both vaults, keeps gielinor clean of meta-test code.

**Built `developer-braindead/verification/check.py`** — one harness, registry of code-shaped checks, runnable standalone (`python developer-braindead/verification/check.py`). Dogfoods item 2 (own locked `VERIFICATION FAILED` banner) + item 12 (ship-dormant: NOT auto-wired into pre-commit — promote when wanted).

- **C1 banner-integrity** — registry holds the 4 ritual banners; `born-link-lint.py` BANNER == its registry block byte-for-byte.
- **C2 born-link-golden** — malformed `[[x.md]]`/`[[../y]]` → block (exit 1 + banner); clean → exit 0. Fixtures **inline → tempdir** (NOT committed `.md`: the commit hook lints every staged `.md`, so a committed malformed fixture would block its own commit — the meta-trap dodged).
- **C3 write-boundaries** — the 4 sub-agent boundary hooks (dwarf/gnome/penguin/shipping-agent) each block an off-surface path (exit 2), allow an on-surface path (exit 0), stay inert on an untyped `general-purpose` spawn (exit 0 — the [[S110_144c0ca2_brain_full_audit|S110]] caveat made permanent). Payloads crafted from each hook's actual stdin contract (read the hooks first — no guessing).

**Verified BOTH ways** (the harness must fail too, not just pass): 3/3 PASS exit 0; then fault-injected a one-char drift into the born-link BANNER → C1 FAIL + `VERIFICATION FAILED` banner + exit 1 → restored (born-link-lint.py back to byte-identical, clean diff).

**Deferred:** brittle markdown-structure checks (respawn step-order, drafts-triage verdict table — break on benign reword); the born-link WRAP path (needs a resolvable mini-vault; exercised live every commit, verified S118).

## State / next

- plan.md §P.2 + §P.3 → done. Khaan recommended-sequence steps 1+2 complete.
- Pending from [[S114_277d9053_khaan-audit-and-open-gate|S114]], unchanged: `meta/write-rules.md` "enforced by hook" line via godly proposal at next bankstanding.
- Next Khaan steps (sequence step 3+): positive-gate-bundle (item 1 + H anti-lockout), 5-lens doctrine (4), scored recall/digest/charges (3/8/7). Autonomous (A/B/C…) = §C-phase, much-later.

## Targets touched

`gielinor/spellbook/failure-banners.md` (new), `gielinor/spellbook/rituals/{respawn,alching,drafts-triage}.md`, `developer-braindead/bank/research/born-link-lint.py`, `developer-braindead/bank/build-lessons.md`, `developer-braindead/bank/plan.md`, `developer-braindead/verification/check.py` (new), this quest-log, `respawn.md` (prepend at close), `comms/active.md`.

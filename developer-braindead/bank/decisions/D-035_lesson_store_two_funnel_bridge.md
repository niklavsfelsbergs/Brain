# D-035 — The two-funnel lesson-store bridge (cap + reconcile, keep both)

**Date:** 2026-06-11 · **Session:** [[S190_977f8615_lesson_store_bridge|S190]] · **Actor:** Braindead (dev-brain)

## Context

An outside-Claude review (same session, pre-pivot) flagged "three overlapping lesson stores, MEMORY.md over its cap, accumulation-without-forgetting" and recommended collapsing to one store. Grounding (`bank/research/2026-06-11-lesson-store-grounding.md`) corrected that framing on two counts:

1. It is not three flat stores. It is **two funnels** — each already internally tiered — plus a shared force-injected pin tier:
   - **Funnel A — the brain's `examine/`**: dated anchors → curated `current.md` roll-up (~3k-tok budget) → `keepsake/` pins. Gated by alching/bankstanding, archived, Obsidian-linked, **portable**. Already has a retire mechanism.
   - **Funnel B — the harness auto-memory**: `memory/*.md` topic files → `MEMORY.md` index. Always-loaded **every session and every mode** (dev-brain/Guthix included — the only store present there). Tended by **nothing** brain-side.
   - `keepsake/current.md` distils Funnel A → a designed promotion, not redundancy.
2. **The "collapse to one store" direction was already rejected** — 2026-06-01, B-015 / G-001 (`deities/guthix/proposals/rejected/2026-06-01-harvest-auto-memory-into-global-examine.md`). The steer: **keep both** (auto-memory = frictionless always-loaded warm store; examine = gated portable canonical), because consolidating onto the harness couples the self-model to Claude Code and loses the draft-gate + graph. "The problem was never two stores; it was no **bridge**." That bridge was endorsed in principle but **withdrawn on a false premise** (a bad-glob "examine is empty") and never built. The drift it named is real and ongoing — confirmed concretely: the S123 `reconcile-definition-before-numbers` lesson lived in both funnels, hand-mirrored, same `originSessionId`, zero cross-link.

## Decision — cap + reconcile, do not consolidate

Keep both funnels (honoring B-015). Give Funnel B the discipline Funnel A already has, and build the missing bridge so the two stop drifting.

1. **Acute cap fix (done).** Compressed the `MEMORY.md` index to one-rule-per-line (28.3 KB → 22.3 KB, under the ~24.4 KB load-truncation cap); detail stays in the topic files. All 104 entries preserved (index↔topic bijection verified). MEMORY.md lives outside the repo (`~/.claude/projects/.../memory/`), so it is **not** under git — the durability floor is the topic files + this detector, not version control.

2. **Detector (done).** `developer-braindead/verification/lesson-store-check.py` + `test_lesson_store_check.py` (14/14). Read-only, four checks: CAP (working + hard), over-long index lines, integrity (orphan/dangling), and **DRIFT** — a Funnel-B topic file duplicating a Funnel-A examine anchor *without* a cross-link. Exact normalized-name match = high confidence; token-overlap ≥0.6 = "likely". Live: **28 dupes (7 exact, 21 likely), 23 unlinked.** This is the enforcement backbone (hand-enforced caps drift; detectors hold) and it *produces the reconcile worklist automatically*.

3. **Reconcile model = link, don't merge (done — rulebook).** A lesson in both funnels keeps **one canonical examine anchor** + a MEMORY entry carrying the **short rule + a cross-link** to that anchor by stem. The MEMORY entry stays self-sufficient (it's the only store loaded in dev-brain/Guthix mode) but stops diverging. Codified as **`bankstanding.md` step 8** (system-scope — auto-memory is global, not player-scoped), with a non-scope pointer in `alching.md` and a `layer-routing.md` row (mirrored to `AGENTS.md` by `sync_agents_md.py`).
   - **Retirement signals are honest, not firing-telemetry.** A passive memory has no cheap "fired in N sessions" signal, so retirement is **graduation-to-keepsake** or **supersession** only — move the topic file to `memory/archive/` (never delete), drop its index line.

## Honest limits

- **DRIFT recall is a conservative floor** — name-match only. Reworded twins (e.g. MEMORY `anchor_referent_before_analyzing` ↔ examine `anchor-to-existing-state...`) evade it; the bankstanding manual scan still earns its keep.
- **The backfill is incremental, by design.** Step 8 caps at "a few per pass"; the ~27 remaining dupes reconcile across future bankstandings, not in one hand-pass (B-015: backfill is optional for the path to work). Verified the loop end-to-end on one pair (`reconcile-definition-before-numbers`: detector flipped UNLINKED → linked, unlinked 23 → 22).
- **22.3 KB under a 24.4 KB cap is a thin margin** — the durable headroom is the reconcile dedup + retirement, not the one-time trim.

## Links

- Grounding + design: `bank/research/2026-06-11-lesson-store-grounding.md`
- Prior decision (keep-both): B-015 / [[G-001_2026-06-01_examine-emptiness-and-store-drift|G-001]] + `deities/guthix/proposals/rejected/2026-06-01-harvest-auto-memory-into-global-examine.md`
- Detector: `developer-braindead/verification/lesson-store-check.py`
- Ritual: `gielinor/spellbook/rituals/bankstanding.md` step 8

# Lesson-store consolidation — grounding findings (S190, 2026-06-11)

> Grounding pass for the "lesson-store consolidation" quest (born from the 2026-06-11 outside-Claude review). **The review's framing — "collapse three overlapping stores into one" — is partly wrong and runs against a standing principal steer.** This note records what's actually on disk before any design.

## The architecture as-found — two funnels + a shared pin tier, NOT three flat stores

The review called it "three overlapping stores of the same lessons." Ground truth: it's **two parallel funnels**, each already internally tiered, plus a shared force-injected pin layer.

**Funnel A — the brain's `examine/` (player-scoped, respawn-read, gated):**
- Tier 1: `examine/confirmed/<dated>.md` anchors — full narrative. Jebrim **80**, global **5**, Zezima ~2.
- Tier 2: `examine/confirmed/current.md` — curated roll-up, **~3k-token budget**, one-liner + `→ anchor` pointer.
- Tending: **alching step 4** enforces the current.md budget → rotations to `archive/`; **bankstanding** rotates stale sections. Archive-not-delete. So Funnel A *has* a retire mechanism.

**Funnel B — the harness auto-memory (cross-everything, always-injected, model-managed):**
- Tier 1: `memory/feedback_*.md` topic files — full narrative. **104 files / 490 KB.**
- Tier 2: `MEMORY.md` index — one line per memory, **loaded every session, every mode**.
- Tending: **none brain-side.** Only the model's own write-discipline (check-before-dup, update-not-append). No archive, no cap enforcement.

**Shared pin tier — `keepsake/current.md`:** force-injected at SessionStart by `keepsake-forced-read.py`. ~5 reflexes, distilled from global `examine`. This is a **designed promotion** (examine → pin), not redundancy.

## The three REAL problems (distinct from the review's framing)

1. **The two funnels duplicate, by hand, and drift.** Same lesson lives in both, unlinked. Confirmed concretely: the S123 "reconcile-definition-before-numbers" lesson exists as `examine/confirmed/2026-05-29-reconcile-definition-before-numbers.md` AND `memory/feedback_reconcile_definition_before_numbers.md` — same `originSessionId` (4a7041b5), mirrored prose, no cross-reference. Double capture, double drift surface.
2. **MEMORY.md is over its cap right now (acute).** 28.3 KB vs 24.4 KB limit → the harness truncates it at load, so saved feedback isn't fully reaching context. Funnel B's index tier has no enforced budget; Funnel A's does (alching step 4).
3. **Funnel B has no retirement.** Both anchor piles grow unbounded, but Funnel A at least has alching/bankstanding→archive; Funnel B has nothing. The harness funnel is the unmanaged twin.

## The standing steer this quest must respect (B-015 / G-001, 2026-06-01)

This was worked **10 days ago**. `deities/guthix/quest-log/completed/G-001` + `B-015` + the **rejected** proposal `deities/guthix/proposals/rejected/2026-06-01-harvest-auto-memory-into-global-examine.md`.

- The principal's steer: **keep BOTH stores — they serve different strengths.** Auto-memory = frictionless, always-loaded (hot capture). Examine = gated, archived, Obsidian-linked, **portable/substrate-independent** (the canonical self-model). "The problem was never two stores; it was no bridge."
- Explicitly **rejected**: (a) consolidate onto auto-memory + retire examine (loses draft-gate/archive/graph; couples self-model to the harness — migration risk); (b) consolidate onto examine + demote auto-memory to a thin index (fights the frictionless tool that works; drifts cold in weeks).
- The harvest **bridge** (auto-memory → examine at bankstanding 3b) was endorsed *in principle* but **withdrawn** — only because its stated premise ("global examine empty / graduation never fires") turned out to be a bad-glob artifact. The bridge idea itself was never disqualified on merits, and **never built.**
- Note: G-001's "correction" voided all three findings together, but finding 3 (the two stores drift) was bundled with two genuinely-false glob findings and is **independently true** — the fresh S123 evidence above proves the drift continues.

## Consequence for the quest

The quest is **not** "collapse to one store" (that fights B-015). It is **"bridge + cap the two deliberately-separate funnels"**:
- (acute) bring MEMORY.md back under cap;
- (durable) give Funnel B the retirement/cap discipline Funnel A already has;
- (the never-built piece) a reconcile bridge so the two funnels stop drifting / stop double-capturing.

Design + the open fork (how much bridge vs just cap) → surfaced to Niklavs before any identity-shaped write.

## The chosen design (Niklavs: "cap + bridge", 2026-06-11) — "warm capture, canonical anchor, one reconcile"

Honors B-015 keep-both. Three parts:

1. **Funnel B stays the warm, always-loaded, self-sufficient layer.** It's the only store present in *every* mode (dev-brain included), so its entries must carry the rule, not just point at examine. But it gains Funnel A's missing discipline:
   - **Cap enforcement** — index lines trimmed to the rule (~≤180 chars); the example/anchor lives in the topic file. Brings MEMORY.md under the harness cap and keeps it there.
   - **Retirement** — *honest* signals only (no firing-telemetry; can't cheaply measure "fired in N sessions" for a passive store): retire a MEMORY line when its lesson (a) graduates to an always-on **keepsake** reflex, or (b) is **superseded/subsumed** by a newer entry. Age + redundancy, not usage.
2. **The bridge = reconcile, not merge.** A lesson in both funnels keeps **one canonical examine anchor** + a MEMORY entry carrying the short rule **and a cross-link to that anchor by slug**. Ends the divergent hand-mirrored prose (the S123 case). Drift dies; stores stay separate.
3. **Enforcement = detector + ritual, not a hook** (MEMORY is model-written, un-hookable): a **new detector file** (NOT the e6e7b78d-residue `hygiene-check.py`) flags over-cap / over-long-lines / examine↔MEMORY duplicate-without-crosslink. The **reconcile step** lands in **bankstanding** (system-scope — auto-memory is global, not player-scoped) with a light pointer from alching.

**Build order:** (1) acute MEMORY.md cap compression [authorized maintenance, no rulebook] → (2) detector [new file] → (3) bankstanding/alching reconcile step + layer-routing row [HOLD for Niklavs nod — user-only rulebook] → (4) one-time reconcile pass over the existing duplicates → (5) D-NNN + close.

# D-035 — Retire a warm MEMORY line when its lesson graduates to an always-on rule

> **Status:** draft (proposed in bankstanding [[B-020_2026-06-18_memory-cap-trim-and-graduation-retire|B-020]], 2026-06-18). Promote to `lorebook/confirmed/D-035_*.md` if it stands; add to `lorebook/_index.md` in the same pass.

## Decision

When a lesson held in the harness auto-memory (`MEMORY.md` index + `memory/*.md` topic file) **graduates to an always-on rule** — pinned as a `keepsake/current.md` reflex (force-injected every session) or written into an `@import`-ed `CLAUDE.md` / `meta/*.md` file — **retire its warm MEMORY line** (move the topic file to `memory/archive/`, drop the index line). The rule is already in context every session via the always-on surface, so the warm copy is pure redundancy paying rent against the hard cap.

This is the **active half** of the existing two-funnel reconcile (bankstanding step 8): the detector already flags caps and examine↔MEMORY drift, but retirement-on-graduation was happening only reactively at the cliff. Make it a *standing* move at every alching/bankstanding, not a cleanup that fires once the harness is already truncating.

## Why

`MEMORY.md` is always-loaded, in every mode, and **hard-capped at ~24.4 KB — past which the harness silently truncates at load** (the load-bearing copy is lost without warning). [[B-020_2026-06-18_memory-cap-trim-and-graduation-retire|B-020]] found it at 26.3 KB and *already being truncated* (the SessionStart warning confirmed "only part was loaded").

The structural cause: MEMORY grows monotonically through use (every harvested lesson adds a line), but nothing pruned it. By [[B-020_2026-06-18_memory-cap-trim-and-graduation-retire|B-020]] it held 131 entries, **76 of them in the 185–200-char band** — saturated. Trimming over-length lines to the rule bottomed out **right at the cliff** (~24.4 KB); the next memory write re-breaches. Trim alone cannot create headroom on a saturated index — only **retiring entries** can, and the cleanest, lowest-judgment tier to retire is the one that has graduated to an always-on surface (the warm line carries no information the session doesn't already load).

## How to apply

- At **alching** (per-player harvest) and **bankstanding step 8**: for each MEMORY entry, ask *"is this rule now always-on (keepsake reflex / CLAUDE / meta import)?"* If yes → retire it (archive the topic file, drop the index line). Keep the `examine/confirmed/` anchor — per [[B-015_2026-06-01_scoped-examine-graduation-and-store-drift|B-015]] the two funnels are kept *both*; this retires only the *redundant-because-always-on* warm copy, not the canonical lesson.
- Bias retirement to the **graduated** and **superseded** tiers. A lesson that is *only* in MEMORY+examine (not always-on) stays — it is still earning its warm line.
- Keep the index a clean bijection with the topic files (the detector enforces this).
- Run `developer-braindead/verification/lesson-store-check.py` after; target the **working cap (20 KB)**, not the hard cap — headroom is the point, so retirement fires before truncation, not at it.

## Trigger

Bankstanding [[B-020_2026-06-18_memory-cap-trim-and-graduation-retire|B-020]] (2026-06-18): MEMORY.md over the hard cap and actively truncating. Trim + reconcile cleared it to 23.3 KB but only ~0.5 KB headroom; reaching real headroom required retiring graduated entries (multiple-choice, copyable-deliverables → always-on `communication-protocol.md`; anchor-to-state, never-assert-absence → force-injected keepsake reflexes; content-over-verbosity → CLAUDE.md). The lesson: don't let MEMORY creep to the cliff — retire on graduation, continuously.

## Related

- [[D-032_braindead_full_access|D-032]] — the Phase-1 trim that moved several rules to JIT/always-on, creating the graduation surface this decision prunes against.
- Bankstanding step 8 (`spellbook/rituals/bankstanding.md`) and the detector `developer-braindead/verification/lesson-store-check.py` — the reconcile machinery this decision makes proactive.
- [[B-015_2026-06-01_scoped-examine-graduation-and-store-drift|B-015]] (`deities/guthix/quest-log/completed/B-015_*`) — the keep-BOTH-funnels steer this respects (retire only the redundant warm copy, never the examine anchor).

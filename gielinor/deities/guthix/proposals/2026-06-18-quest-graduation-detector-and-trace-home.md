# Proposal: quest-graduation detector + sub-agent trace home + backlog cleanup

**Drafted:** bankstanding [[B-020_2026-06-18_memory-cap-trim-and-graduation-retire|B-020]] (2026-06-18), Guthix. **Approved in-session by the principal** (approach = "Detector + trace-home + cleanup"). **Build target: dev-brain (Braindead).** Guthix proposes; the implementation is dev-brain work (detector code, ritual wiring, trace routing) — carry this into a `Lets develop gielinor` session.

## Problem

Quest promotion (`quest-log/in-progress/` → `completed/`) is **ritual discipline, not enforced**, and the ritual that does it (`close-session` step 6 / [[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]]) is skipped by fast/late-OPEN sessions that commit a footprint and stop without cueing close. Net: Jebrim's `in-progress/` holds **73 files** (2026-06-18) — ~40 stale-done (shipped + comms-CLOSING'd, never moved), ~25 sub-agent traces (no graduation path at all), a few genuinely-open umbrella quests. Same failure mode as the MEMORY.md cap this same pass: a store grown monotonically because the prune step is discipline and the discipline lapses under load. Principle adopted: **detectors hold; discipline drifts.**

## The signal already exists

`close-session` writes `open_dep: none` (or a blocker name) into each quest's `inventory/<slug>-resume__<sid8>.md` header, and that field's comment already says it "feeds [[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]] graduation." The decision data is sitting there, used only inside the ritual. The fix surfaces it *outside* the ritual.

## Part 1 (keystone) — `developer-braindead/verification/quest-graduation-check.py`

Read-only detector, mirror of `lesson-store-check.py`. For every player:
- Scan `quest-log/in-progress/*.md`. For each quest, locate its `inventory/*-resume__*.md` and read the `open_dep` header.
- **GRADUATABLE** = `open_dep: none` AND a matching comms `CLOSING` exists (cross-check `comms/active.md` + archives by sid8/SNNN). These are stale-done; should be in `completed/`.
- **NO-RESUME** = an in-progress quest with no resume file (close-session step-3 gap) — soft flag.
- **TRACE** = filename matches a sub-agent prefix (`S_shipagent_*`, `S_dwarf_*`, `penguin_*`, `recon_*`, `*_shipagent_*`, `*_dwarf_*`) — counted separately (see Part 2), excluded from the "real quest" backlog count.
- Output: per-player counts + a `--graduatable` list. Read-only; the `git mv` stays gated to close-session / gnome / principal (never the detector, never bankstanding — cross-namespace writes would fight the [[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]] parallel-safety guard).
- Caps: flag when a player's real-quest `in-progress/` exceeds ~N (start N=15, tune).

**Wiring:** call it at **respawn** (extend the existing reconciliation prompt, which clearly isn't coping at 73 — have it batch-summarize "M graduatable, K traces to archive" instead of listing every file) and surface in **bankstanding**. Optionally a `hygiene-check.py` arm.

## Part 2 (structural) — sub-agent traces get a non-quest home

Sub-agent run-logs were never quests and have no graduation path. Route them out of `in-progress/`:
- Preferred: a `quest-log/traces/` (or `quest-log/sub-agent/`) folder the dwarf/gnome/penguin/shipping-agent write boundaries point at instead of `in-progress/`, OR auto-archive a trace to `quest-log/archive/traces/` when the sub-agent returns.
- Update the four `*-write-boundary.py` hooks + `modes.md` write-surface tables + the spawn skills accordingly.
- Removes ~⅓ of the noise structurally so traces never inflate the in-progress count again.

## Part 3 (one-time) — drain the existing 73

A deliberate `close-session` pass on Jebrim (principal or gnome), **once [[S265_17290ea4_scm-resizable-columns|S265]] frees his namespace**. Its [[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]] scan auto-graduates the unambiguous shipped+committed quests as one vetoable batch; archive the ~25 sub-agent traces; leave genuine umbrella quests ([[S245_3172630e_eu-tender-no-hermes-routing-ops-coherence|S245]]/[[S248_319db0c2_ups-retention-curve|S248]]/S250) in-progress.

## Why not the alternatives (recorded for the review)

- **Enforce-at-close hook** (run [[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]] automatically on every session end): rejected as primary — a hook moving files across namespaces during parallel sessions risks the exact [[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]] clobber the guard prevents. The detector routes around the missing close-cue without that risk.
- **Just clean up**: bails water; grows back. The detector is what makes recurrence self-correcting.

## Related
- [[D-029_auto-graduate-unambiguous-complete-ready-quests]] — the in-ritual graduation this decouples from the ritual.
- `developer-braindead/verification/lesson-store-check.py` — the proven detector pattern this mirrors.
- [[B-020_2026-06-18_memory-cap-trim-and-graduation-retire|B-020]] trace + `deities/guthix/bank/drafts/notes/2026-06-18-quest-graduation-depends-on-skipped-ritual.md` — the observation behind this.
- [[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]] guard (parallel-safety: sessions don't sweep siblings) — the constraint that rules out a cross-namespace mover.

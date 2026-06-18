# B-020 — bankstanding (2026-06-18): MEMORY cap reconcile + graduation-retire

**Actor:** Guthix (bankstanding mode). **Session:** guthix-9d93fcd1. **Prior pass:** [[B-019_2026-06-12_lesson-funnel-reconcile|B-019]] (2026-06-12).

## What this pass covered

First bankstanding since [[B-019_2026-06-12_lesson-funnel-reconcile|B-019]] (6 days; a heavy week of Jebrim sessions [[S243_f6d41a0d_ups-lps-oml-2026-surcharge-export|S243]]–[[S266_e455d12d_orwo-box-grain-quota-estimator|S266]]). Globals were clean; the live problem was the harness auto-memory over its hard cap.

### Phase 0 — alching cadence
- **Jebrim: skipped (flagged).** Live sibling `jebrim-5cbb1d00` ([[S265_17290ea4_scm-resizable-columns|S265]], busy) in his namespace + multiple in-progress quests → textbook step-0 "has changes but has an in-progress quest → flag and skip." Alching mid-quest with a live sibling would collide. Recommend a dedicated Jebrim alch once [[S265_17290ea4_scm-resizable-columns|S265]] closes (last alched 2026-06-17 [[S253_5974b4ee_g1_alching|S253]], gnome g1 — 4th consecutive gnome run; the harvest wave since is large).
- **Zezima: skipped silently.** No changes since 2026-06-01 (no Zezima sessions).

### Steps 1, 2, 5 — clean
Inbox empty; all global drafts folders (`examine/`, `niksis8/`, `lorebook/`, `keepsake/proposals/`) empty; all global `rejected/` folders empty. Nothing to triage.

### Step 3 — cross-player synthesis
Gate open (N=2: both Jebrim and Zezima carry confirmed `examine/` + `niksis8_character/`), but scanned clean. The two players' `niksis8_character` observations are domain-separated by design (Jebrim = work-relationship, Zezima = personal-life) with no genuine recurrence; the one shared examine pattern (anchor-to-existing-state) is already a global keepsake reflex. **Nothing to graduate** — declined to manufacture a graduation (global `niksis8` stays thin by design, grows through real observation).

### Step 4 — global current.md size budgets
All under budget: `examine/confirmed/current.md` ~700 tok, `niksis8/confirmed/current.md` trivially thin, `keepsake/current.md` ~600 tok. No rotations. (The [[S253_5974b4ee_g1_alching|S253]] "examine current.md over-budget" leftover is Jebrim's *per-player* file — alching's job, not bankstanding's.)

### Step 8 — lesson-funnel reconcile (the substantive work)
`MEMORY.md` was **26.3 KB, over the 24.4 KB hard cap — actively truncating at load** (SessionStart warning confirmed partial load). Detector (`lesson-store-check.py`): 28 over-length index lines, 34 examine↔MEMORY duplicates (1 unlinked), integrity otherwise a clean bijection.

Two principal-approved decisions this pass:
1. **Trim + retire graduated** (first ask): trimmed all 28 over-length lines to the rule (zero info loss — detail lives in topic files + examine anchors), added the missing cross-link (`thinning-threshold` — fixed in the *topic file body*, since `_linked` reads the body not the index, and the examine anchor is `confirmed/` so unwritable by Guthix), retired 2 lines graduated to always-on `communication-protocol.md` (`multiple-choice-with-recommendation`, `copyable-deliverables-plain-text`).
2. **Retire 3 more + log discipline** (second ask, after trim-only bottomed out at the cliff): retired `anchor_referent_before_analyzing` + `never_assert_absence_against_principal_claim` (both force-injected via `keepsake/current.md` every session) + `content_over_verbosity` (in CLAUDE.md).

**Outcome:** 26.3 KB → **23.3 KB** (under hard cap, ~0.5 KB headroom), all index lines ≤200 chars, 128/128 clean bijection, 0 unlinked duplicates. 5 topic files moved to `memory/archive/` (never deleted). Detector flag dropped from OVER-HARD-CAP to the softer over-working-cap warning.

**Structural finding:** MEMORY was *saturated* — 131 entries, 76 in the 185–200-char band. Trim alone cannot create headroom on a saturated index; only retirement can. → drafted [[D-035_retire-memory-lessons-on-graduation]] making retire-on-graduation a standing alching/bankstanding discipline (target the 20 KB working cap, not the cliff).

### Step 7 — lorebook
Drafted `lorebook/drafts/D-035_retire-memory-lessons-on-graduation.md`. Awaits principal promotion → `confirmed/` + `_index.md` entry.

## Open / handed to principal
- **Promote or reject [[D-035_retire-memory-lessons-on-graduation|D-035]]** (lorebook draft).
- **Jebrim alch** is overdue-ish and was skipped (live sibling) — run once [[S265_17290ea4_scm-resizable-columns|S265]] closes.
- Real working-cap headroom (toward 20 KB) needs a larger retirement campaign someday (~15–20 graduated/superseded entries) — deferred; [[D-035_retire-memory-lessons-on-graduation|D-035]] makes it incremental instead.

## Footprint (commit at close, pathspec-scoped)
- `MEMORY.md` + `memory/archive/` (5 files moved) + `memory/feedback_thinning_threshold_regresses_sparse_case.md` (cross-link) — harness auto-memory, outside the git tree.
- `gielinor/lorebook/drafts/D-035_*.md` (new).
- `gielinor/deities/guthix/quest-log/completed/B-020_*.md` (this file) + resume + comms CLOSING.

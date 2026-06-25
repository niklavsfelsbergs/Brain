# S277 — Guthix floor-unlock for `confirmed/` writes in bankstanding (sid d371d189)

**Entered** dev-brain via "lets develop gielinor" mid-conversation — a pivot from a live Guthix bankstanding ([[B-021_2026-06-19_bankstanding|B-021]], same sid). The bankstanding itself was committed/complete (absorbed into the live ORWO session's commit `d749a4a` via a shared-index sweep — content safe, [[D-024_parallel_player_coordination|D-024]] hazard, noted not fixed).

## The ask
Principal, mid-bankstanding: *"why can't guthix act with my permission? He should be able to, i want to close everything during bankstanding."* — he wants bankstanding to close `confirmed/` promotions in-pass, not route every one to his own `git mv`.

## Diagnosis
The `confirmed/` floor (`block-confirmed-writes.py`) is a **PreToolUse hook = binary actor check** (`resolve_actor == "braindead"`). It can't read "the principal authorized this write," so gielinor [[D-034_guthix_executes_on_explicit_authorization|D-034]] gave authorized-Guthix the discipline-gated (hook-free) surfaces but kept the floor `braindead`-only. Mechanism limit, not trust limit.

## Built (principal picked: per-session unlock grant; confirmed/ writes only)
A **second bypass** in `block-confirmed-writes.py`: `actor==guthix` × `.mode∈{bankstanding,alching}` × non-empty `.claude/intent/<sid8>.floor-unlock` marker → allow, logged `bypass-guthix-authorized`. Deletes untouched (`block-deletes.py` stays braindead-only). The marker is the machine-readable authorization signal [[D-034_guthix_executes_on_explicit_authorization|D-034]] said a hook couldn't read.

Files:
- `gielinor/.claude/hooks/block-confirmed-writes.py` — bypass + `read_mode`/`floor_unlocked` helpers.
- `developer-braindead/verification/test_block_confirmed_unlock.py` — 9 cases, **live-verified from the stdin entry point** (every gate-drop blocks; player+marker blocks; draft path allowed). `run_tests.py` → **21/21 suites**.
- `gielinor/spellbook/rituals/bankstanding.md` — floor-unlock lifecycle (write-on-grant, clear-at-close, gnome-recommends/Guthix-executes).
- `gielinor/meta/write-rules.md` + `gielinor/meta/guthix.md` — floor carve-outs.
- gielinor `lorebook/confirmed/D-036_*` + `_index.md` cue row + [[D-034_guthix_executes_on_explicit_authorization|D-034]] amendment pointer.
- `developer-braindead/bank/decisions/D-036_*` — build record.

## Verification
- New hook test 9/9 live; full suite `run_tests.py` 21/21; `hygiene-check.py` Axis C (lorebook cue-index) clean; `py_compile` clean.

## Open / watch
- **First live exercise by a real guthix-actor bankstanding** — this session pivoted to Braindead, so the unlock path is test-verified but not yet run by an actual `guthix` session. Offered the principal a live test (re-enter Guthix, grant, close B-021's pending examine promotions).
- Marker clear-at-close is ritual discipline (no auto-clear hook; stale marker is sid-scoped → acceptable).
- Carried from B-021 (not this session's): jebrim quest backlog ~36 + the examine/domain-digest promotions still pending the principal/an unlocked bankstand.

## Main-brain changes.
Yes. gielinor edits: `.claude/hooks/block-confirmed-writes.py` (the bypass), `spellbook/rituals/bankstanding.md` (marker lifecycle), `meta/write-rules.md` + `meta/guthix.md` (floor carve-outs), `lorebook/confirmed/D-036` (new) + `D-034` (amendment) + `lorebook/_index.md` (cue row).

## Cascade.
None pending. The rule docs (write-rules / guthix.md / bankstanding.md / lorebook + _index) were all updated in the same pass as the hook, so no downstream doc is left to sync. `AGENTS.md` mirror (`tools/sync_agents_md.py`) covers commit policy only — unaffected. Forward: first live exercise of the unlock by a real guthix-actor bankstanding.

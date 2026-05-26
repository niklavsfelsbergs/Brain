# B-001 — first bankstanding pass

**Date opened:** 2026-05-22
**Cued by:** principal via `Hey Guthix` → `bankstand` (session dd1060c4)
**Status:** in-progress

## Phase 0 — alch changed players

**Roster:** Jebrim, Zezima. (Inbox is not a player.)

- **Jebrim.** `last-alched.md` = 2026-05-22 ([[S030_2026-05-22_dashboard-gold-cutover|S030]] alching). Many files newer than that timestamp — bank drafts, examine drafts, inventory, multiple in-progress quests ([[S031_2026-05-22_temp-tracking-missing-orderitems|S031]], [[S032_2026-05-22_bi-etl-shipping-mart-harvest|S032]], [[S033_2026-05-22_shipping-agent-audit|S033]], OPEN_shipping-agent-personal-folders, S030_g1). **Has changes AND has open in-progress work.** Per ritual rule: default is to flag to the principal and skip this round; alching a player mid-quest risks tending work that is not settled. Flagging now.
- **Zezima.** `last-alched.md` = "Never." But Zezima's tree is scaffold-only: `.gitkeep` files, the persona, CLAUDE.md, confirmed/current.md placeholders. No drafts, no quest-log entries, no bank notes. Nothing to alch. Skip silently this round; will pick up when she starts operating.

**Phase 0 outcome:** no alching performed. Principal confirmed default (skip Jebrim mid-quest). Zezima skipped silently. Flagged Jebrim for the next session-close/alching cycle once in-progress quests settle.

## Phase 1 — triage `players/inbox/`

Empty. Nothing to triage.

## Phase 2 — global identity drafts

**`examine/drafts/`:** empty.
**`niksis8/drafts/`:** empty.
**`keepsake/proposals/`:** empty.
**`lorebook/drafts/`:** 4 pending. Surfaced to principal — see turn.

**Observation while surfacing:** the 2026-05-22 lorebook-folder-naming-correction draft only proposes fixing **2 of 7** `lorebook/decisions/` references in `meta/`. Filed follow-up `2026-05-22-lorebook-folder-naming-correction-expanded-scope.md` capturing the remaining 5 file-level hits (9 total line edits across 6 files: drafts-mechanics.md lines 3+55, death-and-spawn.md, modes.md, write-rules.md ×2, _about.md ×2). Principal greenlit option 1 (approve all 4 as-is + follow-up draft).

**Proposed promotions (principal-only — `confirmed/` is hook-blocked for me):**

```
git mv gielinor/lorebook/drafts/2026-05-20-close-session-ritual-adoption.md \
       gielinor/lorebook/confirmed/D-018_close-session-ritual-adoption.md
git mv gielinor/lorebook/drafts/2026-05-21-harvest-pump-installation.md \
       gielinor/lorebook/confirmed/D-019_harvest-pump-installation.md
git mv gielinor/lorebook/drafts/2026-05-21-layer-routing-and-resume-via-inventory.md \
       gielinor/lorebook/confirmed/D-020_layer-routing-and-resume-via-inventory.md
git mv gielinor/lorebook/drafts/2026-05-22-lorebook-folder-naming-correction.md \
       gielinor/lorebook/confirmed/D-021_lorebook-folder-naming-correction.md
```

The follow-up draft `2026-05-22-lorebook-folder-naming-correction-expanded-scope.md` stays in `drafts/` until the next bankstanding (or principal pin) promotes it.

## Phase 3 — cross-player synthesis

**Population check:**

- Jebrim: 7 confirmed `examine/` entries + 3 confirmed `niksis8_character/` entries. Populated.
- Zezima: 0 confirmed entries in either layer (placeholder `current.md` only). Empty.

**Result:** cross-player promotion is **not yet possible.** A pattern that "recurs across players" requires two populated players; we have one. The integrative job is structurally unavailable this round.

Flagged for the first bankstanding after Zezima begins operating and accumulates confirmed identity entries. At that point this phase becomes productive.

## Phase 4 — global size budgets

| Layer | Size | Budget | Status |
|---|---|---|---|
| `examine/confirmed/current.md` | 345 B | ~3k tokens | well under |
| `niksis8/confirmed/current.md` | 284 B | ~3k tokens | well under |
| `keepsake/current.md` | 332 B | ~2k tokens | well under |

All three globals are essentially empty placeholders. No rotations to propose. Will become meaningful once Phase 3 starts producing graduations.

## Phase 5 — global rejected/ patterns

- `examine/rejected/`: empty.
- `niksis8/rejected/`: empty.
- `lorebook/rejected/`: empty.

No miscalibration pattern to surface. Same structural reason as Phase 3 — system is too young for rejections to have accumulated at global scope.

## Phase 6 — alching-cadence audit (post-check)

- **Jebrim** — skipped Phase 0 (mid-quest). Last alched 2026-05-22, same day. Not aging. Will pick up at next session-close + alching cycle once `S031`/`S032`/`S033`/`OPEN_*` quests settle.
- **Zezima** — skipped Phase 0 (no content). `last-alched.md` reads "Never" but threshold-fire is dampened: no drafts, no quest-log activity, no inventory motion. Re-evaluate when she starts operating.

No defensive alchings recommended.

## Phase 7 — lorebook entry for this round

**Revised mid-round.** Initial assessment: no lorebook entry warranted (round was structural triage, no behavioral change). Then during the `meta/` patch step, a PowerShell snippet I authored using `Get-Content -Raw` mangled every em-dash in 6 meta files via the Windows-1252-default footgun. Recovered via `git checkout HEAD --` then re-patched with `[System.IO.File]::ReadAllText`.

**Filed lorebook draft:** `gielinor/lorebook/drafts/2026-05-22-powershell-utf8-readall-not-getcontent.md` — system-scope behavioral rule for PowerShell snippet authoring. Observation-backed (this incident).

Round outcomes revised:
- 4 lorebook drafts promoted ([[D-018_close-session-ritual-adoption|D-018]] — [[D-021_lorebook-folder-naming-correction|D-021]]).
- 9 meta/ line edits across 6 files (lorebook/decisions/ → lorebook/confirmed/).
- 2 new lorebook drafts filed (expanded-scope follow-up; PowerShell UTF-8 rule).
- Jebrim flagged for next-cycle alching.

## Despawn

B-001 closing. Quest log moves to `completed/`. Guthix recedes.

## Summary

B-001 was structurally light because the brain is young: 1 active player, mostly-empty globals, no rejection patterns. The valuable surfacing was Phase 2 — the 4-draft lorebook backlog had been waiting for exactly this ritual to land it, and the broader doc-rot pattern (5 more `decisions/` references) only surfaced because Phase 2 forced the `grep`.

**Ritual outcome:**
- 4 lorebook drafts greenlit for principal promotion ([[D-018_close-session-ritual-adoption|D-018]] through [[D-021_lorebook-folder-naming-correction|D-021]]).
- 1 new follow-up draft filed (`lorebook-folder-naming-correction-expanded-scope`).
- Jebrim flagged for next-cycle alching.
- Zezima still in pre-operational state.

## Despawn

Closing B-001. Quest log moves to `completed/` on principal confirmation. Guthix recedes; the brain resumes its waiting.




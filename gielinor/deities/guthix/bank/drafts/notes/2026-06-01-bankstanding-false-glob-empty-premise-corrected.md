# A bankstanding built three findings on false-empty Glob results — corrected

**Observation (consultation→bankstanding, 2026-06-01, Jebrim session sid d6c2db46; [[B-015_2026-06-01_scoped-examine-graduation-and-store-drift|B-015]] / [[G-001_2026-06-01_examine-emptiness-and-store-drift|G-001]]).** This note originally asserted that global `examine/` had never been written to and that the brain's two self-knowledge stores had badly drifted. **Both claims were false** — they came from Glob calls I didn't cross-check. Keeping the corrected record because the *error* is the durable lesson.

## What was claimed vs what is true

| Claim (from Glob) | Ground truth (from `ls`) |
|---|---|
| global `examine/confirmed/` empty, "never written to" | **3** entries (2026-05-25, -29, -30); graduation fires |
| Zezima `examine/confirmed/` = 0 | **2** entries |
| cross-player synthesis dormant at N=1 | **N=2** — live |
| "architected layer cold, auto-memory won" | layer is warm-ish (3/week); the asymmetry vs auto-memory (~50) is mild *underuse*, not absence |

The only residual true observation: the self-observation corpus skews heavily to Jebrim (38 vs Zezima 2) — but that is honest usage, not a structural failure, and needs no intervention.

## The durable lesson

A `**/*.md` Glob silently skips files directly in the target directory, and an empty Glob result disagreed with `ls` even on a flat `*.md` pattern. I built an entire bankstanding — three findings plus a godly proposal — on the unverified "empty" reading. Direct `ls` voided all of it. **Cross-check any absence/count claim with a second method before reasoning on it.** Graduated as the global examine draft `2026-06-01-glob-results-are-claims-not-ground-truth.md`, child of [[2026-06-01-verify-the-thing-dont-trust-the-wiring|verify-the-thing]].

## Disposition

- Harvest godly proposal (premised on the cold layer) → withdrawn to `deities/guthix/proposals/rejected/`.
- verify-the-thing entry → kept, graduated, anchor corrected.
- This note, [[G-001_2026-06-01_examine-emptiness-and-store-drift|G-001]], [[B-015_2026-06-01_scoped-examine-graduation-and-store-drift|B-015]] → corrected to the real state.

# `git add` scoping when parallel sessions stage content

**Date:** 2026-05-22 (session [[S030_2026-05-22_dashboard-gold-cutover|S030]], dashboard gold cutover).
**Status:** draft.

## The observation

During [[S030_2026-05-22_dashboard-gold-cutover|S030]] close, the brain repo had pre-existing modifications staged by a parallel `developer-braindead/` session that Niklavs ran alongside this Jebrim session ([[D-017_user-only-with-explicit-permission|D-017]] decision, S025 dev quest log — committed in `5ec5c4c`). When the cutover quest's earlier brain commit (`c41ce97`) was staged, the `git add` was scoped to `gielinor/players/jebrim/...` and worked correctly — but the pattern of "`git add <specific>` + `git commit`" almost picked up extra parallel-session content on at least one occasion in this session, because:

- `git add <specific>` only adds the named paths, but
- `git commit` (without `--only` / `-o`) commits *everything currently staged*, including content staged by the parallel session.

The lesson: in a multi-session-on-one-repo workflow, **always run `git status` between `add` and `commit`**. Confirm the staged set matches the intent set. If parallel content is staged, decide explicitly whether to include or exclude it (`git restore --staged <path>` to exclude).

## Why it matters

- `git add -A` is already flagged across the spellbook as risky for sensitive-file inclusion. The parallel-session case is the same hazard with a different vector: even scoped `add` doesn't guarantee a scoped commit.
- The fix is cheap (one `git status` line) and surfaces parallel-session interference immediately.
- The cost of missing it is a "what is this file doing in my commit?" moment in `git log`, which is recoverable but noisy.

## Rule

In multi-session brain-repo workflows (Jebrim active + parallel dev-brain or other), the commit cadence is:

1. `git add <specific paths>`
2. `git status` — confirm staged set.
3. If unexpected content staged: `git restore --staged <path>` to remove, then back to step 2.
4. `git commit -m ...`

Already the close-session step 8 discipline ("Stage scoped. Verify with `git status` before committing.") — this draft anchors the rule to the concrete near-miss so it's harder to forget when the next parallel session lands.

## Anchor

Session [[S030_2026-05-22_dashboard-gold-cutover|S030]] (Jebrim, dashboard gold cutover). Parent quest `quest-log/completed/S030_2026-05-22_dashboard-gold-cutover.md` T6 commit-cycle + close-session brief's `git add` warning.

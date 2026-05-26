# Scope git commits with explicit pathspecs when sessions run in parallel

**Type:** operating rule (git hygiene under parallel sessions). Drafted 2026-05-23, S055 close. Confirmed 2026-05-24 (B-005 bankstanding).

**Claim.** In the shared brain working tree, a bare `git commit` (no pathspec) commits the **entire staged index** — including files that a *concurrent* session has staged but not yet committed. With multiple Claude terminals live (the norm now — see [[D-017_user-only-with-explicit-permission]], [[D-018_close-session-ritual-adoption]], [[D-024_scope-git-commits-with-pathspecs-parallel-sessions]]), this silently sweeps another actor's work into your commit.

**Anchor (verbatim sequence).** 2026-05-23, S055 Jebrim alching close. I ran `git add <jebrim paths>` then `git commit` (bare). My pre-commit check was `git diff --cached --name-status -- gielinor/players/jebrim/` — **filtered to jebrim/**, so it showed only my files and looked clean. But the concurrent Zezima S056 session had already `git mv`-staged three of its own alching promotions (`zezima/bank/notes/latvia-property/*`, `zezima/niksis8_character/confirmed/2026-05-23-home-decisions-gut-fit-veto.md`). The bare commit (`1d582c6`) took the whole index → those three Zezima files landed under a "Jebrim alching" message. No data loss; wrong attribution; not cleanly reversible while the other session is live (rewriting shared `main` history under a parallel session is riskier than the mislabel).

**Rule.**
1. Commit with **explicit pathspecs**: `git commit -- <path> [<path> …]` (or `git commit <paths>`), never a bare `git commit`, whenever parallel sessions are possible.
2. Before committing, inspect the **unfiltered** staged set: `git diff --cached --name-only` (no `-- <dir>` filter). A filtered check hides cross-session contamination — that's exactly what masked it here.
3. Prefer staging + committing only your own paths in one scoped step; don't rely on "I only added my files" — the index may already hold another session's staged work.

**Why it matters.** The brain's parallel-session model (per-session sids, comms channel, inventory suffixes) disambiguates *files*, but the **git index is shared** — it's the one place the parallelism leaks. This rule closes that gap.

**Scope.** Every actor, every session (players, Guthix, Braindead). Applies to the brain repo and any shared out-of-tree repo touched by concurrent sessions.

**Follow-up (open).** Consider a one-line cross-reference in the close-session and alching ritual docs (where commits happen). Deferred — ritual docs are user-only; raise as a godly proposal or principal edit if it proves worth wiring.

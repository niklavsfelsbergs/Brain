---
date: 2026-06-18
session: 5cbb1d00
quest: S265_scm-resizable-columns
---

# `git push` is branch-granular — a scoped commit does not scope the push

**Observation ([[S265_17290ea4_scm-resizable-columns|S265]], this session).** I committed only my 8 SCM files with explicit pathspecs ([[D-024_scope-git-commits-with-pathspecs-parallel-sessions|D-024]] discipline, clean). But when I went to push, local `main` was **3 commits** ahead of `origin/main`, not 1 — two `Topic 50` ORWO commits from a *live sibling Jebrim session* (`e455d12d`) sat *beneath* mine on the shared `main`. A normal `git push` publishes the whole branch up to the tip, so it would have published the sibling's in-progress work too. I caught it via `git rev-list --count origin/main...HEAD` showing "ahead 3" and surfaced it before pushing.

**The lesson.** [[D-024_scope-git-commits-with-pathspecs-parallel-sessions|D-024]] scopes the **commit** (pathspec → only your files land in *your* commit). It does **not** scope the **push** — push is branch-granular: it ships every commit reachable from the branch tip, including any sibling commits that are ancestors of yours on a shared branch. You cannot push "just my commit" without rewriting history (cherry-pick onto the remote tip).

**How to apply.** On a shared working tree with parallel sessions, before pushing a branch: run `git rev-list --left-right --count origin/<branch>...HEAD` (or `git log --oneline origin/<branch>..HEAD`) and read the *full* list of what will ship. If sibling commits ride along, surface them to the principal before the push — especially when push = deploy (picanova/bi-analytics). Publishing another live session's committed work is the principal's call, not a silent default.

**Also (operational, same session):** when a deploy "isn't running," it may have already *finished* — fast build-and-deploy workflows complete in a couple minutes. Check the Actions run history (API / `gh run list`) for a completed-success run on your `head_sha` before concluding it never triggered. Verified a22ca52's "Deploy Shipping Costs Dashboard" run completed-success via the Actions API, not by assuming the path filter failed.

Relates to [[2026-06-12-which-variant-anchor-to-most-recent-active]] and the [[D-024_scope-git-commits-with-pathspecs-parallel-sessions|D-024]] commit-scoping discipline.

# bi-analytics deploy topology — push to main → ECR :latest rebuild

Source: discovered S097 (2026-05-26) shipping the SCM daily_product OOM fix.

The `shipping_costs_monitoring_nextjs` DAG runs the ECR image `123038732324.dkr.ecr.eu-central-1.amazonaws.com/shipping_costs_monitoring:latest` via `KubernetesPodOperator` in namespace `pcs-dashboard`. **CI rebuilds `:latest` on push to `main`** of `github.com/picanova/bi-analytics`. (Principal confirmed: "it builds from pushing to main.")

**The three local clones are git WORKTREES of one repo, not independent clones:**
- `Documents/GitHub/bi-analytics` — branch `shipping-mart-cutover` (active SCM dev branch).
- `Documents/GitHub/bi-analytics-main` — branch `main`. Often **dirty** with the principal's WIP — do not stash/commit/merge into it.
- `Documents/GitHub/_bi-analytics-deploy` — branch `deploy-cutover-2026-05-26`. Merges *from* cutover; **not** a build trigger.

Because they share one `.git`, a branch can only be checked out in one worktree at a time (`git checkout main` from the cutover worktree fails: "already used by worktree").

**Verify the deployed code matches a ref** by comparing the crash-traceback line numbers to `git grep -n <pattern> origin/<ref> -- <file>`. S097: traceback `con.execute` at L2448 matched `origin/main` exactly → confirmed main = deployed.

**Safe deploy pattern when `main` worktree is dirty** (used S097):
1. Commit fix on `shipping-mart-cutover`.
2. `git worktree add --detach /tmp/deploy-tmp origin/main`
3. In it: `git merge shipping-mart-cutover --no-edit` → verify scope with `git diff --stat origin/main HEAD`.
4. `git push origin HEAD:main` (fast-forwards main since the merge's first parent is origin/main).
5. `git worktree remove /tmp/deploy-tmp --force`.

This never touches the dirty `main` worktree and avoids a non-ff branch push (cutover diverges from main after each merge-back). Push to main = deploy; always confirm with the principal first.

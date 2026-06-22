# The unfiltered staged-set check must be a stop-and-read step, not chained into the commit

**Observed:** S282 (`8792cd8e`), close-session commit. I knew [[D-024_scope-git-commits-with-pathspecs-parallel-sessions|D-024]] (commit with explicit pathspecs,
inspect the unfiltered staged set first), yet I ran `git add <file> && git diff --cached --name-only &&
git commit -m ...` as one chained command. The diff *did* print the sibling's pre-staged S278 deletion —
but the commit fired in the same breath, so I committed it anyway (`2e312bb`, then had to reset +
recommit with a pathspec as `fe10b05`).

**The trap:** `git add <specific file>` does **not** scope the commit — `git commit` (no pathspec) commits
the **whole index**, including anything a parallel session left staged. The safety check (`git diff
--cached`) is theater when chained with `&&` into the commit: the output scrolls past and the commit
happens regardless of what it showed.

**Rule:** Two independent guards, both required. (1) Commit **with the pathspec** — `git commit -- <paths>`
— which commits only those paths and ignores the rest of the index. (2) If inspecting the staged set, make
it a **separate tool call you actually read** before deciding to commit — never `add && diff && commit`
in one chain. The whole point of the unfiltered check is a human-in-the-loop beat; a chained command
removes the loop.

Generalizes beyond this session/player — cross-conversation memory already carries
[pathspec-commit-from-first-commit]; this adds the "don't chain the check into the commit" nuance.

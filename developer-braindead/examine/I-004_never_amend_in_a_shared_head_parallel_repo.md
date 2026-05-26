# I-004 — Never `git commit --amend` in a shared-HEAD parallel repo, even for a cosmetic fix

**Date.** 2026-05-24. **Session ref.** sid 93958e4c (token-usage audit; respawn.md collapse).

**Ruling.** When multiple dev sessions share one working tree and one branch HEAD ([[D-024_parallel_player_coordination]]), treat every commit as immutable the instant it lands. Do **not** `git commit --amend` — not for content, and not even for a cosmetic message typo. HEAD can move under you between your `git commit` and your `git commit --amend`: a sibling commits on top, and your amend silently rewrites *their* commit instead of yours. If a commit needs fixing, make a **new** commit.

**Context.** This session committed the token-audit work cleanly (`6fecbe1`), but the commit subject carried a stray `@` from a bad heredoc. I ran `git commit --amend` to fix that one cosmetic character — believing HEAD was still my commit. In the few-second window between my commit and the amend, live sibling @d82c4fbc had committed their [[S073_d82c4fbc_terminal-scroll-root-fix|S073]] cockpit work (`28d155e`) on top of mine, moving HEAD. My `--amend` therefore landed on **the sibling's** commit, overwriting their "[[S073_d82c4fbc_terminal-scroll-root-fix|S073]]: cockpit terminal scroll fix" message with my token-audit message. No content was lost (the amend keeps the tree; only message + committer change), but their commit was mislabeled and re-hashed.

Recovery was clean precisely because nothing was destroyed: the sibling's original commit was still in the **reflog** (`HEAD@{1}`), so `git commit --amend -C 28d155e` restored their exact message **and** author onto the unchanged tree (`28d155e → 19e2415`). I posted a coordination note + apology in `comms/active.md`. Total damage: one re-hash and a courtesy ping. Had I pushed before noticing, it would have been worse.

This is the live, self-inflicted instance of a hazard already on record from the other direction — Jebrim's confirmed lesson *git-add-scoping-with-parallel-sessions* (the shared **index** is also shared state). Amend is the same class of bug applied to shared **history**.

**Why.** `--amend` is defined as "rewrite whatever HEAD currently points at." That definition is safe only when you are the sole writer of HEAD. Under [[D-024_parallel_player_coordination]], HEAD is contended, so `--amend` is a read-modify-write on shared state with no lock — a textbook race. The cost of the race (clobbering a sibling's commit) dwarfs the benefit (a tidier message). A fresh commit has no such race: it only ever *adds* a node, never mutates an existing one.

**How to apply.**
- Shared-HEAD repo → **append-only git discipline.** New commits only; never `--amend`, `rebase`, or `reset --hard` on shared history.
- A message typo in a just-landed commit is not worth fixing. Leave it (the body + co-author trailer still carry the truth), or note the correction in the next commit.
- If you ever *must* rewrite, first `git rev-parse HEAD` and verify it equals the hash you intend to touch **in the same command** as the rewrite — and even then, prefer not to.
- When a sibling's commit *is* damaged, the reflog (`HEAD@{n}`) is the recovery surface: `git commit --amend -C <orig>` restores message + author from the original onto the current (identical) tree. Then post a comms note naming the old→new hash.

**Related.** [[D-024_parallel_player_coordination]] (parallel session coordination — the shared-state regime this lesson lives under), [[I-002]] (render/verify before shipping — sibling build-discipline posture), `bank/build-lessons.md` (the carried-lessons digest; the [[S038_brain_underutilization_diagnosis|S038]] "shared global state is hostile to parallel sessions" family).

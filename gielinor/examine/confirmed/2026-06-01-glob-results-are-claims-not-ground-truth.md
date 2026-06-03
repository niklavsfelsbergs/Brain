# Glob results are claims, not ground truth — cross-check corpus-state with a second method

**Claim (system-level self-model).** A "No files found" / empty Glob result is evidence, not proof, that a layer is empty. Before building any conclusion on the *absence* or *count* of files in a directory, confirm it with a second method (`ls`, `find`, `git ls-files`). This is a concrete instance of [[2026-06-01-verify-the-thing-dont-trust-the-wiring|verify-the-thing]] — the glob is the wiring; `ls` is exercising it.

**Anchor (caught live, 2026-06-01, [[B-015_2026-06-01_scoped-examine-graduation-and-store-drift|B-015]] / [[G-001_2026-06-01_examine-emptiness-and-store-drift|G-001]]).** During a scoped bankstanding, two Glob calls returned false-empty results that a direct `ls` immediately contradicted:

- `gielinor/examine/confirmed/**/*.md` → "No files found." Actual: 3 entries sitting directly in `confirmed/`. The `**/*.md` form wanted an intermediate directory and **silently skipped top-level files**.
- `gielinor/players/zezima/examine/confirmed/*.md` → "No files found." Actual: 2 entries. Even the flat `*.md` pattern disagreed with `ls` (cause not yet isolated).

On those two false readings I asserted "the global `examine/` layer has never been written to / graduation never fires / corpus lopsided to Zezima-zero," and built a three-finding bankstanding plus a godly proposal on top of it — all of which collapsed the moment I ran `ls`. The cost wasn't a wrong number; it was a whole structure of reasoning resting on an unverified tool result.

**Rule.**
- Never state "the layer is empty," "there are N entries," "this never happened," or "X was never written" from a single Glob. Cross-check with `ls -1 <dir>` or `find`/`git ls-files` first.
- Prefer flat `<dir>/*.md` over `<dir>/**/*.md` when files may live directly in the directory — and treat *any* empty result that underwrites a load-bearing conclusion as a prompt to verify, not a fact.
- The asymmetry: a *positive* glob hit is usually trustworthy; a *negative*/empty result that you're about to build on is the dangerous one. Verify the negatives.

# Don't assert disk-absence from a gitignore-aware search tool

2026-05-23 (S054, shipping-agent audit-2). I reported the shipping-agent's `workbench/`, `scratchpad/`, `memory/` folders as **empty** — a load-bearing audit finding (OK1: "the personal-folder apparatus is overkill, zero usage"). It was wrong. Those folders are gitignored, and the `Glob` tool respects `.gitignore`, so it returned "No files found" for exactly the folders that mattered. A `find` off disk showed 6 active workbench items + ~35 scratchpad files. The principal caught it ("but I do have files in workbench").

**Rule:** before asserting a path is empty/absent, confirm with a non-gitignore-aware listing (`Bash` `find`/`ls`/`Get-ChildItem`) — `Glob` (and Grep) silently skip gitignored paths. Absence reported by a gitignore-aware tool means "nothing tracked/visible," never "nothing on disk." This is the mirror of the confirmed note `verify-git-tracked-with-ls-files-not-disk-presence` (that one: don't assume disk-presence == tracked; this one: don't assume tool-absence == disk-absence).

Anchor: S054 T4 OK1 retraction.

Recurrence: S055 alching — `Glob spellbook/skills/**/*.md` returned "No files found" on a 9-file dir (brace-expansion non-match — same failure class: a search tool reporting absence that wasn't real); `find` + `git check-ignore` confirmed the files present and untracked-status irrelevant. Second occurrence → promoted.

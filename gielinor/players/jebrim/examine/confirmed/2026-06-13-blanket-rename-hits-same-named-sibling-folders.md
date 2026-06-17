# A blanket folder-rename hits same-named sibling folders elsewhere in the tree — enumerate them first

**2026-06-13 ([[S239_dc163efd_eu-tender-architecture-refactor-execution|S239]] post-close, dc163efd) — EU-tender `carriers/ → carrier_engines/` rename.**

I did a blanket `carriers/ → carrier_engines/` replace across the live `.md` docs. It correctly
rewrote the engine-package path `2_analysis/carriers/` — but it **also** rewrote
`2_analysis/docs/carriers/` → `docs/carrier_engines/`, a **different folder** (the per-carrier
narrative docs, created in P4) that I was *not* renaming. Caught it on the post-replace grep, reverted
the 7 wrong refs.

**The trap:** a folder name is rarely unique in a tree. `carriers` named the engine package AND a
`docs/carriers/` subfolder. A token-level blanket replace can't tell "the folder I'm renaming" from
"a same-named folder somewhere else." This is distinct from the P5 data-vs-module case
([[2026-06-13-plan-confirm-step-is-load-bearing]] sibling) — there the *same token* meant two things
(module vs data dir); here the *same token* names two real folders.

**The discipline:** before a blanket rename of a path token, `grep` the whole tree for every
occurrence and **enumerate the distinct folders that share the name** — rename only the target's
refs, guard the others (anchor on the full path, e.g. `2_analysis/carriers/` not bare `carriers/`,
or exclude `docs/`). Then a post-replace grep for the *wrong* form (`docs/carrier_engines`) as the
catch-net. Same lesson family as the careful targeted handling I used for `cost_matrix_2026q1`
(module vs `data/cost_matrix_2026q1/`) — when in doubt, anchor the path, don't blanket the token.

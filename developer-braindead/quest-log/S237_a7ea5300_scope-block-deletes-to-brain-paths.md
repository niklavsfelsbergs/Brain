# S237 — scope block-deletes.py to brain paths only

**sid8:** a7ea5300 · **date:** 2026-06-12 · dev-brain via "lets develop gielinor" (mid-session pivot from a Jebrim EU-tender cleanup pass, same sid).

## What

`block-deletes.py` (architectural guarantee #2) matched its DELETE_PATTERNS against the command string regardless of where the delete landed, so a `git rm` in the **bi-analytics work repo** got blocked even though no brain file was at risk (hit live this session during the tender cleanup). Added a **scope guard** after the braindead bypass, before the pattern loop: allow a delete when its effective directory is an absolute path **outside the brain** AND no absolute brain path appears in the command (the second clause closes a `cd /tmp && rm <brain-path>` leak). Effective dir = leading `cd`/`Set-Location`, else payload `cwd`, else brain root (conservative default). git-bash `/c/...` and Windows `C:\...` drive forms normalized so they compare alike. The braindead bypass and the full floor for every other actor are untouched.

## Verify

NEW `developer-braindead/verification/test_block_deletes_scope.py` — drives the real hook via stdin with a non-braindead actor (so the guard, not the bypass, is under test). **9/9**: work-repo deletes (bash `cd`, pwsh `Set-Location`, cwd-based) ALLOW; brain-path deletes (relative, absolute, git-bash `/c/`, `Remove-Item`) BLOCK. `py_compile` clean. First test suite this hook has had.

## Why now

The Jebrim session minted a standing NFE rule (commit/clean as you go); work-repo deletes will recur, so the over-broad guard would keep blocking legitimate cleanup. Scoping it removes the friction without weakening brain protection.

**Cascade.** None — the change is hook-local; no rulebook/ritual/test depends on the old over-broad behavior.
**Main-brain changes.** `gielinor/.claude/hooks/block-deletes.py` (the scope guard).

## Session shape

One session, two actors (sid a7ea5300): Jebrim did the EU-tender post-presentation cleanup (committed + pushed `c10818a..b92a110`; hand-off in [[S236_a7ea5300_eu-tender-cleanup-and-nfe-commit-rule]]) + drafted `docs/ARCHITECTURE_DISCOVERY_PLAN.md` (committed in bi-analytics, unpushed); pivoted here for the hook fix. Committed by pathspec.

## Leaving open

The architecture-discovery execution (next Jebrim session — trace the code + mine the record, ask Niklavs only the residue). Standing dev backlog unchanged: close-gate continuation false-FAIL fix, MEMORY.md trim, shipping-digest decision, Zezima bootstrap, ~6.6k CORE-thinning, Khaan item 9, 2 [[S128_b64229ad_comms-append-lock|S128]] one-liners, Jebrim quest graduation (31 in-progress).

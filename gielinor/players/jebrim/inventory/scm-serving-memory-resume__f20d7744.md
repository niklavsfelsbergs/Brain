---
quest: S146_scm-serving-memory-review
sid8: f20d7744
ts: 2026-06-02 12:40
open_dep: principal merges fix/scm-serving-memory → checks live; deploy-side env sizing (DUCKDB_MEMORY_LIMIT vs pod limit) + manifest items (volume type, probes, creds→secret) pending
---

# S146 — SCM serving-node memory review — resume

**Status:** in-progress (OOM crash-loop FIXED live; durability + optional perf-tuning + bd_cache structural fix open).

**Where we are:** Branch `fix/scm-serving-memory` (`abfbcdb`) merged + deployed (`:latest`). Confirmed LIVE via kubectl: the 502s were OOMKills (exit 137, 3 restarts, pod limit 1536Mi) — DuckDB ran on the code's 4GB default because the env var was unset. **Applied `kubectl set env DUCKDB_MEMORY_LIMIT=512MB`** → new pod 2/2 Running 0 restarts, OOM resolved. (bd_cache race did NOT fire — logs clean — it's a real but secondary issue.)

**Open items:**
- **Durability:** the `kubectl set env` lives in the cluster deployment spec (survives CI `rollout restart`) but is NOT version-controlled. To make permanent, add `ENV DUCKDB_MEMORY_LIMIT=512MB` to `docker/Dockerfile` (or the out-of-repo manifest) — offered to principal.
- **Perf tuning (if breakdown feels slow from spilling):** raise pod mem limit 1536Mi→2-3Gi AND `DUCKDB_MEMORY_LIMIT`→~1.5GB. `kubectl set env` + `kubectl set resources` (need creds + cluster access).
- **bd_cache structural fix (still queued):** per-request `db.connect()` so the temp table is connection-local — see below.

**Next concrete step (NEW, prioritized — reported live 2026-06-02):** the Breakdown tab intermittently shows no-data → "failed to load data" → works only on hard reload. Diagnosed as the **`bd_cache` shared-connection race**: `bd_cache` is one global temp table on the single shared DuckDB connection keyed by a module-global `cachedFingerprint` (`breakdown/route.ts:64`); DuckDB temp tables are connection-scoped, so concurrent/rapid breakdown requests with different filters stomp each other's `CREATE OR REPLACE` (the route already has `bd_cache does not exist` retry blocks at :700/:740 — proof it recurs). The alert→breakdown path triggers it (fires several panel fetches at once; a 2nd alert click overlaps). **This is the C2/C4 "proper" fix DEFERRED in the shipped branch — my fix only bounded the temp-table window, not the race.** Fix: give `bd_cache` a per-request identity — cleanest is a fresh `db.connect()` per request (temp tables become connection-local), or `bd_cache_<fp>` dropped after use, or inline the now-pruned glob as a CTE. Confirm via `kubectl logs deploy/shipping-costs-monitoring -n shipping-dashboard | grep bd_cache`.

**Other next step:** if it still OOMs after deploy, the likely cause is `DUCKDB_MEMORY_LIMIT` (default 4GB) > pod headroom. Get `kubectl get deploy shipping-costs-monitoring -n shipping-dashboard -o yaml | grep -A4 resources` and set `DUCKDB_MEMORY_LIMIT` ≈ pod_limit − 512MB node heap − data-volume(if memory-backed) − ~512MB overhead. Then walk the deploy-side TODO (quest §"Deploy-side TODO"). NOTE: a per-request connection (the bd_cache fix) changes memory math — each connection gets its own memory_limit budget; size threads/limit accordingly.

**Files / paths to read first:**
- `gielinor/players/jebrim/quest-log/in-progress/S146_f20d7744_scm-serving-memory-review.md` (the quest — synthesis + deploy-side TODO)
- Dwarf findings: `S146_d{1,2,3,4}_*.md` (same folder)
- Worktree/branch: `C:/Users/niklavs.felsbergs/Documents/GitHub/_scm-mem-fix` (branch `fix/scm-serving-memory`, pushed)
- `bank/notes/projects/scm_nextjs_duckdb_oom_modes.md` (now: 3 OOM modes — pipeline-RAM, pipeline-temp-spill, serving-DuckDB-native; see new draft)

**Worktree note:** the `_scm-mem-fix` worktree can be removed once the branch is merged (`git worktree remove _scm-mem-fix`). It has an `--ignore-scripts` node_modules (no duckdb native) — fine, it was only for type-checking.

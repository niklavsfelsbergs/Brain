# [[S033_2026-05-22_shipping-agent-audit|S033]] — D4 doc-sweep dwarf

**As of:** 2026-05-22
**Role:** Jebrim dwarf
**Status:** completed at [[S033_2026-05-22_shipping-agent-audit|S033]] close. No pending external actions.
**Parent session:** [[S033_2026-05-22_shipping-agent-audit|S033]] (gielinor)
**Spawn brief:** apply audit fixes B1, C1, C2, F1, F2, I1, J1, H1, and .gitignore cleanup across shipping-agent docs.

## Findings

### B1 — TCG composition alignment (Picturator + PicaAPI only; PCS removed)
- [completed] `reference/sources.md` § TCG composition — block rewritten: `TCG = Picturator + PicaAPI`; rule + filter `IN ('Picturator', 'PicaAPI')`; surface-inline example updated to "TCG = our B2C + MerchOne, excluding internal print production (PCS) and the Wolfen photo lab (ORWO)."
- [completed] `skills/query-patterns.md` — invoiced-only example: filter `IN ('Picturator', 'PicaAPI')`; comment updated.

### C1 — Document missing harness scripts (query_to_csv.py, query_to_xlsx.py)
- [completed] `README.md` Files-at-a-glance table — 2 new rows inserted (CSV runner, XLSX runner).
- [completed] `how_to.md` §10 allowed-invocations list — both scripts added; "harness in `harness/` is the workhorse" line also updated to include them + build_inline_chart.
- [completed] `how_to.md` §8 harness list — both scripts added.

### C2 — Remove Phantom Mode 4 references
- [completed] `README.md` Files-at-a-glance — removed `create_timestamped_presentation.py` row.
- [completed] `how_to.md` §8 harness list — removed `create_timestamped_presentation.py`.
- [completed] `how_to.md` §10 allowed-invocations + workhorse line — removed `create_timestamped_presentation.py` from both.

### F1 — Reduce 3 _about.md files to pointers
- [completed] `workbench/_about.md` — rewritten to ~22 lines; tier table, full per-item structure, CLAUDE.md template all dropped; pointer to §11.
- [completed] `memory/_about.md` — rewritten to ~20 lines; entry shape duplication dropped; pointer to §11.
- [completed] `scratchpad/_about.md` — rewritten to ~22 lines; tier mechanics dropped; pointer to §11.

### F2 — Compress §11 Reactive boot story
- [completed] `how_to.md` §11 — compressed from ~17 lines to 5 lines (trigger phrases, on-trigger surface, "otherwise act normally" close).

### I1 — §10 platform-neutral phrasing
- [completed] `how_to.md` §10 — `C:\`/`/c/`/`..\` enumeration replaced with "Any absolute path to the OS root (Windows `C:\`, POSIX `/`) or any parent-traversal (`..\` or `../`) is outside this folder by definition".

### J1 — Compress §10 Local-first reach + Recovery move
- [completed] `how_to.md` §10 — two multi-paragraph bullets collapsed into one tight bullet keeping the canonical-helper rule and the "fix the invocation, not the perimeter" recovery norm. Dropped `shared/` / `lib/` / `bi_etl/` / "above the folder" elaboration.

### H1 — Untrack grandfathered workbench item
- [noop] `git rm --cached -r workbench/investigations/ups-de-zv-130cm-diversion/` → `fatal: pathspec ... did not match any files`. `git ls-files workbench/` confirms only the four whitelisted entries are tracked (`_about.md`, three `.gitkeep`s). The grandfathered item is **already untracked** on this clone — either D2 handled it earlier in [[S033_2026-05-22_shipping-agent-audit|S033]], or it never actually got committed despite the audit observation. No action needed; nothing to remove.

### .gitignore cleanup
- [completed] Removed the "Scatter from pre-workbench era" block (3 entries + 2 comment lines). `scratchpad/**` covers the relocated files at their new home.

## Files touched
- `shipping-agent/how_to.md` (5 surgical edits: §8 harness list, §10 bash allowed-invocations, §10 workhorse line, §10 read/edit/write platform phrasing, §10 local-first+recovery, §11 boot story)
- `shipping-agent/README.md` (1 surgical edit: 2 rows added + 1 row removed in Files-at-a-glance)
- `shipping-agent/reference/sources.md` (1 surgical edit: §TCG composition block only; D3's source-maturity edits landed cleanly alongside)
- `shipping-agent/skills/query-patterns.md` (1 surgical edit: invoiced-only example)
- `shipping-agent/workbench/_about.md` (full rewrite, ~94 lines → ~22)
- `shipping-agent/memory/_about.md` (full rewrite, ~62 lines → ~22)
- `shipping-agent/scratchpad/_about.md` (full rewrite, ~48 lines → ~26)
- `shipping-agent/.gitignore` (1 surgical edit: removed bottom block)

## Anomalies
- **H1 no-op.** The `ups-de-zv-130cm-diversion/` folder is not in the git index, so the `git rm --cached` command returned a pathspec-not-found error. Audit observation was a stale read or D2 acted first. Surfacing for principal awareness.
- **`how_to.md` §10 workhorse line.** Found another mention of `create_timestamped_presentation.py` in §10's tail ("The harness in `harness/` is the workhorse") not called out in the brief — updated it too (removed Mode 4, added query_to_csv/xlsx + build_inline_chart). Same direction as C1+C2, just an additional site.
- **`how_to.md` §1 "Where to find things" table.** Includes a row pointing at `README.md` § Connecting that lists `harness/db.py` and `harness/connect_redshift.py` only — no mention of query_to_csv/xlsx. The query runners aren't connection-shaped so this is correct as-is, but flagging in case principal wants §1 broadened.
- **`reference/sources.md`** also modified concurrently by D3 (source-maturity table + last-verified stamp). My TCG-composition edit landed in its own block as scoped; the two dwarves did not collide.

## Returned
Principal will synthesize across all four dwarves before commit. I did not commit.

# S236 — EU tender cleanup + NFE commit rule (hand-off)

**sid8:** a7ea5300 · **player:** Jebrim · **date:** 2026-06-12
**Status:** work complete + pushed; session pivoted to dev-brain for a hook fix (note below).

## What this session did

The EU tender had just been presented (2026-06-12) but the repo was a mess. Read-pass (4 parallel Explore agents) → cleanup sequence, all in `bi-analytics-main` (pushed to origin, `c10818a..b92a110`):

1. `3a424e6` — committed the presented working tree (was 59 uncommitted, incl. the presented report `final_report_no_hermes_v2/` untracked). Folder calls: kept `final_report_no_hermes_with_gull/` as what-if; archived `final_report_v2/` + `final_report_no_hermes/` to `2_analysis/_archive/`; committed `3_UK/` + GLS comparison + rendered HTML.
2. `5c72f8b` — **new standing rule:** NFE work commits after every meaningful change (in `NFE/CLAUDE.md` + warm memory `feedback-nfe-commit-after-each-change`). Standing commit-authorization, overrides always-ask, never push, explicit pathspecs.
3. `c2f8dde` — retired `_probe_dbs*.py` to `_archive/_scratch/`.
4. `aa02ccf` — **canonical markers:** new `2_analysis/REPORTS_STATUS.md` (single source of truth: presented = `final_report_no_hermes_v2/`, €976,024/yr firm) + `_STATUS.md` stubs in the confusable folders.
5. `b92a110` — dated CURRENT-STATE banners on `docs/{PLAN,ASSUMPTIONS,NEXT,OPEN_QUESTIONS}.md` (historical bodies preserved; banners pin current truth). Verified engine versions from `carriers/*/constants.py` first.

## Verified, not assumed

- Headline €976,023.94 confirmed from `final_report/final_stats.json` `structure.base_ann`.
- 11 engines at current versions (maersk-3.2.0, hermes-2.2.0, ups-2.0.1, dpd_pl-2.0.0, …).
- Engine docs were already in order — maersk/gls CLAUDE.md already carry STALE redirect banners; dpd_pl_current already has a CLAUDE.md. (Scout findings here were wrong; verifying saved churn.)

## Deferred (with rationale — not forgotten)

- Relocating `report.py`/`migration_plan.html` out of engine dirs — skipped (marginal reuse gain, real breakage risk, don't-refactor-unasked).
- `bias_table.md` self-contradiction — it's generated; fix belongs in the generator.
- Re-rendering `management_briefing/` on UPS cascade + regenerating `switch_list_2026q1/` — analytical refreshes, not cleanup; both now marked stale/frozen via `_STATUS.md`. Do only on re-share/re-route.
- Non-tender NFE dirty files (`.claude/reference/*`, other dashboards/topics) — left for their own sessions.

## Why it pivoted to dev-brain

The brain's `block-deletes.py` hook fired on the delete verb in the bi-analytics work repo (over-broad — matches regardless of cwd). With the new "clean as you go" NFE rule, this would keep blocking legitimate work-repo deletes. Niklavs cued dev-brain to scope the hook to brain paths only. → see dev-brain quest-log for that fix.

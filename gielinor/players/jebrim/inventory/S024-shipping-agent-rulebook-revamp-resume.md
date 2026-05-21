# S024 resume — shipping-agent rulebook + structure iteration

**Status:** in-progress. The shipping-agent iteration thread is **still ongoing** — more friction will surface as real shipping-agent sessions run against the new structure.

## Where we are

Two iteration tranches landed in S025 (2026-05-22) under this quest slug:

**Tranche A — documentation split** (T13–T14). Pushed 3 commits to `bi-analytics-main`:

- `0532678` — added a thin human-onboarding `README.md`.
- `e15777a` — split `how_to.md` from 793 → 313 lines (−60%). Extracted `reference/mart-contract.md` (§1 + §3 + §4), `reference/known-dq.md` (§9), expanded `reference/sources.md` (source-maturity table), `reference/_about.md`, `skills/query-patterns.md` (§5), `skills/_about.md`. Folded §6 connection details into `README.md` § Connecting. Audience tags + per-entry `last-verified` stamps on LIVE files.
- `d0d8386` — moved 5 `.py` scripts + `sample_queries.sql` into `harness/`. Updated `BASE_DIR` to `.parent.parent` so folder-root anchoring still resolves `.env` + `visualization-studio/content/...`. Doc references updated; `.claude/settings.json` unchanged.

**Tranche B — Phase 1 from earlier in S024** (T1–T12). Mode 2 inline charts as default, §0 at nine cross-cutting rules, §10 tightened three times (T4 shell-explore ban, T8 parent-folder reach ban, T12 local-first reach + recovery rule).

The shipping-agent's structure today:

```
shipping-agent/
  README.md  how_to.md
  CLAUDE.md  AGENTS.md  GEMINI.md  GROK.md
  requirements.txt  .env  .gitignore
  harness/    db.py, connect_redshift.py, build_*.py, create_*.py, sample_queries.sql
  reference/  _about.md, mart-contract.md, sources.md, tables.md, coverage-audit.md, known-dq.md
  skills/     _about.md, query-patterns.md
  visualization-studio/  STANDARDS.md, app/, content/, lib/
  .claude/    settings.json (allow/deny patterns unchanged)
```

Each file declares audience (AI / AI + analyst / human) and stability (STABLE / LIVE). LIVE files carry `last-verified` stamps + re-verify probes.

## Next concrete step

Watch for residual friction in real shipping-agent sessions against the new structure. Specific regressions to scan for:

1. **Routing failures** (the load-bearing risk). When a new gotcha surfaces mid-session, does the agent (or you, when editing later) put it in the right file? Or does it default back to `how_to.md`? If `how_to.md` starts growing past ~400 lines again, the discipline didn't hold.
2. **Live-vs-stable contamination.** `mart-contract.md` is STABLE — if dated observations start landing in it, the separation is collapsing.
3. **Stamp drift.** LIVE entries without `last-verified` stamps. Or stamps that aren't refreshed when the entry is updated.
4. **Path anchoring failures in harness scripts.** Smoke test passed locally; any subsequent script that gets added needs `BASE_DIR = Path(__file__).resolve().parent.parent` (one parent more than the old root-level convention).
5. **Phase 1 watch-list (still live).** Pre-action narration creeping back, auto-breakouts by sub-platform, latency creep, scope-perimeter reaches (currently 3 incidents; a 4th means rewriting `.claude/settings.json` deny patterns to handle absolute paths).

When new friction surfaces, the move is the same: principal flags via screenshot, Jebrim diagnoses the root cause, proposes the targeted fix, edits.

## Files / paths to read first

- `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/how_to.md` — the always-loaded rules + the §1 "Where to find things" index.
- `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/reference/_about.md` — orientation + routing for new reference content.
- `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/skills/_about.md` — orientation + routing for new skills.
- `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/.claude/settings.json` — current deny patterns (relative-path `../**` only; would need rewriting for absolute-path catches if §10 behavioral rule fails again).

## Pending drafts

- `gielinor/players/jebrim/spellbook/drafts/skills/structural-restructure-mechanism-over-shape.md` (S025 harvest) — methodology: when restructuring, lead with mechanisms (routing, budgets, live-vs-stable, stamps, harvest) before shape. Anchor: S024 T14. Surface at next alching.

## Parked items from earlier S023 alching walk

Still untriaged from before this session. The 7-item alching proposal from post-S023 lives in [[S023-shipping-mart-coverage-audit-resume]] — re-surface when next alching runs.

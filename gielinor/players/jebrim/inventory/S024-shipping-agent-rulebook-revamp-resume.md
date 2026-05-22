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

**Tranche C — gold cutover + standalone** (T19–T21, S028, 2026-05-22). One commit to `bi-analytics-main` (`7e74670`) + one to brain (`cbf1766`). Schema cutover from `enterprise_silver.fact_*` → `shipping_mart.fact_*` across the 4 gold facts; spine + dim data denormalized into `fact_shipments` (no joins outside `shipping_mart`); standalone posture (local `.env` with `ship_mart_ro`, no walk-up, agent folder relocatable). Doc rewrites strip silver/bronze lineage (4-table scope only): `reference/sources.md`, `tables.md`, `mart-contract.md`, `coverage-audit.md`, `known-dq.md`, `skills/query-patterns.md`, `README.md`, `harness/sample_queries.sql`, `connect_redshift.py` DEFAULT_QUERY, `harness/db.py` docstring, `visualization-studio/{STANDARDS.md, lib/standards.js, app/page.js, content/light-presentation-template.json.example}`. Added §0 rule 10 (schema perimeter) + rule 11 (cost-basis disclosure / denominator matching / % invoiced reporting). Cost-vocab apply folded in (T16/T18 sharpening landed as `mart-contract.md` § Cost columns + how_to.md §0 rule 11 + worked-example block).

## Cutover applied — bi-analytics-main 7e74670 (T21, S028, 2026-05-22)

The standalone gold cutover and cost-vocab apply **landed in a single bi-analytics-main commit** (`7e74670`, pushed). The brain-side companion is `cbf1766` (this repo). Both pushed.

**What landed:** 16 files in bi-analytics-main (`.env.example` + `README.md` + `how_to.md` + `harness/{db.py,connect_redshift.py,sample_queries.sql}` + `reference/{mart-contract,tables,sources,coverage-audit,known-dq}.md` + `skills/query-patterns.md` + `visualization-studio/{STANDARDS.md,lib/standards.js,app/page.js,content/light-presentation-template.json.example}`). Net +591 / −746 lines (4-table scope is a strict simplification).

**Smoke-test baseline (verified, post-cutover):**
- Connection as `ship_mart_ro` ✓
- 4 tables in `shipping_mart`: `fact_shipments` 65 cols, `fact_shipment_cost_summary` 32, `fact_shipment_invoice_lines` 17, `fact_shipment_orderitems` 14 (128 total)
- April 2026 TCG row count: 276,490 (matches transcript's 276,483; +7 data growth)
- Invoiced-only avg cost April 2026 TCG: **€6.95 / 209,874 invoiced parcels** (vs silver-era €6.29 / ~231K — ~21K fewer invoiced parcels in gold for same slice)
- Permission denied on `enterprise_silver.fact_shipments` confirms `ship_mart_ro` boundary

## Watch points (carried forward)

The cutover apply is done; what's next is **monitoring real shipping-agent sessions** against the new structure. Specific regressions to scan for in coming sessions:

1. **`shipping_provider_group` granularity.** First post-cutover carrier-breakdown query should confirm the group field gives Niklavs the granularity he expects. If too coarse, agent may need to surface `shippingprovider_extkey` selectively. (Silver-era queries used a phantom `shippingprovider_name` that never actually existed.)
2. **Cost-basis rule firing.** The T18→T20 sharpening landed as how_to.md §0 rule 11. If a fresh cost-question transcript still produces a basis-less headline or a mismatched denominator after the apply, the wording isn't the issue — §0 rule priority/structure is. Don't redesign yet; need a real post-apply incident first.
3. **Schema-perimeter rule firing.** §0 rule 10 (no joins outside `shipping_mart`). `ship_mart_ro` enforces this at the DB layer (permission denied) — should never trip in practice, but if the agent reaches for `enterprise_silver.*` in a query, that's worth flagging as the rule not landing.
4. **The €6.95 vs €6.29 invoiced-avg shift.** Documented in commit message + T21 entry. Likely gold's invoice-matching is stricter; consumers downstream of the silver-era number may need a heads-up. Not load-bearing for the agent itself.
5. **Gold-dag ground-truth path.** Currently still at `bi-etl/dags/enterprise_silver/shipping_data_mart/` transitionally per principal (T19). Re-pin keepsake when bi-etl repoints.
6. **Routing failures.** When a new gotcha surfaces mid-session, does it land in the right post-cutover file? `mart-contract.md` STABLE, `coverage-audit.md` / `known-dq.md` LIVE with stamps. If `how_to.md` starts growing past ~400 lines, the discipline didn't hold.
7. **Live-vs-stable contamination.** `mart-contract.md` is STABLE — if dated observations start landing there, separation is collapsing.
8. **Stamp drift.** LIVE entries without `last-verified` stamps. Or stamps that don't refresh when entries update.
9. **Phase 1 watch-list (still live).** Pre-action narration creeping back, auto-breakouts by sub-platform, latency creep, scope-perimeter reaches.

When new friction surfaces, the move is the same: principal flags via screenshot, Jebrim diagnoses root cause, proposes targeted fix, edits.

## Parked ideas

- **Local-files channel for shipping-agent consumers (T17, 2026-05-22).** Multi-consumer problem: BI team pulls updates from GitHub but also needs personal rules / preferences / scratch surviving reclones. Recommended shape: `.local.md` sidecars next to each shipped `.md` (`CLAUDE.local.md` auto-loaded by directory walk; `how_to.local.md` / `notes.local.md` reference-on-demand) + `.gitignore` for `*.local.md`, `local/`, `.env`. Two undecided: ship a `CLAUDE.local.md.example` template (yes/no), and personal-rule override status (silent / agent-flagged / append-only). Working recommendation: scaffolded + silent override. Unpark when consumers signal friction from missing local channel.
- **`scope-perimeter.py` PreToolUse hook for shipping-agent (T17 discussion).** Diagnosed mid-T17: the bi-analytics-main session opens at the repo root, so default-CWD Grep calls reach outside `shipping-agent/` and trip `settings.json` allow-list prompts (`cost.*month|cost.*variation|...` screenshot). A PreToolUse hook would catch absolute-path reaches and default-CWD reaches that the relative-path deny patterns miss. Principal said "forget it" — not building now. Unpark if the prompt-fatigue from §10 / settings.json deny patterns recurs at meaningful frequency.

## Next concrete step

S024 has no further work of its own — Tranche C (the gold cutover) closed the active apply backlog. The thread stays in-progress to absorb post-cutover friction. **Wait for real shipping-agent sessions against the post-cutover structure**; route incidents per the watch points above. Adjacent thread to consider re-opening: alching to triage the S023 parked 7-item proposal + S026's two drafts + this session's outputs (keepsake proposal awaiting pin).

## Files / paths to read first

- `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/how_to.md` — the always-loaded rules + the §1 "Where to find things" index.
- `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/reference/_about.md` — orientation + routing for new reference content.
- `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/skills/_about.md` — orientation + routing for new skills.
- `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/.claude/settings.json` — current deny patterns (relative-path `../**` only; would need rewriting for absolute-path catches if §10 behavioral rule fails again).

## Pending drafts

- `gielinor/players/jebrim/spellbook/drafts/skills/structural-restructure-mechanism-over-shape.md` (S025 harvest) — methodology: when restructuring, lead with mechanisms (routing, budgets, live-vs-stable, stamps, harvest) before shape. Anchor: S024 T14. Surface at next alching.
- `gielinor/players/jebrim/bank/drafts/notes/projects/shipping_mart_cost_vocabulary_2026-05-22.md` (S024 T16/T18/T20 harvest, rewritten for gold) — durable column model for `real_shipping_cost_eur` / `expected_shipping_cost_eur` / `avg_shipping_cost_eur` / `final_shipping_cost_eur` + `cost_source` (gold values `'invoice'`/`'expected'`/`'avg'`/NULL with verified distribution), 11-bucket grain rule, % invoiced reporting rule, disclosure/denominator rules. **Proposal text already applied to shipping-agent docs (T21).** At next alching: archive the proposal section, promote the column-vocabulary remainder to `bank/notes/`.
- `gielinor/players/jebrim/keepsake/proposals/2026-05-22_shipping-data-mart-routing-post-cutover.md` (S024 T19/T20) — supersedes current `Shipping Data Mart — routing` pin in `keepsake/current.md`. Reflects 4-table scope, denormalized spine + dim, gold-verified `cost_source` distribution, schema-perimeter discipline. Awaiting principal pin into `current.md`.
- `gielinor/players/jebrim/examine/drafts/2026-05-22-bash-on-windows-quoted-path-creates-literal-filename.md` (S027 harvest) — self-observation: writing intent sidecar files with `Bash echo "..." > "C:\path\file.txt"` on Windows produces a literal filename with the colon encoded as U+F03A, not a write to the intended path. Use the Write tool or PowerShell `Set-Content` instead. Anchor: S027 stray-file incident at brain root.

## Parked items from earlier S023 alching walk

Still untriaged from before this session. The 7-item alching proposal from post-S023 lives in [[S023-shipping-mart-coverage-audit-resume]] — re-surface when next alching runs.

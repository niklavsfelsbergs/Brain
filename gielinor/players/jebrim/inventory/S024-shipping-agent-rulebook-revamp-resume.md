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

## Pending apply — standalone cutover, gold-verified (T19 + T20, 2026-05-22) — primary tranche

**Blocked on:** next session opened in `bi-analytics-main/` working dir (or worktree-equivalent). All three repos present locally; blocker is §10 perimeter discipline, not machine state.

**Scope (locked in T20).** Agent operates on **4 gold facts only** — `shipping_mart.fact_shipments`, `shipping_mart.fact_shipment_cost_summary`, `shipping_mart.fact_shipment_orderitems`, `shipping_mart.fact_shipment_invoice_lines`. No spine join (denormalized into fact). No dim join (denormalized into fact). No source-side lineage in agent docs (defer to bi-etl). No `enterprise_silver.*` references anywhere. Standalone — relocatable to any folder with its own `.env` + `harness/`.

### Apply tranche — single bi-analytics-main session, single commit

**A. Credentials + standalone.**

- Create `shipping-agent/.env` with `ship_mart_ro` creds (REDSHIFT_USER / REDSHIFT_PASSWORD). `.env.example` template alongside (no secrets).
- Verify `.gitignore` covers `.env` (already gitignored per S024 T17 discussion).
- `harness/db.py` already loads from local `.env` only via `find_dotenv()` walk — but it currently *would* walk up to `NFE/.env` if local is missing. Tighten to explicit `load_dotenv(BASE_DIR / ".env")` only — no walk-up. (Sole code change in the harness.)
- Smoke-test: `python harness/connect_redshift.py --query "SELECT 1"`.

**B. Schema flips — only the 4 facts.**

15 files reference `enterprise_silver.{fact_shipments|fact_shipment_cost_summary|fact_shipment_orderitems|fact_shipment_invoice_lines}` (16 hits total; one is historical generated query under `visualization-studio/content/generated/claude/20260522-082530--*/query.sql` — leave). Flip those 15 to `shipping_mart.*`.

**Plus** all 28 distinct `enterprise_silver.*` references across shipping-agent get stripped or replaced per the table below — not just the 4 facts. This is what "4-table scope" requires.

| Silver reference | What happens |
|---|---|
| `enterprise_silver.fact_{shipments,shipment_cost_summary,shipment_orderitems,shipment_invoice_lines}` | Rename to `shipping_mart.fact_*` |
| `enterprise_silver.map_shipment_key` | **Drop.** Data is on `shipping_mart.fact_shipments` (`source_system`, `shippingprovider_extkey`, `shop_ordernumber`, `trackingnumber`, `source_order_id`, `shop_order_created_date`). Update every query to use fact columns; drop the spine join. |
| `enterprise_silver.dim_shipping_providers` | **Drop.** Data is on `shipping_mart.fact_shipments` (`shipping_provider_id`, `shipping_provider_group` [carrier name, high-level — "DHL", "FedEx"], `shippingprovider_extkey` [service-level]). Drop the dim join; replace `d.shippingprovider_name` references with `f.shipping_provider_group`. Note: `service_type`, `truck_provider`, `has_truck_cost` are gone — confirmed not used in user-facing queries. |
| `enterprise_silver.fact_truck_charges` | **Drop.** Not in gold; internal plumbing only. Remove from presence-check queries, source-maturity tables, etc. |
| `enterprise_silver.shipping_charge_bucket_mapping` | **Drop reference.** Lineage info, not queryable. Strip from `reference/sources.md` mentions. |
| `enterprise_silver.{dhl,fedex,ups,maersk,gls,dpd,…}_invoices` (~24 carrier-specific tables) | **Drop all.** Source-side lineage tables — agent never queried them, only documented. Per principal scope: lineage defers to bi-etl docs, not agent. Strip from `reference/sources.md` and `reference/tables.md`. |
| `enterprise_silver.{pcs_orders,pcs_sentparcels,pcs_truckloads,pcs_parcel_reorder_flags,rew_orders,dpd_poland_struct,db_schenker_lines}` | **Drop all.** Same as above — source-side, not queryable from `ship_mart_ro`, not in agent scope. |

**C. Doc stripping for 4-table scope.**

- `reference/sources.md` — major rewrite. Currently documents 23 carrier-specific invoice schemas + bronze→silver pipeline per source. Strip all of this. Replace with a thin section: "The mart aggregates ~28 source-side invoice schemas via bi-etl. The agent does not query source-side tables directly — for lineage understanding, see bi-etl `dags/enterprise_silver/shipping_data_mart/`." Keep the source-systems concept (ORWO / Picturator / PicaAPI / PCS / Rewallution) since `source_system` is a column on `fact_shipments` — but document as values of the fact column, not as upstream sources.
- `reference/tables.md` — strip the `map_shipment_key`, `dim_shipping_providers`, `fact_truck_charges` sections entirely. Strip the "Sources used" / bronze-pipeline content from each fact section. Keep grain, scope, key cols, NULL semantics, gotchas for the 4 facts only.
- `reference/mart-contract.md` — STABLE contract for the 4 facts. Add the new cost-columns subsection (per cost-vocab §A, rewritten in T20). Drop any pipeline / lineage references.
- `reference/coverage-audit.md` — review for silver references; flip / drop as needed. The coverage matrix itself stays (covers the 4 facts).
- `reference/known-dq.md` — same review pass.
- `skills/query-patterns.md` — drop the spine + dim join example; replace with a 4-fact join pattern (typical `fact_shipments` ⟕ `fact_shipment_cost_summary` ⟕ `fact_shipment_orderitems`).
- `harness/sample_queries.sql` — rewrite all 5 sample queries. Drop presence-check on `fact_truck_charges`/`map_shipment_key`/`dim_shipping_providers`. Update query 2 to use `fact_shipments.source_system` directly. Update query 3 to use `fact_shipments.shipping_provider_group`. Remove obsolete NOTE about `real_shipping_cost_eur` being NULL (no longer true).
- `harness/db.py` — update the example docstring SQL from `SELECT * FROM enterprise_silver.fact_shipments LIMIT 10` to `SELECT * FROM shipping_mart.fact_shipments LIMIT 10`.
- `README.md` § Connecting — rewrite for new `ship_mart_ro` local-`.env` flow. Strip three `enterprise_silver.` references.
- `visualization-studio/STANDARDS.md` and `lib/standards.js` and `app/page.js` — update silver references.

**D. Standalone severance.**

- `how_to.md` §10 — drop any caveat exempting credential walk-up. With local `.env` and the tightened `db.py`, §10 is literally true.
- `how_to.md` and `README.md` — drop the older NFE-side reference pointer (`bi-analytics-main/NFE/.claude/reference/shipping-data-mart/`). Relocatable goal forbids external dependencies.

**E. Schema-perimeter rule (§0 new cross-cutting).**

Add a new numbered §0 rule:

> **N. Schema perimeter — `shipping_mart` only.** All queries qualify as `shipping_mart.<table>` (never assume `search_path` defaults). The agent's surface is the 4 facts: `fact_shipments`, `fact_shipment_cost_summary`, `fact_shipment_orderitems`, `fact_shipment_invoice_lines`. Reaching for `enterprise_silver.*`, `enterprise_bronze.*`, or any other schema is a scope violation (and `ship_mart_ro` would deny it anyway). For source/lineage understanding, defer to bi-etl docs — not in agent scope. Future extension to raw invoices may broaden scope; if so, it lands as an explicit rule change, not ad-hoc reach.

**F. Cost-vocab doc edits (T16/T18/T20 rewrite, folded into same commit).**

Three insertions (text in `bank/drafts/notes/projects/shipping_mart_cost_vocabulary_2026-05-22.md` post-T20 rewrite):

1. **`reference/mart-contract.md` § Cost columns — invoiced vs expected vs final.** Source: §A of cost-vocab draft. Includes the cost-columns table, the `cost_source` distribution table (verified 2026-05-22), When-to-use list, and cost-bucket grain section (11 buckets named directly, tax+customs excluded from total_eur). Qualify table names as `shipping_mart.fact_*`. Mark LIVE, `last-verified: 2026-05-22`.
2. **`how_to.md` §0 cost-rule.** Source: §B of cost-vocab draft (~180 words). Five sub-rules: state basis upfront, match denominators to numerators, default to invoiced-only headline, report % invoiced euro-weighted, flag bucket breakdowns as invoiced-only. Uses `cost_source = 'invoice'` (not `'real'`).
3. **Worked-example block.** Fold into `reference/mart-contract.md` or `skills/query-patterns.md`. Three SQL patterns showing wrong vs right denominators for "avg shipping cost per parcel" (€5.24 wrong / €6.29 invoiced-only / €X population-weighted), using `shipping_mart.*` qualification and `cost_source = 'invoice'`.

### Smoke tests (post-apply)

- **Connection:** `python harness/connect_redshift.py --query "SELECT 1"` — returns 1 row.
- **Schema sanity (4 tables present):** `python harness/connect_redshift.py --query "SELECT table_name, COUNT(*) AS col_count FROM information_schema.columns WHERE table_schema = 'shipping_mart' GROUP BY 1 ORDER BY 1"` — returns the 4 fact tables with their column counts (fact_shipments: 66, fact_shipment_cost_summary: 32, fact_shipment_invoice_lines: 17, fact_shipment_orderitems: 13).
- **April 2026 TCG row count:** `python harness/connect_redshift.py --query "SELECT COUNT(*) FROM shipping_mart.fact_shipments WHERE shop_order_created_date >= DATE '2026-04-01' AND shop_order_created_date < DATE '2026-05-01' AND source_system IN ('Picturator', 'PicaAPI', 'PCS')"` — should match S027's ~276K TCG-April figure.
- **Cost-basis re-run of the T18 anchor:** `python harness/connect_redshift.py --query "SELECT SUM(real_shipping_cost_eur) / NULLIF(COUNT(*), 0) AS avg_invoiced_eur FROM shipping_mart.fact_shipments WHERE shop_order_created_date >= DATE '2026-04-01' AND shop_order_created_date < DATE '2026-05-01' AND source_system IN ('Picturator', 'PicaAPI', 'PCS') AND cost_source = 'invoice'"` — should match the €6.29 figure (within rounding).
- **Schema-perimeter probe:** `python harness/connect_redshift.py --query "SELECT 1 FROM enterprise_silver.fact_shipments LIMIT 1"` — should return permission-denied. Confirms `ship_mart_ro` boundary.

### What this tranche does NOT include

- Locating the gold-dag ground-truth path in bi-etl. The repoint is in flight per principal; path stays at `bi-etl/dags/enterprise_silver/shipping_data_mart/` until the move. Re-pin the keepsake when the path moves.
- Future extension to raw-invoice access. Out of scope per principal — "maybe in the future."
- A `MUST` block / pre-query checklist for the cost-vocab rule, even though T18 flagged it. Wait for post-apply real incident before redesigning §0's structure.

### Brain-side outputs landed (S028)

- `bank/drafts/notes/projects/shipping_mart_cost_vocabulary_2026-05-22.md` — full rewrite for gold (T20).
- `players/jebrim/keepsake/proposals/2026-05-22_shipping-data-mart-routing-post-cutover.md` — tightened with 4-table scope + denormalization confirmation (T20).
- S024 quest log T19 (proposal) + T20 (verification + scope narrowing).
- This inventory section.

### Open question deferred (not blocking apply)

- Will `shipping_provider_group` give Niklavs the carrier-breakdown granularity he typically wants? Sample queries previously used `dim_shipping_providers.shippingprovider_name` (phantom column — never existed). Best guess: `shipping_provider_group` is the right axis for user-facing "cost by carrier" answers (~30-40 distinct values, high-level). If finer granularity is needed, fall back to `shippingprovider_extkey` (service-level). Verify on first post-cutover carrier-breakdown query.

### Watch on next shipping-agent session against new rule

The T18 sharpening was prompted by a failure of the T16 rule to fire. If a fresh transcript still produces a basis-less headline or a mismatched denominator after the rule lands, the issue isn't the wording — it's that §0 rules don't fire reliably when the agent is mid-query. Possible follow-up: move the most behavioral sub-rules to a higher-priority surface (top of §0, or a dedicated `MUST` block), and/or add a pre-query checklist for cost questions. Don't redesign yet; need a real post-apply incident first.

## Parked ideas

- **Local-files channel for shipping-agent consumers (T17, 2026-05-22).** Multi-consumer problem: BI team pulls updates from GitHub but also needs personal rules / preferences / scratch surviving reclones. Recommended shape: `.local.md` sidecars next to each shipped `.md` (`CLAUDE.local.md` auto-loaded by directory walk; `how_to.local.md` / `notes.local.md` reference-on-demand) + `.gitignore` for `*.local.md`, `local/`, `.env`. Two undecided: ship a `CLAUDE.local.md.example` template (yes/no), and personal-rule override status (silent / agent-flagged / append-only). Working recommendation: scaffolded + silent override. Unpark when consumers signal friction from missing local channel.
- **`scope-perimeter.py` PreToolUse hook for shipping-agent (T17 discussion).** Diagnosed mid-T17: the bi-analytics-main session opens at the repo root, so default-CWD Grep calls reach outside `shipping-agent/` and trip `settings.json` allow-list prompts (`cost.*month|cost.*variation|...` screenshot). A PreToolUse hook would catch absolute-path reaches and default-CWD reaches that the relative-path deny patterns miss. Principal said "forget it" — not building now. Unpark if the prompt-fatigue from §10 / settings.json deny patterns recurs at meaningful frequency.

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
- `gielinor/players/jebrim/bank/drafts/notes/projects/shipping_mart_cost_vocabulary_2026-05-22.md` (S027 / S024 T16-T16b harvest) — durable column model for `real_shipping_cost_eur` / `expected_shipping_cost_eur` / `avg_shipping_cost_eur` / `final_shipping_cost_eur`, cost-bucket grain rule (buckets are invoiced-only), and the doc-edit proposal text for `reference/mart-contract.md` + `how_to.md` §0. Surface at next alching; archive the proposal section once applied to the shipping-agent docs.
- `gielinor/players/jebrim/examine/drafts/2026-05-22-bash-on-windows-quoted-path-creates-literal-filename.md` (S027 harvest) — self-observation: writing intent sidecar files with `Bash echo "..." > "C:\path\file.txt"` on Windows produces a literal filename with the colon encoded as U+F03A, not a write to the intended path. Use the Write tool or PowerShell `Set-Content` instead. Anchor: S027 stray-file incident at brain root.

## Parked items from earlier S023 alching walk

Still untriaged from before this session. The 7-item alching proposal from post-S023 lives in [[S023-shipping-mart-coverage-audit-resume]] — re-surface when next alching runs.

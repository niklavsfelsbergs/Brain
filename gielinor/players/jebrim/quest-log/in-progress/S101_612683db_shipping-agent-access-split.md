# S101 — Shipping-agent access split (one agent, two tiers)

**Session:** jebrim-612683db · **Opened:** 2026-05-27
**Mode:** player (Jebrim), principal · design consultation

## Ask

`picanova/shipping-agent` is now shared with many colleagues on `ship_mart_ro` (read-only, gold `shipping_mart.*` only). Niklavs wants to run the **same** agent with **full DB access** (raw invoice tables; contracts parked for now) so he can train + version one agent — without forking into two.

## Decisions (this session)

- **Architecture: one repo, per-user gitignored access overlay.** Principal picked **local overlay** over an env-var profile or a fork (AskUserQuestion, 2026-05-27).
  - Hard boundary = the **DB role** (`ship_mart_ro` denies non-gold at the database; non-bypassable). Rulebook scope = UX layer only.
  - Three per-user seams, all already gitignored: `.env` (creds), personal folders (`workbench/`/`memory/`/`scratchpad/`), + NEW `CLAUDE.local.md` (Niklavs-only scope widening).
  - Shared change needed: make `how_to.md` rule 10 (schema perimeter) **conditional** — "shipping_mart only, unless a local profile grants wider scope." Colleagues with no overlay = identical behavior to today.
- **Contracts: parked.** Raw invoice *files*/contracts (non-DB) deferred — would need a file/document tool, separate build.
- **Raw invoice tables: mapped from bi-etl** (principal: "might be updates by now" → pulled fresh).

## Finding — what actually feeds gold (CORRECTED)

**First pass was wrong** — I enumerated the *write targets* of the legacy `dags/shipping_invoice_cost/` ingestion DAGs. Principal corrected: look at the **shipping data mart DAGs** (`dags/shipping_mart/`) and what *they read FROM*. Re-ran on the FROM/JOIN clauses there.

Gold builds at **`dags/shipping_mart/`** (top-level DAG): `fact_shipments`, `fact_shipment_cost_summary`, `fact_shipment_orderitems`, `fact_shipment_invoice_lines` (per-carrier provider SQL under `.../sql/providers/`), `fact_truck_charges` (out of agent scope). **Keepsake pin still names old `enterprise_silver/shipping_data_mart/` → rotate.**

Source tables feeding gold (FROM/JOIN, deduped):

| Schema | refs | What it carries | Grant? |
|---|---|---|---|
| `enterprise_silver` | 143 | **dominant input** — cleaned per-carrier `*_invoices`/`*_charge_lines`, `shipping_charge_bucket_mapping`, `dim_shipping_providers`, `map_shipment_key`, `revenues`, `avg_shipping_costs`, `pcs_*` order rollups, `orwo_picturator_bridge` | **YES (core)** |
| `enterprise_bronze` | 103 | source-system order/shipment data: `picaapi_*` (MerchOne), `pict_*` (Picturator), `orwo_*` (Wolfen), `pcs_*` (internal print), `rew_*` (Rewallution); a few still-raw carrier invoices (`fedex_invoicedata_historical`, `dpd_poland_secondstructure_invoice`, `ontrac*`, `landmark*`); static ref (`currency_rates`, `countries_static_iso_map`, `dim_truck_costs`) | **YES (core)** |
| `dw` | 1 | `dim_products` | YES (dim) |
| `sl_gold` | 1 | `dim_date` | YES (dim) |
| `asa`, `bi_stage_dev_dbo`, `bi_asa_dev_dbo`, `poc_landing` | 2/4/2/2 | legacy stragglers gold still touches (`temp_expected_shipping_costs_pack`, a few fedex/ups invoice tables, `orwo_navcluster_data`) | optional — no-surprises only |
| `shipping_mart` | 17 | self-refs (post-processing reads its own facts) | already granted |

`poc_dw` is **NOT** read by gold — drop it from the grant list (it's the older parallel cost fact). `fs`/`m`/`dhl`/`orwo_packaging` matches were aliases/false-positives.

**Recommended role grant:** SELECT on `enterprise_silver`, `enterprise_bronze`, `dw`, `sl_gold`. Add `asa`/`bi_stage_dev_dbo`/`bi_asa_dev_dbo`/`poc_landing` only to close edge-case gaps.

**Same-DB question RESOLVED:** gold joins `enterprise_silver` + `enterprise_bronze` + `dw` + `sl_gold` in single statements using 2-part names → all schemas in **one Redshift db** (`bi_stage_dev`, `db.py` default). So Niklavs's `.env` is a **user swap only**, no `REDSHIFT_DB` override needed.

**Caveat:** silver/bronze carry no gold cleaning, bucket collapse, vocabulary, or DQ caveats — full-access work is off the curated contract. Fine for Niklavs (training/debug); exactly why colleagues stay on gold.

## Creds — RESOLVED (principal decision + verified)

Reuse Niklavs's existing NFE Redshift user, not a new role. Source: `bi-analytics-main/NFE/.env` → `REDSHIFT_USER=tcg_nfe`. Password stays in his local `.env` (never committed/printed). Host/db = shipping-agent `db.py` defaults (same cluster, `bi_stage_dev`) → `.env` is a **user swap only**.

**Verified live (redshift MCP, 2026-05-27):** `tcg_nfe` has USAGE + SELECT on all 5 — `enterprise_silver`, `enterprise_bronze`, `dw`, `sl_gold`, `shipping_mart`. **No DBA / grants / new role needed.**

## Drafted this session (shipping-agent working tree, NOTHING committed/pushed)

Tree was clean @ `11996a8` (only untracked `demo/`, not mine). Three changes:

1. **`CLAUDE.local.md`** (NEW, root) — Niklavs's full-access/maintainer overlay: `tcg_nfe` user, in-scope schemas (silver/bronze/dw/sl_gold + gold), build lineage pointers, off-gold-contract discipline (no bucket collapse / no DQ cleaning / raw vocab → flag when reaching upstream), stay-read-only. **Verified gitignored** (`git check-ignore` → `.gitignore:35`) — invisible to git, never ships.
2. **`.gitignore`** += `CLAUDE.local.md` (M) — the safety net so it can't be swept by a stray `git add .`.
3. **`how_to.md` rule 10** (M) — added the local-profile exception: gold-only perimeter is absolute *unless* a `CLAUDE.local.md` widens it; no-op for colleagues (no overlay = today's behavior). Connection user is the real gate.

**HELD for principal:** `.gitignore` + `how_to.md` are shared-repo edits — push to picanova/shipping-agent is principal-gated. `git commit -- <pathspec>` (only those 2 files; exclude untracked `demo/`). His agent works locally the moment the overlay + rule-10 edit are in his working tree — push is for repo consistency, not his functionality.

## Open / next

1. ~~Same-db~~ ~~role+grants~~ ~~draft overlay~~ ~~draft rule-10~~ all RESOLVED.
2. **`.env` set** → `tcg_nfe` active, `ship_mart_ro` kept as commented toggle (still gitignored). Smoke-test an upstream-only query to confirm full access live.
3. Principal review + push the 2 held shared edits (`.gitignore`, `how_to.md`) to picanova/main (`git commit -- <pathspec>`).
4. **Harvest DONE (this session):** bank draft `bank/drafts/notes/projects/2026-05-27-shipping-mart-gold-lineage-and-access-tiering.md` (lineage + access model) + keepsake proposal `keepsake/proposals/2026-05-27-routing-pin-mart-path-and-access-update.md` (mart-path rotation + access-tiers line) + **spellbook skill draft `spellbook/drafts/skills/calling-the-shipping-agent.md`** (how/when to call the agent as a scoped dwarf). All await alching/principal promotion.
5. Brain repo commit (jebrim namespace + comms) — awaiting principal go.
6. **DEV-BRAIN task (not Jebrim's lane):** build a dedicated `shipping-agent` subagent type — `.claude/agents/shipping-agent.md` + cockpit sprite/label rendering + a write-boundary decision — so a shipping-agent call is visibly distinct from a generic dwarf. Small task. Skill `calling-the-shipping-agent.md` step 2 already points at this; ad-hoc dwarf is the fallback until built.

## Trace
- bi-etl `dags/shipping_invoice_cost/` (ingestion), `dags/shipping_mart/` (gold build).
- shipping-agent `harness/db.py` (`.env`-only creds, no fallback), `how_to.md` rule 10 (perimeter).

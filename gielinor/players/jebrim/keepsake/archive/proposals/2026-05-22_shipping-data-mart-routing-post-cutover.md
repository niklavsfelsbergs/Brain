# Proposed pin — Shipping Data Mart routing (post-cutover, gold-verified)

**Proposed:** 2026-05-22 (S028, mid-S024 cutover work)
**Supersedes:** the current `Shipping Data Mart — routing` pin in `keepsake/current.md` (originally pinned 2026-05-21 via `archive/proposals/2026-05-21_shipping-data-mart-routing.md`, re-pathed same day after the S022 restructure).

## Pin text (what surfaces every Jebrim session)

> **Shipping Data Mart — routing.** Gold layer **`shipping_mart`** schema is the agent's entire surface — four facts, no joins outside the schema:
> - `shipping_mart.fact_shipments` (wide fact, 66 cols — spine + provider data denormalized in)
> - `shipping_mart.fact_shipment_cost_summary` (per-shipment 11-bucket cost pivot, invariant `SUM(buckets) == total_eur == fact_shipments.real_shipping_cost_eur`)
> - `shipping_mart.fact_shipment_orderitems` (line-item rollup per shipment)
> - `shipping_mart.fact_shipment_invoice_lines` (per-charge-line invoice detail with `charge_bucket`)
>
> Cutover from `enterprise_silver.*` landed 2026-05-22. Old silver facts are **gone** (not deprecated views). `map_shipment_key` and `dim_shipping_providers` are not needed — their data lives on `shipping_mart.fact_shipments` directly (`source_system`, `shippingprovider_extkey`, `shipping_provider_group`, `shipping_provider_id`). `fact_truck_charges` is out of scope.
>
> **Shipping-agent (standalone).** Lives at `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/` today, but **relocatable** — designed to run anywhere with its own `.env` and `harness/`. Entry doc: `shipping-agent/README.md` (human onboarding) + `shipping-agent/how_to.md` (AI-facing rules + §1 "Where to find things" index). Reference content in `shipping-agent/reference/` (mart-contract, sources, tables, coverage-audit, known-dq); query methodology in `shipping-agent/skills/query-patterns.md`.
>
> **Connection.** Local `.env` in `shipping-agent/` with the `ship_mart_ro` user (read-only, gold-only access). `harness/db.py` loads from the local `.env` only — does not walk up. Smoke-test: `python harness/connect_redshift.py --query "SELECT 1"`.
>
> **Ground truth (Redshift DDL / pipeline).** `Documents/GitHub/bi-etl/dags/enterprise_silver/shipping_data_mart/` per-folder READMEs — currently the silver dags but **being repointed to gold** (path stays for now; will move with the dags). `git pull origin main` before reading the code for an audit/sanity check.
>
> **Outputs.** Land per `how_to.md` §7–§8 conventions — `shipping-agent/visualization-studio/content/charts/claude/YYYYMMDD-HHMMSS--<slug>.html` for Mode 2 inline; `visualization-studio/content/generated/claude/YYYYMMDD-HHMMSS--<slug>/` for bundle modes.
>
> **Schema discipline (in-force).** Queries qualify as `shipping_mart.<table>` always — never assume `search_path`. The agent's surface is the four tables; reaching for anything in `enterprise_silver.*`, `enterprise_bronze.*`, or any other schema is a scope violation (and `ship_mart_ro` would deny it anyway). For source/lineage understanding, defer to bi-etl docs — not in agent scope.
>
> **`cost_source` values (verified 2026-05-22):** `'invoice'` (65%), `'expected'` (24%), NULL/uncosted (8%), `'avg'` (2%). Note: column name is `real_shipping_cost_eur` but the flag value is `'invoice'` — naming asymmetry; future cleanup may align.
>
> **Update discipline.** When new gotchas / recipes / coverage drift / DQ classifications emerge from real work, update the appropriate file in `shipping-agent/` (LIVE files carry `last-verified` stamps; STABLE files don't). Cross-update Jebrim's `bank/notes/` only when the learning is methodology or routing, not mart specifics.

## What changed from the prior pin

| Field | Before (2026-05-21) | After (post-cutover, gold-verified) |
|---|---|---|
| Schema for the four facts | `enterprise_silver.fact_*` | `shipping_mart.fact_*` |
| Spine + dim joins | Required: `JOIN map_shipment_key`, `JOIN dim_shipping_providers` | **None** — both denormalized into `fact_shipments` |
| Agent scope | 4 facts + spine + dim + truck-charges (7 tables) + source-side lineage docs (~24 carrier invoice tables) | **4 facts only.** Source-side lineage out of scope; defer to bi-etl |
| Old `enterprise_silver.fact_*` | Live | **Gone** (not deprecated views — hard cutover) |
| Credentials | `find_dotenv()` walked up from `db.py` to `NFE/.env`; no local `.env` after `ship_mart_ro` was deprovisioned | Local `shipping-agent/.env` with restored `ship_mart_ro` (gold-only); explicit single-file load |
| Agent location semantics | Coupled to `NFE/` parent (credential walk-up + reference reach) | Standalone — designed to be moved anywhere |
| Older NFE-side reference | Kept "for navigation" as lighter sibling | Dropped — local `shipping-agent/reference/` is sole authoritative source |
| Ground-truth path | `bi-etl/dags/enterprise_silver/shipping_data_mart/` | Same path, transitionally — dags being repointed to gold; path will move with them |

## Why this qualifies for keepsake (unchanged)

- **Frequent standing topic.** Principal stated in S015: "I will now be frequently working on the shipping data mart with you, Jebrim." Cutover does not change the cadence.
- **Cutover changes load-bearing facts.** Schema name, agent scope (4 tables, no joins outside), credentials, and standalone-vs-coupled posture all flipped on the same day. Without a refreshed pin, every Jebrim session post-cutover would either re-derive the new state from quest-log archaeology or run stale queries against `enterprise_silver.fact_*` and get permission-denied.
- **Standalone-ness is a behavioral commitment.** "Designed to be moved anywhere" is a constraint the agent must hold itself to: never re-introduce a walk-up to `NFE/.env`, never reach out for reference content, never query outside `shipping_mart`. Pin makes the commitment visible at every session start.
- **Scope narrowing is the load-bearing simplification.** 4 tables instead of 7+24 — the bank/keepsake should mirror that simplification, otherwise the agent keeps re-loading silver-era complexity.

## Rotation criteria

Rotate out when:
- Ground-truth path moves to the actual gold dag location (rotate this version, pin a tighter one with the new path), **or**
- Schema names / agent scope / credential model shift again, **or**
- Shipping data mart stops being a frequent working topic.

## Apply still needs (not blocking this pin)

These belong in the bi-analytics-main apply session, not the keepsake pin:

- Apply the 4-table-scope doc-stripping pass to `reference/sources.md`, `reference/tables.md`, etc. — remove source-side lineage; agent only knows the 4 gold facts.
- Apply the cost-vocab rewrite (`'invoice'` not `'real'`, 11 buckets named directly, tax/customs excluded from total_eur) — see `bank/drafts/notes/projects/shipping_mart_cost_vocabulary_2026-05-22.md`.
- Add §10 schema-perimeter rule: forbid queries outside `shipping_mart.*`.
- Locate the gold-dag ground-truth path when the bi-etl repoint lands; re-pin then.

## Source

S028 (this session) — Niklavs surfaced two coupled changes (gold cutover + `ship_mart_ro` restored) with the explicit goal "agent can be moved anywhere." Gold-side verification via `ship_mart_ro` against `information_schema.columns` (128 cols across 4 tables) and live invariant checks (12.03M `cost_source='invoice'` rows, bucket sum invariant holds at zero diff across 200K sample). Scope narrowed to 4 tables on principal's call (lineage to bi-etl, not agent).

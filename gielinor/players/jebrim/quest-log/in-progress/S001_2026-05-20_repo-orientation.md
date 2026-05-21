# S001 — 2026-05-20 — Repo orientation: NFE + bi-etl

**Principal:** Niklavs
**Player:** Jebrim
**No pending external actions.**

> Resume state for this quest lives in `players/jebrim/inventory/S001-repo-orientation-resume.md` (per `meta/layer-routing.md`). This quest-log keeps narrative, decisions, and the turn log.

## Confirmed picks (5)

1. ✅ `projects/2_EU_tender_2026` — landed at `bank/notes/projects/eu_tender_2026.md`.
2. ⏳ `projects/1_shipping_data_mart` — drafted; pending status-pass + write.
3. ⏳ `SHIPPING-COSTS/carriers` — untouched. *Future task: review vs EU tender 2026.*
4. ⏳ `dashboards/shipping_costs_monitoring_nextjs` — untouched.
5. ⏳ `SHIPPING-COSTS/analysis` — untouched.

`projects/2_EU_tenders_2026` (plural) is a folder-rename artifact — ignore.

## Future deliverables noted

- **Review of SHIPPING-COSTS (US tender) vs EU tender 2026** — different approaches; learnings/comparison expected. Principal flagged for later.
- **Update Jebrim's `_about.md`** — repo paths are stale (`Documents/bi-analytics-main/...` should be `Documents/GitHub/bi-analytics-main/...`).

## Workflow conventions (carry forward)

- Reads need no approval; writes do.
- Drafts go to chat first; principal approves; only then write to `bank/notes/`.
- bi-etl pulls happen mid-deep-dive when an NFE thing references it.
- Note granularity: per-concept primary, per-project landing notes, anchor links to repo paths, no mirroring of repo structure.

## Repo paths (verified, corrected from stale `_about.md`)

- NFE: `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics-main\NFE\`
- bi-etl: `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-etl\`
- bi-analytics (older sibling, source of redshift MCP config): `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics\`

## Pending drafts

### Shipping Data Mart — landing note (awaiting status-pass + approval)

Drafted in T6 from docs only (`README.md`, `CLAUDE.md`, `next_session.md`). Principal flagged: docs-intent, not verified status. Revise after the status-pass listed under "Next concrete step." Intended path on approval: `bank/notes/projects/shipping_data_mart.md`.

---

```markdown
# Shipping Data Mart

**Source (design):** `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics-main\NFE\projects\1_shipping_data_mart\`
**Source (implementation):** `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-etl\dags\enterprise_silver\shipping_data_mart\`
**Status (per docs, unverified):** v1 design phase. 8 tables, 142 columns specified. Sources being mapped, pipelines not yet built. Scope: data from 2024-01-01 onwards.

## Two homes, two roles

| Repo | Role | What lives there |
|---|---|---|
| NFE `1_shipping_data_mart/` | **Design / spec** | Markdown column specs, ER diagram, investigation threads, design decisions |
| bi-etl `dags/enterprise_silver/shipping_data_mart/` | **Implementation** | Actual pipelines, per-table READMEs, what's actually shipped |

**Authority rule (from NFE CLAUDE.md):** if design and implementation disagree, **trust the bi-etl READMEs**. The mart moves fast on the bi-etl side — `git pull origin main` before any audit.

## What it answers

- Average delivery time by carrier
- Which warehouse causes the most delays
- Shipping cost per shipment, broken down by cost type
- Cost quota: shipping cost as % of net revenue per shipment
- Which carrier/route combinations are most expensive
- Which carriers are breaching SLAs, and by how much

## The 8 tables

| # | Table | Grain | Cols | Role |
|---|---|---|---|---|
| 1 | `map_shipment_key` | 1 per (trackingnumber, shop_ordernumber) | 5 | Surrogate key generator |
| 2 | `fact_shipments` | 1 per shipment | 55 | **Mart spine** — wide fact, identity + dims + dates + costs + revenue |
| 3 | `fact_shipment_orderitems` | 1 per produced item per shipment | 10 | Product lines + line-item revenue |
| 4 | `fact_shipment_invoice_lines` | Many per shipment | 15 | Raw carrier invoice lines |
| 5 | `fact_shipment_cost_summary` | 1 per shipment | 30 | Pivoted cost breakdown, **derived from #4** |
| 6 | `fact_truck_charges` | 1 per truck departure | 11 | Truck departures + allocation |
| 7 | `dim_shipping_providers` | 1 per carrier × service | 8 | Carrier reference |
| 8 | `dim_carrier_sla` | 1 per carrier × country × date range | 8 | SLA rules for breach calc (SharePoint-maintained) |

## Key design decisions worth carrying

- **Grain.** `trackingnumber + shop_ordernumber` is the unique grain. Tracking numbers get reused by carriers across orders. Surrogate `shipment_id` from `map_shipment_key`; FK across all tables.
- **Wide fact, no `dim_shipment`.** Dimensional attributes (site, provider, destination, package dims, shop) sit inline on `fact_shipments`. Intentional for analytics simplicity at 1:1 grain.
- **Cost hierarchy.** `final_shipping_cost_eur = COALESCE(real, expected, avg)`. `cost_source` column always stored. Real/expected/avg sources are mid-redesign — `enterprise_silver.shipping_costs` and `dw.v_shipping_invoices_expected_ship_costs_all` are explicitly being **replaced**.
- **SLA in view, not stored.** `sla_breach_flag` and `days_vs_sla` are computed at query time joining `dim_carrier_sla`. Avoids stale data when SLA records are corrected retroactively.
- **SCD Type 1 everywhere.** Late-arriving invoice data treated as backfill, not history. Daily snapshot table can be added later if a "what was X on day Y?" use case appears.
- **Order is the source of truth, not the parcel.** Pipelines start from PICT + PICAAPI orders, then LEFT JOIN PCS for internal-site shipping. An order with no trackingnumber in a terminal shipped status is a DQ issue (flagged, not dropped).

## Source-system architecture

Two source-system axes per shipment:

| Side | Systems |
|---|---|
| **Orders (identity + revenue)** | PICT (Picturator) `pict_*`, PICAAPI `picaapi_*`. PTS deferred (T-19). |
| **Shipping data** | Internal sites → `pcs_*`. External sites → same shop system as the order. |

Internal sites: Szczecin, Columbus (active); Phoenix, Miami (legacy still active). Köln excluded (v1, ~12 orders since 2024).
External sites: Wolfen, LaserTryk, Allcop, Elanders, UnitedArts, VR, MerchRocket, PrintAndLogistics (more may surface — T-28).

`source_system` column = `Picturator` or `PicaAPI` (mixed case as stored, **not** PICT/PICAAPI).
**No `production_system` column** — PCS-vs-shop is derivable from `production_site`.

## Source priority (search order)

When sourcing any column, layers in order:

1. **Curated:** `enterprise_silver`, `sl_gold`, `ol_gold`
2. **Raw analytical:** `enterprise_bronze`
3. **Landing:** `poc_landing` (tag SQL with TODO to migrate)
4. **Legacy last resort:** `dw`, `bi_stage_dev_dbo`, `bi_dw_dev_dbo` (with justification)

**Never use:** `*_federated` schemas, `enterprise_silver.shipping_costs` (being replaced), `dw.v_shipping_invoices_expected_ship_costs_all` (being replaced), `dw.shipment_logs` (ruled out by default), `old_ol_*` / `old_sl_*` legacy snapshots.

## Investigation threads

`investigation/investigation.md` tracks open threads T-01 through T-34. Source mapping is the live work — next-session prompt directs to filling `Source` cells in `model/data_model.md` via Redshift MCP read-only.

Key open threads:
- **T-14, T-15, T-16** — real/expected/avg cost redesign.
- **T-17** — truck allocation logic + landing-only table dependency.
- **T-19** — PTS integration scope.
- **T-26** — production-site LIKE map.
- **T-29** — PCS join validation.
- **T-31** — terminal-shipped-status definition for DQ.
- **T-34** — `net_revenue_eur` scope: product-only vs full order financial total.

## Cross-references

- Consumer: [[projects/eu_tender_2026]] — Phase 2 replay pulls 2026 Q1 from `enterprise_silver.fact_shipments` + `enterprise_silver.fact_shipment_cost_summary`.
- Shared reference tables (reuse — never rebuild): `sl_gold.dim_currencies` (FX), `sl_gold.dim_date` (calendar), `sl_gold.dim_shops`.
- FX rule (v1): all `_local` → `_eur` at `shop_order_created_date`.
- Business-day rule (v1): `dim_date.isweekday` only — no per-country holidays.

## Branches to write (concept notes)

- The cost hierarchy pattern (`invoice → expected → avg → final` + `cost_source` flag) as a reusable BI pattern.
- The wide-fact-vs-star-schema trade-off at 1:1 grain — why this mart chose wide.
- The order-as-truth + LEFT-JOIN-PCS pattern for multi-source pipelines.
- The schema search order as a transferable convention.
- Per-table deep notes once pipelines exist (likely after bi-etl review).
```

---

## Turn log (history; reference only)

- T1: Address opens session, Jebrim active. Principal frames task: not personality, but work-domain grounding.
- T2: Aligned on workflow + note granularity (per-concept primary, principal approves every write).
- T3: Surveyed NFE; produced touch-count table for last 6 weeks; proposed picks of 5.
- T4: Principal confirmed picks; clarified SHIPPING-COSTS = US tender (distinct from EU tender). Captured this quest-log entry. Starting deep-dive #1 (EU tender 2026).
- T5: EU Tender 2026 landing note drafted from README.md + CLAUDE.md + 2_analysis/CLAUDE.md + NEXT.md. Approved by principal. Written to `bank/notes/projects/eu_tender_2026.md`.
- T6: Started deep-dive #2 (shipping data mart). Drafted landing note from README + CLAUDE.md + next_session.md. Principal challenged: was this from docs or from project status? Honest answer — docs only, status not verified. Proposed two paths: land draft as-is with "unverified" caveat, or pause for 15-min status pass. Principal redirected to MCP setup first.
- T7: MCP setup. Found redshift definition at `bi-analytics/.mcp.json` (not bi-analytics-main). ClickUp already available at brain root via Claude.ai connector. Wrote `brain/.mcp.json` with redshift + orps. Added `.mcp.json` to `brain/.gitignore`. **Restart required** for activation.
- T8: Principal asked about session handoff mechanics. Walked through the receiving side (respawn → reconciliation prompt → in-progress quest-log). Identified gap: chat-only drafts (e.g., the shipping data mart draft) don't survive restart.
- T9: Principal noted dev-brain has close-session + respawn skills working in unison; gielinor doesn't. Discussed approach. Aligned: trigger "lets close the session," covers all players, always commit, SNNN prefix before date, global ritual.
- T10: Drafted `close-session.md` ritual content. Principal approved as-is. Principal overrode `meta/write-rules.md`'s user-only constraint on `spellbook/rituals/` for this specific write.
- T11: Wrote `gielinor/spellbook/rituals/close-session.md` and updated `gielinor/CLAUDE.md` with pointer.
- T12: Principal cued close. Executed close-session ritual.

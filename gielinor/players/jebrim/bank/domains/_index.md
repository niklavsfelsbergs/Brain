# bank/domains/_index.md — Jebrim's domain map

> **Always-read** (force-injected every Jebrim session, like the keepsake). The map of Jebrim's work domains — *what he knows*, one line each. The per-domain **digest** (`<slug>.md`) is **cue-loaded** when its topic fires; this index is just the lay of the land. Spec + frontmatter schema in `_about.md`. Keep it a map — one line per domain, never a digest-of-digests.

## Digested domains

| Domain | What it is | Cue / load |
|---|---|---|
| **[[scm]]** | Shipping Costs Monitoring — the productized always-on `shipping_costs_monitoring_nextjs` dashboard + alert engine over the gold shipping_mart (two runtimes: Airflow pipeline + Next.js serving). | `scm`, "shipping costs monitoring", "alert engine" → loads `scm.md` |
| **[[shipping-mart]]** | The gold `shipping_mart` contract (4 facts, 11-bucket cost invariant, cost-basis, package-dim gate, lineage + access tiers) **and the shipping-agent** — the talk-to-your-data tool that queries it. | `shipping mart`, `fact_shipments`, `cost_for_routing`, `shipping-agent` → loads `shipping-mart.md`; also the global `cue_registry.py` shipping row → external repo + specialist |
| **[[eu-tender]]** | EU Tender 2026 — the quantitative carrier-tender review (cost-only, full-year basis): architecture, switchable-incumbent scoring, the re-rating trust gate, current ~6-carrier portfolio + routing rebuild. | `eu tender`, `carrier tender`, `decision report`, `routing report`, `carrier overview` → loads `eu-tender.md` |
| **[[carrier-contracts]]** | Carrier contracts & invoices — rate-card reading, contract terms/expiry, invoice DQ (FIF/UPS-ORWO), dimension-coverage map, re-rating discipline. | `carrier contract`, `rate card`, `fif`, `dimension coverage`, `fuel surcharge` → loads `carrier-contracts.md` |
| **[[nfe-repo]]** | NFE workspace structure — `shipping_topics/` (ad-hoc), `projects/` (multi-phase), `dashboards/` (productized), `.claude/reference/` (patterns) — and where to do which kind of work. | `nfe`, `shipping_topics`, `repo structure`, `which folder` → loads `nfe-repo.md` |
| **[[production-times]]** | Throughput/timing pillar (distinct from cost) — PCS production lead time (wd, P85/P95, 3-wd target), fulfillment lifecycle, transit-time SLA, and **delivery-promise cutoffs**. Sites SZZ/CMH/PHX/MIA; anchor `order_flagging.pcs_production_times`. | `production time(s)`, `pcs production`, `fulfillment`, `promise cutoff`, `transit time` → loads `production-times.md` |
| **[[bi-etl]]** | The Airflow→Redshift ETL repo — **trace a warehouse/mart table or column back to its DAG + source**. Layer map (enterprise_bronze→silver→gold), the DAG-header `Reads/Writes` + data-definition lineage artifacts, the 5-step trace workflow. | `bi-etl`, `data pipeline`, `trace back`, `lineage`, `which dag`, `enterprise_bronze` → loads `bi-etl.md` |

## Not yet digested (uncovered clusters — §Z bootstrap worklist)

*(Empty — all currently-named Jebrim domains are digested as of 2026-06-09. 2026-06-09 coverage-decision: shipping-savings REJECTED by principal ("bad project"); tcg-organic-growth + Lyto rejected; production-times + bi-etl ACCEPTED and digested. Dashboard-build method is a **skill** gap, not a domain. New clusters land here when a future pass names them.)*

*Rotate a domain from the lower list to the table when alching lands its digest. Keep this index under budget — if it grows past a screen, that's a signal the domains need consolidating, not a longer index.*

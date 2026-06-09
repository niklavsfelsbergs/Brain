# bank/domains/_index.md — Jebrim's domain map

> **Always-read** (force-injected every Jebrim session, like the keepsake). The map of Jebrim's work domains — *what he knows*, one line each. The per-domain **digest** (`<slug>.md`) is **cue-loaded** when its topic fires; this index is just the lay of the land. Spec + frontmatter schema in `_about.md`. Keep it a map — one line per domain, never a digest-of-digests.

## Digested domains

| Domain | What it is | Cue / load |
|---|---|---|
| **[[scm]]** | Shipping Costs Monitoring — the productized always-on `shipping_costs_monitoring_nextjs` dashboard + alert engine over the gold shipping_mart (two runtimes: Airflow pipeline + Next.js serving). | `scm`, "shipping costs monitoring", "alert engine" → loads `scm.md` |

## Not yet digested (uncovered clusters — §Z bootstrap worklist)

These are live Jebrim domains with bank-note clusters but no digest yet. The §Z.D coverage detector names them; alching synthesizes each into a digest here.

- **EU Tender 2026** — quantitative carrier-tender review (parcel + freight, cost-only scoring; full-year basis). Cluster: `eu_tender_2026*`, the re-rating/trust-gate + per-carrier validation notes. *(Currently carried by the keepsake pin + cue.)*
- **Shipping data mart** — the gold `shipping_mart` contract/schema/cost-basis + the shipping-agent. *(Carried by the keepsake routing pin + the global `cue_registry.py` shipping row → external repo + specialist.)*
- **Carrier contracts & invoices** — UPS/DPD/DHL/FIF rate cards, invoice DQ, dimension coverage, re-rating method. Cluster: the `2026-06-09-*` carrier notes + FIF quirks.

*Rotate a domain from the lower list to the table when alching lands its digest. Keep this index under budget — if it grows past a screen, that's a signal the domains need consolidating, not a longer index.*

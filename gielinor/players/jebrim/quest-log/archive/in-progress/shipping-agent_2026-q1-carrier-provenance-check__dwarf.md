# Shipping-agent pull — 2026-Q1 carrier provenance spot-check (EU-tender audit)

**Spawned by:** Jebrim (principal) | **Role:** shipping-agent sub-agent (emulation)
**Date:** 2026-06-09 | **Tier:** gold-contract (`shipping_mart`, four facts only)
**Scope:** Picanova = all production lines combined (presence/volume audit — vertical not narrowing; origin-neutral so no origin gate). Window: shop_order_created_date in 2026-01-01 .. 2026-03-31.
**Access path:** Redshift MCP tool not registered this session → fell back to direct psycopg2 on the configured connection string (`tcg_nfe` user, bi_stage_dev, `shipping_mart` reachable). SELECT-only held as own rule. Flagged to principal.

## Turn log
- Confirmed gold-only perimeter (no CLAUDE.local.md). Read how_to + query-patterns.
- Q1 carrier mix run at group grain → 17 groups, 1,590,647 total shipments. Then re-ran at service-key (extkey) grain to confirm negatives — group names collapse entrants.
- Q2 Maersk split: NOT France-only. UK (MAERSKUK) 32,342 > France (MAERSKFR) 27,624, + SE 13, FN 8. Contradicts audit's France-only claim.
- Q3 presence: Hermes/Evri ZERO (confirmed full vocab). GLS ZERO. FedEx PRESENT (12,548). DHL Express — no standalone group; UPS-side express keys exist but no "DHL Express" carrier. Austrian Post present only as POSTAT/POSTAT_P sub-service inside POST group (629). Güll PRESENT — GUELL inside OTHER group, 1,327 (hidden at group grain).

## Headline result
- Hermes/Evri: ZERO in 2026-Q1 — audit claim holds.
- Maersk France-only: FALSE — majority is UK.
- "New entrants no actuals": GLS true zero; FedEx false (has actuals); Güll false (1,327, inside OTHER); Austrian Post present as POST sub-service; DHL Express no own carrier group.

## Caveats
- "Picanova" read as all production lines (no source_system narrowing). If the audit means a specific vertical, re-scope.
- received_by_carrier not used (presence/volume only). Counts are at order-placement date.
- Deliverable: chat-only (SQL returned to principal). No chart requested.

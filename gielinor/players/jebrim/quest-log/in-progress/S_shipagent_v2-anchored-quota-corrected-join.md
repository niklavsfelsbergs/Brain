# v2 date-anchored shipping-cost-quota — corrected join direction

**Player:** Jebrim | **Agent:** shipping-agent (emulation) | **Date:** 2026-06-17
**Tier:** gold-contract for mart facts; OFF-CONTRACT on `dw.sales_fact.archivedtime` lookup (brief-authorized, no CLAUDE.local.md).

## Ask
Rebuild v2 anchored quota with corrected join: DRIVE from `fact_shipments` (shipment grain), LOOK UP `archivedtime` from `dw.sales_fact` via `shop_ordernumber=ordernumber` + `source_system=data_source` (scalar many-to-one, no fan-out). Scope: Picturator+PicaAPI, all sites except {PCS CMH, PCS MI, PCS PX} (Wolfen IN). Jan–May 2026 + YTD. Two methods (SCM native + corrected anchored). Sanity gate vs v1 on excl-Wolfen.

## Turn log
- Mart contract loaded (how_to.md full + mart-contract.md). No CLAUDE.local.md -> gold-only default; off-contract dw lookup is brief-authorized.
- Confirmed `dw.sales_fact` unique per (ordernumber, data_source) — lookup genuinely scalar, no fan-out. Match rate on 2026-created orders = 99.98% by revenue. Join is SOUND.
- SCM method reproduced EXACTLY: YTD €6,931,955 / €37,029,541 / 18.72%; monthly 19.18/18.83/18.17/18.50/18.77. Unchanged.
- SANITY GATE FAILED at first reading: archived-revenue-lens excl-Wolfen = 19.42% vs v1 mart-derived 19.76% (0.34pt, exceeds ~0.2pt gate). STOPPED per instruction.
- Diagnosed: cost ties to v1 within 0.7% (€6.37M vs €6.41M); divergence is entirely revenue (€32.78M archived-lens vs €32.43M v1, +1.1%).
- Tested order-PLACED revenue lens: excl-Wolfen = €6,366,109 / €32,433,723 / 19.62%. Revenue €32,433,723 = EXACT match to v1 mart-derived. Gate PASSES (0.14pt) under this lens.
- CONFLICT surfaced: v1's anchored series dated cost by ship/archived but revenue by ORDER-PLACED month (= SCM revenue lens). Brief asks revenue by ARCHIVED month. Archived-rev lens makes rev DIFFER from SCM (brief requirement) but fails the v1 gate; placed-rev lens passes the gate but makes rev == SCM (violates "must differ"). The two brief requirements conflict.

## Result (both readings reported to principal; principal to pick)
- v2 incl-Wolfen, archived-rev lens: cost €6,581,868 / rev €37,666,074 / 17.47%. Monthly 18.41/17.57/16.20/17.09/17.77.
- v2 incl-Wolfen, placed-rev lens: cost €6,581,868 / rev €37,029,541 (==SCM) / 17.77%. Monthly 19.59/18.15/16.11/18.08/16.62.
- Wolfen adds: cost +€215,759; rev +€4.89M (archived) / +€4.60M (placed).
- Apr/May anchored still settling (invoice backfill).

## Open / needs principal
Pick the revenue lens for v2: archived-month (differs from SCM, but excl-Wolfen gate at 0.34pt) vs order-placed (ties v1 at 0.14pt, but rev==SCM). Recommend reporting v1 was placed-rev-lens; if v2 must have rev != SCM, the archived-lens 0.34pt gap is an explained lens shift, NOT a broken join.

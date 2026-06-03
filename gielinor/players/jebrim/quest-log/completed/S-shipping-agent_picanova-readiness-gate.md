# Shipping-agent pull — Picanova cost-savings data-readiness gate

**Actor:** shipping-agent (specialist sub-agent, Jebrim-scoped)
**Date:** 2026-05-31
**Principal:** Jebrim (via Niklavs)
**Mode:** read-only mart probe. Tier intended: gold contract (entity-ID question may need upstream — see below).

## Ask
Data-readiness gate for a Picanova-only (Picanova GmbH = EU origins, Picanova Inc. = US origins) re-rating / carrier-optimisation project. Trailing 90d from 2026-05-31, anchored on `shop_order_created_date`. Seven numbered deliverables: entity ID + row counts, origin sites, grain-column coverage (dims = key risk), cost basis split, the realistic carrier-option table (origin→carrier→service), destination spread, weight/size percentiles.

## Status — BLOCKED on live mart access
- Redshift MCP tools (`mcp__redshift__*`) are **not exposed** as callable tools in this session.
- The configured connection (`.mcp.json` redshift server; shipping-agent `harness/` + `.env`, user `tcg_nfe`) resolves the cluster to **private 10.144.x.x addresses** — VPN/internal only. TCP to `bi...redshift.amazonaws.com:5439` **times out** from this environment (general outbound is fine — google.com / public AWS endpoints connect).
- No cached/snapshot mart data locally (`data/` empty; workbench items carry recipe `CLAUDE.md` only, no frozen rows).
- Net: cannot ground-truth a single figure. Per fixture-vs-live discipline, returned NO numbers — would not fabricate. Delivered instead: the exact column/predicate map per deliverable (from the verified gold mart contract), the entity-ID gap, and a ready-to-run SQL pack so the pull is one reconnect away.

## Key finding to carry forward (independent of connectivity)
**The "Picanova entity" (GmbH/EU vs Inc./US) is NOT a documented gold column.** `reference/sources.md` defines the platform axis (`source_system`: Picturator/PicaAPI/PCS/Rewallution/ORWO) and the B2B/B2C derivation, but no legal-entity / billing-entity field. Picanova GmbH vs Picanova Inc. most likely has to be **derived from origin** — `production_site` (17 values; EU print sites + Wolfen vs the US site `PCS CMH` / Columbus) and/or `destination_country` region — NOT from a native entity column. This needs principal confirmation before any row count is trustworthy; resolving it correctly is the gate's gate. May require an upstream (`enterprise_silver`/`bronze`) check to find a billing-entity field — off the gold contract, flag if reached.

## Deliverable (outside brain)
Runnable SQL pack: `Documents/GitHub/shipping-agent/scratchpad/20260531-picanova-readiness-gate.sql` — seven blocks, one per deliverable, plus entity-discovery probes that must run first.

## Next step
Principal runs the SQL pack from a VPN-connected session (or re-invokes the specialist there), starting with the entity-discovery probes (Block 0) to settle the Picanova GmbH/Inc predicate, then Blocks 1–7.

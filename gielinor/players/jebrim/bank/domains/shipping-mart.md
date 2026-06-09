---
domain: shipping-mart
title: Shipping data mart — the gold shipping_mart contract + the shipping-agent
patterns:
  - shipping mart
  - shipping_mart
  - fact_shipments
  - fact_shipment_cost_summary
  - mart contract
  - cost_for_routing
  - ship_mart_ro
  - shipping-agent
  - talk-to-your-data
corpus:
  - bank/notes/projects/2026-05-27-shipping-mart-gold-lineage-and-access-tiering.md
  - bank/notes/projects/2026-05-23-package-dimensions-carrier-envelopes.md
  - bank/notes/projects/shipping_agent_vocab_harvest_2026-05-22.md
  - bank/notes/workflow/shipping-agent-skills-loading.md
  - bank/notes/projects/dashboard_and_shipping_agent_convergence.md
  - bank/notes/projects/shipping-mart-v1-freeze-reconciliation-2026-05-25.md
specialist: shipping-agent (subagent_type) — loads picanova/shipping-agent how_to.md §0 + reference/ by construction
freshness: 2026-05-27
synthesized: 2026-06-09
---

# Shipping data mart — the gold `shipping_mart` + the shipping-agent

The gold layer is the **entire query surface** — four facts, no joins outside the schema. **Do not reason about the mart from memory** (Jebrim CLAUDE.md hard precondition): spawn the **shipping-agent** (`subagent_type: shipping-agent`) for any pull past a one-line lookup — it loads the rulebook by construction — or load `picanova/shipping-agent` `how_to.md` §0 + `reference/{mart-contract,tables,known-dq}.md` before writing SQL or reading any figure.

## The four facts (`shipping_mart.*`)
- `fact_shipments` — wide spine (~65 cols; provider data denormalized in; `shippingprovider_extkey` = carrier service-tier/product).
- `fact_shipment_cost_summary` — per-shipment 11-bucket cost pivot; **invariant `SUM(buckets) == total_eur == real_shipping_cost_eur`** to the cent. `bkt_discounts`/`bkt_credit_note` negative; tax + customs excluded (pass-through).
- `fact_shipment_orderitems` — line-item rollup per shipment.
- `fact_shipment_invoice_lines` — per-charge-line invoice detail with `charge_bucket`.

`map_shipment_key`/`dim_shipping_providers` not needed (data is on `fact_shipments`). `fact_truck_charges` is **out of the agent's gold scope** but exists for linehaul sizing → [[2026-06-09-fact-truck-charges-navigation]].

## Cost basis (load-bearing)
- Default cost = `final_shipping_cost_eur = COALESCE(real, expected, avg)` ("the one number"). `cost_source` (2026-05-22): `'invoice'` 65% / `'expected'` 24% / NULL 8% / `'avg'` 2%. Column is `real_shipping_cost_eur` but the flag value is `'invoice'`.
- The 11 buckets derive from silver `shipping_charge_bucket_mapping`. Every query qualifies `shipping_mart.<table>` — reaching outside is a scope violation (`ship_mart_ro` denies it at the DB).

## Package-dimension gate
Carrier envelopes are hard cutoffs independent of weight (DHL Paket 60×60×120, ≤31.5 kg). **TCG volume is canvas-dominated — long/flat/narrow** (UPS-DE 2–5 kg ≈ 98×71×5 cm), busting second-side limits by design. **Any carrier-swap savings number is invalid until gated against the alternative's envelope** (the €460K→€0 lever) → [[2026-05-23-package-dimensions-carrier-envelopes]].

## The shipping-agent (the tool I query the mart with)
Standalone repo `Documents/GitHub/shipping-agent/` (relocated out of NFE 2026-05-22 to escape the CLAUDE.md walk; own `.env` + `harness/`). **Monitor vs investigator:** [[scm]] is the always-on monitor; the agent is the ad-hoc investigator — same mart, open question schema.
- **File structure:** `how_to.md` always-loaded (§0 rules + §1 "Where to find things" index + the *Skill triggers — load on cue* registry); `reference/{mart-contract,tables,sources,known-dq,coverage-audit}.md` + `skills/` load-on-cue. A skill is **inert without a `how_to.md` §0 trigger hook** → [[shipping-agent-skills-loading]].
- **Connection:** local `.env`, user `ship_mart_ro`; smoke-test `python harness/connect_redshift.py --query "SELECT 1"`.
- **Analyst trip-ups it encodes** (full set → [[shipping_agent_vocab_harvest_2026-05-22]]): `TCG` = `source_system IN ('Picturator','PicaAPI')` only (not PCS/ORWO/Rewallution — PCS is cost-only); group `shipping_provider_group` for "what's X costing", `invoice_source` for reconciliation; `db_schenker` 100% `unclassified` by design; current-MTD low %-invoiced is normal, past-30d <95% is a real coverage hole.

## Lineage + access
- Gold builds in `bi-etl/dags/shipping_mart/` (top-level DAG; `git pull origin main` before an audit). Dominant input `enterprise_silver` (cleaned carrier invoices + `shipping_charge_bucket_mapping`); `enterprise_bronze` = source orders + a few raw invoices; `dw.dim_products` + `sl_gold.dim_date`. `poc_dw` NOT read by gold.
- **Two tiers, one repo:** colleagues `ship_mart_ro` (gold-only, DB-enforced, non-bypassable); Niklavs `tcg_nfe` via a gitignored `CLAUDE.local.md` overlay → SELECT on silver/bronze/dw/sl_gold/shipping_mart. Silver/bronze is **off-contract** (raw vocab, no bucket collapse) — flag when querying there.

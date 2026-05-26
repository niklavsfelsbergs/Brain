# Jebrim — keepsake/current.md

> Read at respawn (when Jebrim is active). Pinned items that must surface every Jebrim session. Under size budget (~2k tokens). User-only; the agent proposes via `proposals/`.

## Shipping Data Mart — routing

Pinned 2026-05-22 (S028, post gold cutover). Supersedes 2026-05-21 pin.

**Schema.** Gold layer `shipping_mart` schema is the agent's entire surface — four facts, no joins outside the schema:
- `shipping_mart.fact_shipments` (wide fact, 65 cols — spine + provider data denormalized in)
- `shipping_mart.fact_shipment_cost_summary` (per-shipment 11-bucket cost pivot, invariant `SUM(buckets) == total_eur == fact_shipments.real_shipping_cost_eur`)
- `shipping_mart.fact_shipment_orderitems` (line-item rollup per shipment)
- `shipping_mart.fact_shipment_invoice_lines` (per-charge-line invoice detail with `charge_bucket`)

Cutover from `enterprise_silver.*` landed 2026-05-22 — old silver facts are **gone** (not deprecated views). `map_shipment_key` and `dim_shipping_providers` are not needed — their data lives on `shipping_mart.fact_shipments` directly. `fact_truck_charges` is out of scope.

**Shipping-agent (standalone).** Lives at `Documents/GitHub/shipping-agent/` (relocated 2026-05-22 out of NFE — escaped CLAUDE.md walk). Self-contained — runs anywhere with its own `.env` and `harness/`. Entry doc: `shipping-agent/README.md` (human) + `shipping-agent/how_to.md` (AI-facing rules + §1 "Where to find things" index). Reference content in `shipping-agent/reference/`; query methodology in `shipping-agent/skills/`.

**Connection.** Local `.env` in `shipping-agent/` with the `ship_mart_ro` user (read-only, gold-only). `harness/db.py` loads from the local `.env` only — does not walk up. Smoke-test: `python harness/connect_redshift.py --query "SELECT 1"`.

**Ground truth.** `Documents/GitHub/bi-etl/dags/enterprise_silver/shipping_data_mart/` per-folder READMEs — being repointed to gold (path stays for now). `git pull origin main` before reading the code for an audit/sanity check.

**`cost_source` values (2026-05-22):** `'invoice'` 65%, `'expected'` 24%, NULL/uncosted 8%, `'avg'` 2%. Column name is `real_shipping_cost_eur` but the flag value is `'invoice'` — naming asymmetry; future cleanup may align.

**Schema discipline.** Every query qualifies as `shipping_mart.<table>`. Reaching outside `shipping_mart.*` is a scope violation (and `ship_mart_ro` would deny it).

*Rotate out when ground-truth path moves to the gold-dag location, or scope/schema/credentials shift again, or the mart stops being a frequent topic.*

## EU Tender 2026 — active

Pinned 2026-05-21 ([[S021_2026-05-21_alching-and-rule-fix|S021]]). Source: `archive/proposals/2026-05-21_eu-tender-2026.md`.

Quantitative review of 2026 EU shipping carrier tenders for TCG-Picanova. Target: 4–6 parcel + 1 freight, cost-only scoring. Phase 2 in flight; **DPD PL walkthrough is the next concrete step.** Decisions locked 2026-05-12 (cost-only, hard cap 6, lane diagnostic + portfolio scoring). New offers landing live (DPD PL + FedEx arrived 2026-05-20). Full detail in `bank/notes/projects/eu_tender_2026.md`.

*Rotate out when tender decisions are signed and carriers contracted, OR project pauses > 1 month with no active work, OR pin grows stale relative to current state.*

## EU Tender 2026 — bottom-line assessment from [[S034_2026-05-22_eu-tender-logic-review|S034]]

Pinned 2026-05-22 ([[S034_2026-05-22_eu-tender-logic-review|S034]]). Surface to principal at every Jebrim respawn until v2 report ships OR pin grows stale. Source: `archive/proposals/2026-05-22-eu-tender-bottom-line.md`.

**The project is on a credible path to a defensible decision IF three things land before signing:**

1. **Enough Round 1 replies to flip fuel + customs + residential off proxy on at least 5 of 7 engines.** Sequencing risk — carrier replies are 1-2 weeks each.
2. **Service-quality sidecar.** One-page qualitative overlay (returns rate, claims handling, transit-time variance, account-team responsiveness) per shortlisted carrier. Bridges "Hermes scores best" and "Hermes is signable."
3. **Volume-tier rerating on the shortlisted portfolio.** §B.15. Engines price nominal-tier today; shortlisted slices cross tier boundaries.

**Biggest risk:** provisional numbers getting locked. The 2026-05-14 placeholder-vs-real fuel collapse (EUR 230k → 18k headline) is the cautionary precedent — cite explicitly in v2 methodology.

**The principal should read the full assessment** — chat transcript at end of [[S034_2026-05-22_eu-tender-logic-review|S034]], or reconstruct from `quest-log/in-progress/S034_2026-05-22_eu-tender-logic-review.md` + the 15 dwarf children in `completed/`.

*Rotate out when v2 report ships AND the three conditions have landed, OR the project pauses > 1 month with no active work, OR the pin grows stale relative to current state.*

# Shipping-agent vocab harvest — 2026-05-22 (S029)

> Recon harvest from NFE + `shipping_topics/` for things to teach the shipping agent. Six trip-up rules + glossary + paste-ready proposal for `shipping-agent/reference/` and `how_to.md`. Sibling to [[shipping_mart_cost_vocabulary_2026-05-22]] and [[shipping_costs_monitoring_nextjs_vocab]].

**Source paths walked (via Explore dwarves):**

- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carriers/{dhl_paket,fedex,austrian_post,gls,dpd_pl,maersk}` — `constants.py`, `calculate.py`, `surcharges/*.py`, `rate_tables/migrate.py`.
- `bi-analytics-main/NFE/.claude/reference/shipping-data-mart/{overview,sources,tables,mart-contract,how_to,coverage-audit,known-dq,data_model,legacy_adhoc_corrections}.md`.
- `bi-analytics-main/NFE/projects/3_shipping_data_mart/{fact_shipment_invoice_lines/sql/providers,dim_shipping_providers,dim_truck_costs}/...`.
- `bi-analytics-main/NFE/shipping_topics/*` — ~41 topic folders, sampled 6–10 deeply (README + main script).
- `workbench/shipping_topics/*` — topics 1–22 not present in NFE, sampled (tassenlibling, Asendia US, US PHX shutdown).
- Power BI: `Shop Order Info.tmdl` (production-site LIKE-patterns).

**Not walked:** `bi-etl/`, `dashboards/shipping_costs_monitoring_nextjs/` (S026 covered it), other `NFE/projects/` siblings.

---

## § 1 — Trip-ups for the agent

Six rules. Each is a place where an analyst question would land on a confidently-wrong default unless the agent is taught the rule.

### 1. `TCG` = `source_system IN ('Picturator', 'PicaAPI')` — nothing else

TCG (The TCGroup / Picanova Company Group) is the acquirer; ORWO is the acquired entity. PCS is cost-only (no revenue) and small-sample. Rewallution is small PL dropshipping via Baselinker.

- **When an analyst says "TCG":** filter `source_system IN ('Picturator', 'PicaAPI')`. Do not include PCS, ORWO, or Rewallution by default.
- **Never report standalone:** PCS (cost-only, no revenue). Rewallution surface only when explicitly asked.
- **Common wrong default:** summing all five `source_system` values when asked "what's TCG costing us." Inflates by ~73% of orderitem rows (ORWO-weighted).

### 2. Shipping cost excludes tax, customs, and duties

The mart's `total_eur` / `final_shipping_cost_eur` already exclude `tax_eur` and `customs_duties_eur`. When pulling from raw `fact_shipment_invoice_lines`, filter `charge_bucket NOT IN ('tax', 'customs_duties')`.

- **UPS `Manual Bill` / `838xxx` invoice sub-stream** is NOT freight cost — it's customs/duty/VAT/DDP/import-fee recharges (German invoice text "ZOLL- UND/ODER ZOLLABFERTIGUNGSGEBÜHREN"). The mart routes most of it into the excluded buckets; an analyst pulling raw invoice lines will hit it.
- **Common wrong default:** summing all UPS invoice lines as "shipping cost" — inflates by the Manual Bill stream.

### 3. `invoice_source` granularity ≠ carrier

`dhl_orwo` and `ups_orwo` are distinct `invoice_source` values from `dhl` and `ups`. Same carrier, different invoice provenance — bulk-bill allocation, where one carrier invoice line splits across tied shipments.

- **"What's DHL costing us"** → group by `shipping_provider_group`.
- **Reconciliation, coverage, invoice-completeness audits** → group by `invoice_source`.
- **Common wrong default:** filtering `invoice_source = 'dhl'` to get total DHL spend — misses the `dhl_orwo` bulk-bill allocation.

### 4. `db_schenker` charge bucket is 100% `'unclassified'` by design

DBS doesn't send consistent `charge_description`s. Partial mapping was rejected in favor of conservative 100% unclassified classification — this is a deliberate decision, not a defect.

- **When asked "why is DBS 100% unclassified":** state the rule, don't propose a fix.
- **Anchored:** `bi-analytics-main/NFE/projects/3_shipping_data_mart/fact_shipment_invoice_lines/sql/providers/db_schenker.sql`.

### 5. Oversize surcharge sub-types — heuristic by cost magnitude

The mart does NOT distinguish between sub-types of oversize/handling surcharges (Over max limits, large package, AHS, weight-based). All collapse into `oversize_overweight_eur`. When asked which sub-type a given surcharge is, infer from cost magnitude and carrier:

| Carrier | Surcharge magnitude | Likely sub-type |
|---|---|---|
| UPS | > €500 | **Over max limits** surcharge |
| UPS | > €100 | **Large package** surcharge |
| UPS | smaller | AHS handling or weight |
| Other carriers | any | Likely AHS handling or weight |

- **Flag as inferred.** This is guidance, not a deterministic mapping in the data.

### 6. Current-window low `% invoiced` is expected; past 30 days is concerning

Carrier invoice lag is days-to-weeks. Current month-to-date routinely shows 20–28% invoiced. That's normal.

- **Past 30 days from today:** if `% invoiced < ~95%` on the slice, treat as a coverage problem, not a temporal artifact. Investigate the wiring — missing `invoice_source` for a carrier, ETL gap, classification miss.
- **Common wrong default:** flagging current-week or current-MTD low `% invoiced` as a defect.
- **Threshold sharpened from "~90 days" to "30 days"** per principal direction, 2026-05-22.

---

## § 2 — Glossary additions

Terms the agent will encounter in questions/conversation that aren't in current docs. Definitions terse; full context in source folders.

**Corporate identity:**

- **`TCG`** — The TCGroup / Picanova Company Group. The acquirer corporate entity. In mart filter terms: `source_system IN ('Picturator', 'PicaAPI')`.
- **`ORWO`** — ORWO Photolab GmbH. Acquired entity. `source_system = 'ORWO'`. Wolfen-hardcoded production site. V1-active-build (under construction).
- **`Picanova`** — corporate brand reference, used interchangeably with TCG in some contexts.

**Source systems (lower-priority surfacing):**

- **`PCS`** — internal production system, cost-only source (no revenue). Sites: CGN, PL, MI, PX, CMH. **Do not report standalone.**
- **`Rewallution`** — PL dropshipping via Baselinker, small volume (~1K shipments), PLN→EUR FX upstream. **Surface only when explicitly asked.**

**Carriers / service tiers:**

- **`FXEHD`** — FedEx Home Delivery (~$18.27/shipment).
- **`FXESPPS`** — FedEx SmartPost (~$9.64/shipment).
- **`e-PAQ Elite DDP`** — Asendia's tracked-duties-paid express international service.
- **`DDP`** — Delivered Duty Paid (Incoterms — when it appears in context, it's the service tier).
- **`Asendia US Elite`** vs **`Asendia US Standard`** — Elite ~8× cost of Standard.
- **`Ontrac OML`** — Oversized Multi-Line surcharge ($1,300 + $550 demand). Distinct from AHS.
- **`Ontrac AHS`** — Additional Handling Surcharge; often predicted, not always invoiced.

**Acronyms / shorthand:**

- **`MD`** — Mother's Day campaign (seasonal promise-flag tracking).
- **`CMH`** — Columbus production site (PCS CMH, US-origin).
- **`PHX`** — Phoenix production site (US).
- **`FIF Report`** — UPS monthly invoice file (`YYYY-MM_Korrektur.xlsx`). Key accounts identified by 4-char reference prefix (1700/1300/1100).
- **`Manual Bill`** — UPS `838xxx` invoice sub-stream — customs/duty/VAT/DDP recharges, NOT freight.
- **`AHS`** — Additional Handling Surcharge (general term; specific to OnTrac and FedEx variants).
- **`Sperrgut`** — German term for oversize/bulky parcel (DHL surcharge: 20 EUR DE, 21 EUR Intl).

**ORWO product lines:**

- **`DD Kalender`** — Digital-Druck (digital-printing) calendar product.
- **`Premium Kalender`** — premium calendar variant.
- **`Digitaldruck`** — digital-printing product family.

**Customers / shops:**

- **`tassenlibling`** — DHL invoice customer linked to ORWO Photolab GmbH (cust #5311934365).
- **`Rossmann`** — B4-envelope user; reference example for low sperrgut rate (0.1%).
- **`Pictrs` / `myposter` / `sendmoments`** — key accounts in UPS FIF Report.

**Operational vocabulary:**

- **`Variant B`** — truck-cost allocation method, PCS internal sites only.
- **`Phase 0–5`** — orchestrator phases. Phase 5 = cost-column UPDATE.
- **`feed freshness`** — ETL-health check via `max_shipped_ts` recency per source.
- **`promise flag` / `promise cutoff`** — date-based delivery commitment used in seasonal-campaign analysis (MD).
- **`carrier shift`** — temporary or permanent volume reallocation across carriers. Often time-bounded ("clean and time-bounded" = baseline → surge → baseline within a window, no tail).
- **`V1-stable`** vs **`V1-active-build`** — source-system maturity flags. Picturator, PicaAPI (post-2025-11), PCS, Rewallution are V1-stable; ORWO is V1-active-build.

---

## § 3 — Negative space (what the mart does NOT model)

State these as "the agent should not lean on these framings" — they don't appear in the data:

- **Incoterms** (DAP/EXW/FCA/CPT/CIF/FOB/CIP). Cost-responsibility framing lives in vendor/customer contracts outside the data model. **Exception:** `DDP` appears as a service-tier name (Asendia e-PAQ Elite DDP), not as a cost-responsibility framing.
- **Returns vocabulary.** `is_returned` exists on `fact_shipments` but is undefined in V1. No RMA, reverse logistics, refused-parcel, undeliverable, return-to-sender modeling.
- **POD / AWB / BOL / SLA / KPI / ETA / ETD / LTL / FTL / PUDO.** These standard logistics-industry acronyms don't appear in NFE code. The team uses `current_shipping_status` (DELIVERED / IN_TRANSIT / etc.), `sl_shipped_ts` / `sl_delivered_ts`, `trackingnumber` — not the industry acronyms.
- **HS codes, IOSS, OSS, customs declaration, broker.** Customs is bucketed as `customs_duties` on the cost side; no commodity-classification or declaration-pipeline modeling.
- **`is_test` / `is_void` / `is_void_cancelled` flags.** No bad-data exclusion markers — quality is enforced via source priority dedup and sanity date filter (`BETWEEN '2024-01-01' AND current_date+30`).

---

## § 4 — Proposal — text to apply to the shipping-agent docs

### A. Add to `how_to.md` §0 cross-cutting rules (six rules, paste-ready)

> **N. TCG scope.** `TCG` means `source_system IN ('Picturator', 'PicaAPI')` — nothing else. PCS is cost-only with no revenue and small sample — do not report standalone. Rewallution is small PL dropshipping — surface only when explicitly asked. ORWO is a separate entity (acquired); never include in a TCG headline.
>
> **N+1. Shipping cost excludes tax, customs, and duties.** Use `final_shipping_cost_eur` / `total_eur` — both already exclude `tax_eur` and `customs_duties_eur`. When pulling raw `fact_shipment_invoice_lines`, filter `charge_bucket NOT IN ('tax', 'customs_duties')`. The UPS `Manual Bill` / `838xxx` invoice stream is customs/duty/VAT recharges, NOT freight — already routed to the excluded buckets.
>
> **N+2. `invoice_source` granularity.** `dhl_orwo` and `ups_orwo` are distinct invoice sources from `dhl` and `ups` — bulk-bill allocation, where one carrier invoice line splits across tied shipments. Group by `shipping_provider_group` for "what's <carrier> costing us." Group by `invoice_source` only for reconciliation, coverage, or invoice-completeness audits. Never filter `invoice_source = 'dhl'` and call it total DHL spend.
>
> **N+3. `db_schenker` 100% unclassified by design.** DBS doesn't send consistent `charge_description`s; partial mapping was rejected in favor of conservative 100% unclassified bucketing. When asked, state the rule — this is a decision, not a defect.
>
> **N+4. Oversize surcharge sub-types — heuristic by cost magnitude.** The mart does not distinguish between sub-types in `oversize_overweight_eur`. When asked which type a given surcharge is:
>
> | Carrier | Surcharge magnitude | Likely sub-type |
> |---|---|---|
> | UPS | > €500 | Over max limits |
> | UPS | > €100 | Large package |
> | UPS | smaller | AHS / weight |
> | Other | any | AHS / weight |
>
> Flag the inference — this is guidance, not deterministic.
>
> **N+5. `% invoiced` thresholds by recency.** Current month-to-date / current week: low `% invoiced` (e.g. 20–28%) is expected; carrier invoice lag is days-to-weeks. **Past 30 days from today:** if `% invoiced < ~95%` on the slice, treat as a coverage problem — investigate the wiring (missing `invoice_source`, ETL gap, classification miss). Don't flag a fresh window as defective.

(Insertion point: §0 cross-cutting rules. Current numbering runs through rule 7 plus the §11 cost-basis rule from `shipping_mart_cost_vocabulary_2026-05-22`. These become rules 8–13 unless rules have been added since.)

### B. Add to `reference/glossary.md` (or wherever team-vocabulary lives)

Use the entries in § 2 above. Suggested grouping:

- Corporate identity (TCG, ORWO, Picanova).
- Source systems with surfacing rules (PCS, Rewallution).
- Carriers / service tiers (FXEHD, FXESPPS, e-PAQ Elite DDP, OML, AHS).
- Acronyms (MD, CMH, PHX, FIF Report, Manual Bill, Sperrgut).
- ORWO product lines (DD Kalender, Premium Kalender, Digitaldruck).
- Customers (tassenlibling, Rossmann, Pictrs, myposter, sendmoments).
- Operational vocabulary (Variant B, Phase 0–5, feed freshness, promise flag, carrier shift, V1-stable/V1-active-build).

### C. Add to `reference/` a `not-modeled.md` (negative space, optional)

§ 3 above — the things the mart deliberately doesn't model. Saves the agent from leaning on framings (incoterms, returns, industry acronyms) that aren't in the data.

---

## § 5 — Why this note exists in Jebrim's bank

The six trip-ups and glossary are durable mart knowledge — Jebrim should know them as part of the shipping-mart vocabulary, alongside [[shipping_mart_cost_vocabulary_2026-05-22]] and [[shipping_costs_monitoring_nextjs_vocab]]. The proposal section is captured here because the shipping-agent docs can only be edited from `bi-analytics-main` — the next session in that repo applies it.

Promote during alching when (a) the proposal has been applied to the shipping-agent docs and the trip-ups + glossary are the surviving content, or (b) the proposal sits unapplied long enough that Jebrim needs the vocabulary as durable knowledge regardless.

## § 6 — Related

- [[shipping_mart_cost_vocabulary_2026-05-22]] — cost-column vocab, % invoiced euro-weighted formula, denominator-matching rule.
- [[shipping_costs_monitoring_nextjs_vocab]] — dashboard-side vocab (alert types, issue lifecycle, tier files, etc.).
- [[shipping_mart_coverage_audit_2026-05-21]] — coverage audit (ORWO POST, Picturator POST_DVF, MAERSK, ASENDIA holes).
- `bi-analytics-main/NFE/.claude/reference/shipping-data-mart/` — formal mart docs.
- `bi-analytics-main/NFE/shipping_topics/` — ad-hoc analysis tree (~41 topic folders) where corporate vocabulary lives.
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carriers/` — per-carrier `constants.py` files (surcharge taxonomy, service codes, dimensional divisors).

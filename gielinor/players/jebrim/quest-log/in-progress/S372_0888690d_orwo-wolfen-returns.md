# S372 — ORWO / Wolfen returns cost investigation + NFE topic 51

**Player:** Jebrim · **sid8:** 0888690d · **2026-06-26**

Ask (Niklavs): "We pay tons for returns for production site Wolfen — why? Specific customer, specific products, what?" Later scoped to: compute from the **raw carrier invoices** (mart has no returns section), build an NFE shipping topic + a DHL-meeting Excel.

## What happened (turn log)

- **Grounded** on Jebrim's keepsake + shipping-mart domain + the ORWO/Wolfen entity note (ORWO = `production_site='Wolfen'`). Established returns are **not in the gold mart** (UPS RTS redistributed onto outbound + >90d dropped; `is_returned` unconfirmed) → justified off-mart departure to `enterprise_silver.{ups,dhl}_orwo_invoices`.
- **Return signal:** UPS `chargecategorycode='RTN'`; DHL `prod` joined to `shipping_charge_bucket_mapping` (desc ~ retoure/rücksend/return).
- **First false trail caught:** the general `shipping_ups_returns_addition` (€245k) is the **Picanova PCS-PL** UPS book, not Wolfen — verified by account number (ORWO = 0R6D51). Wolfen UPS returns there ≈ €775.
- **The real finding:** return **rate** surged ~0.2% → 11% from **March 2026** on BOTH carriers (DHL RETOURE + UPS Rückholservice prepaid return services, from €0). Outbound volume fell → not a volume effect; pickups concurrent → not a billing backlog; both carriers same month → a deliberate **ORWO-side return program launch**, not a delivery-quality problem. Combined ~€105k Mar–Jun (~€300–350k/yr).
- **Attribution wall (proven 4 ways):** which customer/product is NOT recoverable — return tracking doesn't link to outbound order (2% match), DHL ref 96% masked `(Y)` even in bronze, UPS `sendercompanyname` uniformly "ORWO PHOTOLAB GMBH" / single account / 305 scattered postcodes. Root cause = white-label pooling. Best proxy = outbound DE brand mix (Rossmann ≈ half), labeled inference.
- **Deliverable:** NFE **topic 51** (`shipping_topics/51_orwo_wolfen_returns/`) — findings.md, sql/, build_returns_excel.py → DHL-meeting Excel (Overview+Questions, charge types, monthly trend+rate, product×month onset, May detail, **Raw invoice lines**). Committed to bi-analytics-main across `ee90a08 → e9f9590 → da23dc3 → 25ca595` (standing NFE auth, **never pushed**).
- **Correction (Niklavs): "wtf no invoice number? all columns blank."** I'd shipped the raw tab with placeholder `—` columns because the Redshift MCP was down. Fix: the MCP being down ≠ can't query — connected directly via `redshift_connector` + `tcg_nfe` creds (`NFE/.env`, host from `brain/.mcp.json`) → pulled the real 14,522 May lines (`pull_dhl_returns.py` → `data/dhl_returns_may_raw.csv`); also fixed euro format rounding to 2dp. → examine draft + memory.

## Decisions

- Cost from **raw silver invoices**, not the gold mart (returns absent there) — documented departure.
- Excel is **DHL-focused** (their meeting); UPS parallel noted in the Overview only.
- Raw tab kept **all** 14,522 lines (incl. ~7.2k €0.04 energy-surcharge lines), sorted substantive-first + autofilter.

## Pending external actions

None pending on my side. His actions (carried): send the Excel/questions to DHL Mon; ask ORWO ops what return offering went live in March + for which shops. NFE commits made under standing auth, **not pushed** (his action).

Resume: `inventory/orwo-wolfen-returns-resume__0888690d.md`.

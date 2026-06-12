---
domain: carrier-contracts
title: Carrier contracts & invoices — rate cards, terms, invoice DQ, dimension coverage
patterns:
  - carrier contract
  - rate card
  - carrier invoice
  - fif
  - fif report
  - dimension coverage
  - contract expiry
  - fuel surcharge
  - ups rate
  - dpd offer
corpus:
  - bank/notes/projects/2026-06-09-picanova-eu-carrier-contract-overview.md
  - bank/notes/projects/2026-06-09-carrier-invoice-dimension-coverage.md
  - bank/notes/projects/2026-06-09-carrier-measured-vs-passthrough-dims.md
  - bank/notes/projects/2026-06-09-ups-old-vs-new-rate-card-diff.md
  - bank/notes/projects/2026-05-28-ups-orwo-fif-data-quirks.md
  - bank/notes/projects/2026-06-02-fif-vat-subtotal-grain.md
  - bank/notes/projects/2026-06-09-fif-report-vs-ups-portal-export.md
  - bank/notes/projects/2026-06-09-fact-truck-charges-navigation.md
  - bank/notes/projects/shipping-contract-corpus.md
  - bank/notes/projects/2026-06-11-austrian-post-public-indices-dhl-demand.md
  - bank/notes/projects/2026-06-11-fedex-pl-fuel-fx-remote-area-mechanics.md
  - bank/notes/projects/2026-06-11-fedex-q1-2026-fuel-history.md
  - bank/notes/projects/2026-06-11-hermes-destatis-diesel-fuel-mechanics.md
  - bank/notes/projects/2026-06-11-maersk-row-fedex-pl-public-surcharges.md
  - bank/notes/projects/2026-06-11-ups-de-2026-published-surcharges.md
  - bank/notes/projects/2026-06-11-ups-invoice-charge-profile.md
  - bank/notes/projects/2026-06-11-ups-oml-lps-negotiated-thresholds.md
  - bank/notes/projects/2026-06-11-ups-residential-and-peak-surge-mechanics.md
  - bank/notes/projects/2026-06-11-ups-new-offer-vs-today-cost-drivers.md
  - bank/notes/projects/2026-06-12-dpd-pl-contract-export-only.md
specialist: shipping-agent (full-access tier reaches bronze/silver raw invoice tables for reconciliation)
freshness: 2026-06-12
synthesized: 2026-06-12 (corpus +1: DPD-PL export-only served set)
---

# Carrier contracts & invoices

The carrier-relationship layer beneath [[eu-tender]]: contract terms, rate-card reading, invoice data-quality, and which carriers expose real dimension data. Source-of-truth for offers/contracts: **`bi-analytics-main/NFE/docs/shipping_contracts/`** (`0. OLD/` superseded, `1. EU/`, `2. US/`) — gitignored binaries, no git-history recovery; look here first.

## Classify the doc before reading a date (load-bearing)
A headline date is **not** auto an expiry — the document *type* decides → [[2026-06-09-picanova-eu-carrier-contract-overview]]:
- **Offer** (rate card seeking acceptance) → date = **sign-by / acceptance window**, not when rates stop. (DPD PL "valid till 31.01.2026" = sign-by; it *was* signed → 2026 rates live.)
- **Executed contract** (term clause) → date = real term window.
- **Issued price list** (German *Preisliste*) → date = **effective-from**, open-ended.

**Contract status (2026-06-09):** Maersk auto-renews → term to 30.07.2027 (notice window closed); UPS indefinite, 30-day notice, **discount-off-published-tariff so GRI flows through**; DHL Paket Preisliste renewed 03.01.2026; DPD PL signed; DPD UK to 21.11.2026 (planned drop, 3-mo notice by ~21.08.2026); Yodel expired 31.01.2026; GLS/PostNord dropped. **No active carrier locks against rate increases** — each has a review or pass-through.

## Reading a rate card — the rate-TYPE column, not just the value
UPS card "Fuel Surcharge = 35, *Percent Off*, Net Rate NA" is a **35% discount off the floating published index**, not a flat 35% (same type as Free Domicile "80 Percent Off") → effective fuel ≈ `index × 0.65`; invoice-reconciled effective fuel/base ≈ **19–20%** road. The 2026 UPS offer's +5% on Standard-light ≈ **one GRI** (parity vs a GRI'd incumbent); zones unchanged, Expedited new, WW-Economy absent → [[2026-06-09-ups-old-vs-new-rate-card-diff]]. Diff identical-layout cards to isolate the *negotiated* change clean of GRI drift; split light vs heavy (a flat mean-across-bands inverts the picture).

## Invoice data-quality (FIF / UPS ORWO)
The FIF report = UPS monthly invoice file → [[2026-05-28-ups-orwo-fif-data-quirks]] + [[2026-06-02-fif-vat-subtotal-grain]]:
- `invoicedate` stored inconsistently (ISO + some US `M/D/YYYY`) — **always `invoicedate::date`** for bucketing.
- **VAT is a separate `'19.000 % Tax'` row, not a column**, keyed by tracking; a shipment's charges + VAT can split across two invoices (327xxx freight / 838xxx customs) → per-invoice VAT fold ≠ whole-month.
- FIF report reproduces bronze to the cent; the **UPS portal export double-counts** charges on trackings with a package-dimension join fan-out → [[2026-06-09-fif-report-vs-ups-portal-export]]. *Disagreeing totals → suspect grain mismatch before "dropped data."*

## Dimension coverage (raw upstream, off-contract)
Of ~21 carriers: **~10 carry real measured dims, 5 oversize-billing-signal only, 3 (DHL feeds) nothing** → [[2026-06-09-carrier-invoice-dimension-coverage]]. **Audit method:** profile the *widest bronze source* + charge-DESCRIPTION **values**, not a narrow silver table's column names (a name-scan false-negatived ~14 carriers). **A populated column ≠ an independent measurement** → [[2026-06-09-carrier-measured-vs-passthrough-dims]]: Maersk reprints OUR declared L/W/H verbatim (passthrough); Yodel only 6.9% populated; verify provenance (exact-equality test, dual-field trap) before claiming "full coverage."

## Fuel-index mechanics by carrier (2026-06-11 research picks)
Each carrier floats fuel off a **different public index** — never reuse one number across carriers: **Hermes** → Destatis Grossverbraucher diesel, reply-ladder bands (0% ≤122.7, +0.5%/2.578pt; the *offer* ladder is a retired 2015-base trap, ~1.26×) → [[2026-06-11-hermes-destatis-diesel-fuel-mechanics]]; **FedEx PL** → three *independent* indices (Intl = jet fuel, Regional = EU diesel — one number can't serve both), 2-week lag empirically confirmed, band tables in [[2026-06-11-fedex-q1-2026-fuel-history]] + [[2026-06-11-fedex-pl-fuel-fx-remote-area-mechanics]]; **UPS** → weekly Mondays, EC diesel (road) / USGC jet (express), 2-week lag → [[2026-06-11-ups-de-2026-published-surcharges]]; **Austrian Post** → BMWET prev-month-max diesel TKZ tiers (own 0–32% card non-public) → [[2026-06-11-austrian-post-public-indices-dhl-demand]]; **Maersk ROW** lanes = Maersk base + FedEx public surcharges → [[2026-06-11-maersk-row-fedex-pl-public-surcharges]]. **UPS ground truth (12-mo invoices):** ~€235k/yr billed by charge types NOT in the cost model (peak/demand ~€191k); oversize must be read NET (UPS reverses ~54% in place); seasonal €0.20/pkg Base Rate Surcharge + standing Over-Max €440 survive partial waivers → [[2026-06-11-ups-invoice-charge-profile]]. **2026-offer mechanics:** OML 400 (reply) vs 419 (negotiated) allowance, LPS 101.80 assumed, residential flat €0.40 (carrier-confirmed), peak residential-gated → [[2026-06-11-ups-oml-lps-negotiated-thresholds]] / [[2026-06-11-ups-residential-and-peak-surge-mechanics]]; offer-vs-today cost-driver decomposition (~73% base/GRI, ~19% residential, fuel neutral; CH/GB operative-tier is the residual gap) → [[2026-06-11-ups-new-offer-vs-today-cost-drivers]].

## Re-rating discipline
Reconcile a re-rate against the unit's ground-truth actuals before reporting a delta (a new flat fee can flip a near-zero delta's sign); test for a real lever (negotiated discount / contract term) before fitting an engine parameter (DPD's sheet-vs-invoiced gap was a ~9% discount, not a divisor). Linehaul/truck sizing → `shipping_mart.fact_truck_charges` (volume-weight over a full demand cycle) → [[2026-06-09-fact-truck-charges-navigation]]. Trust-gate detail lives in [[eu-tender]]; spawn the **shipping-agent** for the actuals pulls.

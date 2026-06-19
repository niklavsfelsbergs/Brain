# S279 — ORWO tender: roadmap + Phase-1 UPS cost-basis validation

**sid8:** 6fbdcee1 · 2026-06-19 · continues [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]] (tender kickoff). This session's increment: the 5-phase roadmap + Phase-1 UPS pipeline profiled and the rate card **validated**. Parent tender thread [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]] stays in-progress.

## Ask (Niklavs)
"Continue on ORWO tender." Explain the repricing-base approach, then build Phase 1 (UPS). Locked design calls: mart spine, UPS first, base-rate-first. Then: write a full roadmap. Build it ("yep"). Close the base-rate gap. Price against invoice lines only. Then update all docs + proper handover + wrap.

## Done this session
- **`roadmap.md`** (NEW, `7_ORWO_tender_2026/`): 5-phase plan-of-record — objective, reframe, locked decisions, cost-basis mosaic, phases 0–5, chase list, risks, deliverables.
- **`repricing_base/`** (NEW): `sql/01_ups_tracking_base_reconciliation.sql` + `findings.md`. UPS tracking-grain pipeline profiled + validated end-to-end, live.
- **Updated** `_scope.md` (plan → roadmap; resolved Qs) and the bank/inventory resume.

## Verified facts (live, Redshift MCP, read-only)
- **Grain:** 128,805 UPS shipment rows → 34,001 trackings (3.79:1 consolidation). 5 dest countries: DE 91.8%, AT 5%, UK 2.7%, FR 0.5%, NO trace.
- **Cost = invoice lines** (Niklavs' call, locked). Mart `SUM(real)` per tracking == silver `SUM(netamount)` (€7.16 vs €7.27) — equal-split, SUM correct — but the **mart `base_rate_eur` bucket is bundled/consolidated/RTS-redistributed**, so it is NOT the contract base. Price off silver charge lines.
- **Card VALIDATED:** actual invoiced forward freight (`Dom. Standard` line) matches the contract net card to the cent by band — 3–5 kg €3.26 vs €3.26; 5–10 kg €4.14 (blend); 10+ kg €5.77 vs €5.79. Fuel ~18% of base + residential €0.40 reconcile; oversize = NULL-for-most LPS/Overmax tail.
- **One parcel population:** DE UPS ORWO = 99.6% normal parcels avg ~6.5 kg (68.6% are 3 kg+); no light-mail stream.

## Corrections this session (verify-the-thing paid 3×)
1. **"Silver invoices span ~Jan–Apr"** → WRONG (Niklavs caught: "I see Jan–June"). Parsed `invoicedate` (275k ISO + 485 slash) = **Jan–Jun 2026**; my read conflated order-month match-taper (lag + lower bound) with the invoice window.
2. **"Modeled base under-prices invoiced base by 50–85% (rate-card gap)"** → WRONG. The €5.41 "actual base" was the **mart `base_rate_eur` bucket** (bundled + consolidation-summed), not the contract base. Against silver `Dom. Standard` lines the card matches exactly. Self-caught by tracing to charge lines.
3. **"Big cheap sub-gram ~€0.97 mail stream, segment it out"** → WRONG (Niklavs' "what's the share?" caught it). A **line-level `actualweight<=1` filter dropped each parcel's freight line**, leaving fuel+VAT companions — normal parcels looked like €0.97 mail. At tracking grain, genuinely-cheap = 49 trk = 0.4%, ~0% cost.

## Decisions (Niklavs)
- Mart spine / UPS first / base-rate first (design calls).
- **Cost basis = INVOICES ONLY** — drop the mart real cost as a source.

## Pending external actions
None pending. (NFE `7_ORWO_tender_2026/` committed under standing NFE auth; brain committed at close.)

## Next increment (carried in resume `orwo-tender-resume__abfcf511.md`)
Build the per-tracking **invoice-line base table** (forward freight `Dom. Standard`/zone + fuel/surcharge layer), gate vs the card, then template onto DHL (Phase 2). Chase items: AT-Post Factsheet, 2026 Güll card, GLS quote, UPS fuel index.

## Cascade
NFE `7_ORWO_tender_2026/` (roadmap + repricing_base + _scope edits) under standing NFE auth. Brain: this quest-log entry + resume update + 2 examine drafts + comms OPEN/CLOSING. No mart writes (read-only). bi-etl 5ab0322c2 still local-unpushed (his push, [[S266_e455d12d_orwo-box-grain-quota-estimator|S266]] carry-over). Parent [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]] stays in-progress (tender umbrella).

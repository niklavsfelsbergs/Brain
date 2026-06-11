# S201 — GLS old vs new offer comparison (sid8 3389aeeb)

**Quest.** EU tender: Niklavs surprised GLS isn't competitive — old contract cost was good.
Compare new tender offer vs old contract to explain why it got worse.

## Turns

- **T1 (2026-06-11).** Respawn as Jebrim. Grounded: eu-tender + carrier-contracts digests, S196
  resume (result-investigation context). Located the material: new offer = `1_offers/picanova/GLS/`
  (276a159AiC, engine gls-2.0.0); old contract line = `docs/shipping_contracts/0. OLD/EU/GLS/`
  (276a45fi26: 2024 contract, 2025 MPI card, 2026 continuation conditions) + current-folder
  `1. EU/1. PICANOVA/GLS/GLS Contract Picanova 2026.pdf`.
- **T1 cont.** Built `1_offers/picanova/GLS/comparison/` (extract_old_cards.py +
  compare_old_vs_new.py + findings.md). Extraction spot-verified vs PDFs; 52/52 EBP countries
  align; tender stack reconstruction ties to engine output +0.00%.
- **T1 findings.** Same Q1 parcels: 2025 terms €2.67M → tender €3.07M = **+14.9%**; tender is
  **+8.7% above GLS's own 2026 continuation**. Bridge: +5.7% GLS annual uplift / +€97k base-card
  re-shape / +€148k stack (new 4.1% Dieselfloater, Klima 1→2.5%, EFTA 19.50→25). Structural:
  old card was FLAT 2–25 kg (AT 4.11, DE 4.14 @15–25kg); tender is steep per-kg (DE 25kg +190%);
  95% of EBP parcels dim-weighted → heavy bands = canvas slice; EBP 5–8 kg +50.7% biggest block.
- **T1 pending.** Shipping-agent (background) pulling GLS invoiced history: volume end-date +
  effective total/base ratio to validate the old-stack model. Status: `pending` at spawn.

## Artifacts (bi-analytics, UNCOMMITTED — principal-gated)

- `1_offers/picanova/GLS/comparison/{extract_old_cards.py,compare_old_vs_new.py,findings.md}`
- `comparison/data/old_cards.parquet`, `comparison/out/{base_rate_diff,q1_scenarios,q1_by_country}.parquet`

- **T2 (2026-06-11).** Shipping-agent returned: GLS volume ended 2025-07 (wind-down Aug, last scan
  2025-10-01); old book NL+AT 83% / DE 3%, ~1.4kg light export, ~EUR4.5/parcel. Old-stack model
  VALIDATED vs invoices: non-DE stack/base 28.8% actual vs 29.2% modelled; DE toll EUR0.380 exact.
  Appended appendix to findings.md (caveat 6 resolved). Bank draft written:
  bank/drafts/notes/projects/2026-06-11-gls-old-vs-new-offer-why-worse.md. All 4 tasks complete.
  Open: bi-analytics comparison/ files uncommitted (principal go pending); shipping-agent flagged
  a mart charge-bucket-mapping gap (GLS stack lands in Unclassified) — surface if GLS recurs.

- **T3-T4 (2026-06-11).** Niklavs follow-ups: (1) old-book countries specifically -- yes, all worse
  (NL +16.5%, AT +24.8%, BE +30.5%, DK +25.8%; only the 1-2kg billable band improved anywhere);
  (2) why -- base rates, ~80-85% of it (entry band +20-30% + flat 2-25kg abolished), stack a uniform
  +3.7%. Both persisted into findings.md ("Follow-up: the old-book lanes"). Accepted ("ok got it").
- **T5 (2026-06-11).** Close. No pending external actions. Shipping-agent trace graduated ->
  completed/S201_3389aeeb_sa_gls-invoiced-groundtruth.md. Resume in inventory (open_dep:
  bi-analytics commit go). Harvest: 1 bank draft (gls-old-vs-new-offer-why-worse). Cascade: none --
  comparison/ is additive; carrier_overview/decision/routing reports untouched (GLS engine
  unchanged). Main-brain changes: quest-log + inventory + bank draft + comms + intent only.

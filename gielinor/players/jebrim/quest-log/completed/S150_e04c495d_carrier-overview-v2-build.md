# S150 (cont., sid8 e04c495d) — Carrier Overview v2: build + "vs today" baseline

Continuation of the S150 carrier-overview quest (design born e59202cf; v2 plan + v1 build born d691c033). This session executed the v2 rebuild end-to-end, then extended it with a 2026-Q1 actual-invoice "vs today" baseline. Deliverable lives in `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carrier_overview_v2/`. **All work committed to bi-analytics `main` (5 commits); NOT pushed.**

## What happened

**Part 1 — v2 build (Phases 0–7), principal handed full autonomy.**
- Phase 0: 8 decisions signed (X=10%+gap, fold<2%, no cap/flag>7, **single-source dropped**, keep 9 lanes, friendly+predicate names, full-yr vol + Q1 cost, girth re-derive).
- Phase 1: 9 dwarves extracted verified contract boundaries → `verification/phase1/`; I reconciled each against `constants.py`.
- Phases 2–4: segment model (lane × weight × dim-class) + competitive map off the cost matrix; 52 material segments; every winner-flip contract-explained, no unexplained flips. Density dropped as an axis (93% low-density = constant). Tested finer grids — the mean-vs-argmin divergence is intrinsic, don't fragment.
- Phase 5: 9-dwarf hands; Phase 6/7: synthesis + self-contained HTML. v1 marked SUPERSEDED.
- Commit `e475efb`. (Also recovered + committed the lost `5_shipping_savings` project from stranded WIP `36636a5` — `94d4130`; caught a gitignored-rate-data defect.)

**Part 2 — the "vs today" baseline (principal-directed, iterative).**
- Q: do the new offers beat what we pay today? First wired the recovered current-contract re-rate engines (maersk_eu/ups_eu) → **validated they under-price 20–35%** vs real invoices (UPS engine €4.62 vs actual €7.12). Demoted them.
- Switched to **2026-Q1 actual invoices** (shipping-agent mart pull → `data/actuals_2026q1.parquet`; `sql/20260605-01_*`): UPS + Maersk + DB Schenker, PCS PL, `real_total_eur` (excl tax/customs). Commit `f70226c`.
- **Carrier-identity correction:** Maersk FR = `shippingprovider_extkey` MAERSKFR (NOT Colis Privé — I wrongly trusted the engine header). Maersk FR launched Jan 2026 (107 in 2025 → 27,624 in Q1-2026 @ €4.72), so the 2025 population couldn't show it.
- Full document pass (`beb32aa`): vs-Today column per segment, decision KPI + callout, 9 hands rewritten (real wins vs hollow), DB Schenker freight block, methodology + ledger.
- **UPS LPS/OML treatment** (`b3904ee`): OML (oversize >€400, refunded) netted out; LPS (≤€400, real) kept. UPS today €8.08→€7.57; 1 verdict flip.
- Hand number-sync to OML-adjusted cards (`510fc67`). Document internally consistent.

## Headline finding
Tender beats today on **33/46 segments (~89% of book)**, **fails on ~11%** — **France entirely (keep the current Maersk contract €4.72)** + CH/ROW bulky tail. Switch: DE core→DHL Paket, IT/Iberia/Nordics-DK→new Maersk, Benelux→DPD.

## Principal confirmations this session (carry into the report + next phase)
1. **New carriers (Hermes/FedEx/DHL Express) will NEVER be invoice-measured** — we only get invoiced after signing. So "validate before banking" is wrong framing: the modelled cost is the only basis pre-signature; it's irreducible model risk, not a closable gap. **→ report new-carrier caveat should be reworded next session.**
2. Güll: awaiting carrier response (HELD confirmed).
3. Maersk FR: recent but we keep it.
4. UPS LPS is a real overcharge ("UPS fucks us with LPS") — kept; OML refunded → netted.
5. DB Schenker stays — nothing else can take freight.

## No pending external actions.
All mart pulls completed; all commits landed; nothing awaiting an external system.

## Cascade
- The canonical EU-tender `docs/` + per-carrier status tables were NOT touched this session (v2 is a self-contained re-cut). If v2 supersedes v1 as the carrier-relationship deliverable, a docs pointer update is a candidate next-session cascade item — low priority.
- v1 `carrier_overview/PLAN.md` already marked SUPERSEDED.

## Main-brain changes
None. All writes were to `bi-analytics-main` (separate repo) + this brain quest-log/inventory/comms. No `gielinor/meta`, ritual, or hook changes.

## Open / next phase — PLANNED + LOCKED (handover ready)
**Final carrier setups (portfolio scoring) on a 2026-Q1 actuals basis.** End of session: discovered the **decision report already scores portfolios** (`decision_scorer.py` §B.13 state model INCUMBENT/NEW_OFFER/OFF, cap 6, savings vs Σ real invoices) — but on the stale 2025 basis. Wrote the authoritative phase plan: **`bi-analytics .../2_analysis/decision_report/PLAN_final_setups_2026q1.md`** (committed `17c0249`, decisions `4478c73`). Phases A (2026-Q1 cost matrix, full pull → engines + real invoices, OML-netted; Maersk-FR fix falls out) → B (re-point scorer, drop [[S120_3760e65b_eu-tender-full-year-build|S120]] reprice hack) → C (reconcile) → D (score setups) → E (summarize in overview).
**Decisions LOCKED (principal):** (1) Maersk = two carriers (`maersk_current_fr` incumbent + `maersk_eu_new`); (2) NO bias correction — tender engines firm/face-value (the 20-35% under-pricing was the SAVINGS re-rate engines, not the tender engines; Güll alone HELD); (3) volume basis = 2026-Q1.
A detailed handover prompt was delivered to the principal (chat) for the fresh session. Also queued: the new-carrier-caveat reword across the overview. Resume points to the PLAN.

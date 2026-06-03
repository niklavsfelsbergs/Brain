---
quest: S148_eu-tender-dhl-paket-round2
sid8: 104c786b
ts: 2026-06-03 12:20
open_dep: FedEx Round-2 rebuild + fuel-history pull queued for next session
---

# Resume — EU Tender DHL Paket + FedEx Round-2 (S148)

**Status:** in-progress · session 104c786b · 2026-06-03 · DHL Paket DONE, FedEx reviewed-only
**Quest:** `quest-log/in-progress/S148_104c786b_eu-tender-dhl-paket-round2.md`

## Where we are
DHL Paket Round-2 carried fully through: `dhl_paket-2.0.0` built, full-year matrix + decision_scorer + report + cross_carrier all regenerated, §B.24 cascade landed. FedEx Round-2 reviewed only (blockers closed, rebuild deferred). **Everything UNCOMMITTED, principal-gated.**

## Engine deltas (dhl_paket-2.0.0)
- `FUEL_PCT_DE_ENERGY` 2.5%→**1.25%** (confirmed flat schedule).
- PiP window (11,28)/(12,2)→**(11,24)/(12,7)** (confirmed 2025; 2026 = Nov 23–Dec 6 in comment).
- Bulky trigger UNCHANGED — **confirmed correct** (any-side>60); €2.31M Q1 / €11.62M FY is real.
- 20/20 fixtures pass. FY total €25.10M→€25.12M (energy −€70k, PiP +€90k).

## What we still assume (DHL Paket) — documented in REVIEW_CONCLUSIONS + ASSUMPTIONS + DECISIONS
1. Thin-flat Sperrgut waiver — **upside-only**, pending Stefan. (Engine prices full Bulky now.)
2. Intl TCS = 5%-of-base proxy, NOT the confirmed per-country €/kg (~€600 Q1, immaterial; 12 countries only).
3. TCS 2025 monthly history — non-blocking (Q1 covered by 01.01.2026 values).
4. Volume re-pricing tiers (Q8) — deferred to Stefan (§B.15).

## Next concrete step
**FedEx rebuild → `fedex-2.0.0`** (the other Round-2 carrier; reviewed, blockers closed):
- Wire RE vol-weight divisor = **5000** (all services); two-index fuel (Regional→RE, International→IE) on **base+surcharges** scope; FX = billed PLN → ECB conversion (4.234 interim); ODA/OPA tier postcode map from `round_2/ODA_OPA_tiers_codes (1).xlsx`.
- **Still open for FedEx:** pull fuel Q1-2026 monthly %s self-serve ("Show all weeks" on the surcharges page); customs per-parcel "Clearance Fees" amount → rephrased re-ask (or documented assumption). Current week values are 49.25% IE / 22.50% RE (June — NOT Q1; don't lock these as Q1).
- Then re-run cost_matrix + decision_scorer + report.

DHL Paket: only fold in the thin-flat waiver outcome if/when Stefan confirms (upside-only).

## Commit plan (when principal says go)
- bi-analytics-main (separate repo, on main @ a0902cc): `git commit -- 2_analysis/carriers/dhl_paket 2_analysis/data/cost_matrix 2_analysis/data/scenarios.parquet 2_analysis/decision_report 2_analysis/cross_carrier_view.html 2_analysis/docs "carrier_responses_to_open_questions/..."`. Pathspec-only (S131 #1 hazard; shared dirty tree).
- brain (this repo): `git commit -- gielinor/players/jebrim/quest-log/in-progress/S148_104c786b_*.md gielinor/players/jebrim/inventory/eu-tender-dhl-paket-round2-resume__104c786b.md gielinor/comms/active.md`.

## Files to read first (next session)
- `carrier_responses_to_open_questions/fedex/REVIEW_CONCLUSIONS.md` + `round_2/fedex_2` + the 2 screenshots + the ODA/OPA xlsx.
- `2_analysis/carriers/fedex/` engine + `2_analysis/docs/technical/engines/fedex.md`.
- DHL Paket Round-2 block in its REVIEW_CONCLUSIONS.md for the assumptions ledger.

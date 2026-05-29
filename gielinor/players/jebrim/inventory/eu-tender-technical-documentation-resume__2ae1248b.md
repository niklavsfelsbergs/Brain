# RESUME — EU Tender 2026 technical documentation + audit fixes — S121 (2ae1248b)

**Status:** DONE + COMMITTED + PUSHED to origin/main (tender 36ee4fa). Quest S121 complete.
**Repo:** out-of-tree `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis`. Tender on origin/main @ `36ee4fa` (rebased onto the dashboard work, clean). Brain on origin/main.

## What S121 delivered
**Full technical reference** (`docs/technical/`, 15 files) as a **document-as-audit** pass (principal-chosen: stable-first, parallel dwarves):
- README (index + per-engine template), 01-architecture, 02-engine-framework, 03-scorer, 04-report, engines/{9 carriers} (6 deterministic full-depth via 6 parallel dwarves + 3 held-lite by me), 05-audit-findings (register).

**Audit fixes** (principal chose "fix everything + re-run"; all verified vs fixtures + a full pipeline re-run — do_nothing=€0 PASS, baseline €14.85M unchanged, headline renew_maersk_plus_hermes €634,959 ≈unchanged, drop-DPD route €732k→€726k):
- **A1** DHL Express pickup denom re-baked Q1→full-year (PICKUP_WEEKS 13→52, eligible 184,273→956,968; €0.538→€0.414/parcel). Fixtures 26/26.
- **A2** DHL Express demand window (1,1)-(2,16)→(10,1)-(2,16) wrap (adds Oct–Dec 2025 leg).
- **A3** Maersk ROW fuel → base + ROW AHS (EU stays base-only).
- **A4** Maersk ROW oversize/overweight → exclusivity group (Q11 highest-only); fixture updated; 17/17.
- **A5** GLS Season date-column guard (defensive); 12/12.
- **B1–B10** doc-drift (ASSUMPTIONS Hermes fuel Feb0%/Mar7%, DPD customs €484k-Q1→€2.32M/yr basis + GB opt-2, AP FX +3.2%; hermes/dpd code comments; report Hermes "11 assumptions" reword; maersk/gls CLAUDE.md staleness pointers; FUEL_SUMMARY rows; dpd CLAUDE.md wiring).
- **B11 DEFERRED** (maersk fixtures.py docstring + compare_to_phase1 parity — dev-doc hygiene, zero impact; tracked in 05-audit-findings.md).

## Deferred / residual (in 05-audit-findings.md)
- A1 deeper runtime-allocation ideal (fixtures bind the constant symbolically).
- A4 fuller ROW AHS re-model (Dimension-as-billable-uplift + separate Oversize tier + AHS-Packaging).
- B1/B2 full maersk/gls CLAUDE.md body refresh (pointer banners added now).
- B11 maersk fixtures docstring + parity-tool baseline.
- Cross-engine PEAK validation (maersk EU + hermes Q4 first fire on full-year — check vs peak-season invoices when available).

## COMMIT (done)
Tender 36ee4fa (32 files, pathspec-scoped, rebased + pushed origin/main). scenarios.parquet + data/cost_matrix/ gitignored (build intermediates). Brain: jebrim quest-log S121 + 6 dwarf traces + this inventory + comms.

## Next concrete step
Nothing blocking. The technical reference is the durable artifact; remaining residuals (above) are tracked in 05-audit-findings.md for a follow-up. Carrier round-2s (FedEx/DHL-Paket/Güll/UPS) still flip the held sets from provisional when they land.

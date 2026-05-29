# Shipping-agent: known-issues register live re-verify

**Actor:** shipping-agent (sub-agent, Jebrim namespace)
**Date:** 2026-05-28
**Tier:** gold-contract (`shipping_mart.*`, read-only via Redshift MCP). Maintainer profile (`tcg_nfe`) present but no query reached upstream — all 12 rows are gold-contract.

## Ask
Re-verify Jebrim's 12-row `shipping_mart` known-issues register (built from `reference/known-dq.md`
+ `coverage-audit.md`) against the LIVE mart. Per row: STILL-ACCURATE / DRIFTED / RESOLVED. Used the
embedded re-verify probes (per-extkey carrier-ts NULL probe; coverage Probe 1/2). Source-scoped
(exclude ORWO/PCS/Rewallution) on carrier-event coverage.

## Result (headline)
12/12 verified. None RESOLVED, none fully invalidated. Mostly STILL-ACCURATE.
- **DRIFTED:** Row 1 bare-`DHL` (NULL 96–99%→~75–89%, volume 84K→~1K/mo); Row 1 `DHLWPKT`
  (100%→~62%); Row 8 DHL2/DHLKP attribution (not ORWO-only — material Picturator volume too; ORWO
  DHL2 ~672K not ~522K).
- **Count drifts:** POST_DVF ~183.7K→190.5K; NULL-extkey ~12.7K→10.2K; USPS 151K→153.5K @ 98.1%→97.7%.
- **STILL-ACCURATE:** Rows 2 (DPD UK delivered 100% NULL), 5 (is_returned 67.3% pop, 2 vals), 7
  (PCS/Rew/ORWO 100% NULL), 9 (PicaAPI 3–6%/10–14%), 10 (db_schenker 100% unclassified), 11
  (production_site='Other' near-zero — 83 rows/~2.5M; framing now stale), 12 (workhorses low-NULL).

## Checks
- Bare-`DHL`: confirmed the drift via per-month trajectory (clean early-2025 → ~95% late-2025 →
  ~75–89% 2026), so the full-2025 aggregate (49.1%) is a misleading read — recent/monthly is truth.
- Current-month (May 2026) NULL/coverage runs hot on normal lag — used Nov2025–Apr2026 steady-state.
- Source coverage Probe 1 reconciles with coverage-audit (Picturator 91.6%, ORWO 73.8%, PicaAPI 94.8%).

## Flags for principal
- Row 1 bare-`DHL` contradicts known-dq's "stable, growing" reading.
- Row 8 exclusion list must name DHL2/DHLKP for Picturator too, else a source-scoped carrier
  scorecard inherits the by-design null.
- Patch list of 7 rows needing number/status changes handed back in the report.

## Deliverable
Full findings returned to Jebrim as chat text (harness blocked the workbench `findings.md` write;
content delivered in the return message). Intended workbench home was
`shipping-agent/workbench/analysis/20260528-known-issues-register/findings.md`.

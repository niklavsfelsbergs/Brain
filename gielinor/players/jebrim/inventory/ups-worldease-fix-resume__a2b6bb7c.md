---
quest: ups-worldease-column-fix-and-rerun
sid8: a2b6bb7c
ts: 2026-06-26
open_dep: FIX APPLIED + VALIDATED (CH engine base 12.01->7.64, total 9.79 vs invoiced 9.68 = +1%, was +56%); doc warnings placed; CASCADE RERUN is the next + irreversible step (checkpoint with principal pending)
---

# Resume — UPS World Ease column fix + tender cascade rerun

## The finding (root cause)
The EU-tender UPS engine prices **CH (Switzerland) on the wrong rate column**. CH has two
columns in `DE E-Standard Single`: c25 "PP / TP" (normal lane, €12.01) and c26 "WE PP + TP"
(**World Ease**, €7.64). `extract_rates.py` `STD_COL_ISO2` maps CH→c25 and explicitly skips the
WE columns ("v1 uses the primary lane"). We actually ship CH on **World Ease** — invoiced base
€7.48 ≈ WE €7.64 (old card WE €7.28). So the engine overstates CH base by ~€4.5/pc (€12.01 vs
€7.64), which inflated the "CH 48% gap / operative-tier overprice / €135k outflow / hard-to-retain"
reads and likely mis-routed CH off UPS.

World Ease isn't a modeled service — it's a rate VARIANT (extra Standard columns + a separate
`DE E-Express Saver_WE` sheet the extractor never reads). Engine prices 4 service sheets and picks
cheapest, but takes ONE column per country in Standard → dropped WE for CH.

## Option (a) lane reconciliation — DONE (full book, invoiced base vs engine base)
- **CH** — ratio 1.61, in scope. THE fix (World Ease). ~62k shed parcels.
- **DK** — ratio 1.46, in scope but EU/no-WE; invoiced flat ~€5.2 vs card €7.64+ = a DK negotiated
  flat-rate discount, NOT World Ease. ~€7k/yr, immaterial. NOTE for later, not this cascade.
- **GB** — ratio 2.48, OUT of tender scope (not in cost matrix). Hygiene only.
- US/CA/AU/JE — WW-Economy stays_current=100%, engine base not comparable. Not affected.
- All other EU lanes ±10% — correct.
- LI/NO have a WE column but priced identical to normal (€14.36) — no impact.

## Plan (approved 2026-06-26; "warnings now / numbers last", "stop at no-Hermes ops routing")
1. ✅ Option (a) full lane reconciliation.
2. ⏳ Doc safety stubs (warnings only) — NFE repo (extract_rates.py, comparison/findings.md,
   carrier_engines/ups/CLAUDE.md, ups_retention_levers.md) + gielinor (draft/approve:
   bank/notes/2026-06-11-ups-engine-vs-current-cost-corrected.md + ups-routing-keep-vs-offer note,
   bank/domains/eu-tender.md). No numbers yet.
3. Fix `extract_rates.py` — WE as candidate lane min(normal,WE) where distinct WE exists (CH;
   audit LI/NO/GB-704); wire `DE E-Express Saver_WE`. Re-extract. VALIDATE CH per-parcel ≈ invoiced
   BEFORE downstream.
4. Re-run cascade via `regen_all.py` → engine → cost_matrix → routing → final_stats → no-Hermes v2 +
   no-Hermes ops routing report. The `base_ann==976023.94` regen gate WILL move — re-baseline
   DELIBERATELY only after confirming the delta is entirely CH→WE (+ any CH routing flip). CHECKPOINT
   with principal before this irreversible step.
5. Finalize docs with corrected numbers + quest-log + this resume. Commit (NFE per-change standing
   auth, ASK first; gielinor at close). NEVER push.

## Key files
- `1_offers/picanova/UPS/calculation/extract_rates.py` (STD_COL_ISO2 + ZONE_SHEETS — the fix)
- `1_offers/picanova/UPS/calculation/output/replay.parquet` (real_* = invoiced, ups_* = engine)
- `1_offers/picanova/UPS/comparison/data/diff_standard.parquet` (old vs new base per band)
- `2_analysis/regen_all.py` (the orchestrator + €976k gate)
- card: `Documents/Shipping/1. EU/1. PICANOVA/UPS/Picanova UPS Rate Card 2026.xlsm` (old) +
  `1_offers/picanova/UPS/offer/...NEU.xlsm` (new). WE = "WE PP + TP" in row 16.

## Reproduce CH proof
Old WE €7.28 / new WE €7.64 / invoiced base €7.48 (11,269 Q1 parcels, all Standard, avg 1.25 kg).
Engine (wrong) €12.01. WE column = c26 in DE E-Standard Single; engine used c25.

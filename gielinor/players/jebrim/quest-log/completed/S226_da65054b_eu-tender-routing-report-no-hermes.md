# S226 — EU tender: no-Hermes routing report

**Player:** Jebrim · **sid8:** da65054b · **2026-06-12** (crash-resumed mid-build)

Resume state → `inventory/eu-tender-routing-report-no-hermes-resume__da65054b.md`.

## Ask

Niklavs: where does the routing report stand vs `final_report_no_hermes_v2`, and should we
build a `routing_report_no_hermes`? He wanted the **package × dest × weight-band** view ("what's
going where") as a **full report, scoped to the no-Hermes scenario**.

## What I found (the architecture answer)

Two different report families, and the no-Hermes side only had one:
- **`routing_2026q1/` (routing report)** = the executed-plan cell table (one carrier per
  dest×packagetype×weight band) — exactly the "what's going where" grid, but the 6-carrier
  **with-Hermes** portfolio (`FINAL_6` baked into `build_final.py`).
- **`final_report_no_hermes_v2/`** = the no-Hermes *savings narrative*. It re-runs a true
  no-Hermes routing internally (`build_stats_no_hermes.py` monkeypatches the engine to FINAL_5)
  but emits only carrier-level aggregates — the per-parcel routing is thrown away.
- So **no no-Hermes routing table existed.** The no-Hermes routing was *computed* every stats
  run, just never *rendered* at cell grain.

## Decisions (both via AskUserQuestion)

1. **DBS-oversize treatment = pinned to freight** (conservative €976k basis); the +€696k/yr
   UPS/DHL reroute shown as a gated caveat, not the headline.
2. **Build = parametrize `build_final.py`** (not a fork), per the repo's "one routing, synced
   lockstep" rule.

## What I built

- **`build_final.py`** parametrized: `build(final, pin_dbs, out_dir, scenario)`. Defaults
  **verified numerically identical** (with-Hermes plan untouched — saving €395,197.18, etc.).
  Std-track DBS pin = force-keep DBS-dominated cells on freight; variable-track DBS pin =
  per-parcel. `python build_final.py no_hermes` → FINAL_5 + DBS-pinned grid.
- **`carrier_envelopes.py`** parametrized (`data_dir`) → no-Hermes §03 carrier view.
- **`routing_report_no_hermes.py`** — dedicated renderer (matching the repo's own
  `report_no_hermes_v2.py` precedent), reusing CSS/JS/table-builders, re-narrated for 5
  carriers, reading no-Hermes data + the reused physical envelope + the €696k reroute caveat.

Output: `routing_2026q1/no_hermes/routing_report_no_hermes.html` (717 KB, 1,877 rules).

## Numbers / reconciliation

- Q1 saving **€209,028** / annual **€976,024/yr**; 5 carriers; DBS retained 9,175 on freight
  (saving 0); €696k/yr reroute = gated upside, excluded.
- Reconcile to the no-Hermes final report: **do-nothing + parcel count (531,194) exact**;
  Q1 saving within **€3,280** — the ~226 non-DBS parcels in DBS-dominated cells that follow the
  cell onto freight (a cell commits to one carrier; the savings idealisation splits them
  per-parcel). The operational whole-cell gap, stated on-page in §07, not hidden.

## Verification

- Default `build_final.py` re-run = scalar-stats identical to canon (regression PASS).
- No-Hermes grid CSV = exactly the 5 carriers, 531,194 parcels.
- HTML: 0 Hermes routing rows, 5 portfolio cards, 0 unrendered f-string placeholders.

## Pending external actions

None pending. **bi-analytics committed `9d171a2`** (pathspec-scoped: `build_final.py`,
`carrier_envelopes.py`, `no_hermes/`; not pushed). Two throwaway probe files
(`_probe_dbs.py`, `_probe_dbs2.py`) left for Niklavs to `rm` (brain delete-guard blocked me).

## Cascade.

None — self-contained build on top of the already-shipped no-Hermes final report. The eu-tender
domain digest could later reference the new routing_report_no_hermes artifact, but no edit was
load-bearing this session.

## Main-brain changes.

This is a main-brain (gielinor/Jebrim) session; no dev-brain changes.

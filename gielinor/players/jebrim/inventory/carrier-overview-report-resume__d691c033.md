---
quest: carrier-overview-report (EU tender — manager-facing carrier report)
sid8: d691c033
parent_sid8: e59202cf
ts: 2026-06-03 17:30
open_dep: BUILD COMPLETE — awaiting principal review of the 2 HTML + commit decision
---

# Resume — Carrier Overview Report (EU tender, manager-facing) — BUILD DONE

**Status:** BUILD COMPLETE this session (d691c033). Spec was locked in S150 design session (e59202cf). All work self-contained under `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carrier_overview/`. UNCOMMITTED (principal-gated, separate repo).

## What got built (matches PLAN §0 tree exactly)
- `lib/lane_taxonomy.py` — 9-lane map + neutral 3-profile lens + Q1 basis (single source of truth).
- `lib/cost_slices.py` — materialises `_data/` slices (lane/profile position, cheapest-share, incumbent baseline, envelope overlay, carrier-vs-invoice). Contender gate: coverage ≥30% AND ≥200 parcels. **Re-run `python lib/cost_slices.py` to refresh `_data/` if engines change.**
- `sections/<carrier>.md` × 9 (dwarf deep-dives, §4 6-element template).
- `build_report.py` → `carrier_overview.html` (full, 173 KB) + `exec_brief.html` (1-2pg, 26 KB). **Re-run `python build_report.py` to regenerate the HTML after editing sections.**

## Verified (verify-the-thing)
- Independent recompute off the raw cost matrix (bypassing cost_slices) for DE/IT/CH/AT matches to the digit.
- HTML: all 9 sections embedded, 0 raw-markdown leak, 41 tables rendered, winners badge-flagged inline.

## Cross-carrier headline (corrected against data — 3 briefing priors were wrong)
- DE (67%) → **Hermes** cheapest avg €4.16 **(provisional** — pre-Hermes baseline; today's DHL invoice €3.28 sits below it). DHL Paket per-parcel cheapest on ~1.49M DE Compact parcels. Profile flips: DHL Paket Compact / Hermes Bulky-standard / GLS Large.
- FR → GLS · Benelux + Nordics → DPD PL · AT → **Güll (held)** · IT + Iberia → Maersk (gross-weight edge) · CH → **Austrian Post** (€8.66, beats UPS incumbent) · ROW → **DHL Paket** (NOT FedEx — FedEx dearest on ROW).
- FedEx / DHL Express never lead on €/parcel — coverage / reach plays.

## Next concrete step
1. **Principal:** open `carrier_overview.html` + `exec_brief.html`; review. Spot-check any carrier section vs the master matrix.
2. **Commit** (principal go): pathspec-scoped — `2_analysis/carrier_overview/{lib,sections,_data,build_report.py,*.html}` in bi-analytics (separate repo, on main, NOT pushed); brain trace (S150 quest-log + this resume + comms + dwarf siblings). Mark S150 → completed/ on commit.

## Known caveats baked into the report (not bugs)
- Hermes provisional (soft baseline); Güll held (no Round-2, guell-1.0.0 ceiling) — both flagged inline.
- Raw engine cost, bias not baked; year-1 rates only; volume-tier rerating out of scope (per spec).
- Profile lens uses neutral `max(weight_kg, volume_cm3/5000)` — NOT any carrier's billable (first cut had a carrier-specific-dim bug, fixed + sections refreshed).

## Optional follow-ups (new work, not blockers)
- Service-quality sidecar (transit/claims) — out of cost scope per spec.
- Güll: convert held ceiling to firm once a Round-2 offer lands.
- Re-validate Hermes savings on a Hermes-inclusive window (Q2 2026) before banking.

---
quest: cost-structure-card (EU-tender carrier-overview v2) + Warenpost engine add
sid8: f4a07849
ts: 2026-06-08
open_dep: S165 card+Warenpost COMMITTED (d54836d). S166 routing service-split (f82b01df) BUILT+verified, NOT committed (awaiting go) + Part 6 overview-annotation optional/pending. decision_report still stale vs matrix (DISREGARDED per principal).
---

# Resume — Cost Structure card + Warenpost engine addition (carrier-overview v2)

## Warenpost engine addition (dhl_paket-2.0.0 → 2.1.0) — DONE, big blast radius
Sized the Warenpost exclusion (~169k parcels / 5.9% book / ~€0.5M/yr DHL overstated on light-EU), principal said build. Added Warenpost Intl Std + Premium as a 5th/6th DHL service:
- `carriers/dhl_paket/extract_rates.py` +extract_warenpost → rate_tables/{warenpost_std_formula,warenpost_premium_formula,zones_warenpost}.parquet (NEW).
- `carriers/dhl_paket/{constants.py,calculate.py}` +service, eligibility (≤1kg, 35.3×25×10 envelope, ex-USA), unit+per-100g pricing, no Toll/CO2, no fuel; ENGINE_VERSION→2.1.0. `surcharges/toll_co2.py` excludes Warenpost.
- tests: 22/22 pass (3 fixtures flipped to Warenpost, 2 added).
- **Re-ran the full-year cost_matrix (12 partitions, 25.9M rows)** — REALIZED: 168,753 Warenpost parcels, DHL intl ≤1kg €7.29→€6.25 (€475k/yr saving, matched the sizing).
- Re-ran carrier_overview_v2 pipeline (competitive_map→build_summary→build_hand_cards→probe→report). 9/9 cost-structure verify clean.

## ⚠ Stale-downstream flag (needs S150 coordination)
The cost_matrix is shared. I re-ran it, so **decision_report/ (S150) + routing_2026q1/ now reflect PRE-Warenpost DHL costs** — stale vs the matrix. I did NOT re-run them (avoid clobbering live S150). DHL's light-EU position improved (~€0.5M); the decision report must be re-run in a coordinated S150 pass to pick it up. The EU-tender keepsake "track doc updates / Step-8 cascade" applies.

## ROUTING SERVICE-SPLIT — BUILT in S166 (f82b01df), NOT yet committed
Parts 1–5 of `PLAN_routing_service_split.md` done + verified (full record: quest-log `S166_f82b01df_routing-service-split-build.md`).
1. ✅ Regenerated cost_matrix_2026q1 (Warenpost in) + derive_envelope (must-freight 165).
2. ✅ Residual removed: quantified 8,396 (PostNord SE, all std, all ≥1 in-scope bid, 0 unserved) → 0 stranded after the fix; the "no in-scope carrier" edge does NOT occur (no dead path added).
3. ✅ service carried through build_final (FAMILY_TO_ENGINE + with_service); rules band-merged on (carrier,service), assignment gains service; two-Maersks split clean (FR carrier-only). 1,985 rules, no explosion.
4. ✅ service_labels.py (23 keys verified vs live matrix).
5. ✅ Service-split display: routing-table Service column+filter, portfolio Products, what-each-takes Products line, dim-table Service column. Carrier-level smoothing kept (90.7% fidelity; (carrier,service)-smoothing rejected — cost 15pts, contradicts locked "carrier top-level"). Direct Link gone except migration FROM (truthful source).
Saving €411,344 (13.9%), up from €399,750/13.5% pre-Warenpost.

6. ✅ Part 6 — carrier_overview_v2 winner-service annotation (modal service per segment winner; no re-key; all 52 annotated).
**COMMITTED** bi-analytics `f47098d` (14 files, pathspec-scoped, NOT pushed). EXCLUDED non-mine dirty: decision_report.html, validation/db_schenker/* (S164), _decision_sets_2026q1.py + decision_scorer_2026q1.py + report_2026q1.py + switch_list_2026q1/ (S150 untracked).

**OPEN:** (a) **push** — awaiting go (main ahead 19). (b) ⚠ _decision_sets_2026q1.py untracked but imported by committed build_final.py — S150's to commit.
Decisions locked: residual→reroute-to-next-active; full split routing-report-only; overview=annotate-only; UPS/DBS/Maersk-FR carrier-only; authored labels. Revert point = d54836d.

## Where we are (cost-structure card)
Built and verified. Each of the 9 carrier pages in
`bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carrier_overview_v2/carrier_overview.html`
now ends with: a hand-written **## Cost structure** prose overlay (eligibility
narrative + every position's trigger) followed by an auto-rendered **Rate-card
ledger** (every position · amount · fires-on incidence% · season/exclusivity/
fuel-class tags · "varies" for tiered) + a **worked example** + a collapsible
**full rate card** (the rate-table grids). Engine-only, internal-analyst,
hedged. Verification harness: **9/9 clean**.

## Next concrete step
1. **Principal review** the rendered `carrier_overview.html` (open in browser;
   pick any carrier, scroll to the bottom two cards).
2. **Commit** (asked, not yet done) — pathspec-scoped to `carrier_overview_v2/`
   only (bi-analytics `main` is dirty with sibling work — db_schenker, UPS,
   decision_report — do NOT sweep). Never push.

## Files
- `carrier_overview_v2/lib/cost_structure.py` — engine introspection (NEW).
- `carrier_overview_v2/lib/_cost_structure_probe.py` — verify + worked example (NEW).
- `carrier_overview_v2/build_report.py` — +render_cost_structure +CSS (MOD).
- `carrier_overview_v2/sections/<9 carriers>.md` — +## Cost structure prose (MOD).
- `carrier_overview_v2/verification/cost_structure/<slug>.md` — audit (NEW).
- `carrier_overview_v2/_data/cost_structure/<slug>_example.json` — examples (NEW).
- `carrier_overview_v2/PLAN_cost_structure.md` — full build record + decisions (NEW).

## Notes
- Decisions: triggers in prose (no engine edits) · incidence included · worked
  example yes · exec_brief untouched (its diff is only a regenerated timestamp).
- Regenerate: `python carrier_overview_v2/lib/_cost_structure_probe.py` then
  `python carrier_overview_v2/build_report.py`.
- Prose does NOT auto-sync; engine change → rewrite that section (version stamped).
- Engine-owner observations (not fixed, out of scope): stale docstrings in
  fedex/calculate.py + dhl_express/remote_area.py — see PLAN_cost_structure.md.

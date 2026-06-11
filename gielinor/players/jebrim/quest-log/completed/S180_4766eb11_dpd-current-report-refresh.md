# S180 — EU-tender report refresh: UPS +5% GRI wiring + DPD-current incorporation

**Player:** Jebrim. **Session:** 4766eb11. **Opened:** 2026-06-09. **Status:** deliverable complete; commit gated on principal go.
Continuation of [[S178_09c2d809_dpd-pl-current-engine]] (built the `dpd_pl_current` engine) and the [[S175_6c5170d1_routing-cost-basis-review|S175]] routing-cost-basis plan (which flagged the UPS GRI). Picks up [[S178_09c2d809_dpd-pl-current-engine|S178]]'s left-open "where do we incorporate this engine" + the unwired UPS GRI.

## Ask

Pick up the DPD-current report refresh: wire the UPS +5% GRI into `build_final.py`, rerun routing, leave FR per engine, then update the three EU-tender reports (routing_report, carrier_overview_v2, decision_report) to the kept-DPD-on-current-contract + post-GRI basis. Commit engine + GRI + reports as one unit on principal go.

## What happened (turn log)

1. **Grounding + a false-alarm location check.** Niklavs flagged the files might be wrong-repo; verified `bi-analytics-main` on `main` is the canonical EU-tender tree (all 3 bi-analytics worktrees share the same origin; main carries the latest tender commit). Resolved — right place.
2. **UPS +5% GRI wired** (`routing_2026q1/build_final.py`). UPS is incumbent-only (no engine), so its forward keep/bid IS its forward price → added `UPS_GRI_PCT=0.05` and a `today_eur_fwd` column (UPS parcels ×1.05) used in the standard keep cost, variable inc_v bid, and the per-parcel floor. Baseline `today_total` stays GRI-free Q1 actuals (the established tender basis). [[S171_c4e56024_ups-fuel-basis-and-gri-sensitivity|S171]] confirmed the UPS contract floats on its published tariff (no GRI cap), so the GRI genuinely flows through.
3. **Rerun + verified.** Saving **13.4% → 12.8% (€395k → €377k)**; baseline unchanged €2.955M. UPS sheds ~12,500 parcels (retained 42,276 → 29,781); IT/ES do **not** flip (Maersk dominates IT 23,825 / ES 13,581, zero DPD); DPD grows 83,454 → **88,985**. GRI decomposition: do-nothing forward would absorb €56.5k of GRI on the €1.13M / 149k-parcel UPS book; the optimized portfolio absorbs only €17.6k → re-routing avoids €38.9k. Headline framing locked (principal): **vs Q1 actuals, decomposed** (12.8% headline; engine's +€17.3k offset by the −€17.6k retained-UPS GRI).
4. **Engine-value reframe (principal Q).** Split DPD's 88,985 book: 61,356 retained vs **27,629 cross-carrier capture** the engine can price but actuals-only never could (22,343 pure engine value pre-GRI + ~5.3k GRI tipping). Became the lead narrative pillar.
5. **routing_report.{py,html}** — updated DPD card (current kept, tender declined, cross-carrier capture, FR/near-PL not IT/ES), UPS card (€10.48 avg post-GRI, ~119k migrate), subtitle, summary bullets (DPD + GRI decomposition), methodology, stale France caveat (DPD now wins FR; Maersk-FR-extension ~€60k predates the engine → flagged re-estimate). HTML regenerated.
6. **carrier_overview_v2** — principal chose **DPD PL (current)** as a full independent competing entry. Rebuilt full-year `data/cost_matrix/` (2025, 12 parts) — `cost_matrix.py` `_ENGINES` already had `dpd_pl_current` → picked it up; **verified zero drift** on the other 9 (penny-identical), added cleanly (15.30M cost_sum, below tender's 17.28M). Tagged `current` in `competitive_map.CURRENT`, regenerated competitive map + summary. **DPD-current = #1 winner: 16/52 segments** (incl. 7 off its own declined tender sibling). Registered in `build_report.py` + wrote `sections/dpd_pl_current.md`. Tender `dpd_pl` card → "declined" banner.
7. **decision_report re-score** — confirmed stale (Jun 5, pre-engine). Re-ran `decision_scorer_2026q1.py` (auto-picks up `dpd_pl_current` via `_decision_sets_2026q1`) + `report_2026q1.py`. **`renew_dpd_pl` −€2,258 → +€68,245**. Reframed DPD blurb (retirement-candidate → keep) + CH-viability wording. 68/82 scenarios shifted up.
8. **Sibling-card reconciliation.** Found the cards were **already partly drifted from the grid** pre-change — so most "loses to DPD" claims survive either engine. Genuinely-false fixes: **guell** ("wins all of AT" → loses AT ≤1 std to DPD-current at €3.66, beating even held/under-priced guell) + **dpd_pl tender** (declined banner). One-line clarifiers on dhl_paket/gls/fedex. HTML rebuilt.
9. **Pre-commit diligence** — engine gate −0.4%, 11/11 fixtures. Assembled pathspec commit scope; surfaced 2 scope questions (untracked decision-track files; excluded parallel-session dirty files).

## Decisions

- **Headline basis = vs Q1 actuals, decomposed** (principal). Not forward-do-nothing (14.4%).
- **DPD-current in carrier_overview = full data-layer grid competitor** (principal), accepting the full-year matrix rebuild + 16-flip restructure.
- **decision_report re-scored in-unit** + **sibling cards reconciled now** (both principal-confirmed).
- FR left per engine (over-prices vs Chronopost actuals → saving is a floor). Annualisation deferred.

## Pending external actions

- **The bi-analytics commit is PENDING principal go** (+ confirmation of the two scope questions). All bi-analytics deliverable files are complete but UNCOMMITTED (principal-gated, separate repo). Nothing else pending.

## Pending drafts

None embedded — harvest written to `examine/drafts/` (surfaced at close).

## Cascade

- **Brain (sid8 4766eb11, committed this close):** this quest-log entry, `inventory/dpd-current-report-refresh-resume__4766eb11.md`, 1 examine draft, comms OPEN+CLOSING, intent marker.
- **bi-analytics-main (SEPARATE repo, UNCOMMITTED — principal-gated):** `carriers/dpd_pl_current/*` + `carriers/PLAN_dpd_pl_current_engine.md` + `cost_matrix.py` + `_decision_sets_2026q1.py` (engine + registration, from [[S178_09c2d809_dpd-pl-current-engine|S178]]); `routing_2026q1/build_final.py` (GRI); `routing_2026q1/{routing_report.py,routing_report.html,routing_stats.json}`; `carrier_overview_v2/{build_report.py, lib/competitive_map.py, sections/dpd_pl_current.md (new), sections/{dpd_pl,dhl_paket,gls,fedex,guell}.md, carrier_overview.html, exec_brief.html, verification/phase3_reconciliation.md}`; `decision_report/{report_2026q1.py, decision_report.html}` + `decision_scorer_2026q1.py`. Regenerated parquets gitignored.
- **Main-brain changes (gielinor/):** none beyond this session's own quest-log/inventory/comms/examine-draft.

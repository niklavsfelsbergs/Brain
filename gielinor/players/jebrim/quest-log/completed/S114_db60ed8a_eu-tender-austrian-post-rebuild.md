# S114 — EU Tender 2026 austrian_post-2.0.0 rebuild

**Session:** db60ed8a · 2026-05-27 · Jebrim (principal)
**Continues the engine-rebuild batch** (maersk-3.0.0 S102 → hermes-2.0.0 S103 → dhl_express-2.0.0 S104-live). Picking up the **next unclaimed engine** while jebrim-e50113ed (S104) finishes dhl_express.
**Repo:** out-of-tree `Documents/GitHub/bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carriers/austrian_post/`

## Goal
Rebuild `austrian_post-1.0.0` → `austrian_post-2.0.0` on confirmed Round-1 reply values (PLAN §B.7.c/d), per `carrier_responses_to_open_questions/Austrian Post/REVIEW_CONCLUSIONS.md`. Then it feeds the downstream `cost_matrix.py` re-run (run once all rebuilt engines land — coordinate with S104). maersk-3.0.0 + hermes-2.0.0 are committed reference patterns. FedEx + DHL Paket HELD (round-2).

## Build scope (from REVIEW_CONCLUSIONS "Engine to-do")
- **Keep:** gross-only (Q2 ✓✓ retires dim-weight risk), PEAK=0 (Q5), 21–29kg round-up forward-asof (Q7), Off-Limit=0 (Q8).
- **Q12 CH customs** — flip `CH_CUSTOMS_INDIVIDUAL_EUR 0.0 → 1.00`, wire a CH-only surcharge node (fires regardless of ZAZ; settles the cross-carrier ZAZ inconsistency: Maersk waives, AP doesn't).
- **Q3 CH FX** — monthly multiplier = prior-month avg EUR/CHF ÷ 1.06 baseline, keyed on `shop_order_created_date` month. ECB: Dec 1.0716 / Jan 1.0784 / Feb 1.0940 (→ Jan orders ×1.011, Feb ×1.017, Mar ×1.032; +1.1%/+1.7%/+3.2%). Re-scales CH leg only.
- **Q4 Sperrgut groß** — trigger on **length >100cm** (incl. square tubes), 7.80€. Currently cuboid-overflow within L+girth≤360; tighten to the carrier's stated ≤100cm-standard / >100cm-Sperrgut rule.
- **Q1 AT fuel** — keep **4% Q1 baseline** (D5); AP's own 0–32% D-card NOT public → no defensible monthly ladder (don't fabricate precision — hermes-style call). Flag 12% (Iran spike) as sensitivity. Still chase the D-card.
- **Q6 Maut** — €0.29 flat; flag the in-Q1 0.27→0.29 transition (≈0.02€/parcel) as a replay residual.
- **Q9 CH rate** — ⚠️ replace the **Wolfen→CH proxy** (rates.parquet paket_ch_hd, 35 bands €6.65–15.80) with the actual **Stettin→Hohenems = Stettin→Salzburg** card (offer line 139).
- **Q10/Q11 line-haul (§B.7.d)** — DECISION PENDING (see below). Depends on parcels-per-pallet density (internal, ~€0.75–4.50/parcel). dhl_express precedent = model-as-flagged-ASSUMPTION.

## Turn log

### Turn 1 — respawn + pickup + scope
Respawned Jebrim (cue "Hey Jebrim, another session is almost finished with Hermes... pick up the next one"). Grounded: comms tail + S103/S104 quest-logs + both engine-rebuild resume notes. Mapped the referent — the live sibling (e50113ed/S104) is finishing **dhl_express** (the engine after hermes; hermes shipped clean S103 @990d61c), so the next *unclaimed* engine is **austrian_post**. Posted OPEN to comms (heads-up to S104; different carrier subdir, no overlap). Grounded the austrian_post spec: REVIEW_CONCLUSIONS (12 Qs all answered) + current engine (constants/calculate/surcharges/rate_tables) + maersk/hermes patterns + population schema (has date + zipcode). Scope mapped (above). Surfaced the build plan + the Q10/Q11 line-haul decision to principal.

### Turn 2 — principal: "assume it" → austrian_post-2.0.0 BUILT + verified
Principal ruled line-haul = MODEL as flagged ASSUMPTION (dhl_express precedent). Grounded the two data needs: carrier reply (12 answers) + offer CLAUDE.md line-haul table + Preisblatt row 138/139 (Stettin→Salzburg 226/345/459/506/599; Stettin→Hohenems blank → per Q9 = same Stettin rate) + _base framework. Wired all 7 build steps:
- **constants.py** — ENGINE_VERSION 2.0.0; CH_CUSTOMS 0.0→1.00; CH FX dict (prior-month EUR/CHF ÷ 1.06: Jan ×1.011 / Feb ×1.017 / Mar ×1.032); SPERRGUT_LENGTH_CM 100; line-haul (599/5 ÷150 ×1.04 = €0.8306/parcel) — all 3 sub-assumptions (rate tier, density 150, DSV diesel 4%) flagged; kept FUEL_PCT_AT 4% (Q1 point est, D-card not public); Maut 0.29 (0.27 early-Q1 flagged).
- **sperrgut_at.py** — trigger → d_max>100 (longest dim), within L+girth≤360 (Q4; replaces cuboid-overflow, more lenient on W/H).
- **customs_ch.py** (NEW) — 1.00€ on every eligible CH/LI, regardless of ZAZ (Q12).
- **linehaul.py** (NEW) — flat €0.83/parcel on every eligible AP parcel (AT+CH share Stettin rate; FX-exempt).
- **calculate.py** — `_apply_ch_fx` rescales CH base by per-order-month multiplier (Q3), after eligibility/before surcharges; AT untouched; docstring + input contract (+shop_order_created_date) updated.
- **surcharges/__init__** — registered CustomsCH + LineHaul in ALL.
- **fixtures + test_engine** — +shop_order_created_date, +expected cols; updated all existing totals; added CH-FX (Jan/Mar), Sperrgut 100/101 boundary, Q4 width-overflow-leniency fixtures.

**Verify: 19/19 fixtures PASS.** Full-pop smoke (528,721 rows) CLEAN: 32,812 eligible (6.2%; AT 23,326 + CH 11,430 serviced), components reconcile EXACTLY to €245,154.32 (base 172,041.59 FX-rescaled + fuel 4,220.01 + maut 6,716.69 + sperrgut 24,788.40 + diesel_ch 482.55 + customs_ch 9,651.00 + line_haul 27,254.08 + peak 0). LINE_HAUL on all eligible; CUSTOMS_CH on all 9,651 CH-eligible; FX months Jan–Mar. **AP cost moves UP on rebuild** (customs + line-haul + CH FX now fire), per review thesis.

**FINDINGS for principal:**
1. **Sperrgut fires on ~3,178 AT parcels (13.6%, €24,788)** under the length>100 rule — the 2nd-largest component. Plausible for Picanova's large-format print mix but worth a product-mix confirm (the rule is now more lenient on W/H, stricter is unlikely the issue).
2. **Line-haul €27,254 is the single biggest add and is fully an ASSUMPTION** (density 150). Sensitivity: density 50 → ~€82k; density 200 → ~€20k. The real density is Picanova ops' to set (Q10).
3. **93% of population is `country_not_served`** — expected (AP is the AT/CH/LI specialist; only bids its lane).

**Doc:** austrian_post/CLAUDE.md refreshed (I/O, phases, surcharges, FX/line-haul/Sperrgut sections, validation incl. smoke, open items, version history 2.0.0).

**Repo state:** HEAD now `146e9ed` (S104 dhl_express committed — sibling finished). My 9 austrian_post files (7 M + 2 new) clean to commit on top, pathspec-scoped. **Commit HELD for principal go** (per global "ask before committing"). Downstream `cost_matrix.py` re-run + ranking shift still pending (runs once all rebuilt engines land).

### Turn 3 — committed; cost_matrix deferred (2 more carrier replies landed)
Principal: "just commit" — declined the immediate cost_matrix re-run because **answers came in from 2 more providers**; we'll fold those in and continue from there. Committed `austrian_post-2.0.0` → tender **`e8ddc62`** (9 files, +390/-114, `git commit -- <pathspec>` over the austrian_post subtree only; ~86 unrelated WIP files in the tree untouched, local-only no push). Subtree now clean.

**All 4 deterministic-ready engines rebuilt + committed:** maersk-3.0.0 (3b86d6a), hermes-2.0.0 (990d61c), dhl_express-2.0.0 (146e9ed, S104), austrian_post-2.0.0 (e8ddc62, this). cost_matrix.py re-run + ranking shift NOT run — deferred until the 2 new replies are reviewed (and likely their engines rebuilt), so the ranking reflects the fuller picture. FedEx + DHL Paket still old/HELD (round-2). S114 stays in-progress: the open thread is now the 2 new carrier replies (which 2 TBD — candidates from S099 close: DPD PL / GLS / Güll / FedEx round-2 / UPS offer) → Round-1-style reply review, then rebuild + cost_matrix.

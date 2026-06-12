# S221 — EU tender no-Hermes v2 report: review Q&A session

- **sid8:** eec4ee99
- **Date:** 2026-06-12
- **Actor:** Jebrim (principal)
- **Status:** in-progress
- **Subject:** principal reviewing `final_report_no_hermes_v2/report_no_hermes_v2.html`, asking questions about its figures. This is the running Q&A log for that session.

## Q&A

### Q1 — What does "Carrier-level rates" mean for DPD Poland? (1% of its 659,511 €/yr)

**Answer.** It's a rate-model-grain label, not a DPD product. The §02 service-mix table splits each carrier's annual volume by `(family, service)` from `routing_assignment.parquet`. Most DPD-PL parcels resolve to a named service (Direct — home delivery 96%, MIX — home delivery 3%). The 1% are parcels routed to / kept on DPD with a **null service**, because no eligible service-level row priced them — so the report's `svc` lambda falls back to the generic "Carrier-level rates" label (`report_no_hermes_v2.py:80`; DPD wasn't in `SVC_NULL`).

**Where the null comes from (traced end-to-end):**
- Service is joined from the 2026-Q1 cost matrix, keyed `(shipment_id, engine)`, filtered to `eligible & service.is_not_null()` (`build_stats_no_hermes.py:76-81`). No eligible service row → null.
- Of the **1,943 Q1 null-service DPD parcels** (≈7,871/yr, the rounded 1%), the reject reasons on their `dpd_pl_current` rows are: **`country_not_served` — 1,806 (93%), all destination PL**; **`over_max_weight` — 137 (7%)** (heavy tail up to ~31 kg).
- They're still counted in DPD volume because routing is per **cell** (`country × packagetype × weight_kg`) and DPD is their **current incumbent** — the cells are kept on DPD via the do-nothing path (`q1_base.py:101-117`), even where the engine can't price the parcel.

### Q2 — It's mostly PL? And it's just not in the contract?

**Answer.** Yes to both, verified against the engine (not just the reject label). The DPD-PL current-contract engine's served set is 29 countries (`carriers/dpd_pl_current/constants.py:38-43`): AT, BA, BE, BG, CH, CZ, DE, DK, EE, ES, FI, FR, GB, GR, HR, HU, IE, IT, LT, LU, LV, NL, NO, PT, RO, RS, SE, SI, SK. **PL is not on it** — the modeled contract is an **export book** (Direct to 6 countries, MIX to 29); DPD-PL → Poland **domestic** isn't a priced lane in the offer sheet (`docs/shipping_contracts/.../DPD PL Offer 2026.xlsx`). The 1,806 PL parcels *are* shipping on DPD today (kept as incumbent), so Picanova does move PL-domestic on DPD — the extracted 2026 sheet just doesn't carry a domestic rate. Not a model bug; a rate-card coverage gap.

**Follow-up flagged:** if the PL-domestic lane should read cleanly, that's a "get/extract the DPD-PL domestic rate card" task. Not yet actioned.

## Action taken — DPD label change

On principal cue, relabeled the DPD null-service row from the generic "Carrier-level rates" to **"Poland — not in contract"** in `report_no_hermes_v2.py` (added `"dpd_pl"` to `SVC_NULL`, line 79) + matching legend clause. HTML regenerated (25 KB), renders clean. **Uncommitted** in bi-analytics (separate repo, commit-gated; never push).

## Action taken — restore the carrier-to-carrier flow matrix (§03)

Principal flagged the no-Hermes v2 report was **missing the "Reroute — volume moved to a cheaper carrier" flow view** (the from→to matrix grouped by source carrier, reprice/reroute rows). The content pass ([[S219_e0eb59c8_eu-tender-final-report-content-pass|S219]]) had pointered it out, but v2 still *computed* `matrix_table` and orphaned the variable. Restored: inserted the v1 intro paragraph + `{matrix_table}` into §03 after the split table, reworded the trailing legend (dropped the "lives in the Q1 routing report" pointer), and corrected the docstring. Regenerated HTML (31 KB, was 25 KB), renders clean — 5 source groups (UPS / DHL Paket / DPD / Maersk / DB Schenker) with reprice + reroute rows. **Uncommitted** (commit-gated; never push).

## Action taken — make no-Hermes v2 standalone (in progress)

Principal: v2 should read standalone, not as a "companion to the main recommendation." Fixed the 4 hard cross-references to the main report in `report_no_hermes_v2.py`:
- §00 lede (l.347): "This is the companion to the main recommendation…" → "The recommendation: a five-carrier base portfolio, Hermes declined." + defined "oversize parcel module" inline (was undefined for a standalone reader).
- §03 (l.370): "the gated slice in the main report" → "the optional upside in §03 … sits outside the plan."
- §05 (l.392): "same pipeline as the main report, with Hermes removed" → "carrier set fixed with Hermes off, routing re-run over the remaining five."
- §07 (l.405): dropped "(and on the Hermes module in the main report)".
Regenerated HTML (31 KB), grep confirms 0 "companion"/"main report" strings remain. Uncommitted.

## Action taken — strip unconfirmed Hermes / DBS-reroute content (management-facing)

Principal: report goes to management — keep it clean of the unconfirmed Hermes module + DB Schenker oversize-reroute upside; both are a later conversation. Decisions (AskUserQuestion): (1) keep Hermes only in the §02 "carriers assessed / not selected" list; (2) retitle to "Carrier Recommendation" (drop the "no-Hermes scenario" chrome). **No figures change — €976,024 is already the clean base, net of both.**

~20 coordinated edits in `report_no_hermes_v2.py`:
- **De-Hermes framing:** title/eyebrow/H1/sub/footer → "Carrier Recommendation" (no "without Hermes"); KPI "no Hermes" dropped; §00 lede + §01 + DBS card reworded; "base portfolio" → "five-carrier portfolio" throughout (the "base" wording implied a module on top).
- **Removed DBS oversize-reroute upside entirely:** the §03 "Optional upside" callout (the ~€/yr re-homing onto UPS/DHL + dimensions gate), §04 + §06 parentheticals, the §07 "commission the dimensions check" ask, and the §03 legend tags.
- **DB Schenker KEPT as the freight carrier** (carries ~€2.29M freight; only the speculative reroute went).
- Footer provenance genericized (dropped `stats_no_hermes.json` filename leak).
- Docstring updated to the standalone framing.

Verified: regenerated HTML (29 KB), grep sweep — "Hermes" appears exactly once (the §02 not-selected list), zero "base portfolio / dimensions check / DB Schenker reroute / oversize reroute / no-hermes / scenario". Uncommitted (commit-gated; never push).

## Action taken — slide deck + contrast fix

**Deck (new):** `final_report_no_hermes_v2/deck_no_hermes_v2.py` → `deck_no_hermes_v2.html` (35 KB, 14 slides). Principal wanted a deck "as clean as the report, not a cringe huge-title deck." Explicitly did NOT reuse the existing `final_report_no_hermes/deck_no_hermes.py` — principal flagged it as the inflated-type version (titles to 76px, numbers to 118px) *and* it still carried the stripped Hermes/DBS-reroute content. New deck inherits the report's exact palette + component classes (`.kpi/.card/table.t/.callout`) at report scale: section headings ~22–28px, hero figure capped 42px, tables 12px mono. Same cleaned standalone content (no Hermes module, no DBS reroute; Hermes only in the §02 not-selected list). 14 slides: title → recommendation → reviewed → who-carries-what → service mix → yardstick → by-confidence → by-mechanism → flow matrix → go-live → how-built → risks → decisions → close. Keyboard/click/dot nav. Reads stats_no_hermes.json + annual_stats.json (no hand-typed figures).

**Contrast fix (both v2 files):** principal flagged dark-gray-on-dark text hard to read. Lightened the shared palette `MUT` 0.42→0.62 and `DIM` 0.26→0.44 (white-alpha) in `report_no_hermes_v2.py` + `deck_no_hermes_v2.py`. Borders unchanged (.07/.14). Both regenerated, verified — no .26/.42 text remains.

## Open

- bi-analytics edit (`report_no_hermes_v2.py` + regenerated HTML) uncommitted — awaiting principal review + commit go.
- **Sibling consumers not yet changed:** the same generic "Carrier-level rates" fallback exists in `final_report.py` (main report) and `report_no_hermes.py` (v1) — DPD would still read "Carrier-level rates" there. Propagate the "Poland — not in contract" label or leave v2-only? Principal's call.
- DPD-PL domestic rate-card coverage gap — note in EU tender bank or leave? (raised, not actioned).

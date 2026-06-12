---
quest: S228_guell-no-hermes-with-gull
sid8: 50e52247
ts: 2026-06-12 13:35
open_dep: build the final_report_no_hermes_with_gull report variant (handed off; principal passing the prompt on now)
status: in-progress — investigation ANSWERED (S228); report-variant build is the next deliverable
---

# Resume — Güll → no-Hermes portfolio (investigation done, report build next)

**Where we are:** S228 answered "does adding Güll to the 5-carrier no-Hermes portfolio give meaningful savings?" → **+€163,897/yr PAPER** (full-year decision-set scorer). Niklavs then asked for a standalone report and is passing the build handoff on now. Investigation + finding fully captured (bank draft + quest-log).

**Next concrete step — build `final_report_no_hermes_with_gull`** (new standalone folder in `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/`, templated on `final_report_no_hermes_v2/`). The 5-carrier no-Hermes portfolio PLUS Güll (guell-2.0.0), standalone management "Carrier Recommendation" beside the existing 5-carrier one.

Build steps:
1. Stats — template `final_report_no_hermes/build_stats_no_hermes.py` → with-Güll builder: `FINAL = {dhl_paket, maersk, dpd_pl, ups, db_schenker, guell}`, add `guell` to `FAMILY_TO_ENGINE`; write `stats_no_hermes_with_gull.json` in the new folder.
2. Report — copy `final_report_no_hermes_v2/report_no_hermes_v2.py` → `final_report_no_hermes_with_gull/report_no_hermes_with_gull.py`, point at the new JSON; keep v2 standalone framing (no Hermes module, no DBS-reroute upside), now SIX carriers.
3. Deck (optional) — same for `deck_no_hermes_v2.py`.

**Watch-outs (will bite if copied blindly):**
- `base_ann` cross-check assert in `build_stats_no_hermes.py` (== `annual_stats.structure.base_ann`, the published 5-carrier figure) breaks once Güll is added → re-anchor; keep the internal `do_nothing − plan == saving` reconciliation.
- Tier split: `offer_mask` is maersk-only → add `guell` to the offer-based tier.
- Verify `q1_base.build_pp` routes Güll when it's in the FINAL set (candidate frame carries Güll prices per `routing_2026q1/build_routing.py`; "[HELD/provisional]" is only a print label).

**Flag on the page:** 150 parcels/pallet = working assumption (line-haul density). Revisable via `carriers/guell/constants.py` `PARCELS_PER_PALLET` (re-run engine prices + report, not just text). ~€40k-per-50-parcels sensitivity. Report re-derives Güll in its conservative q1 basis (UPS-on-engine, DBS-pinned) → expect < +€164k = the management number.

**Locked calls (already in guell-2.0.0, no engine change):** FX 1.08; ignore AT bulky shape; Güll's stated outbound per-pallet rates (24.50 AT / 40 CH).

**Files to read first:**
- `players/jebrim/bank/drafts/notes/projects/2026-06-12-guell-no-hermes-marginal-and-density-gate.md` (the full finding)
- `players/jebrim/quest-log/in-progress/S228_50e52247_guell-no-hermes-portfolio-marginal.md`
- bi-analytics `final_report_no_hermes_v2/` (template) + `final_report_no_hermes/build_stats_no_hermes.py` (stats source)

**Also open (non-blocking):** logistics-manager parcels-per-pallet/sprinter fill (the one data item that firms the marginal); Commerzbank strongest-of-month FX pull; bi-analytics S225 edits still UNCOMMITTED (separate repo, principal commit go).

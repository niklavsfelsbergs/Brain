# S118 D1 — EU Tender snapshot-docs refresh (dwarf trace)

**Role:** Jebrim dwarf. **Spawned by:** Jebrim principal (S118).
**Scope:** Bring two stale out-of-tree EU-Tender-2026 snapshot docs to current state. No git commit (principal commits). Out-of-tree paths under `bi-analytics-main/NFE/projects/2_EU_tender_2026/`.

## What I did
- Read both target files, then rewrote/refreshed in place preserving voice + section structure.
- `2_analysis/docs/NEXT.md` — full rewrite (always-overwritten handoff). Stamp → 2026-05-28 (S118).
- `carrier_responses_to_open_questions/CROSS_CARRIER_OVERVIEW.md` — refreshed header, readiness table, per-carrier notes, outstanding list, cross-carrier themes.

## NEXT.md changes
- Phase line → engines rebuilt → cost matrix re-run → decision report regenerated.
- Listed all 6 rebuilt+committed engines with commits (maersk-3.0.0 3b86d6a, hermes-2.0.0 990d61c, dhl_express-2.0.0 146e9ed, austrian_post-2.0.0 e8ddc62, dpd_pl-2.0.0 5998ef6, gls-2.0.0 96bc47f).
- Added S117 cost-matrix ranking (Hermes 4.575 < DPD PL 4.907 < GLS 5.029 << FedEx 6.93 [HELD] < DHL Paket 7.98 [HELD] < Maersk 8.11; DPD PL flipped →2nd).
- Added S118 decision_scorer + report regen (90 sets, do_nothing €0.00 PASS, ~€196k–€206k Q1 saving).
- Added the two material flagged assumptions (dpd_pl CH €484k, gls EFTA €278.9k; both collapse under CCD).
- New "Status checks (user-blocked, phrased as questions)" = the 4 INTERNAL Picanova-ops items (DHL Express DTP incoterm; AP pallet density; DHL Express pickup days/week; AP import-VAT-8%). Open-Q triage: nothing vital to ask a carrier.
- "Still carrier-blocked" = FedEx round-2 (June ZOOM) / DHL Paket round-2 (Bulky) / Güll (no reply, guell-1.0.0) / UPS (no offer).
- "Next concrete step" = agent-drivable: fold 4 internal answers → re-run; rebuild FedEx/DHL Paket/Güll on replies; full-year scoping later phase.

## CROSS_CARRIER_OVERVIEW.md changes
- Header → 2026-05-28; added a cost-matrix-ranking + report-regen callout block.
- Readiness table: 6 done engines now "rebuilt + committed (engine-x.y.z)" with commits + €/parcel; added DPD PL + GLS rows; FedEx/DHL Paket marked HELD.
- Per-carrier notes: rewrote Hermes/AP/Maersk/DHL Express to "rebuilt + committed" with engine internals; added new DPD PL + GLS sections (S115, deterministic-ready); DHL Paket/FedEx marked HELD + round-2 dispatched/sent.
- Re-ordered notes by competitiveness (Hermes, DPD PL, GLS, AP, Maersk, DHL Express, DHL Paket, FedEx).
- "Still outstanding" list → FedEx round-2 / DHL Paket round-2 / Güll (no reply) / UPS (no offer); dropped DPD PL + GLS (now reviewed/built).
- CH-customs theme line updated for DPD PL + GLS; noted both collapse under consolidated customs.
- Kept both standing caveats (Q1 basis, fuel spiking).

## State
- Both files edited + verified read cleanly. No git commit (left for principal).
- No other files touched.

---

## ADDENDUM — PLAN.md action-tracker refresh (separate dwarf run, 2026-05-28)

**Scope:** `2_analysis/docs/PLAN.md` (~977 lines, live §A/§B action tracker). Bring §B statuses + §A current-states current to the engine-rebuild cycle. Preserve history + structure; flip markers + append dated outcomes only. No git commit.

### §B items flipped to `[x]` (done)
- §B.19 Maersk `maersk-3.0.0` (commit 3b86d6a) — EU fuel 6.6%+band, ROW FedEx idx×50%, AT/DE/DK tolls, oversize cumulative, oversize_surcharge_eur populated, DE routing-code 0.
- §B.20 GLS `gls-2.0.0` (96bc47f) — ordered compounding stack; Pre-financing+Weighing→0; Delivery-private €0.15; EFTA €25 CH/NO; BigParcel>150L.
- §B.22 Hermes `hermes-2.0.0` (990d61c) — gross-only confirmed (0.588 genuine); bulky per-country; Destatis base-2021 fuel; MAX_LENGTH 170.
- §B.23 DHL Express `dhl_express-2.0.0` (146e9ed) — per-CW TDI~30%/DDI~18%+fuel-on-surcharges; remote-area 108k list; Demand Jan1-Feb16; line-haul ~€0.54; customs 0. Cost moved UP.
- §B.25 DPD PL `dpd_pl-2.0.0` (5998ef6) — zone fee conditional-by-postcode; gross formula+€0.20; monthly Orlen; customs CH/GB; line-haul incl. Sub-steps 4+5 discharged.
- §B.7 (+B.7.b/c/d/e) Austrian Post `austrian_post-2.0.0` (e8ddc62) — CH customs €1.00 regardless-of-ZAZ; CH FX prior-month÷1.06 (closes B.7.b); Sperrgut len>100; line-haul €0.83; AT fuel 4%. B.7.e v3.0.0 discharged into 2.0.0.
- §B.8 / §B.13 — added 2026-05-28 refresh notes (cost matrix re-ran 9 engines 4.76M/3.27M; 90 sets; report regenerated). Both already `[x]`.

### §B items kept open (annotated, NOT flipped)
- §B.21 Güll — STILL BLOCKED, no carrier reply (only carrier with zero response); engine stays guell-1.0.0.
- §B.24 DHL Paket — HELD, Round-2 pending (Bulky ~EUR 2.31M); round-2 dispatched.
- §B.28 FedEx — HELD `[~]`, Round-2 / June ZOOM (fuel + RE vol-weight + customs + FX open); favourably locked: residential 0, axis sorted, multi-AHS highest-only, IE div 5000.
- §B.3 fuel — kept `[~]`, annotated MOSTLY DONE (real fuel in 6 rebuilt engines; tail = Maersk EU history self-serve + FedEx/DHL Paket held).
- §B.15 / §B.16 / §B.17 / §B.9 (UPS) — untouched, remain open (full-year / terminal / carrier-blocked).

### §A carriers refreshed (Current-state cells → "wired in <engine>-x.y.z (2026-05-28)")
- Maersk (ROW fuel, oversize_surcharge_eur NaN, DE routing-code, ROW 4th oversize trigger).
- GLS (Energy/Dieselfloater, WeighingService→0, ClimateProtect, Pre-financing→0, EFTA, line-haul→none, Delivery-private, compounding order, BigParcel, Season).
- DHL Express (AIR/ROAD fuel, fuel scope, Remote Area, Non-Conveyable, Oversize, Customs→0, PLT, Demand, Emergency→0, PCS line-haul).
- Hermes (vol-weight gross-only, bulky table, bulky trigger, intl limits, diesel/Destatis, residential→0).
- DPD PL (engine build → 2.0.0, walkthrough done).
- Austrian Post (Wechselkurs, CH customs, line-haul; Sperrgut length-trigger noted, shape-gate still parked).

### Other
- Updated §B.5 per-carrier status blocks (Maersk/AP/GLS/Hermes/DHL Express → rebuilt+committed; DHL Paket/FedEx → HELD; DPD PL → built).
- Updated "Dependencies and parallelism" tail: added "Closed this cycle" block; flipped open-bullets for §B.7/19/20/22/23/25 to CLOSED, §B.21 to STILL BLOCKED, §B.24/28 to HELD.
- **Lifecycle check:** file's "delete when all §B done" rule — NOT all §B done. Open: Güll (no reply), FedEx (held), DHL Paket (held), UPS (§B.9 no offer), §B.15 volume-tier, §B.16 v2 report, §B.17 DPD-PL retirement, full-year scoping. **File stays.**
- No git commit. No other files touched in this addendum run.

---

## ADDENDUM 2 — OPEN_QUESTIONS / ASSUMPTIONS / REPORT_NOTES reconciliation (separate dwarf run, 2026-05-28)

**Scope:** three live tracker docs under `2_analysis/docs/`. Bring them to current state vs the 6-engine rebuild + 5-reply review cycle. No git commit. Preserve structure.

### OPEN_QUESTIONS.md
- Read fully (330 lines). Found it stale: reviewed carriers still listed all items open; no DPD PL section existed at all.
- Added "Reply reviewed / engine rebuilt / residuals" header note to **Maersk, DHL Express, Hermes, GLS, Austrian Post** sections; marked the questions the replies resolved as `answered`/`resolved` (dated 2026-05-27) inline, kept only genuine residuals open, tagged each residual INTERNAL / low-value-carrier / self-serve.
- **Created a new DPD PL section** (was missing) — header note (dpd_pl-2.0.0) + the CH-customs €484k material flagged assumption + minor residuals.
- Cross-carrier ZAZ entry: appended a 2026-05-28 status line (DPD PL=opt1 €44/opt2 CCD; GLS=EFTA per-parcel-or-CCD; Maersk/AP/DHL-Express resolved; Güll/DHL-Paket pending; FedEx held).
- **FedEx / DHL Paket / Güll / UPS left OPEN** (carrier-blocked) — added one-line current-status notes only.

### ASSUMPTIONS.md
- Read fully (755 lines). Found Maersk/DHL Paket/DHL Express/Hermes/AP/FedEx already carried "REPLY UPDATE 2026-05-27" blocks (folded by prior S099/S102 sessions). **GLS and DPD PL were still pure v1/Phase-1 placeholders** — those were the gap.
- **GLS:** added a REPLY UPDATE block (gls-2.0.0) flipping placeholder rows to confirmed wired values (compounding stack, Pre-financing/Weighing→0, Delivery-private €0.15, EFTA €25) + marked the **EFTA €278.9k MATERIAL FLAGGED ASSUMPTION** (collapses under CCD).
- **DPD PL:** added a REPLY UPDATE block (dpd_pl-2.0.0) + marked the **CH-customs €484k MATERIAL FLAGGED ASSUMPTION** (€44/parcel opt-1; collapses under CCD).
- Kept AP line-haul €0.83/parcel (density 150, sensitivity €20–82k) + DHL Express demand Jan1–Feb16 as flagged (already present, reaffirmed).
- FedEx/DHL Paket/Güll left as placeholder (engines not rebuilt) — already annotated.

### REPORT_NOTES.md
- Added cross-carrier **cost_matrix Q1 ranking** (Hermes < DPD PL < GLS << FedEx[HELD] < DHL Paket[HELD] < Maersk) as the unit-cost reference.
- Added the **two material flagged assumptions** as decision-maker caveats (dpd_pl CH €484k, gls EFTA €278.9k — both collapse under CCD) — were NOT surfaced in the report before.
- Added **DHL Express cost-moves-UP-on-rebuild** sentence so the ranking isn't misread.

### State
- All three files edited + verified. No git commit. No other files touched.

---

## ADDENDUM 3 — SESSION_LOG.md + DECISIONS.md append-only catch-up (separate dwarf run, 2026-05-28)

**Scope:** the two APPEND-ONLY history docs under `2_analysis/docs/` that stopped at 2026-05-21 (session 25). Append concise entries to bring both current; read each first to match format; never edit existing entries; no git commit.

### SESSION_LOG.md — 6 new entries appended (newest-at-top, before session 25)
- session 31 (2026-05-28) — decision_scorer + report regen + open-Q triage (brain S118): 90 sets, do_nothing €0.00 PASS, no code change; ~€196-206k Q1 saving; 4 residuals INTERNAL; 2 material flagged assumptions.
- session 30 (2026-05-28) — cost_matrix re-run all 9 engines (4.76M/3.27M); Q1 like-for-like ranking on 429,721 common-coverage parcels; DPD PL flipped →2nd.
- session 29 (2026-05-28) — DPD PL + GLS reviews + dpd_pl-2.0.0 (5998ef6) / gls-2.0.0 (96bc47f) rebuilds (S115/S117); GLS 0-byte-reply lesson.
- session 28 (2026-05-27/28) — dhl_express-2.0.0 (146e9ed, S104) + austrian_post-2.0.0 (e8ddc62, S114).
- session 27 (2026-05-27) — maersk-3.0.0 (3b86d6a) + hermes-2.0.0 (990d61c).
- session 26 (2026-05-27) — reply-review wave + FedEx Round-1 reviewed + Round-2 sent (S099/S102).
- Continued the local session counter from 25; matched existing header style + NEXT.md pointer per entry.

### DECISIONS.md — 3 new dated 2026-05-28 entries appended (newest-at-top, before the 2026-05-27 FedEx entry)
- (a) Q1 like-for-like ranking = current decision basis; DPD PL flipped uncompetitive→2nd (S118) — 6-row ranking table + S034 -€417k contrast.
- (b) Open-questions triage: no further carrier round for Maersk/DHL Express/AP/DPD PL/GLS; 4 residuals internal.
- (c) Two material flagged assumptions held (dpd_pl CH €484k @ opt-1; gls EFTA €278.9k) pending consolidated-customs call — ~€763k Q1 contingent.
- Matched existing entry format (date header, one-line decision, rationale, Related wiki-links).

### State
- Both files edited append-only + verified; no existing entries altered. No git commit (principal commits). No other files touched.

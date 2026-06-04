---
quest: carrier-overview-report (EU tender — manager-facing carrier report)
sid8: d691c033
parent_sid8: e59202cf
ts: 2026-06-04 23:42
open_dep: v2 rebuild PLAN written + audited + committed; awaiting principal sign-off on 8 Phase-0 decisions, then a FRESH session executes
---

# Resume — Carrier Overview (EU tender) — v2 REBUILD planned, not started

## Where this is
- **v1 BUILT** (`bi-analytics .../2_analysis/carrier_overview/`): lib + 9 carrier sections + synthesis → `carrier_overview.html` + `exec_brief.html`. Committed `dd7785d`. **Superseded** — has two foundational flaws (below).
- **v2 PLAN written, audited, corrected, committed** (`carrier_overview_v2/PLAN.md`). NOT executed.

## Why v2 (the two v1 flaws)
1. **Whole-lane blended framing** — v1 compares carriers on each lane's average *if one carrier took ALL the lane's volume* (incl. parcels it's bad at). Nobody routes that way. Must compare **per cut of volume where each carrier competes**.
2. **Wrong Sperrgut predicate** — v1's "side>60cm = 38.3%" measured the wrong thing. Real DHL Paket Sperrgut (verified `dhl_paket/constants.py` STD 120/60/60) = **longest>120 OR second>60 = 21.8%** of book. v1 framing/segmentation built on memory, not contracts.

## The plan (carrier_overview_v2/PLAN.md — read it in full)
Segment-based: a *segment* = a region of raw parcel-attribute space where the cheapest-or-within-X% carrier **set** is constant. Boundaries = surcharge **cliffs** + base-rate **crossovers**, **discovered empirically per lane + explained from verified contracts**, reconciled both ways. Chargeable weight is carrier/lane/service-specific (gross-only / ÷5000 / ÷6000) so axes are **raw** (`weight_kg`, `volume_cm3`, dims). 7 phases, each with a verification gate; I cross-check every sub-agent number against the constants/matrix. Goal section at top.

## Next concrete step — a FRESH session executes (this context is loaded/spent)
1. **Principal answers the 8 Phase-0 decisions** (PLAN §11): X% threshold + show-gap; materiality fold %; segment-count ceiling; keep/drop single-source blended; keep 9 lanes or split on zones; segment naming (friendly-precise vs predicates); time basis (full-year vol + Q1 unit cost); girth handling.
2. **Phase 1** — 1 dwarf per carrier extracts verified boundaries/rate-structure into `carrier_overview_v2/verification/phase1/<carrier>.md`; I reconcile each against the constants. (Briefs were drafted this session; the killed run wrote nothing — start fresh.)
3. **Phases 2-7** per the plan (segment grid → empirical reconciliation → competitive map → per-carrier hands → synthesis → render, reusing v1's UX). Cross-document consistency pass at the end (PLAN §10).

## Carrier facts already verified this session (re-confirm in Phase 1, don't trust this list blind)
- Chargeable basis: gross-only = DHL Paket, Hermes, Güll, Austrian Post, Maersk-EU; ÷5000 = DHL Express, DPD PL, FedEx, Maersk-ROW; ÷6000 = GLS-EBP (GLS-BP gross).
- DHL Paket Sperrgut: longest>120 ∨ second>60 ∨ short>60; bulky reject cap L+girth 360 DE / 300 intl; €20 DE / €21 intl.
- Girth formula (shared, `_base/supplement.py`): `d_max + 2*(d_mid + d_min)`.
- 9 engine carriers; 8 firm + Güll held; new-carrier (no current invoice) = Hermes, FedEx, DHL Express.

## Checkpoints (recover to either)
- bi-analytics `dd7785d` (v1 build + v2 plan); brain `1039e71` (+ this close). NOT pushed.

## HANDOVER PROMPT (paste as the first message of the fresh session)
> Hey Jebrim, execute the EU-tender Carrier Overview **v2 rebuild**. The plan is locked at `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carrier_overview_v2/PLAN.md` — read it in full first (Goal + §1-§14); it supersedes v1 (`../carrier_overview/`). Resume context: `inventory/carrier-overview-report-resume__d691c033.md`. Start with Phase 0: walk me through the 8 open decisions in §11 and get my answers before any fan-out. Then Phase 1 (one dwarf per carrier → verified `verification/phase1/<carrier>.md`, you reconcile each against the constants), then Phases 2-7 per the plan. Hold the discipline: every number traced to a verified constant or the cost matrix; sub-agent output is verified, not copied; gates between phases. Don't skip Phase 0.

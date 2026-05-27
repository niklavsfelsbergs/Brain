# S102 — EU Tender 2026: FedEx Round-1 reply review

**Session:** 6217a8d5 · 2026-05-27 · Jebrim (principal)
**Continues:** [[S099_55ea7bc0_eu-tender-carrier-reply-review|S099]] (carrier-reply review; closed clean 14:02). This session reviews the FedEx reply that landed after S099 closed.

## Ask
Principal: back on the EU tender; a new reply (FedEx) dropped at `carrier_responses_to_open_questions/fedex/fedex`. Review it vs our dispatched open questions; assess whether FedEx can now do a DETERMINISTIC cost calc (no proxies), same bar as the S099 carriers.

## Turn log
- Respawn + sibling detection: S099 owner (55ea7bc0) ended clean, same terminal; braindead-a268b008 dev-brain (no overlap). Adopted S099 EU-tender resume state. Posted OPEN.
- Located + read the FedEx reply (6.5KB plain text, dropped 14:11) and the FedEx open-questions doc (`2_analysis/docs/open_questions/fedex.md` — 20 carrier-facing Qs, Blocks B1-B5, Changes C1-C5).
- **Assessment (delivered to principal):** reply is explicitly *preliminary*. NOT deterministic-ready.
  - **Closed/confirmed:** B4 residential → 0 uplift ("rate card does not differentiate" → flat all-in; kills €2.1-3.15M worst case — biggest de-risk); B5 axis (longest=physical-longest, girth=2w+2h, 2nd-longest=sorted-mid → confirms engine sorted-dims); C1 multi-AHS highest-only effective 2026-01-12 → confirms engine ordering + Q1 replay window; IE vol-weight div=5000 confirmed; min billable 0.5 kg; customs basis = DAP (no duty advancement default).
  - **Still open (blockers):** B1 fuel (#1 big-bet — only a public URL, scope vague, index TBC, cadence answer garbled); B2 **RE** vol-weight divisor BLANK (dominant service, 96.7% dim-heavy — load-bearing); B3 customs fee amount = "Clearance Fees" no number (CH 11,414 parcels, €138-207k Q1); FX (4.30 placeholder, ECB self-serve fallback); C5 remote/address (URLs not values + attribution data-blocked, no postcode col); C4 unauthorized (discretionary — engine reject defensible).
  - **Correctness flag:** C2 REF "available for all EU zones" CONTRADICTS engine's Zone-R-only migrate patch — fix needed, but near-zero Q1 impact (2 parcels >68kg, BE/FI); per-zone REF rates not supplied.
- **Principal action surfaced:** FedEx offered a ZOOM to close surcharges — pick **June 2 @ 12:00** or **June 9 @ 10:00**.

## Writeup + cascade — DONE (principal "yeah write it up")
- Wrote `carrier_responses_to_open_questions/fedex/REVIEW_CONCLUSIONS.md` (open-Qs block + 20-row resolution table + verdict, DHL-Paket-shape).
- Cascade (8 files): CROSS_CARRIER_OVERVIEW (6th carrier row + per-carrier para + CH-customs theme), FUEL_SUMMARY (FedEx row + moved out of "no info"), OPEN_QUESTIONS (reply-landed delta block under ## FedEx), ASSUMPTIONS (2026-05-27 reply-update subsection), NEXT (6 reviewed + ZOOM follow-up + outstanding), PLAN §B.28 ([~] HELD + revised envelope ~€5.5-6.0M), DECISIONS (new top entry). REPORT_NOTES left as-is (FedEx still not score-ready — existing framing holds).
- All out-of-tree bi-analytics-main edits; UNCOMMITTED (awaiting principal go), git commit -- <pathspec>.

## Web-answerability assessment (principal asked) — IN PROGRESS
Web/self-serve closes the *numbers* on ~4 items but NOT the two biggest levers (fuel scope+index, RE vol-weight) — those are carrier-only. Detail delivered in chat; offered a penguin to pull them ahead of the meeting.

## Tighten pass — DONE
Principal: 1 fuel (look + resend scope), 2 pull FX, 3 **shipping_zipcode IS in fact_shipments** (correct knowledge; consult shipping-agent if unsure), 4 min-charge good. "Tighten all we can + leave off remaining Qs to send."
- **Mart check (redshift MCP):** `shipping_mart.fact_shipments.shipping_zipcode` exists, ~98-100% digit-leading after CHR(8194)-strip+trim → remote-area attribution feasible. **My Internal #6 "no postcode column" was WRONG** — and echoed across sibling carrier reviews (flagged for a cross-carrier sweep). Verified directly; didn't need the shipping-agent.
- **Penguin** (S099_p2 research file): FX SOLVED (ECB Q1 2026 Jan 4.2114/Feb 4.2186/Mar 4.2725, avg 4.234; 4.30 was ~1.5% high). Remote-area SOLVED from in-repo VASS PDF (EAS Tier A PLN15/shp, B 2.60/kg min105, C 3.35/kg min135; addr-corr INTL PLN43.70). Fuel = GAP (all FedEx pages access-gated) BUT structure firmed: two indices (Regional→RE weekly, International→IE step-change) → engine needs FUEL_PCT_RE + FUEL_PCT_IE.
- **openpyxl:** min-charge cells RESOLVED — only 4 yellow cells = service headers, 0 yellow rate cells → engine correct. Closes Q14.
- **Wired interims** into REVIEW_CONCLUSIONS (self-serve section + rows + blocks + engine-todo) + ASSUMPTIONS + FUEL_SUMMARY (2 FedEx index rows) + OPEN_QUESTIONS (Internal #6 corrected).
- **Round-2 dispatch written:** `1_offers/picanova/FedEx/questions_for_carrier_round2.md` — 7 carrier-only Qs (fuel scope+index+history, RE vol-weight, customs fee+ZAZ, FX policy, volume tiers, peak, EAS postcode list), plain send-ready block at top.

## Remaining open / principal actions
- Pick FedEx ZOOM slot (2/9 Jun) + send round-2 (or walk it on the call).
- Fuel %s: retry FedEx pages off-network (penguin hit access-gates).
- FX interim 4.234: confirm vs ECB EXR.M before locking in engine.
- Cross-carrier sweep: the "no postcode column" claim is wrong in Maersk/GLS/Hermes/DHL Express/DPD PL reviews too.
- `fedex-2.0.0` rebuild stays HELD pending fuel + RE vol-weight.

## Engine rebuilds (principal: "rebuild the engines which we can"; cadence = one-at-a-time/verified)
- **maersk-3.0.0 — DONE + VERIFIED.** constants (FUEL_PCT_EU 0.10→0.066, FUEL_PCT_ROW 0.10→0.2475, AT_TOLL 0.29, new DE_TOLL 0.19 + DK_TOLL_GLS 0.05, ROW_MAX_LWH_PRODUCT_CM3 169901), at_toll trigger flipped on, new de_toll.py + dk_toll.py (always-on DE/DK), registered in __init__, row_oversize 4th trigger (lwh_product>169901 = the "2xLxH cm3" AHS volume cap). Fixtures 15/15 pass (+ new DK fixture, toll/fuel checks added to test_engine). Full-pop smoke clean: 468,552 eligible, total €4.35M, AT toll €6,763/DE €65,385/DK €121, fuel €170k. Oversize parquet was already populated (BE/LU 6.10/IT 2.0/ES 1.0/CH reject) — IT "2+2 stack" + ES exact-tier-trigger left as the review's flagged minor residuals.
- **HELD/next:** hermes-2.0.0, dhl_express-2.0.0, austrian_post-2.0.0, then cost_matrix re-run + ranking shift. FedEx + DHL Paket rebuilds stay HELD (round-2 pending).
- Engine edits UNCOMMITTED (bi-analytics-main, on top of 8cdf616).

## Brain side
UNCOMMITTED (awaiting principal go): S102 quest-log, this session's intent, penguin research file + S099_p2 quest-log, comms OPEN. Out-of-tree bi-analytics-main edits (REVIEW_CONCLUSIONS + cascade + round-2 dispatch) also uncommitted. git commit -- <pathspec> (shared-index hazard; sibling braindead-a268b008 dev-brain, no overlap).

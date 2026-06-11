# S205 (f08474c9) — UPS Round-1 reply review + engine-spec decisions

**Player:** Jebrim. **Date:** 2026-06-11. **Status:** completed — review shipped, all engine assumptions decided, `ups-2.0.0` build handed off to a new session via handover prompt.

## What happened

1. **Reply readability check.** UPS Round-1 answers landed as a raw Outlook paste in `carrier_responses_to_open_questions/UPS/UPS`. The surcharge table arrived flattened (one cell per line) but fully reconstructable. Confirmed complete.
2. **Q-by-Q review** against `questions_for_carrier.md` (11 Qs): **6 resolved, 4 partial, 1 dodged.** Wrote `carrier_responses_to_open_questions/UPS/REVIEW_CONCLUSIONS.md`; flipped the status table; corrected `UPS/CLAUDE.md`; un-staled the `CROSS_CARRIER_OVERVIEW.md` UPS row ("no offer yet" was 8 days stale).
3. **Three v1 assumptions overturned by the reply:** fuel "35" = 35% discount off the published weekly index (~20.31% effective — confirms the [[S171_c4e56024_ups-fuel-basis-and-gri-sensitivity|S171]]/rate-card-diff reading); **no dimensional weight on Standard** (actual kg only — in our favour); **OML not unconditionally waived** (90 parcels/yr allowance, then €499.10 — against us).
4. **Discussion rounds with Niklavs settled the full v2 spec** (see Decisions). Key analytical beat: a contract-deterministic engine on mart dims prices LPS/OML ≈ €0 while the real net is ~€1.44M standing — because the trigger is UPS's dimensioner, not our data (S199). Hence the by-bill ruling.
5. **New contradiction surfaced:** reply quotes OML at >400 cm L+G (book) vs the negotiated 419 (S199 principal-stated). Round-2 / contract-text check.

## Decisions (principal, 2026-06-11)

- Fuel **flat 20%** (revisit trigger: weekly-index replay only if scoring-sensitive).
- LPS **€101.80 assumed** (book; round-2 ask), trigger L+G >325 cm, 40 kg min billable, suppresses AHC.
- **All-Single** rates; **zone follows shipper PLZ** per workbook `DE_ZONES` (assumed, round-2 confirm).
- **Oversize adjustment BY BILL** — empirical incidence from invoices (S199 cohorts); exact approach (cohort incidence vs flat uplift) decided at calculation-build time; dispute-grade ~€641k/yr stays a visible line.
- **Fee tail flat €0.05/parcel**; no line-item Saturday/signature/paper-invoice modeling (process-driven, not carrier-differentiating).
- **`zugeschnittene Verpackung` on UPS = routing mistake** (noted in bank draft).

## Artifacts

- bi-analytics (UNCOMMITTED, commit ask pending): `carrier_responses_to_open_questions/UPS/REVIEW_CONCLUSIONS.md` (new) + `CROSS_CARRIER_OVERVIEW.md` (UPS row) + `1_offers/picanova/UPS/{CLAUDE.md, questions_for_carrier.md}` (A1–A14 assumption table, status flips).
- Brain: append to `bank/drafts/notes/projects/2026-06-11-ups-oml-lps-negotiated-thresholds.md` (principal rulings + 400-vs-419 discrepancy).

## Hand-off

The `ups-2.0.0` engine-build prompt was delivered in-chat at close (paste-ready for a fresh Jebrim session). Spec sources for the build session: `UPS/CLAUDE.md` working assumptions A1–A14 + `REVIEW_CONCLUSIONS.md` (decisions + engine to-do) + the S199 dimensioner bank note. First build task = the deferred incidence-layer design decision (with principal).

No pending external actions.

## Process note

Entered without posting the comms OPEN — caught by the `require-open` write gate on the first brain write (turn ~5). The gate did its backstop job; first-try discipline miss logged against the known ~72% stat.

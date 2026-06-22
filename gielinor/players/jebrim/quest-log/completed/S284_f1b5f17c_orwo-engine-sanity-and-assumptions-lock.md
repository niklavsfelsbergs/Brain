# S284 — ORWO tender: engine sanity-check + B3 confirm + assumptions-locked re-run

**Player:** Jebrim · **sid8:** f1b5f17c · **2026-06-22**
**Continues:** [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]]/abfcf511 (ORWO tender umbrella) · [[S283_60de5609_orwo-tender-assumptions-and-carrier-questions|S283]]/60de5609 (assumptions + dispatch) · [[S281_926f247a_orwo-carrier-engines-refactor-gls-maersk|S281]] (carrier engines).
Picks up after S283-cont (ca27d9be) — the full-cost surcharge re-run that reversed the GLS verdict.

## Ask

Sanity-check the ORWO GLS + Maersk repricing engines against the EU-tender (Picanova) engines (ground
truth — ORWO stacks were lifted from them). Hunt mechanical contradictions, not value drift. Fix ORWO if
it contradicts; re-run + report delta. Then (mid-session) the principal closed the three remaining open
assumptions and asked to re-run.

## Turn 1 — engine cross-check: ENGINES AGREE

Line-by-line diff of both engine pairs (`projects/2_EU_tender_2026/.../carrier_engines/{gls,maersk}/`
ref vs `7_ORWO_tender_2026/repricing_base/carrier_engines/{gls,maersk}/` under test). **No mechanical
contradictions.** Every copied value + every compounding rule matches:
- GLS: Energy 0.205 / Klima 0.025 / Diesel 0.041 / Toll-Intl 0.057 / Toll-Nat 0.38 / DE-private 0.15.
  Order matches (Energy+Klima+Season on base → Toll on full net x-border / €0.38 flat domestic → Diesel
  after toll → €0.15 flat uncompounded). ORWO copied the ACTIVE Toll-Intl-on-net mechanic, NOT the
  retired base-only `gls/surcharges/toll_international.py`.
- Maersk: EU fuel 6.6% base-only / AT 0.29 / DE 0.19 / DK 0.05 additive / Overpack 0.40 every parcel.
- Deltas all legit ORWO-specific divergences (Season blended annual-proxy; ROW deferred; GB on ORWO card;
  dim-dependent surcharges dormant — ORWO is dim-poor), not transcription errors. No fix / re-run needed.
- Outcome: the −€265k/yr verdict is reference-consistent → stronger to quote.

## Turn 2 — B3 GB clearance CONFIRMED (Andrea)

Andrea confirmed Maersk GB customs clearance = **€0** (folded into Evri/Yodel door rate). This was the
biggest single lever (assumption B3, Low-Med). Number doesn't move (engine already assumed €0); its
biggest risk is gone. GB-Maersk −€177k/yr now carrier-confirmed.

## Turn 3 — three open assumptions LOCKED + re-run → −€282k/yr

Principal decisions closing the tender's open items:
1. Adopt Picanova surcharge rates as correct for ORWO — dispatch now confirms, no longer blocks. No Δ.
2. Hold incumbent GRI at 5% for the do-nothing comparison. No Δ.
3. Exclude GB/EFTA clearance for GLS too (€0), mirroring Maersk. CHANGED a number → set
   `per_lane_optimum.py` GLS_IC18 3.0→0.0, RE-RAN.

**New headline −€282k/yr** (was −€265k). GB unchanged (Maersk wins). Real effect = CH-GLS −€18k→−€35k/yr.
Run: current €2,451,899 H1 / optimum €2,311,013 H1 / saving −€140,886 H1. Whole-lane split: Maersk
−€187k/yr (GB + FR/ES/IT/IE tails) + GLS −€94k/yr (AT −€56k + CH −€35k + NL/BE/NO).

**Final recommendation:** keep DHL on DE domestic; move GB→Maersk, AT+CH(+NL)→GLS; ≈ −€282k/yr.

## Decisions

- Engines validated against Picanova reference — faithful; no contradictions.
- B3 (Maersk GB clearance) = €0 confirmed by Andrea.
- Assumptions locked: Picanova rates adopted; GRI 5%; GLS GB/EFTA clearance excluded (€0).
- Headline final at −€282k/yr on locked assumptions.

## Cascade

Downstream files updated this session: `carrier_engines/COMPARISON.md` (VALIDATED block + ASSUMPTIONS
LOCKED block + headline/lane tables + GB lever + caveats → −€282k), `per_lane_optimum.py` (GLS_IC18→0),
`carrier_questions/{Maersk.md, _provisional_assumptions.md}` (B3 RESOLVED, GLS-B2 clearance excluded),
resume__60de5609 (sanity-check + B3 + assumptions-locked blocks; next-step set to the logic walkthrough).

## Main-brain changes

None to globals/meta/rituals. Player-scope only (Jebrim quest-log + inventory + comms).

## Pending external actions

None pending this session. Carried-open (principal's, on the umbrella): SEND the carrier dispatch
(now confirmation-not-blocker); get real ORWO GRI% per incumbent.

## Open (carried on umbrella [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]])

NEXT SESSION = walk the principal through the whole ORWO tender logic end-to-end (assumed / decided /
built, every step, information-dense). See resume__60de5609 "NEXT SESSION — START HERE".

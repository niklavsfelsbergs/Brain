# UPS OML/LPS predictor investigation — what predicts the surcharges?

**Player:** Jebrim · **sid8:** ee882f39 · **Date:** 2026-06-11 · **Status:** complete

## Ask

Niklavs: build a good prompt for investigating what causes UPS OML and LPS surcharges — is there anything in the data that predicts them? Fork: no predictor → either our data doesn't represent reality or UPS mischarges; predictor found → data partly right, course-correct. Then: run it.

## Turn log

1. **Prompt build (3 iterations).** Grounded in the 2026-06-02 verify run ([[S-shipping-agent_pcs-pl-ups-oml-lps-verify]]), the UPS charge-profile + published-surcharges bank notes, and the S167 dimension-coverage map. Corrections from Niklavs: (a) **325/419 are OUR negotiated LPS/OML triggers** — the verify run's bands were right, the DE-book 300/400 comparison was wrong; (b) the prompt must mandate **deep cohorts** (packagetype × dim band × weight band), CUSTOM_OVERSIZED named as cohort of interest.
2. **Bank draft** written: [[2026-06-11-ups-oml-lps-negotiated-thresholds]] (negotiated thresholds + cohort hypothesis; findings folded in at close).
3. **Shipping-agent run** (agent trace: [[S199_ee882f39_sa_ups-oml-lps-predictor]]). Headline: **the predictor is UPS's own dimensioner measurement** — printed on the invoice (`packagedimensions` vs `detailkeyeddim`; passthrough test confirms independence). Verdict on €1.44M standing net: ~€425k legitimate by our dims (>325), ~€390k tolerance-zone 300–325 (thin-axis cm-level disagreement), ~€641k dispute (incl. entire over-max family — UPS measured lengths 1.5–2.7× keyed, physically implausible). CUSTOM_OVERSIZED cleared (avg L+G 296; 70/31,580 >325). Reversal coverage collapsed since Q4-2025 → receivable accruing ~€160k+/qtr. Spot-verified family totals against silver inline (match within 1–6%, deltas explained by reversal-only credits).
4. **"€425k legitimate" challenged** by Niklavs ("I don't believe we ship so many >325") — drill showed he was right to push: 94% of the bucket is ONE box, `zugeschnittene Verpackung` 130.3×91.6×(7–10), L+G 327.5–333.5 — over the negotiated 325 by 2.5–8.5 cm, on **catalog dims** (identical triplet thousands of times = spec values, not measurements). Only 24,407 of 2.1M PCS PL UPS shipments exceed 325 at all.
5. **Incidence drill:** the box gets charged ~48% (2023–24 ~50–52%), nearly vanished in 2025 (12 shipments — packaging change?), back in 2026 at 26.7% (1,497 shipped Jan–May, ≈ €70k/yr run-rate). Coin-flip incidence on identical declared dims = the physical box straddles the threshold.

## Decisions

- Negotiated thresholds recorded as bank draft (closes the gap where the verify run used them without recording they're contractual).
- "Legitimate" label softened in-session: the €425k bucket is threshold-straddling catalog-dims, subject to the same physical audit as the 300–325 zone.

## Pending external actions

No pending external actions. (Agent run completed; spot-verify completed; nothing sent externally.)

## Open / needs principal (carried in the agent trace too)

- Physical re-measure audit (STANZVERPACKUNG 120×90 + the zugeschnittene 130.3×91.6 box, as-packed vs UPS dimensioner) — adjudicates €390k + €425k buckets.
- UPS claims cadence: reversal machinery broke Q4-2025; ~€160k+/qtr accruing un-reversed.
- known-dq UPS LPS/OML entry should gain the independent-measurement finding (maintainer edit, principal-gated).
- Ask PCS PL what changed in 2025 (the >325 box's disappearance) and why it returned in 2026 — likely IS the course-correction.

## Cascade

Cascade: none — no canonical docs/status tables affected (investigation, not tender-doc work).

## Main-brain changes

- `bank/drafts/notes/projects/2026-06-11-ups-oml-lps-negotiated-thresholds.md` (new draft, findings folded in)
- `examine/drafts/2026-06-11-legitimate-bucket-needs-same-skepticism.md` (harvest)
- Agent trace `quest-log/completed/S199_ee882f39_sa_ups-oml-lps-predictor.md`
- Probe SQL outside the brain: `shipping-agent/scratchpad/ups_oml_lps_predictor_probes.sql`

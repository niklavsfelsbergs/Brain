# S171 — UPS offer comparison: GRI sensitivity + fuel-basis reconciliation + engine refit

**Player:** Jebrim. **Session:** c4e56024. **Opened:** 2026-06-09 ~14:00. **Status:** in-progress.
Continuation of the S168 UPS rate-card-diff thread ([[S168_1a9eb9d9_ups-old-vs-new-rate-card-diff]]);
picks up the +5% GRI sensitivity that [[be1b4946]] ([[S170_be1b4946_eu-tender-carrier-substitution-deltas|S170]]) teed up but parked.

## Ask
"How does our UPS cost comparison change if we increase the old offer costs by 5% to accommodate for
general rate increase?" → grew into reading the card's fuel listing → an invoice reconciliation →
an engine refit → a consolidated old-vs-new summary → save the knowledge.

## What happened (turn log)
1. **GRI sensitivity.** Applied a flat +5% GRI to the incumbent card against the S168 diff. The offer's
   ~+5% on Standard-light is a GRI-sized move → core EU lanes go to **parity** vs a GRI'd baseline
   (`(1+d)/1.05−1`: DE −0.2%, FR/AT/IT/BE/NL/CH ≈ 0%); **PL ~−19%, DK/GB ~−4.8%** become genuine wins.
2. **Fuel listing.** Read the Zuschläge sheet on both cards: Fuel = **"35, Percent Off — per Shipment,
   Net Rate NA"**, identical old vs offer. Recognised "Percent Off" = a **discount off the floating
   index** (same rate-type as Free Domicile 80%-off → pay 20%), NOT a flat 35% surcharge. So effective
   fuel = `index × (1 − 0.35)`.
3. **Invoice reconciliation** (spawned shipping-agent; trace `S168_1a9eb9d9_ups-fuel-effective-rate-reconciliation.md`).
   Effective fuel/base = **19.3% overall, 19.8% road** (UPS04STD, 91% of vol) → implied index ~30.4%.
   Express 23–26%, WW Eco 5–6%. Drifts to ~24–28% Apr–May 2026 (spring spike — a fixed discount on a
   floating index does that; a flat 35% couldn't move). UPS discount/credit buckets empty (discounts
   baked into net base). **Verdict: discount reading confirmed, decisively.**
4. **Engine refit.** `calculation/engine.py` `FUEL_PCT 0.35 → 0.20` (2025 road baseline) + rewrote the
   inline comment, summary print line, and the README param row. Re-ran (cached shipments, no Redshift
   pull). Q1 pure-quoted calc **€1.685M → €1.505M (−€179,598, −10.7%)**; gap to actual (`real_total_eur`
   €1.257M) halved (+34% → +20%). Forward pricing should use `published_forward_index × 0.65`.
5. **Knowledge saved.** Updated the S168 bank draft with Fuel + GRI-sensitivity sections; gave a
   consolidated old-vs-new summary.

## Decisions
- Fuel refit chosen (principal, multiple-choice): **re-run at ~20% effective now**, flag the spring
  spike as a separate sensitivity — over parametrize-and-hold or capture-only.
- The contract is evergreen / no-GRI-clause / floats on the published tariff ([[S170_be1b4946_eu-tender-carrier-substitution-deltas|S170]] recon) → a GRI
  genuinely flows through; the sensitivity isn't hypothetical.

## Pending external actions
None pending. (bi-analytics engine edits are UNCOMMITTED — separate-repo, principal-gated; see resume.)

## Cascade
- bi-analytics (separate repo, on main, UNCOMMITTED): `UPS/calculation/engine.py` + `README.md`;
  `output/replay.parquet` regenerated (gitignored).
- Brain: bank draft updated; this quest-log; inventory resume; comms OPEN+CLOSING; 1 examine draft.

# S278 — Non-ORWO SCM expected-vs-invoiced understatement: what is the estimate understating?

**Player:** Jebrim · **sid8:** c1ecf686 · **Date:** 2026-06-19 · **Status:** completed (investigation shipped; decision = park)

## Ask
Niklavs (Hey Jebrim): in SCM with **ORWO excluded** (the TCG entity), invoiced cost runs much higher than the expected/estimate basis — investigate why, what are we understating? Then: even without UPS, there's still a decent mismatch — investigate, **May only**.

## What happened (2 shipping-agent passes, gold `shipping_mart`, order-month lens, READ-ONLY)

**Pass 1 — whole non-ORWO.** Like-for-like residual (real vs the `expected` assigned to the same invoiced rows) = **+5–7% on mature months**, NOT "much higher" (the inflated read was immature-June / full-population). Real understatement, survives the maturity gate (grows on mature months — opposite of a selection artifact). **Tail, not level:** ~3% oversize/large-package slice carries **88%** of the residual (1.74–1.98×); the ordinary 97% is priced near-perfectly (0.997–1.01×). The flat per-country `expected` model is dimension/surcharge-blind by construction. **UPS = 42%** of residual (fuel + oversize). US best-calibrated (1.005×); miss is EU + missing-rate lanes (Australia ~21×).

**Pass 2 — May, ex-UPS.** Residual = **€73,059 = 58.2%** of the full non-ORWO May residual (€125,422). Two drivers: (1) **DPD UK €23,709 (1.46×)**, ~32% of it — broad UK-lane under-pricing, **1.40× even on plain parcels** (rate-card miss, not a tail); (2) a **diffuse ~4% surcharge drift** across ordinary parcels (fuel/residential/remote-area/truck charges the flat scalar can't see). Oversize is the *minority* here (39% of the residual) — the headline flip from the UPS story. **DB Schenker is NOT a driver** (1.019×; corrects the April-cut suspicion). All dispersion, no structural holes in this slice.

## Decisions
- **Park `expected` as-is.** Fix lands when tenders close and the **re-rating engine fills `expected`** (surcharge/dim-aware) — kills dispersion at the root. A flat ×1.04/×1.07 is the wrong shape (fixes the mean, not the dispersion; mis-baselines the per-corridor alert engine; multiplier isn't stable Feb→Apr). Captured to bank draft.
- Trigger to revisit: tender close + engine-fill.

## Errors / corrections
- None caught by the principal this session. The framing ("much higher") was reframed by the data (moderate + tail-concentrated) — surfaced cleanly, not a misjudgment.

## Pending external actions
None pending. Read-only DB; chat + 1 bank draft only.

## Harvest
- 1 bank draft: `bank/drafts/notes/projects/2026-06-19-non-orwo-expected-understatement-parked.md` (the finding + the park decision). Awaits alch.
- No examine/niksis8/keepsake drafts (Q1–5 empty; no correction/revert this session).

**Cascade.** None into other players or globals. Sibling note: supersedes the scalar-fix framing in the `2026-06-18-ups-carrier-expected-cost-multipliers` bank draft (same defect; the engine-fill replaces per-carrier multipliers) — flagged in the new draft's Related, to reconcile at next alching.

**Main-brain changes.** `players/jebrim/`: 1 bank draft (parked-decision); S278 quest-log (this, completed/); 2 shipping-agent traces (S278_shipagent_*). No globals, no other players, no `confirmed/` promotions.

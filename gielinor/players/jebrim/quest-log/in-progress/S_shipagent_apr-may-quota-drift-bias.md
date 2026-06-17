# Shipping-agent pull — will the re-anchored Apr/May quota drift up as invoices load?

**Spawned by:** Jebrim (principal). Scoped execution engine for a mart pull.
**Player in scope:** Jebrim.
**Tier:** mixed — TASK 1 fully gold-contract; TASK 2/3 OFF-CONTRACT (joins `dw.sales_fact` for archived-dated revenue + expected, per the validated re-anchored series).
**Scope:** TCG = `source_system IN ('Picturator','PicaAPI')`; all production sites EXCEPT Wolfen, PCS CMH, PCS MI, PCS PX. (Pre-resolved in brief.)
**Connection user:** `tcg_nfe` (wider NFE user, gives `dw.*` access — no CLAUDE.local.md present, so flagged off-contract on the dw legs.)

## Turn-by-turn
- Read how_to.md in full + mart-contract.md. No CLAUDE.local.md → gold perimeter is default; dw legs flagged off-contract.
- TASK 1 (bias, on-contract): on already-billed in-scope shipments, actual/expected euro-weighted = Feb 1.040, Mar 1.035, Apr 1.154, May 1.159. Apr+May combined = **1.156**. n=359,854 Apr+May. Bias is recent + widening.
- Robustness: trimmed agg (drop ratios <0.2x / >5x; 1.6% of rows) = **1.077**. ~Half the 15.6% headline is a surcharge tail — 1,034 parcels billing >5x estimate (oversize/handling the estimate doesn't see). Structural per-parcel under-estimate ~8%.
- TASK 2 (fallback share, re-anchored): expected (non-invoiced) leg as share of total cost — Apr **7.6%**, May **21.8%** (May more recent → more invoice lag → bigger fallback leg).
- TASK 3 (projection): replace expected leg with expected×bias.
  - Apr: now 18.49% → 18.60% (low, 1.077) / 18.71% (high, 1.156). Delta **+0.1 to +0.2 pt**.
  - May: now 19.21% → 19.53% (low) / 19.86% (high). Delta **+0.3 to +0.65 pt**.
- Checks: deltas reconcile by hand (expected_leg × (bias−1) ÷ revenue). Brackets monotone. Bias not solely outlier-driven (trimmed still >1).

## Headline
Quota barely moves. Apr fallback share is tiny (7.6%) so even a 15.6% under-estimate adds <0.25 pt. May moves more (~0.3-0.65 pt) only because its fallback leg is still large (21.8%) from invoice lag — that share shrinks toward Apr's as May's invoices land, so the realized May rise is likely toward the low end.

## Caveats / open
- Off-contract dw.sales_fact rebuild — built fresh here (NFE folder not on this machine), so revenue denominator (in-scope-order-bridged) may differ in detail from Jebrim's validated series. The quota DELTA is robust to revenue level (revenue held constant current vs projected); the ABSOLUTE quota level should be reconciled against the validated series before quoting.
- Cross-month: expected is archived-dated, actual ship-dated. Re-anchored method books expected by archived month regardless, so projection is internally consistent; physical settlement moves some euros to later ship-months → May's in-month rise is an upper bound. Small effect.

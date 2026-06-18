# Picturator June 2026 quota crater — maturity artifact investigation

**Spawned by:** Jebrim (principal), shipping-agent emulation
**Tier:** gold-contract (`shipping_mart` only; no CLAUDE.local.md present → gold perimeter absolute)
**Scope:** Picturator (`source_system = 'Picturator'`), order-month lens (`shop_order_created_date`)
**Date:** 2026-06-17 (June is a partial month, 17 days in)

## Ask
Why does Picturator SCM final-quota crater June (~16.2%) vs May (~18.6%) on the 12-month Overview line. Confirm/refute the partial-month cost-maturity hypothesis. Quantify implied mature June quota.

## Status trace
- Verified column mapping: no `order_source` column exists; SCM "Order Source" = `source_system`. Picturator confirmed present (1.31M rows since Jan).
- Quota = final_shipping_cost_eur / net_revenue_eur, order-month. Reproduces SCM Final quota (June 16.06% ≈ SCM 16.2%; May 18.59% ≈ 18.6%). Match confirmed.
- Cost not NULL across the board → rule 36 (reload) does NOT trip. This is a coverage/maturity question.
- Monthly pull Oct-2025…Jun-2026 done: final quota, invoiced quota, cost coverage %, row-state shares.
- **June cost coverage = 20.4%** (invoiced cost €130k / final €636k); 22% rows invoiced, 75.5% on `expected` estimate. Mature months (Jan-Mar): 90-96% coverage. May: 78% (still maturing at obs date).
- Two depressing mechanisms found: (1) `expected` estimate under-predicts actuals by ~35% (€4.3-4.5 booked vs €6.7 invoiced in mature months); (2) June's early-invoiced parcels are a cheap biased sample (€5.20/parcel vs €6.7 mature).
- Denominator clean: June rev/parcel €35.24 = in-band (Jan-May €34.30-35.42). No revenue anomaly.
- **Implied mature June quota = 18.99%** (re-cost all June parcels at €6.69 matured invoiced per-parcel benchmark). Full ~2.9pt gap explained by cost under-fill. Numerator ~100%, denom ~0%, mix ~0%.

## Verdict
**Maturity artifact — expected, self-corrects.** NOT a real cost reduction. June quota will rise to ~18.5-19% as invoices land over the next 4-8 weeks.

## Checks done
- SCM reproduction (June/May quotas match the dashboard figures).
- Coverage cross-month (June 20% vs mature 90-96% — sharp tell).
- Estimate-vs-actual per-parcel gap (estimate runs ~35% low → confirms numerator under-fill direction).
- Denominator sanity (rev/parcel in-band → rules out denominator/mix).
- Reconciliation: implied mature quota (18.99%) lands back in the mature band → gap fully attributed.

## Deliverable
Chat-only findings table returned to principal (no chart requested). SQL in the return summary.

---

## THIRD PASS (2026-06-17) — reconciled additive bridge

**Ask:** the two prior passes produced conflicting implied-mature figures (18.99% waterfall vs 16.54% net, ~2pp apart). Build ONE additive bridge for the observed −2.53pp delta; say which prior number was wrong + the mechanical reason.

**Method (locked):** rate card R_c = each carrier's MAY invoiced per-parcel rate (most mature benchmark for the period — May is 78% invoiced; Jan-Apr flat card under-priced May, June's own early-invoiced sample is biased cheap, so neither is right). MatureCost_m = Σ parcels_{m,c} × R_c, same card both months. Denominator = each month's observed revenue (rev/parcel in-band €34.38→€35.24, no anomaly). Laspeyres hold-one-at-a-time.

**Bridge (sums to −2.53pp, residual 0.00):**
- A. Maturity (net under-fill): **−1.75pp** — June obs sits 1.67pp below mature card (un-invoiced est cheap); May gap +0.08pp. Self-correcting.
- B. Mix / lane / yield: **−0.78pp** — UPS share 20.1→18.3%, Maersk 13.0→15.2%, rev/parcel +2.5%. GENUINE, does NOT self-correct.
- C. Rate: **0.00pp** (same card by construction; no real per-lane rate move once maturity+mix netted).
- D. Residual: **+0.00pp**.

**Implied mature June quota = 17.7–17.9% (state ~17.8%).** June won't return to May's 18.59% even fully invoiced — the −0.78pp mix shift is real.

**Reconciliation — which prior number was wrong:**
- Trace-1's 18.99% (flat €6.69 waterfall): WRONG + not reproducible. Flat €6.69 × June's actual parcel count = 14.77%, not 18.99% (the 18.99% used a too-high flat rate or wrong denom). Flat-rate is structurally wrong anyway — ignores June's cheaper Maersk-up/UPS-down mix.
- Trace-2's 16.54% net: directionally right, slightly low. Reproducible version (keep invoiced + re-cost rest at own-carrier May rate) = 17.63%. Reads low because it KEEPS June's biased-cheap early-invoiced actuals (24,945 parcels @ €5.20) instead of repricing them to mature. Repricing ALL parcels → 17.7–17.9%.
- The ~2pp conflict was: a non-reproducible inflated flat-rate figure (18.99%) vs an un-repriced-early-sample figure (16.54%). Truth sits between, at ~17.8%, and splits cleanly into −1.75pp maturity (self-corrects) + −0.78pp mix (permanent).

**Checks:** bridge sums to −2.53pp exactly (residual 0.00); May mature counterfactual within 0.08pp of May observed (card fits its own month); mix term cross-validated on carrier shares + rev/parcel; both prior methods recomputed live to locate their errors.

**Deliverable:** waterfall table + reconciliation + SQL returned to principal. Bridge scripts in `shipping-agent/scratchpad/picturator-june-quota-bridge.py` + `reconcile-prior-numbers.py`.

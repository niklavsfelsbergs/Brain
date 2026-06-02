# FIF report VAT — compute on the net subtotal, not per-line

Source: `bi-analytics-main/NFE/shipping_topics/42_fif_orwo_ups_invoice_file/pipeline.py` + the bi-etl DAG `fif_ups_orwo_monthly/docker/src/tasks/build_fif.py`. Anchor: [[S143_51f034e4_fif-report-accounting-fixes|S143]]. Companion to [[2026-05-28-ups-orwo-fif-data-quirks]].

**The rule accounting uses (and the real invoice).** VAT = net **subtotal** × rate, rounded **once** at the aggregate grain — not per-charge-line `round(net × 0.19)` summed. Same 19% rate; the difference is purely the rounding grain. Per-line rounding over ~43k lines/month accumulated a **~€16/month** drift on the cumulated VAT (April 2026: per-line €13,889.34 vs subtotal-grain €13,873.36, net unchanged at €104,312.29 — the €15,99 accounting flagged).

**Implementation.** `fold_vat_rows` keeps per-line VAT full-precision (no `.round(2)`); `build_pivot` computes `VAT Total = round(Net Total × rate/100)` on the summed net and `Gross Total = Net Total + VAT Total` (exactly consistent). Mirrors the source Excel's behaviour (live `=net*rate` formula, totals round on display).

**Trap avoided.** The raw bronze `19.000 % Tax` rows sum to a *different* figure (April €13,831.66) — that is NOT accounting's target. Their target is net×rate (€13,873.36). Don't "fix" by switching VAT to the bronze tax-row sum. (Verified against April before coding — see [[feedback_read_domain_knowledge_before_proposing]] discipline.)

**Key-account note.** Prefixes 9102–9105 → single TCG line (`keyaccount_id` 9101), per accounting; ~€9.5k April net moved from the ORWO fallback bucket to TCG.
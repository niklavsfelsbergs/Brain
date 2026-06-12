# Verify a "we don't model X" claim before asserting it — especially against the principal's domain knowledge

**As-of:** 2026-06-12 ([[S220_097ab6e8_eu-tender-q4-mix-seasonality|S220]], sid8 097ab6e8). Anchor: [[S220_097ab6e8_eu-tender-q4-mix-seasonality]].

## The moment

Mid-analysis I wrote, twice, that "the tender doesn't model Warenpost as a carrier" — basing it on a `carriers/` directory listing that showed `dhl_express` and `dhl_paket` but no `warenpost` dir. Niklavs pushed back: *"but what? dont we model warenpost? we have an engine for that."* A grep showed Warenpost is a cheapest-eligible **service tier inside the `dhl_paket` engine** (constants `WARENPOST_MAX_*`, calculate.py prices it). My claim was wrong, and it was load-bearing — I'd half-built a conclusion ("Warenpost seasonality can't enter the engine") on top of it.

## What went wrong

A directory listing is a **narrow** surface — it shows carrier *families*, not the *services* nested inside an engine. I treated absence-in-the-listing as absence-in-the-model. This is the same class as the carrier-dimension-coverage re-audit ([[2026-06-09-carrier-invoice-dimension-coverage]]): a name-scan of the narrow surface false-concluded "no X" for things that lived one layer deeper.

## The rule

Before asserting "we don't model / don't have / there's no X" — particularly when the principal's reaction implies otherwise — **widen the search and verify** (grep the code, read the engine, not just `ls` the dir). Reinforces the standing memory `feedback_never_assert_absence_against_principal_claim`: when Niklavs says it exists, my empty search is "not found yet → widen," never "doesn't exist." Cheap to check, expensive to build a conclusion on a wrong absence-claim.

## What I did right (keep)

Once corrected I didn't defend — I grepped, confirmed I was wrong, said so plainly, and the correction *strengthened* the analysis (measuring Warenpost-eligibility by quarter became the sharpest evidence for the verdict). Fast, non-defensive reversal on being shown wrong is the right shape; the fix is to not make the unverified absence-claim in the first place.

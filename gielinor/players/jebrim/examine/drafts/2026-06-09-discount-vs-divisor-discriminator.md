# A sheet-vs-actuals gap: test discount-vs-parameter before fitting a parameter

**Observation ([[S178_09c2d809_dpd-pl-current-engine|S178]], 09c2d809).** Building the DPD-current engine, the sheet rates
ran ~9% above DPD's invoiced base. I "resolved" it by fitting an effective dim
divisor (÷8000 vs the contract's ÷5000) — a single fudged parameter that centred
the aggregate, dressed up with a plausible-but-unproven "bounding-box volume
overstates billed volume" story. Niklavs pushed back: *"we should have a 9% discount
on top of invoiced amount. Does that explain it better?"* It did — and it was the
**grounded** explanation (a real negotiated term he knew about), not a fit.

**Why the fit was wrong (and how to have caught it myself).** A flat discount and a
billing-parameter (divisor) make *different* predictions, and the data can
discriminate them. The discriminator: split parcels by whether the parameter even
*bites* — for the dim divisor, parcels where actual weight dominates are
divisor-independent. Those parcels were *still* ~5% below sheet — which a divisor
change physically cannot produce, only a multiplicative discount can. I had the data
to run that test before reaching for the fudge; I didn't, because centring the
aggregate *felt* like resolving the gap.

**Rule.** When a model's output sits at a constant ratio off ground truth, first ask
whether a **real commercial/structural lever** (a negotiated discount, a contract
term, a known rebate) explains it — especially one the principal can confirm — before
fitting an engine parameter to absorb it. A fitted parameter that only centres an
*aggregate* is a fudge until a discriminating test rules out the grounded mechanism:
find the subset where the parameter is inert and check whether the gap persists
there. If it does, it's not that parameter. Prefer the lever you can name and the
principal can verify over the constant you tuned. (Same family as
"populated-column-is-not-a-measurement" and "documented-tradeoff-isn't-acceptance":
a number that reconciles is not yet an explanation.)

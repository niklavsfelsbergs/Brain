# Verify an inherited analysis claim before relaying it -- even my own committed notes

**Status:** draft -- principal triages. From [[S277_47bed7aa_uk-yodel-negotiation-levers]] (2026-06-19).

This session I relayed the committed 3_UK analysis's "offshore is +GBP 16k/Q adverse under Yodel (incumbent
absorbed remote)" as settled. When the principal asked to fold offshore into the comparison, I pulled the
actual cost buckets -- and it overturned the claim: the incumbent billed ~EUR 0 remote BUT its offshore base
ran 2x mainland (EUR 7.02 vs 3.28/pcl), so offshore is ~cost-NEUTRAL between today and Yodel (+GBP 1,604),
not +GBP 16k. The committed figure compared Yodel against a *repriced* baseline that understated true offshore
cost.

**Lesson:** a claim sitting in a committed bank note / analysis doc -- even one I wrote -- is still a
hypothesis when it becomes load-bearing for a new decision. The "verify the thing, don't trust the wiring"
reflex applies to inherited *prose*, not just live wiring. Same session also caught `real_shipping_cost_local`
being mixed-currency (would have silently corrupted a total) -- the disagreeing-figure reflex ([[reconcile
definition before numbers]]) flagged it before I reported the bad number.

**How to apply:** when a prior note's number anchors a fresh comparison, re-pull the one figure it rests on
before relaying it -- cheap, and it caught a 10x error here.

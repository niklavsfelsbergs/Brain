# A thinning/sampling threshold tuned for the dense case regresses the sparse case

**Observed:** S247, 2026-06-16. I fixed "no labels on weekly/daily" in the SCM Overview chart by adding density thinning: `labelStep = ceil(points / 14)`. I tuned the constant (14) against the dense case I was fixing (weekly ~26+, daily 100s). I did **not** check it against the case that already worked — monthly. An 18-month monthly view → `ceil(18/14)=2` → every-other label. The principal caught it the next turn ("only every second is showing"). I had to follow up with a per-granularity budget (monthly 24, weekly/daily 14).

**The lesson:** when adding a thinning / sampling / down-selection rule to fix a high-cardinality case, **validate the rule against the LOWEST-count input it will also govern** — not just the dense input that motivated it. A single global threshold silently changes behavior for inputs near the boundary; the case that was already fine can regress. Either special-case the sparse class or set the threshold from what the sparse class needs, then confirm the dense case still thins.

**Why it matters:** the regression shipped (committed + pushed) before the principal saw it. The check was cheap (one mental pass: "what does monthly's point count do under /14?") and would have caught it pre-deploy. This is the close-the-blast-radius discipline applied to a parameter, not just code.

Anchor: CostTrend.tsx labelStep; commits `64edeec` (the regression) → `eb6bdee` (the fix).

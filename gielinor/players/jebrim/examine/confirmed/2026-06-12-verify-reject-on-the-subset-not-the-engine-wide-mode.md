# Verify the reject reason on the actual subset, not the engine-wide dominant mode

**Observation ([[S221_eec4ee99_eu-tender-report-review-qa|S221]], 2026-06-12).** Tracing why ~1% of DPD-Poland's parcels showed as "carrier-level rates" (NULL service), I inspected the `dpd_pl_current` cost-matrix rows and saw the only NULL-service rows engine-wide were `over_max_girth` (32,542 of them). I formed the hypothesis — and stated it to Niklavs as the likely cause — that the 1% were **oversize/over-girth** parcels.

**It was wrong.** When I joined the *actual routed-but-NULL* shipment_ids back to the cost matrix, their rejects were **`country_not_served` (93%, all PL) + `over_max_weight` (7%)** — `over_max_girth` was not in the subset at all. The engine-wide dominant NULL reason ≠ the reason for the specific subset I was explaining.

**Lesson.** A reject_reason (or any categorical label) tallied across a whole population is a hypothesis about any *subset* of it, not a fact. When explaining why a *specific selected slice* has a property, filter to that slice's actual rows and read the reason there — don't generalize from the population's modal value. I caught it by verifying before the load-bearing claim landed (good), but I'd already voiced the wrong cause once.

Sibling of the recalled lessons: *populated column ≠ measurement*, *selection evidence isn't class evidence*, *categorical class needs a physical cross-check*. Same family — the property of the whole isn't the property of the part until checked on the part.

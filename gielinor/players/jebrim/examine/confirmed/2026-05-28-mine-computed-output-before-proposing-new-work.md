# Mine existing computed output before proposing new work

**Observation ([[S118_f41737e5_eu-tender-decision-scorer-report-regen|S118]], 2026-05-28).** Asked "what can we do in the meantime [while waiting on carriers]?", I offered a menu of *new* workstreams (full-year scoping, service-quality sidecar, fuel sensitivity sweep). The principal redirected: *"can't we already test out the scenario calculations for the carriers which we have full engines for?"* — and he was right: I'd re-run `decision_scorer.py` (90 sets in `scenarios.parquet`) earlier the same session but had never actually *read the decision signal off it*. The regen was mechanical; nobody had interpreted it.

**Rule.** When computed output already exists (a re-run parquet, a regenerated report, a materialized matrix), **mine it for the answer before proposing new analysis.** Re-running a generator is not the same as extracting its signal — the interpretation step is the deliverable, and it's cheap relative to standing up a new workstream. Default to "what can the artifacts we already have tell us?" before "what new thing could we build?"

**How to apply.** After any scorer/matrix/report regen, the next move is a read-off (leading result + robustness + what it hinges on), not a hand-off. Surface that read *first* when asked "what's next," then offer new workstreams as the layer beyond it.

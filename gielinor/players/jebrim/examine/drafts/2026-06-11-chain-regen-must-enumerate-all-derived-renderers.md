# A chain regen must enumerate ALL derived renderers — the verify gate only covers what it was built to cover

**Moment (sid8 9399f067, 2026-06-11, UPS cascade step 7):** I regenerated the report chain (matrix → scorer → routing → annual → final_report) and got verify_report PASS — and nearly committed with `routing_2026q1/routing_report.html` and `annual_2026/annual_report.html` still rendering the superseded [[S203_021047a4_q09-baseline-bridge|S203]] numbers. verify_report checks final_report against annual_stats; it says nothing about the OTHER two HTML renderers downstream of the same stats files. Caught only at commit time, when the pathspec audit made me ask why those files showed as modified-by-someone-else.

**The pattern:** a PASS from the chain's verify gate reads as "the chain is consistent" but actually means "the artifacts the gate enumerates are consistent." Sibling renderers added later (routing_report.py, annual_report.py) sit outside the gate's coverage, so a regen that runs only the gated path leaves them silently stale — the derived-report-drift failure mode, one level up: not prose-vs-data but renderer-vs-stats.

**Rule:** when regenerating a derived chain, enumerate consumers of the regenerated stats files (grep for the stats filename) and re-run every renderer — don't infer completeness from the verify gate's PASS. Where feasible, propose adding the missing artifacts to the gate itself.

Sibling of: fix-the-class-across-sibling-consumers ([[S178_09c2d809_dpd-pl-current-engine|S178]]), derived-report-prose-drifts ([[S180_4766eb11_dpd-current-report-refresh|S180]]).

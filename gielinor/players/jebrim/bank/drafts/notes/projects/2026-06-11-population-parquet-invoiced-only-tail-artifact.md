# EU-tender population parquet — invoiced-only basis thins the window tail (fake label deaths)

**Source:** [[S197_b93204b5_q04e-label-churn-deep-dive|S197]] (sid8 b93204b5) q04e label-churn deep dive, 2026-06-11. Findings note: bi-analytics `NFE/projects/2_EU_tender_2026/2_analysis/result_investigation/q04e_label_churn_deep_dive_findings.md`.

**The fact.** `2_analysis/data/population_2026q1.parquet` is invoiced-only (tender scope). For invoice-lagged volume (freight especially), the last ~2 weeks of the window thin out: GEL showed 60/wk → 1 → 0 across late March in the parquet, while the live mart shows GEL steady 69–81/wk through the same window and ~330/mo through June 2026. The "label stopped" read was pure extract artifact.

**Rule of use.** Never read label/carrier deaths, stops, or share collapses off the parquet's final ~2 weeks — verify against the live mart (shipping-agent) first. Symmetrically, q04d/q04e-style monthly Jan→Mar comparisons are safe in the interior of the window but not at its edge.

**Related q04e verdicts (detail in the findings note):** WICKEL 80x60 family → ORWO_80x60 = relabel-equivalent (fold; carrier-side swap 2026-02-23); STANZ 120x90→120x80 = real size change crossing Maersk ≤300 L+girth, and a *reversion* to S80's 2-year incumbency, not a takeover (re-weight cells ~3×, don't fold).

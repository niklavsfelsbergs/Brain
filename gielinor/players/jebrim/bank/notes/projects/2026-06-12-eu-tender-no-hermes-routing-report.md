# EU tender — the no-Hermes routing report (+ the scenario-variant build pattern)

**Artifact.** `bi-analytics-main/.../2_analysis/routing_2026q1/no_hermes/routing_report_no_hermes.html`
— the executed-plan cell table (one carrier per destination × packagetype × weight band) for the
**no-Hermes 5-carrier** scenario. Sibling of the with-Hermes `routing_2026q1/routing_report.html`.
Built 2026-06-12 ([[S226_da65054b_eu-tender-routing-report-no-hermes|S226]]). Headline Q1 €209,028 / annual €976,024/yr; DBS oversize pinned to freight;
the +€696k/yr UPS/DHL reroute is the gated upside (excluded).

**The two report families (don't conflate).** `routing_2026q1/` = the *executed-plan cell grid*
("what's going where"). `final_report_no_hermes_v2/` = the *savings narrative*. The no-Hermes
routing was always *computed* (`build_stats_no_hermes.py` monkeypatches the engine to FINAL_5)
but never *rendered* at cell grain until this report.

**The build pattern — parametrize the authoritative builder, don't fork.** The routing math lives
in `build_final.py` (mirrored in `annual_2026/q1_base.py`); repo rule = "one routing, synced
lockstep." So for a scenario variant: add params to `build_final.py` —
`build(final=carrier_set, pin_dbs=bool, out_dir, scenario)` — defaults unchanged (verify the
default run is scalar-stats-identical to canon), then `python build_final.py no_hermes`. Same for
`carrier_envelopes.py` (`data_dir`). The *renderer*, by contrast, follows the repo's own precedent
of **dedicated** no-Hermes report files (`report_no_hermes_v2.py`) — prose diverges too much to
thread conditionals. So: parametrize the math, fork the narrative.

**The DBS pin — cell-grain vs parcel-grain reconciliation gap.** "Pin DBS to freight" maps to a
clean cell rule (DBS-dominated std cells force-keep db_schenker; variable DBS-origin parcels pin
per-parcel) because **99.96% of DBS-origin std parcels sit in DBS-dominated cells**. The executed
grid then reconciles to the parcel-grain €976k headline within **€3,280 Q1** — the ~226 non-DBS
parcels sharing a DBS-dominated cell, which follow the cell onto freight (a cell commits to one
carrier; the savings idealisation splits them). do-nothing + parcel count tie exactly. This is the
same decision-vs-routing operational gap the tender already documents — report it, don't distort
the grid to hide it.

**Next variant teed up (Niklavs deferred, [[S225_9f716f1f_guell-2.0.0-build|S225]]):** does adding Güll to the no-Hermes 5-carrier
portfolio give meaningful savings? Same machinery, `final = FINAL_5 | {guell}`.

Source: `routing_2026q1/{build_final,carrier_envelopes}.py` + `no_hermes/routing_report_no_hermes.py`;
committed bi-analytics `9d171a2`. Builds on [[eu-tender]] domain; sibling of the no-Hermes final
report ([[S212_177f00f1_eu-tender-no-hermes-report|S212]]/[[S219_e0eb59c8_eu-tender-final-report-content-pass|S219]]/[[S221_eec4ee99_eu-tender-report-review-qa|S221]]).

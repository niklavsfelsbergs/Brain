# S212 · eu-tender — no-Hermes final report + UPS routing Q&A

**Actor:** Jebrim · **sid8:** 177f00f1 · **Domain:** [[eu-tender]]
**Pending external actions:** None pending. (bi-analytics report files written to disk, uncommitted — a principal decision, not a dangling action.)

EU-tender questions session. Answered routing questions, reformatted the main report's service-mix table, and built a no-Hermes companion report. Surfaced two material findings along the way.

## Turn log

- **UPS migration question.** Niklavs asked why, given the new UPS offer, only DB Schenker (+ Direct Link) migrate *to* UPS. Answer: routing commits one carrier per (dest×product) cell; an "A→UPS" flow needs A currently holding the cell AND UPS cheapest there. UPS is a net *donor* (sheds ~371k, gains ~22k). The two to-UPS flows differ: DBS→UPS +€450k (UPS genuinely cheapest), Direct-Link→UPS −€34k (Direct Link dropped, parcels inherited at a small loss). Wholesale UPS = −€50.9k (scorer); the offer wins per-cell, not per-book.

- **Service-mix table reformat (main report).** Edited `final_report/final_report.py` service_table: carrier total moved onto the carrier row (mint accent, after the name), service rows show **% share only**, parcel count dropped. Regenerated `final_report.html`.

- **Built `final_report_no_hermes/`.** Scenario: decline Hermes → oversize module off. Principal chose (AskUserQuestion) the **conservative basis**: DBS oversize stays on freight, headline = **€976,024/yr (6.47%)** = exactly `annual_stats.structure.base_ann` (reconciles Δ €0.00). Two scripts: `build_stats_no_hermes.py` (qb.build_pp no-Hermes primary, DBS pinned, service via cost-matrix with_service replay, asserts vs published base) → `stats_no_hermes.json`; `report_no_hermes.py` → `report_no_hermes.html`. Module sections dropped; Hermes → "not selected"; single-number story.

- **Finding 1 — DBS reroute survives without Hermes.** The optimizer re-homes most DBS oversize onto UPS (€514k) + DHL (€173k) = **€696k/yr** even without Hermes — contradicting the main report's "no parcel-carrier home without Hermes" prose. Hermes' *unique* value is only ~€237k/yr, not the €933k module headline. Rendered as a not-banked "Optional upside" caveat (template dims + the [[S205_f08474c9_ups-round1-reply-review|S205]] zV-on-UPS routing-mistake flag).

- **Finding 2 — "old contract in the routing" = UPS WW-ECO/Australia tail.** UPS competes as incumbent-keep (current contract ×1.05 GRI) AND new-offer engine, per cell. The null-service "carrier-level" UPS rows = the **WW-ECO tail, which is entirely Australia** (2,636 Q1 / ~11k yr): the 2026 offer is EU-scoped and rejects AU (no WWE product), so they're kept on the current contract. €0 saving (doesn't inflate headline), but if signing the new offer *ends* the current contract, AU has no modeled price — reassigning to the cheapest portfolio alt (DHL Paket + Maersk) costs **+€211k/yr** (UPS's AU rate ~€27/parcel is the cheapest available). Relabeled the service row → "Australia — current UPS contract (not in 2026 offer)" + legend note. Niklavs is checking for a possible UPS AU special offer.

- **GB/US scope.** Both **absent from the cost matrix entirely** — tender scope is 17 destinations (AT AU BE CH DE DK ES FI FR IE IT LU NL NO PL PT SE). So GB/US are not priced in either report; any high GB/US pricing Niklavs saw is from another artifact (carrier_overview / mart) or the live sibling [[S211_dcd18cfd_ups-savings-dbschenker-reroute-investigation|S211]] UPSWWE check.

## Decisions made

- No-Hermes headline = conservative base (€976k), DBS pinned to freight — **principal-chosen** over the full optimizer output (€1,672k) because the DBS-reroute-without-Hermes rests on template dims + the zV-on-UPS mistake.
- AU tail left in the report on the current UPS contract, honestly labeled, pending Niklavs's special-offer check.

## Cascade.
Touched only the bi-analytics EU-tender repo (`final_report_no_hermes/` new; `final_report/final_report.py` service-mix edit). No gielinor cascade. The AU-relabel + service-mix-format are NOT yet mirrored into the main `final_report/` — left as an offered follow-up.

## Main-brain changes.
None to `gielinor/` content beyond this close (quest-log, inventory, comms, one bank draft).

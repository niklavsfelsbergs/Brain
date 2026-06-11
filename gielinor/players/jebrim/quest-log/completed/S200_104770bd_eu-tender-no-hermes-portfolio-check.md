# S200 — EU tender: no-Hermes 6-carrier portfolio check

> sid8: `104770bd` · 2026-06-11 · Jebrim · born + closed same session
> Question-and-answer session off the [[S194_907d4e63_eu-tender-holdup-pass-and-project-rating|S194]] final-report state. No bi-analytics writes; analysis read-only.

## The ask

Final report surfaced that Hermes might not be picked (dims gate + appetite risk). Niklavs: *if we drop Hermes, do we have a 6-carrier portfolio which beats the picked 5?*

## What was done

1. Grounded in the [[S194_907d4e63_eu-tender-holdup-pass-and-project-rating|S194]] resume (`inventory/eu-tender-final-report-resume__907d4e63.md`) + [[eu-tender]] digest. Base portfolio = dhl_paket, dpd_pl, ups, maersk (FR keep + EU new = one family), db_schenker; Hermes only enters as the oversize module.
2. Read the scored landscape `2_analysis/data/scenarios_2026q1.parquet` (82 decision sets, 2026-06-10 17:10 build, current cost matrix) + `_decision_sets_2026q1.py` for the candidate pool: dhl_express, gls, guell, austrian_post, fedex (Yodel never engined; DPD tender offer declined).
3. Decomposed the per-carrier slices of the candidate 6th-slot scenarios; checked engine trust vs `decision_report/bias_table.md` (stale 2026-05-22 vintage — flagged).

## The answer (delivered in chat)

- **Yes on paper, mostly no in substance.** Q1 cherry-pick basis, ≤6 cap: base-5 saves €258,263 (8.74%); with-Hermes-6 €347,476 (11.76%).
- **+DHL Express (€378,266, +€120k) is a mirage**: ~€84k of it is DBS-origin freight parcels (DBS slice 5,062→2,690) — the same conditional oversize slice the Hermes module carries, gated on the same dims check, priced by an engine last measured at 196% of invoice (tiny slice, stale table).
- **+Güell (€307,465, +€49k) is the defensible 6th slot**: parcel-shaped wins (14.6k parcels, DBS untouched), engine at 0.75 of invoice (fresh-bid undercut). Risk is commercial (rates holding), not modeling.
- +FedEx +€55k (partly same mirage, 1.73 bias); +Austrian Post +€22k; +GLS +€1k.
- Net: the base-5 pick survives a Hermes exit intact; the freed slot buys at most a thin Güell add. Numbers are selection-ceiling Q1, not routing-annual — a cell-level routing run + annualization for base+Güell is the missing piece if the report should carry the option (offered; not commissioned).

## Conclusion-levers confirmation (turn 2)

Niklavs' list (DBS dims, Güell + UPS final answers) confirmed with precisions: DBS dims gates *both* Hermes and the DHL-Express mirage; UPS GRI 5↔5.9 is only ±€19k/yr (magnitude) but a UPS *re-bid* would be unmodeled and could reshape the pick; Maersk EU fuel band (±€28k/yr) and DHL thin-flat waiver move numbers, not the pick.

## Correction beat (turn 3)

I characterized the DHL thin-flat waiver as a both-ways mover ("erode or pad the base"). Niklavs challenged ("sperrgut 20 eur? that wont disappear") → grounded in `carrier_overview_v2/sections/dhl_paket.md` + phase-1 verification: it's a negotiated Sperrgut *exemption for thin flats* (<1 cm, d_mid>60 trips; 362k parcels, 12.8% of DHL volume), in negotiation (pending Stefan), and the engine prices the full €20 today → **upside-only**. Corrected in-chat; examine draft captured (see harvest).

## Found at close — final_stats.json internal drift (REPORT TO THREAD OWNER)

Post-S198-rebase (2026-06-11 12:45 cascade), `annual_2026/annual_stats.json` structure = **base €393,477 / module €581,215** (sum €974,692, matches the [[S198_cbc40f78_fr-incumbent-rebase|S198]] headline), but `final_report/final_stats.json` structure still = **base €420,218 / module €577,502** (sum €997,720, pre-rebase) while its own `annual.saving` = €974,692. The build_final_stats cross-assert presumably ran before build_annual regenerated → ordering gap; **final_report.html renders a stale base KPI that disagrees with the annual report.** 3rd recurrence of fix-the-class-across-sibling-consumers on this report pair. Belongs to the [[S194_907d4e63_eu-tender-holdup-pass-and-project-rating|S194]]/[[S198_cbc40f78_fr-incumbent-rebase|S198]] thread (bi-analytics is principal-gated; live siblings own it) — surfaced in the close statement, not fixed here.

(The €420,218 base quoted in this session's turn-1 answer is therefore the stale vintage; current is €393,477. Structural conclusions unaffected.)

## Process notes

- **No OPEN posted** — session entered via address and went straight to work; respawn comms step missed (siblings logged me as "unknown actor, no OPEN in tail"). Per close ritual, no bare CLOSING posted; miss recorded here.
- SNNN: disk max was [[S198_cbc40f78_fr-incumbent-rebase|S198]] but live sibling ee882f39 publicly claimed [[S199_ee882f39_sa_ups-oml-lps-predictor|S199]] in its comms OPEN → took **S200** to avoid a duplicate.
- No pending external actions.

## Harvest

- `bank/drafts/notes/projects/2026-06-11-eu-tender-no-hermes-6th-slot-landscape.md`
- `examine/drafts/2026-06-11-ground-open-item-direction-before-characterizing.md`

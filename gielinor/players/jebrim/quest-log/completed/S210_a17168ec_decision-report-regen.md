# S210 · decision_report regen — the lone UPS-cascade straggler

**Player:** Jebrim · **sid8:** a17168ec · **2026-06-11**
**Deliverable:** shipped + committed (bi-analytics `5fb7289`, pathspec `decision_report/` only; not pushed).

## What was asked

Regenerate the EU tender `decision_report` — the one report the [[S208_9399f067_ups-cascade|S208]] UPS cascade re-scored
but never re-rendered. `decision_report.html` predated the cascade (Jun 10 17:10) while
routing/annual/final/carrier_overview were all rebuilt on the refreshed engines.

## What happened

- **Grounded first** in the two cascade resume files (carrier-overview-v2 [[S209_89e4a123_carrier-overview-v2-rederive|S209]] + ups-cascade
  [[S208_9399f067_ups-cascade|S208]]) + the routing canon, before touching anything. Established that the *inputs* were
  already fresh (`cost_matrix_2026q1` + `scenarios_2026q1` scorer + `_decision_sets_2026q1`
  with `ups` in `RENEWABLES`, all Jun 11 19:2x) and committed in the cascade (`19bc826`) —
  only `report_2026q1.py` had never been re-run, and its hardcoded prose was stale.
- **Scope = re-run + targeted source edits** (not a pure re-render): the script's narrative
  hardcoded "UPS INCUMBENT-only, no offer yet" + engine stamps maersk-3.0.0 / hermes-2.0.0,
  which a re-run does not fix.
- **Edits to `report_2026q1.py`:** UPS narrative rewritten to the sign decision (current
  contract being replaced → "keep today" off the table; wins per-cell not per-book; CH
  operative-tier base = negotiate, Nordics oversize/LPS = dispute, pre-signature levers);
  pending-table UPS row updated likewise; engine stamps → maersk-3.2.0, hermes-2.2.0
  (verified against `carriers/*/constants.py`, not the brief text). Re-rendered.
- **Verify PASS:** no brace/None leak (`{text}`/`{x}` are Plotly hovertemplate tokens);
  canon present + matching the scorer (lead €174,633, ceiling €222,228, routing €395,197,
  baseline €2.96M, renew_ups −€50,908 rendered red); engine versions match the matrix;
  UPS card badge = NEW OFFER; diagnostic table has a ups engine row.

## Decisions / findings

- **Firm full-cover ≤6 lead moved €306k → €174,633** and the +1 entrant flipped DHL Express →
  Hermes — but the *recommended six did not change* (it was already DHL Paket · Maersk ·
  Hermes · DPD-PL · UPS · DB Schenker per final_report). The drop is honest: all-renewals
  sets now renew UPS, whose 2026 offer is −€50.9k wholesale. Proof: `keepfr_maersk_eu_plus_hermes`
  (the one set that *keeps* UPS at today's invoice) is identical pre/post at €222,228.
- **"Higher points on the chart" reconciled** (principal Q): every set above the lead fails one
  of three gates — over the locked cap-6, strands >100 parcels, or leans on held Güll. Best
  firm full-cover **7-carrier** set = `...dhl_express_hermes` €197,891 → relaxing cap-6 to 7
  buys **+€23,258 Q1** via DHL Express. Cap-6 is the principal's own 2026-05-12 lock, relaxable.
- **Pre-existing (NOT touched):** the "Held ceiling (leans on Güll)" KPI + "raw top puts Güll
  in NEW_OFFER" bullet were *already* mislabeled in the committed Jun-10 HTML (pointed at a
  non-Güll set). Out of scope for UPS+canon; flagged for a separate ceiling-KPI pass.

## Follow-ups (carried, not this quest's deliverable)

- **Bank digest re-stamp — deferred to alching (principal call S210).**
  `bank/domains/eu-tender.md` line 49 still headlines the S194-era Q1 €201,916 / annual
  €997,720 frame. Re-stamp target: Q1 €395,197 (12.93%) / annual €1,908,707 (12.66%, band
  1,882,470–1,934,944) / firm €990,225 + DBS-contingent €918,482 / 5 reports current / engines
  incl. ups-2.0.1 + dpd_pl_current-1.0.0. It's a *reframe* (base+module → firm+contingent),
  not a number swap. Detail in archived resume `inventory/archive/decision-report-regen-resume__a17168ec.md`.
- **Offered (not accepted):** properly annualize the 7-carrier (+DHL Express) delta via the
  seasonal re-weight so the cap-6-vs-7 trade can be weighed.

## Pending external actions

None pending. Deliverable committed (bi-analytics `5fb7289`); never pushed.

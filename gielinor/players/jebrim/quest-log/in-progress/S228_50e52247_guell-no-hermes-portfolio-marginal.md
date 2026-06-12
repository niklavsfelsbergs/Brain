# S228 — Güll → no-Hermes portfolio marginal (the S225-deferred question)

**Session:** 50e52247 · 2026-06-12 · Jebrim · continuation of [[S225_9f716f1f_guell-2.0.0-build|S225]] (guell-2.0.0 build).
**Mode:** read-only investigation over bi-analytics; brain-namespace writes only.

## Ask

Niklavs deferred at [[S225_9f716f1f_guell-2.0.0-build|S225]]: *does adding Güll to the 5-carrier no-Hermes EU-tender portfolio (€976,024 base, `final_report_no_hermes_v2/`) give meaningful savings?* Then, across the turn: per-country won volume; "is Güll worth considering?"; which engine assumptions might understate Güll's cost; explain the pallet-contract mechanics to frame a logistics-manager question; and whether a no-Hermes+Güll report is buildable now at 150/pallet.

## What was done / found

**Marginal.** Pinned the portfolio first (didn't guess): the no-Hermes-5 = `all_renewals` in the full-year `_decision_sets.py` scorer (DHL-Paket/Maersk/DPD-PL NEW_OFFER + UPS/DBS INCUMBENT, all entrants OFF), membership-equal to `build_stats_no_hermes.py`'s `FINAL_5`. Read off current `scenarios.parquet`: `all_renewals` €456,541 → `all_renewals_plus_guell` €620,438 = **+€163,897/yr PAPER** (+36%). Hermes-isolation: off `all_renewals_plus_hermes` the Güll marginal is +€150,617, so removing Hermes frees only ~€13k — the 164-vs-61 gap is mostly general saturation, not Hermes. Hypothesis confirmed in sign, modest in size.

**Two-pipeline catch (load-bearing).** The €976,024 report is NOT the decision-set `all_renewals` — it's the q1 routing pipeline (`q1_base.build_pp` + `cost_matrix_2026q1`, UPS-on-engine, DBS-pinned). Membership-equal ≠ numerically-equal; the +€164k does not add onto €976,024.

**Per-country (annual won):** AT 79,497 (of 139,246 eligible, 57%, €5.34 avg) + CH 31,523 (of 53,712, 59%, €8.56 avg) = 111,020 parcels, €694,030. No LI volume. Donors: Maersk −61.8k/−€351k (biggest), UPS −23.8k, DPD −15.7k, DHL −8.8k, DBS −849/−€101k (likely eligibility artifact, flagged).

**Verdict on "should Güll be considered":** yes as a real candidate — no-Hermes is its best case, beats Austrian Post for the AT/CH slot by ~€105k — but PAPER, not sign. Defensible floor ~€60–120k after no-parity + assumption haircuts. The decision is "onboard an unvalidated carrier for a probably-€60–120k prize on lanes incumbents already cover," not "is the number good."

**Understatement assumptions (ranked):** (1) density 150/pallet — dominant, divisor on inbound sprinter €0.80 + outbound AT €0.16/CH €0.27; 150→100 ≈ +€28–55k; sprinter weight-cap (1,000 kg) may bind before pallet-cap. (2) FX 1.08 strongest-of-month proxy. (3) outbound per-pallet rates Q11-open. (4) AT bulky shape un-wired. Principal calls: #2 keep 1.08, #4 ignore shape, #5 use Güll's stated outbound rates — all three already encoded in guell-2.0.0, no rebuild.

**Contract pallet mechanics** (Q10/Q11, from REVIEW_CONCLUSIONS + cost_calculation_tree): inbound €955/sprinter qty-independent, cap 8 pallets/1,000 kg; outbound €24.50 AT / €40 CH per pallet, cap 1.85 m/300 kg; both all-in (insurance excl). Contract fixes the container price; Picanova ops supplies the fill. Framed a logistics-manager question (delivered in chat, plain-text): realistic parcels-per-pallet AT/CH + per-sprinter, and whether fill binds on volume or weight first; flagged the ~€40k-per-50-parcels sensitivity and the shared-trailer upside lever.

**Feasibility of a no-Hermes+Güll report:** small build, not a cascade. Güll already priced in the q1 pipeline (wins cells in `build_routing.py` emergent routing; "[HELD/provisional]" is only a print label). Add `"guell"` to `build_stats_no_hermes.py` FINAL set + `FAMILY_TO_ENGINE`, re-run stats→report→deck (~1–2h). Report re-derives Güll in its conservative basis → expect < +€164k = the management-ready number. 150/pallet revisable via the one constant (re-run engine prices, not just the report). **Recommended next-session deliverable.**

## Harvest

- Bank draft: `bank/drafts/notes/projects/2026-06-12-guell-no-hermes-marginal-and-density-gate.md` (the consolidated finding).

## Open / handed to resume

- Build the no-Hermes+Güll standalone report variant (next session; 150/pallet flagged on page).
- Logistics-manager density question (the one data item that firms the marginal).
- Commerzbank strongest-of-month FX pull (non-blocking).
- bi-analytics [[S225_9f716f1f_guell-2.0.0-build|S225]] edits still UNCOMMITTED (await Niklavs commit go — separate repo).

## Cascade / main-brain changes

- Cascade: none (read-only investigation; no bi-analytics writes this session).
- Main-brain changes: bank draft + this quest-log + resume update + comms OPEN/CLOSING. Commit held at principal's request (small convo continuing before close).

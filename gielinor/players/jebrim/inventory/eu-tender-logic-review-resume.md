# EU Tender Logic Review — Resume State

**Quest:** `S034_2026-05-22_eu-tender-logic-review.md`
**Status:** in-progress (deliverable shipped; follow-ups open)
**Last touched:** 2026-05-22 (S034 close)

## Where we are

Logic review of the EU Tender 2026 Phase 2 codebase (`bi-analytics-main/NFE/projects/2_EU_tender_2026/`) shipped via 7 audit dwarves (D1-D7) + 8 fix dwarves (F1-F8). All 15 dwarf deliverables in `quest-log/completed/`. EU tender repo carries uncommitted F1-F8 changes — needs a separate commit in `bi-analytics-main/`.

The headline shift from the work: F6 wired FedEx + DPD PL into the scorer, surfacing `renew_maersk_plus_fedex` (EUR 377k mandatory) as the new #2 cap6 portfolio. `renew_dpd_pl` standalone = -EUR 416k — confirms DPD PL retire-only stance.

## Next concrete step

Triage the 5 explicit open items from the S034 delivery summary:

1. **Re-run F4 against the F6-wired scorer.** F4 used full-eligibility slice for DPD PL + FedEx because they were scorer-invisible at F4-time. Now they're wired — recompute their winning-slice bias ratios.
2. **Commit the EU tender repo changes.** `bi-analytics-main/` has uncommitted F1-F8 modifications. Either ask the principal to commit, or do it under explicit authorisation.
3. **Audit population grain.** F5 surfaced that `sql/population.sql` is trackingnumber-grain but `decision_scorer.py:58` does `.unique(subset="shipment_id")`. Quantify the drop with a quick polars count.
4. **Decide on the engine bumps deferred by F7.** AP→2.0.0 (CH customs + multi-service + line-haul) and Maersk→3.0.0 (fuel 5% + AT/DE/DK tolls). Each is a hours-to-days workstream; ship when the principal wants.
5. **Cleanup:** prune the two `_s034_f2_verify_*.py` ad-hoc scripts in `2_analysis/`; add FedEx prose to `CARRIER_NARRATIVE`.

Lower-priority parking:
- Enumeration cartesian-growth question (F6 noted: 90 decision sets from 35; full enumeration to be evaluated against the §B.6/§B.13 supersession).
- Maersk Q-DBS-1 carrier-facing follow-up Qs raised by F1 (ES tier axis, IT band semantics, CH intent) — already in the existing dispatch backlog.

## Files / paths to read first

- `gielinor/players/jebrim/quest-log/in-progress/S034_2026-05-22_eu-tender-logic-review.md` — the parent narrative with turn log.
- `gielinor/players/jebrim/quest-log/completed/S034_d1_maersk.md` through `S034_f8_freight_drop.md` — per-dwarf detail.
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/DECISIONS.md` — six 2026-05-22 entries land here from F1/F2/F6/F7/F8.
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/bias_table.md` — refreshed by F4.

## Pending drafts

None blocking. Harvest produced two drafts (see step-6 surface in S034 close).

# S184 · Decision report — headline the decision-vs-routing savings reconciliation

**Player:** Jebrim · **sid8:** bc889f31 · **2026-06-09**
**Repo touched:** `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/decision_report/` (external — principal-gated, uncommitted)

## What this was

Niklavs asked why the decision report's headline savings number doesn't match the routing report's, then asked me to **headline that reconciliation inside the decision report** so it's clear.

## The reconciliation (the answer)

Two reports, **same €2.96M Q1 invoiced-actuals baseline**, different question — so the numbers differ by design, not by error:

- **Decision report = selection leaderboard.** 82 candidate carrier sets scored by **mandatory saving** — every parcel to the cheapest *eligible bid in the set*, no operational constraint. Leading ≤6 candidate = **€430,055 (14.6%)** (`all_renewals_*` set, DPD-PL as NEW_OFFER).
- **Routing report = executed plan.** One chosen forward-basis portfolio routed under the real **one-carrier-per-cell** rule (a destination×packagetype cell commits to a single carrier). Executed saving = **€377,471 (12.8%)**.
- **The gap is operational.** Per-parcel theoretical floor €2,475,020 → committed routing €2,577,549 = the **€102,529 "operational gap."** The routing portfolio also fixes each carrier's forward basis (DPD-PL kept on *current* contract, not its new offer) and uses a GRI-free baseline; the leaderboard's best-case sets don't.
- **Bottom line:** decision-report figures are best-case selection ceilings; €377,471 is what the chosen plan actually captures. Quote routing operationally, the leaderboard to compare sets.

Note: `REPORT_NOTES.md` still carries a stale €635k/yr full-year line (pre-S182 scenario basis); both live HTMLs are 2026-06-09 on the Q1 basis.

## What I built

In `decision_report/report_2026q1.py`:

1. **Live cross-read** of `routing_2026q1/routing_stats.json` (`routing` dict, graceful `None` fallback if absent) — so the callout never drifts from the routing deliverable (the derived-report-prose-drifts-from-data guard).
2. **A `warn`-styled headline callout** "Headline: why this differs from the routing report," placed in the top intro region (after the "What changed vs prior" callout, before block 01). Renders the selection-vs-executed framing + the €377,471 / €102,529 figures dynamically.

Regenerated `decision_report.html`; verified the callout rendered with the correct live figures (430,055 / 377,471 / 2,475,020 / 2,577,549 / 102,529).

## Pending external actions

None pending in-session. The `bi-analytics-main` commit is **gated on Niklavs's go** (see resume `open_dep`). Offered but not yet actioned: updating the stale `REPORT_NOTES.md` €635k/yr line.

## Cascade / Main-brain changes

None to brain content this session — all substantive work was in the external `bi-analytics-main` repo. Brain close artifacts only: this quest-log entry, the inventory resume, one bank draft (the decision-vs-routing reconciliation as durable EU-tender domain knowledge).

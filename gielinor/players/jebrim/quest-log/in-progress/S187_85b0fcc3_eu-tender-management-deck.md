# S187 — EU Tender 2026 management slide deck (Q1 basis)

**Player:** Jebrim. **sid8:** 85b0fcc3.
**Ask:** build a self-contained reveal.js HTML briefing deck for senior management (Ops VP / C-level) on the EU Tender 2026 carrier decision — Q1-only basis (531,194 parcels), outcome-first plain-business language, ~12–16 slides on a fixed 9-point arc, every figure sourced from the rebuilt reports (no recall), unsourceable items flagged.

## Turn log

- Grounded off the eu-tender domain digest + 3 bank notes (routing-cost-basis, db-schenker-reroute, hermes-slice) + keepsake. Read the three rebuilt reports: `routing_2026q1/{routing_stats.json,routing_report.html}`, `carrier_overview_v2/{exec_brief,carrier_overview}.html`, `decision_report/decision_report.html` (stripped tags to text via a temp `_deck_tmp/`, since console can't encode unicode; scratch moved out of repo after).
- Built deck → `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/management_briefing/eu_tender_2026_briefing.html`. 12 slides, reveal.js 4.6.1 from CDN, speaker-notes with sourced figures per slide. Single file, opens by double-click.
- **Headline figures (all Q1, sourced to `routing_stats.json` + decision_report):** today €2,955,020 (€2.96M); routed €2,577,549; saving €377,471 (12.8%); op_gap €102,529; 531,194 parcels. Portfolio (6): DHL Paket 282,638/€961k · DPD-PL 88,985/€439k · Hermes 68,191/€368k · Maersk 60,523/€396k · UPS 29,781/€312k · DB Schenker 1,076/€102k (sum = routed_total ✓). Decisions: sign Maersk EU (~€306k lever), keep Maersk-FR (€4.72 flat, tender can't price FR), decline DPD offer + keep current (−0.4% validated engine; worse on 100% material volume), add Hermes. Per-market saving bars computed from by_dest (DE €182k…SE −€6k, only loser). Used the FINAL rebuilt routing as authoritative (not the earlier Hermes/UPS bank-note splits).
- **Niklavs corrected slide 1 ("the first slice is fucked") + wanted the report-family theme.** Root cause: a CSS rule forced `--paper` bg on every reveal `section` → cream box bled over the dark title. Rebuilt the WHOLE deck on the report palette (#0a0e14 / Fraunces+Space Grotesk+JetBrains Mono / cyan #7dd3fc), removed all per-section bg overrides, locked `--r-background-color`. Re-verified: 12 balanced sections, 12 notes, 0 anomalies, 0 forced section-bg.
- **Niklavs Q: "how does €2.96M arrive from the mart? SCM shows €3.3M for just 7 countries."** Read `sql/population_2026q1.sql` (deterministic scope) → spawned shipping-agent to reconcile live. See completed quest [[S187_85b0fcc3_scm-vs-tender-q1-reconciliation]]. Answer: different population — tender = PCS-PL print-site only + invoiced-only + dim-gated, 18 ctry; SCM = ALL sites (incl. Wolfen photo lab) on COALESCE(real,expected). Dropping the PCS-PL origin filter alone takes the 7-country total €2.80M→€3.24M ≈ Niklavs's €3.3M. €2.96M is the correct scope for the tender deck. Also surfaced: live mart has crept to ~€3.03M net (invoice backfill, +2.3% since build) vs the deck's frozen €2,955,020.

## Decisions made in-flight
- Authoritative routing source = final `routing_stats.json` (rebuilt Jun 9 19:12), NOT the earlier-iteration bank-note splits (UPS 45,654/Hermes 62,299) — final pushed more off UPS (UPS 29,781 kept).
- Deck scope deliberately kept Q1-only; the full-year carrier-overview total (2.875M shipments) intentionally NOT used anywhere.
- Left two figures off the slides (parked in speaker-notes, raise-if-asked): the €430k selection-leaderboard ceiling, and the Maersk-EU oversize-ceiling caveat on ~1,291 DE parcels.

## Cascade.
None — the deck is a new derived artifact in bi-analytics (separate repo); it reads from the reports, nothing in the brain or the tender pipeline depends on it. No docs/ or per-carrier-status cascade triggered.

## Main-brain changes.
Brain-side only: this quest-log + the reconciliation quest + resume + comms OPEN/CLOSING + harvest drafts + cross-conv memory. No `gielinor/` rule/ritual/hook edits.

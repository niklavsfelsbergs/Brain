# S099 d — Doc-sync of EU-tender 2_analysis/docs (dwarf run-log)

**Role:** dwarf (doc-sync operative), inheriting Jebrim.
**Brief:** Sync four EXTERNAL tender docs to the carrier reply-review round source-of-truth (5 `REVIEW_CONCLUSIONS.md` + `CROSS_CARRIER_OVERVIEW.md` + `FUEL_SUMMARY.md` + `FULL_YEAR_SCOPING_NOTE.md`). DECISIONS.md, OPEN_QUESTIONS.md, PLAN.md, REPORT_NOTES.md. Do not commit.
**Base dir:** `C:/Users/niklavs.felsbergs/Documents/GitHub/bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/`
**Source dir (corrected):** source files live one level up, at `2_EU_tender_2026/carrier_responses_to_open_questions/` (NOT under `2_analysis/`).

---

## Source-of-truth facts pulled (2026-05-27 / S099)

5 carriers reviewed: Austrian Post, Hermes, Maersk, DHL Express → deterministic-ready after rebuild; DHL Paket blocked on Bulky ~EUR 2.31M → Round-2.

Locked calls:
- Maersk EU fuel = 6.6% + sensitivity band; oversize cumulative (no change); DE routing-code = 0.
- Hermes gross-weight-only; residential 0.
- DHL Express customs = 0.
- AP no-peak; CH customs EUR 1.00 regardless of ZAZ.
- CH customs distinct legs: Maersk in-base/ZAZ-waived; AP EUR 1.00 regardless-of-ZAZ; DHL Express EUR 0 (no clearance charge). GLS/Güll/DHL-Paket still pending.

Goal reframe: decision basis = full-year cost; Q1 2026 = unit-cost reference. Annualisation method PARKED/deferred (`FULL_YEAR_SCOPING_NOTE.md`).

Cross-carrier still open: volume-tier item (cross-carrier §B.15).

---

## Edits applied (4 files)

1. **DECISIONS.md** — appended two newest-at-top entries: (a) 2026-05-27 carrier reply-review round summary; (b) 2026-05-27 goal-reframe (full-year basis / Q1 reference / annualisation parked). Cited the 5 REVIEW_CONCLUSIONS files + FULL_YEAR_SCOPING_NOTE.
2. **OPEN_QUESTIONS.md** — annotated the cross-carrier ZAZ/CH-customs entry: Maersk + AP + DHL Express legs resolved 2026-05-27; GLS/Güll/DHL-Paket still pending. Annotated the volume-tier item as still open (dated). No deletions.
3. **PLAN.md** — status annotations dated 2026-05-27 on §B.7.c/d (AP), §B.19 (Maersk), §B.22 (Hermes), §B.23 (DHL Express) → reply set in / ready to rebuild. §B.24 (DHL Paket) → HELD pending Round-2.
4. **REPORT_NOTES.md** — appended two Cross-carrier notes: fuel volatility (sensitivity dimension, FUEL_SUMMARY.md) + full-year framing (Q1 unit-cost reference, FULL_YEAR_SCOPING_NOTE.md).

All edits match each file's existing style (append-dated, no history rewrite). NOT committed per brief.

---

## DONE

Verified via `git diff --numstat`: DECISIONS +190/0 (2 entries, pure insert), REPORT_NOTES +6/0 (2 notes, pure insert), OPEN_QUESTIONS 3/3 (in-line ZAZ + volume-tier annotations), PLAN 19/1 (5 §B status annotations). `2026-05-27` marker counts match intent (DECISIONS 3, OPEN_QUESTIONS 2, PLAN 6, REPORT_NOTES 3). Nothing committed.

**Note for principal:** the brief's source path (`../../carrier_responses_to_open_questions/`) was off by one level -- source files actually live at `2_EU_tender_2026/carrier_responses_to_open_questions/` (sibling of `2_analysis/`, not under it). No impact on the task; flagging for the path reference. Also: ASSUMPTIONS.md / NEXT.md / bias_table.md / open_questions/maersk.md showed `M` in the working tree before this run -- pre-existing, not touched by this dwarf.

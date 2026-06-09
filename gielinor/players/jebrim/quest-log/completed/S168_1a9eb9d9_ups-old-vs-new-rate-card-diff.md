# S168 — UPS current-contract vs 2026-offer rate-card diff

**Player:** Jebrim · **Session:** 1a9eb9d9 · **Date:** 2026-06-09
**Thread:** EU tender 2026 → UPS (continuation of S163/S164 Phase-2 work; comparison sub-deliverable).

## Ask
While UPS's answers to the dispatched Round-1 questions are still pending, compare what's directly
comparable now: the **old/current contract rate card** vs the **new 2026 tender offer** — rate cards.

## What happened
- Confirmed task accessible. Located both cards: new offer already extracted to parquet (S163 build);
  current contract at `Documents/Shipping/1. EU/1. PICANOVA/UPS/Picanova UPS Rate Card 2026.xlsm`.
  Baseline chosen (via multiple-choice): **current effective 2026 card** — both 2026-priced → isolates
  the negotiated delta, no GRI drift.
- Verified the old card's workbook layout is **identical** to the new offer (sheet names + row/col
  offsets) before reusing `extract_rates.py` logic — re-validated borrowed constants, didn't assume.
- Built `comparison/compare_rate_cards.py` (bi-analytics repo): diffs Standard (destination-keyed),
  Express/Express Saver (zone-keyed), and DE_ZONES. Wrote `comparison/findings.md` + parquet diffs.

## Decisions / findings
- **Headline: new offer = ~+5% on Standard light (≤2 kg) across nearly all EU lanes** — modest uplift
  on our workhorse product. Carve-outs: **PL −15%** (same zone), **DK + GB flat**.
- Standard heavy bands reshape unevenly (PL +24%, CH −41%, a cluster +1.6%) — small tail.
- **Express/Saver ≈ 97% identical** — premium air not renegotiated.
- **Zones unchanged; Expedited new; WW Economy absent** (tail stays on current contract).
- Fuel/peak/LPS deliberately **not** compared (provisional pending UPS Q1/Q4/Q6).
- Two measurement artifacts caught + corrected (band-mean inversion = real weight signal; DE_ZONES
  fan-out false "PL zone change" → properly keyed = 0 changes). Did not report the false positive.

## Pending external actions
None pending.

## Knowledge saved
- Bank draft: `bank/drafts/notes/projects/2026-06-09-ups-old-vs-new-rate-card-diff.md` (promote at alching).
- Artifact (bi-analytics, separate repo, **uncommitted**): `…/UPS/comparison/{compare_rate_cards.py,findings.md}`.

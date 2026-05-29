# S122 — EU tender: switchable-incumbent treatment + 2 new open questions

**Player:** Jebrim
**Session:** 330dea7d
**Date:** 2026-05-29
**Status:** complete (deliverable shipped)

## Ask

Principal walked through how the EU tender treats **incumbents that also submitted a new offer** — the "switchable" carriers (DHL Paket, Maersk, DPD PL). Then, focused on Maersk: are all currently-operated Maersk countries re-priced on the new offer, or are some not even in it? Closed by documenting two items as open.

## What happened

- **Switchable-incumbent mechanic confirmed** (source: `2_analysis/docs/technical/03-scorer.md`, `_decision_sets.py`). Each switchable holds 3 mutually-exclusive states `{INCUMBENT, NEW_OFFER, OFF}`. The do-nothing baseline re-prices INCUMBENT bids on the **2026 engine card where the engine can price the parcel, else falls back to the 2025 invoice**. One uniform rule for all three — not a per-carrier story. Baseline_2026 €14.85M vs invoice_today €14.27M (+€581k; 2026 cards dearer).
- **Per-carrier reality (principal-supplied):** DHL Paket = pure rate increase, new card live since 03.01 → not a decision lever, fixed cost in every scenario. DPD PL = new offer over-prices its own current parcels (`renew_dpd_pl` standalone −€417k full-year) → keep at invoice *unless* the current contract expires. Maersk = the GB/FR/SE/FI/IE tail.
- **Maersk coverage verified against the rate tables** (not inferred): EU card = 25 countries (`eu_hd_rates.parquet`); ROW = ~150 via FedEx Economy (`row_zones.parquet`). Confirmed empirically that **GB, FR, SE, FI, IE are in neither table** → `country_not_served`. Of the Phase-1 "already-Maersk" set (FR/GB/SE/DK/FI), **only DK is actually on the 2026 card**. So current Maersk lanes on-card re-price to the new offer (~88% of volume, DE the bulk); the off-card tail falls back to 2025 invoice and strands entirely on renewal.
- **Correction in-session:** I first claimed GB routes via the ROW/FedEx-Economy branch (inferred from post-Brexit logic). Principal's follow-up prompted me to check `row_zones.parquet` — GB is absent there too. Claim was wrong; corrected. See harvest.

## Deliverable — 2 open questions documented

Added to `2_analysis/docs/OPEN_QUESTIONS.md` (working repo `bi-analytics-main/NFE/projects/2_EU_tender_2026/`):

1. **Maersk § (after the "Still open" residuals):** "Maersk GB offer — expected 2026-06-02" — GB currently `country_not_served`; a forthcoming offer extends coverage and re-opens the GB lane. Status: awaiting.
2. **DPD PL § (after the "Still open" residuals):** "Will the current DPD PL contract expire (forcing sign-or-drop)?" — if it lapses, the INCUMBENT-at-invoice state disappears and DPD PL collapses to `{NEW_OFFER, OFF}`. Working assumption from this session: assume it expires (parked — not yet wired into `_decision_sets.py`). Status: open.

## Pending external actions

None pending. The two `OPEN_QUESTIONS.md` edits are written to disk in the `bi-analytics-main` repo (a **separate** git repo) but **left uncommitted there** — committing the tender repo is a separate principal action outside the brain close-commit.

## Decisions / carry-forward

- **DPD PL "assume contract expires"** is a parked working assumption, not yet a model change. When unparked: edit `_decision_sets.py` to drop DPD PL's INCUMBENT state (→ `{NEW_OFFER, OFF}`) + add a `DECISIONS.md` entry. Tracked now as the new open question above.
- **Maersk GB offer 2026-06-02** — when it lands, extend the Maersk card coverage and re-score the GB lane.

## Anchor

This session: S122 (sid8 330dea7d). Sibling EU-tender quests: [[S118_f41737e5_eu-tender-decision-scorer-report-regen|S118]], [[S121_2ae1248b_eu-tender-technical-documentation|S121]]. Bank: [[eu_tender_2026]].

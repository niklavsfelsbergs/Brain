---
quest: S209_89e4a123_carrier-overview-v2-rederive
sid8: 89e4a123
ts: 2026-06-11 (late, T2)
open_dep: none — committed 0611bed (re-derive) + a5e3de5 (keep-incumbent sweep); quest complete
---

# carrier_overview_v2 field-wide re-derive — DONE + COMMITTED (0611bed); UPS GRI re-cut done

The last open step of the S208 UPS cascade. UPS tender engine brought into `2_analysis/carrier_overview_v2/` as the 10th new-offer competitor; whole grid + every carrier's relative prose re-derived (S185). Then (T2) re-cut the UPS framing for "current contract going away" + added the GRI lens. Report re-rendered, verify PASS. **bi-analytics COMMITTED `0611bed`** (pathspec carrier_overview_v2/, 27 files; never pushed).

## T2 — the UPS decision reframe (principal-driven)

- "Keep today's UPS" is fiction if the contract is being replaced → signing is the baseline. The carrier_overview "vs today" bar is **GRI-free raw Q1**; the routing/decision report applies UPS's **+5% GRI keep-side-only** (do-nothing).
- **Cost-jump drivers (decomposed from engine components + actuals real_*_eur):** CH +65-78% = the **operative-tier BASE** (€12.01 vs today €7.49; the parked CH/GB finding, revisit trigger = *before signature*, ~€360k/yr). Nordics +27% = higher base + oversize/LPS. FR +4-6% = **basically flat** (base ±€0.15, fuel-timing). Line-haul is a wash (today "truck €0.72" = engine €0.75).
- **GRI'd-forward:** FR slices flip to break-even+; CH/Nordics stay (tier + oversize). Matches findings.md (offer ~6-14% cheaper than GRI'd billing on EU core).
- **Re-cut:** ups.md (one-line, where-it-wins, 5 verdicts, practical-surface, IT Std 2-5, analyst-take/net), EXEC ups one-liner, methodology GRI-free note. Sign the offer; negotiate CH operative tier before signature (or route CH bulky → Güll); dispute the Nordics oversize/LPS.

## Consistency sweep — DONE (commit a5e3de5)

Principal asked to sweep for consistency. Reframed every UPS-today "keep the incumbent" across the other hands (maersk IT Std 2-5 + ROW Bulky 2-5 ×2, fedex FR bulky + analyst-take, dpd_pl Nordics ×2 + header, dhl_paket ROW header + tail + analyst-take) → "real increase on the old UPS rate / route to least-dear / dispute the oversize / per-parcel router", GRI context where it flips. Generic segment-map verdict softened to "GRI-free — see Methodology". Audit: only 4 legit "keep" refs remain (Maersk-FR ×2 + DPD kept contract + the methodology rule). Re-rendered, verify clean.

## Where we are — complete

- **Matrix:** full-year `data/cost_matrix/` regenerated with the `ups` engine (11 carriers, 31.6M rows; additive — existing 10 reprice identically). *Gitignored — not in any commit.* `cost_matrix.py:_ENGINES` already had ups (S208); the on-disk matrix predated it.
- **_data chain:** `competitive_map.py` → `build_summary.py` → `build_hand_cards.py` re-run. `build_actuals.py` untouched (UPS already in the 2026-Q1 "today" overlay). 52 kept segments, grid structure unchanged.
- **Config:** `ups` added to `competitive_map.ALL_CARRIERS` + `build_report.py` CARRIER_LABELS / EXEC / EXEC_ORDER (re-ranked decision-relevant: maersk, dpd_pl_current, dhl_paket, ups, …). UPS badge = **firm** (auto). Not new/held/current.
- **Sections:** 10 carded carriers re-narrated by a **dwarf fan-out** (d1–d10, narrate-off-card) + my gate vs the card/parquet; `dpd_pl_current.md` (cardless) + the EXEC superlatives written by me. Stale engine-version stamps fixed (dhl_paket→2.2.0, hermes→2.2.0, maersk→3.2.0).
- **Render + verify:** `carrier_overview.html` (473 KB) + `exec_brief.html` (23 KB). 11 carrier pages incl. ups; 0 brace/None leak; key numbers match parquet; exec brief 11 rows. `verification/ledger.md` + `phase3_reconciliation.md` updated.

## New canon — winner counts (52 segments)

maersk **15** (#1, was 14) · dpd_pl_current **13** (was 16) · guell **8** (was 10) · dhl_paket **7** · **ups 7 (NEW)** · gls **2** · hermes **0** (was 3) · dhl_express **0** (was 1) · fedex 0-mean/cheapest-6 · austrian_post 0 · dpd_pl 0 (declined).

**The load-bearing UPS finding:** 5 of UPS's 7 wins are **HOLLOW vs today** — the new offer prices above UPS's own current invoiced cost on CH/FR/Nordics bulky; only the two ROW lanes (~0.3% book) genuinely beat today. UPS wins the tender field but loses to the status quo on most of its wins.

## Next concrete step

**Principal commit go** — pathspec-scoped to `NFE/projects/2_EU_tender_2026/2_analysis/carrier_overview_v2/` (27 files: code + sections + cards + 2 HTML + ledger; `data/cost_matrix` gitignored). Never push.

## Open flags (carried, not blocking)

- Engine-version drift surfaced by the regen is legitimate (population unchanged 2,875,235; verified vs git — dhl_paket Warenpost 2.1.0, hermes eligibility tighten, maersk 3.2.0) — but it means the v2 `_data` had been stale since before this session; any other consumer of the v2 grid should re-run.
- The "In the routing" numbers in `dpd_pl_current.md` are from the S208 routing run (UPS now an active renewable there) — flagged in-section as indicative, may shift on a routing re-run.
- Still open from S208/S206 (not this quest): zV-on-UPS routing policy; renew_ups −50.9k wholesale vs +103k selective framing; round-2 batch; additional-services PDF; **Jebrim alch OVERDUE** (15+ examine drafts + a sibling alch mid-promotion in the tree).

## Files to read first

1. this file
2. `verification/ledger.md` → "S209 re-derive" section (the full audit)
3. quest-log `S209_89e4a123_carrier-overview-v2-rederive.md` + the d1–d10 dwarf traces

# [[S033_2026-05-22_shipping-agent-audit|S033]] — D3 restamp dwarf

> **Role:** dwarf (Jebrim namespace)
> **Spawned by:** Niklavs (principal) via [[S033_2026-05-22_shipping-agent-audit|S033]] audit apply-fixes pass
> **Scope:** Re-run coverage-audit probes against gold (`shipping_mart.*`), refresh numbers + stamps in `reference/coverage-audit.md` and the Source-maturity section of `reference/sources.md` in the shipping-agent repo.
> **Started:** 2026-05-22
> **Status:** completed at [[S033_2026-05-22_shipping-agent-audit|S033]] close. No pending external actions.

## Brief

The two LIVE reference files in shipping-agent carry pre-gold-cutover stamps (2026-05-21, silver-era). Gold landed 2026-05-22; mart lives at `shipping_mart.*` accessed via `ship_mart_ro`. Three probes from § Regenerate need rerunning; numbers and stamps then updated surgically.

## Plan

1. Run Probe 1 (coverage by source) via shipping-agent harness.
2. Run Probe 2 (coverage by source × carrier_group, ≥1000).
3. Run Probe 3 (ORWO by month).
4. Run ORWO column-NULL probe (destination_country, revenue, weight).
5. Edit `coverage-audit.md` — stamp + 5 sub-tables/sections.
6. Edit `sources.md` Source-maturity section only — stamp + ORWO row.
7. Summary to principal.

## Actions

- **Probe 1 (coverage by source)** — completed. Identical to silver-era:
  - Picturator 5,005,768 @ 86.7% cost / 99.3% revenue
  - ORWO 2,506,429 @ 68.7% cost / 0.0% revenue
  - PicaAPI 1,192,685 @ 93.9% cost / 99.6% revenue
  - PCS 15,919 @ 68.7% cost / 0.0% revenue (by design)
  - Rewallution 957 @ 97.9% cost / 100.0% revenue

- **Probe 2 (source × carrier_group, ≥1000)** — completed. The four documented holes all still present at the same magnitudes:
  - ORWO POST 567,930 @ 0.4%
  - Picturator MAERSK 97,662 @ 68.9%
  - Picturator ASENDIA 5,832 @ 0.0%
  - Picturator (unresolved) 334,001 @ 44.4% — folds in POST_DVF (170K @ 0% from original extkey-level audit; Probe 2 group-level can't isolate it)

- **Probe 3 (ORWO by month)** — completed. Output identical row-for-row to the existing table 2025-10 → 2026-05.

- **ORWO column-NULL probe** (extra, for sources.md maturity table):
  - destination_country: 100.0% blank
  - net_revenue_eur: 100.0% NULL
  - weight_kg: 47.1% NULL
  - All match the pre-cutover wording. Gold did NOT bring the ORWO wiring online.

- **Edit `coverage-audit.md`** — completed. Surgical edits:
  - Top stamp bumped to 2026-05-22 with gold-via-ship_mart_ro framing.
  - "Pre-cutover numbers" header → "Post-cutover numbers (gold, ..., verified 2026-05-22)"; ORWO note tightened.
  - Mart-wide coverage prose: dropped "Re-verify against gold before quoting" — now verified.
  - Concentrated holes section: re-framed as "(post-cutover, 2026-05-22)" with "all four persist through the gold cutover at the same magnitudes" lede. Each hole re-verified; POST_DVF gets a note that Probe 2 can't surface it directly (extkey-level claim still holds from original audit).
  - ORWO by-month section: "pre-cutover" → "2026-05-22 read"; added "Gold matches silver exactly."
  - Country dimension: ORWO line tightened — now states "re-verified against gold 2026-05-22, source-level NULL probe" and drops the "Re-verify" hedge.

- **Edit `sources.md` Source-maturity section** — completed (one collision with concurrent D4 write to the file; resolved by re-reading and retrying my Edit — D4 was working in a different section).
  - Stamp 2026-05-21 → 2026-05-22 with "gold cutover live; ORWO destination_country and revenue_eur both still 100% NULL post-cutover — the wiring did not land in gold."
  - ORWO row: kept the same structure, refined wording — "100% blank in gold (re-verified 2026-05-22; wiring still pending)" / "100% NULL in gold (intended-populated work has not yet landed)" / "47% NULL" → "47% NULL (re-verified 2026-05-22)".

## What shifted vs silver — for the principal

**Nothing material.** Gold inherited the upstream wiring unchanged. Same row counts, same coverage percentages, same holes at the same magnitudes, same ORWO column-NULL pattern. The cutover is a packaging/access change (mart now at `shipping_mart.*` via `ship_mart_ro`), not a content change. The ORWO destination_country/revenue work that was "in progress" pre-cutover did **not** land — those columns are still 100% NULL/blank.

## Status

D3 task complete. Returning summary to principal.

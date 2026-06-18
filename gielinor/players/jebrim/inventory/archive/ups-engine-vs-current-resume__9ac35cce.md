---
quest: S213_ups-engine-vs-current-cost
sid8: 9ac35cce
ts: 2026-06-11 23:30
open_dep: none
---

# UPS engine cost vs current cost — investigation DONE

**Status:** done. Consultation/investigation; questions answered, corrected finding written to bank draft. No bi-analytics writes.

## Where we are

Settled how the 2026-offer UPS engine cost compares to current invoiced cost (ex-LPS/OML), per-country and by component. **Corrected** an early-session error (premium-air-priced the WW-ECO tail) after Niklavs caught it: scored on `go_forward_eur`, the offer is ~break-even vs GRI'd today (+2.9% offer-served book), and −7.8% once CH+GB are stripped. Savings origin ≈ 73% base / 19% residential / fuel neutral. Full writeup: [[2026-06-11-ups-engine-vs-current-cost-corrected]].

## Next concrete step

None required — investigation closed. Carried for Niklavs (not actions for the agent):
1. **CH + GB operative-tier base** — negotiate before signature or route away (the whole residual cost gap; pure base-rate problem). Connects to the parked CH/GB items in `ups-cascade-resume__9399f067`.
2. US/AU/CA + WW-ECO tail — no ask; stay on current by the `WW-ECO-stays` rule.

## Files / paths to read first

1. this file
2. bank draft `bank/drafts/notes/projects/2026-06-11-ups-engine-vs-current-cost-corrected.md` (the corrected finding + the go_forward method note)
3. quest-log `S213_9ac35cce_ups-engine-vs-current-cost.md` (turn log incl. the correction)
4. source: `1_offers/picanova/UPS/calculation/output/replay.parquet` (cols: `go_forward_eur`, `stays_current`, `ups_*_eur`, `real_*_eur`)

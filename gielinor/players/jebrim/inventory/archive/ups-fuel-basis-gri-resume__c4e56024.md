---
quest: S171_ups-fuel-basis-and-gri-sensitivity
sid8: c4e56024
ts: 2026-06-09 14:45
open_dep: bi-analytics engine refit UNCOMMITTED (separate-repo principal gate); volume-weighted old-vs-new base-rate replay not yet run
---

# Resume — UPS fuel basis + GRI sensitivity (S171)

**Status:** in-progress.

**Where we are:** Fuel basis is RESOLVED — the card's "35 Percent Off" is a 35% discount off UPS's
floating index, confirmed by invoice reconciliation at ~19.8% effective (road). Engine refit to
`FUEL_PCT=0.20` landed (Q1 calc −€180k, gap to actual halved). GRI sensitivity done: offer ≈ "current +
one GRI" on core lanes, with PL/DK/GB as wins. Knowledge saved to the S168 bank draft.

**Next concrete step:** Two open items, in priority order:
1. **Commit the bi-analytics engine refit** — `UPS/calculation/engine.py` + `README.md` are edited but
   UNCOMMITTED (separate repo, on main). Needs an explicit principal commit + push go.
2. **Volume-weighted old-vs-new base-rate replay** (the original S168 next-step, still not run): price
   2026-Q1 actuals through the *old* card, diff vs the new-card replay. Fuel/peak/LPS identical both
   sides → delta is clean of placeholders → a defensible *relative* €/yr number. Converts "~5% on the
   card" into "€X/yr on our mix." Offered to Niklavs; he wound down before a go.

**Files to read first:**
- `players/jebrim/bank/drafts/notes/projects/2026-06-09-ups-old-vs-new-rate-card-diff.md` (the synthesis — Fuel + GRI sections)
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/1_offers/picanova/UPS/calculation/engine.py` (FUEL_PCT=0.20, refit)
- `bi-analytics-main/NFE/projects/.../UPS/comparison/findings.md` (the base-rate diff)
- quest-log `S168_1a9eb9d9_ups-fuel-effective-rate-reconciliation.md` (the shipping-agent reconciliation trace + SQL)

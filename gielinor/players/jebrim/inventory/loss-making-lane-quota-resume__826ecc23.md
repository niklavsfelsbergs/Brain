---
quest: S229_loss-making-lane-quota
sid8: 826ecc23
ts: 2026-06-12 14:10
open_dep: principal decisions on closure scope + optional deeper cuts (CH, US posters/tubes, DB Schenker continental)
---

# Resume — loss-making-lane quota scan (NFE topic 47)

**Status:** in-progress (deliverable shipped; follow-ups open).

**Where we are:** NFE `shipping_topics/47_loss_making_lane_quota/` built and reproducible —
findings.md, both-grain SQL, build_data.py, make_excel.py, parquets, and the 3-sheet Excel
(`outputs/loss_making_lanes_2026_invoiced.xlsx`). Canonical cut = **2026 + invoiced-only**.
Live loss-makers: CH+DB Schenker 157%; US+FedEx "21" Tube" 119% (2,474 ships, 98% inv);
DB Schenker cut-to-size class (CH/ES/NL); DB Schenker continental cluster 60–75% (FR biggest
€79k). bi-analytics-main **not yet committed**.

**Next concrete step (blocked on Niklavs' calls):**
1. Closure scope — CH+DB Schenker only, DB Schenker oversized/cut-to-size as a class, or a
   full DB Schenker continental carrier review (incl. FR/IT)?
2. US posters/tubes — re-price, re-route off FedEx/UPS, or raise product price? FedEx 21"
   Tube is the highest-confidence target.
3. €0-revenue shipments — keep in (cost reality) or strip out (clean pricing view)?
4. Commit bi-analytics-main topic-47 folder? (separate repo — needs explicit go.)

**Optional deeper cuts offered, not yet run:**
- DB Schenker continental cluster packagetype breakdown (is it all cut-to-size/oversized?).
- US FedEx "21" Tube" cost-bucket decomposition (what drives 119%).
- Whether CH+DB Schenker is itself seasonal or steady through 2026.
- Record the final 2026+invoiced cut + Excel into findings.md (mostly done; verify prose).

**Files to read first:**
- `bi-analytics-main/NFE/shipping_topics/47_loss_making_lane_quota/findings.md`
- `.../47_.../sql/` (both grains + the 3 excel_s*.sql) and `make_excel.py`
- quest-log: `S229_826ecc23_loss-making-lane-quota.md` + the Wolfen sub-trace
- `players/jebrim/examine/drafts/2026-06-12-current-period-invoiced-floor-for-bad-segment-scans.md`

---
quest: S211_ups-savings-dbschenker-reroute-investigation
sid8: dcd18cfd
ts: 2026-06-11 21:30
open_dep: none
---

# UPS savings + DB-Schenker zV→UPS reroute — investigation DONE

**Status:** done. Consultation/investigation; questions answered, finding written to bank draft. No bi-analytics writes.

## Where we are

Settled the full chain from "how did UPS change savings" down to per-parcel zV→UPS economics. Headline: UPS engine raised annual saving €1,442,782 → €1,908,707 (+€465,925, clean q09 basis). The DB-Schenker→UPS zV reroute is real and robust (~€38/parcel saving; break-even LPS incidence ≈58%); the tender does NOT overstate the DBS baseline (the €48-mart-vs-€66.65-tender "gap" is an all-zV-blend vs expensive-moved-subset population artifact). Full writeup: [[2026-06-11-zv-dbschenker-ups-reroute-economics]].

## Next concrete step

None required — investigation closed. Optional follow-ups offered but not accepted:
1. Quantify the full-year book impact of the zV→UPS slice at 26.7% vs 50% LPS incidence (cost-matrix join).
2. The zV-on-UPS routing **policy** decision is Niklavs' (accept vs exclude the 1,062 zV ≈41% of the DBS→UPS move) — already carried in `ups-cascade-resume__9399f067` open flags; not duplicated as an action here.

## Files / paths to read first

1. this file
2. bank draft `bank/drafts/notes/projects/2026-06-11-zv-dbschenker-ups-reroute-economics.md` (the settled finding + verify-against paths)
3. quest-log `S211_dcd18cfd_ups-savings-dbschenker-reroute-investigation.md` (turn log)
4. pre-UPS report snapshot: `~/Documents/eu-tender-pre-ups-snapshot-98cdd49/` (pre-q09 basis — flag when reading)

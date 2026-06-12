---
quest: S233_guell-linehaul-density-correction
sid8: 14a9b5f3
ts: 2026-06-12 16:01
open_dep: logistics-manager inbound-sprinter fill/consolidation answer (Niklavs owns); bi-analytics commit pending principal (their go)
---

# Resume — Güll line-haul density correction

**Status:** in-progress (deliverable shipped this session; thread parked on the logistics conversation)

**Where we are:** Grounded the Güll line-haul density against the mart (S231/S232): the flat 150 parcels/pallet was ~2–3× the observed Szczecin packing (~52). Split the engine constant into inbound 52 / outbound 75/lane, regenerated cost matrix + stats + report. Güll's net marginal collapsed from +€163,097 to **+€520/yr** (wins 308 CH parcels). Report HTML reframed to "Güll evaluated → not competitive." All bi-analytics changes **uncommitted** (their go).

**Next concrete step — blocked on Niklavs:** the logistics-manager conversation. The one lever that could revive Güll is the **inbound sprinter**: is the €955 Szczecin→Lindau truck Picanova-only, or shared with other customers (→ our per-parcel share drops below the €2.30 a Picanova-only 52/pallet implies)? Also: does the sprinter fill on space (8 pallets) or weight (1,000 kg) first? If the inbound economics change materially, re-run the engine with a lower inbound allocation and re-evaluate. Otherwise Güll stays parked on cost.

**Open for principal:** (1) the bi-analytics commit (their go). (2) Austrian Post carries the same unvalidated 150 — correct it too if AP is still live in the tender (separate task, not started).

**Files to read first (next session):**
- This session's quest-log: `quest-log/in-progress/S233_14a9b5f3_guell-linehaul-density-correction.md`.
- `bank/drafts/notes/projects/2026-06-12-guell-no-hermes-marginal-and-density-gate.md` — density-gate writeup, now updated with the grounded finding.
- bi-analytics: `carriers/guell/constants.py` (the three split density constants), `final_report_no_hermes_with_gull/{build_stats,report}_no_hermes_with_gull.py`.
- The two mart-pull traces: `quest-log/in-progress/S231_shipagent_*.md`, `S232_shipagent_*.md`.

**Locked calls:** densities inbound 52 / outbound 75/lane (Niklavs-endorsed via multiple-choice). Güll: do not add on current economics. bi-analytics uncommitted (their go).

---
quest: S245_eu-tender-no-hermes-routing-ops-coherence
sid8: 3172630e
ts: 2026-06-16 01:00
open_dep: none (deliverables shipped+committed; only parked Q15/Güll remain)
---

# Resume — EU tender no-Hermes routing OPS-coherence + operational report

**Status:** in-progress — core deliverables shipped+committed; only parked follow-ups remain.

**Where we are:** No-Hermes routing is operationally coherent (serve-aware smoother in `build_final.py`,
no_hermes path only; 99.4% clean / 0 gaps / 0 flips; ~€39k/yr cost accepted) — bi-analytics `8b83ce9`.
The operational dispatch report (`routing_report_ops_no_hermes.py`) was reviewed, a service-rendering bug
fixed (it treated per-parcel size-driven product splits as fake weight ranges → now shows a weight cutoff
only where products genuinely split by weight, else volume shares), and committed `11fc677`. Also verified
the ~0.155% dimension-DQ parcels change **zero** routing decisions — cosmetic only; flagged as Q16 for the
data team, not patched here.

**Next concrete steps (all parked, none blocking):**
1. **Q15:** smoothing floor 5% vs 10% — pending an ops preference (fewer carrier breaks?).
2. **Q16:** upstream mart dimension DQ (~826 parcels) — data-team fix, not routing work.
3. *(separate thread)* Güll density gate — parcels-per-pallet (150/pallet); see
   `inventory/eu-tender-no-hermes-with-gull-resume__b94d4675.md`.
4. *(optional)* mirror the report's service-sliver suppression into the downloadable `routing_rules.csv`
   so the CSV matches the report — cosmetic, low value, skip unless asked.

**Files to read first:**
- `bi-analytics-main/.../2_analysis/routing_investigation/ops_coherence/findings.md` — full writeup (triage, cross-country pivot, the €39k cost split).
- `bi-analytics-main/.../2_analysis/routing/build_final.py` — `smooth_routing()` + the no_hermes path.
- `bi-analytics-main/.../2_analysis/routing/no_hermes/routing_report_ops_no_hermes.py` — the operational report renderer (uncommitted).
- `bi-analytics-main/.../2_analysis/docs/DECISIONS.md` (2026-06-15 entry) + `OPEN_QUESTIONS.md` (Q15).

**Note:** bi-analytics `routing_rules.csv` / parquets are gitignored — rebuild via `python routing/build_final.py no_hermes`.

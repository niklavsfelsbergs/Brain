---
quest: S245_eu-tender-no-hermes-routing-ops-coherence
sid8: 3172630e
ts: 2026-06-16 00:00
open_dep: ops report renderer awaiting principal eyeball + bi-analytics commit
---

# Resume — EU tender no-Hermes routing OPS-coherence + operational report

**Status:** in-progress (smoothing shipped+committed; operational report built, awaiting eyeball)

**Where we are:** No-Hermes routing is now operationally coherent — serve-aware smoother baked into
`build_final.py` (no_hermes path only), regenerated table 99.4% clean / 0 gaps / 0 flips, cost ~€39k/yr
accepted. Committed to bi-analytics `8b83ce9`. The operational HTML dispatch report is built and verified
but the renderer is **uncommitted** and the principal hasn't eyeballed the HTML yet.

**Next concrete steps:**
1. **Principal eyeballs `routing/no_hermes/routing_report_ops_no_hermes.html`** — then decide adjustments
   (column order, country-grouped sections vs flat filterable table, show €/parcel?, wording). Open with
   `start ...routing_report_ops_no_hermes.html`.
2. **Commit the ops renderer** to bi-analytics once approved: `routing/no_hermes/routing_report_ops_no_hermes.py`
   (the `.html` is gitignored — regenerates from the .py). Explicit pathspec; NFE standing auth; never push.
3. **Q15 (OPEN_QUESTIONS):** floor 5% vs 10% — parked pending an ops preference (fewer carrier breaks?). Not blocking.
4. *(separate thread)* Güll density gate — parcels-per-pallet estimation (150/pallet) firms Güll's marginal;
   see `inventory/eu-tender-no-hermes-with-gull-resume__b94d4675.md`.

**Files to read first:**
- `bi-analytics-main/.../2_analysis/routing_investigation/ops_coherence/findings.md` — full writeup (triage, cross-country pivot, the €39k cost split).
- `bi-analytics-main/.../2_analysis/routing/build_final.py` — `smooth_routing()` + the no_hermes path.
- `bi-analytics-main/.../2_analysis/routing/no_hermes/routing_report_ops_no_hermes.py` — the operational report renderer (uncommitted).
- `bi-analytics-main/.../2_analysis/docs/DECISIONS.md` (2026-06-15 entry) + `OPEN_QUESTIONS.md` (Q15).

**Note:** bi-analytics `routing_rules.csv` / parquets are gitignored — rebuild via `python routing/build_final.py no_hermes`.

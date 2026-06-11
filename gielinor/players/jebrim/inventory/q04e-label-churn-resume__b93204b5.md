---
quest: S197_q04e-label-churn-deep-dive
sid8: b93204b5
ts: 2026-06-11 12:40
open_dep: principal review of q04e findings (CONCLUSION block) + bi-analytics commit decision for the q04e files
---

# Resume — q04e packagetype label-churn deep dive

**Status:** in-progress (deliverable shipped, awaiting review).

**Where we are:** `q04e_label_churn_deep_dive_findings.md` + `q04e_label_churn_deep_dive.py` written into bi-analytics `2_analysis/result_investigation/` (UNCOMMITTED there, principal-gated). Verdicts: WICKEL 80x60 family → ORWO_80x60 = relabel-equivalent, fold (carrier-side swap Mon 2026-02-23); STANZ 120x90→120x80 = real size change crossing the Maersk ≤300 L+girth ceiling AND the Jan 28 "switch" is a reversion (S80 the 2-year incumbent, Dec–Jan S90 surge = the anomaly) — re-weight, don't fold. No other churn pairs; GEL's Q1-tail "death" = invoiced-only artifact.

**Next concrete step:** blocked on you — review the findings note and record the CONCLUSION block; decide whether the q04e files join the next bi-analytics commit. Open analytical threads if you want them chased: (a) where the heavy strapped multi-item parcels went post-cutover (no heavy tail in ORWO); (b) the Dec–Jan STANZ inversion — baseline or exception for cost attribution; (c) the May-12 resurrected plain WICKEL 80x60 on a new 90.3×60.5×9.0 box (~500/mo, missed by Q1-frozen label sets).

**Files / paths to read first:**
- bi-analytics `NFE/projects/2_EU_tender_2026/2_analysis/result_investigation/q04e_label_churn_deep_dive_findings.md`
- `players/jebrim/quest-log/in-progress/S197_b93204b5_q04e-label-churn-deep-dive.md`
- sibling context: `q04d_stale_today_exposure_scan_findings.md` (the trigger) + result_investigation/README.md (q04e row left to session 5733cb1d)

**Pending drafts:** none (harvest written to disk this close).

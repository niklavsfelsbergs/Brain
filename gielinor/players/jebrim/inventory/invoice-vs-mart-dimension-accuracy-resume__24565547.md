---
quest: S173_invoice-vs-mart-dimension-accuracy
sid8: 24565547
ts: 2026-06-09 15:10
open_dep: none
---

# Resume — package-dimension accuracy (topic 45)

**Status:** in-progress (deliverable shipped; follow-ups optional, none blocking)

**Where we are:** Built `bi-analytics-main/NFE/shipping_topics/45_invoice_vs_mart_dimension_accuracy/` (CLAUDE.md + sql/ + dark-themed `package_dim_accuracy_overview.html`). Established which carriers independently *measure* dims vs reprint our declared dims; PCS-PL independent measurement ≈ Yodel only; Yodel shows systematic under-declaration on the longest axis driven by strapped/wrapped multipacks. bi-analytics is uncommitted (separate repo, principal-gated).

**Next concrete step (all optional — pick on principal cue):**
1. **Apply the coverage-note corrections** to `bank/drafts/notes/projects/2026-06-09-carrier-invoice-dimension-coverage.md` — demote Maersk (passthrough), DB Schenker + Direct Link (volume-only) out of "real measured dimensions"; fix the Yodel "full coverage" → 6.9%. Proposed but not yet approved.
2. **Size the € exposure** of under-declared strapped/wrapped multipacks on the ~86k measurable Yodel parcels (does it correlate with oversize surcharges billed?).
3. **Raise the 22.5cm fallback-floor** declared-dim default with the declaration-pipeline owner.

**Separate parked question (future session, system-scope → likely Guthix):** "What should we pull out of the NFE CLAUDE setup now that we have the brain system?" — review `NFE/CLAUDE.md` + `.claude/reference/*` (report-patterns, house-style) for conventions now redundant with the brain. Niklavs will raise it himself.

**Files to read first:**
- `bi-analytics-main/NFE/shipping_topics/45_invoice_vs_mart_dimension_accuracy/CLAUDE.md` (full tables + verdicts)
- This session's quest: `quest-log/in-progress/S173_24565547_invoice-vs-mart-dimension-accuracy.md`
- `bank/drafts/notes/projects/2026-06-09-carrier-invoice-dimension-coverage.md` (S167 coverage map — the corrections target)
- `bank/drafts/notes/projects/2026-06-09-carrier-measured-vs-passthrough-dims.md` (this session's verdict harvest)

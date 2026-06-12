# S234 — EU tender presented; pin the canonical report artifact

**Player:** Jebrim
**sid8:** 976b6908
**Opened:** 2026-06-12 ~15:30
**Status:** complete (pin landed + committed; no open dep)

## What happened

Niklavs cued that the EU tender just got presented (`<fkyea>`). I opened in celebration/next-steps mode but grounded off the **stale** `final_report/` and quoted its old base €420k / oversize-module €577k split as the headline. He corrected: *"how do you not know the final saving was 976k? just the firm one."*

Verified ground truth: the canonical/presented artifact is `2_analysis/final_report_no_hermes_v2/` (`report_no_hermes_v2.html` + `deck_no_hermes_v2.html`), a standalone management "Carrier Recommendation". Its firm headline = **five-carrier base portfolio €976,024/yr** (`final_stats.json` → `structure.base_ann`; no Hermes, DBS pinned to freight). The gated Hermes+DBS module (€932,683/yr) is stripped from the presented version. `final_report/` + the old €420k/€577k split are superseded.

## Decision

Pin a `CANONICAL PRESENTED REPORT = final_report_no_hermes_v2/` pointer into `bank/domains/eu-tender.md` (the force-loaded eu-tender digest) so any future session lands on v2 and answers "976k firm" without re-deriving from the wrong folder. This is the "always known" surface the principal asked for.

## Done

- `bank/domains/eu-tender.md` — added the canonical-artifact pointer at the head of the Current-state section, marked `final_report/` + the €420k/€577k split SUPERSEDED, cross-linked [[S221_eec4ee99_eu-tender-report-review-qa|S221]] (standalone reframe) + [[S222_3309c3da_eu-tender-no-hermes-v2-headline-reconciliation|S222]] (headline reconciliation).
- Harvest: reinforced examine draft `2026-06-12-which-variant-anchor-to-most-recent-active.md` with this session as a costlier second occurrence (grounding off the wrong variant, not just building it) → promote on next alch.

## Pending external actions

None pending. (No bi-analytics writes — read-only verified `final_report_no_hermes_v2/` + the €976,024 `structure.base_ann`.)

## Cascade

None — single brain-namespace pin, no sibling consumers to sync.

## Main-brain changes

`bank/domains/eu-tender.md` digest pin; one examine-draft reinforcement.

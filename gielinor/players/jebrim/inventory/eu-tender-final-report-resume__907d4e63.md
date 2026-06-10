---
quest: S194_eu-tender-holdup-pass-and-project-rating
sid8: 907d4e63
ts: 2026-06-11 00:40
open_dep: bi-analytics final_report/ uncommitted — awaiting principal review + commit go (separate repo, never push)
---

# Resume — EU-tender final presentation document

## Where we are
- Hold-up pass DONE (3 dwarves): numbers tie exactly on HEAD a96e449; six-item cleanup list delivered in chat
  (stale €377k management_briefing is the risky artifact; A5 scorer floor / bias_table / Maersk ROW demand still open;
  2 unknown test reds: austrian_post f3 crash + hermes f3 forced-mode; docs/NEXT.md + OPEN_QUESTIONS two eras behind).
- FINAL REPORT BUILT + VERIFIED: bi-analytics `2_analysis/final_report/` — build_final_stats.py → final_stats.json →
  final_report.py → final_report.html (+ verify_report.py, PASS). Single-page HTML, family dark theme.
- **HEADLINE RESTRUCTURED (2026-06-11, principal direction "huge change of narrative"):** primary cut = decision
  structure: **Base portfolio €420,218/yr (2.9%, 5 carriers, no Hermes, DBS-origin pinned to freight — true no-module
  counterfactual run inside build_final_stats)** + **Oversize module €577,502/yr (= reroute €525,360 + Hermes
  other-lanes uplift €52,142; Hermes + reroute presented as ONE decision gated on the dims check)**. The old
  "committed €472,360 (firm)" aggregate is retired from display (verify_report documents this); the three-tier
  confidence split (Confirmed €176,250 / Offer-based €296,110 / Conditional €525,360) stays as the secondary cut.
- Hardcoded prose claims (not from stats): DPD new offer "≈19% more expensive" (S170 +18.8%), UPS migration "~62%"
  (verified 61.5% in verify_report.py), "200+ rate checks" (D3 counted 215+), "10 carriers assessed".

## Hermes dependency (post-close addition, 2026-06-11)
86% of Hermes' value (€478,669 of €558,039/yr vs today) is DBS-origin; ex-DBS €79,370/yr on ~8.3k parcels — not
slot-worthy alone. Report now sequences the DBS dims check as PREREQUISITE for the Hermes signature (asks #2 vs #4;
warn callout in §02). Companion scripts: final_report/{hermes_counterfactual,hermes_by_packagetype}.py. The dims
branch logic: as-recorded → Hermes earns slot; smaller → saving re-homes to DHL/Maersk; larger → stays freight;
ops-no → stays freight. Three of four branches end without Hermes.

## Next concrete step
1. Niklavs reviews final_report.html in browser (visual NOT eyeballed by me — data layer verified). Expect tier-name
   and prose iteration rounds.
2. On his go: commit bi-analytics `git commit -- NFE/projects/2_EU_tender_2026/2_analysis/final_report` (pathspec only,
   never push). Note annual_2026/ + UPS fuel fix + UPS comparison/ also still await commit go.
3. LATER (his stated plan): turn the HTML into a slide deck; retire/supersede the stale management_briefing/ then.

## Files to read first
- bi-analytics `2_analysis/final_report/{build_final_stats.py, final_report.py, final_stats.json, verify_report.py}`
- `quest-log/in-progress/S194_907d4e63_eu-tender-holdup-pass-and-project-rating.md` (+ d1/d2/d3 sibling logs)
- digest `bank/domains/eu-tender.md` (3.2.0/2.2.0 state)

## Watch-outs
- bi-analytics SEPARATE repo, principal-gated commits, never push. final_report/ + annual_2026/ + management_briefing/
  all untracked.
- The old management_briefing/ deck still sells €377k as current — superseded by this report; do not present it.
- Tier names are first-draft audience-friendly (Confirmed / Offer-based / Conditional) — principal may rename.

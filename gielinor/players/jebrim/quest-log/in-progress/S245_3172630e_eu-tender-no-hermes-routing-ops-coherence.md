# S245 · EU tender — no-Hermes routing OPS-coherence + operational report

**Player:** Jebrim · **sid8:** 3172630e · **2026-06-16**
**Domain:** [[eu-tender]] · continues the no-Hermes routing thread ([[S212_177f00f1_eu-tender-no-hermes-report|S212]]/[[S226_da65054b_eu-tender-routing-report-no-hermes|S226]]/[[S230_b94d4675_eu-tender-no-hermes-with-gull-report|S230]]).

## Ask

Sanity-check the no-Hermes routing rules — do they make OPS sense? Flag the nonsense
(non-monotone carrier/weight assignments — DHL 0-5kg / UPS 5-6kg / DHL 6+kg shape) and
decide what to do at scale. Then: put together an HTML final routing report for the scenario.

## What happened

- **Diagnosed the rule table.** `routing/no_hermes/routing_rules.csv` (1,799 cell rules) carried
  86 carrier flip-flop lanes, 515 weight gaps, single-parcel slivers — the cheapest-per-cell
  optimizer has no operational-coherence constraint.
- **Built the triage classifier** (`routing_investigation/ops_coherence/triage_routing_rules.py`)
  on the *monotone-step-function* definition: a lane makes sense if carrier-vs-weight is monotone
  with supported breakpoints; a carrier that RETURNS is the defect. Result: the 86 flip-flops were
  structural NOISE — collapse to ~1-3 genuinely-ambiguous lanes (essentially `STANZVERPACKUNG
  120x80`, where UPS/DPD are near-tied). 957 lanes → ~96% single-carrier at carrier level.
- **Cross-country oracle** (`cross_country_pivot.csv`) confirmed the near-tie read: clean-winner
  countries (AT→Maersk, CH→UPS, NL→DPD) are steady; only near-tie countries flicker.
- **Cost check.** Standalone estimate said ~€6k/yr; the AUTHORITATIVE figure from the real build
  is **~€38.8k/yr** (the estimate under-counted can't-serve folds). Split: noise-folding ~€35.5k,
  tie-collapse ~€3.3k. Floor is non-monotone (2% → €50k), so 5% stands.
- **Baked the smoother into `build_final.py`** — `smooth_routing()` + `smooth=` param, enabled on
  the `no_hermes` CLI path only. Serve-aware fold (never strand a parcel), gap-bridge, collapse ties
  (STANZ→UPS). DB Schenker pinned. OFF by default → headline 6-carrier plan byte-unchanged (verified).
  Regenerated table: 99.4% clean, 0 gaps, 0 flips.
- **Built the operational HTML report** (`routing/no_hermes/routing_report_ops_no_hermes.py` →
  `.html`): carrier-primary dispatch list, service as the load-bearing column, open-ended top band
  ("X kg +"), single-carrier lanes as "all weights", by-dimensions section for variable packagetypes.
  Sibling of the audit/cell-grid `routing_report_no_hermes.html`. 1,000 dispatch rows, 96% single-carrier.

## Decisions (principal, 2026-06-15/16)

- Smooth the no-Hermes routing; **accept full clean at ~€39k/yr** (over cost-capped / document-only).
- `STANZVERPACKUNG 120x80` → **UPS**. Floor **5%** (Q15 parks 10% pending ops preference).
- Report shape: carrier-primary, **service is the critical column for ops**; open-ended top band; by-dims separate. Audience: ops + principal.

## Cascade

- `bi-analytics-main` (separate repo): committed **`8b83ce9`** — smoother + investigation + docs
  (DECISIONS 2026-06-15, OPEN_QUESTIONS Q15). Operational report renderer built but **uncommitted**
  (awaiting principal eyeball). `routing_rules.csv` + parquets are gitignored (regenerate from code).
- EU-tender docs updated in the same commit (DECISIONS, OPEN_QUESTIONS) — domain doc-sync honoured.

## Main-brain changes

- None to `gielinor/` content beyond this close (quest-log + inventory resume + one examine draft).
  All substantive work landed in `bi-analytics-main/NFE/projects/2_EU_tender_2026/`.

## Pending external actions

None pending. (bi-analytics `8b83ce9` committed; ops renderer commit is a next-session item, not a dangling pending.)

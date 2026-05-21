---
name: publish-aggregates-only-after-disprove-pass
description: Aggregate stats over heterogeneous populations are provisional until one disprove-pass has been run; don't publish them as classifications until then
metadata:
  type: examine
---

# Publish aggregates only after a disprove-pass

**The pattern.** When I summarize a population with a single statistic (X% of Y has property Z), the statistic is at risk of hiding a population mix. If Y is heterogeneous along an obvious axis (time, source, sub-dim, carrier, leaf), the headline number may blend regimes that should be classified separately.

**The rule.** Before treating an aggregate as a classification, run one disprove-pass: decompose by the most obvious axis and see whether the rate splits. If it splits, the aggregate was hiding ≥2 regimes — the classification belongs at the post-split level, not the aggregate level. Only after the disprove-pass survives can I publish the aggregate as a finding.

**The why.** Aggregate-as-classification compounds. Once a misclassification ("PICT 34% NULL → anomaly?") enters a reference doc, downstream readers cite it without rerunning the decomposition. The audit cost of the wrong aggregate is much higher than the inspection cost of the disprove-pass.

## Observation

S014, 2026-05-21. I had already encoded a NULL-classification working set at T11 ("Picturator ~34%, PicaAPI ~78% carrier-ts NULL — open investigation") and was about to publish it as §9 of the TTYD how-to. The principal pushed back — "this is an easy check we can do right now. Take a look — what is actually missing? Based on source and month."

Three probe rounds, three reframings:

1. **Probe by source × month.** The "PicaAPI 78%" was a regime-change average (carrier-ts ingestion landed 2025-11); not an anomaly. PCS + Rewallution were silently 100% NULL alongside ORWO; T11's NULL classification had missed them entirely.
2. **Probe by dim group.** The "PICT 34% degraded Sep 2025" was wrong — only DHL and UPS groups, not PICT-wide. All other carriers stayed clean.
3. **Probe by extkey.** The "DHL + UPS broke" was wrong — workhorse extkeys (DHLPKT, UPS04STD) stayed clean; specific new extkey variants (bare DHL, bare UPS, DHLWPINT, DHL54PREMIUM, DHLWPKT, UPSWWE) were never wired.

Each layer disproved the previous framing. The §9 that landed is actionable at the extkey level. The §9 I was about to publish before the principal's nudge would have been an aggregate-as-classification — misleading for any reader doing actual transit-time analysis, and downstream-encoded in §4's NULL classification too.

## How to apply

When I'm about to publish a single number as a classification or a finding:

- Ask: *what's the obvious axis along which this population might split?* (Time, source, dim, leaf.)
- Run the decomposition. One query, one pass.
- If the rate splits, restate the classification at the post-split level. If it stays uniform, the aggregate survives.
- The disprove-pass is cheap (one SQL, two minutes); the cost of skipping it is downstream encoding of wrong classifications that propagate.

Pair with [[mart-null-classification-by-drill-down]] — the skill that operationalizes this for mart NULL audits. The skill is the *how*; this examine draft is the *why* and the trigger condition.

## Scope

Jebrim only. Per principal's call at T23: "Jebrim is the analyst." The discipline is methodology-of-analytical-work, which lives with the analyst character, not the global agent identity.

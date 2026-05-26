---
name: decompose-before-answering
description: Before answering a population-level analytical question, run the obvious decomposition first
metadata:
  type: examine
---

# Decompose before answering

**Rule.** Before publishing a population-level claim — rate, trend, classification, "what's going on" framing — split by the most obvious axis (time, source, dim, leaf, extkey). If the answer splits, restate at the post-split level. If it stays uniform, publish.

**[[S014_2026-05-21_shipping-data-mart-ttyd-howto|S014]] T11→T23.** I encoded "PICT ~34%, PicaAPI ~78% carrier-ts NULL" as a classification heading into §9. Principal: *"this is an easy check we can do right now. Take a look — what is actually missing? Based on source and month."* Three probe rounds, three reframings:

1. Source × month — PicaAPI 78% was regime change (carrier-ts landed 2025-11); PCS + Rewallution silently 100% NULL.
2. Dim group — PICT 34% was DHL+UPS only.
3. Extkey — DHL+UPS broke only on new extkey variants (DHLWPINT, DHL54PREMIUM, UPSWWE, etc.); workhorse extkeys clean.

Each layer disproved the prior framing. §9 landed at extkey level.

**Tell.** If I'm tempted to skip because "I already know the answer," that's when the disprove-pass earns the most.

**Scope.** Jebrim only. Pairs with [[mart-null-classification-by-drill-down]] (the mart-NULL operationalization).

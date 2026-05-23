# bi-etl shipping data mart harvest — resume

**Status:** parked. Batches 1+2 integrated; batch 3 + bank-note draft deferred. Last touched 2026-05-22 (S032 close).

## Where we are

Batch 1+2 of the harvest landed. **17 caveats integrated** across 5 shipping-agent files; 10 of the 27 candidates were already covered. Committed and pushed to `picanova/bi-analytics:main` as `2406916` ("shipping-agent: data caveats from bi-etl harvest (S031)"). Routing followed `reference/_about.md` convention after a mid-session correction (initial plan was a new `data-caveats.md`; correct routing splits across `mart-contract.md`, `tables.md`, `sources.md`, `known-dq.md`, `how_to.md`).

Niklāvs surfaced an agent-side issue at the end: the running shipping-agent session described itself with stale pre-cutover language ("silver-layer mart", "7 silver-layer mart tables", "Sendmoments" as entity scope, missing ORWO from priority list). Diagnosed as agent hallucination — the docs themselves are clean. Three remediation options were laid out (re-trigger / harden §11 boot story / both); none applied. Parked.

## Next concrete step

Per Niklāvs' direction, the harvest itself is parked. Focus shifts to **shipping-agent audit** (separate quest — see `shipping-agent-audit-resume.md`). Items remaining on this harvest quest are blocked or low-priority:

1. **Batch 3 dig** — `fact_shipment_cost_summary` aggregation rules, `fact_truck_charges` Variant B allocation, `post_processing` UPDATEs. Was deferred mid-session; can resume when the audit clarifies whether more caveats are warranted.
2. **Jebrim's `bank/drafts/notes/shipping/bi-etl-shipping-mart-caveats.md`** — cross-quest summary note pointing to the agent-side docs as SOR. Discussed but not drafted. Low-priority — agent-side docs are the operational SOR; the bank note is a convenience for cross-mart pattern reuse.
3. **Hallucination guardrail in `shipping-agent/how_to.md` §11** — harden the boot story to forbid freehand mart description (per Option B from the diagnosis). Likely subsumed by the audit findings.

## Files / paths to read first

When this quest is resumed:

1. This file.
2. `shipping-agent-audit-resume.md` — the audit may inform what (if anything) is still needed here.
3. `bi-analytics-main` commit `2406916` — what landed in batch 1+2.
4. The skipped-caveats list from S032 chat history (10 already-covered items, plus the ~30 batch-3 candidates not yet evaluated).

## Watch-outs

- **Don't re-run batch 1+2 caveats.** They're integrated. Re-route conflict check via grep before adding any new caveats.
- **bi-etl repo cadence.** Pull `bi-etl` before resuming any SQL-level dig — the mart moves fast (per keepsake pin).
- **Routing rule first.** Read `shipping-agent/reference/_about.md` before proposing any new docs. The routing rule was the load-bearing miss earlier in this quest.
- **Agent location.** As of S032 close (2026-05-22), the agent lives at `Documents/GitHub/shipping-agent/` (relocated from `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/`). The bi-analytics-main commit `2406916` for batch 1+2 still lives at the old path in that repo's history; if reopening this quest after the old location is removed, point at the new path.

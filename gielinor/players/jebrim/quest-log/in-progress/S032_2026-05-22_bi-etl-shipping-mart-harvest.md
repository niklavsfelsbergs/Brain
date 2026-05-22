# S032 — 2026-05-22 — bi-etl shipping mart harvest

**Player:** Jebrim
**Birth:** S032 close
**Status:** in-progress (parked at close)

## What this quest is

Dig through `bi-etl/dags/enterprise_silver/shipping_data_mart/` to extract operational caveats for the `shipping-agent/` package — the kind of mechanics gotchas, defensive logic, and "things that might not be all the way true" that don't surface in column-level docs. Output: caveats routed into the agent's reference layer so it can communicate uncertainty when answering.

## Turn-by-turn

- **Open.** Niklāvs cued the harvest; framed the angle as "defensive-logic archaeology" — every defensive SQL construct in the mart is a documented gotcha worth lifting into prose. Niklāvs sharpened to: caveats the shipping-agent needs to **communicate** when something might not be all the way true.
- **Pulled bi-etl.** `46310c4d3` post-pull. Skimmed mart structure: 7 entities (4 facts + dim + lookup + spine), 23+ providers in invoice-lines.
- **Batch 1.** 33 caveats extracted from mart README + fact_shipments README + legacy_adhoc_corrections. Niklāvs culled to 16 keepers via leverage sort (recommend / maybe / probably-not).
- **Batch 2.** ~30 caveats from per-provider SQL + map_shipment_key + invoice-lines README. Niklāvs culled to 11 keepers via the same leverage sort. Total 27 candidates across batches.
- **Routing pivot mid-flight.** Proposed new `reference/data-caveats.md` (Path A). Niklāvs approved. **Then discovered** `reference/_about.md` carries an explicit routing rule that splits content across 4 existing files — new file would duplicate and violate convention. Surfaced the conflict; re-proposed Path A as "re-route per existing convention." Niklāvs approved. Mapping revealed ~10 of the 27 candidates were already covered in existing docs.
- **Applied 17 inserts** across 5 files: `mart-contract.md` (×4), `tables.md` (×4), `sources.md` (×2), `known-dq.md` (×2), `how_to.md` (×1 new cross-cutting rule on transit/delivery DQ + renumbering pass on rules 16–28 → 17–29 + 7 cross-reference updates).
- **Committed + pushed.** `picanova/bi-analytics@2406916` — "shipping-agent: data caveats from bi-etl harvest (S031)" (commit subject says S031 because SNNN wasn't computed yet at commit time; close-session resolved to S032).
- **Late surface — agent hallucination.** Niklāvs pasted output from a running shipping-agent session that described itself with stale pre-cutover language ("silver-layer mart," "7 silver-layer mart tables," "Sendmoments" as entity scope, ORWO missing from priority list). Diagnosed: docs are clean (gold-explicit throughout); the agent freehand-generated from model prior despite docs being correct. Three options offered (re-trigger / harden §11 boot story / both). Parked.
- **Close.** Niklāvs cued park + close. Next session = shipping-agent audit. Resume files for both quests written. Harvest skill draft captured in `spellbook/drafts/skills/`.

## Pending external actions

None pending. `bi-analytics-main` commit pushed (`2406916`).

## Decisions made

- **D1 — Routing convention beats single-file convenience.** Proposed a new `data-caveats.md`; discovered existing routing rule in `reference/_about.md` mid-flight; switched to splitting across existing files. The convention was load-bearing — would have duplicated content if not surfaced.
- **D2 — Cull batch-by-batch with leverage sort.** Batches of 25-30 caveats were too large to validate as a list; sorting into recommend / maybe / probably-not per leverage gave Niklāvs a fast triage surface. Pattern repeated successfully across both batches.
- **D3 — Caveat shape is "what the agent should communicate when answering."** Not "every defensive construct in SQL." The shipping-agent operates under a Direct/Decompose/Clarify mode framework with cost-basis and DQ-uncertainty disclosure rules — caveats had to fit that surface, not be raw mart trivia.
- **D4 — Harvest stops at batch 2.** Batch 3 (cost_summary aggregation, truck_charges Variant B, post_processing UPDATEs) deferred. Coverage of high-leverage caveats was good enough; diminishing returns expected.
- **D5 — Hallucination is its own category.** The observed mismatch between clean docs and stale agent output isn't a doc bug — it's an agent-behavior question that becomes part of the next quest's scope (audit).

## Pending drafts

None pending principal sign-off — the harvest's product (the 17 caveats) landed directly in the shipping-agent docs via Niklāvs' in-session approvals (not in this brain's draft layer).

## Related

- `inventory/bi-etl-shipping-mart-harvest-resume.md` — resume state if this quest is reopened.
- `inventory/shipping-agent-audit-resume.md` — next session's quest, framed at close.
- `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/` — where the work landed.
- Commit `2406916` on `picanova/bi-analytics:main`.
- `spellbook/drafts/skills/2026-05-22-read-routing-manifest-before-proposing.md` — skill harvested from D1.

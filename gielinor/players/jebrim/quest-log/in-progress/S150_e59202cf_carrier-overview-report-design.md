# S150 — Carrier Overview Report: design + spec (session e59202cf, 2026-06-03)

Same session as the [[S148_104c786b_eu-tender-dhl-paket-round2|S148]] FedEx rebuild (committed e31f786 / be4a393); after FedEx closed, pivoted to scoping a new deliverable with the principal.

## What was asked
A **manager-facing carrier-overview report** for the shipping & logistics manager: per carrier — what they service, where competitive, which cost-position negotiations change the story, and which lanes they're viable on + who they compete with. Discussed and scoped (not built).

## What happened
Iterative design discussion → locked a thorough, executable spec. Grounded the taxonomy in a real data pull (verify-the-thing, not recall):

- **Data findings** (from `population.parquet`, 2.875M shipments, DQ clean): **vol-weight dominates 96.2%** of parcels (median bill 2.2× actual) → light-but-bulky book, chargeable weight is the axis; **a side >60cm on 38.3%** = the single most decisive dim line (DHL Sperrgut trigger); only 17 destinations, top-7 = 95.7%.
- **Surprises that reshaped it:** AT (4.9%), IT (4.0%), ES (2.4%) bigger than CH and missing from the principal's first lane list; **no UK volume** in the priced population (DPD UK out of scope) → UK skipped; NO immaterial (0.01%).
- **9-lane taxonomy locked:** DE / FR / Benelux / AT / IT / Iberia / CH / Nordics / ROW.
- **Key design resolution:** parcel profiles are **carrier-native** in each section (carriers' surcharge geometries differ), but the cross-carrier comparison runs the **same real parcels** through every engine (no shared profile needed) with a neutral Compact/Bulky/Large slice as a reading lens only.
- **10 clarifying questions answered** → decisions locked (new-offer engine cost basis + invoice-compare line; full-year volume / Q1 head-to-head; raw engine cost; vol-weighted-avg winner; dims-assumed-correct; freight folded; no separate UPS/DB Schenker sections; volume-tier OUT; facts + "Analyst take" line; two deliverables full-HTML + exec-brief).
- **Build shape:** self-contained `2_analysis/carrier_overview/` folder; build `lib/` first, then 9 carrier dwarves in parallel → sections, then synthesis → 2 HTML deliverables.

## Artifacts
- `bi-analytics-main/.../2_analysis/carrier_overview/PLAN.md` — canonical thorough spec (incl. Decisions-locked block). `docs/CARRIER_OVERVIEW_REPORT_PLAN.md` → pointer.
- brain `inventory/carrier-overview-report-resume__e59202cf.md` — foreground + kickoff prompt.

## Next
BUILD (next session). Kickoff prompt is in the resume. One dwarf per carrier (roster in PLAN §5) + synthesis. Substantial fan-out session, token-heavy by design ("thorough, not quick").

## Cascade.
None — this is a new-deliverable design session; no engine/matrix/decision-doc changes (the FedEx cascade was [[S148_104c786b_eu-tender-dhl-paket-round2|S148]], already landed). The spec doc is the only new tender-repo artifact.

## Main-brain changes.
None — player work session over the tender repo; no gielinor architecture/meta/ritual changes.

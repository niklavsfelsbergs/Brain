---
quest: S275_abfcf511_orwo-tender (continuation; this session sid cb17c25e)
sid8: cb17c25e
ts: 2026-06-19 (session cb17c25e: Wolfen uninvoiced-carrier coverage gap -- handover note only; no NFE writes)
parent_resume: inventory/orwo-tender-resume__926f247a.md (the canonical ORWO resume + MONDAY HANDOVER -- read that first for tender state)
open_dep: MODEL the uninvoiced postal/consolidator layer at Wolfen; BLOCKER = no invoiced cost, Niklavs to decide pricing basis (see below)
---

# ORWO Tender 2026 -- Wolfen uninvoiced-carrier coverage gap (handover)

> **⚠ CORRECTION (2026-06-25): FKBRING + CIRRO are EXCLUDED -- TCG does not pay their shipping.**
> Verified `enterprise_bronze.orwo_pts_parcelfinish` (`carrierid` × `senderkeyaccountid`): FKBRING/FKBRINGPARCEL
> = key account **`fotoknudsen`** → Norway; CIRRO = key account **`onskefoto`** (Önskefoto) → Sweden. These are
> dedicated single-key-account Nordic brand lanes, NOT TCG-paid freight. Their 0% invoice coverage is correct
> (no TCG invoice because TCG isn't billed). Remove them from the "uninvoiced layer to price" table below --
> the TCG-paid layer to solve is everything else (POST_DVF/Deutsche Post is the real one). Noted in NFE
> `projects/7_ORWO_tender_2026/_scope.md` (2026-06-25 EXCLUSION block).

> Separate session file (cb17c25e) on purpose: the canonical resume __926f247a was being actively
> edited by a live sibling (its dims / MONDAY HANDOVER write) when I worked, so per D-024 anti-clobber
> I am NOT piling into that file. Fold this item into the canonical resume's OPEN list at the next
> clean (non-racing) ORWO session. Comms cross-pointer posted (jebrim-cb17c25e OPEN, 2026-06-19).

## THE HANDOVER ITEM -- model the uninvoiced postal/consolidator layer

The reprice work so far (UPS, DHL, GLS, Maersk) covers only the **UPS+DHL invoiced spine**. It is NOT
the whole Wolfen book. At `shippingprovider_extkey` grain (`production_site='Wolfen'`, gold
`shipping_mart.fact_shipments`, full order period), **~600k shipments / ~22% of the Wolfen book ship
via carriers with 0% invoice coverage** -- and they are real operational lanes, not trials:

| Carrier (extkey)        | What it is                          | Shipments | Share  | Invoice cov |
|-------------------------|-------------------------------------|-----------|--------|-------------|
| POST_DVF                | Deutsche Post (Warenpost-class)     | 426,457   | 15.5%  | 0%          |
| FKBRING + FKBRINGPARCEL | Bring (Nordic post)                 | 78,804    | 2.86%  | 0%          |
| CIRRO                   | cross-border consolidator           | 69,847    | 2.53%  | 0%          |
| POSTNL_MB/EU/AVG        | PostNL                              | 11,424    | 0.41%  | 0%          |
| POST (literal)          | generic postal                      | 4,590     | 0.17%  | 0%          |
| GUELL                   | Guell (regional/linehaul)           | 4,078     | 0.15%  | 0%          |
| TD                      | tracked-delivery stream (confirm)   | 3,200     | 0.12%  | 0%          |
| POSTAT_* (5 variants)   | Austrian Post                       | 3,869     | 0.14%  | 0%          |

## THE BLOCKER (Niklavs to decide) -- how do we price them?

We have **NO invoiced cost** for any of these. Only the UPS + DHL invoice books were loaded into
`enterprise_silver` (the original tender scope), so the mart prices these carriers via
`final_shipping_cost_eur` (expected/avg/rate-card) and `real_shipping_cost_eur` is null. They cannot
be repriced on an invoiced spine the way UPS/DHL were. Before they enter the tender comparison,
Niklavs has to figure out the cost basis. Options to weigh:
  - pull each carrier's rate card and model cost from the card (like the GLS/Maersk carrier-switch did);
  - source + load their invoices into silver (gives a true invoiced spine, heavier);
  - accept a modeled expected-cost basis as the comparison floor.

## DQ note that bit the first pass

`shipping_provider_group` is unreliable -- the same extkey maps to more than one group (POST_DVF
appears under both POST and OTHER; DHL3 under both DHL and OTHER). A group-level rollup HID this whole
layer (the first answer only saw a single "POST 15.5%" lump). **Use `shippingprovider_extkey` as the
carrier grain, not the group.**

## NOT to model (genuinely tiny + no-cost noise)

GLS 14 (cross-border EuroBusiness trial, Aug-Sep 2025, mostly DELIVERED -- the "GLS lapsed" carrier),
ASENDIA 3 (UK/CH mail trial, ALL status=EXCEPTION -- failed), DHLX2 69, DBSCHENKER 60, UNITEDPRINT 60,
MAERSKFR 1, STANDARD 1, and `(null)`/unassigned 2,097 (no carrier picked yet -- concentrated in June
2026 in-flight + a Dec 2025 peak-season residue).

## Anchors

Canonical ORWO resume: inventory/orwo-tender-resume__926f247a.md. Parent quest
[[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain]]. Mart contract:
bank/domains/shipping-mart.md. All figures read live READ-ONLY via Redshift MCP, 2026-06-19.

# Mart pull: PCS CUSTOM_OVERSIZED example for EU tender DB Schenker reroute

Player in scope: Jebrim
Tier: gold-contract (shipping_mart.fact_shipments only)

## Ask
Concrete PCS + CUSTOM_OVERSIZED shipment example for DB Schenker reroute work:
one order# + tracking, dims (l/w/h/girth/weight) + carrier, plus 5 alternates.
Provenance: which column = PCS, which = order number.

## Scope used
- packagetype matched case-insensitively + trimmed: LOWER(TRIM(packagetype)) = 'custom_oversized'
- PCS identifier = source_system = 'PCS' (shop is NULL for PCS rows; source_system is the storefront code). 1,192 PCS oversized shipments total.
- order number = shop_ordernumber
- 2026-Q1 filter (received_by_carrier_date) returned 0 — that date col is NULL across the whole PCS-oversized slice, so dropped the date filter per brief.

## Result (DB Schenker primary, for reroute relevance)
Primary: order PPO33731316, tracking 00159074594178139988, shipment_id 13143055500285006
  dims 165 x 122 x 5 cm, girth 419 cm, 7.19 kg, DB SCHENKER
Alternates (all PCS / CUSTOM_OVERSIZED / DB SCHENKER):
  PPO72144506, PPO61923460, PPO66479142, PPO28088879, PPO96686747

## Checks
- girth reconciles: PPO33731316 165+2*(122+5)=419 ok; PPO72144506 200+2*(150+30)=560 ok
- source_system='PCS' confirmed distinct from Picturator/PicaAPI storefronts; shop NULL for PCS

## Open
- received_by_carrier_date unpopulated for PCS-oversized -> no date scoping possible on this slice (flag for tender work if Q1-specific evidence needed).

---

# Mart pull (cont.): PCS zV (cut-to-size) examples — same reroute work

Ask: ~8 concrete PCS zV (zugeschnittene Verpackung) shipments w/ order#, tracking, dims, carrier;
matched column; templated-dims caveat + distinct-tuple share.

## Scope used
- packagetype: LOWER(TRIM(packagetype)) = 'zugeschnittene verpackung'
- 3 casing variants in this slice: 'zugeschnittene Verpackung' (199), 'Zugeschnittene Verpackung' (196), 'zugeschnittene verpackung ' [trailing space] (105). TRIM catches the 3rd.
- source_system = 'PCS'; order# = shop_ordernumber. 500 zV rows total on PCS.

## Key correction vs prior PCS pull
- PCS zV order#s are NOT mostly PPO. Mixed prefixes across many carriers: UKA/YODEL (177), MFA/UPS (70), UKA/DPD UK (43), FRA/UPS (40), BTBA, NLA, ITAA, SEA... PPO is a minority (29 rows). DB SCHENKER present (10 rows, incl. 7 PPO).
- The brief's "PPO..." and "~130x92x8" both DO appear but are not the whole slice.

## Sample (diversified across prefix + carrier)
- PPO05277707 | ship 755049561702529861 | trk 00159074594195353749 | 130.3x91.6x7.6 | girth 328.7 | 3.168kg | DB SCHENKER
- PPO63093980 | ship 753773436620901264 | trk 00159074594194979841 | 130.3x91.6x7.6 | 328.7 | 3.615kg | DB SCHENKER
- PPO74511773 | ship 1142261945221396504 | trk 1Z698W756819135699 | 110x85x20 | 320 | 9.870kg | UPS
- PPO75988598 | ship 230165910877764851 | trk 1Z698W756869991278 | 121x80x7.6 | 296.2 | 3.852kg | UPS
- MFA19911618909 | ship 952022780711304971 | trk 1Z698W756830126703 | 110x85x20 | 320 | 6.250kg | UPS
- FRA49901474503 | ship 935584404275004039 | trk 1Z698W756862680661 | 130.3x90.3x10 | 330.9 | 9.807kg | UPS
- BTBA1000611251 | ship 230128670716739803 | trk JJD0002233022014022 | 110x85x20 | 320 | 9.220kg | YODEL
- UKA39905531333 | ship 643606672528722902 | trk JJD0002233022035885 | 130x70x25 | 320 | 17.517kg | YODEL
- PPO91335052 | ship 754180890322715095 | trk UY017052775FR | 21.5x22.5x3.7 | 73.9 | 0.300kg | ASENDIA (the lone tiny outlier)

## Templated-dims caveat (the answer to caveat Q)
- YES, strongly templated on L/W/H: only 9 distinct L/W/H tuples across 500 rows. Top 3 cover ~90%:
  110x85x20 (39%), 130.3x90.3x10 (30.6%), 130x70x25 (20%). The ~130x91.6x7.6 template = 4.6%.
- BUT weight is NOT templated: 349 distinct L/W/H/weight tuples across 500 -> dims are box presets, weight is real per-parcel.

## Checks
- variant count verified by GROUP BY packagetype (3, incl. trailing-space)
- girth reconciles: 110+2*(85+20)=320 ok; 130.3+2*(90.3+10)=330.9 ok
- distinct-tuple share computed directly (9 L/W/H vs 349 L/W/H+wt)

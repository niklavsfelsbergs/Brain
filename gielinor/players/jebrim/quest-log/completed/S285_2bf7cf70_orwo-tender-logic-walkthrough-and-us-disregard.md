# S285 — ORWO tender: logic walkthrough + per-lane UPS-share verification + US disregarded

**Player:** Jebrim · **sid8:** 2bf7cf70 · **2026-06-22**
**Continues:** [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]]/abfcf511 (ORWO tender umbrella) · [[S283_60de5609_orwo-tender-assumptions-and-carrier-questions|S283]]/60de5609 (assumptions) · [[S284_f1b5f17c_orwo-engine-sanity-and-assumptions-lock|S284]]/f1b5f17c (engine sanity + lock). Delivers the walkthrough [[S284_f1b5f17c_orwo-engine-sanity-and-assumptions-lock|S284]] queued as the next step.

## Ask

Walk Niklavs through the whole ORWO tender logic end-to-end. Then a chain of clarifying questions that pulled on the UPS thread and ended in a scope decision.

## Turn 1 — the walkthrough (chat)

Delivered the end-to-end logic in chat, dense: the entity (Wolfen, not `source_system='ORWO'`), the weight-only reframe, the 5 decisions (invoices-only cost basis · Wolfen spine · tracking grain · full-cost both sides · per-lane switch), the pipeline (spine → silver cost → per-tracking base → card+trust-gate → `carrier_engines/{ups,dhl_paket,gls,maersk}/` → switch_compare → per_lane_optimum → COMPARISON.md), the −€509k→reversal→−€282k arc, the locked assumptions, the open tail. No `WALKTHROUGH.md` doc built — he wanted the in-chat walk.

## Turn 2 — clarifications

- **"Freight-only"** = base transport charge (weight × zone × service), surcharges stripped — the misleading lens that made GLS look cheap; full-cost both sides is the reversal.
- **Lane assignments** corrected: Maersk = GB + FR/ES/IT/IE; GLS = AT + CH + NL/**BE**/NO (he wrote "NE"). GB is the whole Maersk story (−€177k of −€187k); AT+CH the GLS story.
- **Annualization** = simple H1×2 (GLS Season carried as blended 0.417% annual-proxy); flagged as rough, seasonality not modelled.

## Turn 3 — the UPS thread (mart-verified, READ-ONLY)

"Do we drop UPS completely?" → checked ground truth instead of inferring. Read NFE `per_lane_optimum.py` + `COMPARISON.md`: the optimum compares **{current incumbent, GLS, Maersk}** — the UPS *new offer* is NOT a candidate. Then live mart (`shipping_mart.fact_shipments`, `production_site='Wolfen'`):

- **US is UPS-captive — 99.3%** (UPSWWE 3,039 + UPSEXPRESS 68 + tail; POST/USPS/DHL = noise; ~3,135 all-period). No competitor card serves US → optimum keeps it on incumbent.
- **EU cross-border lanes are genuinely UPS today**: GB 87.7% · AT 65.2% (DHL 30% too) · CH 87.5% · FR 85% · IT 92% · ES 90% · BE 90% · IE 80% · NL 26.6% (rest postal) · NO ~0%. DE 5.3% UPS.
- So **"drop UPS from EU" = the −€282k saving itself**, concentrated in **GB (→Maersk −€177k) + AT (→GLS −€56k) + CH (→GLS −€35k)**; FR/IT/ES/BE/IE are near-ties where UPS is competitive.
- Caveats: the saving is measured vs UPS-*current*, not the UPS-*offer* (AT is UPS's defendable lever); 1→2 cross-border carriers is an unpriced ops cost; pulling EU volume weakens leverage on the US lane where UPS is captive.

## Correction harvested

My Andrea-screenshot summary named only the *winning* carriers per lane ("keep DHL; GB→Maersk; AT+CH→GLS") and hid that the moved lanes are **UPS** lanes — i.e. the recommendation is a UPS-from-EU exit. Niklavs caught it with "wait we drop UPS completely?" → examine draft `2026-06-22-name-the-incumbent-a-switch-exits` + memory entry.

## Turn 4 — the uninvoiced-carrier layer (mart-verified, READ-ONLY)

Profiled the ~604k / 22% Wolfen 0%-invoice layer (sibling __cb17c25e). What/where: POST_DVF = Deutsche Post Warenpost DE-domestic mail **427,869** (71% of the layer); FKBRING/PARCEL = Bring → NO 78,971; CIRRO = consolidator → SE 69,967; PostNL → NL 11,421; POST/GÜLL/TD/POSTAT = DE + small cross-border tails. All mail-class / postal last-mile. Carry-mapping: DHL Warenpost can take POST_DVF (same product); Maersk can't (no DE-domestic mail); Bring(NO)/Cirro(SE)/PostNL(NL) are postal last-mile where parcel carriers are likely cost-negative.

**POST_DVF cost check:** 100% `cost_source='expected'`, **€1.27M all-period / €2.98 avg, 0% invoiced** — never validated against a real bill (POST is a known structural 99%-estimate hole, [[S266_e455d12d_orwo-box-grain-quota-estimator|S266]]). Decided it **stays on DHL** (no cheaper alternative for sub-1kg DE mail), but the cost basis is unverified.

## Turn 5 — handover swapped

Principal redirected the handover: **annualization deferred**; next session **validates + costs the uninvoiced carriers**, first task = **Warenpost NEW vs OLD contract** reprice on POST_DVF vs the €2.98 expected. Resume NEXT block + handover prompt updated accordingly.

## Decisions

- **DISREGARD US** (principal) — drops US (1,855 H1 / ~3.1k shipments) from tender scope; €0 optimum delta → **headline unchanged −€282k/yr**. US joins sendmoments as out-of-scope.
- **POST_DVF stays on DHL/Deutsche Post** — Warenpost DE mail, no cheaper alternative; but its €1.27M/€2.98 cost is 100% modeled-expected, unvalidated → next-session check.
- **Handover swapped** — uninvoiced-carrier validation (Warenpost new-vs-old first) is next; annualization deferred to after.

## Cascade

Updated `inventory/orwo-tender-resume__60de5609.md` (canonical rolling resume — S285 DONE block + US-disregard + per-lane UPS findings + the uninvoiced-carrier profile table + POST_DVF facts; NEXT = validate+cost the uninvoiced carriers, Warenpost new-vs-old first; annualization deferred to LATER). No NFE/bi-etl writes (read-only session). 1 examine draft + 1 memory entry. Two close commits this session: 6c99317 (walkthrough+US) + 150d9a2 (carrier layer + handover swap).

## Main-brain changes

None to globals/meta/rituals. Player-scope only (Jebrim quest-log + inventory + comms) + 1 memory entry.

## Pending external actions

None pending this session. Carried-open (principal's, on the umbrella): SEND the carrier dispatch; get real ORWO GRI% per incumbent.

## Open (carried on umbrella [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]])

NEXT SESSION = **validate + cost the uninvoiced carriers** (~604k / 22% Wolfen gap), first task = **Warenpost NEW vs OLD contract reprice on POST_DVF vs the €2.98 expected**. Annualization deferred to after. See resume__60de5609 "NEXT SESSION — START HERE".

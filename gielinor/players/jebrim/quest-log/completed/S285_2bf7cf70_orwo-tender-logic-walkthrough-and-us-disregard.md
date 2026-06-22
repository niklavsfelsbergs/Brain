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

## Decisions

- **DISREGARD US** (principal) — drops US (1,855 H1 / ~3.1k shipments) from tender scope; €0 optimum delta → **headline unchanged −€282k/yr**. US joins sendmoments as out-of-scope.

## Cascade

Updated `inventory/orwo-tender-resume__60de5609.md` (canonical rolling resume — S285 DONE block + US-disregard + the per-lane UPS findings; NEXT reset to proper annualization per the EU-tender method). No NFE/bi-etl writes (read-only session). 1 examine draft.

## Main-brain changes

None to globals/meta/rituals. Player-scope only (Jebrim quest-log + inventory + comms) + 1 memory entry.

## Pending external actions

None pending this session. Carried-open (principal's, on the umbrella): SEND the carrier dispatch; get real ORWO GRI% per incumbent.

## Open (carried on umbrella [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]])

NEXT SESSION = **annualize properly per the EU-tender method** (per-country seasonal re-weight + peak split, replacing H1×2; anchor `research/2026-06-10-eu-tender-annualization-method-and-assumptions.md`). See resume__60de5609 "NEXT SESSION — START HERE".

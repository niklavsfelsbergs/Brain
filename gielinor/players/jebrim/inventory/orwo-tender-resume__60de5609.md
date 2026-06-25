---
quest: S283_60de5609_orwo-tender-assumptions-and-carrier-questions (continues S275/S281 ORWO arc; this increment worked under session ca27d9be)
sid8: 60de5609   # canonical rolling ORWO resume; last touched by session 2bf7cf70 (S285) 2026-06-22
ts: 2026-06-22 (S286 / 614ffdf6)
open_dep: tender MODELING + assumptions COMPLETE; US DISREGARDED. **ANNUALIZATION DONE this session → headline -EUR343k/yr (-3.2%), band -325k..-362k** (supersedes crude H1×2 -EUR282k; full report `repricing_base/annual_2026/`). POST_DVF characterized: it's Deutsche Post **DV-Freimachung** letter/Dialogpost mail (NOT Warenpost), expected = hardcoded **DHL Kleinpaket 2.79×1.0125 + peak** (bi-etl `update_fact_shipments_cost.sql`); no DE-domestic Warenpost card exists. Rest of layer (Bring 73k/Cirro 70k/PostNL 11k/tails ~14k = ~165k) is **100% UNCOSTED (cost_source NULL)**, not expected. Carried-open (principal's): ask Bring/Cirro/Deutsche-Post re cost; SEND dispatch; get real GRI%.
---

# ORWO Tender 2026 - resume

> **2026-06-25 (S367/ae7565da) — methodology explainer built + method stress-tested.** NEW `NFE/projects/7_ORWO_tender_2026/methodology_walkthrough.html` (sections 00-08) for Niklavs to present — the "how it was calculated" companion to `annual_report.html`. Eight methodology challenges verified + folded in. Two settled for good: (a) **candidate set = {incumbent, GLS, Maersk}** — probed UPS/DHL as cross-challengers, both LOSE every contested lane (DHL-Intl GB €276k vs €53k), not worth implementing; (b) **dim/volumetric weight** — base rides on the incumbent's billed weight (UPS /5000, dim-inclusive), competitors inherit it = conservative (UPS /5000 ≥ GLS /6000); recomputing GLS on its own /6000 moves the saving <€650/yr (band quantization on light parcels). Headline UNCHANGED −€343k/yr. **(c) GRI/baseline (verified from silver invoices):** the −€343k is vs **current (flat 2026) costs, GRI-EXCLUDED** (`annual_orwo.py` do-nothing = current×vol, no ×1.05); the 5% GRI is a forward placeholder for the incumbent-offer value only. **No GRI absorbed in 2026** — DHL base+surcharges flat Sep25–Jun26 (all-in per parcel falls into March as Q4 peak unwinds, not a rise); UPS band floors flat Mar–Jun (silver doesn't reach 2025 → use OLD-vs-NEW UPS cards for the annual delta). The "March cost rise" = the DHL returns surge (`__0888690d`), not an outbound GRI. NEXT-SESSION block below is still the live next step (uninvoiced layer — but FKBRING/CIRRO now excluded per S366).

## >>> WHERE WE STAND (2026-06-22, 16:10) - read this first

**The surcharge re-run is DONE and it REVERSED the verdict.** Folding each carrier's own
surcharge stack into GLS/Maersk AND leveling the incumbent's ACTUAL invoiced surcharges into
"current" (full-cost both sides) kills the -EUR509k/yr GLS saving. On full-cost:

- **All-GLS single switch: +EUR792k/yr WORSE.** All-Maersk: +EUR777k/yr WORSE.
- **DE-domestic core (548k parcels) is the driver:** GLS lands ~+43% (27% stack + ~EUR0.53/parcel
  flat tolls) vs DHL's ACTUAL invoiced ~5.4%. GLS loses DE-domestic **even at 0% energy**
  (+EUR92k H1 / +EUR185k/yr) - so GLS A1 (energy) sizes the loss but CANNOT flip the domestic core.
- **Real saving = lane-specific, ~-EUR265k/yr** (per-lane whole-lane full-cost optimum): keep DHL
  on DE domestic, move **GB -> Maersk (-EUR177k/yr)**, **AT -> GLS (-EUR56k/yr)**, **CH -> GLS
  (-EUR18k/yr)**, small EU tails. NOT a primary switch.
- The -EUR741k/yr freight-only per-lane optimum and -EUR509k/yr primary are both DEAD (freight-base).

**Load-bearing caveat:** GLS/Maersk surcharges are MODELED at Picanova-default (provisional) rates;
DHL/UPS are ACTUAL invoiced (trust-gated). The reversal is conditional on the provisional % - the
dispatch confirms them. But the 0%-energy check shows it'd take negotiating the WHOLE GLS stack
(klima+diesel+toll+private) down, not just fuel, to bring GLS-primary back.

## DONE THIS SESSION (sid ca27d9be)
1. **GLS engine** (`carrier_engines/gls/{constants,calculate}.py`): added the surcharge stack -
   Energy 20.5% + Klima 2.5% + Season(blended 0.417%) on base, Toll Intl 5.70% x-border / 0.38
   national flat domestic, Dieselfloater 4.1% after toll, DE delivery-private 0.15. Emits
   `gls_full_eur` / `gls_surcharge_eur`.
2. **Maersk engine** (`maersk/{constants,calculate}.py`): EU fuel 6.6% on base + country tolls
   (AT 0.29/DE 0.19/DK 0.05) + Overpack 0.40/parcel. Emits `maersk_full_eur`.
3. **Both `switch_compare.py`**: load_book carries incumbent surcharge (UPS fuel+resi; DHL surcharge
   ex Sperrgut), builds `current_full`; prints freight-only AND full-cost. Re-ran both.
4. **New `carrier_engines/per_lane_optimum.py`**: whole-lane cheapest-carrier synthesis -> -EUR265k/yr.
5. **COMPARISON.md REWRITTEN** to the corrected full-cost verdict (pending banner -> CORRECTED note;
   restructured headline + lane table; primary-switch-dead reading).

## >>> ASSUMPTIONS LOCKED + HEADLINE FINAL (2026-06-22) — −€282k/yr

Three open items closed by principal decision → tender is concludable:
1. **Surcharge %s**: ADOPT Picanova rates as correct for ORWO (GLS energy/diesel/klima/toll, Maersk
   fuel/tolls). Dispatch now *confirms*, no longer *blocks*. No number change (already in engine).
2. **Incumbent GRI**: hold at 5% for the do-nothing comparison. No number change (already placeholder).
3. **GLS GB/EFTA clearance**: EXCLUDE for GLS too (€0), mirroring Maersk's confirmed €0. CHANGED a number
   — set `per_lane_optimum.py` GLS_IC18 3.0→0.0, RE-RAN.

**NEW HEADLINE: −€282k/yr** (was −€265k). GB unchanged (Maersk −€177k/yr, still wins). The exclusion's
real effect = **CH-GLS −€18k→−€35k/yr** (€3 off 2,828 parcels). Whole-lane split now: Maersk −€187k/yr
(GB + FR/ES/IT/IE tails, 25.7k trks) + GLS −€94k/yr (AT −€56k + CH −€35k + NL/BE/NO, 30.7k trks).
Per_lane_optimum run output: current €2,451,899 H1 / optimum €2,311,013 H1 / saving −€140,886 H1.
COMPARISON.md fully updated (headline table + lane table + GB lever + caveats + ASSUMPTIONS LOCKED block).

**Recommendation shape (final):** keep DHL on DE domestic; move GB→Maersk, AT+CH(+NL)→GLS; ~−€282k/yr.

## >>> B3 GB-CLEARANCE CONFIRMED (2026-06-22, Andrea) — €0, headline de-risked

Andrea confirmed Maersk GB customs clearance = **€0** (folded into the Evri/Yodel door rate). This was
assumption **B3 (Low-Med)** — the single biggest lever in the −€265k/yr headline. The number does NOT
move (the engine already assumed €0); its biggest risk is now gone. GB-Maersk −€177k/yr stands confirmed.
Flipped to RESOLVED in `carrier_questions/Maersk.md` + `_provisional_assumptions.md`; COMPARISON.md GB
lever note updated. Still open on GB: GLS-side clearance (assumed IC18 €3, GLS High but not Andrea-confirmed).

## >>> SANITY CHECK DONE (2026-06-22, session f1b5f17c) — ENGINES AGREE

Cross-checked ORWO GLS + Maersk engines vs the EU-tender (Picanova) engines (ground truth).
**No mechanical contradictions.** Every copied value + every compounding rule matches:
- **GLS**: Energy 0.205 / Klima 0.025 / Diesel 0.041 / Toll-Intl 0.057 / Toll-Nat 0.38 / DE-private 0.15
  all match ref `constants.py`. Order matches (Energy+Klima+Season on base → Toll on full net x-border /
  €0.38 flat domestic → Diesel after toll → €0.15 flat uncompounded). ORWO correctly copied the
  ACTIVE Toll-Intl-on-net mechanic, NOT the retired base-only `gls/surcharges/toll_international.py`.
- **Maersk**: EU fuel 6.6% base-only / AT 0.29 / DE 0.19 / DK 0.05 additive / Overpack 0.40 every parcel
  all match ref. Fuel base excludes tolls+overpack both sides.
- **Legit divergences (NOT contradictions, flagged):** GLS Season blended 0.417% (= 1%×5/12) vs ref
  1% month-gated — annual-proxy placeholder; dim-dependent surcharges dormant in ORWO (no dims in engine
  input — GLS BigParcel/Overlength, Maersk EU oversize/handling-reject); ROW deferred; GB on the ORWO
  Maersk card (ref excludes GB from Picanova Maersk; GB lever leans on clearance B3, scenario'd).
- **One thing to verify in population-prep:** ORWO consumes a pre-computed `billable_weight_kg`; confirm
  the GLS Euro (EBP) dim-weight cap `max(gross, dim/6000)` cap 30kg was applied upstream so dim-heavy
  x-border parcels aren't understated. Maersk EU is gross-only → no issue.

**Outcome:** −€265k/yr verdict is reference-consistent → stronger to quote. No engine fix / re-run needed.
COMPARISON.md stamped with a VALIDATED 2026-06-22 note.

## >>> S285 DONE (2026-06-22, session 2bf7cf70) — WALKTHROUGH DELIVERED + US DISREGARDED

Logic walkthrough delivered **in chat** (assumed/decided/built/numbers/open, dense). Did NOT build a
`WALKTHROUGH.md` doc — he wanted the in-chat walk; the doc offer stands if he asks later.

**Mart-verified this session (READ-ONLY, gold `shipping_mart`, `production_site='Wolfen'`):**
- **US is UPS-captive — 99.3%** (UPSWWE 3,039 + UPSEXPRESS 68 + tail; only POST/USPS/DHL noise; ~3,135
  shipments all-period / 1,855 H1 invoiced). No GLS/Maersk card serves US → optimum keeps it on incumbent.
- **EU cross-border lanes ARE genuinely UPS today** (UPS share by dest): GB 87.7% (21.5k) · AT 65.2% (41.5k,
  DHL 30% too) · CH 87.5% · FR 85% · IT 92% · ES 90% · BE 90% · IE 80% · NL 26.6% (rest postal) · NO ~0% (Bring).
  DE 5.3% UPS (DHL+postal core). So **"drop UPS from EU" = the −€282k saving**, concentrated in
  **GB(→Maersk −€177k) + AT(→GLS −€56k) + CH(→GLS −€35k)**; FR/IT/ES/BE/IE are near-ties (UPS competitive).
- **`per_lane_optimum.py` compares {current incumbent, GLS, Maersk} — the UPS *new offer* is NOT a candidate.**
  So "drop UPS" is measured vs UPS-*current*, not UPS-*best*. UPS could defend AT (its lever, S280). To make
  the drop-UPS call against UPS's best rates, add the UPS 2026 offer as a 4th candidate in per_lane_optimum.
- Caveats surfaced: pulling EU volume off UPS weakens leverage on the US lane (UPS-captive, no fallback) — now
  moot since US disregarded; and 1→2 cross-border carriers (GLS+Maersk) is an ops cost the rate model ignores.

**DECISION (principal): DISREGARD US.** Drops US (1,855 H1 / ~3.1k) from tender scope. €0 optimum delta
(US was already incumbent-stays) → **headline unchanged −€282k/yr.** Like sendmoments, US is now out-of-scope.

## >>> NEXT SESSION — START HERE: VALIDATE + COST THE UNINVOICED CARRIERS

**Task (Niklavs, 2026-06-22):** close out the **uninvoiced postal/consolidator layer** — ~604k shipments /
22% of the Wolfen book that ship via 0%-invoice carriers and were excluded from the tender's UPS+DHL spine
(sibling resume `orwo-tender-resume__cb17c25e.md`). For each: confirm what it is, what it carries, whether
GLS/Maersk/DHL can carry it, and **what it actually costs** (these are priced 100% on the mart `expected`
basis — a modeled estimate, never validated against an invoice).

**▶ FIRST CONCRETE STEP — validate Warenpost NEW vs OLD contracts (POST_DVF, 71% of the layer).**
POST_DVF = **Deutsche Post Warenpost, DE-domestic light mail**, 427,869 shipments, **100% `cost_source='expected'`,
€1.27M total (all order-periods) / €2.98 avg, 0% invoiced.** Decided: it **STAYS on DHL/Deutsche Post** (no cheaper
alternative — DHL Warenpost IS this product; GLS/Maersk parcel networks are pricier for sub-1kg mail; Maersk doesn't
serve DE-domestic mail at all). But the cost is unverified (POST is a known structural 99%-estimate hole, S266).
→ **Get the NEW vs OLD Deutsche Post / DHL Warenpost domestic contract cards, reprice the 428k POST_DVF stream on
each, and compare both to the €2.98 expected.** Answers: (a) is the €2.98 expected trustworthy? (b) does the new
Warenpost contract save vs the old? Contract anchor: `NFE/docs/shipping_contracts/.../ORWO` (DHL Warenpost = base +
per-100g × zone, carrier-contracts digest); reprice off the mart Warenpost weight band.

**Then the rest of the layer** (smaller, postal last-mile — likely STAY, displacement is cost-negative; confirm
eligibility + cost only if a consolidator/postal card is in hand):

| Carrier | What it is | Carries (dest, vol) | Can GLS/Maersk/DHL take it? |
|---|---|---|---|
| **POST_DVF** | Deutsche Post Warenpost | DE 427,869 | DHL Warenpost (= same product). NOT Maersk. ← the one that matters |
| **FKBRING** (+PARCEL) | Bring (Norwegian Post) | NO 78,971 | DHL-Intl/Maersk reach NO but customs + Bring is national post → hard to beat |
| **CIRRO** | cross-border consolidator | SE 69,967 | GLS/DHL-Intl *can*; consolidator economics likely cheaper → needs card |
| **POSTNL** | PostNL | NL 11,421 | GLS (already wins NL) / Maersk *can*; PostNL cheap local |
| POST / GUELL / TD / POSTAT | postal / Güll / tracked-del / Austrian Post | DE ~11.7k + AT/FR/GB tails | DHL/GLS absorb either way; tiny |

**Cost-basis blocker (carry it):** none of these have an invoice → priced on mart `expected`; the parcel reprice
engines can't price mail-class. To compare, need each carrier's **mail/Warenpost-equivalent card**, not the parcel
cards already loaded. Mart facts above pulled live S285 (READ-ONLY, gold `shipping_mart`, `production_site='Wolfen'`).

## >>> ✅ DONE 2026-06-22 (S286) — ANNUALIZED PROPERLY per the EU-tender method

**Headline = −€343k/yr (−3.2%), band −€325k…−€362k**, on €10.6M annual carrier-comparable spend.
Built `repricing_base/annual_2026/annual_orwo.py` (self-contained build+render, mirrors EU-tender
`2_EU_tender_2026/.../annual_2026/`) → `annual_stats.json` + `annual_report.html` (8 sections: KPIs,
H1→annual bridge waterfall, carrier portfolio, volume/cost curve, peak exposure, by-dest, do-nothing-vs-tender,
methodology + ledger). **Method:** per-lane saving-per-parcel (engine, validated, population-invariant)
× **actual** per-lane annual volume from ORWO's own **order-created-date** curve (real Q4 2025 peak +
mature Feb–Apr non-peak run-rate; May/Jun immature, Jul–Sep estimated → DE-only, €0 saving). Bridge:
H1 −€140,886 → +€201,277 volume scale → +€1,309 peak differential → **−€343,472**. Beats crude ×2 by
+€61k (Q4 ~40% of volume > flat double); **robust** — saving rides on mature Q4 cross-border volume.
GB(→Maersk)+AT/CH(→GLS) = ~95% of saving. COMPARISON.md + per_lane_optimum.py ANNUALIZE note updated.

**Cost basis caveat:** the €10.6M annual is the engine's carrier-comparable FULL-COST (same basis as
the headline), NOT the mart accounting total — don't reconcile to GL. Provisional: GLS/Maersk surcharge
stacks Picanova-adopted (locked); Jul–Sep est. (DE-only, €0 saving). Refinements deferred: quantify the
UPS Q4 peak-differential upside; nail Jul–Sep + May/Jun maturity with a cleaner volume model.

### (original deferred spec, for reference)
Replace the crude **H1×2** with the per-country seasonal re-weight + peak split the EU tender used (anchor:
`players/jebrim/research/2026-06-10-eu-tender-annualization-method-and-assumptions.md`): base = repriced book (no ×N
replay); volume → FY per-country via each dest's own 2025 seasonal ratio (EU-tender FY-share Q1 20.7/Q2 21.2/Q3 17.9/
**Q4 40.2**); cost = peak-free base × annual vol + peak rate × peak-window vol; both sides same 2026 basis; present as a
band; build the H1→annual bridge waterfall. Mirror `2_EU_tender_2026/.../annual_2026/`. **Do this after the carrier layer.**

## >>> (prior next-step: EU-tender vs ORWO engine sanity check — DONE this session)

**Task (Niklavs, 2026-06-22):** cross-check the ORWO GLS + Maersk engines against the EU-tender
(Picanova) GLS + Maersk engines. **Treat the EU-tender engines as CORRECT (ground truth).** The
ORWO surcharge stacks were *lifted* from them (the provisionals say so) — so the question is: does
the ORWO implementation **contradict** the reference anywhere? If the reference is right and ORWO
diverges, ORWO is wrong.

- **Reference (assume correct):** `NFE/projects/2_EU_tender_2026/2_analysis/carrier_engines/{gls,maersk}/`
  — `constants.py` + `calculate.py` + the **`surcharges/`** subdir (ORWO has no such subdir — the
  stack is inline in `calculate._apply_surcharges`) + `tests/` + `CLAUDE.md`.
- **Under test:** `NFE/projects/7_ORWO_tender_2026/repricing_base/carrier_engines/{gls,maersk}/`
  — `constants.py` + `calculate.py` (`_apply_surcharges`).
- **What to check for contradictions (not just value drift — mechanics):**
  1. **Surcharge %s**: GLS Energy 20.5% / Diesel 4.1% / Klima 2.5% / Toll Intl 5.70% / DE-private
     0.15 / Season 1%; Maersk EU fuel 6.6% / country tolls (AT 0.29/DE 0.19/DK 0.05) / Overpack 0.40.
     Do these match the EU-tender constants, or did I transcribe a wrong number?
  2. **Application ORDER + base**: ORWO applies Energy+Klima+Season on base → Toll → Diesel (A5).
     Does the EU-tender engine compound the same way (e.g. is Toll Intl really on the full net incl.
     Energy/Klima, is Diesel really after toll, is Season on base)? A wrong compounding order is the
     subtle contradiction to hunt.
  3. **Domestic vs x-border split**: ORWO uses national flat €0.38 domestic / 5.70% x-border. Same
     split logic in EU-tender?
  4. **Per-parcel vs %**: confirm the €0.38 toll + €0.15 private are per-parcel flat in BOTH (they
     dominate the DE-domestic verdict — if EU-tender treats them differently, the reversal moves).
  5. **Maersk**: EU fuel on base-only (not full)? country tolls additive per-parcel? Overpack on
     every parcel? ROW fuel handling (ORWO defers it).
  6. **Weight-band / as-of-join + oversize thresholds** if time.
- **Output:** a contradiction list (file:line both sides) — for each, EU-tender value/mechanic vs
  ORWO, and which is right. If ORWO contradicts the reference, fix ORWO + re-run + note the headline
  delta. If they agree, the −€265k/yr corrected verdict is reference-consistent (stronger to quote).
- **Caveat to hold:** EU-tender is Picanova (different contract/volume); some divergence is
  *legitimately ORWO-specific* (the dispatch confirms those). A contradiction is where the
  *mechanic* differs or a value ORWO claims to copy from Picanova doesn't actually match Picanova.

## NEXT CONCRETE STEP (after the sanity check)
1. **Niklavs to SEND the dispatch** - `carrier_questions/{GLS,Maersk}.md` (send-ready, unchanged this
   session; outward action, no channel wired here). The whole GLS stack now decides viability, not
   just A1/A2. Flip rows to RESOLVED as replies land; swap real % into the engine constants + re-run.
2. **Get each incumbent's real ORWO GRI%** (UPS/DHL) - the only incumbent-offer value is GRI-avoided,
   currently on a placeholder 5%.
3. Then: US/ROW-zone modeling, seasonal annualization (replace H1x2 + blended Season/BlackWeek with
   real monthly), confirm Maersk DE last-mile (B1) + GB clearance (B3) - GB-Maersk -EUR177k/yr leans
   on clearance folded into the Evri/Yodel door rate (assumption B3, Low-Med).

## FILES (corrected state)
- `repricing_base/carrier_engines/COMPARISON.md` - the corrected verdict doc (full-cost).
- `repricing_base/carrier_engines/{gls,maersk}/{constants,calculate,switch_compare}.py` - engines w/ stack.
- `repricing_base/carrier_engines/per_lane_optimum.py` - the -EUR265k/yr synthesis.
- `carrier_questions/{GLS,Maersk}.md` + `_provisional_assumptions.md` - dispatch + the locked provisionals.

## KEY NUMBERS (full-cost, H1; x2 ~ annual)
- Current full-cost all lanes: EUR 2.452M H1.
- GLS non-GB +EUR428k H1 (+EUR857k/yr); GB IC18 -EUR65k/yr. Maersk non-GB +EUR485k H1 (+EUR969k/yr); GB -EUR192k/yr.
- DE-domestic: GLS +EUR441k H1 (+22.5%); at 0% energy still +EUR92k H1.
- Per-lane optimum saving: -EUR132k H1 / -EUR265k/yr (GB Maersk + AT/CH GLS + tails).

## DECISIONS LOG (carried)
- Full-cost BOTH sides is the headline basis (Niklavs confirmed 2026-06-22) - freight-only and
  GLS-side-only both mislead (opposite directions).
- Ignore non-conveyable / DHL Sperrgut going forward (EUR307k excluded from current).
- Provisional assumptions adopted for the interim calc (see `_provisional_assumptions.md`).

## STILL OPEN (carried)
- The uninvoiced-carrier coverage gap (~600k Wolfen shipments / ~22% via 0%-invoice carriers:
  Deutsche Post, Bring, Cirro, PostNL...) - sibling resume `orwo-tender-resume__cb17c25e.md`;
  Niklavs to decide cost basis.
- Create the `orwo-tender` bank digest at next Jebrim alching (mart-weight-grain -> shipping-mart,
  rate cards -> carrier-contracts; add the full-cost-both-sides reversal as a method note).

## ANCHORS
NFE `projects/7_ORWO_tender_2026/`. Quest [[S283_60de5609_orwo-tender-assumptions-and-carrier-questions]];
prior [[S281_926f247a_orwo-carrier-engines-refactor-gls-maersk]]; umbrella
[[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain]]. MEMORY: competitor-reprice-carries-own-surcharges.

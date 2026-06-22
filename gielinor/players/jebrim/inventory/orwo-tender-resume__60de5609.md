---
quest: S283_60de5609_orwo-tender-assumptions-and-carrier-questions (continues S275/S281 ORWO arc; this increment worked under session ca27d9be)
sid8: 60de5609   # canonical rolling ORWO resume; last touched by session 2bf7cf70 (S285) 2026-06-22
ts: 2026-06-22 (S285 / 2bf7cf70)
open_dep: tender MODELING + assumptions COMPLETE; logic walkthrough DELIVERED (S285); US DISREGARDED by principal (drops US 1,855 H1 from scope, €0 optimum delta — headline unchanged at -EUR282k/yr). NEXT = ANNUALIZE PROPERLY per the EU-tender method (replace H1x2 with per-country seasonal re-weight + peak split), see block below. Carried-open (principal's): SEND dispatch (now confirmation); get real GRI%.
---

# ORWO Tender 2026 - resume

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

## >>> NEXT SESSION — START HERE: ANNUALIZE PROPERLY (per the EU-tender method)

**Task (Niklavs, 2026-06-22):** replace the crude **H1×2** annualization with the proper per-country
seasonal re-weight + peak split that the **EU tender** used. The −€282k/yr is H1×2 on provisional rates;
the EU tender built a defensible full-year bridge — mirror it for ORWO.

**The EU-tender method to copy** (anchor: `players/jebrim/research/2026-06-10-eu-tender-annualization-method-and-assumptions.md`,
"design locked with Niklavs"; built parallel to `2_EU_tender_2026/.../annual_2026/`):
1. **Base = the actual repriced book** (here: ORWO H1 parcels), NOT a ×N replay — current mix baked in.
2. **Volume → full-year per-country**: `FY ≈ H1_actual × (FY_2025_country / H1_2025_country)` — scale each
   destination by its OWN 2025 seasonal ratio, not one global factor (ORWO is cross-border-first, AT/GB/CH-heavy
   — their seasonal shapes differ). 2025 monthly FY-share in the EU tender: Q1 20.7/Q2 21.2/Q3 17.9/**Q4 40.2** (Dec 21.5).
3. **Cost = peak-free base × annual volume + peak rate × peak-window volume.** Split each lane's volume into
   peak (per carrier window) vs non-peak from the 2025 monthly shape. For ORWO that means deriving the GLS/Maersk
   peak (Season/BlackWeek — currently folded as the blended 0.417% annual-proxy) + each incumbent's real Q4 premium.
4. **Both sides identical 2026 basis**; `saving = FY_baseline − FY_portfolio`; peak fires both sides (largely cancels).
5. **Present as a band** (surcharge-rate sensitivity), not a point — esp. since GLS/Maersk rates are provisional.
6. Build the **Q1/H1→annual bridge waterfall** (the EU-tender centerpiece): anchor → volume scale → ±peak → ±band = annual.

ORWO data anchors for the re-weight: live mart (`shipping_mart.fact_shipments`, Wolfen, order-month) for the
2025 per-country monthly volume shape; the engines' peak-free unit cost is already in the matrices. Confirm whether
to mirror the EU-tender `annual_2026/` report shell or keep it a calc + COMPARISON.md update.

Source: this resume + `repricing_base/carrier_engines/{COMPARISON.md, per_lane_optimum.py}` +
the EU-tender annualization research file above + `2_EU_tender_2026/.../annual_2026/` as the template.

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

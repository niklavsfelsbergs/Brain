# S283 - ORWO tender: assumptions review + carrier-question dispatch

**sid8:** 60de5609 - 2026-06-22 - continues the ORWO arc (umbrella [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]]; prior session [[S281_926f247a_orwo-carrier-engines-refactor-gls-maersk|S281]]). Cue: "hey jebrim, remind me where we stand on orwo tender" -> deep-dive into point-1 + assumptions. Fresh `/clear` session (sid 60de5609, NOT 926f247a).

## Ask (Niklavs)
Where do we stand on ORWO. Then: explain point-1 (reprice bulky tail), interrogate the assumptions, prepare carrier-question files (one per carrier, confirm-same-as-Picanova where already answered), update docs + wrap up.

## Done this session
- **Where-we-stand readout** off the MONDAY HANDOVER (GLS primary ~-EUR509k/yr verdict as it then stood).
- **Point-1 (reprice bulky tail) investigated then DROPPED as immaterial.** Computed the whole ORWO packaging catalog (`ORWO Packages Real Dimensions.xlsx`, 46 types) against GLS/Maersk oversize thresholds: catalog tops out at **120cm longest / 135L volume** - under the GLS Overlength (>120) and Big-Parcel (>150L) triggers; only **one type (id-27 Wickelkarton 80x100, 111x83x7) trips a reject** (80cm mid-dim cap). Maersk absolute ceiling (175/200cm, 300 girth) also untripped. The catalog is the physical ceiling, so the ~73% packaging-join gap does not undermine this. ORWO is not a bulky shipper in carrier-oversize terms.
- **Niklavs correction: DHL Sperrgut = TOO THIN (non-conveyable), not oversize.** Reframed the EUR307k Sperrgut: the relevant analog is GLS **Non-conveyable EUR0.80/parcel** (confirmed on the ORWO card, "Additional price components"), ~18x cheaper than DHL's ~EUR14 Sperrgut. **DECISION (Niklavs): IGNORE non-conveyable** (one-off DHL situation, not carried forward) - logged as an explicit assumption.
- **LOAD-BEARING FINDING: the ORWO GLS engine OMITS GLS's own surcharge stack.** `carrier_engines/gls/constants.py` models only Toll National 0.38 + GB clearance - **no Energy / Dieselfloater / ClimateProtect** (the EU-tender GLS engine modeled them at 20.5% + 4.1% + 2.5%). Verified the GLS offer rates are **base** (PDF p.5: "base price ... refer to Additional price components for surcharges") and `switch_compare.py:8` is freight-only ("ex surcharge"). So the **-EUR509k headline OVERSTATES the GLS saving by ~25% on base and may flip the DE-domestic driver** (GLS ~25% stack vs DHL domestic ~7.5%). This overturns the prior "verdict is SAFE" claim in [[S281_926f247a_orwo-carrier-engines-refactor-gls-maersk|S281]].
- **Extracted ALL assumptions per carrier** (3 dwarves UPS/DHL/Maersk + own GLS read; 5 traces in `quest-log/traces/`). Picture: incumbent (UPS/DHL) "savings" are GRI-avoided on **placeholder 5% GRI** (DHL flat -> EUR0 without the real GRI%); GLS overstated (energy omitted); Maersk **no invoiced baseline** at all.
- **Built the carrier-question dispatch** (EU-tender `contract_engine_review_PLAYBOOK` pattern): NFE `carrier_questions/{GLS,Maersk}.md` - Section A = confirm-same-as-Picanova (GLS already answered the equivalent 15-Q set for Picanova; one answer named ORWO), Section B = ORWO-specific. Maersk card is the **shared Picanova_ORWO_Sendmoments** card so most terms carry. Plus `_provisional_assumptions.md` (compute-now values) + a pending-correction caveat banner on `COMPARISON.md`.

## Decisions (Niklavs)
- **Ignore non-conveyable / DHL Sperrgut** going forward (one-off DHL situation) - noted as assumption.
- Replicate the EU-tender carrier-question approach for GLS + Maersk; confirm-same-as-Picanova where already answered.
- Update docs + wrap up.

## Corrections / failure modes this session
- **Presented -EUR509k as "the verdict" before checking the GLS engine modeled GLS's own fuel.** Niklavs' "show me each assumption" push surfaced the energy/dieselfloater omission - a ~25% overstatement that the prior session's MONDAY HANDOVER called "SAFE". Verify-the-thing: the engine was never exercised for surcharge-completeness. -> examine draft + memory.
- **Relayed dwarf-supplied oversize thresholds (120/150/300) as fact** until Niklavs flagged they are not in the ORWO contract - traced provenance: GLS GTC SS4.2 + Picanova Q12/Q14 answers, not ORWO's contract. Same theme (assumption surfaced as verdict).
- **Wrong sid8 for most of the session** - operated as if continuing as 926f247a (the prior session); the require-open hook revealed the actual sid is 60de5609. Posted the late OPEN at the close gate (the recurring continuation-entry OPEN-skip; gate backstopped it).

## Verification
- Dims/oversize: computed the full 46-type catalog vs every GLS threshold (deterministic, from the dims file). GLS non-conveyable EUR0.80 + thresholds 120/150/300: read off the ORWO offer xlsx + EU-tender engine source (file:line cited in traces). GLS energy omission: confirmed against `gls/constants.py` (absent) + `switch_compare.py:8` (freight-only) + offer PDF p.5 (rates are base). The corrected GLS number is NOT yet computed - that is the next step (lock provisionals + re-run).

## Cascade
- **COMPARISON.md -EUR509k is now flagged PENDING CORRECTION** (energy/diesel omitted). Next session: lock the GLS provisionals (Energy 20.5% + Diesel 4.1% + Klima 2.5%, etc. per `_provisional_assumptions.md`) into `carrier_engines/gls/` + Maersk surcharges, re-run -> the corrected working number for the stakeholder meeting.
- Carrier-question files are ready to send; the two that decide the GLS verdict are GLS A1 (energy) + A2 (dieselfloater).
- The orwo-tender bank digest (still undigested per `bank/domains/_index.md`) should fold in the assumptions-register + the energy-omission lesson at next alching.

## Main-brain changes
- None to gielinor rules/rituals. Brain writes = this quest entry + resume__60de5609 (archives __926f247a) + 5 dwarf traces + 1 examine draft + comms OPEN/CLOSING.

## Open / next
- See `inventory/orwo-tender-resume__60de5609.md`. Tender modeling is NOT meeting-ready: the GLS -EUR509k omits GLS's fuel. Next concrete step = lock the provisional assumptions + re-run GLS (and Maersk surcharges) for the corrected number; send the carrier-question dispatch (`carrier_questions/`). Then US/ROW, seasonal annualization, present the corrected GLS recommendation. Parent [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]] stays in-progress (umbrella).

---

## Turn 2 (2026-06-22, session ca27d9be) — surcharge re-run; the verdict REVERSED

Picked up the S283-close next step: lock the provisional surcharges + re-run. Before building I verified the comparison basis — the reprice parquets carry incumbent surcharge SEPARATELY (`invoiced_fuel`/`invoiced_resi`, `invoiced_surcharge`), and `invoiced_freight` is genuinely freight-only. So the prior −€509k synthesis had leveled DHL's €143k into "current" by hand. **A fair re-run must fatten BOTH sides to full-cost** — fattening only GLS (the literal instruction) would invert the bias and report a false GLS loss. Sized it first: incumbent surcharges ~€198k H1 vs GLS stack ~€515k H1 → the swing flips GLS to worse. Niklavs confirmed full-cost-both-sides as the headline basis (multiple-choice).

### Built
- **GLS engine** (`carrier_engines/gls/{constants,calculate}.py`): Energy 20.5% + Klima 2.5% + Season(blended 0.417%) on base → Toll Intl 5.70% x-border / €0.38 national flat → Diesel 4.1% after toll → DE-private €0.15. Emits `gls_full_eur`.
- **Maersk engine**: EU fuel 6.6% on base + country tolls (AT 0.29/DE 0.19/DK 0.05) + Overpack €0.40. Emits `maersk_full_eur`.
- **Both `switch_compare.py`**: load_book carries incumbent surcharge (UPS fuel+resi; DHL surcharge ex Sperrgut) → `current_full`; both print freight-only AND full-cost.
- **New `per_lane_optimum.py`**: whole-lane cheapest-carrier synthesis (corrected the per-parcel `min_horizontal` cherry-pick to whole-lane assignment — the operationally-bookable number).

### Result — the −€509k saving is DEAD
- All-GLS single switch **+€792k/yr WORSE**; all-Maersk **+€777k/yr WORSE** on full-cost.
- DE-domestic core (548k) is the driver: GLS ~+43% (27% stack + ~€0.53/parcel flat toll+private) vs DHL's ACTUAL invoiced ~5.4%. **GLS loses DE-domestic even at 0% energy** (+€92k H1) — A1 sizes the loss but can't flip the core.
- Real saving = lane-specific **~−€265k/yr** (per-lane whole-lane optimum): keep DHL domestic, GB→Maersk −€177k/yr, AT→GLS −€56k/yr, CH→GLS −€18k/yr, EU tails.

### Cascade
- **COMPARISON.md REWRITTEN** (restructured, not bolted-on — the finding moved the decision line): pending banner → CORRECTED note; new full-cost headline + lane table; "primary switch is dead" reading.
- Dispatch `carrier_questions/{GLS,Maersk}.md` is send-ready and unchanged — the whole GLS stack (A1/A2/A3/A4/A7/A9) now decides viability, not just energy. **Sending is Niklavs' action** (outward, no channel wired).

### Verification
- 0%-energy break-even computed directly from the parquet (per-parcel, faithful to the surcharge order). GLS/DHL DE-domestic full-cost from the engine, not hand math. Incumbent surcharge magnitudes sized from the actual reprice parquets (UPS fuel 14% / DHL surcharge 7.5% of freight). Caveat carried: competitor side is MODELED-provisional, incumbent side is ACTUAL-invoiced — the reversal is conditional on the provisional %, which the dispatch confirms.

### Failure modes
- Late OPEN again (the recurring continuation-entry skip) — require-open gate caught it before the first brain write; posted as jebrim-ca27d9be.

### Open / next
- See `inventory/orwo-tender-resume__60de5609.md`. Tender is now meeting-ready as an HONEST story (primary switch dead; saving is GB-lever + select-EU ~−€265k/yr, pending carrier confirmation of the provisional surcharges). Next: Niklavs sends the dispatch; get incumbent GRI%; US/ROW + seasonal annualization. Parent [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]] stays in-progress.

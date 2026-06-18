# S211 · UPS savings + DB-Schenker zV→UPS reroute investigation

**Player:** Jebrim · **sid8:** dcd18cfd · **Born:** 2026-06-11 · **Type:** consultation/investigation (read-only over bi-analytics; brain writes only)

A multi-turn principal Q&A that started at "UPS is in the final report — how did savings change?" and drilled all the way down to the per-parcel economics of the DB-Schenker→UPS zV reroute. No bi-analytics writes. Settled finding written to bank draft [[2026-06-11-zv-dbschenker-ups-reroute-economics]].

## Turn log

- **T1 — how did savings change.** UPS engine raised annual saving (q09 basis, yardstick fixed) €1,442,782 → €1,908,707 = **+€465,925**, 100% plan-side. Firm €990,225 / DBS-contingent €918,482. Rate moves €483,133 unchanged (keep-side invariant). Grounded off `ups-cascade-resume__9399f067` + `carrier-overview-v2-rederive-resume__89e4a123`.
- **T2 — "hollow" + the GRI.** Corrected my own framing: the "5/7 hollow vs today" was the **GRI-free** carrier_overview bar; GRI'd-forward, FR flips to break-even, only CH/Nordics stay (tier/oversize, not GRI). Savings headline IS GRI-aware (routing applies +5% keep-side).
- **T3 — DBS-contingent 525→918.** First mis-explained as "yardstick rose." Principal pushed: UPS can't change the yardstick. Right — `98cdd49` (the snapshot I diffed) is **pre-q09**; the do-nothing rebasis + UPS landed together in `19bc826`, so my diff conflated them. Same-yardstick clean delta is €517,123 → €918,482.
- **T4 — pre-UPS snapshot.** Extracted `2_analysis/` from `98cdd49` → `~/Documents/eu-tender-pre-ups-snapshot-98cdd49/` (flagged pre-q09 basis).
- **T5 — the €862k he remembered.** Found in quest-log `S203_021047a4`: q09-no-UPS base €862,401 + module €602,049 (€1,464,449; never committed). His memory was right.
- **T6 — which parcels move DBS→UPS.** 2,585 parcels (committed plan); oversize/custom (1,062 zV + 995 CUSTOM_OVERSIZED + 508 mailers). Caught + bypassed the stale `move_population.parquet` (DBS→Hermes/0-UPS) via the authoritative `routing_assignment`⋈actuals join.
- **T7 — "how can zV fit UPS, L+G>325?"** zV L+G median 328 (max 340), longest 130 — fits UPS's 419/274 ceiling. 325 = our negotiated LPS band boundary, not the reject limit.
- **T8 — LPS pricing.** `cost_lps = incidence × amount`. Mis-claimed the 26% was a naive blend that "should be 100% / €310k under-charge" → **withdrawn**: it's a zV-cohort-specific empirical 0.2595 (band d_325_419), physically real because the box straddles the 325 trigger (coin-flip dimensioner). Cost is correctly modeled; [[S205_f08474c9_ups-round1-reply-review|S205]]'s "mistake" is operational, not a pricing bug.
- **T9 — UPS vs DBS cost.** DBS €66.65 (tender keep) vs UPS €37.84 (83% of which is the €31 expected LPS).
- **T10 — "why €48 in the mart?"** The big reconciliation. Mis-claimed the tender overstates DBS by ~€20 / contingent inflated → **withdrawn**. Truth: zV DBS cost is **bimodal** (DE €34 bulk vs EU-intl €60-72); €48 is the all-zV blend, the optimizer moves only the expensive EU-intl cells to UPS, whose real mart cost is **€76.38** — *higher* than the €66.65 keep_cost. No overstatement. Break-even LPS incidence ≈58% (robust, not the "~34% knife-edge" I'd said off the wrong blend).

## Decisions / outcomes

- Settled: zV→UPS saves ~€38/parcel and is robust to LPS incidence up to ~58%. The DBS baseline is not overstated. Cost model is correct.
- Open (Niklavs', carried from [[S208_9399f067_ups-cascade|S208]], not new): zV-on-UPS routing **policy** — accept the saving or exclude the 1,062 zV (≈41% of the move) on operational/packaging grounds ([[S205_f08474c9_ups-round1-reply-review|S205]]).

## Pending external actions

None pending. Read-only investigation; brain-only writes committed at close.

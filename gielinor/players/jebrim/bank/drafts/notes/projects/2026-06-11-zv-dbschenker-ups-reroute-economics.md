# zV → DB Schenker → UPS reroute economics (EU tender)

**As-of:** 2026-06-11. **Session:** [[S211_dcd18cfd_ups-savings-dbschenker-reroute-investigation|S211]] (dcd18cfd). **Player:** Jebrim. **Status:** draft (data-verified against committed routing + mart actuals; conclusions settled this session after two self-corrections).

Anchor for the question "UPS is in the final report — how did savings change, and is the DB-Schenker→UPS reroute real?" Sits next to [[2026-06-11-ups-oml-lps-negotiated-thresholds]] (the LPS/OML thresholds + the zV-on-UPS ruling) and [[2026-06-11-ups-cascade-new-canon]] (the headline savings).

## Headline: how UPS changed the savings (clean q09 basis, yardstick fixed)

- Annual saving **€1,442,782 ([[S203_021047a4_q09-baseline-bridge|S203]], no UPS) → €1,908,707 ([[S208_9399f067_ups-cascade|S208]], with UPS)** = **+€465,925**, 100% plan-side (cheaper routing; do-nothing baseline byte-identical both sides — do-nothing Q1 €3,055,317, rate moves €483,133 unchanged).
- DB-Schenker-contingent slice **€517,123 → €918,482** on that same q09 basis (the old committed `98cdd49` €525,360 is a pre-q09 vs-today number — not comparable; don't subtract it).
- **Yardstick caveat that burned two turns:** the committed pre-UPS commit `98cdd49` is *pre-q09* (vs-today basis, annual €997,719; base €420,218 + module €577,502). The q09 do-nothing/GRI rebasis + UPS landed in the *same* commit `19bc826`, so a naive `98cdd49`→HEAD diff conflates them. The q09-no-UPS intermediate (€1,442,782; base €862,401 + module €602,049) was **never committed** — it survives only in quest-log `S203_021047a4`. Pre-UPS report snapshot extracted to `~/Documents/eu-tender-pre-ups-snapshot-98cdd49/` (pre-q09 basis — flag when reading).

## The DB-Schenker → UPS move (committed plan, `routing_assignment.parquet`)

Of 10,713 DB-Schenker-origin Q1 parcels: **2,585 → UPS**, 4,077 → Hermes, 2,096 stay DBS, rest dhl_paket/maersk/unrouted. The UPS-bound set is **oversize/custom**: 1,062 zugeschnittene Verpackung (zV), 995 CUSTOM_OVERSIZED, 508 GEL mailers, 20 pallets. UPS Standard (2,541) / Express Saver (44). Countries: DE 765, FR 610, NL 350, IT 327, CH 139, tail.

**Stale-artifact trap:** `validation/db_schenker/move_population.parquet` (written 17:10) predates the [[S208_9399f067_ups-cascade|S208]] regen (`routing_assignment` 19:28) and shows DBS→Hermes/zero-UPS. It is stale — use `routing_assignment` joined to actuals incumbent (`shipping_provider_group=='DB SCHENKER'`) as authoritative.

## zV physically fits UPS — 325 is the surcharge boundary, not the reject limit

- UPS engine ceiling: **longest ≤ 274 cm, L+girth ≤ 419 cm** (`carriers/ups/constants.py:23-24`).
- The zV box: longest side **130 cm**, L+girth median **328 cm** (max 340; engine dims == actuals dims, no DQ understatement). Zero exceed 419 or 274. Flat-and-wide, not long.
- **325 cm is OUR negotiated LPS trigger** (`BILLABLE_LPS_BANDS` `d_325_419`), overriding UPS book >300/≤400. So zV clears eligibility but lands in the LPS band.

## The LPS is priced by incidence, not flat — and that's correct here

- `cost_lps = incidence × LPS amount`, per parcel (`calculate.py:398`; cohort rate coalesced over band fallback). **Not** "every zV pays the surcharge."
- zV cohort, band `d_325_419`: **p_lps = 0.2595**, €96.58/event (1,237 historical UPS ships). So each zV carries ~**€31 expected LPS** (0.26 × ~€120 incl. 40 kg min-bill bump), not €96.
- **The 26% is physically real, not a modeling shortcut:** this box is catalog-dim *threshold-straddling* (L+G 327.5–333.5 vs the 325 trigger) — UPS's dimensioner catches it on a coin flip (~50% in 2023-24, 26.7% in 2026; S199/[[2026-06-11-ups-oml-lps-negotiated-thresholds]]). BY-BILL prices what UPS actually charged. **The cost is correctly modeled** — an earlier "should be 100% / €310k under-charge" framing this session was wrong and withdrawn.

## Cost reconciliation — why the mart shows ~€48 but the tender uses €66.65

The numbers don't conflict; they're **different populations** (the trap that cost two self-corrections this session):

- **€48 = ALL DB-Schenker zV, blended across destinations.** Bimodal: DE €34 (the 4,924-parcel bulk), PL €21 — vs FR €72, NL €67, IT/AT/ES/BE €60-65. cost_source `invoice` (86%), real.
- The optimizer **only moves the expensive EU-international cells to UPS**; cheap DE → Hermes (€37) or stays DBS, PL stays DBS (`keep_wins`). So the moved-to-UPS subset's **real mart cost is €76.38** (FR €70, NL €66, IT €61, BE €59, CH €220, DK €95) — *higher* than the tender's keep_cost €66.65.
- **Therefore the tender does NOT overstate DB Schenker.** keep_cost €66.65 (q09 March-anchored forward mean, `build_final.py:158-159`) is slightly *below* the real €76.38. The €48-vs-€66.65 "gap" was an all-zV-blend vs moved-subset artifact. March is **not** a spike (€45.80 ≈ Q1) — the [[S203_021047a4_q09-baseline-bridge|S203]] March-mean-contamination flag does not apply to this slice.

## Per-parcel economics + robustness

| | per parcel |
|---|---|
| DB Schenker (real mart, moved subset) | **€76.38** (tender keep_cost €66.65) |
| UPS (engine, all-in) | **€37.84** — base €4.66 + fuel €0.93 + **LPS €31.24 (83%)** + line-haul €0.75 + rest €0.26 |
| **saving** | **~€38** (~€29 on the conservative tender basis) |

- **Break-even LPS incidence ≈ 58%** against real €76 DBS (`6.6 + p×120 = 76.38`). Above even the 2023-24 high of 50% → the zV→UPS saving is **robust**, not a knife-edge. (An earlier "~34% break-even / almost underwater" this session used the wrong €46.60 all-zV blend as the DBS baseline — withdrawn.)

## [[S205_f08474c9_ups-round1-reply-review|S205]] "routing mistake" — operational, not a pricing error

zV-on-UPS pencils out (saves ~€38/parcel). [[S205_f08474c9_ups-round1-reply-review|S205]]'s "mistake" ruling is **strategic/operational**: knowingly routing a box that coin-flips a ~€100 surcharge onto UPS is fragile and odd when the fix is **packaging** (get the box under 325 cm L+G) or keeping it on DBS. The engine carries the LPS cost correctly; the *routing choice* is the flagged item. Open policy call (Niklavs): accept the zV-on-UPS saving, or exclude the 1,062 zV by policy (≈41% of the DBS→UPS move).

## Verify-against (paths)

- `routing_2026q1/routing_assignment.parquet` (assigned family) ⋈ `data/actuals_2026q1.parquet` (`shipping_provider_group`, `real_total_eur`, `cost_source`).
- `routing_2026q1/cell_candidates.parquet` (`keep_cost` DBS vs `eng_cost` UPS per cell).
- `carriers/ups/{constants.py,calculate.py}` + `rate_tables/oversize_incidence_cohort.parquet` (zV band p_lps).
- `routing_2026q1/build_final.py:158-159,216` (keep_ref March-anchored forward mean).
- quest-log `S203_021047a4` (the never-committed q09 intermediate + base/module split).

# S148 — EU Tender 2026: DHL Paket + FedEx Round-2 reply review

**Session:** 104c786b · 2026-06-03 · Jebrim (principal)
**Continues:** the carrier-reply-review loop ([[S099_55ea7bc0_eu-tender-carrier-reply-review|S099]] / [[S102_6217a8d5_eu-tender-fedex-reply-review|S102]]). DHL Paket + FedEx were the two carriers HELD on old engines pending Round-2; both replies landed 2026-06-03.

## Ask
Niklavs: "second round of replies for dhl paket and fedex came in. Do you know what to do?" → confirmed the reply-review loop → "lets start with dhl and carry out the next steps and note what we still assume." So: full DHL Paket pass (review → rebuild → matrix → cascade), assumptions noted explicitly; FedEx reviewed-only this session.

## Reply locations
- DHL Paket: `carrier_responses_to_open_questions/DHL Paket + Deutsche Post/round_2/dhl_paket_2` (email, 8 Qs answered).
- FedEx: `carrier_responses_to_open_questions/fedex/round_2/` — `fedex_2` (covering email, 7 Qs), 2 fuel screenshots, `ODA_OPA_tiers_codes (1).xlsx` (67,514-row postcode→tier map, 116 countries).
- (First search found only fedex/round_2; flagged honestly rather than asserting DHL absent — Niklavs then dropped the DHL file in. Per never-assert-absence.)

## FedEx Round-2 — REVIEWED (rebuild deferred)
All Round-1 blockers closed by `fedex_2`:
- **RE volumetric divisor (#2, the hard blocker, ~€1.0–1.5M Q1): RESOLVED** — "All services have 5000 divisor" (RE + IEF/REF too).
- **Fuel scope (#1b): RESOLVED** — base + surcharges/VAS (wider base; engine must not apply fuel to base-only).
- **Two-index structure (#1a): CONFIRMED** — International index → IE (49.25% current week), Regional EU gas-oil → RE/REF (22.50%).
- **FX (#4/#12): RESOLVED** — billed in PLN, no carrier-side FX → our ECB conversion (4.234 interim) correct.
- **ODA/OPA remote-area list (#13): DELIVERED** (the xlsx).
- **Still open (not blockers):** fuel Q1-2026 monthly %s (self-serve, "Show all weeks"); customs per-parcel "Clearance Fees" amount (carrier didn't understand — needs a concrete rephrase). FedEx engine stays `fedex-1.0.0` HELD; rebuild is the next focused pass.

## DHL Paket Round-2 — REVIEWED + REBUILT `dhl_paket-2.0.0` (deterministic-ready)
The weakest Round-1 reply became the most-resolved.
- **Bulky axis (Q1, THE €2.31M Q1 lever): RESOLVED, engine CORRECT.** A 95×65×5 cm flat canvas *is* Sperrgut "because one side is 65 cm, which exceeds the 60 cm limit." Validates the any-side-over-60 sorted-dim trigger (`bulky_de.py`: `d_max>120 OR d_mid>60 OR d_min>60`). **€2.31M Q1 / €11.62M full-year Bulky is real, not proxy.** No code change — Round 2 confirms it.
- **Energy surcharge (Q2): CONFIRMED flat 1.25%** (full 01/2025–04/2026 schedule). `FUEL_PCT_DE_ENERGY` 2.5% proxy → 1.25%.
- **GoGreen Plus (Q5): opt-in** → engine €0 correct (kills +€48k).
- **CH customs (Q6): recipient-cleared** → no Picanova ZAZ, engine €0 correct (DHL Paket leg of cross-carrier ZAZ closed = ZAZ-independent).
- **Peak/PiP (Q7): dates confirmed** → PiP window assumed Nov 28–Dec 2 → Nov 24–Dec 7 (2025) / Nov 23–Dec 6 (2026).

### Engine changes (`dhl_paket-1.2.0 → dhl_paket-2.0.0`)
`constants.py`: `FUEL_PCT_DE_ENERGY` 0.025→0.0125; PiP window (11,28)/(12,2)→(11,24)/(12,7); version bump; Intl-TCS comment documents the per-country-€/kg finding + proxy retention. `tests/fixtures.py`: `_FUEL_DE` 0.025→0.0125 (+ docstring/comment sync). 20/20 fixtures pass. Bulky/GoGreen/CH = no code change (confirmed correct/€0).

### Downstream (all regenerated on the new engine, UNCOMMITTED)
- Full-year cost matrix re-run (`cost_matrix.py`, 12 monthly partitions, ~26M rows).
- `decision_scorer.py` (90 sets, do_nothing €0.00 PASS), `decision_report/report.py`, `cross_carrier_view.py`.

### Numbers
Full-year DHL Paket **€25.10M → €25.12M** (net **+€19.9k**: energy −€70.3k offset by PiP +€90k from the wider confirmed window). Bulky €11.62M unchanged. Decision sets effectively unchanged. **The value of the round is epistemic** — the €25.1M (incl. €11.62M Bulky) is now confirmed/defensible, not proxy-based.

## What we still assume (DHL Paket) — none block the Q1 number
1. **Thin-flat Sperrgut waiver — UPSIDE-ONLY.** ORWO <1cm calendars (possibly thin canvases) waiver in negotiation, pending Stefan. Engine prices full Bulky today; waiver can only reduce it. Revisit: Stefan's return / decision.
2. **Intl TCS modelled as 5%-of-base proxy, not the confirmed per-country €/kg.** Reply gave Q1 values for 12 named long-haul countries; others unspecified + materiality ~€600 Q1. Refine to per-country €/kg lookup only if precision needed.
3. **TCS 2025 monthly history** — not supplied (non-blocking; 01.01.2026 values cover Q1 2026).
4. **Volume re-pricing trigger % / tiers (Q8)** — deferred to Stefan (§B.15, non-blocking).

## Cascade (done this session)
REVIEW_CONCLUSIONS.md (Round-2 block + verdict flip) · ASSUMPTIONS.md (DHL section header + constants table) · OPEN_QUESTIONS.md (DHL header → resolved) · NEXT.md · PLAN.md §B.24 (`[ ]`→`[x]`) · DECISIONS.md (new 2026-06-03 top entry) · CROSS_CARRIER_OVERVIEW.md + FUEL_SUMMARY.md · technical engine docs (`carriers/dhl_paket/CLAUDE.md` + `docs/technical/engines/dhl_paket.md`).

## Brain side
**No pending external actions** (no sends/emails; the only "pending" was the close-session commit, made this close). bi-analytics-main edits committed pathspec-scoped at close (separate repo, NOT pushed); brain trace committed pathspec-scoped. Both repos: `git commit -- <pathspec>` ([[S131_0b0f2049_lived-operator-severity-audit|S131]] #1 hazard).

## Cascade.
DHL Paket §B.24 cascade run in-pass (7 docs + 2 engine docs + carrier REVIEW_CONCLUSIONS) — see the Cascade section above.

## Main-brain changes.
None — this is a player work session over the bi-analytics tender repo; no gielinor architecture/meta/ritual changes.

## Next
- FedEx rebuild (`fedex-2.0.0`): wire RE vol-weight=5000, two-index fuel (base+surcharges scope), FX=PLN/ECB, ODA/OPA tiers; pull fuel Q1-2026 %s self-serve; customs = documented assumption or a rephrased re-ask. Then re-run matrix + scorer + report.
- DHL Paket: only the thin-flat waiver outcome to fold in if/when Stefan confirms (upside-only).

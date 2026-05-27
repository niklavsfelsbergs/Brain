# S099 — EU Tender 2026: carrier Round-1 reply intake/review

**Session:** 55ea7bc0 · 2026-05-27 · Jebrim (principal)
**Goal:** Carriers have returned Round-1 replies. Per carrier, review the reply vs our dispatched open questions and judge whether we can now run a **deterministic** cost calc (every cost driver priced from a confirmed rule, no proxy). Bar from S034 bottom-line: clear ASSUMPTIONS on fuel/customs/residential, ≥5 of 7 engines off proxy.

Responses land in `bi-analytics-main/NFE/projects/2_EU_tender_2026/carrier_responses_to_open_questions/<carrier>/`. Principal feeds carriers one at a time.

## Turn log

- **T1–T3 (grounding).** Respawned as Jebrim; read keepsake (EU Tender pin + S034 bottom-line), `docs/NEXT.md`, `docs/` state, EU tender bank note. Posted OPEN to comms. Confirmed understanding. Principal: DPD PL sent but no reply yet (reply-waiting, out of scope this round). Principal: responses go in `carrier_responses_to_open_questions/`, starting with `Maersk/`.
- **T4 (Maersk review).** Read `Maersk/Maersk_EU.md` (14 answers), our dispatch `1_offers/picanova/Maersk/questions_for_carrier.md` (15 Qs + Round-1-closed table), `ASSUMPTIONS.md` Maersk block. Verified the two attached xlsx:
  - Diffed updated rate card (2026-05-27) vs offer (2026-05-07): **exactly 1 cell changed** = the Q13 ROW-oversize wording fix (`2xLxH < 169,901 CBM` → `2xLxH > 169,901 cubic centimetre`). No silent rate moves. ✓
  - `Remote Areas Fedex.xlsx` = 67,510-row Country/City remote-area lookup, Out-of-Pickup + Out-of-Delivery each tagged Tier A/B/No → this is the **Q12** answer (ROW Extended Area Service definitions). Data delivered. ✓
  - **NOT present in folder:** EU fuel monthly history (Q1, referenced "see history / my last email"), 2025 EU peak schedule (Q3, "sent in last email"), FedEx PL non-standard-parcel PDF (Q11, `new-offer-rates-vassuis-en-pl.pdf`). → chase from principal.

## Maersk reconciliation — 14 of 15 answered; Q1 fuel-history is the only real determinism gap

RESOLVED (engine-ready for Q1 replay):
- Q2 ROW fuel = 24.75% net (50% of 49.50% published) — lockable; index Air/Ground not explicit (minor).
- Q5 volume lock: 10% mix-delta = re-pricing trigger (methodology note).
- **Q6 oversize = CUMULATIVE** ("standard only if all criteria satisfied") → engine already cumulative, NO change. Retires the ~EUR 1.3M permissive-reading risk.
- **Q7 dims = SORTED** longest/mid/short → engine already sorts, NO change.
- Q8 oversize scalars: (a) BE/LU ColisPrivé 6.10 flat ✓; (c) IT GLS 2+2 stack, outside bands = reject ✓; (d) CH over-spec = reject (XL = separate pricey tariff) ✓; (b) ES PAACK pick-one-tier ✓ but trigger dimension not explicit (minor).
- **Q10 DE DHL Routing Code = exception only** ("incorrect postcode triggers by carrier, not Maersk") → engine zero CONFIRMED. Retires the ~EUR 137k always-on risk (S034 F5).
- Q12 ROW Extended Area Tier A/B → lookup file delivered (see above).
- Q13 ROW 4th oversize trigger → `2*L*H > 169,901 cm³` (corrected file). Wire-able.
- Q14 Liechtenstein = CH SwissPost rates identical (WA1 confirmed).
- (Round-1 already-closed: AT/DE/DK tolls always-on additive, ZAZ waives CH fee conditional on Picanova ZAZ, CH customs in-base, >30kg reject, AT handling exception.)

PARTIAL / non-blocking for Q1 determinism:
- **Q1 EU fuel — THE gap.** Scope confirmed (base only). Current = 6.6% + 2.4% Iran emergency (weekly-reviewed, waived when normal). But the **monthly Q1 2026 history** (Jan/Feb/Mar) that pins the replay is the "last email" attachment, NOT in folder. Fuel = biggest swing (±~EUR 24k Q1 / 1pp; engine currently 10% vs confirmed ~6.6–9%). Need history OR lock current 6.6% with Iran as documented scenario.
- Q3 EU peak (2025 proxy schedule) — attachment not in folder. Non-blocking for Q1 (PEAK_PCT=0 fine in Q1 EU); needed for Q4/full-year.
- Q4 ROW peak — window given (Oct 27–Jan 18) but no magnitude. Jan 1–18 touches Q1 for ROW (small; EUR 238k lane).
- Q9 remote-area "carrier-based; Spain only via Correos" — needs an interpretation call for ES (PAACK)/IT (GLS) Picanova lanes.
- Q11 ROW non-standard = "same as FedEx Poland definition" (shape-based; mart has no shape signal → likely document-and-skip). Need the FedEx PL PDF to confirm non-derivable.

NOT answered:
- Q15 Overpack future-state written confirmation — non-blocking (future-state narrative only; current 0.40 always-on already confirmed Round 1).

## Verdict (Maersk)

Maersk EU lane is **deterministic-ready for the Q1 2026 replay** once the `maersk-3.0.0` rebuild (PLAN §B.19) wires the confirmed constants. The two largest risk levers collapsed favourably (oversize cumulative; routing-code zero). The **single remaining proxy** is EU fuel monthly %, pending the history attachment — fuel is the biggest swing, so this is the one to chase before locking.

## Fuel ruling (principal, T4)

- **Maersk EU fuel locked at 6.6% base-only** for the Q1 deterministic calc (drop the old 10% proxy). Iran 2.4% emergency NOT in the locked point estimate.
- **Maersk to also be simulated across a fuel-rate sensitivity band** (not a single point) — fuel is the biggest swing lever and currently volatile.
- **Cross-carrier methodology caveat (principal):** fuel currently varies a lot; treat fuel as a sensitivity dimension, not a point estimate, when drawing tender conclusions — and it varies more for some carriers than others. → belongs in `REPORT_NOTES.md` + a harvest candidate for a bank note at session close (NOT drafted mid-quest per harvest-after-stabilize discipline).

## Hermes review (T5–T7) — 10/10 answered; vol-weight + residential resolved hugely favourable; fuel has a two-ladder problem

Source: Outlook paste `hermes` (tables linearized but lossless) → cleaned to `hermes_response_CLEANED.md` (original preserved). Dispatch = 10 Qs (`1_offers/picanova/Hermes/questions_for_carrier.md`). Two answers defer to `202511_Country Details_EN.pdf` (17pp, read).

RESOLVED — favourable, engine already correct:
- **Q1 weight basis = EXCLUSIVELY GROSS WEIGHT.** No vol-weight rule → engine correct. **Retires the ~EUR 0.5–1.5M Q1 "uplift" risk** and the chief suspect behind the 0.588 "too-good-to-be-true" bias ratio. Hermes really does bill gross → its favourable ranking largely HOLDS (not a vol-weight artifact).
- **Q10 residential = all-in, private = commercial.** Residential uplift = 0 confirmed (clears an S034 cost-driver for Hermes).
- Q5 intl returns = recipient-local parcelshop only (returns OOS reading confirmed).
- Q9 toll EUR 0.20 contractually fixed for 2026 (engine MAUT_EUR=0.20 confirmed).

RESOLVED — data delivered, engine rebuild (`hermes-2.0.0`) needed:
- **Q2 intl bulky per-country values** (corrects a ratecard error; real values much bigger than the slide-4 "5.29–15.00": AT 5.29, ES/PT 15.75, CH 29.16, DK/FI/SE 26.25, IT 36.75, PL 66.72, **NL 92.35**, most others 57.75; CY/MT n/a). Wire `BULKY_INTL_EUR` lookup.
- **Q3 bulky trigger** (Country Details p2): standard doorstep = L≤120/W≤60/H≤60 & girth≤300, 30kg (all must hold; girth=L+2W+2H); **bulky = longest side >120cm ≤170cm & girth≤360**. Dimension-based (not shape) → derivable from mart dims → wireable. Picanova posters/canvases >120cm longest now priced at the (large) intl bulky rates → material recompute on intl, but deterministic.
- Q4 intl limits: **30kg cap confirmed** (engine MAX_WEIGHT_INTL=30 correct; CZ parcelshop 15kg OOS). Tighten MAX_LENGTH 200→170 (bulky ceiling); 450L volume proxy not in the EU product def (dim/girth-based) — minor, few edge parcels.

PARTIAL — the real gaps:
- **Q6 fuel — TWO different Destatis ladders now on file.** Scope confirmed (base only, not toll/bulky/peak). **Offer slide-8 ladder** (in engine `diesel_schedule.parquet`): 0% band up to index **155.3**; offer-issue "Mar 2026 = 154.9 → 0%". **Reply ladder**: 0% band only up to **122.7**; "Jan 2026 = 122.3 = €1.424/L → 0%" (internally consistent on base-2021). Different base years → can't mix. Jan = 0% confirmed; diesel was stable early-2026 so Q1 ≈ 0% (engine's net 0% likely right), BUT the basis is wrong and both ladders must be reconciled to one (recommend the reply's base-2021 ladder) + get Feb (carrier pending) + March on that same series. Magnitude small (~EUR 26k/pp) but exactly the "handle fuel carefully" case.
- Q7 volume tier: rates are volume/structure-conditional; bonus/penalty thresholds set at contract. No tier breakpoints given (cross-carrier §B.15 item, non-blocking).
- Q8 sub-country/island: **single per-country rate confirmed, no sub-zones / no non-deliverable lists** (good for determinism); only an "Island Delivery Surcharge EU 8.00" line, which reads as an optional service Picanova doesn't book → engine 0 likely correct (confirm auto-vs-opt-in with principal).

## Hermes verdict
Deterministic-ready for Q1 once `hermes-2.0.0` wires bulky (trigger + per-country values). The two biggest levers resolved favourably (gross-weight, residential=0), so the engine wasn't under-pricing on weight — the strong Hermes ranking largely survives; only bulky tightens it. Fuel is ~0% for Q1 but the two-ladder basis must be cleaned up (principal's fuel-caution, in miniature). Bulky-on-intl is the one number that will move (upward) on rebuild.

## DHL Express review (T9) — 11/11 answered; customs risk collapsed favourably, but Demand Surcharge bleeds into Q1

Source: `DHL Express_Picanova_q&a.pdf` (11 A) + `DHL_Express_Remote_Area_Surcharge_locations_2026.xlsx` (108k rows). Conclusions → `DHL_express/REVIEW_CONCLUSIONS.md`.

Headline finding (Q9): **Demand Surcharge 2025 window = 01.10.2025–16.02.2026 → overlaps Q1 2026 replay (Jan1–Feb16, ~47/90 days).** Engine PEAK_PCT=0 under-prices that slice. Dispatch wrongly assumed Demand was Q4-only. Need magnitude (carrier gave a link).

Favourable: **Q7 customs = no clearance charge → CUSTOMS_FLAT=0 correct, retires ~EUR 100k CH risk** (only DTP 2%/min5€ if Picanova picks that incoterm — confirm); Q6 oversize 10€ confirmed; Q8 PLT no fee; Q10 Emergency suspended since 2024 = 0.

Data delivered (rebuild): Q1 TDI air **~30%** (proxy 45% too HIGH); Q2 DDI road **~18%** (proxy 12% too LOW — road=86% bulk → cost rises ~30-40k Q1); Q3 fuel scope = base+listed transport surcharges; Q4 remote-area list (108k); Q5 non-conveyable weight 25-70kg(12/20€)+shape, excl. with OSP (shape un-wireable, no mart signal); Q11 pickup 1 van+1 truck/day billed separately → per-parcel line-haul alloc (+~0.5-0.9€/parcel).

Net: DHL Express cost moves **UP** on rebuild (road fuel +6pp, pickup alloc, Demand Jan1-Feb16) → **less** favourable than current under-priced engine. Fuel proxies were wrong in OPPOSITE directions (air over, road under) — principal's fuel-caution in evidence again.

## DHL Paket review (T10) — weakest reply; NOT deterministic-ready

Source: `DHL_paket` (email, rep Stefan, on vacation) + DPI country PDF + Schweiz.pdf (image slide). Conclusions → `DHL Paket + Deutsche Post/REVIEW_CONCLUSIONS.md`.

Headline: **the single biggest lever — Bulky ~EUR 2.31M Q1 — is UNRESOLVED.** Q1 axis interpretation dodged ("sizes are strictly"); Q2 hard-vs-manual gate not answered, but a live signal: Stefan is negotiating a **thin-flat (<1cm) Sperrgut waiver for ORWO calendars** → default charges thin flats (engine right), waiver pending. Until pinned, DHL Paket's dominant cost component is uncertain by up to 2.31M.

Favourable (locked): **Q9 Stettin pickup included → retires ~EUR 0.78M hidden-line-haul risk**; **Q11 routing-code exception-only → retires ~EUR 254k**; Q12 heavy-label auto=0; Q8 toll 0.19 locked; Q10 bulky country list delivered (DPI PDF).

Open/deferred: Q3 Energy monthly history NOT supplied ("see invoices" → self-serve); Q5 TCS + Q6 named-fuel MISUNDERSTOOD by rep; Q13 GoGreen Plus reads mandatory ("calculated for you", Nadine) → possible +EUR 48k; Q14 CH customs DEFERRED (Leif/Andrea; Schweiz.pdf = image, Gerlach broker). Needs Round 2 / a call (rep flagged "next meeting").

Contrast: Maersk/Hermes/DHL-Express mostly cleared; DHL Paket does not — biggest lever open + fuel must be reconstructed from invoices.

## Overview + NEXT.md (T19)
Principal: NEXT.md IS mine to edit (overrode the bank-note "never auto-write docs/*" for the handoff file). Built `carrier_responses_to_open_questions/CROSS_CARRIER_OVERVIEW.md` (5-carrier readiness table + per-carrier settled/open + outstanding + cross-themes) and rewrote `2_analysis/docs/NEXT.md` to current state (reply-review phase, the reframe, follow-ups, pending DPD PL/GLS/Güll/FedEx + UPS-no-offer). Recommendation given: while waiting, principal sends DHL Paket Round-2 + small confirmations; review remaining carriers as they land; full-year = later phase.

## GOAL REFRAME — full-year, not Q1 (T18)
Principal reframed: the decision basis is **full-year cost**, not cheapest-in-Q1. Q1 2026 = recent-cost reference / per-shipment unit-cost engine; full-year = that × annual volume profile + seasonal surcharges (peak/demand) + forward fuel + volume-tier effects. Key insight: Q4 dominates (Picanova calendars/canvases/gifts = volume + surcharge + mix-shift peak), and the peak surcharges we kept deferring as "zero in Q1" are exactly what differentiate carriers over a year (AP no-peak = hidden edge; DHL Paket peak+peak-in-peak; Hermes/FedEx/DHL-Express demand). Principal: **proceed on Q1 now, defer the annualisation method, park the idea.** Parked: `carrier_responses_to_open_questions/FULL_YEAR_SCOPING_NOTE.md` (tender) + keepsake proposal (brain, surfaces next Jebrim respawn) + offered a docs/NEXT.md pointer line. Annualisation options (deferred): (1) replay 2025 actuals on 2026 cards [rec], (2) Q1 unit-cost × monthly weights, (3) forward 2026 forecast.

## Fuel summary saved (T17)
Principal: save per-carrier fuel knowledge (we'll model where fuel stabilises later). Wrote `carrier_responses_to_open_questions/FUEL_SUMMARY.md` — per-carrier index/source/scope/Q1-value/current-spike/pre-spike-baseline/engine-constant table + the Iran-spike cross-cutting story + low/mid/high sensitivity framing anchored on pre-spike baselines. Coverage answer to principal: info-or-clear-path for ALL questions on Maersk/Hermes/DHL-Express/AP; DHL Paket is the exception (Bulky €2.31M + others open → Round-2 drafted).

## Principal pulled the FedEx figures → Maersk ROW RESOLVED (T16)
Principal opened the FedEx PL International-FSC table (screenshot: **49.50%**, 25–31 May 2026, USGC $4.152) + saved the two VASS/demand PDFs into the Maersk folder. This **flips the earlier "doesn't reconcile" verdict**:
- **ROW fuel RECONCILES:** 49.50% IS the live FedEx International FSC; ROW lane = International/USGC-jet index (NOT Regional ~19%). VASS confirms "International FSC except Regional Economy." Maersk's ×50% → 24.75% is the current-spike net; for Q1 use Jan–Mar weekly International FSC ×50% (lower; pull "Show all weeks"). The dwarf's Regional-vs-International ambiguity is settled toward International.
- **AHS/Oversize defs confirmed** (VASS): AHS-Dim >121/>76/>266 L+girth/>169,901 cm³ (matches Q13 fix), +18kg min billable; Pkg; Weight >25kg; highest applies. Oversize >243/>330/>283,168cm³/>50kg. Use Maersk EUR rates.
- **Extended Area tiers** (VASS): A PLN15, B 2.60/kg(min105), **C 3.35/kg(min135)** — Maersk's sheet omits C (confirm). Maersk EUR ≈ PLN÷4.3.
- **Demand Surcharge full schedule** (demand PDF): Europe→RoW €0.40/kg (Jan1–Feb15) → SUSPENDED (Feb16–Mar4) → €0.70 (Mar5–31); APAC/China €0.40→susp→€1.00. Time+zone varying in Q1 — engine ROW peak=0 wrong. Confirm Maersk passes FedEx demand through.
All folded into Maersk REVIEW_CONCLUSIONS web block. (Tried to rm my 5 `_*.txt` PDF-extraction dumps from the response folders; brain delete-hook blocks `rm` from any brain session even for the external bi-analytics repo → flagged for manual cleanup, not bypassed.)

## Curl-dwarf result (T15) — partial; hard WAF wall confirmed
Dwarf D1 (S099_d1): browser-headed curl on all FedEx URLs → identical domain-wide WAF "System Down" stub (not a UA filter). Pivoted to **web.archive.org** → fetched dated FedEx PL **Regional FSC ≈18.5–19%** + **Domestic PL FSC ≈19–19.5%** (Jan–Mar 2026). International FSC weekly % = JS-rendered from a WAF-gated AEM endpoint → unreachable by machine. PLN VASS amounts + demand schedule = WAF-blocked + no Wayback snapshot → unreachable.
**Verdict: 49.50% reconciles with NO fetched FedEx public rate** → it's a Maersk-internal commercial figure. Real lever = which fuel index the ROW lane uses: Regional/EU-diesel ~19% (→50%off ≈9.5%) vs International/jet ~40% (→≈20%) — big ROW swing. **Push back to Maersk: name the service + cite the table.** Folded into Maersk conclusions. Residual figures need a human browser or Maersk's source PDF — documented hard wall, not worth re-attempting by agent. (Dwarf temp dumps in /tmp/fedex-d1, outside the brain.)

## Curl-dwarf for the FedEx bot-wall (T15) — PENDING
Penguin P2 hit a FedEx-domain bot-gate (WebFetch blocked). Spawned 1 dwarf with Bash/curl (browser UA + pl-PL headers) to pull: exact Q1 2026 FedEx PL International fuel surcharge % (resolve 49.50% vs public ~37–43%) + PLN VASS handling/ODA-OPA amounts (gated PDF). Reads P2's research file for candidate URLs first. Findings → S099_d1 quest-log; fold into Maersk conclusions on return.

## Penguin results folded in (T14)
3 penguins returned; research in jebrim/research/ + sibling quest-logs S099_p1/p2/p3. Folded into the 4 conclusions files' open-Q blocks:
- **Hermes Q6 RESOLVED:** reply ladder = current base-2021 (offer's 0%≤155.3 was retired 2015-base) → use reply ladder. Destatis index Jan ≈122.5→0%, Feb ≈123.6→~0.5%, **Mar ≈151→~11% (Iran diesel spike)**. CORRECTION: Q1 fuel NOT ~0% — March material. Pin Feb/Mar exact from GENESIS 61241.
- **AP Q3 (FX) RESOLVED:** "1.06/1.09" = EUR-per-CHF (reciprocal), billed prior-month avg; ECB Jan 1.0784/Feb 1.0940/Mar 1.0996; uplift +1.1–3.7%. AP's AT-diesel D-card still not public (request); DSV basis confirmed (monthly→weekly 2026-03-16), exact % gated.
- **DHL Express Q9 (Demand) values FOUND:** Dom TD €0.10/kg, Intl DD €0.15/kg, Intl TD zone matrix €0.10–1.90/kg (EU→Americas €0.50); window overlaps Q1 → wireable. Confirm zone mapping + Jan-Feb values held (page current-only).
- **Maersk ROW NEW finding:** FedEx PL public International FSC ~37–43% ≠ the 49.50%/24.75% Maersk quoted → push back to Maersk. ROW peak €0.10–0.15/kg (Dec–Feb leg touches Q1) + non-standard definition found. Exact Q1 fuel % + PLN amounts gated (FedEx bot-wall; need human/curl or a dwarf with Bash).

Cross-carrier theme: **March 2026 diesel spike (Iran)** lifts fuel for everyone — validates the principal's fuel-as-sensitivity rule. The FedEx bot-wall is the one place web hit a limit (a dwarf-with-curl could pull the gated PDFs).

## Round-2 dispatch + web-research triage (T13)
- DHL Paket Round-2 dispatch saved: `1_offers/picanova/DHL Paket + Deutsche Post/questions_for_carrier_round2.md` (8 Qs, send-ready + internal mapping). Principal: "that's all" for re-asks beyond DHL Paket — but I flagged DHL Express (Demand Surcharge values, blocking) + Maersk (missing referenced attachments) still warrant carrier follow-up; AP carrier-complete, Hermes minor.
- Web-answerable triage: Hermes fuel (Destatis), Maersk ROW (FedEx Poland public), AP trio (bmwet/ECB/DSV), DHL Express Demand (DHL public link).
- **PENDING — spawned 3 penguins** (foreground) to pull the public data:
  - P1 → `research/2026-05-27-hermes-destatis-diesel-index.md` (Hermes fuel + 2-ladder reconcile)
  - P2 → `research/2026-05-27-maersk-row-fedex-poland-surcharges.md` (Maersk ROW)
  - P3 → `research/2026-05-27-austrian-post-public-indices-and-dhl-express-demand.md` (AT trio + DHL Express Demand)
  Fold confirmed figures into each carrier's REVIEW_CONCLUSIONS.md on return.

## Open-questions header added to all 4 prior files (T11)
Principal: put "what remains open" at the top of each conclusions file. Added `## ⏳ Open questions remaining` block atop Maersk / Hermes / DHL Express / DHL Paket conclusions. Convention extended to AP.

## Austrian Post review (T12) — strong reply, 12/12, deterministic-ready

Source: `Austrian_post` (email, 12 answers). Conclusions → `Austrian Post/REVIEW_CONCLUSIONS.md`.

Favourable: **Q2 gross-weight-only** (retires dim-weight risk on canvases/posters); **Q9 Stettin→CH Hohenems available** at Stettin→Salzburg price (replaces Wolfen proxy); Q5 no peak; Q7 round-up; Q8 Off-Limit=0; Q4 tubes ≤100cm standard / >100cm Sperrgut groß. **Q12 resolves cross-carrier ZAZ:** AP customs fee 1.00€ applies REGARDLESS of ZAZ (vs Maersk waives); AP brokers CH lane; import VAT 8% not refunded.

Self-serve monthly series (public, none blocking, Q1≈known): Q1 AT fuel bmwet.gv.at (Q1≈4%, **currently 12% Iran** — same spike as Maersk); Q3 CH FX (EUR prices @1.06 ref, billed prior-month avg, **now 1.09 ≈ +2.8% CH**); Q6 Maut 0.27→0.29 transition in Q1; Q11 trucking diesel = DSV floating index (not AT D-table).

Main genuine open = **Q10 parcels-per-pallet density — INTERNAL (Picanova ops), not carrier** — the line-haul allocation denominator (~0.75–4.50€/parcel).

5 carriers reviewed (Maersk, Hermes, DHL Express, DHL Paket, AP). Pending replies: DPD PL (sent, no reply), GLS, Güll, FedEx; UPS no offer yet.

## Conclusions persisted (T8)

Principal: save per-carrier conclusions alongside the responses so they survive. Written:
- `carrier_responses_to_open_questions/Maersk/REVIEW_CONCLUSIONS.md`
- `carrier_responses_to_open_questions/Hermes/REVIEW_CONCLUSIONS.md`

Each = per-Q resolution table + verdict + verified-attachment notes + fuel ruling/finding + chase list + engine to-dos. These are the source for the eventual `docs/*` Step-8 cascade (not yet run — docs/ is confirm-before-write). **Convention going forward: every carrier folder gets a `REVIEW_CONCLUSIONS.md` as it's reviewed.**

## Next concrete step

- Chase 3 attachments from principal (fuel history, 2025 peak schedule, FedEx PL non-standard PDF).
- Decide fuel handling: history-driven monthly lookup vs lock current 6.6% + Iran scenario.
- On principal go: flip Maersk `questions_for_carrier.md` status rows to RESOLVED + run Step-8 cascade (DECISIONS/ASSUMPTIONS/PLAN §B.19 ungate/OPEN_QUESTIONS).
- Then next carrier in `carrier_responses_to_open_questions/`.

## WRAP (T20) — session wrapped up
Docs cascade done via 3 dwarves — status tables (Maersk 9R/5P/1O, Hermes 8R/2P, DHL-Express 10R/1P, AP 11R/1P, DHL Paket 6R/3P/7-round2); ASSUMPTIONS all 5 blocks → confirmed values (old proxies superseded in place); DECISIONS +2 entries (reply-review + goal-reframe); OPEN_QUESTIONS ZAZ 3-leg resolved; PLAN §B.7/19/22/23 ready, §B.24 HELD; REPORT_NOTES fuel + full-year. **Tender repo committed 74dabe3** (main, 42 files +3065/-455, NOT pushed; bundled prior engine/report WIP per principal "everything in subtree"; excluded 10 scratch _*.py/_*.txt — delete-hook blocked rm so left untracked). Memory saved: `feedback_eu_tender_track_doc_updates`. Inventory resume + comms CLOSING + mode marker wrapped_up written. Next-session rec: rebuild the 4 ready engines + re-run the Q1 cost matrix. **Brain repo left uncommitted — awaiting principal go (global pref: always ask before committing; only the tender repo was authorized).**

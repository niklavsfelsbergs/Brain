# S196 — EU tender: result investigation (final-report Q&A)

- Session: 5733cb1d, 2026-06-11. Actor: Jebrim.
- Context: Niklavs reviews the final report (final_report.html, base/module structure) and asks
  investigation questions. All answers accumulate in NEW bi-analytics folder
  `2_analysis/result_investigation/` (script + findings note per question) for an end review.
- Siblings at open: b2e97698 (jebrim hygiene pass, live), e6e7b78d (braindead). 907d4e63 closed 09:40.

## Turns

- T1 (Q01: "192k parcels UPS→DPD PL — what are they actually?"): traced the figure to
  final_stats.json flows (192,517 ann = 39,780 Q1, €47,611/yr). Built result_investigation/
  (README + q01 script + findings). Profile: DE 82%/FR 15%, UPS04STD today → dpd_direct_home
  99.6%, standard flat prints (ORWO_80x60 + Wickelverpackung + Stanzverpackung = 88%), median
  3.0kg / 91×63×4.5cm — nothing oversize. Economics: thin (avg €5.54→€5.30); priced by
  dpd_pl_current engine (new offer priced 1 parcel); vs UPS-2026 bid (actuals ×1.05) saves
  €20.6k Q1 vs €9.6k vs today — half the flow is GRI-avoidance; 77% of parcels individually
  negative vs today (cell-level routing). Observed unexplained small rcost uplift over
  dpd_pl_current (median +0.33%, immaterial <€700 flow-level) — not chased.
- T2 (Q01b: threshold to de-risk the marginal swap): principal clarified questions close by ROUND,
  not single answer. Simulated a cell-level (dest×packagetype) switch threshold on the flow.
  Key accounting: staying on UPS pays the 2026 bid (×1.05 GRI; ups→ups books −€108.7k), so headline
  cost of keeping a cell = its saving vs UPS-2026 (flow total €101.1k ann, not the €47.6k vs-today).
  Sensitivity: 5% threshold keeps 102k/192.5k (53%) on UPS for €17.9k/yr headline; if GRI never
  lands the threshold portfolio is €8.6k BETTER. 4 DE bulk cells dominate (3 of 4 negative/breakeven
  vs today). Recommended 5% as nearly-free de-risking. Findings appended to q01 findings §Q01b.
- T3 (Q01 CLOSED — principal's conclusion recorded in findings): 22k–192k to DPD PL is our choice
  (threshold dial, €0–47.6k/yr vs modelled GRI; conservative end better if no GRI) → logistics
  manager's call. Re-decide once DPD PL's new offer is final: it's +18.8% pricier ([[S170_be1b4946_eu-tender-carrier-substitution-deltas|S170]]), so if
  signed near draft these cells don't move to DPD at all. Flow presumes current-contract rates.
- T4 (Q02: UPS→Maersk 164,769 ann / 40,396 Q1): OPPOSITE of Q01. IT 57% + ES 38%, small/light
  (median 1.14kg, 65×41×5cm, top type W60x40), eu_hd offer engine 96.5%. Saving real: −17.1% avg
  (€216.8k/yr vs today = 22% of headline; €279.8k vs UPS-2026); only 22% of parcels individually
  negative. Threshold barely bites: 5% keeps only 2.2% on UPS; keeping half costs €76.5k/yr. Risk
  axis = counterparty/model (offer-based new partner, no invoice reconciliation, Maersk EU fuel
  band open) not operational swap. q02 script + findings written; conclusion pending principal.
- T5 (Q02 CLOSED): principal conclusion "maersk makes sense" — recorded in q02 findings. Genuine
  price gap, move stands; residual risk managed contractually, not by routing less volume.
- T6 (Q03: UPS→DHL Paket 72,675 ann / 11,600 Q1, €126,468/yr): the SWITZERLAND flow — CH 82% +
  AU 13%, lightest of the three (median 0.57kg, pizza boxes/Teppichkarton/posters). BIMODAL:
  Warenpost intl (4.1k Q1 parcels) saves −40..50% = €19.2k of €21.8k Q1; paket_intl_economy
  (6.5k parcels) near-breakeven (GRI-avoidance). Two CH pizza-box cells = €81k/yr of €126k.
  Threshold: 5% parks 16% for €4.1k/yr; 7.5% cliff costs €24k (real 6-7% cells cross). DHL =
  invoice-reconciled incumbent → low counterparty risk; ops notes (warenpost limits, CH customs
  process, AU transit time not priced). Findings written; conclusion pending principal.
- T7 (Q03b: CH deep-dive — trust check): grounded in engine CLAUDE.md + offer CLAUDE.md +
  ASSUMPTIONS/DECISIONS. CUSTOMS = like-for-like, checked both sides: UPS movers carry €5 total
  real customs (Picanova own CH VAT/customs account, D11) and DHL Round-2 Q6 confirmed
  recipient-cleared/no-ZAZ → engine €0 correct. Saving drivers real: Warenpost ~−48% on sub-1kg
  + DHL 0% fuel CH (Z1) vs UPS 11.6%. HONEST GAPS: CH lane has NO DHL invoice history (CH today
  = 98.6% UPS; 4 DHL parcels) → offer-trust like Maersk, the "confirmed" tier label is weak for
  this lane (engine doc: Q1 parity vs actuals never run); Warenpost Std = basic-tracking goods
  mail, service level for CH B2C needs ops sign-off. AU still to do; conclusion pending.
- T8 (CH conclusion recorded: "CH ships with DHL Paket — clear", residual = ops sign-off on
  Warenpost Std + Q1 invoice audit). Q03c AU deep-dive: AU today 100% UPS (Std avg €30.65 +
  WWECON €17.27); tender splits AU 3 ways (1,489 DHL / 1,068 Maersk row_hd / rest stays).
  DHL prices AU via NAMED-country keys: warenpost_premium 933 @ €9.72 vs WWECON €15.93 (−39%),
  paket_intl_premium 556 @ €25.43 vs Std €28.18 (−10%). Customs like-for-like EMPIRICALLY:
  UPS AU invoiced customs = €0 (AU LVIG GST collected at point of sale) → offer gap #15
  (AU customs unmodeled) is a non-issue. Caveats: zero DHL AU history (offer-trust), Warenpost
  goods-mail to AU = amplified service-level question (63% of AU movers), residual paket gap
  only −10% if ops rejects warenpost. AU slice ≈ €6.6k Q1 / ~€30k yr. Conclusion pending.
- T9 (Q03/AU CLOSED): principal conclusion — AU savings small, open decision whether to use DHL
  for AU at all; treat the AU-on-DHL assignment as optional, not banked. Recorded in q03c.
  Q03 round (DHL Paket flow: profile + threshold + CH + AU) now fully closed.
- T10 (Q04: Maersk→DPD PL 67,608 ann / 13,287 Q1, €20,164/yr): 100% FR / 100% MAERSKFR carrier-only
  → dpd_direct_home, light (med 0.9kg). Maersk engine prices 0 of them → stay-bid = actuals (no
  GRI); both sides solid, trust not the issue. TWIST: ~half the flow is zero-to-negative (Poster
  40cm cell −€5.3k/yr, Pizza 20x20 −€2.5k/yr) — moved only for one-carrier-per-cell consolidation
  (cells shared with strongly-positive UPS-origin parcels). Headline €20.2k = net +€28k/−€7.8k.
  A 1-10% per-slice threshold parks ~46% on Maersk and IMPROVES the plan +€7.4k/yr; cost = cells
  permanently split by origin. Findings written; conclusion pending.
- T11 (GRAIN CORRECTION — principal caught it): I asserted cell = dest×packagetype from an [[S192_384c1c27_db-schenker-reroute-package-dims|S192]]
  memory; build_final.py says CELL = dest×packagetype×wkg (1-kg floor band, std packagetypes;
  variable per-parcel by dims; keep-candidate = DOMINANT incumbent only; std rcost = cell MEAN —
  resolves the Q01 +0.33% uplift loose end). Re-ran Q01b+Q04 thresholds at true grain (q04b):
  UPS→DPD 1% parks 25% for €1.1k/yr (coarse said 0.1%); 5% parks 41% for €7.1k (was 53%/€17.9k).
  Maersk→DPD: 1% parks 45% for +€8.1k GAIN. Corrections appended into q01/q04 findings + README.
  Lesson: verify-routing-against-the-table-not-domain-logic recurrence — quoted a comms note
  instead of the builder code.
- T12 ("what does UPS have to do with Maersk→DPD?"): grounded the answer in the actual cell —
  (FR×Poster40cm×0kg) = 2,461 maersk @4.06 + 434 ups @6.86(→7.20 fwd) + 245 dpd @4.39; leave-as-is
  blend ≈ €4.52 vs all-to-DPD €4.52, DPD edges it, whole cell moves; flows table slices one cell
  decision into Q01-win + Q04-loss by origin. Without the UPS parcels the cell stays (~4.09<4.52).
  Worked example added to q04 findings.
- T13 (Q04c: temporal cell-mix validation, principal hypothesis): PARTIALLY CONFIRMED + bigger
  artifact. FR by month: DPD POLAND 3,203→2→0 (completed switch, stopped after Jan — cleanest
  artifact, cur_inc=dpd_pl is stale for that cohort); UPS FR −19% overall but small formats
  actively migrating (pizza 239→53 = −78%, posters −51% Jan→Mar) — exactly the Q04 dragged-loss
  cells; DE clean (movers flat by month). Consequences: stale keep-blends, GRI leaks onto
  cohorts that already left UPS, flow rows misstate operational change for FR. Fix options
  recorded (A: rebase sensitivity in result_investigation, recommended first; B: build_final.py
  incumbent rebase + cascade re-run). Conclusion + fix decision pending principal.
- T14 (Q04d: whole-book scan, principal-directed "investigate everywhere"): THREE artifacts.
  (1) FR carrier staleness — dest-level FR-ONLY (sweep over 18 dests clean elsewhere).
  (2) PACKAGETYPE LABEL CHURN mid-Q1 (biggest): W80x60AE 17,853 Jan→0 Mar replaced by ORWO_80x60
  1,609→10,867; ST120x90→120x80. Cells key on label string → DE era-cohorts got DIFFERENT winners
  (old label 8,252 UPS / 8,951 DPD; new label ~100% DPD) → dead-label routing rows, phantom
  UPS-keep volume; my own sweep-3 GRI-leak €63k was mostly label churn (verified before reporting).
  (3) CUSTOM_OVERSIZED DBS→UPS drift DE/AT/IT/CH (DBS share 54%→41% in Q1, label stable, real) —
  €108.7k/yr booked on stale-dominant cohorts; touches the conditional module baseline → add
  "DBS book still on DBS?" to the 3-gate check. Recommended ONE fix pass: label-normalization map
  + cur_inc rebase + cascade re-run. Findings in q04d file; fix decision pending principal.
- T15 (scope confirms + true-grain recheck of FR migration, principal pushed grain again):
  (a) verified Jan DPD-FR cohort lands on Maersk Feb/Mar (cohort-level, packagetype-matched);
  (b) FR-only confirmed for cell staleness; oversize DBS→UPS drift is the separate non-cell item;
  (c) at dest×pkg×wkg the FR UPS/Maersk mix = 3 patterns: heavy bands 100% UPS by design (not
  stale), light bands mid-migration but STILL mixed in March (13-28% UPS — dragged-loss problem
  real+persistent there, threshold lever relevant), small steady remainders. Fix refined: DPD
  rebase wholesale; UPS = re-weight keep-blends to March shares, not label rebase; heavy bands
  untouched. Addendum in q04c findings. Side deliverable earlier: handoff prompt for a parallel
  session on the packagetype label churn (q04e namespace reserved).
- T16 (Q04 resolution + commit + handoff): principal confirmed the FR staleness changes ROUTING
  DECISIONS (poster-cell winner flips), not just savings → full build fix decided (build_final.py
  incumbent rebase: DPD-FR cur_inc→maersk wholesale + keep-blends from March state w/ Q1 fallback +
  cascade re-run). Principal: "commit them + prompt for another session". Committed bi-analytics
  98cdd49 (final_report/ + annual_2026/ + result_investigation/, pathspec; management_briefing
  left out — superseded; NOTE: swept sibling's in-flight q04e_* files, benign, flagged). Handoff
  prompt for the FR-rebase session delivered in chat.
- T17 (Q05: DPD PL→Maersk 26,184 ann / 4,658 Q1): TWO stories. AT 65% = real ongoing decision
  (alive all 3 months, ~1k/mo; −5% vs today / ~11% vs DPD engine bid; €5-15k/yr by basis; eu_hd
  offer-trust same as Q02). FR 34% = the Q04c stale January cohort — move already happened in
  reality, €85 booked, rebase session will dissolve it into maersk→maersk. No dragged-loss issue
  (225 parcels / −€34). Engine-vs-actuals note: dpd_pl_current prices these ~7-8% above Q1
  invoiced (not chased). Findings + README updated; conclusion pending.
- T18 (Q05 CLOSED): principal — AT trusted (rides with Q02 Maersk decision); FR slice handled by
  the q04f rebase session. Recorded in q05 findings.
- T19 (Q06: UPS→Hermes 5,350 ann / 1,041 Q1, €77,745/yr): the UPS OVERSIZE-FEE ESCAPE — big flat
  stuff (CUSTOM_OVERSIZED €141.67→€50.22, custom-cut, PIZZA/ST 120x90; med longest 120cm, chg
  13.3kg; DE+AT 81%). 165 parcels carry €24,380 UPS oversize fees = 77% of flow today-cost; UPS
  billing the fees = independent evidence dims are real (vs DBS zV template risk). Bimodal: median
  −€3.56 (70% small losers, cell-drag), p95 +€134. No-module counterfactual: these parcels would
  net €26.5k via DHL-rescue; Hermes adds €51.3k ≈ the module's ENTIRE €52,142 other-lanes uplift —
  flow is module-gated, not independent. Month-stable. Findings written; conclusion pending.
- T20 (principal challenged the €141.67 CUSTOM_OVERSIZED avg — "I don't see that in invoices"):
  verified with invoice-level rows + book-wide split. €141.67 = the 72-parcel Hermes-won TAIL of
  3,880 UPS CUSTOM_OVERSIZED (label = custom-CUT carton, not physically oversize; 86% avg €8.21
  stay UPS; variable track per-parcel by real dims). Tail carries Large Package €101.80 / OML
  €1,075.90 fees (netted >€400 in baseline). Concrete trackingnumbers added to q06 findings.
  His invoice intuition correct for the packagetype — consistent with the flow.
- T21 ("how can it win only a subset — destinations?"): NO — variable track routes per parcel on
  cost; UPS's per-parcel bid = its actual invoice → Hermes wins exactly the parcels UPS measured
  and fined. DEEPER FINDING: recorded dims of UPS CUSTOM_OVERSIZED are template-like (cluster
  ~132×84×6, L+girth p95 314; both fee and no-fee groups ~identical) — if real, UPS's >300cm rule
  would fine ~all, it fines 2% → recorded dims ≠ measurements; UPS scanners are the implicit
  instrument. Selection OK (carrier-certified big) but Hermes engine PRICES the 72 on the template
  shape (€50 avg) → understatement risk on the €1,075-OML monsters. REVISED q06 trust section:
  dims-check gate matters for the UPS slice too (populated-column-not-a-measurement recurrence,
  UPS side). Corrected my own earlier "dims are real here" claim.
- T22 (cherry-pick discussion + Q06b): principal concern — is variable-track routing ops-executable
  at all? Confirmed: standard cells = executable rules; variable track = per-parcel ceiling, UPS
  slice conditioned on ex-post fee info (not executable ex ante); executable version needs real
  dims at dispatch (production knows the cut; bi-etl lineage trace still open). Q06b: DBS chunk is
  NOT high-cost cherry-pick — 57% of book moves (class-wide), stays are the EXPENSIVE ones (dims-
  rejected), savings broad (median €17.87, top decile 27%); real risk = template dims (already
  gated, Conditional/LOW). Q06b appended to q06 findings. NOTE: q04f rebase session landed —
  headline €997.7k→€974.7k, DBS→Hermes now 4,745 Q1 — used post-rebase artifacts for Q06b.
- T23 (Q06c: "don't we have more crazy-surcharged shipments?"): YES — full UPS oversize-fee pool
  €140,867 Q1 (~€675k/yr) on 701 parcels. Plan rescues ~€69k (Hermes 24.9k + DPD 27.2k + Maersk
  15.7k + misc); €71.5k STAYS on UPS = €31.8k OML anomalies (>€400, netted by design, ops-
  prevention prize) + €39.7k/Q1 (~€190k/yr) recurring Large-Package fees in STANDARD cells that
  are structurally unrescuable (template dims = can't identify the fee magnets at label time).
  ~€190k/yr = quantified additional prize for real-dims-at-dispatch. Method note: stay-slice
  booked-saving column meaningless (cell-mean smearing). Q06c appended to q06 findings.
- T24 (untangle turns: "only 20 LPS fees?" + "is Hermes also expensive?"): walked the 701-parcel
  fee pool split (170 variable→Hermes / 115 incidental via DPD-Maersk cells / 387 stuck standard /
  29 OML-excluded). Anatomy of the 170: UPS ~€199 all-in (base 23 + fuel 27 — UPS fuel-surcharges
  fees — + fee 146) vs Hermes €33.74 → €120/parcel; €20.4k = count-limited, not Hermes-expensive;
  ~€28k vs raw invoices (€7.7k OML-netted). Appended to q06 findings.
- T25 (Q04 + Q06 CLOSED, principal conclusion): (1) FR routing needed changes — carriers had
  already shifted during Q1; executed via q04f rebase (headline →€974.7k). (2) Custom parcels ARE
  cherry-picked but impact small (~€78k/yr reachable, count-limited), and routing handling is
  unsolved (no executable dispatch rule without real dims; locks the ~€190k/yr standard-cell LPS
  pool too). Conclusions recorded in q04 + q06 findings.
- T26 (CLOSE, "thats all for now"): round 1 (Q01–Q06) complete, all conclusions recorded. Quest
  stays in-progress (review continues by rounds). Harvest: 1 examine draft
  (selection-evidence-is-not-class-evidence) + 1 bank draft (result-investigation round-1 claims)
  + 1 cross-conv memory. Resume → inventory. bi-analytics Q05/Q06 + conclusion edits left
  uncommitted there pending principal go (q04f_* files belong to the rebase session).

No pending external actions. (bi-analytics commit 98cdd49 completed T16; comms posts completed.)

## Round 2 — continuation session 87f50e88 (2026-06-11)

- T27 (recap + Q07): session opened with a round-1 recap ask, then "lets continue" → round 2.
  Q07 ("no-Hermes = only new-Maersk-countries + reshuffle existing volume, correct? + show
  Maersk's new volume per country"): CONFIRMED with 3 precisions (DHL gets new-to-DHL CH/AU
  lanes; residual carriers consolidate into the 5, DK residual→Maersk at a small loss; no-Hermes
  leaves DBS book on DBS). Per-country pull (q07 script + findings, post-rebase basis): NEW
  Maersk volume 44,913 Q1 / ~190k yr, €53.6k Q1 / ~€224k yr saving vs today; IT 22.9k (87.6%
  of country) + ES 15.2k (94.1%) = 85% of it; AT 4.1k (Q05 slice), DK 1.1k NEGATIVE (residual
  consolidation), AU 1.1k row_hd, FR new trivial (360; kept FR book 12,445). Concentration-risk
  note: Maersk becomes near-total carrier for IT/ES. Also added the pending q04e README row.
  Conclusion pending principal.
- T28 (Q08: "what migrates DHL Paket→DPD PL? we didn't answer that, right?" — correct, new):
  21,946 Q1 (~105k/yr) and it saves NOTHING (−€568 Q1). 99.6% = the single DE×Poster40 light
  cell q04f flagged as the March-anchor knife-edge flip (avg €3.21 DHL→€3.25 DPD, 68% of
  parcels individually negative, 30% within ±€0.10). Verdict: optimizer noise on a flat cost
  surface, poster child for the Q01b minimum-saving threshold (any ≥~1% parks it on DHL).
  q08 script + findings + README row written. Conclusion pending principal.
- T29 (Q08b: "why does it pop up if it's a loss?"): grounded in build_final.py — (1) argmin
  with no min-saving threshold (ε wins move whole cells); (2) decision basis = q04f
  March-anchored keep (DHL €3.338) vs DPD €3.255 → DPD wins forward by €0.08, while the
  reported saving uses full-Q1 actuals (DHL €3.211, Jan/Feb cheap → −€0.04). DHL cost in the
  cell drifted up through Q1 (3.15/3.17/3.34). Loss label = retrospective yardstick artifact;
  forward-real vs noise undecided (open: what drove DHL March +€0.17). §Q08b appended.
- T30 (Q08c, principal: "March got a rate increase" + Q1-vs-annual confusion): CONFIRMED
  empirically — DHL flat rate €3.13→€3.32 (+6.1%) late Feb, same-weight buckets all step;
  cell is genuinely cheaper on DPD forward (+€8.7k/yr vs post-increase rate). Clarified: no
  sign flip Q1→annual (−568 × 4.82 = −2,724, same yardstick); the "loss" is the stale Jan/Feb
  baseline scaled into the year. FLAGGED baseline-vintage implication: all savings vs DHL
  understated ~rate-delta on moved volume; dhl→dhl stays book a phantom negative (ups→ups
  analog) — feeds the round-2 "stays" question. §Q08c appended.
- T31 (report-confusion fix decided): proposed the three-number bridge (Q1 actuals → do-nothing
  @2026 rates → plan; per-flow savings on (2)−(3) only) + threshold as companion; Niklavs chose
  "write a prompt for another session" (q04f pattern). Handoff prompt delivered in chat —
  q09_baseline_bridge namespace reserved for that session; includes the [[S200_104770bd_eu-tender-no-hermes-portfolio-check|S200]] final_stats
  ordering-drift fix; threshold explicitly out of scope (interaction noted).
- T32 (understanding turns on the bridge): clarified (a) the 2026-rates yardstick = March
  anchor mechanism (sweeps all carriers; DHL implicit via March invoices, UPS GRI the only
  synthetic markup; single-cell DHL verification caveat → q09 to scan book-wide all carriers);
  (b) decisions were NOT made unadjusted — q04f already put the decision side on the forward
  basis; only reporting lagged. Real residual gap surfaced: thin-cell fallback (3,049 cells
  keep full-Q1 mean ≈ ⅔ pre-increase for DHL → ~4% understated keep, pro-incumbent bias on
  marginal cells). Addendum line for the q09 prompt delivered in chat (carrier-level March
  uplift factor as fallback; quantify flips + €).
- T33 (scope confirm): "just change the savings calc and we're good?" — yes for the confusion
  fix (reporting-layer only; thin-cell check may flip marginal winners, reported before
  adoption). Unchanged opens restated: threshold call, rate unknowns (GRI 5.9 / Maersk fuel
  band / DHL waiver / DPD offer), remaining round-2 questions (stays, residual→DPD,
  DBS→Hermes, tier split, do-nothing — easier post-q09).
- T34 (WRAP, round 2): q09 prompt pasted by principal into a parallel session ("its happening
  on the side"); this session closes. Round-2 footprint: q07/q08 scripts + findings + README
  rows (q04e/q07/q08) in bi-analytics, UNCOMMITTED there. Quest stays in-progress; resume →
  inventory/eu-tender-result-investigation-resume__87f50e88.md (5733cb1d resume archived).
  Harvest: 1 bank draft (rate-vintage yardstick bridge) + 1 examine draft (drop-to-analogy).

No pending external actions this continuation (round-2 writes were local file writes; comms posts completed).

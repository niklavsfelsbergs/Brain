# S056 — Apartment purchase in Latvia: domājamās daļas vs dzīvokļa īpašums

**Player:** Zezima (first real session — pre-operational until now)
**Opened:** 2026-05-23
**Session:** e5df54a2

## What this is

Niklavs viewed an apartment in Riga he likes. The catch: it is registered as
**domājamās daļas** (notional/ideal co-ownership shares of a whole property) rather
than as a **dzīvokļa īpašums** (a separately-titled apartment unit / condominium).
He wants research into what buying that form of ownership would imply.

## Turn log

- **T1** — Scoping. Asked for topic, purpose, and reach (internal-thinking vs real
  external digging).
- **T2** — Topic landed: Riga apartment, domājamās daļas not dzīvokļa īpašums.
  Principal gated on "first let me know if you understood." Confirmed the legal
  distinction; he confirmed scope: leaning to buy but willing to walk if bad;
  mortgage-financed; planning to live in it; hold horizon unknown.
- **T3** — Spawned 4 background research agents (general-purpose substrate briefed
  as penguins — true penguin agent type only registers from gielinor/ CWD):
    - P1 legal structure & buyer/occupant security (lietošanas kārtība, partition
      right, pirmpirkuma tiesības)
    - P2 mortgage / bank financing of an ideal share
    - P3 resale/liquidity + conversion to dzīvokļa īpašums
    - P4 practical risks & co-owner dynamics + buyer due-diligence
  All write to zezima/research/ + own sibling quest-log (S056_pN_*). Returned control
  to principal; synthesis gated on all 4 returning.

- **T4** — P2 (mortgage) returned, confidence med-high. Key: co-owner can pledge own
  share (Civillikums 1072) but Tier-1 banks generally won't mortgage a bare ideal
  share; realistic path = Altum-guaranteed loan on a clean half-house WITH a
  *lietošanas kārtība* registered in Zemesgrāmata. Financing harder, not impossible —
  hinges on the registered use-arrangement (ties to P1). Held synthesis; awaiting P1/P3/P4.

- **T5** — P1 (legal) returned, high confidence. Core: domājamā daļa = abstract
  fraction of whole building, not the flat (CL 1067/1072). Right to occupy a specific
  apt exists only via *lietošanas kārtība*, which binds future buyers ONLY if
  registered in Zemesgrāmata. Permanent exposure to CL 1074 — any co-owner can demand
  division anytime (2022 reform: 5-yr bar w/ broad exceptions); outcomes range from
  conversion to dzīvokļu īpašumi to forced auction ending the home. CL 1073 pre-emption
  (2-mo first-refusal, outsiders only). EMERGING HINGE: "is the lietošanas kārtība
  registered?" — load-bearing for financing (P2), occupancy security, and likely
  conversion (P3).

- **T6** — P4 (practical risks) returned, med-high. Practitioner consensus: avoid ideal
  shares if you can (advokāts Egīls Radziņš, outright). #1 pre-purchase check (3rd
  source converging on the hinge): written + Zemesgrāmata-registered lietošanas
  kārtības līgums securing access to YOUR flat. Worst cases: uncooperative co-owner
  blocks repairs/renovation; forced auction of whole building (~70-75% market start);
  co-owner's creditors auction their share, no pre-emption → stranger co-owner. Fresh:
  Senāts SKC-108/2025 (2025-12-17) — usage utilities to actual occupant, not by share;
  mgmt/reserve/tax stay proportional. Enforcement may lag.

- **T7** — P3 (resale + conversion) returned, med confidence. Discount real but
  magnitude poorly sourced (ignore ≈90% anecdote); cash-buyer-dominated pool is the
  driver. Exit: 2-mo first-refusal + 1-yr redemption clawback. CURE = convert to
  dzīvokļa īpašums via VZD division (fees cheap ~€40 + ~€30-45/apt; cadastral survey
  is the variable cost) but needs UNANIMOUS co-owner consent (one holdout = hostage
  problem) or court-forced dissolution.
- **T8** — All 4 returned. Wrote synthesis verdict to research/
  2026-05-23-domajamas-dalas-SYNTHESIS-verdict.md and delivered to principal.
  Verdict: pros lean "don't unless"; hinge = registered lietošanas kārtība; second
  fork = pusmāja vs multi-apt-building share. Gave WALK/CONSIDER decision frame + a
  6-item "find out about THIS apartment" checklist. Surfaced the disambiguating
  questions needed to land the call definitively.

- **T9** — Principal answered the disambiguating question: it's a building with ~70
  apartments. This is the "time bomb" case (P2/P4) — a share of a large multi-apartment
  building, NOT a pusmāja. Verdict sharpens to LEAN WALK. Three bites at 70 owners:
  (1) mortgage likely declined by Tier-1 (Altum support was pusmāja-shaped) → may kill
  his finance-it plan outright; (2) escape hatch effectively closed — conversion needs
  ~70-owner unanimity, unrealistic, so the discount is ~permanent; (3) CL 1074 division
  + creditor-auction exposure multiplied across 70 owners. Honest caveat: such buildings
  are lived in day-to-day if there's a functioning registered use-arrangement + manager;
  the decisive practical test is whether he can even get a mortgage on a 1/70 share.

- **T10** — DECISION: Niklavs is passing on the apartment. Clean resolution; research
  did its job (turned an attractive flat + unfamiliar Latvian term into a confident
  no). Quest deliverable complete.

## Where we are

RESOLVED — principal decided to pass. Quest complete; ready to move to completed/ on
session-close. Research artifacts (4 penguin files + synthesis verdict) preserved in
zezima/research/ as reusable reference for future apartment hunts; due-diligence
checklist reusable.

- **T11** — Principal sent a 2nd ss.lv listing (Duntes 28, "Duntes Ozoli", €120k,
  70.4 m², 2-rm, 2007 brick, 9/16). Fetched + read verbatim. KEY DISTINCTION (and a
  teaching case): listing says "Īpašuma sastāvā ir zemes gabala domājamās daļas" —
  the domājamās daļas refer ONLY to the LAND PLOT, not the apartment. The apartment
  itself is a proper dzīvokļa īpašums (registered separate unit). Confirmed by
  "to apsaimnieko dzīvokļu īpašnieku biedrība" (apartment-owners' association — exists
  only for buildings split into dzīvokļa īpašumi). This is the NORMAL/healthy structure
  — owning your share of the land is a plus (no forced ground-rent). First automated
  fetch-summary mis-read it as co-ownership; careful verbatim re-read corrected it.
  Definitive confirmation = pull Zemesgrāmata folio. Location nuance: filed "centrs"
  but Duntes is ~10 min from centre (seller's own text admits it).

- **T12** — Principal wants in-depth buy/no-buy on Duntes 28 + a reframe. Spawned 4
  more background penguins (S056_p5..p8): P5 location/daily-life (Duntes/Skanste/
  Sarkandaugava, transport, Skanste development, safety, noise), P6 price+resale market
  (€1,714/m² fair? comparables, Riga 2026 trends, liquidity), P7 building/project
  ("Duntes Ozoli" 2007 quality, developer, biedrība mgmt, €0.95/m² fee, heating/energy,
  defects), P8 money (2026 mortgage rates/LTV/Altum, NĪN, notary + ~1.5% Zemesgrāmata
  fee + agent, total upfront+monthly, Zemesgrāmata/Kadastrs checks). All → zezima/
  research/ (2026-05-23-duntes28-*). Delivered initial reframe + asked principal 3
  framing questions (own/rent now? buy-to-live-indefinitely vs stepping-stone? is €120k
  comfortable or a stretch?) to personalize the synthesis.

- **T13** — P6 (price/market) returned, med-high. €120k/€1,714/m² is FAIR-TO-FAVOURABLE,
  ~10-16% below comparable asking when framed against Duntes Ozoli project (~€2,000/m²
  2-rm) + Pētersala/centre-adjacent segment; only looks dear vs raw Sarkandaugava avg
  (~€1,071/m², wrong comp = old/small stock). €100-160k 2-rm band = most liquid segment.
  Rent optionality ~€470-550/mo (~4.5-5% gross yield). Riga ~flat + modest 2026 upside.
  Loggia + courtyard parking add unquantified value. Verdict axis "good asset by price" =
  early yes.

- **T14** — P5 (location) returned, med-high. Duntes 28 on the SEAM of Sarkandaugava /
  rising Skanste / Pētersala — NOT central (listing says "centrs" but Wikipedia+Latio
  file it Sarkandaugava/Northern; ~3km, 15-20min transit to Old Town). Pros: Sky&More
  mall across road, kindergarten in building, ER hospital next door, hilltop views.
  Cons: transit lags area growth (council member flagged), through-road + mall traffic
  noise, transitional/industrial surroundings in patches. Net: mixed-to-positive but
  SPECIFICALLY for a car-owning owner-occupier on a higher/quieter floor betting on
  Skanste maturing (planned tram to Central Station, no firm date). → makes framing Q1
  (how he lives / drives?) decisive for this axis.

- **T15** — P8 (money) returned, med-high. One-off buy cost ~€2,150-2,300 (1.5% state
  fee ~€1,800 dominant; agent normally seller-paid). All-in to OWN ~€730-840/mo
  (~€523/mo mortgage on €102k @ ~4.6% 30yr + ~€67 mgmt + utilities + NĪN + insurance).
  Rate = estimate (6M Euribor ~2.55% falling + 1.5-2.2% margin); needs written bank
  offer (±€30-50/mo per 0.5%). Altum young-specialist (≤35 + education) → 5% down
  possible. NĪN tip: declare residence before Jan 1 for reduced Riga rate (saves
  several hundred €/yr). → carry-cost axis answered; pivots on his current rent (Q1).

- **T16** — P7 (building) returned, med. 2006 cascading RC tower (3 sections 7/13/16,
  217 apts, Budimex-built), Class C energy (73.1 kWh/m²/yr), €0.95/m² mgmt normal-for-
  serviced. Flags: developer SPV liquidated (no warranty), self-managed biedrība,
  2008 "Bietes balva" anti-prize (AESTHETIC only, not structural — no defects/litigation
  found), listing-says-brick-vs-aggregator-says-RC. CENTRAL UNKNOWN = reserve fund +
  planned major repairs (terraces/flat roofs/1st-gen lifts on 20yr building) — document
  request only.
- **T17** — All 4 (P5-P8) read in full. Wrote synthesis verdict to research/
  2026-05-23-duntes28-SYNTHESIS-verdict.md + delivered to principal. VERDICT: buy-worthy,
  proceed to due diligence (opposite of apt #1 — nothing structurally disqualifying;
  fair-to-good deal on a sound asset). Gating checks: (1) reserve fund/major repairs,
  (2) honest location-fit. Provisional rec flexes on his 3 framing answers (rent now /
  settle-vs-stepping-stone / comfortable-vs-stretch). Gave full pros/cons + an 8-item
  pre-commit due-diligence checklist.

## Where we are

Both apartments analyzed. Apt #1 (70-unit domājamās daļas) = WALK (done). Apt #2
(Duntes 28, proper dzīvokļa īpašums) = BUY-WORTHY, proceed to DD. Synthesis verdict
delivered + saved. Awaiting principal's 3 framing answers to lock the Duntes rec, and/or
his next move (e.g. draft seller/biedrība/bank questions).

- **T18** — Principal supplied 2 due-diligence findings: (1) NO reserve fund; (2) real
  usable size ~58 m² (70.4 counts the 8.6 loggia; living area 58.6). Both cool the
  verdict. No reserve fund = the flagged central landmine, answered badly (future repairs
  → special levies / deferred maintenance on a 20yr tower w/ terraces+lifts, no warranty,
  self-managed). Real size → price is ~€1,950-2,050/usable-m² = fair/market not the
  10-16% bargain (that was loggia-inflated denominator). Updated synthesis file with a
  REVISION banner. New verdict: "fair deal with a real maintenance catch" — proceed only
  eyes-open + budget levies + use both facts as price-negotiation leverage; lean
  pass/hard-negotiate if it's a stretch. Still not apt #1's structural danger.

## Where we are

Duntes 28 verdict COOLED (no reserve fund + true ~58m²) from "good deal" to "fair deal
w/ a real catch." Still no framing answers (rent/horizon/comfort) — he answered DD items
instead. Have enough for a clear updated lean: negotiate hard or pass unless rent saved /
horizon long / budget comfortable justify it.

- **T19** — Principal asked for the negotiation angle. Drafted: strategy (two levers —
  no-reserve-fund repair-liability transfer = lead; usable-area-58-not-70 = support),
  number framework (open ~€105k / land ~€110-113k on €120k ask; his call), tactics
  (get no-fund in writing, don't reveal max, anchor on uncapped repair risk, offer
  price-cut OR seller reserve top-up), and a ready-to-send message in Latvian + English.

- **T20** — DECISION: passing on Duntes 28 too. Principal's reason is spatial/feel —
  photos flatter ("it lures you in"), but the room is narrow and long, not much usable
  space. His own eye caught the fit problem the research couldn't measure (and it
  corroborates the ~58 m² real-size finding + the no-reserve-fund strike). Both
  apartments now passed. S056 resolved.

## Where we are

RESOLVED — both apartments passed. Apt #1 (70-unit domājamās daļas) = walk on legal/
structural danger. Apt #2 (Duntes 28) = pass on spatial fit + no-reserve-fund risk
despite clean ownership & fair price. Principal trusted spatial intuition over the
pretty listing. Research artifacts (8 penguin files + 2 synthesis verdicts) preserved in
zezima/research/ as reusable reference + checklist for future viewings.

## Next concrete step

None required. Quest ready to move to completed/ on session-close. On a later Zezima
alching pass, harvest bank/ domain notes: the domājamās-daļas vs dzīvokļa-īpašums
distinction (incl. the land-share normal case); Riga price framing (right comp set;
usable vs headline area); reserve-fund-is-the-hidden-risk; and the meta-lesson —
listings flatter, walk the actual space. First real Zezima domain knowledge.

## Close — S056 (2026-05-23)

- **No pending external actions.** All research (4+4 penguins) completed; both decisions
  (pass / pass) made by principal. Nothing left in flight.
- **Quest complete** — moving this file + 8 penguin siblings (S056_p1..p8) to `completed/`.
- **Harvest (3 drafts):** `bank/drafts/notes/latvia-property/domajamas-dalas-vs-dzivokla-ipasums.md`,
  `bank/drafts/notes/latvia-property/riga-apartment-buy-evaluation.md`,
  `niksis8_character/drafts/2026-05-23-home-decisions-gut-fit-veto.md`.
- **Artifacts preserved:** 8 research files + 2 SYNTHESIS-verdict files in `research/`.

## Next concrete step

On all-return + framing answers: synthesize buy/no-buy with pros/cons, a recommendation,
and the reframe tied to his situation. Then a Zezima alching pass to harvest bank/ domain
notes (Latvia apartment-buying literacy — both the domājamās-daļas distinction and the
Duntes/market specifics).

## Next concrete step

Await principal's answers to the disambiguating questions, then sharpen the verdict to
his specific apartment. If he wants, draft questions for the seller/agent/notary, or a
script for the bank/Altum call. Harvest to zezima/bank/ during a later alching pass
(Zezima's first real domain knowledge — apartment-buying in Latvia).

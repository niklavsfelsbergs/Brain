# S115 — EU Tender 2026 DPD Poland Round-1 reply review

**Session:** db60ed8a · 2026-05-27 · Jebrim (principal)
**Same session as S114** (austrian_post rebuild, committed e8ddc62). This is the "continue with the new replies" thread.
**Repo:** out-of-tree `Documents/GitHub/bi-analytics-main/NFE/projects/2_EU_tender_2026`

## Goal
Review the newly-arrived carrier reply (Round-1 style, like S099): replies vs dispatched open questions → per-question resolution + deterministic-readiness verdict + engine to-do. Keep canonical docs in sync.

## Turn log

### Turn 1 — MISFILE CATCH + DPD PL reply review
Principal: "GLS folder has been added with their responses." **Grounded before analyzing (anchor-referent discipline) — and caught a mis-file:** the file in `carrier_responses_to_open_questions/GLS/` is **not GLS — it's the DPD Poland reply.** Evidence: it answers the DPD PL dispatch (`1_offers/picanova/DPD PL/questions_for_carrier.md`, S078) 1:1 — zone fee col K, `dpd.com/pl` Table of Zones, exceed-technical-limitations 22.50, billable max(actual,vol/5000) + per-kg surcharges, **PKN Orlen Arctic Diesel 2**, CH/GB option-2 customs, ORWO 85%-DE, Transports line-haul, volume tiers; and the text says "DPD PL"/"DPD MAX"/"Szczecin". GLS's actual dispatch is a different 15-Q set (Energy/ClimateProtect/Pre-financing/EFTA/Köln/YourGLS) — none touched. Flagged to principal; **principal confirmed + said rename GLS→DPD_PL and continue.**

Renamed `carrier_responses_to_open_questions/GLS/` → `DPD_PL/` (+ inner file `gls` → `dpd_pl`). Reviewed the reply against the DPD PL dispatch + offer CLAUDE.md.

**Verdict: deterministic-ready for Q1 after a `dpd_pl-2.0.0` build** (NB: **no DPD PL engine exists in `2_analysis/` yet** — from-scratch build, not a rebuild). Strong reply, all 11 answered. **The two biggest Phase-1 cost-inflators both resolve FAVOURABLY** (DPD PL ran ~3× current invoice on pessimistic defaults):
1. **Zone fee CONDITIONAL not blanket (Q1)** — "per parcel to specified areas (mostly islands with ferries)", postcode PDF attached → collapses the ~47%-of-headline assumption.
2. **Surcharge mechanism corrected (Q4)** — worked example `4.29×1.075 + 0.06+0.05+0.09 = 4.81`: **fuel = %·base (7.5%@~6300 band), road+energy+security = flat 0.20/parcel** — NOT the per-kg 0.29/kg the rate-sheet blue table implied. Materially lower on heavier parcels. ⚠️ reconcile vs the offer's "counted surcharges" columns N–S before building.

Other resolutions: billable = max(actual, vol/5000) ✓ (Q4); fuel monthly first-reading, Q1 PLN Jan 4876/Feb 5037/Mar 5712 (Q5); **CH stays option 1** (44+45; opt2 needs CH entity+resident director), **GB can use option 2** (Q6); exceed-tech graduated — ship+22.50 for 31.5–~33 kg, reject gross (Q3); **line-haul INCLUDED in per-parcel rates** (no per-pallet allocation — contrast Austrian Post; only min-fill penalties as risk) (Q8/Q9); volume tiers explicit (>50k base / 25–40k +5% / 20–25k +10% / <20k +10%) (Q10); additional services ~0 for Picanova's cuboid flow (Q11). Residual: tariff-codes/parcel internal (assume ≤3, Q7).

**Deliverables:** `carrier_responses_to_open_questions/DPD_PL/REVIEW_CONCLUSIONS.md` (full per-Q + verdict + engine to-do); flipped the DPD PL dispatch status table (11 rows → RESOLVED) in `1_offers/picanova/DPD PL/questions_for_carrier.md`.

**FINDINGS for principal:**
1. **DPD PL likely flips from "uncompetitive" to competitive** — both headline inflators (zone-fee blanket, per-kg surcharges) were artifacts of pessimistic Phase-1 defaults; the reply corrects both downward. Real ranking needs the dpd_pl-2.0.0 build + cost_matrix.
2. **dpd_pl is a FROM-SCRATCH engine build** (no existing engine), bigger than the AP/dhl_express rebuilds — and the zone-fee needs parsing the 2021 Table-of-Zones PDF (postcode ranges) + matching `shipping_zipcode`.
3. **The 2nd new provider reply is still unknown** — principal mentioned 2 new replies; only DPD PL surfaced (mis-labelled GLS). GLS dispatch remains genuinely OPEN (no GLS reply). Ask which the 2nd is.

### Turn 2 — committed; build held (principal)
Principal rulings: (1) **2nd reply = GLS, coming later** — "I will add GLS after we are done with DPD." So proceed DPD-only for now; the GLS dispatch stays genuinely OPEN until that reply lands. (2) **Commit the review, hold the build.** Committed the DPD PL review out-of-tree → tender **`cf0b6c4`** (3 files: `DPD_PL/REVIEW_CONCLUSIONS.md` + `DPD_PL/dpd_pl` reply + `DPD PL/questions_for_carrier.md` status flip; pathspec-scoped, local-only no push). The zone PDF (`Table of zone surcharges…2021.pdf`) is **gitignored** (`.gitignore:18 *.pdf`, like all offer attachments) — stays on disk for the build, not version-controlled. The from-scratch `dpd_pl-2.0.0` build + `cost_matrix.py` re-run are HELD until GLS is reviewed too (so cost_matrix runs once on the full engine set).

**Repo state:** DPD PL review COMMITTED (cf0b6c4). Brain-side S115 records uncommitted (awaiting principal go).

### Turn 3 — GLS reply reviewed (PARTIAL)
Principal uploaded GLS. Identity re-checked (post-DPD-misfile discipline) — genuinely GLS this time (`Postleitzahlen je Zone.pdf`, GLS-branded calculator). Reply = **2 price-calculator screenshots (`question3.png`, `question10.png`) + the postcode PDF; the `GLS` text file is EMPTY (0 bytes)** — no prose answers.

**Verdict: NOT deterministic-ready — PARTIAL (~6/15 + a new surcharge + 2 ambiguities).** Wrote `carrier_responses_to_open_questions/GLS/REVIEW_CONCLUSIONS.md`; flipped the GLS dispatch status table (answered rows + new row 16).

Resolved from the calculator: **application order (Q10)** — base → Energy 20.5% + KlimaProtect 2.5% + Season 1% (each on the base subtotal, ADDITIVE, no compounding) → Maut → Dieselfloater → total; **Q3** ClimateProtect 2.5% on base; **Q7** private-address +0.15 national / 0.00 export; **Q8** Toll national flat 0.38 / export 5.70% (⚠ base inconsistent between the two screenshots — base in q3, subtotal2 in q10); **Q11** postcode→zone PDF supplied; **Q15** Season windows Apr&May/Oct–Dec → **0 in Q1**.

**NEW: "Dieselfloater"** — a 2nd fuel-type %-surcharge (not in the dispatch), ~4.1% in March (2.16€/L), fires after Maut, **fires in Q1**. Added as dispatch row 16.

**STILL OPEN (the big blast-radius levers): Pre-financing 4.8% (Q4), WeighingService (Q2), EFTA clearance 25€ (Q5), Stettin pickup/line-haul (Q6), Energy 3-month history + 4%-discount (Q1), Dieselfloater Jan/Feb + cadence.** Signal: Pre-financing/WeighingService/Service-flat-rate are ABSENT from the official calculator → may not apply to Picanova, but must be confirmed (don't assume). Energy shown 20.5% vs the engine's 28% assumption — materially lower.

**Repo state:** GLS review out-of-tree (REVIEW_CONCLUSIONS + status flip), NOT committed. Reply artifacts (2 PNG + PDF) on disk (PNG/PDF likely gitignored). dpd_pl + gls builds + cost_matrix still HELD.

### Turn 4 — GLS round-2 drafted; DPD PL build delegated
Principal: "draft the follow-up dispatch" + "hold off DPD PL engine, will be built by another session." Drafted **`1_offers/picanova/GLS/questions_for_carrier_round2.md`** — send-ready copy block + annotated, 6 questions: (1) Pre-financing/WeighingService/Service-flat-rate applicability (framed off the calculator's omissions — sharp), (2) Energy + Dieselfloater Jan/Feb/Mar + 4%-discount formula, (3) Toll Intl base, (4) EFTA clearance grain + NO threshold, (5) Szczecin pickup/line-haul, (6) Big Parcel/Non-conveyable/Oversized bundle. Led with send-ready plain text per the lead-with-send-ready rule.

**DPD PL engine build is NOT mine** — handed to another session per principal. This session's EU-tender work = the two reviews (DPD PL committed, GLS uncommitted) + the GLS round-2 draft.

### Turn 5 — GLS RE-REVIEWED on the full saved reply (verdict corrected)
Principal flagged: the `GLS` text file had **not been saved** when I did Turn 3 — I'd reviewed off the 2 screenshots only and (wrongly) called GLS "partial / needs a big round-2." They saved it; I re-read it (full 15-answer email) + finally opened the zone PDF (had only noted it by filename before — honest gap, now closed). **Verdict corrected: GLS is deterministic-ready for a gls-2.0.0 build pending 3 small inputs**, not a big round-2. All 15 answered, ~13 fully resolved; the big levers resolved FAVOURABLY:
- Pre-financing 4.8% → **0** (SEPA/on-time). WeighingService → **~0** (fires only if weights not supplied; Picanova sends EDI weights). Stettin line-haul → **included** (largest lever, clean). EFTA 25€ → per-parcel OR per-CCD/day (CCD needs fiscal-rep/import-entity). Toll Intl 5.70% → **full net invoice** (compounds). Big Parcel → >150 L. Oversized 30€ → girth>300 only. Season → Apr/May/Oct–Dec (0 in Q1). Q11 zone PDF read (FR/Korsika, IT N/S, ES Balearen/Kanaren, PT Azoren/Madeira, GR/Athen).
- Genuine residuals (small): 4%-discount formula (subtractive vs multiplicative — unanswered); monthly Energy+Dieselfloater Jan/Feb/Mar (self-serve GLS link — 403 to auto-fetch + interactive); NO informal-vs-25€ threshold; EFTA/CCD decision (internal/strategic); Q13 Non-conveyable (offer page 14 — couldn't extract, no PDF tooling in-session); GB sub-region blank in the zone PDF.

Rewrote `GLS/REVIEW_CONCLUSIONS.md` (full per-Q + corrected verdict), updated the GLS dispatch status table (≈13 RESOLVED), and **trimmed the round-2 draft** from 6 big Qs to 3 small clarifications (discount formula / monthly fuel values / NO threshold) + internal follow-ups.

**Tooling notes:** `pdftoppm`/`pdfplumber`/`pypdf` unavailable in-session (can't render/extract the 3MB offer PDF); GLS diesel&energy page 403s WebFetch. So offer-page-14 + live monthly fuel values need the principal.

**LESSON (for memory/feedback):** don't review a carrier reply off partial artifacts when a reply file is present-but-empty — an empty/zero-byte source file is a "not saved yet" signal, confirm before concluding. My Turn-3 "partial" verdict was an artifact of that.

### Turn 6 — GLS finalized + "from-scratch" correction + handover
Principal: "use what it is now" for GLS fuel (hold the calculator snapshot as a flagged year-long assumption, like AP/Hermes), NO threshold irrelevant, and for the 4%-discount — reasoned it's **moot** (the calculator's 20.5% is Picanova's net rate; discount baked in / conservative if not) → **no round-2 to GLS at all.** Finalized: GLS `REVIEW_CONCLUSIONS.md` (Q1 → resolved-as-assumption, verdict deterministic-ready), dispatch status (Q1 RESOLVED), and **superseded the round-2 file** (not needed).

**CORRECTION (verify-don't-assert):** checked `2_analysis/carriers/` — **BOTH engines already exist**: `gls-1.1.0` AND **`dpd_pl-1.0.0`** (zone_fee/uplift_per_kg/customs/non_sortable/non_standard surcharges). So DPD PL is an **UPDATE, not from-scratch** — my earlier "no DPD PL engine" came from a stale offer-doc line (the pre-2026-05-20 retire-decision note); I shouldn't have trusted it without checking the dir. Fixed the DPD PL REVIEW_CONCLUSIONS (verdict + engine-to-do) accordingly.

**HANDOVER written:** `inventory/eu-tender-engine-builds-handover__db60ed8a.md` — next session builds dpd_pl-2.0.0 (UPDATE) + gls-2.0.0 (UPDATE) then cost_matrix across all engines. Both deterministic-ready; specs in the two REVIEW_CONCLUSIONS.

## Next (next session)
- **Build `dpd_pl-2.0.0`** (UPDATE of dpd_pl-1.0.0) + **`gls-2.0.0`** (UPDATE of gls-1.1.0) per the handover note + REVIEW_CONCLUSIONS.
- Then `cost_matrix.py` re-run + ranking shift across all engines; FedEx + DHL Paket still HELD (round-2).
- GLS internal residuals (non-blocking): EFTA/CCD decision, Q13 offer page-14, GB sub-region.
- **Another session builds dpd_pl-2.0.0** (from scratch) per `DPD_PL/REVIEW_CONCLUSIONS.md` — the resume note `inventory/eu-tender-dpd-pl-reply-review-resume__db60ed8a.md` carries the build spec for them.
- cost_matrix re-run across all engines once dpd_pl + gls land.
- Commit pending (principal go): GLS review (REVIEW_CONCLUSIONS + status flip) + GLS round-2 draft; brain-side S115 records.
- **GLS reply** — principal will add it after DPD; review against the GLS 15-Q dispatch (Energy/ClimateProtect/Pre-financing/EFTA/Köln/YourGLS), same Round-1 pattern.
- THEN doc cascade (Step-8): ASSUMPTIONS/DECISIONS/OPEN_QUESTIONS/NEXT + cross-carrier CH-customs row (DPD PL = option-1 individual 44+45) + per-carrier status table (EU-tender doc-sync rule).
- THEN build `dpd_pl-2.0.0` (from scratch) per `DPD_PL/REVIEW_CONCLUSIONS.md` engine to-do (+ any GLS engine), then `cost_matrix.py` re-run across all engines + ranking shift.

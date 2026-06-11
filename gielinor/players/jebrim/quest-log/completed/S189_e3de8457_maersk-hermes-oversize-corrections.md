# S189 — Maersk + Hermes oversize engine corrections + DB Schenker savings split

**Player:** Jebrim · **sid8:** e3de8457 · **2026-06-10**

Carrier replies (Maersk + Hermes, 2026-06-10) on the EU-tender oversize open questions came in. Corrected both engines, sized the impact, cascaded the new numbers through routing/decision/carrier-overview, and added a confidence split to the routing report. Repo: `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/`.

## What happened

**The carrier answers.**
- **Maersk** confirmed a hard handling ceiling the rate card never stated (the S164 gap): longest ≤ 175 cm (DE 200) **AND** girth ≤ 300 cm, rejecting oversize **even where a per-country surcharge exists**. The GEL tubes (200 cm / 360 pure-girth) fall outside it → **Niklavs' call: GEL stays on DB Schenker.**
- **Hermes** retracted the 450 L volume assumption — the real gate is dimensional (standard ≤120cm: W/H≤60 & girth≤300; bulky 120–170cm: girth≤360). The bulky per-destination surcharges (€57.75/€92.35/…) were **already** in the engine since `hermes-2.0.0` (I overstated their novelty one turn — self-corrected).

**Engine fixes (committed `bi-analytics` fceacc6).** `maersk-3.1.0` (absolute handling ceiling, EU branch, even with a surcharge) + `hermes-2.1.0` (girth gate replaces the volume gate). Tests updated to the corrected contracts: maersk 18/18, hermes 32/32.

**Impact.** Surgical pass first (corrected gates over the 7,593 move-population, no shared-state overwrite): 1,909 fall out, €76.8k Q1 saving lost under pure-girth. Then the full regen.

**The girth-definition open question.** Stefan said "girth 300 cm"; the reading is genuinely ambiguous and **decision-vital (€75k/Q1, ~€300k/yr swing)**:
- The rate card's Oversized table uses precise headers **`L+W+H`** and **`L+2W+2H`** — never the word "girth." Stefan introduced it loosely.
- Three live readings of "300": pure girth 2(W+H) [encoded], L+W+H, or L+2W+2H. The L+2W+2H reading is **self-contradictory** (would reject Maersk's own DE standard 120×60×60 = l2w2h 360 parcel), but "length + length-girth" is the *standard* parcel-carrier format (UPS/FedEx/USPS), so it can't be dismissed on convention.
- Maersk fallout swings 845 → 2,819 (99%) between pure-girth and L+girth.
- **Drafted a one-line clarification to Stefan pinned to his own column names** — Niklavs sends it. Proceeding on pure-girth meanwhile ("consider it as we currently do").

**Full cascade (committed `bi-analytics` 6833671).** Regenerated Q1 + 2025 cost matrices on the corrected engines, then:
- **Routing report** — tender Q1 saving **€377k → €276,951 (9.4%)**. NEW **savings split** (`build_final.py` + §00 section): DB Schenker reroute **€168,585 (61%, LOW confidence)** vs €108,366 (39%) firm; 87% of saving lands on Maersk+Hermes. Fixed staled DB Schenker prose (1,076→2,048, must-freight 165→299).
- **DB Schenker validation** — 6,606 moved (was 7,593), 100% eligible.
- **Decision report** — rebuilt (`decision_scorer_2026q1` → `report_2026q1`).
- **Carrier overview + exec brief** — rebuilt on the corrected 2025 matrix. The rebuild *surfaced* a leak: the retired `MAX_VOLUME_CM3` was still showing in the Hermes eligibility table as a phantom live cap + stale 450 L prose → removed the dead constant, fixed `sections/hermes.md`.

## Decisions
- **GEL tubes stay on DB Schenker** (Niklavs, this session) — outside Maersk's confirmed ceiling.
- **Pure-girth assumed** for Maersk's "300" pending Stefan's confirmation; L+girth / L+W+H are documented sensitivities.
- **Management deck NOT updated** — deferred until Stefan confirms girth (avoid rendering a management number twice / shipping €377k).

## Commits
- `bi-analytics-main` (main, **not pushed**): **fceacc6** (engines + tests + impact script), **6833671** (cost-matrix regen → routing/decision/carrier-overview + savings split + Hermes 450 L cleanup). Derived parquets gitignored — commit code/deliverables, regen data.
- `brain` (this close): this quest-log + resume + harvest drafts + comms CLOSING, scoped to e3de8457 pathspecs only (shared tree dirty from parallel sessions; [[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]] sweep hazard).

## Pending external actions
- **Niklavs to send the girth clarification to Stefan (Maersk).** When the answer returns: if pure-girth confirmed, no change; if L+girth, re-run the engines + full cascade (Maersk oversize lane ~collapses, saving drops toward ~€200k) and refresh the deck.

## Process notes (harvested → drafts)
- Overstated the Hermes bulky-surcharge novelty before checking it was already encoded (self-caught).
- Called pure-girth "the only coherent reading" overconfidently; Niklavs' "would it even make sense?" pushback → checking industry convention reversed it to genuinely-ambiguous → ask. (→ examine draft + memory.)
- The full carrier-overview rebuild surfaced the 450 L leak the targeted routing regen missed — a render-from-source isn't clean while a retired constant still resolves.

## Update (continuation, same session) — Maersk girth confirmed = L+2W+2H

Maersk replied: **girth = L + 2W + 2H** (the rate card's `L+2W+2H` column = `length_plus_girth_cm`) — the **downside reading**, and the one I'd initially (wrongly) dismissed as incoherent. Asking was right; the answer was the non-obvious branch. Encoded as **`maersk-3.2.0`** (ceiling = `length_plus_girth_cm ≤ 300`, was pure-girth in 3.1.0); fixtures 18/18 (BG oversize now ceiling-rejects — band unreachable; CH/DE-fuel dims kept under the ceiling).

**Consequence:** most per-country EU oversize surcharges become **unreachable** (their l2w2h standard threshold ≤ the 300 ceiling) → the Maersk EU oversize lane is essentially standard-parcels-only.

**Re-ran the full cascade** on 3.2.0 + the now-committed `hermes-2.2.0` flat-7% fuel (Niklavs' change, `052d3c4`). New numbers:
- Tender Q1 saving **€276,951 → €201,916 (6.8%)**.
- DB Schenker reroute saving **€168,585 → €107,684 (53% of total, still the low-confidence slice)**.
- Parcels moved off DB Schenker **6,606 → 4,490**; DB Schenker freight **2,048 → 4,191** (must-freight 467).
- Rebuilt routing report + split, DB Schenker validation (4,490, 100% eligible), decision report, carrier overview + exec brief. Commit **`a96e449`**.

**Girth question now CLOSED.** Remaining open: management deck refresh (now on the firm €201,916), and the **committed Hermes test suite is red** (21 fixtures still assert pre-2.2.0 fuel — pre-existing from `052d3c4`, Niklavs' to fix/commit).

## Update 2 — all 4 principal-facing reports current + the "not DBS-only" finding

Niklavs cares about **4 reports**: carrier overview, decision report, routing report (Q1), and the **annual report**. First three were rebuilt on 3.2.0 in the cascade above; the **annual report** (`annual_2026/`) I'd missed — rebuilt it: `q1_base.py → build_annual.py → annual_report.py` (skipped `aggregates_2025.py`, which reads `real_*` actuals + volumes, unaffected by engine corrections). **Annual saving €997,720/yr (7%)**, band €969k–€1,026k; same split (DBS reroute €525,360 / 54% low-confidence). q1_base reconciled to the 3.2.0 routing within €1.

**`annual_2026/` is entirely UNTRACKED in git** (never committed by anyone) — flagged to Niklavs; commit deferred to him (the other 3 reports' regens are committed in `a96e449`). The annual rebuild sits on disk, uncommitted.

**Key finding — the Maersk girth change is NOT DBS-only.** Measured on the 3.2.0 Q1 cost matrix: **20,171** parcels lose Maersk-EU eligibility vs pure-girth, of which **13,170 (65%) are currently on NON-DBS carriers** (UPS/other incumbents) and 7,001 on DBS. So the bigger routing effect is whole-book oversize parcels that the tender would have moved to Maersk-EU re-homing to pricier carriers — which is why the saving fell ~€75k, beyond the DBS slice. (This is why all 4 reports, not just the DBS validation, needed the redo.)

# EU Tender 2026 — final adversarial (red-team) audit

**Date:** 2026-06-09 · **Auditor:** Jebrim · **Audited state:** bi-analytics `39c4595` (committed HEAD), `NFE/projects/2_EU_tender_2026/`
**Method:** 80-agent workflow — 11 carrier-engine finders + 8 cross-cutting finders, every material (tier a/b) finding independently re-derived by an adversarial refuter prompted to *disprove* it. Plus one live-mart provenance spot-check (the choice you made at scoping: trust the local Q1 actuals parquet, spot-verify against the live mart). Nothing below survived on a single agent's word.
**Tier key:** (a) conclusion-level — would change a recommendation or the decision; (b) number-level — shifts a figure, not a call; (c) cosmetic — label/prose.

---

## The answer you asked for: is there anything tier-(a)?

**Yes — but it is concentrated in one place, and it is about the *magnitude* and the *Hermes-add* call, not a broken computation.** The headline arithmetic is sound (`€377,471 / 12.77%` ties end-to-end and independently re-derived to the euro). The directional calls — run the tender, migrate off UPS, keep Maersk on France, decline DPD's new offer, DB Schenker for freight — **survive**. What does *not* survive is the claim that the saving is a *conservative floor*, and the confidence behind *adding Hermes*.

Two tier-(a) clusters:

1. **The saving leans >100% on engines that cannot be validated against their own actuals** (confirmed by the audit *and* the live mart).
2. **A live-mart provenance gap the local audit structurally could not see** — the Q1 baseline file is a 3-carrier subset, and the live mart contradicts the "Maersk = France-only" foundation. **This is the single thing I'd confirm before anything goes to management.**

Everything else is tier-(b)/(c): stale trust-gate docs, missing caveats on the exec brief, per-lane number wobbles. Detail below.

---

## TIER (a) — conclusion-level

### A0 — [MUST CONFIRM FIRST, live-mart] The Q1 actuals baseline is a 3-carrier subset, and "Maersk = France-only" is contradicted by the live mart
- **What the project assumes:** `data/actuals_2026q1.parquet` (the local ground truth, 189,917 rows) contains only **UPS / MAERSK / DB SCHENKER**, and treats Maersk as **France-only** (MAERSKFR, 27,447 parcels). The entire Maersk recommendation — keep Maersk on FR, the "single biggest lever," €396k routing slice — is built on that FR lane.
- **What the live mart says (2026-Q1, `shipping_mart.fact_shipments`):** Maersk is **not** France-only. **MAERSKUK = 32,342 — *larger* than MAERSKFR = 27,624** (+ SE 13, FI 8). There is a UK Maersk lane bigger than the French one that the local baseline file excludes entirely.
- **Why it's tier-(a):** if MAERSKUK is **in** the EU-tender scope, there is a ~32k-parcel Maersk lane unaccounted for in the keep-Maersk decision; if it's **out** of scope (post-Brexit UK handled separately), the FR-only framing is defensible but is nowhere stated, and the baseline-subset choice needs to be a documented decision, not a silent filter.
- **Status: RESOLVED (2026-06-10, principal).** MAERSKUK is a **separate deal, out of EU-tender scope** — the FR-only baseline is deliberate and correct, not an accidental subset. Consistent with `docs/open_questions/maersk.md` (FR/SE/FI/IE on a separate pre-existing Picanova-Maersk arrangement, not re-quoted on the tender rate card). The audit correctly flagged "confirm scope"; the answer is "intentionally scoped out." No action.
- **Evidence:** live mart `SELECT shipping_provider_group … WHERE shop_order_created_date IN 2026-Q1` (Maersk split MAERSKUK 32,342 / MAERSKFR 27,624 / SE 13 / FI 8, reconciles to 59,987 total); vs `actuals_2026q1.parquet` providers = {UPS, MAERSK(FR), DB SCHENKER}. Access caveat: the spot-check ran via a direct SELECT-only connection (`tcg_nfe` / `bi_stage_dev` gold mart) because the Redshift MCP wasn't registered this session; scope was "all production lines," which includes US carriers (OnTrac/USPS/Asendia-USA) presumably out of EU-tender scope.

### A1 — The selected portfolio is dominated by Hermes + Maersk-EU, neither reconcilable against own actuals
- **Confirmed (independently re-derived):** in the full-year scenario selector, the `renew_maersk_plus_hermes` portfolio scores **+€645,126**; the same portfolio **without Hermes** (`renew_maersk`) scores **−€199,435**. So Hermes' marginal contribution to the *selection metric* is ~€844k — more than the whole saving. Maersk-EU is the "single biggest lever" and prices **0 of 27,452** Maersk-shipped parcels (Maersk ships FR/SE today, the EU engine doesn't price FR/SE) → zero own-actuals overlap to validate against. Hermes has **zero** Picanova history at all (**confirmed true-zero in the live mart** — no Hermes/Evri anywhere in 2026-Q1).
- **Read the −€199k correctly (see A5):** the negative is **not** "renewing Maersk loses money operationally." It is the scenario metric (`mandatory_saving`) having **no per-parcel do-nothing floor** — renewing Maersk lets the over-pricing Maersk engine *capture* ~212k parcels that do-nothing left at their cheaper real invoice, repricing that tail up ~18%. Hermes, by under-pricing, captures the same tail cheaply. So the metric structurally **rewards whichever unvalidated engine bids lowest on the uncovered tail** — which is exactly why the two least-validatable engines dominate the pick. This *sharpens* A2; it does not flip the directional call.
- **Why it's tier-(a):** the two carriers carrying the selected portfolio are the two that can't be checked against what they'd actually invoice, taken at **face value, no bias correction** (locked, `PLAN_final_setups_2026q1.md:60`), and the selection metric amplifies their under-pricing.
- **Scope note:** these figures are the **full-year scenario scorer** (`scenarios.parquet` / `decision_scorer.py`), the portfolio-*selection* step — distinct from the Q1 routing (`routing_stats.json`) that produced the €377k headline. Treat the −€199k as "why the selector picked Hermes," not a direct claim about the €377k.
- **Evidence:** `scenarios.parquet` rows — `renew_maersk_plus_hermes` mandatory_saving €645,126 / `renew_maersk` −€199,435 (reproduced to the euro); hermes winning slice ~84k parcels ratio 0.893; maersk-EU 60,523 parcels / €396k; `report_2026q1.py:354-360` ("single biggest lever … face value").

### A5 — The scenario selector (`mandatory_saving`) has no per-parcel do-nothing floor — it can price a parcel onto a carrier costing *more* than today
- **Confirmed (from code + data):** `decision_scorer.py:189` sets each parcel's cost to `coalesce(cheapest_active_bid, real_total_eur)` — the cheapest *active bid*, falling back to the real invoice **only when there are zero bids**. There is **no** `min(bid, real_invoice)` per parcel. So a NEW_OFFER engine that bids on a parcel "wins" it at its engine price even when that price exceeds what the parcel actually costs today.
- **The effect, measured:** do-nothing leaves **350,647 parcels uncovered** (€1.89M) — these are parcels whose current carrier isn't a modeled incumbent (DIRECT LINK + misc), sitting at their real invoice. Flipping Maersk to NEW_OFFER **covers +212,111 of them** (uncovered cost €1.89M → €0.79M), but total cost **rises €199,435** → the ~€1.1M tail gets repriced **+18%** onto Maersk's over-pricing engine. `migration_saving` (the cherry-pick metric, `:192`, `max(0, real − effective)`) floors at 0 and so reports **+€1.1M** for the *same* scenario — the realistic saving sits between the two.
- **Why it matters:** `mandatory_saving` systematically **penalizes over-pricing engines and rewards under-pricing ones**, because over-priced bids are forced into the total while a real operator would simply not migrate those parcels. This is the structural reason the selected portfolio leans on the least-validatable (under-pricing) engines (A1/A2). **Fix:** floor each parcel at `min(best_bid, real_invoice)` (never migrate a parcel onto a carrier dearer than its do-nothing cost), or report the saving as the `[mandatory, migration]` band, not the point estimate.
- **Evidence:** `decision_scorer.py:186-198` (coalesce, not min); `scenarios.parquet` do_nothing (n_uncovered 350,647 / uncovered_cost €1,894,573) vs renew_maersk (n_uncovered 138,536 / €786,977, total +€199,435, migration_saving €1,098,482).

### A2 — The "unbiased" trust-gate is a winner's-curse construction, not an accuracy gate
- **Confirmed:** `_refresh_bias_table.py:78-98` builds the trust population as the per-shipment **argmin** across engines, then measures bias on that winning subset (lines 101-121). An engine that over-prices its whole book still shows ratio ≈ 1 on the slice where it happened to bid low enough to win. On the *same* Q1 data, **full-eligibility** ratios show the real picture: maersk **1.78**, dhl_paket **1.89**, dhl_express **2.40**, fedex **2.33**, hermes **1.25**, gls **1.40** vs today. Where own-actuals *do* exist (DHL's real book), the engine prices **1.087** — real over-pricing.
- **Why it's tier-(a):** a modest, defensible bias haircut on the migrated-to carriers collapses the saving (+10% → ~7%; +25% → far less). The gate that says "these engines are unbiased, the saving is real" is measuring the selected cheap tail.
- **Evidence:** `_refresh_bias_table.py:39` (reads full-year `cost_matrix.parquet`, not Q1) + `:78-121`; `report_2026q1.py:457-493` recomputes the same winning-slice ratio for the report; `data/_bias_refresh.parquet` full_eligibility vs winning slices.

### A3 — Hermes engine omits a carrier-defined €249k+ "Manual Handling" oversize tier (biases the lean-on carrier cheaper)
- **Confirmed:** Hermes' Round-1 reply defines a **Manual Handling EU €2.63** tier ("oversized items that do not yet fall into bulky"), and the product spec defines standard as L≤120 **AND** W≤60 **AND** H≤60 **AND** girth≤300. The engine only models BULKY (longest >120) and prices everything ≤120-longest as clean standard — it never checks the W/H/girth cross-section. **98,884 eligible parcels (19.4%)** breach the cross-section (driven by d_mid>60) and get no charge → **~€249k** under-charged on the eligible population, plus smaller omitted surcharges (Volume>150L, NL tiers) and a fuel-basis reinterpretation.
- **Why it's tier-(a):** it biases *down* exactly the engine the headline leans on — compounding A1/A2.
- **Evidence:** `hermes_response_CLEANED.md:34`; `202511_Country Details_EN.pdf` p2; recompute on `cost_matrix.parquet` hermes-eligible `filter(d_max≤120 & (d_mid>60|d_min>60|girth>300))` = 98,884 × €2.63 (ex-AT) = €249,001.

### A4 — Güll's contribution rides on an unconfirmed (HELD) rate card
- **Confirmed (partial — bounded):** `guell-1.0.0` is built from the proposal PDF with **no carrier reply** ("14/14 fixtures are the only confidence signal"). A real but bounded slice of saving (~€42.5k full-year / ~€2.9k in the Q1 headline) depends on rates no carrier has confirmed. Engine transcription is faithful — the risk is the offer being provisional, not a bug. **The project discloses this** (HELD flag), so it's an honest exposure, not hidden. *(Live-mart footnote: Güll actually has 1,327 Picanova shipments in Q1, hidden inside the mart's "Other" bucket — see B-new-1; small own-actuals exist that could partially sanity-check the engine.)*

> **Tier-(a) bottom line.** A0–A5 are one story: **the saving's magnitude and the Hermes-add call rest on engines that can't be ground-truthed, scored at face value, with a trust-gate that doesn't actually gate and a selection metric (A5) that structurally rewards under-pricing.** None of this flips the *direction* (UPS is genuinely dear; migrating off it saves money; keep-Maersk-FR is robust — the cheapest alternative on those FR parcels still loses to MAERSKFR's €4.72 avg). It flips the **framing**: €377k/12.8% is a **Q1 off-season best case, not a conservative floor**, and "add Hermes" is the least-supported call in the deck.

---

## TIER (b) — number-level (verifier-confirmed; shifts a figure, not a call)

**New, from the live-mart spot-check (the local audit could not find these):**
- **B-new-1:** Live mart shows **Güll 1,327** (in "Other" bucket) and **Austrian Post 629** (POSTAT in "Post" bucket) Picanova shipments in Q1 — both treated as zero-actuals greenfield by the project. Small, but they *do* have own actuals that could partially trust-gate those engines. (Hermes & GLS confirmed **true** zero ✓.)
- **B-new-2:** Live mart shows **FedEx 12,548** (FXEHD/FXESPPS) — but FXEHD reads as US home-delivery, likely **out of EU-tender scope**. The "FedEx = new entrant for EU" framing probably holds; worth a one-line scope confirm given the project also calls FedEx greenfield.

**Trust-gate / bias documentation (the recurring theme):**
- `bias_table.md` is **stale on every winning-slice ratio** vs live `_bias_refresh.parquet` (Hermes doc 0.588 → live 0.893; Maersk 0.849 → 0.735; AP 8,803 wins @0.701 → live 33 @0.336; DPD-PL full-elig 2.957 → 1.461). Corrupts trust-gate evidence; does not flip the headline (the report consumes live `scenarios.parquet`, not the doc).
- The stale Hermes **0.588** ratio propagated into the **carrier-facing report + 10 doc files** — overstates Hermes cheapness in prose.
- `bias_table.md` documentation **states FedEx is "unwired / never bids,"** but `_decision_sets.py:53,72` wires FedEx as NEW_OFFER and it wins 7,738–20,331 (Q1) / up to 453k (full-year) parcels. A reviewer trusting the doc would not know an un-trust-gateable engine is winning savings-bearing slots. (Recomputed winning ratio 1.113 → underlying savings defensible; the risk is governance, not the number.)
- The "trustworthy" gate keys on **engine-rebuilt** status, **not reconciliation to actuals** — so Hermes (zero actuals) is labelled "trustworthy floor."

**Per-carrier number issues:**
- **dhl_paket:** engine over-prices its **own** actuals ~1.9× (the entire gap is the bulky surcharge firing on 113,575 flat poster parcels with **no physical/weight cross-check** — the [[S182_e3648d0d_routing-report-size-tiers|S182]] hybrid rule was *not* applied here). Real mechanism; the "inflates the baseline toward the tender" framing was **refuted** (verifier a→b). Inflates the do-nothing baseline, but the headline reads off the Q1 pipeline.
- **dhl_express:** Q1 matrix applies the **full-year** pickup line-haul constant (€0.4144/parcel) to a Q1 population; demand per-kg matrix values are **not** in the offer (self-derived).
- **gls:** EFTA clearance €25/parcel = 9.1% of GLS cost hinges on an unresolved per-parcel-vs-CCD assumption; bias-table row predates the gls-2.0.0 rebuild.
- **guell:** AT eligibility over-rejects on a length+girth cap where the offer specifies girth-only; CHF→EUR FX held at 1.05 (low end of plausible range).
- **austrian_post:** trust gate mis-grained (carrier-blanket masks AT +23% / CH −8%); Sperrgut over-prices ~€20k on AT.
- **dpd_pl_current:** **SE engine under-prices DPD ~20%** (validated ratio 0.797) and books 5,744 SE parcels that arguably should route to GLS — understates routed total ~€15k/Q (verifier downgraded the "wrong-winner erases the call" claim a→b); the ~9% negotiated discount is a **fitted parameter** absent from the offer; DE/IT/ES forward bids (the largest, 365k) are essentially unvalidated (DPD's own book has ~5 DE parcels).
- **dpd_pl (new, declined):** intentionally drops a documented €0.176/parcel energy fee; per-lane validation not uniformly unbiased (FR +8%).
- **fedex:** fuel %s (RE 20.5% / IE 34.5%) are self-reconstructed estimates, not carrier-supplied.
- **ups:** forward GRI applied at **5%** but the project's own UPS research note says 2026 GRI = **5.9%**; LPS invoice-adjustment **inconsistent across tracks** (full-year halves LPS 50%, Q1 routing keeps it); UPS can never *win* a non-incumbent lane (no engine).

**Headline / decision framing:**
- The saving is **not a hard floor** — a modest GRI/fuel/peak stress on the new-offer slice erodes it: +5% GRI → 10.9%, +10% GRI → 8.9%, combo → ~5.5% (verifier trimmed the finder's magnitudes but confirmed the direction; downgraded a→b because the report does *not* itself mislabel the whole figure as a floor).
- Decision report leaderboard uses a **GRI-free** baseline while the routing report **applies** GRI — internal inconsistency.
- `maersk_vs_dbs.md` (freight-partner basis) stale/internally contradictory vs executed routing.
- Full-year headline savings drift slightly from live `scenarios.parquet` (635k vs 645k; 732k vs 726k).
- **Maersk ROW demand surcharge fires in the Q1 window but is left unwired** — under-prices the headline carrier slightly.

---

## TIER (c) — cosmetic / prose-only (representative; full list in workflow output)
- `bias_table.md` describes pre-rebuild DPD-PL and Hermes engines; `ASSUMPTIONS.md` Maersk status note stale/inverted.
- **FR-floor caveat** (DPD over-prices France) **absent** from the carrier overview; **carrier-only-at-actuals** caveat stated only in the routing report.
- maersk EU/IT oversize trigger edges (~€1k swings); maersk engine-doc §10.1/§10.2 stale (describe superseded behavior — engine is actually correct).
- dhl_paket committed full-year matrix stamped `1.2.0` not `2.2.0` (stale name; Q1 partition is correct).

**Cleared on verification (looked alarming, refuted — worth knowing what was checked):**
- **GLS Stettin→Köln line-haul = €0** (looked like a €0.5–2M/yr omission that flips GLS negative): **refuted — carrier-confirmed correct**, not an omission.
- **Maersk EU oversize = €1.75M / 40% of EU cost** on two unconfirmed interpretations: arithmetic right, but the engine chose the **conservative (cost-maximizing)** reading — it biases *against* the tender (understates Maersk savings), so it's safe to present; the permissive reading is an **open carrier question**, not an error.
- **`fedex-1.0.0` stale in the full-year matrix:** real, but the canonical decision basis is the Q1 (v2) pipeline, so no headline impact.
- **`bias_table.md` "saving is real on ratio<1" vs "0.588 too good to be true":** refuted — the doc explicitly carves out Hermes as provisional; no live contradiction.
- **Headline €377,471 / 12.77% ties end-to-end** with no re-statement gap — **confirmed** (and independently reproduced by a build re-run that changed only floating-point trailing digits).

---

## Per-carrier confidence

- **Maersk** — engine transcription clean; FR-keep call robust on cost. **CONFIDENCE: medium-low** — pending the **MAERSKUK-scope** question (A0) and the fact the EU engine has zero own-actuals overlap (A1).
- **DHL Paket** — largest incumbent; engine over-prices its own book ~1.9× via an un-cross-checked bulky surcharge. **CONFIDENCE: medium** (baseline-inflation, but Q1 pipeline is what's scored).
- **DHL Express** — no own actuals; full-year constant on Q1; offer-absent demand matrix. **CONFIDENCE: low.**
- **GLS** — true greenfield (confirmed zero history); line-haul confirmed correct; EFTA clearance assumption open. **CONFIDENCE: medium.**
- **Güll** — HELD/unconfirmed rate card; small own actuals exist (1,327, hidden in mart "Other"). **CONFIDENCE: low** (disclosed).
- **Austrian Post** — no clean parity test; mis-grained gate; small own actuals exist (629). **CONFIDENCE: low-medium.**
- **Hermes** — **the exposed one.** Zero history (confirmed), face-value, omits a €249k defined surcharge tier, carries the saving. **CONFIDENCE: low.**
- **DPD-PL (new, declined)** — decline call holds; energy-fee + FR over-price noted. **CONFIDENCE: medium-high** (the call is to say no).
- **DPD-PL (current, kept)** — aggregate −0.4% vs actuals validated; SE under-prices 20%; DE/IT/ES largely unvalidated; 9% discount is fitted. **CONFIDENCE: medium.**
- **FedEx** — self-reconstructed fuel; "EU greenfield" framing needs a scope confirm (12,548 FedEx shipments exist, likely US). **CONFIDENCE: low-medium.**
- **UPS** — priced from own actuals (unbiased by construction); GRI 5% vs 5.9% note; cross-track LPS inconsistency. **CONFIDENCE: medium-high.**
- **DB Schenker (freight)** — must-freight residual sized at **165 shipments / €24,462 / 0.81%**; basis doc stale. **CONFIDENCE: medium-high.**

---

## What I could not verify (and why)
- **Whether the new-offer engines (Hermes, Maersk-EU) over- or under-price their *true* forward cost** — structurally impossible from the repo: zero own-actuals overlap. The full-year winning ratios (0.73/0.89) and the documented under-modelling all point the *same* direction (they under-price → saving overstated), but the magnitude is unquantifiable in-repo.
- **MAERSKUK / FedEx-FXEHD tender-scope** — needs your confirmation of the tender's population definition (EU-only? which production lines?). The local baseline filters them out; I can't tell if that's intentional.
- **Full-year / annualised behaviour** — the decision scorer reads **only** the Q1 matrix; forward fuel is not projected and Q4 peak/demand are €0 in Q1 bids. The Q1→annual re-weight is "pending, not a ×4" but its magnitude isn't quantified anywhere. This is the largest unhedged risk after A0–A3.
- **Source rate-card PDFs/xlsm** for several carriers (UPS .xlsm is binary; FedEx FAQ PDFs; AP factsheets) — relied on the engines' transcriptions + offer summaries.
- **Live-mart access** ran via a direct SELECT connection (MCP unregistered) on `bi_stage_dev` gold mart — provenance is sound but flag if you want strict MCP-only or a different scope.

---

## Verdict — do the headline conclusions hold?

**The decision holds directionally; the headline number does not hold as presented.**

- ✅ **Run the tender, migrate off UPS, keep Maersk on France, decline DPD's new offer, DB Schenker for freight** — all robust to the audit. UPS is genuinely expensive; the FR-keep beats every alternative on those parcels; the freight residual is tiny and sized.
- ⚠️ **"Add Hermes for coverage" is the weakest call** — it carries the saving, can't be validated, is taken at face value, and provably omits a defined surcharge tier. Defensible as a *coverage* play; not as a *saving* play at the booked magnitude.
- ⚠️ **€377,471 / 12.8% is a Q1 off-season best case, not a conservative floor.** A modest, defensible GRI/fuel/peak stress on the new-offer carriers takes it to single digits.

**Must fix / confirm before this goes to management:**
1. ~~**Confirm the MAERSKUK / baseline-scope question (A0).**~~ **RESOLVED 2026-06-10:** MAERSKUK is a separate deal, out of tender scope; FR-only baseline is correct. No action.
2. **Re-frame the headline** from "conservative floor" to "Q1 best case; annual figure is a separate re-weight," and **state the Hermes/Maersk-EU face-value, no-actuals caveat** on the exec brief (it currently omits both the UPS-GRI and the Q1-annualisation caveats — see B).
3. **Apply a bias haircut (or a stated range) to the Hermes + Maersk-EU migration** instead of booking face value, so the saving is a band, not a point. The full-eligibility ratios give a principled haircut.
4. **Fix the selector floor (A5).** Floor each parcel at `min(best_bid, real_invoice)` in `decision_scorer.py` so the model never migrates a parcel onto a carrier dearer than its do-nothing cost — or report each portfolio as its `[mandatory_saving, migration_saving]` band. Today's `mandatory_saving` understates over-pricing engines and overstates under-pricing ones, which is why the pick leans on the unvalidatable engines.
5. **Regenerate `bias_table.md`** and the 10 propagated docs (all stale post-rebuild), and correct the "FedEx unwired" governance statement.
6. **Note** the Güll/AP small-own-actuals (could partially validate those engines) and the UPS GRI 5% vs 5.9% / cross-track LPS inconsistency.

**Cosmetically nothing is broken in the computation** — the pipeline ties, the engines transcribe their offers faithfully, and the conservative choices (Maersk oversize, GLS line-haul) were verified as deliberate, not bugs. The exposure is entirely in **what the unvalidatable engines are allowed to claim** and **how the number is framed**.

---

*Full per-finding detail (all 103 findings + every adversarial verdict) in the workflow output: `tasks/wvxtih146.output` (run `wf_91d323f7-a64`, 80 agents, 4.5M tokens).*

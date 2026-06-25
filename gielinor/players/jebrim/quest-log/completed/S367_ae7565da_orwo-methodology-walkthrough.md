# S367 — ORWO tender: methodology walkthrough doc + cross-pricing / volumetric sanity checks

**Player:** Jebrim · **sid8:** ae7565da · **2026-06-25**
**Continues:** [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]] (ORWO tender umbrella) · [[S283_60de5609_orwo-tender-assumptions-and-carrier-questions|S283]]/[[S284_f1b5f17c_orwo-engine-sanity-and-assumptions-lock|S284]]/[[S285_2bf7cf70_orwo-tender-logic-walkthrough-and-us-disregard|S285]] (assumptions/engines/walkthrough) · S286 (annualization). Niklavs is presenting the tender; this session built the explainer + stress-tested the method.

## Ask

"Remind me where we stand on ORWO and what we've done" → then build an HTML doc explaining *exactly* what was calculated and how, for him to read + present. Then a chain of sharp methodology challenges, each verified against the engines/cards/mart, each folded into the doc.

## Delivered — the methodology walkthrough

`NFE/projects/7_ORWO_tender_2026/methodology_walkthrough.html` (self-contained, dark theme mirroring `annual_2026/annual_report.html`). Sections 00–08: the question → population → cost basis → trust gate → reprice engines (4 formula cards) → **weight & dimensions** → per-lane optimum → annualization → assumptions ledger. Opened in browser.

## The challenges Niklavs raised, and what each surfaced (all verified, not asserted)

1. **Service level per carrier?** — Verified from the cards: book is ~99% standard/economy ground (express = €4.4k / 1.25% of UPS freight, 88 lines). Competitor engines price standard ground (GLS Euro Business / Maersk Home Delivery); Letterbox/PUDO excluded by policy (ORWO door-delivers). Within Home Delivery, Maersk already picks the cheapest local carrier (GB→Yodel €3.45 over Evri €3.86); GLS has a single home product. → already cheapest-within-mode. §04 service callout added.
2. **§1 over-indexed on UPS** (3 separate framing artifacts) — root cause: project built UPS-first (Phase-1 vertical slice), so the docs are UPS-framed. Fixed §1 (population-first: DHL DE-domestic = ~90% of the base, UPS the ~10% cross-border slice), §2 (cost-bucket table was all-UPS vocab → DHL-buckets-identically note), §5 lane table (broke out FR + all tails with their winners). Ran a full UPS-bias read-through pass.
3. **What are the 34k/93k?** — Live mart: `source_system='ORWO'` (consolidated bulk-mail, UPS 37.9k trk / DHL 374k) + `'Picturator'` (1:1, UPS 94.7k / DHL 227k), both `production_site='Wolfen'`. Two order platforms feeding one plant; keying on `source_system='ORWO'` drops the Picturator cross-border mass = the false "92% domestic."
4. **FR alternative if UPS goes?** — `per_lane_optimum` already moves *every* UPS cross-border lane to a competitor; FR→Maersk −€1,147 H1 (near-tie, Maersk edges it). No lane stranded. §5 exit-UPS coverage callout + full lane table added.
5. **Do contracts use dims for *rates*, not just surcharges?** — YES for some: UPS Economy-DDP (GB/US) + Expedited rate on `max(actual, volumetric)`; GLS-Euro on `L×W×H/6000`. Captured via UPS invoice `billedweight` (= max(actual,vol), 100%). DHL-domestic + Maersk-EU weight-only by contract. §04 wording fixed + weight-basis callout.
6. **Candidate set — does DHL reprice UPS's book?** — No. Incumbents (UPS/DHL) price only their own book (trust-gate); only GLS/Maersk reprice the whole portfolio. Ran a **cross-pricing probe** (DHL-Intl on UPS lanes, UPS on DHL core): both lose every contested lane (DHL-Intl GB €276k vs €53k; AT €122k vs €108k). The raw −€71.8k "gain" = model-vs-own-actual artifact (DE/FR/US), discarded. → not worth implementing. §6 candidate-set note.
7. **How is billed weight valid across different dim factors?** — One measured weight per parcel = the incumbent's billed weight (UPS's, for the cross-border lanes). Competitors inherit it, don't recompute. UPS's /5000 ≥ GLS /6000 ≥ Maersk gross → inherited weight is an upper bound on each competitor's billable → **conservative** (cost overstated, saving understated). New §05 "Weight & dimensions" section.
8. **Recompute GLS on its own /6000?** — Ran the ceiling (billed×5/6 on all UPS parcels): extra saving **−€261 H1 / ~−€640/yr**, no winner flips. Tiny because cross-border parcels are light and sit at the GLS card's 1 kg floor band, so a 17% rescale rarely crosses a band boundary. → conservative approximation costs essentially nothing. §05 closing line added.

## Where we stand (the number, unchanged)

Headline holds: **−€343k/yr (−3.2%), band −€325k…−€362k**, on €10.6M carrier-comparable spend. Recommendation: keep DHL on DE-domestic; exit UPS cross-border → GB→Maersk, AT/CH→GLS (≈95% of saving). The three opens Niklavs closed verbally this session: **no carrier dispatch** (Picanova rates assumed), **GRI held 5%**, **US out of scope** — all already reflected in the engine/doc.

## Probes (throwaway, not committed to NFE)

Cross-pricing probe + GLS-volumetric ceiling were inline python against the existing switch parquets + rate tables (read-only, no files written to NFE). Conclusions captured in the doc + this entry; scripts not retained.

## Decisions

- Methodology walkthrough is a reading/Q&A doc, distinct from the savings report (`annual_report.html`). Both kept.
- Cross-pricing UPS/DHL as challengers: **not worth implementing** (probe shows no lane changes hands; both lose every contested lane).
- GLS own-volumetric recompute: **not worth implementing** (<€650/yr, band quantization).
- Candidate set {current incumbent, GLS, Maersk} stands; documented as a deliberate scope choice, not an oversight.

## Cascade

NFE (standing auth, committed separately): NEW `7_ORWO_tender_2026/methodology_walkthrough.html` (sections 00–08, iterated across the session's challenges). No other NFE writes. Brain: this quest-log entry (completed/), 1 examine draft (build-order-is-not-presentation-order), light dated note appended to `inventory/orwo-tender-resume__60de5609.md`, comms OPEN(late)+CLOSING.

## Main-brain changes

None to globals/meta/rituals. Player-scope only (Jebrim quest-log + inventory + examine draft + comms).

## Pending external actions

None pending this session. Carried-open on the umbrella (principal's, unchanged): the tender deliverable itself is his to present; SEND-dispatch is moot (rates assumed, his call).

## Open (carried on umbrella [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]])

Umbrella ORWO threads unchanged: uninvoiced-carrier validation (`__cb17c25e`, but FKBRING/CIRRO now excluded per [[S366_422d59ed_orwo-fkbring-cirro-exclusion|S366]]), returns-cost dig (`__0888690d`). This session's deliverable (the methodology doc) is shipped → S367 graduated to completed/.

## Post-close addendum (same session, ae7565da) — GRI / savings-baseline check

Two follow-up questions after the first wrap, both verified live (READ-ONLY silver invoices — the INVOICES-ONLY cost basis; mart drops the per-band/per-month detail):

1. **What baseline is the −€343k against?** Verified in `annual_orwo.py`: the do-nothing side = current per-parcel cost × volume, **no ×1.05**. So the saving is **vs current (flat 2026) costs, GRI-EXCLUDED.** The 5% GRI is a forward-hypothetical placeholder used only to size the *incumbents' own 2026 offers* (GRI-avoided), NOT baked into the headline. Implication: the −€343k is conservative vs a realistic "incumbents raise ~5%" do-nothing (switching the cross-border lanes also dodges UPS's GRI on that ~€1M/yr spend ≈ order of +€50k/yr, uncounted).
2. **Has a GRI already hit in 2026?** **No, for both** — confirmed from invoices:
   - **DHL: flat Sep 2025 → Jun 2026.** Base bands €3.35/4.95/10.55/2.79 every month, min=max; Maut €0.19 + energy €0.04 flat. Pushed past base to **all-in net per parcel** (freight + all surcharges): bis-5kg 4.89 (Jan) → 3.73 (Mar) → 3.66 (Apr) — March is a **post-peak LOW** (Q4 Peak/PiP unwinding), not a step up. New March prod codes (2511/2681/101510315) = a separate ~4.4k/mo stream, not a surcharge on the existing book.
   - **UPS: no mid-2026 GRI.** Dom. Standard band floors 3.26/3.82/5.79 + TB Standard 4.15/4.77/5.40 flat Mar–Jun. UPS silver doesn't reach 2025, so the Jan-1 annual step isn't invoice-visible (use the OLD-vs-NEW UPS rate cards for that).
   - The "March cost rise" intuition most likely = the **DHL returns surge from ~March 2026** (separate thread `__0888690d`), which is returns *volume*, not an outbound rate hike.

**Net:** current-cost baseline is genuinely flat 2026 rates; no GRI absorbed; the 5% is forward-only. Read-only — no NFE/brain content writes beyond this addendum + resume note + 1 examine draft.

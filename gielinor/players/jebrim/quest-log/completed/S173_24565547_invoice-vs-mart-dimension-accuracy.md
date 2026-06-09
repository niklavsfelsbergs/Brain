# S173 — Invoice vs mart package-dimension accuracy (topic 45)

**Player:** Jebrim · **sid8:** 24565547 · **Born:** 2026-06-09
**Repo target:** `bi-analytics-main/NFE/shipping_topics/45_invoice_vs_mart_dimension_accuracy/` (SEPARATE repo, uncommitted, principal-gated)

## Ask
Started as recall of the S167 carrier-invoice dimension-coverage finding, then escalated into a real analysis: how accurate are carriers' invoiced package dimensions vs our declared dims in `shipping_mart`, and which carriers actually *measure* (vs reprint our declared dims). Finished with a dark-themed HTML overview report.

## What happened (turn arc)
1. **Recall** — surfaced the S167 coverage map: ~10 carriers carry real measured dims, 5 carry oversize/handling-derived signal only, 3 (DHL feeds) nothing. Gave the grouped status table.
2. **Topic 45 build (shipping-agent pass 1)** — declared-vs-measured accuracy by `packagetype` for the 3 cleanest carriers (Maersk, FedEx, OnTrac). Key discovery: **mart dims are PCS-owned = our DECLARED dims**, so the comparison is declared-vs-measured (not circular). **Maersk turned out to be a passthrough** — it reprints our declared L/W/H verbatim (100% exact), no audit value. OnTrac measures faithfully (~85% within ±2cm); FedEx real but noisy. Also surfaced our-side declared-dim garbage (0.1cm floors, 1000cm ceilings).
3. **Passthrough-vs-measured discriminator (shipping-agent pass 2)** — extended to Asendia USA, USPS, DB Schenker, Direct Link, Yodel, UPS. Verdict: REAL = OnTrac, FedEx, Asendia USA, Yodel; REAL-subset = USPS (assessed slice), UPS (oversize slice); PASSTHROUGH = Maersk; INCONCLUSIVE (volume-only) = DB Schenker, Direct Link. Caught the **dual-field trap** on 4 carriers (a passthrough field + a measured field on the same invoice).
4. **PCS PL carrier mix (shipping-agent)** — at `production_site = 'PCS PL'`: DHL 45% (no signal), UPS 22% (oversize subset only), Yodel 8% (the one full-coverage independent measurement at scale). US measurers absent. Answer: **Yodel is the only at-scale independent measurement from PCS PL; UPS adds an oversize subset.**
5. **Yodel deep-dive (shipping-agent)** — declared-vs-actual by packagetype, ~86k clean parcels. **Coverage correction: Yodel's measured `actual_*` is only 6.9% populated, bursty (strong Oct 2025–Mar 2026)** — overturns the "full coverage" framing I'd relayed in step 3. Finding: we **under-declare the longest axis** (median +2cm, p95 +14, p99 +20.5); 60.6% of parcels >2cm bigger on ≥1 axis, 37.8% >5cm. Driver = **strapped/wrapped multipacks** (WICKELVERPACKUNG, strapped pizza boxes); fixed small boxes track well (MUG 97%, Poster 84%). Our-side DQ: a 22.5cm fallback floor stamped when box spec unresolved.
6. **HTML overview report** — built `package_dim_accuracy_overview.html` synthesizing the above; reskinned to the EU-tender routing-report dark theme (#0a0c0f / mint #00d4aa / Inter + IBM Plex Mono) on principal request.
7. **Parked + close** — principal pivoted to a new question (below) and asked to wrap.

## Decisions / findings that matter
- Mart `length/width/height/volume/length_plus_girth_cm` = **our declared (PCS-owned) dims**, NULL on ORWO/external. (`shipping-agent/reference/known-dq.md:43`.)
- A populated dim column ≠ an independent measurement. **Maersk, DB Schenker, Direct Link do not give an auditable measurement.**
- **PCS PL independent measurement ≈ Yodel only** (at scale), and even Yodel only on 6.9% of parcels.
- Real, actionable signal: **under-declared strapped/wrapped multipacks** → oversize/handling-surcharge + cost-mis-rating exposure. Size it on the ~86k measurable parcels.

## Parked for a future session (principal's pivot)
> **"What should we pull out of the NFE CLAUDE setup now that we have the brain system?"** — i.e. which conventions currently in `bi-analytics-main/NFE/CLAUDE.md` + `.claude/reference/*` (report-patterns, house-style, etc.) are now redundant with / better-homed in the gielinor brain. System-scope — likely a Guthix consultation. Niklavs will raise it in another session.

## Open items (recommended, not yet approved)
- **Coverage-note corrections** to `bank/drafts/notes/projects/2026-06-09-carrier-invoice-dimension-coverage.md`: demote Maersk (passthrough), DB Schenker + Direct Link (volume-only, no independent measurement) out of "real measured dimensions"; correct the Yodel "full coverage" line to 6.9%. Proposed this session, not applied (principal pivoted before greenlight).
- **Size the under-declaration exposure** (€) on the ~86k Yodel measurable parcels — does it correlate with oversize surcharges actually billed?
- **Raise the 22.5cm fallback-floor** declared-dim default with the declaration-pipeline owner.

## Sub-agent traces (this session)
- `S173_24565547_sa_invoice-vs-mart-dim-accuracy.md` (passes 1+2)
- `S173_24565547_sa_yodel-dim-accuracy.md` (Yodel deep-dive)
- `S173_24565547_sa_pcs-pl-carrier-measured-dim.md` (PCS PL carrier mix)

## Pending external actions
None pending. (bi-analytics topic 45 is uncommitted by design — separate repo, principal-gated.)

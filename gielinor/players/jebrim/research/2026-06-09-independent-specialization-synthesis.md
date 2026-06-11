# Independent specialization — synthesis + brainstorm (2026-06-09)

> Brainstormed while Niklavs was away. Question: what high-stakes project/specialization could he go independent on, and what do others in the space do? Built on three penguin research files (below). This is a strategy draft for review, not confirmed knowledge.

**Source research (penguin-authored, same date):**
- [[2026-06-09-parcel-audit-industry-landscape]] — the audit/refund-recovery SaaS market
- [[2026-06-09-carrier-tender-consulting-landscape]] — the carrier-procurement / tender consulting market
- [[2026-06-09-solo-ai-consulting-economics]] — solo/boutique consulting positioning + pricing

---

## The one finding that matters: the white space is exactly where Niklavs already stands

Two independent penguins (parcel-audit market + tender-consulting market) landed on the **same gap**, from opposite ends:

> **European, mid-market, multi-carrier, shipment-level re-rating against the shipper's own invoice actuals — plus tender/RFP design — delivered as transparent analysis-grade work.**

It sits in a seam nobody occupies well:

| Incumbent type | What they do | Why the seam is open |
|---|---|---|
| US contingency audit SaaS (Sifted, ShipSigma, Reveel, 71lbs, Refund Retriever) | Refund recovery + invoice error detection, % of refunds | **US/FedEx-UPS-centric**; EU "coverage" is shallow invoice ingestion, not real DHL/DPD/GLS/Hermes surcharge+zone+DIM logic. Contingency model structurally chases easy refunds, not deep savings |
| Enterprise advisory + freight-audit-payment (Shipware, Green Mountain, Intelligent Audit, Trax) | Managed advisory, multimodal, retainer + gainshare | Freight-first, **retainer-priced, enterprise-only** — out of reach for mid-market EU e-commerce |
| Big-firm sourcing (Kearney, Accenture, BCG, EY) | Strategic sourcing, parcel as a sub-line | **Category-grain benchmarking, not shipment-level re-rating**; day-rate, enterprise |
| EU freight-tender platforms (Transporeon, Städtler, 4flow, Caestra, Freightos) | Freight tender platforms + network consulting | Compare bids; **don't re-rate parcel mixes** against rate cards. No clearly-surfaced EU *parcel*-rate boutique applying US-grade re-rating |
| **The open seam** | **EU multi-carrier parcel+freight re-rating on actuals, transparent shown-math, tender design, mid-market, outcome-priced** | **This is the Picanova EU tender, productized.** |

**The methodology bar is the moat.** Both market penguins independently noted: most "savings analysis" out there is *benchmark comparison*, not *true shipment-level re-rating against the proposed rate card on the shipper's own dims/weights*. Even TransImpact's headline 48-hour turnaround is **black-box AI — they don't show the shipment math.** Niklavs already operates at the higher bar (9 version-stamped engines, a re-rating trust gate, bias-quarantine). The rigor that's "just how we work" here is the thing the market mostly fakes.

**Gainshare fits this domain better than almost any other.** P3's finding: % -of-savings pricing only survives where the outcome is *quantifiable and independently verifiable*. Invoice/procurement data is **the cleanest possible case** — auditable ground truth on both sides (before invoices, after invoices). The thing that makes gainshare risky elsewhere (attribution) is nearly solved here.

---

## The specialization candidates (brainstorm)

Ranked. Each: the wedge, the flagship high-stakes project, pricing, moat, risk.

### 1. The EU Multi-Carrier Tender Specialist  ⭐ recommended core
**Wedge.** "I run carrier tenders for European mid-market e-commerce (€5–50M shipping spend) and re-rate every shipment against the offers on your own actuals — so the savings number is defensible, not a benchmark guess."
**Flagship high-stakes project.** Take a shipper through a full multi-carrier tender: ingest 12 months of invoice actuals → build/run per-carrier rate engines → score portfolio scenarios → recommend the 4–6 carrier mix + routing → hand them a board-grade decision report. *This is literally the Picanova EU tender.* High-stakes because it drives a 7-figure sourcing decision; a wrong sign costs real money — which is exactly where his rigor is the differentiator.
**Pricing.** Fixed-fee diagnostic entry (€8k–€25k, per P3 audit band) → gainshare on verified Year-1 savings (15–30% is the market norm; TransImpact avg 23.6%, Shipware 21.5%, Renaissance 10–30%).
**Moat.** Shipment-level re-rating engines + accumulating EU carrier rate-card/surcharge knowledge + transparent shown-math.
**Risk.** Sales pipeline; longer sales cycle for a big engagement; needs ~1 referenceable anonymized case (he has it).

### 2. The Shipping-Cost Diagnostic (productized audit) — the funnel entry
**Wedge.** A fixed-scope, fixed-price "Shipping Cost Diagnostic": send 12 months of carrier invoices → get back a defensible savings map (re-rated against contract + alternatives), invoice-error/DQ findings, and surcharge-leakage analysis, in ~2 weeks.
**Flagship project.** Productize the audit so it's repeatable and partly AI-delivered (P3: standardized delivery is the precondition for AI leverage).
**Pricing.** €3k–€8k fixed, published price. Low buyer friction; qualifies leads for #1.
**Moat.** Same re-rating depth, packaged.
**Risk.** Must not cannibalize the bigger tender engagement — position it explicitly as the on-ramp.

### 3. Fractional Head of Shipping Analytics — the recurring-revenue ladder
**Wedge.** Ongoing carrier-cost monitoring (the SCM dashboard productized), peak-surcharge mitigation, quarterly carrier reviews, contract-renewal defense — as a fractional retainer.
**Flagship project.** Stand up a live shipping-cost monitoring + alerting capability for a shipper and own the quarterly carrier-cost review.
**Pricing.** Retainer €5k–€15k/mo (P3 fractional band $12k–$25k/mo is for full CDO scope; this is narrower). Stickiest revenue, highest ceiling, slowest to land.
**Risk.** Requires trust built first — this is the *ladder-up* from #1/#2, not the cold open.

### 4. Cross-cutting positioning wedge: **"shown math, not a black box"**
Not a separate business — the *differentiator* stamped across all three. Procurement teams have to defend a carrier switch internally; nobody else hands them the shipment-level audit trail. Lead with transparency against the 48-hour-AI-black-box incumbents.

### Parked: productize the engine as SaaS
The EU re-rating engine *could* become a thin SaaS later. P3's warning stands: that's a **different job** (builder, not consultant). Phase 3 at the earliest, only after services validate demand.

---

## The honest conditions (don't skip these)

1. **IP / clean-room is the real landmine.** The engines, mart access, and domain knowledge were built on the employer's data, tools, and time. Take the *method*, never their assets; rebuild clean-room. Resolve where the line sits before selling anything. This gates everything else.
2. **The EU-white-space thesis is partly absence-of-evidence.** Both market penguins flagged it: the "no EU parcel boutique" finding came from English-language search. **The single highest-leverage de-risking step is a German/Dutch/French-language sweep** to confirm the gap is real, not a search artifact. Cheap to run; do it before betting income on the niche.
3. **Gainshare attribution must be contractually defined.** Invoice data is the clean case, but realized-savings verification needs the client's *post-switch* invoices and an agreed baseline. Write the attribution method into the engagement.
4. **Sales is the bottleneck, not delivery** (P3, emphatic). He's optimized for the part that's already easy. Needs a standing lead-gen routine + the one anonymized case study + authority content. Most technically-strong people starve here.
5. **Sequencing: don't quit.** Land one paid, sanctioned, side engagement → prove outcome *and* sales motion → scale to 2–3 clients → only then go full-time. The leverage is what makes a side engagement survivable.

---

## Nutshell

The market research says the specialization is **already chosen — by what he's good at and where the gap is.** The flagship high-stakes project is the **EU multi-carrier tender, re-rated on actuals, priced on verified savings**, with a productized **Shipping Cost Diagnostic** as the funnel entry and a **Fractional Shipping Analytics** retainer as the ladder-up. The differentiator is *shown math* against black-box incumbents. The gates, in order: clean-room IP, confirm the EU gap (foreign-language sweep), define gainshare attribution, fix the sales muscle, sequence as a side bet first.

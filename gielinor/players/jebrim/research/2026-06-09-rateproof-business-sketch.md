# The business concept — locked sketch (2026-06-09)

> Niklavs' potential independent venture: a productized shipping-cost consultancy for European e-commerce. This is the canonical concept doc — referenced going forward. Working name: **RateProof** (see naming, bottom). Strategy draft for iteration, not confirmed knowledge.

**Companion files (same date):**
- [[2026-06-09-independent-specialization-synthesis]] — the market white-space analysis + specialization candidates
- [[2026-06-09-pre-departure-prep-checklist]] — what to sort out while still employed
- Source research: [[2026-06-09-parcel-audit-industry-landscape]], [[2026-06-09-carrier-tender-consulting-landscape]], [[2026-06-09-solo-ai-consulting-economics]]

---

## What it is, in one line

I build the rate engines that price every carrier option, run the tender or the optimization off them with your KAM negotiations, track your actual costs against the deal you signed — so you know the savings were real — and put an AI agent on top you can just *ask* about any of it.

**Engine → decision → verification → ask-anything, one hand.**

---

## The four-part service catalog (the spine)

These are not four separate gigs — they're **one closed loop.** That's what makes it a practice, not a string of projects.

| # | Service | What it is in the business | Cadence |
|---|---|---|---|
| **3** | **Calculation engines** for existing or new contracts | **The engine room — the IP and the moat.** Reusable core that prices any carrier, any contract. Everything else runs on it. Build once, leverage forever. | Foundational asset |
| **1** | **Tender calculations** | The episodic **big-ticket** engagement — the 7-figure carrier-selection decision. Flagship. *(+ heavy carrier KAM negotiation work)* | Episodic |
| **2** | **Current-setup optimization** | The **recurring, lighter-touch** service — improve the existing setup without a full tender. Faster to sell, more frequent. *(+ carrier KAM work)* | Recurring |
| **4** | **Dashboard: actual vs expected** | The **loop-closer.** Tracks actual cost *against the expectation the engine modeled.* | Always-on |

**Why #4 is the standout.** Tracking *actual cost* is common; tracking actual cost **against the engine's modeled expectation** is rare. It answers the question every shipper has and can't answer — *"did the savings we negotiated actually show up, or is the carrier clawing them back through surcharge creep?"* It does three jobs at once:
- **Proves value** → you get rehired.
- **Makes gainshare billable** → verification of realized savings *is* the invoice basis.
- **Creates stickiness** → they can't switch it off without going blind.

#3 produces the "expected," #4 shows "actual vs expected" — the halves snap into a feedback loop competitors don't have.

**The KAM-negotiation layer is a moat, not a cost.** Audit-SaaS players are pure software — they never sit across from a DHL key-account manager. Big firms do, at enterprise day-rates. The human-negotiation layer *on top of* shipment-level engine rigor is the seam: too hands-on for the tools, too nimble/cheap for the consultancies. Only this venture brings both the math *and* the relationship work.

---

## The product split — why SCM can be a real product

The analytics layer is invariant; only the raw sources differ. So the architecture splits three ways, and the split *is* the business model:

- **Canonical input contract** — one documented shipment-level schema. **The cost-bucket structure already exists** (the gold mart already groups costs into the relevant buckets — that's the hard cross-carrier normalization, already solved; it's portable *method*, rebuilt clean-room). The contract = buckets **+** the trust-making fields (dims, cost basis, status/packagetype), designed **required-vs-optional so it degrades gracefully** on a thinner client.
- **Per-client ingestion adapter** — maps the client's raw carrier data onto the canonical schema. The *only* bespoke work; scoped, billable as onboarding; where the invoice-DQ knowledge earns its keep.
- **The product** (breakdown / monitoring / alerting) — built once on the contract, reused per client.

**Two products hide in "polish," don't conflate them:** (1) the breakdown view as a *client deliverable* — reachable now, basically consulting with a nicer surface; (2) a *self-serve SaaS* — multi-tenancy/auth/billing/support, the "you become a builder" job. **Do (1) first.** The **breakdown tab alone** is an immediately legible wedge/demo and the tier-① diagnostic delivered live.

---

## The conversational layer (the capstone) — the shipping-agent on top

A natural-language agent sits **over the whole stack** — engines (#3), dashboard (#4), tender results, canonical data. Not a fifth service; the **interface over everything.** Anyone can ask: *"why did DPD get more expensive?", "what would we save moving AT to GLS?", "did the tender savings actually show up?", "explain how this recommendation was calculated."*

**Why it matters:**
- **Makes "shown math" interrogable** — the audit trail becomes a conversation, not a PDF. No competitor does this.
- **Scales your explanation** — answers the questions you'd otherwise sit in a call to answer; the bridge that lets the product breathe without you in every meeting.
- **The AI-leverage thesis, visible to the buyer.**

**The moat (again): it's the *hardened* version, not naive text-to-SQL.** Anyone can bolt ChatGPT onto a database and get confidently-wrong cost numbers — worse than nothing in this domain. Yours carries the cost-basis discipline, coverage/DQ caveats, and charge-bucket-first decomposition as guardrails. A competitor's "ask your data anything" lies; yours doesn't.

**Sequencing:** capstone, **not the MVP** — only as good as the layers beneath it, built last. Same two-products rule as the dashboard: *your* delivery tool first (low-risk, immediate), client-facing self-serve later. Clean-room the methodology (how-to, cost-basis rules, caveat discipline are portable; the Picanova-wired instance isn't).

## The offer ladder

**① Shipping Cost Diagnostic** — the on-ramp. Fixed **€6,500**, ~2 weeks. 12 months of invoices in → defensible savings map (re-rated vs contract + alternatives) + invoice-error/DQ findings + surcharge-leakage breakdown + readout. *Fee credited toward a tender if they proceed.*

**② Carrier Tender** — flagship. **€25k–45k base + ~20% of verified Year-1 savings** (gainshare). 6–10 weeks. Full re-rating → portfolio scenarios → decision report → KAM negotiation support → implementation handoff.

**③ Fractional Shipping Analytics** — recurring. **€4k–8k/month.** Monitoring (the #4 dashboard), surcharge alerts, quarterly carrier reviews, renewal defense. Sold after a tender builds trust.

**Differentiator across all three: "shown math, not a black box."** Competitors benchmark or run black-box AI (even TransImpact's 48h turnaround hides the shipment math). This venture hands the client the shipment-level audit trail to defend the decision internally.

---

## Ideal client

European e-commerce / D2C / fulfillment, **~€5–50M/yr** shipping across multiple parcel carriers (DHL, DPD, GLS, Hermes, UPS) + some freight. Buyer: Head of Logistics / Supply Chain / Ops, or CFO. Triggers: contract renewal, peak-surcharge pain, an RFP, post-merger network mess.

## The money math

One client diagnostic → tender ≈ **€6.5k + €30k base + 20% × €380k ≈ €112k.** Three to four flagship clients/yr = **€300–450k.** As a side bet: one diagnostic/month ≈ **€78k/yr part-time**, each a funnel into a tender.

## The proof you lead with (anonymized)

"€3M/yr-volume European e-commerce group, 9-carrier tender: ~13% defensible savings (~€378k/yr), and caught a sourcing error that would have flipped a carrier decision the wrong way."

---

## The four gates before betting rent (from the prep checklist)

1. **Own the method cold** — be able to whiteboard the tender/re-rating logic to a skeptical CFO with no notes. The leverage hides this gap; close it while employed.
2. **Clean-room the IP** — method, not employer assets/data/code. Read the contract (non-compete, IP assignment, confidentiality). This gates everything.
3. **Confirm the EU white space is real** — both market scans flagged it as English-search-based; a German/Dutch/French sweep confirms or kills the thesis.
4. **Sales is the real unknown, not delivery** — the side-bet phase tests one question: *can I get one real person to pay for one diagnostic?*

Sequencing: start the reversible version (prep + one sanctioned side engagement); gate the irreversible version (quitting) on proof.

---

## Naming

**Category:** best described as a **productized consultancy** (or "advisory practice with a product"), *not* a plain consultancy — the engines + dashboard are a product, and that product leverage is the whole point. Front door = consulting (tender/optimization); underneath = a product (engines + the actual-vs-expected dashboard).

**Working name:** **RateProof** — ties to the thesis (shown math, verified/proven savings). Alternates: TrueRate, Lane & Ledger, ShipBasis, Parcel Ledger. *Name is Niklavs' to finalize.*

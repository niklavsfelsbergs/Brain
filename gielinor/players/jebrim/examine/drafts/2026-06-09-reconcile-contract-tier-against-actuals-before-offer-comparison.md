---
observed: 2026-06-09 ([[S170_be1b4946_eu-tender-carrier-substitution-deltas|S170]], be1b4946)
context: EU-tender DPD PL new-offer vs existing-offer comparison
---

# Reconcile a multi-tier existing contract against invoice actuals before comparing a new offer to it

**The moment.** Comparing the DPD PL new tender offer to the existing contract, I produced two opposite numbers: +18.8% (new modeled all-in vs invoice actuals) and **−20.6%** (new base vs the existing card's base). The −20.6% used the existing file's `export MIX HOME service` sheet — a **list tier we don't actually bill on**. Our real actuals (~€4.56/pc) reconcile to a *different* sheet in the same file, `Direct, special offer` (its net prices matched actuals to ~1%). Comparing against the wrong tier **flipped the sign** — made a price increase look like a saving.

**The lesson.** A vendor's existing contract often carries **multiple service tiers / rate sheets** (list vs negotiated-direct vs PUDO). Before comparing a new offer to "the existing contract," **identify which tier is operative by reconciling each candidate sheet against our invoice actuals** — the operative one is whichever reproduces what we actually pay. Don't grab the first/headline sheet. The contradiction between two bases (modeled vs actual, or base vs base) is the diagnostic signal that I'm on the wrong tier — chase it, don't average it.

**Generalizes:** sibling of [[reconcile-definition-before-numbers]] and [[negotiated-source-is-a-subset]] — a curated/multi-part source describes more than one population; pin the operative one against ground truth (our invoices) before modelling. Also: a new offer can only be compared like-for-like once both sides sit on the same basis (all-in vs all-in), and the existing side's ground truth is actuals, not a list card.

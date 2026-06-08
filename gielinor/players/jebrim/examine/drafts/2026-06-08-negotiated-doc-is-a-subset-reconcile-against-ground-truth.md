# A negotiated/partial source is a subset — reconcile against ground truth before concluding or modelling

**Observation (S163, UPS EU-tender Phase 1, 2026-06-08).** Working the UPS offer, I read the negotiated surcharge sheet (`Zuschläge`) and concluded "only fuel, residential and Free Domicile apply — almost everything's waived." Niklavs pushed back twice: "truly only those? seems suspicious," and earlier "I think we did this very quick." Both were right. The sheet's own footnotes said it: *"% Off = % Off UPS Tariff"* and *"rates are exclusive of any additional charges"* — i.e. it's the *negotiated subset*, not the whole bill. Two probes against ground truth then surfaced what the offer hid: the published tariff (peak window, Over-Max €440, book values) and — decisively — **our own UPS invoices**, which showed ~€191k/yr of peak/demand stacked *invisibly inside* the oversize and residential buckets, plus effective fuel ~20% not the card's 35%.

**The pattern.** A document that presents a *curated or negotiated* view (a contract's deviation sheet, a vendor's offer, a summary table) describes a subset of reality. Concluding "this is the complete picture" from it is the same failure as concluding from a code comment or a fixture instead of the authoritative data. The cheap, decisive move is to reconcile against ground truth — and the best ground truth for "what does this cost / what gets billed" is **our own actual invoices**, not the rate card.

**Also:** the rush itself was the tell. I assembled a question round before checking whether answering it would even give a deterministic calc. The completeness/determinism check (run *before* finalizing the deliverable) surfaced four missed inputs and the whole invoice-investigation that found the hidden layer.

**How to apply.**
- When a source is a *negotiated/curated subset* (offer, deviation sheet, "what changed" doc), treat "this is everything" as a hypothesis to disprove — read its own footnotes/exclusions, then reconcile against the authoritative base (published source) and, where it exists, **our own transactional data**.
- For any "what does X cost / what will we be billed" question, **profile the actual invoices** before trusting the rate card. Real billing catches unknown-unknowns the rate card can't (charges that stack inside other buckets, effective vs nominal rates).
- Before finalizing a question round or a model, run a completeness/determinism check: *would answering this actually let me compute the thing?* The gaps it surfaces are the real work.

Relates to [[2026-06-01-verify-the-thing-dont-trust-the-wiring]] (verify against the live source, not the description) and the memory `code-comment-describing-data-isnt-ground-truth`. This is the cost/contract-doc instance of the same reflex.

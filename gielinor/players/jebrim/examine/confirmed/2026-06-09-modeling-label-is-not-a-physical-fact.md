# A modeling-layer label describes the model's coverage, not the physical operation

**Observation ([[S185_e9821cdf_eu-tender-report-signoff|S185]], e9821cdf, 2026-06-09).** Asked what the DPD "carrier-only 1,887" were, I answered that they were parcels that "don't fit DPD." Niklavs pushed: *"so these were shipped with DPD PL even though they don't fit?"* — and that reframing was the catch. I verified `cur_inc` against the cost matrix: **all 1,887 actually shipped via DPD** (cur_inc=dpd_pl). "carrier-only / null `service`" is a property of the **rate engine's coverage** (the `dpd_pl_current` engine is export-only, so it has no named product for PL-domestic), **not** a physical misfit. The parcels fit DPD fine — DPD literally carried them.

**The trap.** A null/sentinel value in a derived model layer (`service = null` → "carrier-only") reads like a statement about the world ("doesn't fit"), but it's a statement about the *model* ("not priced by a named product"). I narrated the model artifact as an operational fact.

**Rule.** Before explaining *why* a slice is unmodeled / null / "other" / uncategorized, verify it against the **authoritative ground-truth field** (here: the actual incumbent carrier). A modeling-layer label is a hypothesis about coverage, not evidence about the underlying operation. Sibling of [[2026-06-09-populated-column-is-not-a-measurement]] (a populated field isn't proof of measurement) and [[code-comment-describing-data-isnt-ground-truth]] — here a *null* field isn't proof of a physical limit.

**Cheap-correction note.** The confirm-before-build reflex made the mis-frame cheap: it was one sentence in chat, corrected within the same turn after a 1-query check, not a built artifact. ([[pin-the-actual-complaint-before-fixing]].)

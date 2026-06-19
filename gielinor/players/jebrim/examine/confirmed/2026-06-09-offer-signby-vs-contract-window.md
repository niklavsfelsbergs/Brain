# A date on a vendor doc isn't automatically an expiry — classify by document type

**Observed:** 2026-06-09, [[S176_0a2a6fff_picanova-eu-carrier-contract-expiry|S176]] ([[S176_0a2a6fff_picanova-eu-carrier-contract-expiry]]).

**The moment.** Asked for PICANOVA carrier contract expiries, I read DPD PL's footnote *"offer for 2026, valid till 31.01.2026"* as the rate-window **expiry** and reported the contract as expired. Niklavs pushed back: *"isnt 31.01.2026 the contract signing expiry date instead of the actual contract window?"* He was right — it's a **sign-by / acceptance deadline**; once signed, the 2026 rates run the offer year. I'd conflated *when you must accept* with *when the rates stop*.

**The rule (generalized).** A date printed on a vendor document means different things by document type:
- **Offer / quotation** → sign-by / acceptance window. If signed, rates run the offer period; the printed date is **not** when rates stop.
- **Executed contract** (signatures + term clause) → genuine term/rate window.
- **Issued price list** (e.g. German *Preisliste*) → effective-from, open-ended (runs until next price change/notice).

**Two compounding lessons:**
1. After the catch, I audited *every* carrier against the rule instead of fixing only the two Niklavs named — which surfaced DB Schenker as a third offer. The earlier instinct to fix just the named instance is the multi-entity generalization trap again ([[don't-generalize-from-single-verified-case]] family).
2. When the exact date genuinely wasn't in our files (DPD PL rate-end), I scanned exhaustively then reported the gap honestly ("implied, no explicit date") rather than inventing one.

**How to apply.** On any "when does X expire" over vendor docs: first identify the document *type*, then read the date in that frame. Don't report an offer's acceptance deadline as a contract expiry.

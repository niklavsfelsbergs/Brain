# S176 — PICANOVA EU/UK carrier contract expiry overview

**Player:** Jebrim. **Born:** 2026-06-09 (sid8 `0a2a6fff`).
**Ask:** When does each contract in `bi-analytics-main/NFE/projects/5_shipping_savings/contracts/1. EU/1. PICANOVA/` expire, and what happens after.

## What happened

Extracted term/validity language from every contract doc in the PICANOVA folder (11 carriers) via `pdftotext -layout` (PDFs) and `openpyxl` (xlsx) — no reasoning from memory. Built a per-carrier expiry overview, then a full "what happens after" overview when asked.

**The correction (high-signal).** Niklavs caught that I'd mis-read DPD PL's footnote *"offer for 2026, valid till 31.01.2026"* as a rate-window **expiry**. It's a **sign-by / acceptance deadline** — once signed, the 2026 rates run the offer year. Generalized the fix into a document-type rule:
- **Offer** (rate card/quotation) → date = sign-by window (DPD PL, DB Schenker, Post Nord).
- **Executed contract** → date = real term window (Maersk, UPS, DPD UK, Yodel).
- **Issued price list** (German *Preisliste*) → date = effective-from, open-ended (DHL Paket, GLS).

Then audited *all* carriers against that rule rather than generalizing from the two Niklavs named — surfaced **DB Schenker** as a third offer (its 06.02.2026 is an acceptance deadline), and confirmed Post Nord's 13.02→15.03.2026 is an offer window too.

**DPD PL exact expiry — not findable in our files.** Exhaustive cell scan of all 6 sheets: the only date anywhere is the sign-by footnote. No `valid from`, no rate-window end. Contracts folder holds no separate signed DPD PL contract PDF (the countersigned offer *is* the agreement). Reported honestly as "implied calendar-2026, no explicit end date."

**Relationship status (from Niklavs):** Yodel stopped, GLS stopped, Post Nord stopped, DPD UK planned-drop, DHL Paket renewed 03.01.2026, DPD PL signed.

## Deliverable

`bank/drafts/notes/projects/2026-06-09-picanova-eu-carrier-contract-overview.md` — classified overview with master table, post-expiry behaviour, action dates (Maersk auto-renew locked to 30.07.2027; DPD UK 3-mo notice by ~21.08.2026), key takeaways. Draft — promote at next alching.

**Source-of-truth update (Niklavs, this session):** canonical contracts home is now `bi-analytics-main/NFE/docs/shipping_contracts/` (`0. OLD/`, `1. EU/`, `2. US/`) — look there first; the `5_shipping_savings/contracts/` path is superseded as the lookup root. Recorded in the bank note's header.

## Decisions

- Report sign-by vs term-window vs effective-from by **document type**, not by raw date.
- Don't assert DPD PL "expired" — distinguish acceptance deadline from rate window.
- Audit every carrier per-instance, not by generalizing from the named two.

## Pending external actions

None pending.

## Cascade

None — single bank-note draft; no canonical docs/status-tables touched.

## Main-brain changes

Bank-note draft + examine draft (this session's harvest). No `confirmed/`, no `meta/`, no rituals touched.

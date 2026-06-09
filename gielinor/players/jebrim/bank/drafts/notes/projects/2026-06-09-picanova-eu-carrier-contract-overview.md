# PICANOVA EU/UK carrier contracts — terms, expiry & what-happens-after

**Drafted:** 2026-06-09 (session `0a2a6fff`). **Status:** finding, stable (corrected once — see *The correction*). **Promote at:** next Jebrim alching.
**Anchor (source docs):** `bi-analytics-main/NFE/projects/5_shipping_savings/contracts/1. EU/1. PICANOVA/` — one subfolder per carrier (PDF/xlsx/msg). Dates below were extracted from those files directly (pdftotext / openpyxl), not from memory.

> **Source-of-truth update (2026-06-09, Niklavs).** The canonical home for shipping offers/contracts is now **`bi-analytics-main/NFE/docs/shipping_contracts/`** — layout `0. OLD/` (superseded offers, incl. `EU/DB SCHENKER POLAND XXL PARCEL AND PALLER/` with 2022–2025 DB Schenker offers), `1. EU/`, `2. US/`. Look here first for any offer, old or current. The old `projects/5_shipping_savings/contracts/` path is superseded as the lookup root (current cards still mirror there). Both are gitignored binaries — no git history recovery.
Reference date for "today" statements: **2026-06-09**. Relationship status (kept/dropped) supplied by Niklavs this session.

## The correction (why this note exists)
The headline date on a carrier file is **not always an expiry**. The tell is the *document type*:
- **Offer** (rate card / quotation seeking acceptance) → the date is a **sign-by / acceptance window**. If signed, the rates then run for the offer year; if not, the offer lapses. It is **not** when your rates stop.
- **Executed contract** (signed, with a term clause) → the date is a **genuine term/rate window**.
- **Issued price list** (e.g. German *Preisliste*) → the date is **effective-from**, open-ended (no expiry; runs until next price change/notice).

Initial pass mis-read DPD PL's "offer for 2026, valid till 31.01.2026" as a rate-window expiry. It is a **sign-by deadline**; DPD PL **was signed** → 2026 rates are live. Post Nord and DB Schenker are the same offer shape.

## Master overview

| Carrier | Relationship | Doc type | Headline date | Meaning | After |
|---|---|---|---|---|---|
| **Maersk** | Active | Signed contract (Schedule 1 dated 04.07.2025) | Initial term **01.08.2025 → 30.07.2026** | Real term window | Auto-extends to **30.07.2027** (successive 12-mo terms) unless 60-day notice before term end. **Notice window closed ~31.05.2026 → it will renew.** Annual rate-review right (Sched 1 §C, ≥15d notice); charges adjustable per Schedule 3 at each charges period, but Picanova has a good-faith **objection right** that freezes current rates until agreement (§7.5); 14-day cost pass-through (§7.6) |
| **UPS** | Active | Signed contract (04.24) | Initial term ended **02.06.2025** | Real term window | Auto-renewed to **indefinite term**, 30-day notice either side (§10). Deal = **discount off UPS published tariff at the shipping-day rate** → annual GRI + surcharge increases **flow through** (discount % holds, absolute prices rise). UPS may **re-calc special rates** if profile deviates from quoted volume (§5). Current rate card effective **21.12.2025** |
| **DHL Paket** | Active | Issued price lists (dated 17.11.2025) + 2026 rate-change notice | **Renewed 03.01.2026** | Effective-from, open-ended | Runs until next price change/notice; 2026 changes already applied |
| **DB Schenker** | New/recent (offer) | **Offer** (.xlsx; signature + acceptance fields) | Accept by **06.02.2026** | **Sign-by deadline** | If signed, rates run under framework agreement **No. WW-WWTWI-300005580866642** — no fixed term in the file; validity-start field left blank |
| **DPD UK** | Active → **planned drop** | Signed contract (19.11.2025) | Yr-1 fixed **21.11.2025 → 21.11.2026**; yr-2 **→ 21.11.2027** | Real term window | Continues into yr-2 (RPI-capped) unless terminated. To exit at the 1-yr mark, serve **3-mo notice by ~21.08.2026**; general clause-10 exit is 1-mo notice (but yr-1 charges are contractually fixed) |
| **DPD PL** | Active (**signed**) | **Offer** (.xlsx) | Sign-by **31.01.2026** | **Sign-by deadline** | **Signed → 2026 rates live** (implied calendar-2026 window; **no explicit rate-end date** in file) |
| **Post Nord** | Dropped | **Offer** (.pdf; "This offer is based upon estimated annual volume…") | Offer open **13.02 → 15.03.2026** | **Sign-by / offer window** | Acceptance window; never a term contract. Academic — relationship ended |
| **Yodel** | Dropped | Signed contract variation (09.25); base 10.07.2023 | Runs until **31.01.2026** | Real term window | **Auto-terminated 31.01.2026** — genuinely expired; matches the stop |
| **GLS** | Dropped | Contract 2026 + T&C 2026 | Rates from **01.05.2025 / 01.01.2026** | Effective-from, open-ended | No end date; would run until notice. Relationship ended on our side |
| **nShift** | Platform/POC | Discovery deck + 2024 doc | — | Not a carrier | Multi-carrier shipping platform; POC-stage ("strategic long-term partnership"), no fixed term/expiry in folder |

## Classification (the rule for this folder)
- **Offers — date = sign-by, not expiry:** DPD PL (signed), DB Schenker, Post Nord.
- **Signed contracts — date = real window:** Maersk, UPS, DPD UK, Yodel.
- **Issued price lists — date = effective-from, open-ended:** DHL Paket, GLS.
- **Sub-tell:** DPD UK's folder also holds loose quotations/rate cards ("proposal valid for 30 days") — those *are* sign-by windows, but **superseded** by the executed 19.11.2025 contract.

## Action dates worth tracking
- **Maersk** — 60-day notice window to avoid auto-renewal closed **~31.05.2026** (past) → **rolls to a fresh 12-mo term ending 30.07.2027**. Leverage on rate adjustments lives *during* the term (they owe 15-day notice on any change).
- **DPD UK** (planned drop) — minimum term to **21.11.2026**; ending at that mark needs **3-mo written notice by ~21.08.2026**, else it rolls into yr-2 (RPI-capped, to 21.11.2027).

## Key takeaways
- **None of the active carriers locks against rate increases** — each live one has a review or pass-through mechanism (Maersk annual review; UPS GRI flow-through; DHL Preisliste; DB Schenker framework).
- The only date that is genuinely an **expiry, past, with effect** is **Yodel (31.01.2026)** — and we've already stopped.
- The `1. EU` folder **mixes EU and UK** carriers (DPD UK, Yodel; UPS/GLS span both) — it's the whole western-Europe carrier set, not EU-only.

## Related
- [[eu_tender_2026]] — UPS/DB Schenker tender threads draw on these incumbents.
- `bank/drafts/notes/projects/2026-06-09-ups-old-vs-new-rate-card-diff.md` — base-net diff of the UPS incumbent card vs the 2026 tender offer.

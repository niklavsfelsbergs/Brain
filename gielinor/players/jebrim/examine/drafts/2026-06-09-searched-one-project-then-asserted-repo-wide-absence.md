---
observed: 2026-06-09 ([[S170_be1b4946_eu-tender-carrier-substitution-deltas|S170]], be1b4946)
context: looking for the current DPD PL contract during the offer comparison
---

# I searched one project and declared the artifact absent repo-wide — it was in a sibling project

**The moment.** Asked whether we had the current DPD PL contract rate card, I searched only `NFE/projects/2_EU_tender_2026/` and reported "there is **no** current DPD contract card in the repo." Niklavs corrected me: it's in `NFE/projects/5_shipping_savings/contracts/1. EU/1. PICANOVA/` — a different project I never looked in. The whole `contracts/` tree of existing carrier agreements (UPS/DPD/Maersk/DHL/GLS/…) lived there.

**The lesson.** A negative claim ("we don't have X") requires searching where X would plausibly live, not just the project I happen to be working in. Existing **contracts** have their own home (`5_shipping_savings/contracts/`), distinct from tender **offers** (`2_EU_tender_2026/1_offers/`). When the question is "do we have the *existing* contract," the tender project is the wrong place to conclude absence from.

**Generalizes:** instance of [[never assert absence against a principal claim]] — an empty search in one location = "haven't found it yet," widen the search, never "it doesn't exist." Pair with: before asserting absence, name the search scope I actually covered so the gap is visible and correctable.

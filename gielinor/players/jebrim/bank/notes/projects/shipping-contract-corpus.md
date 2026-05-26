# Shipping-contract corpus (in the shipping agent)

**As of:** 2026-05-23 ([[S058_1f0ae59a_shipping-contract-corpus-ingest|S058]]). **STATUS: PARKED same session** — built, tested, and pulled from the agent on the principal's call (*"this is bad and im not fixing it"*). This note records what it was and where it's parked, in case it's ever revisited.

The shipping agent (`~/Documents/GitHub/shipping-agent/`, its own git repo) *briefly* carried a curated contract corpus at `contracts/` (top-level) before it was parked.

- **What:** current EU + US carrier contracts, **69 files**. EU by entity→carrier (`eu/`: PICANOVA, ORWO, SENDMOMENTS); US by carrier (`us/`: Asendia, Fedex, Maersk, OnTrac, P2P, USPS).
- **Storage rule:** raw files (PDF/xlsx/…) are **gitignored** (local-only, pull out clean); only `.md` is tracked. `contracts/INDEX.md` is the verified map (per-file type/scope/validity/gotchas); `contracts/_about.md` is the spec.
- **Excluded:** `0. OLD` (~2.7 GB historical — skipped); EU Tender 2026 (synthesized separately in `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/`).
- **Mart vs contracts:** the mart = what we *actually paid*; contracts = what we're *contracted to pay*. Different sources for different questions.
- **Agent wiring:** `how_to.md` §0 "Contract corpus" routes contract-term questions to INDEX (cheap), gates opening source files behind a confirm (expensive — scanned PDFs / big grids, ask-unless-explicit), and ties rule 30 to offering a contract check on contract-resolvable assumptions (dimension caps, surcharge eligibility).
- **Parked (not on `main`).** The agent's `main` was reset to before [[S058_1f0ae59a_shipping-contract-corpus-ingest|S058]] (`c515140`, clean). Work preserved two ways: (1) git branch **`parked/contract-corpus`** in the shipping-agent (commits `543c24d` corpus+index, `124b838` how_to wiring); (2) the curated corpus folder (raw 69 files + `INDEX.md` + `_about.md`) moved to **`~/Documents/Shipping/_PARKED_shipping-agent_contracts/`**. Revive = `git merge parked/contract-corpus` (or cherry-pick the two commits) + move the folder back to `contracts/`. Original source download also still at `~/Documents/Shipping/`.

Dig findings worth knowing: filenames are unreliable (GLS "T&C" is a rate card; "Maersk UK" is a Yodel/Evri card; Asendia "SLA" is the master contract). ORWO 0R6D51 rate card is **missing** (only a corrupt XML-sig placeholder existed). IBAN data sits in ORWO `AN3` (billing annex) + `SEPA` files.

## Related
- [[dashboard_and_shipping_agent_convergence]] — the agent's role over the mart.

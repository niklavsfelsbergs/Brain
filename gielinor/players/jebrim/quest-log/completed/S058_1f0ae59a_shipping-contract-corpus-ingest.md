# S058 — Shipping-contract corpus ingest

**Player:** Jebrim · **Session:** jebrim-1f0ae59a · **Started:** 2026-05-23
**Target:** out-of-tree repo `~/Documents/GitHub/shipping-agent/` (its own git repo, live).

## Ask

"Work on the shipping agent. Feed it our shipping contracts — a lot of info, lives in a separate folder so we can easily pull it out." Principal had just downloaded `Documents/Shipping/`. Be smart about what to pick — only what's actually useful to the agent.

## What happened

- Located the live agent (`GitHub/shipping-agent`, not the older nested `bi-analytics-main/.../shipping-agent`).
- Set up `contracts/` (top-level) following the repo's local-only convention: `.gitignore` rule `contracts/**` + `!contracts/**/` + `!contracts/**/*.md` → **raw files local-only, only `.md` tracked**. Verified with `git check-ignore` + `git add -n` (stages only `_about.md`). Wrote `contracts/_about.md`.
- Surveyed the download: 2,599 files / 2.8 GB. `0. OLD` = 90% (2.68 GB, mostly operational clutter + emails). Current set tiny: `1. EU` (52), `2. US` (28), `3. EU Tender 2026` (29).
- Principal calls: **skip OLD entirely**; **skip EU Tender in the agent** (best synthesized in `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/`).
- Ingested current EU + US only, contract-shaped files (`pdf/xlsx/xlsm/xls/docx/doc/csv`), dropping `.msg/.pptx/.jpg/.zip` noise. Result: **eu/ 49 files (56 MB) + us/ 28 files (35 MB)**, structure preserved (PICANOVA/ORWO/SENDMOMENTS; Asendia/Fedex/Maersk/OnTrac/P2P/USPS).

## State

- My uncommitted files: `.gitignore`, `contracts/_about.md` (+ 77 ignored raw files on disk).
- **Parallel sibling `jebrim-f4bb6eab` (S057) is in the same repo** — its uncommitted `how_to.md` (§0 rules 30–34) is NOT mine. Exclude from any commit I make.

## Dig-through (verified map)

Principal pushed back: a filename-inferred index won't work — files must be opened. Confirmed (Maersk EU "rate card" = rates + remote-area surcharges + dimension list across 3 sheets). Spawned **6 read-only dwarves** by entity/carrier; they opened all 77 files (PDFs via Read, xlsx via openpyxl, docx via unzip).

Findings — filenames lie constantly:
- **3 duplicates** (DPD UK Quotation-08.25, FedEx Fees-02.25, P2P TheCustomizationGroup.xlsx).
- **2 corrupt** (ORWO 0R6D51.xlsm = XML signature blob; FedEx Rates-02.25.xlsx = font-license text). Real 0R6D51 card **missing**.
- **3 non-contract** (2 nShift decks, DPD UK internal tender analysis).
- **~8 type/year mismatches** (GLS "Contract"+"T&C" both rate cards; "Maersk UK" is a Yodel/Evri card; ORWO "Contract DHL 2026" = 18.08.2025 German original; "Austrian Post T&C 2026" = 2025 offer; Asendia "US SLA" = signed master contract; "FedEx Rates 02.25.pdf" = TC GROUP not Picanova; ORWO DHL cryptic cluster decoded).
- **Sensitive:** IBAN/BIC in ORWO AN3 (Annex 2) + SEPA files. **Missing base agreements:** Yodel 2023 master, OnTrac base TSA. **Anomaly:** ORWO 0R6D66 16kg×Chile = 770.3.

Principal approved dropping all 8 (5 dupes/corrupt + 3 non-contract). Corpus now **69 files**. Rebuilt `contracts/INDEX.md` on verified content: data-quality flags section + per-entity/carrier tables (verified type / scope / validity / ⚠ notes). `_about.md` points to INDEX as the entry point.

## State

- **Committed** as `543c24d` on `main` (shipping-agent repo): `.gitignore`, `contracts/_about.md`, `contracts/INDEX.md` — 3 files, 209 insertions. Single atomic, revertible commit; raw files gitignored so a revert never touches local source. Not pushed (push-denied repo).
- S057's `how_to.md` change committed separately by that session (`c515140`) — never entangled with mine.

## Discovery hook — done (committed)

Designed the wiring with the principal (cost-aware): consulting `contracts/INDEX.md` is cheap; **opening a source file is the expensive step** (scanned PDFs, big rate grids) → confirm before opening, ask-unless-explicit. Plus the mart-vs-contract split (mart = what we paid; contracts = what we're contracted to pay) and a scope clause (§10 is the broader codebase, not this in-folder corpus). Tied to rule 30: when an analysis hits a contract-resolvable assumption (dimension caps, surcharge eligibility), surface it and offer the check.

Committed as `124b838` (how_to.md, +15/−1): §0 "Contract corpus" subsection, §1 index row, rule-30 cross-ref.

## State — complete

Two clean isolated commits on `main` (shipping-agent, unpushed):
- `543c24d` — corpus + verified INDEX.md + _about.md + .gitignore.
- `124b838` — how_to.md discovery wiring.

Principal signalled they may **park** the feature later. Raw 69 files gitignored throughout, so reverts never touch local source.

## Parked (same session)

Principal tested the wired agent (*"recent fuel surcharge increases"* → it consulted `INDEX.md`, split contracted-% vs actuals, and asked before opening — the design worked) and called it: *"this is bad and im not fixing it."* Parked immediately.

Method: branched the work as **`parked/contract-corpus`** (preserves both commits), moved the curated corpus folder to **`~/Documents/Shipping/_PARKED_shipping-agent_contracts/`**, then `git reset --hard c515140` so the agent's `main` is clean (as if S058 never landed). Fully revivable: merge the branch + move the folder back. **Net agent change from S058: none.**

# Skill — curating a document corpus for an agent

**Drafted:** 2026-05-23 (S058, shipping-contract ingest).

When feeding a pile of source documents into an agent so it can answer from them:

1. **Don't trust filenames — open the files.** Filename-inferred categorization is unreliable: in practice a "Contract" was a rate card, a "T&C" was a price update, an "SLA" was the master agreement, and two files were corrupt/wrong-type. Build the index from *verified* content.
2. **Parallelize verification with dwarves.** Split the corpus by natural grouping (entity/carrier), spawn read-only dwarves to open every file (PDFs via Read, xlsx via openpyxl dump, docx via unzip) and return tight per-file summaries: type / scope / structure / validity / gotchas / confidence. Principal assembles the index; dwarves don't write.
3. **Curate, don't bulk-copy.** Decide what's actually useful — signal (rate cards, terms, surcharges) vs noise (emails, decks, images, archives). Confirm scope calls with the principal (how much history, which categories).
4. **Storage split.** Raw files gitignored (local-only, pull out clean); only a tracked `.md` knowledge layer commits. A verified `INDEX.md` map routes the agent to the right source file; raw stays out of git history.
5. **Cost-gate expensive reads.** Consulting the index is cheap; opening source files (scanned PDFs, large grids) is expensive — gate it behind a confirm (ask-unless-explicit), and route correctly first (e.g. "what we paid" ≠ "what we're contracted to pay").
6. **Isolate the wiring in its own commit** so the whole feature can be parked with a single revert.

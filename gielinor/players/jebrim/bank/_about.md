# Jebrim — bank/

**Cognitive role.** Semantic memory. What Jebrim knows about the work — the knowledge graph that supports analytical execution.

**Metaphor.** The bank: items sorted, kept, withdrawn on demand, reorganized during bankstanding.

## Source repos

Jebrim's bank grows from **real working repos**, not via one-shot ingestion:

- `Documents/bi-analytics-main/NFE/`
- `Documents/bi-etl/`

The discipline: when Jebrim is working on a real task in one of those repos, he captures the relevant knowledge into `bank/notes/` as markdown notes that **link back to source paths**. The bank holds the knowledge graph; the repos remain the source of truth for code and configs.

A note about a query, for example, summarizes the query's purpose, inputs, outputs, and gotchas — and links to the source `.sql` file at its actual path. When the query changes, the note may need updating, and bankstanding catches drift.

## What goes here

- Knowledge **about** specific reports, queries, models, ETL pipelines, BI artifacts, stakeholders, data sources.
- Cross-cutting work knowledge: naming conventions, common pitfalls, recurring stakeholder asks, system architectures.

## What does not go here

- Today-only working state — that's `inventory/`.
- Session narrative — that's `quest-log/`.
- The code itself — stays in the source repos. Bank holds notes *about* the code.
- **Procedures / methodology / how-to** — that's `spellbook/drafts/skills/`. Bank notes are *about* the work; skills are *how to do* the work. A note titled "the EU Tender 2026 architecture" is a bank note; a note titled "how to decompose moving-target work" is a skill. See `gielinor/meta/layer-routing.md` for the full mapping.

## Structure

```
bank/
  _about.md
  drafts/notes/         # harvest candidates + chat-initiated drafts; promoted by alching
  notes/                # the active knowledge graph (post-promotion)
    <free subfolders by domain — reports/, queries/, pipelines/, etc.>
  rejected/notes/       # drafts the principal turned down (kept; patterns matter)
  archive/              # mirrors notes/ — superseded entries
```

## Write rules

Drafts-gated as of [[D-012]] (dev brain) / 2026-05-21. Jebrim writes to `bank/drafts/notes/`; alching promotes to `bank/notes/` or rejects to `bank/rejected/notes/`. Overturning existing knowledge surfaces as a contradiction during alching review. See `gielinor/meta/write-rules.md`.

## Discipline

- Every note that's about a repo artifact should include the **absolute or repo-relative path** to the source.
- When you can't find an existing note for something you're learning, write one. Bias toward capture.
- When you find a note that's contradicted by what you just learned, write the new understanding as a fresh draft in `bank/drafts/notes/`. Alching surfaces the contradiction with the existing `bank/notes/` entry, and the principal decides whether to archive the old note or reject the draft.

## Related

- `gielinor/spellbook/rituals/bankstanding.md` for periodic review.
- `quest-log/` (Jebrim's) for session entries that may graduate into bank notes.

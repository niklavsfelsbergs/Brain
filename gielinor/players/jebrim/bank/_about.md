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

- Knowledge about specific reports, queries, models, ETL pipelines, BI artifacts.
- Cross-cutting work knowledge: data sources, naming conventions, common pitfalls, recurring stakeholder asks.
- Procedures that are too specific to be `spellbook/` skills but too durable to be `inventory/`.

## What does not go here

- Today-only working state. That's `inventory/`.
- Session narrative. That's `quest-log/`.
- The code itself — that stays in the source repos. Bank holds notes *about* the code.

## Structure

```
bank/
  _about.md
  notes/                # the active knowledge graph
    <free subfolders by domain — reports/, queries/, pipelines/, etc.>
  archive/              # mirrors notes/
```

## Write rules

Auto-write. Jebrim writes to `bank/notes/` freely as he works. Overturning existing knowledge requires a draft in `gielinor/lorebook/drafts/`. See `gielinor/meta/write-rules.md`.

## Discipline

- Every note that's about a repo artifact should include the **absolute or repo-relative path** to the source.
- When you can't find an existing note for something you're learning, write one. Bias toward capture.
- When you find a note that's contradicted by what you just learned, don't silently update — surface the contradiction as a lorebook draft if it's load-bearing, or just archive the old note if it's stale.

## Related

- `gielinor/spellbook/rituals/bankstanding.md` for periodic review.
- `quest-log/` (Jebrim's) for session entries that may graduate into bank notes.

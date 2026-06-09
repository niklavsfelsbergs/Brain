# Commentary methodology — deterministic analysis, then editorial narrative — skill

How to attach AI-generated narrative to data without letting the narrative drift from the numbers. A reusable **analytical principle**, not a code pattern: separate the *computing* from the *writing*, and make every number in the prose traceable to a computed artifact. This is the same traceability discipline the player work already runs (deterministic-then-narrate, the savings-investigation deliverable shape) — written down so it transfers.

> Migrated from `bi-analytics-main/NFE/.claude/reference/commentary-patterns.md` (2026-06-09, [[D-034_guthix_executes_on_explicit_authorization|D-034]]). The NFE doc keeps the `analyze.py`/`generate_commentary.py` scaffolding and points here for the principle.

## When this fires

A deliverable that pairs numbers with prose and **refreshes** — a management dashboard updated daily/weekly, a recurring report, any "here's what the data says this period" narrative where the data changes under the words. Not one-off prose over static data (just write that).

## The two layers — never one

Split commentary into two layers with a hard seam between them:

**Layer 1 — deterministic (no AI).** A pure-computation step reads the result data and writes a structured artifact (`analysis.json`-shaped): every metric, delta, rank, breach. Reproducible, fast, diffable, testable. No LLM touches raw data or does arithmetic.

**Layer 2 — editorial (the LLM).** Reads *only* the Layer-1 artifact (plus a rolling window of recent entries for consistency) and writes sentences. Its job is purely editorial: select what matters, phrase it, keep tone consistent across refreshes. It never recomputes, never sees raw rows.

## Why the seam is the whole point

1. **Traceability** — every number in the prose traces artifact → result → source query. A wrong number is a bug in computation, never a hallucination in a prompt.
2. **Auditability** — the Layer-1 artifact is inspectable, diffable, testable on its own.
3. **Speed** — deterministic analysis runs in <1s; only the sentence-writing needs the model.
4. **Separation of concerns** — the model's only job is editorial judgment. Take arithmetic away from it entirely and a whole class of failure disappears.

## The discipline in one line

**If the LLM is doing math, the architecture is wrong.** Push every computation into the deterministic layer; hand the model a finished artifact and let it write.

## Rolling consistency

Keep a small rolling window of recent commentary entries (an append-only log + a "last N" slice). The editorial layer reads it so successive refreshes stay consistent in framing and don't contradict last period's narrative.

## What stays in the repo

The `analyze.py` starter template, `generate_commentary.py` API wiring, the exact JSON file layout, the refresh command. Repo mechanics. See the repo's `reference/commentary-patterns.md` (now a pointer) for them.

## Related

- [[report-design-language]] — where this narrative renders.
- The player-side savings-investigation deliverable shape applies the same deterministic-then-narrate split to analysis prose.

# guthix/bank/

**Cognitive role.** Semantic memory at system scope. What Guthix knows about the brain itself — cross-cutting patterns, drift observations, recurring themes from bankstanding passes.

**Distinction from a player's bank.** A player's bank holds knowledge about the work *they do* (data sources, queries, stakeholders). Guthix's bank holds knowledge about *the brain that does the work* — its layers, its drift, its cross-cutting patterns. Different stratum.

## What goes here

- **Cross-cutting patterns.** "Players X and Y both have stale shipping-data drafts from before the schema change."
- **Structural observations.** "The respawn ritual is referenced from N files but the load order is enumerated in none."
- **Drift surfacings.** "Bank/notes/ in Jebrim hasn't grown since date Y; either quiet by design (project closed) or quiet by neglect (review needed)."
- **Bankstanding-pass syntheses.** Aggregations across multiple passes: "These three drafts keep getting carried forward; resolve or drop."

## What does not go here

- **Per-player knowledge.** Never. That belongs in the player's own bank.
- **Decisions about how the brain operates.** Those go to global `gielinor/lorebook/drafts/` and graduate to `lorebook/decisions/`.
- **Today-only state.** Use `inventory/` for that.
- **Narrative of what happened.** Use `quest-log/` for that.

## Structure

```
bank/
  _about.md
  drafts/notes/         # observations Guthix has captured but not yet reviewed
  notes/                # promoted knowledge; treated as canonical until contradicted
```

## Discipline

- **Drafts first.** New observations land in `drafts/notes/`. Promotion to `notes/` happens during a later bankstanding pass that reviews the draft against the current state of the brain.
- **Naming.** Slug filenames with date prefix: `2026-05-22-cross-player-shipping-data-drift.md`. Date is when the observation was made.
- **Overturning existing knowledge.** A new draft that contradicts an existing `notes/` entry surfaces the contradiction at the next bankstanding — either the new draft wins (old note archives) or the draft is rejected.
- **Wiki-links.** Use `[[B-NNN]]` for Guthix's own ritual entries, `[[player-name/slug]]` for cross-references into player banks, and `[[D-NNN]]` for global decisions.

## Related

- `gielinor/meta/layer-routing.md` — content-shape → layer mapping.
- `gielinor/meta/drafts-mechanics.md` — the drafts flow generally.
- `gielinor/meta/archive-discipline.md` — what happens to superseded entries.

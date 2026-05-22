# guthix/keepsake/

**Cognitive role.** Always-surface pins at system scope. What Guthix needs to remember every time he descends — load-bearing concerns for the brain that should not have to be re-discovered each pass.

**Distinction from global `keepsake/`.** Global `keepsake/` is the brain's universal pinboard (deadlines, stakeholder commitments — surfaces to *any* actor at respawn). Guthix's keepsake is *for Guthix specifically* — things only he needs each pass.

## What goes here

- **Pending bankstanding work carried across passes.** "Three drafts have been carried forward through 3 passes — resolve or reject next time."
- **Overdue alchings.** "Player Z hasn't alched since 2026-04-12." Surfaces to Guthix on respawn so he can flag it.
- **Long-running drift watches.** "Watch for the schema-rename ripple effects in Jebrim's bank/notes/."
- **Architectural concerns awaiting a decision.** "Layer-routing for cross-cutting observations is fuzzy; clarify next bankstanding."

## What does not go here

- **One-off per-pass state.** That's `inventory/`.
- **Knowledge claims about the brain.** That's `bank/`.
- **System decisions that are now in force.** Those go in global `lorebook/decisions/`; Guthix references them, doesn't pin them.

## Structure

```
keepsake/
  _about.md
  proposals/            # pin candidates Guthix has nominated; principal approves
  current.md            # active pins; surfaced on respawn
```

## Discipline

- **Pinning is principal-gated.** Guthix proposes pins by writing to `proposals/<slug>.md` with an observation-backed reason. The principal moves them into `current.md` during review.
- **Naming.** Slug filenames with date prefix for proposals: `2026-05-22-drafts-carried-three-passes.md`. Date is when the proposal was drafted.
- **Pruning.** Pins decay. When a concern is resolved (the drafts get triaged, the alching happens), the relevant `current.md` line moves to `archive/`. Surfaced pins should always be live.

## Related

- `gielinor/keepsake/_about.md` — the global pinboard analog.
- `gielinor/meta/drafts-mechanics.md` — the proposal-then-approve pattern.

# ticks.md — scheduled triggers

**Metaphor.** In RuneScape, a *tick* is the engine's fundamental time unit — every action resolves on a tick boundary. Here, `ticks.md` is the scheduling slot: the agent's recurring obligations, the rhythm of its automatic life.

**Status.** Dormant in Phase 1. The agent runs on manual triggers only — the principal invokes a session, the agent acts, the session ends. There are no scheduled wakeups, no event listeners, no recurring jobs.

This file exists empty-but-named so that:

1. The brain knows it has a scheduling slot, even when nothing is scheduled.
2. When Phase 2 lands (substrate decision: Routines vs VPS), the scheduling lives in a known place.

## When this becomes live

Phase 2 activates one of two scheduling backends:

- **Claude Code Routines** — cron-style scheduled invocations of Claude Code. Lightest substrate; appropriate if real needs are scheduled-only.
- **VPS + Docker** — full hosted agent, event-driven and reactive in addition to scheduled. Appropriate if needs include messaging bridges, ambient triggers, etc.

Either way: the *definitions* of recurring jobs live here. The *runner* lives in the substrate.

## Format (proposed, not yet live)

Each tick is a section. Frontmatter-style fields for the schedule, the player to embody, the task brief. Example shape (subject to revision when Phase 2 hits):

```yaml
- id: morning-bankstand
  schedule: "0 7 * * 1"            # every Monday 07:00
  player: unscoped
  task: |
    Run bankstanding ritual. Surface drafts and inbox items.
```

Not authoritative. We'll design the real format when scheduling becomes a live concern.

## Related

- `meta/death-and-spawn.md` for what happens to an in-progress tick session if it crashes.
- `spellbook/rituals/` for the procedures a tick might invoke.
- `lorebook/decisions/` for the eventual decision on substrate.

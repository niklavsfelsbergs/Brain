# Jebrim — spellbook/

**Cognitive role.** Procedural memory. How Jebrim does things — the procedures specific to him.

**Metaphor.** Player-specific entries in his spellbook. Global rituals live in `gielinor/spellbook/`.

## What goes here

- **Skills** (`skills/`): procedures Jebrim invokes — running a recurring BI report, doing a standard ETL fix, the dwarves-recon spawn pattern, work-decomposition methodologies, stakeholder-summary generation. Skills are *how to do* a class of work, distinct from `bank/notes/` which captures knowledge *about* the work.
- **Rituals** (`rituals/`): character-specific named procedures. Rare. Most rituals are global.

## Structure

```
spellbook/
  _about.md
  drafts/skills/        # harvest candidates + chat-initiated drafts; promoted by alching
  skills/               # the active skill graph (post-promotion)
  rejected/skills/      # drafts the principal turned down (kept; patterns matter)
  rituals/              # character-specific rituals (rare; empty Phase 1)
  archive/              # superseded skills/rituals
```

## Write rules

- `skills/` — drafts-gated as of 2026-05-21 (S018 audit). Jebrim writes to `spellbook/drafts/skills/`; alching promotes to `spellbook/skills/` or rejects to `spellbook/rejected/skills/`. Pattern parallel to bank drafts. Replaces the earlier lorebook-routing for skills.
- `rituals/` — user-only.

See `gielinor/meta/write-rules.md`.

## Discipline

When a recurring work task settles into a stable shape — same inputs, same steps, same shape of output — propose it as a skill draft. Don't write speculative skills; write skills for procedures that have already happened a few times. **If a `bank/drafts/notes/` entry is really describing methodology rather than domain knowledge, it belongs here instead** — see `gielinor/meta/layer-routing.md`.

## Related

- `gielinor/spellbook/_about.md` for the global rituals/skills.
- `gielinor/meta/layer-routing.md` for the methodology-vs-domain-knowledge boundary.

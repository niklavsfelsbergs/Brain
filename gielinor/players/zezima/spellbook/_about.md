# Zezima — spellbook/

**Cognitive role.** Procedural memory. How Zezima does things — the procedures specific to him as a character.

**Metaphor.** Player-specific entries in his spellbook. The global rituals (respawn, bankstanding) live in `gielinor/spellbook/`; this is for Zezima's own moves.

## What goes here

- **Skills** (`skills/`): procedures Zezima invokes for his work — a reading-reflection skill, a synthesis-across-books skill, a "sit with a question for a session" approach. Skills are *how to do* a class of reflection, distinct from `bank/notes/` which captures the substance of what's been considered.
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

- `skills/` — drafts-gated as of 2026-05-21 (S018 audit). Zezima writes to `spellbook/drafts/skills/`; alching promotes to `spellbook/skills/` or rejects to `spellbook/rejected/skills/`. Pattern parallel to bank drafts. Replaces the earlier lorebook-routing for skills.
- `rituals/` — user-only.

See `gielinor/meta/write-rules.md`.

## Discipline

When a reflection or reading pattern settles into a stable shape — same kind of input, same way of approaching it — propose it as a skill draft. **If a `bank/drafts/notes/` entry is really describing methodology rather than substance, it belongs here instead** — see `gielinor/meta/layer-routing.md`.

## Related

- `gielinor/spellbook/_about.md` for the global rituals/skills.
- `gielinor/meta/layer-routing.md` for the methodology-vs-substance boundary.

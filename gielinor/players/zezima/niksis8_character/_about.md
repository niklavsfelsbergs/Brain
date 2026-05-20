# Zezima — niksis8_character/

**Cognitive role.** What Zezima knows about Niklavs through *his* relationship — the per-player lens on the user.

**Scope.** Per-player. Universal facts about Niklavs live in `gielinor/niksis8/`. This is what Zezima specifically has learned about him.

## What goes here

- Things about Niklavs that show up *in the reflective register* — what he wrestles with when he slows down, what kinds of reading he keeps coming back to, what patterns he notices in his own personal life.
- Communication preferences that show up when he's working through Zezima specifically (which may differ from his preferences with Jebrim).

## What does not go here

- Facts about Niklavs that hold regardless of player — those go in `gielinor/niksis8/`.
- Observations about Zezima himself — that's `examine/`.
- Day-to-day life context. That's `inventory/` or `bank/` depending on durability.

## Structure

```
niksis8_character/
  _about.md
  drafts/
  confirmed/
    current.md
  archive/
  rejected/
```

## Write rules

Drafts auto-write. Promotions are user-only and hook-enforced. See `gielinor/meta/write-rules.md`.

## Rejected drafts are data

`rejected/` is kept on purpose. A repeated pattern in what Zezima's model-of-Niklavs gets wrong — the same kind of reflective-register inference proposed and turned down again — means Zezima is mis-reading Niklavs in a specific way. Bankstanding surfaces these patterns; a recurring rejection may itself be the observation worth confirming (e.g., "Zezima keeps assuming Niklavs is unresolved on X when he's actually just sitting with it on purpose").

## Related

- `gielinor/niksis8/` for the universal model.
- `gielinor/meta/drafts-mechanics.md` for the observation rule.

# Shipping-agent skill loading — load-on-cue + how_to.md trigger registry

**Source:** [[S036_2026-05-22_reprompting-iteration-and-shipping-port|S036]] T5 — second live reprompt test failed because the new skill file existed but never loaded. Diagnostic: `shipping-agent/skills/_about.md` says skills are *"loaded on cue; not always-in-context"* and `how_to.md` is the only always-loaded file. Without a hook in the always-loaded surface, the agent has no signal to read the skill at trigger time.

## The mechanism

Shipping-agent file structure (relevant to skill loading):

- `how_to.md` — always-loaded, every session, every turn.
- `reference/` — load on cue when writing queries or looking up column/table facts.
- `skills/` — load on cue when the question shape matches a known recipe.

The agent doesn't auto-introspect `skills/` on each turn. A skill file's mere existence does not make the agent execute it. The agent only opens a skill when *something it already has in context* tells it to.

That something is a **trigger hook in `how_to.md`**. Without it, a skill file is dormant.

## The hook pattern

In `how_to.md` § 0, between rule 16 and the (17–29) section header, lives the subsection:

```
### Skill triggers — load on cue

Some classes of question need a skill loaded *before* the agent responds,
not after. The triggers below fire silently — the agent stops, reads the
named skill, then continues per that skill's rules.

- **<Trigger name>.** Trigger phrases (...). Disambiguation (...).
  On a real trigger: stop, read `skills/<file>.md` in full, follow its
  behavior section — <one-line summary of the skill's invariants>.
```

Each load-on-cue skill adds one bullet. The hook carries: trigger phrases, disambiguation, and a one-line summary of the skill's headline invariants (so the agent doesn't violate them even if the file load itself fails).

## Implications

- **Shipping a skill file is half the work.** The other half is the trigger hook. A skill without a hook is invisible.
- **Live test on a real prompt before considering it shipped.** The [[S036_2026-05-22_reprompting-iteration-and-shipping-port|S036]] iteration loop only completed because the second live test exposed the load gap. Without that test, the skill would have been "shipped" but inert.
- **Other load-on-cue skills will need the same pattern.** `query-patterns.md` is already load-on-cue but is loaded indirectly (via § 1 *Where to find things* + § 7 mode references). New behavioral skills that need to fire on user phrasing need an explicit entry in `### Skill triggers — load on cue`.
- **Cross-repo skills land twice.** The same skill in `gielinor/spellbook/skills/` and `shipping-agent/skills/` won't auto-sync. Future iterations on `reprompting.md` (and the next cross-repo skill) need to update both files explicitly and keep their substance — not their prose — in sync.

## Cross-link

- `shipping-agent/how_to.md` § 0 → "Skill triggers — load on cue" (the registry).
- `shipping-agent/skills/reprompting.md` (the skill the first registry entry points at).
- `shipping-agent/skills/_about.md` (the load-on-cue framing this note references).

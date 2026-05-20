# Q-003 — Personalities as loadable variants?

**Status.** `resolved` in [[S003]] via [[D-007]] (main brain's [[D-001]]). Opened in [[S001]].

**Resolution.** Loadable, but **not as personality variants of Niklavs** — as **players**, coherent characters with their own knowledge, self-model, and persona who happen to act on Niklavs' behalf.

Initial roster: **Zezima** (personal life, reading, reflection) and **Jebrim** (work, focused analytical execution). Each lives in `gielinor/players/<name>/` with its own full sub-layer template (`bank/`, `quest-log/`, `spellbook/`, `inventory/`, `examine/`, `niksis8_character/`, `keepsake/`) plus a minimal `_about.md`, `persona.md`, and `CLAUDE.md`. The respawn ritual asks which player to embody; the active player's namespace is scoped in.

The Split analogy holds — the brain swaps in a current player like a current self — but the rejection of "personas of Niklavs" matters. Zezima is not Niklavs-when-reflective; Zezima is Zezima, a character who *knows* Niklavs and acts for him in the reflective register.

Discipline: new players added only when content genuinely doesn't fit existing ones AND volume justifies overhead. Don't pre-create speculative players.

Cross-player invocation (dwarf in another player's namespace) is allowed but must be explicit — see [[Q-004]] resolution and `gielinor/meta/modes.md`.

See `gielinor/players/_about.md`.

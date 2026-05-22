Run the drafts-triage ritual per `gielinor/spellbook/rituals/drafts-triage.md`.

**Scope.** Active player's identity + bank + skill drafts (`examine/drafts/`, `niksis8_character/drafts/`, `bank/drafts/notes/`, `spellbook/drafts/skills/`, `keepsake/proposals/`) plus global identity drafts (`examine/drafts/`, `niksis8/drafts/`, `keepsake/proposals/`, `lorebook/drafts/`). Excludes Guthix layers — those are bankstanding territory. Excludes other players — that's their own alching.

**Behavior.** Survey all in-scope drafts; group by layer; number consecutively; surface each with a one-line claim, anchor, and agent recommendation (y/n/edit + reason). Principal triages in batch (`1y 2y 3n 4: edit "..."`). Agent executes via `git mv` (Bash bypasses confirmed/ hook) for player-owned moves; surfaces user-only writes (keepsake pins, lorebook decisions) for principal-side execution.

**Does not** update `last-alched.md` — this is a partial-promotion tool, not a full alching pass.

If no drafts exist in scope, report cleanly and stop.

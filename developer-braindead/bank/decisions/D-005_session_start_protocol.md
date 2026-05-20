# D-005 — 2026-05-20 — Session-start protocol: ask which brain unless told

**Context.** Two brain layers exist (developer-braindead vs main vault). Polluting the main brain with dev-session content is the primary risk this architecture guards against.

**Decision.** At the start of every session, Claude asks which brain to access unless the user has already stated it in the opening message.

**Alternatives considered.**
- Default to developer-braindead during the build phase — rejected; implicit defaults rot, explicit is safer.
- Slash command to switch — deferred; conversational protocol is fine for now.

**Consequences.** One short exchange at session start. Eliminates a category of accidental cross-pollution.

**Session ref.** [[S001]].

# R-002 — Three memory layers may drift

**Severity.** medium. Opened in [[S001_dev_brain_architecture]].

Three persistence surfaces exist: (1) Claude's `~/.claude/projects/.../memory/` (private cross-session memory), (2) `developer-braindead/` (shared dev brain, this folder), (3) `vault/` (main brain, TBD).

**Status update.** In [[S002_dev_brain_runescape_restructure]] §A.3, Claude's memory was slimmed to hold pointers into this folder rather than duplicate content. The duplication risk is now mostly addressed; the residual risk is the memory pointer file going stale as the dev brain restructures (e.g., the pointer currently names `HANDOFF.md`, which became `respawn.md` in [[D-006_dev_brain_restructure]] — needs follow-up).

**Mitigation.** Periodic audit each session. When dev brain structure changes, update the memory pointer in the same session.

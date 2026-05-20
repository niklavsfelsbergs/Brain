# `quest-log/` — about

Episodic memory for the dev brain. One file per session. The chronological record of *what happened* — distinct from `bank/` which records *what is known*.

**Filename pattern.** `SNNN_descriptive_underscore_name.md`. Stable session ID (`S001`, `S002`, …) plus a descriptive name set at session close. Names are *understandable*, not evocative — they tell future-you what the session was about.

**Why named at close, not start.** You can't title a quest before completing it. The shape of a session only becomes clear once it's done.

**Entry discipline.**
- 3–5 bullets per session, max. The quest log navigates; state lives in `bank/`, `examine/`, `player/`.
- Wiki-link references to whatever was created/changed: `[[D-006]]`, `[[I-001]]`, etc.
- Every entry ends with two lines:
  - **Cascade.** listing dev-brain updates landed this session.
  - **Main-brain changes.** listing what (if anything) crossed into `vault/`. Use `none` when nothing crossed.
- After writing the entry, update `respawn.md`.

**Sessions never deleted.** Superseded sessions don't exist — the log is append-only. The `archive/` folder is reserved in case a session ever needs to be archived (e.g., redacted for personal info), but should normally stay empty.

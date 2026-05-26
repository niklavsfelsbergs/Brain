# D-007 — 2026-05-20 — Main brain Phase 1 scaffold landed

**Context.** End of [[S002]] left the dev brain restructured around RuneScape layers ([[D-006_dev_brain_restructure]]) and pointed at a "next session" task: sync with the parallel main-brain design session and start building `vault/`. The parallel session produced a complete Phase 1 design, handed off in [[S003]] as a full brief. This decision records that the build happened: scaffolding landed in `gielinor/` (renamed from the dev brain's working term `vault/`).

**Decision.** Build the main brain Phase 1 scaffold today, at `Documents/GitHub/brain/gielinor/` — sibling to `developer-braindead/` under the same `brain/` parent. Defer the deferred mechanisms (cited in main-brain [[D-001_phase-1-scaffold]] under "Alternatives considered") to real use rather than designing them upfront.

**Structure landed (summary; full detail in main brain).** Body files (`CLAUDE.md`, `CLAUDE.local.md`, `.mcp.json`, `ticks.md`). `meta/` rulebook imported by `CLAUDE.md`. Global cognitive layers (`examine/`, `niksis8/`, `keepsake/`, `lorebook/`, `spellbook/`) each with `_about.md`. Rituals (`respawn.md`, `bankstanding.md`). Players system with initial roster Zezima and Jebrim, each with full sub-layer template. Four portable Python hooks in `.claude/hooks/` wired via `.claude/settings.json`. Founding decision recorded as main-brain [[D-001_phase-1-scaffold]].

**Why `gielinor/` not `vault/`.** The dev brain used "vault/" as the working term for the main brain folder. Niklavs chose **`gielinor/`** instead — "the world the agent inhabits, the total environment, not just a workspace inside it." The name does work that "vault" doesn't: it asserts the main brain is *where the agent lives*, not where it stores things.

**Why `niksis8/` literally.** The user-model folder is named after Niklavs' RuneScape username, on purpose, so the layer is unambiguously about him. Consistent with [[I-001]] (matching the principal's register — including playful, RS-themed naming) and with [[D-006_dev_brain_restructure]]'s commitment to RuneScape vocabulary across both brains.

**Why no seeding for `niksis8/confirmed/current.md`.** Niklavs explicitly held the line: the only fact at birth is "My name is Niklavs." Everything else is earned through observation and approved drafts. Same discipline applies to the players' `_about.md` and `persona.md` — minimal enough to distinguish characters, not full biographies. Same for Jebrim's `bank/` — it grows through real work in `Documents/bi-analytics-main/NFE/` and `Documents/bi-etl/`, not via one-shot ingestion. **Pattern: structure-first, content earns its way in.**

**Why portable Python hooks.** Originally proposed as PowerShell (`.ps1`) since Niklavs is on Windows. Niklavs asked for portability — the brain may travel to a new substrate in Phase 3, hooks should travel with it. Python is cross-platform and widely available.

**Why `meta/` exists.** The main-brain design's `CLAUDE.md` example used `@meta/write-rules.md` but `meta/` wasn't in the official layer list. Resolved as: `meta/` is the **current rulebook** (rewrites in place); `lorebook/` is **history** (only grows). Two lifetimes, two folders.

**Resolves.** [[Q-001]], [[Q-003]], [[Q-004]], [[Q-006]] (see those files for the specific resolutions). Updates [[plan]] §B to `done` (all subitems resolved by main-brain [[D-001_phase-1-scaffold]]).

**Defers.** `/drafts` command shape, bankstanding triggers, crash-reconciliation prompt wording, `inventory/` mechanics, cross-player retrieval mechanism, hook for `meta/` writes, hook for `rituals/` writes, eventual size-budget tuning. None are blockers for Phase 1 operation; they emerge from real use.

**Consequences.**
- The dev brain's job shifts from "design the main brain" to "observe and refine the main brain through use." Future dev brain decisions will be feedback loops, not design loops.
- The main brain is now the canonical source of truth for its own architecture (see `gielinor/lorebook/decisions/D-001_phase-1-scaffold.md`). Dev-brain decisions about main-brain shape should cross-reference rather than duplicate.

**Session ref.** [[S003]].

**Cross-refs.** Main-brain [[D-001_phase-1-scaffold]] (`gielinor/lorebook/decisions/D-001_phase-1-scaffold.md`).

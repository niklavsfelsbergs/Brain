# D-004 — 2026-05-20 — Stable IDs across dev brain docs

**Context.** Cross-referencing between docs (a decision arose from which question? closed by which session?) gets ambiguous fast in freeform prose.

**Decision.** Every entry in `bank/decisions/`, `bank/open-questions/`, `bank/assumptions/`, `bank/risks/`, `examine/` (identity), and `quest-log/` gets a stable short ID: [[D-NNN]], [[Q-NNN]], [[A-NNN]], [[R-NNN]], [[I-NNN]], [[SNNN]]. Numbers are never reused. Cross-references use wiki-link syntax `[[ID]]`, consistent with [[A-002]] (main brain uses wiki-links).

After the [[D-006]] restructure, IDs live in filenames as `D-001_descriptive_name.md`. The descriptive suffix aids discovery; the short ID alone remains the canonical reference.

**Alternatives considered.**
- Reference-style prose with dates only — rejected; doesn't scale.
- UUIDs / hashes — rejected; unreadable.

**Consequences.** Minor overhead at write time. Major payoff in traceability.

**Session ref.** [[S001]].

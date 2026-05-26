# D-004 — 2026-05-20 — Stable IDs across dev brain docs

**Context.** Cross-referencing between docs (a decision arose from which question? closed by which session?) gets ambiguous fast in freeform prose.

**Decision.** Every entry in `bank/decisions/`, `bank/open-questions/`, `bank/assumptions/`, `bank/risks/`, `examine/` (identity), and `quest-log/` gets a stable short ID: [[D-NNN]], [[Q-NNN]], [[A-NNN]], [[R-NNN]], [[I-NNN]], [[SNNN]]. Numbers are never reused. Cross-references use wiki-link syntax `[[ID]]`, consistent with [[A-002]] (main brain uses wiki-links).

After the [[D-006_dev_brain_restructure]] restructure, IDs live in filenames as `D-001_descriptive_name.md`. The descriptive suffix aids discovery; the short ID alone remains the canonical reference.

**Alternatives considered.**
- Reference-style prose with dates only — rejected; doesn't scale.
- UUIDs / hashes — rejected; unreadable.

**Consequences.** Minor overhead at write time. Major payoff in traceability.

**Session ref.** [[S001]].

---

## Amendment — 2026-05-26 (Obsidian-readiness)

The link-form clause is updated for tool-resolvability (Obsidian + any markdown tool that resolves `[[filename]]`). Cross-references now use the **full filename stem** — `[[D-004_stable_ids]]` — not the bare ID `[[D-004]]`.

- The stable ID (`D-004`) remains the **leading anchor** of every link and filename, never reused. Traceability — this decision's core purpose — is unchanged.
- The original *"the short ID alone remains the canonical reference"* rule (above) is **retired**: the descriptive suffix becomes load-bearing inside links. Accepted because slug-renames of stable historical entries are rare and mechanically recoverable (find-replace by the `[[D-NNN` prefix).
- Migration is a one-time **link-text** rewrite — no file renames, so hook/cockpit filename parsing is untouched. Spec + rationale: `bank/research/obsidian-fit-and-migration-spec.md`. First pass (2026-05-26): dev-brain `D-` decision links. Original D-004 text preserved above.

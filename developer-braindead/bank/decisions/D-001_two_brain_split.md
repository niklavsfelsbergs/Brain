# D-001 — 2026-05-20 — Two-brain separation: process belongs to dev, outcome belongs to main

**Context.** Building the agent generates two kinds of artifact: process artifacts (sessions, rejected alternatives, narrative of *why* we chose X) and outcome artifacts (current architecture, current personality, current capabilities). If both live in one place, the live agent has to read its own birth narrative to act — pollution.

**Decision.** Two physically separated surfaces from day one:
- `developer-braindead/` — process. Read only during dev sessions. Never loaded by the live agent.
- `vault/` (structure TBD) — outcome. The live agent's mutable memory. Updated by *deliberate export* from dev sessions.

Each dev session ends by stating in the quest-log entry what, if anything, in the main brain changed.

**Alternatives considered.**
- Single dir with naming convention — rejected; convention drifts, physical separation is harder to violate by accident.
- Have the agent read everything and rely on it to ignore dev content — rejected; wastes context, risks reasoning from dev rationale rather than current state.

**Consequences.** Some artifacts exist in both forms (e.g., dev [[I-001]]-style ledger entries ↔ main personality file once the latter is designed). The export step is its own discipline ([[R-001]]).

**Session ref.** [[S001_dev_brain_architecture]].

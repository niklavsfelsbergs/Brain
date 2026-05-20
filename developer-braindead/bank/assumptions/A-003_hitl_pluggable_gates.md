# A-003 — HITL during Phase 1; gates must be pluggable per tool / action-class

**Status.** `working`. Opened in [[S001]].

Phase 1 keeps human-in-the-loop on irreversible actions. Architecture must allow per-tool or per-action-class autonomy to be enabled later without rewriting the gate layer. Don't hard-code "always ask." Related: [[Q-002]].

**Replace when.** First per-tool or per-action-class autonomy is enabled. At that point, the gate-layer architecture is no longer an assumption — it's an active design. Convert to a [[D-NNN]] documenting the gate-tiering decision and edit this entry's status to `superseded by [[D-NNN]]`.

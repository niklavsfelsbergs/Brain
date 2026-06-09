# S181 — 2026-06-09 — Cockpit: transcript assistant response spans full width

Reopened post-[[S180_b472d014_cockpit_resumed_session_idle_state|S180]]-close (same sid b472d014); fresh OPEN→CLOSING via `comms_append`; no live Braindead siblings. A one-line follow-up to the [[S178_b472d014_cockpit_wrappedup_interrupt_transcript_pilljump|S178]] transcript reading-mode.

- **Niklavs:** the transcript assistant response should span the whole window now that it's bubble-less — the [[S178_b472d014_cockpit_wrappedup_interrupt_transcript_pilljump|S178]] reading mode left it capped at a 50rem reading measure (sensible when it was a bubble, redundant now that it floats).
- **Fix** ([[styles|cockpit/web/styles.css]], `.transcript-view`-scoped): `.asst-bubble max-width: 50rem → none`, and overrode the global `.t-asst max-width: 92%` → `none` in transcript scope so nothing else caps the float. The user message keeps its capped right-aligned gray pill (70%). CSS-only, brace-balanced.

**Cascade.** Edit to [[styles|cockpit/web/styles.css]]; dev-brain [[S181_b472d014_cockpit_transcript_full_width_response|this quest-log]], `respawn.md`, `comms/active.md`.

**Main-brain changes.** none — `cockpit/` is brain-root tooling, not `gielinor/`; `@import` chain untouched.

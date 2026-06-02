# S145 — knowledge-loading & rule-adherence audit + online research

**Dev-brain, 2026-06-02, sid 543c6caf.** Entered mid-conversation via "lets develop gielinor". OPEN posted via `comms_append`. Sibling-detection found a stale OPEN from `braindead-9b67aceb` (10:30, same topic, no CLOSING) — initially read as abandoned-discussion; later proved to be [[S144_9b67aceb_domain_grounding_cue_registry|S144]], which had shipped + committed + plan-sectioned + quest-logged but skipped only its comms CLOSING.

## Ask

Niklavs: brain has tons of knowledge that doesn't load when needed + tons of md rules often not followed. Wants an audit + suggestions (what becomes a hook? what else?) + **full online research** on making an AI brain use its knowledge and obey rules.

## Method

Lighter agent-assisted (Niklavs' multiple-choice pick over full-workflow / solo): 3 read-only internal scouts (knowledge-loading map; rule-adherence leak history + the Jebrim "acting dumb" shipping-report evidence; hook-enforcement surface) + 2 web scouts (agent memory/retrieval SOTA; rule/instruction-adherence + Claude Code hooks SOTA). Synthesized.

## Findings (full writeup: `bank/research/2026-06-02-knowledge-loading-and-rule-adherence.md`)

**Unifying diagnosis** — Niklavs' two problems are one failure: *knowledge/rules bound to a deterministic trigger hold; those depending on the agent deciding to act drift.* Confirmed internally (every hook-enforced line 0 leaks since birth; every discipline rule drifts) AND externally (the field's verbatim "hooks guarantee, prompts suggest"). Convergent with §W's independent "library-rich, reflex-poor" diagnosis. **Counter-intuitive corollary:** the eagerly-loaded `@import` chain (all 8 meta files every session) *degrades adherence to every rule* via constraint-count collapse (~81%→37% at 4–8 constraints), lost-in-the-middle, dilution, context rot — so adding more rule-prose is usually the wrong move.

**Two-bucket principle** (Anthropic Jan-2026 Constitution + hooks doctrine): bright-line checkable rules → code/hooks; judgment rules → reasoned prose with an anchor. Stop restating bright lines in prose.

## What I actually built

Rec #1 (config-driven domain knowledge loader) — **the build Niklavs picked — was already shipped as [[S144_9b67aceb_domain_grounding_cue_registry|S144]]** (`cue_registry.py` + `domain-cue-reminder.py`, registered, shipping-cue archived). Catching this before rebuilding was the anchor-referent / check-the-record discipline paying off. My contribution:

1. **Re-verified [[S144_9b67aceb_domain_grounding_cue_registry|S144]]** independently (the comment claimed boundary-verified): 7/7 synthetic cases (shipping/carrier→emit, non-shipping/bare-report→silent, malformed/wrong-event→exit 0, braindead→skip).
2. **Hardened `domain-cue-reminder.py`** — it resolved the actor via status-only `_actor_for`, the exact path `_actor.py`'s contract forbids (re-opens the S124 sidecar-lag race: a dev session would wrongly get a domain nudge during lag). Routed it through the shared `resolve_actor` (status→intent-file anti-race fallback), mirroring `require-open-on-entry.py`. Verified `py_compile` + 7 boundary cases + a 4-case isolated unit test of the intent fallback.

## Deliverables

- `bank/research/2026-06-02-knowledge-loading-and-rule-adherence.md` — audit + research + ranked menu + sources.
- `plan.md` §X — research-backed intervention backlog (X.2 Stop-hook ritual gate; X.3 draft-gate input-rewrite; X.4 SessionStart forced-read + fill keepsake; X.5 trim import chain → thin router + JIT index [contrarian, highest non-hook leverage, godly proposal]; X.6 critic sub-agent; X.7 adherence telemetry; X.8 mem0-style reconcile in alching; X.9 two-bucket rule audit). §W updated with the hardening note.
- `domain-cue-reminder.py` hardening.

## Then it widened — Niklavs: "the system is acting dumber, I need a real plan"

The session pivoted from audit to a full anti-deterioration program:

- **The deterioration mechanism (the reframe).** The brain grows monotonically (archive-discipline never deletes); identity loads eagerly, the rest waits to be fetched by agent decision. So as the corpus grows, the always-on load gets heavier (→ context rot / lost-in-middle / constraint-count collapse → every rule followed *worse*) AND the deferred pile gets bigger (→ more knowledge the agent must choose to find, and doesn't). **It gets dumber precisely as it gets richer.** Laid out a 4-phase plan: (0) measure, (1) shrink the always-on, (2) make retrieval reflexive, (3) curate against growth.
- **Phase 0 — ground truth (built).** `developer-braindead/verification/brain-weight.py` (always-on weight + git growth curve): **~49.2k tok always-on/session; @import chain tripled 8k→23k in 13 days, monotonic** — "deteriorating" is now a number. `knowledge-miss-regression-set.md` (10 real misses, 2 caught / 3 partial / 5 miss; the eval bar). Adherence baseline off existing `ritual-stats.py` (704 events/30d; key insight: it measures hooks *firing*, not the agent *obeying* — so prefer gates/forced-reads over more nudges).
- **Phase 1 — design + grant + Stage A.** Design doc `bank/research/2026-06-02-phase1-import-chain-trim-design.md` (central principle: only move a rule to JIT if a ritual reads it (R1) or a hook injects it (R2); R3-pointer only for rare reference, else it recreates the decide-to-load failure on the rules). **[[D-032_braindead_full_access|D-032]] — principal granted Braindead unrestricted edit reach** (rulebook + the hook floor; `block-confirmed-writes`/`block-deletes` carry an `actor=="braindead"` bypass, floor intact for all others; verified empirically + live). **Stage A executed:** `death-and-spawn`/`drafts-mechanics`/`archive-discipline` out of the eager `@import` chain (re-triggered by respawn forced-read / ritual inline-echo / `block-deletes` hook); chain **23,295 → 21,304 tok**; regression set unaffected.

## Open

- **Stages B–D** of the @import trim (`plan.md` §X.5) — B (`modes`+`write-rules`), C (the `communication-protocol` split, most delicate), D (cleanup). Each fresh session: edit → `brain-weight.py` → re-score regression set → check adherence; revert on regression.
- **Phase 2/3** backlog (§X.2–X.9): Stop-hook ritual gate (fix `close_check` continuation false-FAIL first), draft-gate input-rewrite, SessionStart forced-read, adherence-rate telemetry, mem0-style alching reconcile, two-bucket rule audit, the curation/retiring force for the still-climbing lesson pile.
- **Live-fire** of the domain-cue hook from a real Jebrim mart prompt (committed + registered; `ritual-stats` shows it already fired 14× — obedience still unmeasured).
- Sibling hygiene: [[S144_9b67aceb_domain_grounding_cue_registry|S144]]'s missing comms CLOSING (the 9b67aceb thread never posted one — ironic given the topic).

**Cascade.** `developer-braindead/`: `verification/brain-weight.py` + `verification/knowledge-miss-regression-set.md` (new); `bank/research/2026-06-02-knowledge-loading-and-rule-adherence.md` + `…phase1-import-chain-trim-design.md` (new); `bank/plan.md` §X + §W + §X.5-StageA; `CLAUDE.md` (full-access scope); this quest-log; `comms/active.md`.
**Main-brain changes.** `gielinor/`: `.claude/hooks/domain-cue-reminder.py` (resolve_actor hardening); `.claude/hooks/block-deletes.py` + `block-confirmed-writes.py` (braindead bypass); `meta/write-rules.md` (Braindead exception); `lorebook/confirmed/D-032_braindead_full_access.md` (new); `CLAUDE.md` (@import trim §X-A); `spellbook/rituals/respawn.md` (death-and-spawn forced-read).

active-mode → unscoped at close.

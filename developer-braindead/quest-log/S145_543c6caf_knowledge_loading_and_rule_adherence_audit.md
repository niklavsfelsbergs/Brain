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

## Open

- **Live-fire** of the domain-cue hook from a real Jebrim mart prompt (committed + registered; loads next fresh session).
- The §X backlog — none urgent; surfaced for Niklavs to steer. X.2/X.3/X.7 are clean dev builds; X.5 is the strategic win but high-blast-radius.
- Sibling hygiene: [[S144_9b67aceb_domain_grounding_cue_registry|S144]]'s missing comms CLOSING (the 9b67aceb thread never posted one — ironic given the topic).

active-mode → unscoped at close.
